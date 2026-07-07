"""End-to-end floor plan processing orchestration."""

from __future__ import annotations

import json
import shutil
import uuid
from pathlib import Path
from typing import Optional

from PIL import Image

from floorplan3d.config import (
    PROCESSED_DIR,
    RAW_DIR,
    YOLO_CONFIDENCE,
    YOLO_MODEL_PATH,
    ensure_runtime_dirs,
    project_dir,
)
from floorplan3d.detection import (
    YOLOObjectDetector,
    attach_openings_to_nearest_walls,
    infer_openings,
    walls_from_symbols,
)
from floorplan3d.geometry_solver import GeometrySolver
from floorplan3d.ocr import TesseractOCRModel
from floorplan3d.pdf_loader import load_floorplan
from floorplan3d.scene_builder import export_glb
from floorplan3d.schemas import FloorPlan, SourceMetadata
from floorplan3d.segmentation import HeuristicSegmentationModel


def process_file(
    input_path: Path,
    filename: Optional[str] = None,
    content_type: str = "application/octet-stream",
    project_id: Optional[str] = None,
) -> FloorPlan:
    ensure_runtime_dirs()
    project_id = project_id or uuid.uuid4().hex
    destination = RAW_DIR / f"{project_id}{input_path.suffix.lower()}"
    if input_path.resolve() != destination.resolve():
        shutil.copyfile(input_path, destination)

    image, page = load_floorplan(destination)
    image_path = PROCESSED_DIR / f"{project_id}.png"
    Image.fromarray(image).save(image_path)

    segmentation = HeuristicSegmentationModel()
    detector = YOLOObjectDetector(
        weights_path=YOLO_MODEL_PATH,
        confidence=YOLO_CONFIDENCE,
        labels=("wall", "door", "sliding door", "window"),
    )
    ocr = TesseractOCRModel()
    solver = GeometrySolver()

    wall_mask = segmentation.predict_wall_mask(image)
    symbols = detector.detect(image)
    labels = ocr.extract_text(image)
    yolo_walls = walls_from_symbols(symbols, pixels_per_meter=solver.pixels_per_meter)
    walls = yolo_walls or solver.solve_walls(wall_mask)
    openings = attach_openings_to_nearest_walls(
        infer_openings(symbols, pixels_per_meter=solver.pixels_per_meter),
        walls,
    )
    rooms = solver.solve_rooms(wall_mask)
    if labels and rooms:
        rooms[0].label = labels[0]

    floorplan = FloorPlan(
        source=SourceMetadata(
            filename=filename or input_path.name,
            content_type=content_type,
            page=page,
            image_size=(int(image.shape[1]), int(image.shape[0])),
        ),
        walls=walls,
        openings=openings,
        rooms=rooms,
        symbols=symbols,
    )
    write_project_outputs(project_id, floorplan)
    return floorplan


def write_project_outputs(project_id: str, floorplan: FloorPlan) -> Path:
    output_dir = project_dir(project_id)
    json_path = output_dir / "floorplan.json"
    json_path.write_text(json.dumps(floorplan.to_dict(), indent=2), encoding="utf-8")
    export_glb(floorplan, output_dir / "scene.glb")
    return output_dir


def read_floorplan(project_id: str) -> FloorPlan:
    json_path = project_dir(project_id) / "floorplan.json"
    return FloorPlan.from_dict(json.loads(json_path.read_text(encoding="utf-8")))

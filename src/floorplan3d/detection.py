"""Floor plan object detection interfaces and YOLO integration."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Protocol, Tuple

import numpy as np

from floorplan3d.schemas import Opening, Symbol, Wall


class ObjectDetector(Protocol):
    def detect(self, image: np.ndarray) -> List[Symbol]:
        """Return detected floor plan objects."""


LABEL_MAP: Dict[str, str] = {
    "column": "column",
    "curtain wall": "wall",
    "dimension": "dimension",
    "door": "door",
    "railing": "railing",
    "sliding door": "door",
    "stair case": "stair",
    "staircase": "stair",
    "wall": "wall",
    "window": "window",
}


@dataclass
class StubObjectDetector:
    """Deterministic placeholder used when no YOLO weights are configured."""

    def detect(self, image: np.ndarray) -> List[Symbol]:
        return []


@dataclass
class YOLOObjectDetector:
    """Ultralytics YOLO adapter for floor plan symbols.

    The referenced repository loads a YOLOv8 `best.pt`, predicts on the uploaded
    image, and filters architectural labels like Wall, Door, Sliding Door, and
    Window. This adapter keeps the same model contract but normalizes detections
    into this app's JSON schema.
    """

    weights_path: Path
    confidence: float = 0.4
    labels: Optional[Iterable[str]] = None

    def __post_init__(self) -> None:
        self._model = None

    @property
    def available(self) -> bool:
        return self.weights_path.exists()

    def detect(self, image: np.ndarray) -> List[Symbol]:
        if not self.available:
            return []
        model = self._load_model()
        results = model.predict(image, conf=self.confidence, verbose=False)
        if not results:
            return []

        selected = {normalize_label(label) for label in self.labels} if self.labels else None
        boxes = getattr(results[0], "boxes", None)
        if boxes is None:
            return []

        symbols: List[Symbol] = []
        for index, box in enumerate(boxes, start=1):
            class_id = int(box.cls.item() if hasattr(box.cls, "item") else box.cls)
            source_label = str(model.names[class_id])
            kind = normalize_label(source_label)
            if selected is not None and kind not in selected:
                continue
            x1, y1, x2, y2 = (float(value) for value in box.xyxy[0].tolist())
            confidence = float(box.conf.item() if hasattr(box.conf, "item") else box.conf)
            symbols.append(
                Symbol(
                    id=f"det-{index}",
                    kind=kind,
                    bbox=(x1, y1, x2 - x1, y2 - y1),
                    confidence=confidence,
                    source_label=source_label,
                )
            )
        return symbols

    def _load_model(self):
        if self._model is None:
            from ultralytics import YOLO

            self._model = YOLO(str(self.weights_path))
        return self._model


def normalize_label(label: str) -> str:
    cleaned = " ".join(label.strip().replace("_", " ").replace("-", " ").lower().split())
    return LABEL_MAP.get(cleaned, cleaned)


def infer_openings(symbols: List[Symbol], pixels_per_meter: float = 100.0) -> List[Opening]:
    openings: List[Opening] = []
    for index, symbol in enumerate(symbols):
        if symbol.kind not in {"door", "window"}:
            continue
        x, y, width, height = symbol.bbox
        is_window = symbol.kind == "window"
        openings.append(
            Opening(
                id=f"opening-{index + 1}",
                kind=symbol.kind,
                position=(
                    round((x + width / 2) / pixels_per_meter, 3),
                    round((y + height / 2) / pixels_per_meter, 3),
                ),
                width=round(max(width, height) / pixels_per_meter, 3),
                height=1.2 if is_window else 2.1,
                sill_height=0.9 if is_window else 0.0,
            )
        )
    return openings


def walls_from_symbols(symbols: List[Symbol], pixels_per_meter: float = 100.0) -> List[Wall]:
    walls: List[Wall] = []
    wall_symbols = [symbol for symbol in symbols if symbol.kind == "wall"]
    for index, symbol in enumerate(wall_symbols, start=1):
        x, y, width, height = symbol.bbox
        if width >= height:
            start = (x / pixels_per_meter, (y + height / 2) / pixels_per_meter)
            end = ((x + width) / pixels_per_meter, (y + height / 2) / pixels_per_meter)
            thickness = max(height / pixels_per_meter, 0.08)
        else:
            start = ((x + width / 2) / pixels_per_meter, y / pixels_per_meter)
            end = ((x + width / 2) / pixels_per_meter, (y + height) / pixels_per_meter)
            thickness = max(width / pixels_per_meter, 0.08)
        walls.append(
            Wall(
                id=f"yolo-wall-{index}",
                points=[
                    (round(start[0], 3), round(start[1], 3)),
                    (round(end[0], 3), round(end[1], 3)),
                ],
                thickness=round(thickness, 3),
            )
        )
    return walls


def attach_openings_to_nearest_walls(openings: List[Opening], walls: List[Wall]) -> List[Opening]:
    if not walls:
        return openings
    for opening in openings:
        opening.wall_id = min(walls, key=lambda wall: _distance_to_wall(opening.position, wall)).id
    return openings


def _distance_to_wall(point: Tuple[float, float], wall: Wall) -> float:
    start = np.array(wall.points[0], dtype=float)
    end = np.array(wall.points[-1], dtype=float)
    target = np.array(point, dtype=float)
    segment = end - start
    length_squared = float(np.dot(segment, segment))
    if length_squared == 0:
        return float(np.linalg.norm(target - start))
    projection = max(0.0, min(1.0, float(np.dot(target - start, segment) / length_squared)))
    nearest = start + projection * segment
    return float(np.linalg.norm(target - nearest))

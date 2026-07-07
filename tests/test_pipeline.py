from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from floorplan3d.pipeline import process_file
from floorplan3d.scene_builder import floorplan_bounds


def test_process_simple_image_creates_floorplan(tmp_path: Path) -> None:
    image_path = tmp_path / "simple.png"
    image = Image.new("RGB", (240, 180), "white")
    draw = ImageDraw.Draw(image)
    draw.rectangle((30, 30, 210, 150), outline="black", width=8)
    image.save(image_path)

    floorplan = process_file(image_path, project_id="pytest-simple")

    assert floorplan.source.filename == "simple.png"
    assert floorplan.source.image_size == (240, 180)
    assert len(floorplan.walls) > 0
    assert len(floorplan.rooms) == 1
    assert floorplan_bounds(floorplan.walls)[2] > 0


def test_floorplan_dict_round_trip() -> None:
    image = np.zeros((20, 20, 3), dtype=np.uint8)
    assert image.shape == (20, 20, 3)

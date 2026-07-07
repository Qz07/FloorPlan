from floorplan3d.detection import (
    attach_openings_to_nearest_walls,
    infer_openings,
    normalize_label,
    walls_from_symbols,
)
from floorplan3d.schemas import Symbol


def test_normalize_reference_labels() -> None:
    assert normalize_label("Wall") == "wall"
    assert normalize_label("Sliding Door") == "door"
    assert normalize_label("Stair-Case") == "stair"


def test_yolo_wall_symbols_become_world_space_walls() -> None:
    symbols = [
        Symbol(id="wall-det", kind="wall", bbox=(20, 30, 180, 10), confidence=0.9),
        Symbol(id="door-det", kind="door", bbox=(90, 25, 30, 25), confidence=0.8),
    ]

    walls = walls_from_symbols(symbols, pixels_per_meter=100)
    openings = attach_openings_to_nearest_walls(
        infer_openings(symbols, pixels_per_meter=100),
        walls,
    )

    assert walls[0].id == "yolo-wall-1"
    assert walls[0].points == [(0.2, 0.35), (2.0, 0.35)]
    assert openings[0].kind == "door"
    assert openings[0].position == (1.05, 0.375)
    assert openings[0].wall_id == "yolo-wall-1"


def test_window_opening_defaults_include_sill_height() -> None:
    openings = infer_openings(
        [Symbol(id="window-det", kind="window", bbox=(10, 10, 40, 20), confidence=0.7)],
        pixels_per_meter=100,
    )

    assert openings[0].height == 1.2
    assert openings[0].sill_height == 0.9

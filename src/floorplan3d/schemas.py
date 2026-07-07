"""Shared floor plan data structures."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional, Tuple

Point2D = Tuple[float, float]


@dataclass
class SourceMetadata:
    filename: str
    content_type: str
    page: int = 1
    image_size: Tuple[int, int] = (0, 0)
    scale: Optional[float] = None


@dataclass
class Wall:
    id: str
    points: List[Point2D]
    thickness: float = 0.15
    height: float = 2.7


@dataclass
class Opening:
    id: str
    kind: str
    position: Point2D
    width: float = 0.9
    wall_id: Optional[str] = None


@dataclass
class Room:
    id: str
    polygon: List[Point2D]
    label: Optional[str] = None


@dataclass
class Symbol:
    id: str
    kind: str
    bbox: Tuple[float, float, float, float]
    confidence: float = 0.0


@dataclass
class SceneDefaults:
    units: str = "meters"
    wall_height: float = 2.7
    floor_thickness: float = 0.12


@dataclass
class FloorPlan:
    source: SourceMetadata
    walls: List[Wall] = field(default_factory=list)
    openings: List[Opening] = field(default_factory=list)
    rooms: List[Room] = field(default_factory=list)
    symbols: List[Symbol] = field(default_factory=list)
    scene: SceneDefaults = field(default_factory=SceneDefaults)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FloorPlan":
        return cls(
            source=SourceMetadata(**data["source"]),
            walls=[Wall(**wall) for wall in data.get("walls", [])],
            openings=[Opening(**opening) for opening in data.get("openings", [])],
            rooms=[Room(**room) for room in data.get("rooms", [])],
            symbols=[Symbol(**symbol) for symbol in data.get("symbols", [])],
            scene=SceneDefaults(**data.get("scene", {})),
        )

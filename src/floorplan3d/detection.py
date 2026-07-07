"""Opening and symbol detection interfaces."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Protocol

import numpy as np

from floorplan3d.schemas import Opening, Symbol


class ObjectDetector(Protocol):
    def detect(self, image: np.ndarray) -> List[Symbol]:
        """Return detected floor plan objects."""


@dataclass
class StubObjectDetector:
    """Deterministic placeholder until a trained YOLO/RT-DETR model is configured."""

    def detect(self, image: np.ndarray) -> List[Symbol]:
        return []


def infer_openings(symbols: List[Symbol]) -> List[Opening]:
    openings: List[Opening] = []
    for index, symbol in enumerate(symbols):
        if symbol.kind not in {"door", "window"}:
            continue
        x, y, width, height = symbol.bbox
        openings.append(
            Opening(
                id=f"opening-{index + 1}",
                kind=symbol.kind,
                position=(x + width / 2, y + height / 2),
                width=max(width, height),
            )
        )
    return openings

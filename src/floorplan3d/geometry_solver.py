"""Convert 2D masks into simple wall and room geometry."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

import cv2
import numpy as np

from floorplan3d.schemas import Room, Wall


@dataclass
class GeometrySolver:
    pixels_per_meter: float = 100.0
    min_wall_length_px: float = 40.0

    def solve_walls(self, wall_mask: np.ndarray) -> List[Wall]:
        edges = cv2.Canny(wall_mask, 50, 150)
        lines = cv2.HoughLinesP(
            edges,
            rho=1,
            theta=np.pi / 180,
            threshold=40,
            minLineLength=int(self.min_wall_length_px),
            maxLineGap=12,
        )
        if lines is None:
            return self._fallback_bounds(wall_mask)

        walls: List[Wall] = []
        for index, line in enumerate(lines.reshape(-1, 4)[:200], start=1):
            x1, y1, x2, y2 = line
            length = float(np.hypot(x2 - x1, y2 - y1))
            if length < self.min_wall_length_px:
                continue
            walls.append(
                Wall(
                    id=f"wall-{index}",
                    points=[self._to_world(x1, y1), self._to_world(x2, y2)],
                )
            )
        return walls or self._fallback_bounds(wall_mask)

    def solve_rooms(self, wall_mask: np.ndarray) -> List[Room]:
        height, width = wall_mask.shape[:2]
        margin = 10
        polygon = [
            self._to_world(margin, margin),
            self._to_world(width - margin, margin),
            self._to_world(width - margin, height - margin),
            self._to_world(margin, height - margin),
        ]
        return [Room(id="room-1", polygon=polygon, label=None)]

    def _fallback_bounds(self, wall_mask: np.ndarray) -> List[Wall]:
        contours, _ = cv2.findContours(wall_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return []
        contour = max(contours, key=cv2.contourArea)
        x, y, width, height = cv2.boundingRect(contour)
        corners = [(x, y), (x + width, y), (x + width, y + height), (x, y + height)]
        walls: List[Wall] = []
        for index, ((x1, y1), (x2, y2)) in enumerate(zip(corners, corners[1:] + corners[:1]), start=1):
            walls.append(Wall(id=f"wall-{index}", points=[self._to_world(x1, y1), self._to_world(x2, y2)]))
        return walls

    def _to_world(self, x: float, y: float) -> Tuple[float, float]:
        return (round(x / self.pixels_per_meter, 3), round(y / self.pixels_per_meter, 3))

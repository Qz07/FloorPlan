"""Wall segmentation with a heuristic fallback and pluggable model boundary."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import cv2
import numpy as np

from floorplan3d.image_preprocess import binarize_floorplan, clean_binary_mask


class SegmentationModel(Protocol):
    def predict_wall_mask(self, image: np.ndarray) -> np.ndarray:
        """Return a binary wall mask for the input RGB image."""


@dataclass
class HeuristicSegmentationModel:
    min_component_area: int = 200

    def predict_wall_mask(self, image: np.ndarray) -> np.ndarray:
        mask = clean_binary_mask(binarize_floorplan(image))
        component_count, labels, stats, _ = cv2.connectedComponentsWithStats(mask, connectivity=8)
        filtered = np.zeros_like(mask)
        for label in range(1, component_count):
            if stats[label, cv2.CC_STAT_AREA] >= self.min_component_area:
                filtered[labels == label] = 255
        return filtered

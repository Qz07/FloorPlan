"""OCR adapter for room labels and dimensions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Protocol

import numpy as np
import pytesseract


class OCRModel(Protocol):
    def extract_text(self, image: np.ndarray) -> List[str]:
        """Return visible text strings from the floor plan."""


@dataclass
class TesseractOCRModel:
    config: str = "--psm 6"

    def extract_text(self, image: np.ndarray) -> List[str]:
        try:
            text = pytesseract.image_to_string(image, config=self.config)
        except pytesseract.TesseractNotFoundError:
            return []
        return [line.strip() for line in text.splitlines() if line.strip()]

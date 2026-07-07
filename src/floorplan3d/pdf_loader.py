"""Load PDFs and raster floor plan images into RGB arrays."""

from __future__ import annotations

from pathlib import Path
from typing import Tuple

import fitz
import numpy as np
from PIL import Image

SUPPORTED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp"}


def load_floorplan(path: Path, page: int = 0, dpi: int = 200) -> Tuple[np.ndarray, int]:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return render_pdf_page(path, page=page, dpi=dpi), page + 1
    if suffix in SUPPORTED_IMAGE_EXTENSIONS:
        return load_image(path), 1
    raise ValueError(f"Unsupported floor plan input type: {suffix}")


def render_pdf_page(path: Path, page: int = 0, dpi: int = 200) -> np.ndarray:
    with fitz.open(path) as document:
        if page < 0 or page >= document.page_count:
            raise ValueError(f"PDF page {page} is out of range for {path.name}")
        matrix = fitz.Matrix(dpi / 72, dpi / 72)
        pixmap = document[page].get_pixmap(matrix=matrix, alpha=False)
        image = Image.frombytes("RGB", (pixmap.width, pixmap.height), pixmap.samples)
        return np.asarray(image)


def load_image(path: Path) -> np.ndarray:
    with Image.open(path) as image:
        return np.asarray(image.convert("RGB"))

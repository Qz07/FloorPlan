"""Runtime paths and simple project storage helpers."""

from __future__ import annotations

from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT_DIR / "data"
RAW_DIR = DATA_DIR / "raw_pdfs"
PROCESSED_DIR = DATA_DIR / "processed_images"
OUTPUT_DIR = DATA_DIR / "outputs"
MODEL_DIR = ROOT_DIR / "models"


def ensure_runtime_dirs() -> None:
    for path in (
        RAW_DIR,
        PROCESSED_DIR,
        OUTPUT_DIR,
        MODEL_DIR / "segmentation",
        MODEL_DIR / "detection",
        MODEL_DIR / "ocr",
    ):
        path.mkdir(parents=True, exist_ok=True)


def project_dir(project_id: str) -> Path:
    path = OUTPUT_DIR / project_id
    path.mkdir(parents=True, exist_ok=True)
    return path

"""Command line entry point."""

from __future__ import annotations

import argparse
from pathlib import Path

from floorplan3d.pipeline import process_file


def main() -> None:
    parser = argparse.ArgumentParser(description="Process a floor plan into JSON and GLB outputs.")
    parser.add_argument("input", type=Path, help="PDF or raster image floor plan")
    parser.add_argument("--project-id", default=None, help="Optional deterministic output project id")
    args = parser.parse_args()

    floorplan = process_file(args.input, project_id=args.project_id)
    print(f"Processed {args.input} with {len(floorplan.walls)} walls")

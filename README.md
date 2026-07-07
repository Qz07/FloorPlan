# FloorPlan 3D

Runnable MVP for converting floor plan PDFs or images into editable JSON geometry and a
3D scene export.

## Backend

```bash
uv run uvicorn floorplan3d.api:app --reload
```

Process one file from the command line:

```bash
uv run floorplan3d path/to/floorplan.pdf --project-id demo
```

Outputs are written to `data/outputs/{project_id}/`:

- `floorplan.json`
- `scene.glb`

## YOLO Detection

Place Ultralytics YOLO weights at `models/detection/best.pt`, or set:

```bash
export FLOORPLAN3D_YOLO_WEIGHTS=/path/to/best.pt
export FLOORPLAN3D_YOLO_CONFIDENCE=0.4
```

When weights are available, the backend uses YOLO detections for `wall`, `door`,
`sliding door`, and `window`. Wall boxes become 3D wall segments; door/window
boxes become openings attached to the nearest detected wall. If no weights are
present, the backend falls back to the heuristic wall extractor.

## Frontend

```bash
cd web
npm install
npm run dev
```

The Vite dev server proxies `/api` to `http://127.0.0.1:8000`.

## Project Layout

- `src/floorplan3d/`: FastAPI app, PDF/image loading, preprocessing, geometry solving, and scene export.
- `web/`: React/TypeScript correction UI and Three.js viewer.
- `data/`: local raw inputs, processed images, and generated outputs.
- `models/`: optional model weights for segmentation, detection, and OCR adapters.

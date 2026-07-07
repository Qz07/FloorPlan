"""FastAPI application for floor plan processing."""

from __future__ import annotations

import shutil
import uuid
from contextlib import asynccontextmanager
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any, AsyncIterator, Dict

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from floorplan3d.config import ensure_runtime_dirs, project_dir
from floorplan3d.pipeline import process_file, read_floorplan, write_project_outputs
from floorplan3d.schemas import FloorPlan


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    ensure_runtime_dirs()
    yield


app = FastAPI(title="FloorPlan 3D API", version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/api/projects")
async def create_project(file: UploadFile = File(...)) -> Dict[str, Any]:
    project_id = uuid.uuid4().hex
    suffix = Path(file.filename or "floorplan").suffix or ".bin"
    with NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
        shutil.copyfileobj(file.file, temp_file)
        temp_path = Path(temp_file.name)
    try:
        floorplan = process_file(
            temp_path,
            filename=file.filename,
            content_type=file.content_type or "application/octet-stream",
            project_id=project_id,
        )
    finally:
        temp_path.unlink(missing_ok=True)
    return {
        "project_id": project_id,
        "status": "complete",
        "floorplan": floorplan.to_dict(),
        "links": {
            "json": f"/api/projects/{project_id}/floorplan.json",
            "glb": f"/api/projects/{project_id}/export.glb",
        },
    }


@app.get("/api/projects/{project_id}")
def get_project(project_id: str) -> Dict[str, Any]:
    output_dir = project_dir(project_id)
    json_path = output_dir / "floorplan.json"
    if not json_path.exists():
        raise HTTPException(status_code=404, detail="Project not found")
    return {
        "project_id": project_id,
        "status": "complete",
        "links": {
            "json": f"/api/projects/{project_id}/floorplan.json",
            "glb": f"/api/projects/{project_id}/export.glb",
        },
    }


@app.get("/api/projects/{project_id}/floorplan.json")
def get_floorplan(project_id: str) -> Dict[str, Any]:
    try:
        return read_floorplan(project_id).to_dict()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Project not found") from exc


@app.put("/api/projects/{project_id}/floorplan.json")
def update_floorplan(project_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    floorplan = FloorPlan.from_dict(payload)
    write_project_outputs(project_id, floorplan)
    return {"project_id": project_id, "status": "complete", "floorplan": floorplan.to_dict()}


@app.get("/api/projects/{project_id}/export.glb")
def get_glb(project_id: str) -> FileResponse:
    glb_path = project_dir(project_id) / "scene.glb"
    if not glb_path.exists():
        raise HTTPException(status_code=404, detail="Export not found")
    return FileResponse(glb_path, media_type="model/gltf-binary", filename="scene.glb")

"""Build 3D scene exports from canonical floor plan JSON."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, Optional, Tuple

import numpy as np
import trimesh

from floorplan3d.schemas import FloorPlan, Opening, Wall


def export_glb(floorplan: FloorPlan, output_path: Path) -> Path:
    scene = trimesh.Scene()
    _add_floor(scene, floorplan)
    for wall in floorplan.walls:
        mesh = _wall_mesh(wall, floorplan.scene.wall_height)
        if mesh is not None:
            scene.add_geometry(mesh, node_name=wall.id)
    for opening in floorplan.openings:
        mesh = _opening_marker(opening)
        if mesh is not None:
            scene.add_geometry(mesh, node_name=opening.id)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    scene.export(output_path)
    return output_path


def _add_floor(scene: trimesh.Scene, floorplan: FloorPlan) -> None:
    points = [point for room in floorplan.rooms for point in room.polygon]
    if not points:
        points = [point for wall in floorplan.walls for point in wall.points]
    if not points:
        return
    xs, ys = zip(*points)
    width = max(xs) - min(xs)
    depth = max(ys) - min(ys)
    if width <= 0 or depth <= 0:
        return
    floor = trimesh.creation.box(
        extents=(width, depth, floorplan.scene.floor_thickness),
        transform=trimesh.transformations.translation_matrix(
            (min(xs) + width / 2, min(ys) + depth / 2, -floorplan.scene.floor_thickness / 2)
        ),
    )
    floor.visual.face_colors = (210, 210, 205, 255)
    scene.add_geometry(floor, node_name="floor")


def _wall_mesh(wall: Wall, height: float) -> Optional[trimesh.Trimesh]:
    if len(wall.points) < 2:
        return None
    start = np.array((wall.points[0][0], wall.points[0][1], height / 2), dtype=float)
    end = np.array((wall.points[-1][0], wall.points[-1][1], height / 2), dtype=float)
    delta = end - start
    length = float(np.linalg.norm(delta[:2]))
    if length == 0:
        return None
    mesh = trimesh.creation.box(extents=(length, wall.thickness, height))
    angle = float(np.arctan2(delta[1], delta[0]))
    transform = trimesh.transformations.rotation_matrix(angle, (0, 0, 1))
    transform[:3, 3] = (start + end) / 2
    mesh.apply_transform(transform)
    mesh.visual.face_colors = (90, 95, 105, 255)
    return mesh


def _opening_marker(opening: Opening) -> Optional[trimesh.Trimesh]:
    width = max(opening.width, 0.1)
    height = max(opening.height, 0.1)
    depth = 0.04
    center_z = opening.sill_height + height / 2
    mesh = trimesh.creation.box(
        extents=(width, depth, height),
        transform=trimesh.transformations.translation_matrix(
            (opening.position[0], opening.position[1], center_z)
        ),
    )
    if opening.kind == "window":
        mesh.visual.face_colors = (75, 150, 210, 170)
    else:
        mesh.visual.face_colors = (190, 120, 65, 210)
    return mesh


def floorplan_bounds(walls: Iterable[Wall]) -> Tuple[float, float, float, float]:
    points = [point for wall in walls for point in wall.points]
    if not points:
        return (0.0, 0.0, 0.0, 0.0)
    xs, ys = zip(*points)
    return (min(xs), min(ys), max(xs), max(ys))

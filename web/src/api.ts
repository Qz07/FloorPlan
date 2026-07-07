import type { FloorPlan } from "./types";

export interface ProjectResponse {
  project_id: string;
  status: string;
  floorplan: FloorPlan;
  links: {
    json: string;
    glb: string;
  };
}

export async function uploadFloorPlan(file: File): Promise<ProjectResponse> {
  const formData = new FormData();
  formData.append("file", file);
  const response = await fetch("/api/projects", {
    method: "POST",
    body: formData
  });
  if (!response.ok) {
    throw new Error(`Upload failed: ${response.status}`);
  }
  return response.json();
}

export async function saveFloorPlan(projectId: string, floorplan: FloorPlan): Promise<ProjectResponse> {
  const response = await fetch(`/api/projects/${projectId}/floorplan.json`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(floorplan)
  });
  if (!response.ok) {
    throw new Error(`Save failed: ${response.status}`);
  }
  return response.json();
}

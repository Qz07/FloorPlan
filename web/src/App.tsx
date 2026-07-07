import { useMemo, useState } from "react";
import { saveFloorPlan, uploadFloorPlan } from "./api";
import { FloorPlanEditor } from "./FloorPlanEditor";
import { ThreeViewer } from "./ThreeViewer";
import type { FloorPlan } from "./types";
import "./styles.css";

function App() {
  const [projectId, setProjectId] = useState<string | null>(null);
  const [floorplan, setFloorplan] = useState<FloorPlan | null>(null);
  const [selectedWallId, setSelectedWallId] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const exportUrl = useMemo(() => (projectId ? `/api/projects/${projectId}/export.glb` : null), [projectId]);

  async function onFileChange(file: File | null) {
    if (!file) {
      return;
    }
    setBusy(true);
    setError(null);
    try {
      const response = await uploadFloorPlan(file);
      setProjectId(response.project_id);
      setFloorplan(response.floorplan);
      setSelectedWallId(response.floorplan.walls[0]?.id ?? null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setBusy(false);
    }
  }

  function updateWallHeight(wallId: string, height: number) {
    setFloorplan((current) => {
      if (!current) {
        return current;
      }
      return {
        ...current,
        walls: current.walls.map((wall) => (wall.id === wallId ? { ...wall, height } : wall))
      };
    });
  }

  async function saveCorrections() {
    if (!projectId || !floorplan) {
      return;
    }
    setBusy(true);
    setError(null);
    try {
      const response = await saveFloorPlan(projectId, floorplan);
      setFloorplan(response.floorplan);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Save failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="app-shell">
      <header className="topbar">
        <div>
          <h1>FloorPlan 3D</h1>
          <p>Convert PDF and image floor plans into editable geometry and 3D exports.</p>
        </div>
        <div className="actions">
          <label className="upload-button">
            <input
              type="file"
              accept=".pdf,.jpg,.jpeg,.png,.webp,.tif,.tiff"
              onChange={(event) => onFileChange(event.target.files?.[0] ?? null)}
            />
            Upload
          </label>
          <button disabled={!floorplan || busy} onClick={saveCorrections}>
            Save
          </button>
          <a className={!exportUrl ? "disabled-link" : ""} href={exportUrl ?? "#"}>
            GLB
          </a>
        </div>
      </header>

      {error ? <div className="error-banner">{error}</div> : null}

      <div className="workspace">
        {floorplan ? (
          <FloorPlanEditor
            floorplan={floorplan}
            selectedWallId={selectedWallId}
            onSelectWall={setSelectedWallId}
            onWallHeightChange={updateWallHeight}
          />
        ) : (
          <section className="panel empty-state">
            <h2>Upload a plan</h2>
            <p>PDF, JPG, PNG, TIFF, and WebP inputs are supported by the backend pipeline.</p>
          </section>
        )}
        <section className="panel viewer-panel">
          <div className="panel-header">
            <div>
              <h2>3D scene</h2>
              <p>{busy ? "Processing..." : projectId ?? "No project loaded"}</p>
            </div>
          </div>
          <ThreeViewer floorplan={floorplan} />
        </section>
      </div>
    </main>
  );
}

export default App;

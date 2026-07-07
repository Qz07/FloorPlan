import type { FloorPlan, Wall } from "./types";

interface Props {
  floorplan: FloorPlan;
  selectedWallId: string | null;
  onSelectWall: (wallId: string) => void;
  onWallHeightChange: (wallId: string, height: number) => void;
}

export function FloorPlanEditor({ floorplan, selectedWallId, onSelectWall, onWallHeightChange }: Props) {
  const [imageWidth, imageHeight] = floorplan.source.image_size;
  const viewBox = `0 0 ${Math.max(imageWidth / 100, 1)} ${Math.max(imageHeight / 100, 1)}`;
  const selectedWall = floorplan.walls.find((wall) => wall.id === selectedWallId) ?? floorplan.walls[0];

  return (
    <section className="panel editor-panel">
      <div className="panel-header">
        <div>
          <h2>2D correction</h2>
          <p>{floorplan.source.filename}</p>
        </div>
        <span>{floorplan.walls.length} walls</span>
      </div>
      <svg className="floorplan-canvas" viewBox={viewBox} role="img" aria-label="Detected floor plan geometry">
        {floorplan.rooms.map((room) => (
          <polygon
            key={room.id}
            points={room.polygon.map(([x, y]) => `${x},${y}`).join(" ")}
            className="room-shape"
          />
        ))}
        {floorplan.walls.map((wall) => (
          <WallLine
            key={wall.id}
            wall={wall}
            selected={wall.id === selectedWallId}
            onSelectWall={onSelectWall}
          />
        ))}
        {floorplan.openings.map((opening) => (
          <circle
            key={opening.id}
            cx={opening.position[0]}
            cy={opening.position[1]}
            r={Math.max(opening.width / 4, 0.06)}
            className={opening.kind === "window" ? "opening-marker window" : "opening-marker door"}
          />
        ))}
      </svg>
      {selectedWall ? (
        <div className="inspector">
          <label>
            Wall height
            <input
              type="number"
              min="1"
              max="8"
              step="0.1"
              value={selectedWall.height}
              onChange={(event) => onWallHeightChange(selectedWall.id, Number(event.target.value))}
            />
          </label>
          <span>{selectedWall.id}</span>
        </div>
      ) : null}
    </section>
  );
}

function WallLine({
  wall,
  selected,
  onSelectWall
}: {
  wall: Wall;
  selected: boolean;
  onSelectWall: (wallId: string) => void;
}) {
  const [start, end] = [wall.points[0], wall.points[wall.points.length - 1]];
  if (!start || !end) {
    return null;
  }
  return (
    <line
      x1={start[0]}
      y1={start[1]}
      x2={end[0]}
      y2={end[1]}
      className={selected ? "wall-line selected" : "wall-line"}
      strokeWidth={Math.max(wall.thickness, 0.08)}
      onClick={() => onSelectWall(wall.id)}
    />
  );
}

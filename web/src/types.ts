export type Point2D = [number, number];

export interface Wall {
  id: string;
  points: Point2D[];
  thickness: number;
  height: number;
}

export interface Opening {
  id: string;
  kind: string;
  position: Point2D;
  width: number;
  wall_id?: string | null;
}

export interface Room {
  id: string;
  polygon: Point2D[];
  label?: string | null;
}

export interface SymbolItem {
  id: string;
  kind: string;
  bbox: [number, number, number, number];
  confidence: number;
}

export interface FloorPlan {
  source: {
    filename: string;
    content_type: string;
    page: number;
    image_size: [number, number];
    scale?: number | null;
  };
  walls: Wall[];
  openings: Opening[];
  rooms: Room[];
  symbols: SymbolItem[];
  scene: {
    units: string;
    wall_height: number;
    floor_thickness: number;
  };
}

import { useEffect, useRef } from "react";
import * as THREE from "three";
import type { FloorPlan } from "./types";

interface Props {
  floorplan: FloorPlan | null;
}

export function ThreeViewer({ floorplan }: Props) {
  const mountRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    const mount = mountRef.current;
    if (!mount) {
      return;
    }

    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0xf6f7f9);
    const camera = new THREE.PerspectiveCamera(45, mount.clientWidth / mount.clientHeight, 0.1, 1000);
    camera.position.set(4, 5, 6);
    camera.lookAt(0, 0, 0);

    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setPixelRatio(window.devicePixelRatio);
    renderer.setSize(mount.clientWidth, mount.clientHeight);
    mount.appendChild(renderer.domElement);

    const light = new THREE.HemisphereLight(0xffffff, 0x8899aa, 2.2);
    scene.add(light);
    scene.add(new THREE.GridHelper(20, 20, 0xb8c0cc, 0xd9dee6));

    if (floorplan) {
      addFloorPlan(scene, floorplan);
    }

    let frame = 0;
    const animate = () => {
      frame = requestAnimationFrame(animate);
      renderer.render(scene, camera);
    };
    animate();

    const resize = () => {
      if (!mount.clientWidth || !mount.clientHeight) {
        return;
      }
      camera.aspect = mount.clientWidth / mount.clientHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(mount.clientWidth, mount.clientHeight);
    };
    window.addEventListener("resize", resize);

    return () => {
      cancelAnimationFrame(frame);
      window.removeEventListener("resize", resize);
      renderer.dispose();
      mount.removeChild(renderer.domElement);
    };
  }, [floorplan]);

  return <div ref={mountRef} className="viewer" />;
}

function addFloorPlan(scene: THREE.Scene, floorplan: FloorPlan) {
  const wallMaterial = new THREE.MeshStandardMaterial({ color: 0x48515f, roughness: 0.75 });
  const floorMaterial = new THREE.MeshStandardMaterial({ color: 0xd8d6cf, roughness: 0.9 });
  const points = floorplan.rooms.flatMap((room) => room.polygon);
  if (points.length > 0) {
    const xs = points.map(([x]) => x);
    const ys = points.map(([, y]) => y);
    const minX = Math.min(...xs);
    const maxX = Math.max(...xs);
    const minY = Math.min(...ys);
    const maxY = Math.max(...ys);
    const floor = new THREE.Mesh(
      new THREE.BoxGeometry(Math.max(maxX - minX, 0.1), 0.08, Math.max(maxY - minY, 0.1)),
      floorMaterial
    );
    floor.position.set((minX + maxX) / 2, -0.04, (minY + maxY) / 2);
    scene.add(floor);
  }

  for (const wall of floorplan.walls) {
    const start = wall.points[0];
    const end = wall.points[wall.points.length - 1];
    if (!start || !end) {
      continue;
    }
    const dx = end[0] - start[0];
    const dz = end[1] - start[1];
    const length = Math.hypot(dx, dz);
    if (length <= 0) {
      continue;
    }
    const mesh = new THREE.Mesh(
      new THREE.BoxGeometry(length, wall.height, wall.thickness),
      wallMaterial
    );
    mesh.position.set((start[0] + end[0]) / 2, wall.height / 2, (start[1] + end[1]) / 2);
    mesh.rotation.y = -Math.atan2(dz, dx);
    scene.add(mesh);
  }

  for (const opening of floorplan.openings) {
    const material = new THREE.MeshStandardMaterial({
      color: opening.kind === "window" ? 0x4fa4d8 : 0xb87943,
      transparent: true,
      opacity: opening.kind === "window" ? 0.62 : 0.78
    });
    const mesh = new THREE.Mesh(
      new THREE.BoxGeometry(Math.max(opening.width, 0.1), Math.max(opening.height, 0.1), 0.04),
      material
    );
    mesh.position.set(
      opening.position[0],
      opening.sill_height + opening.height / 2,
      opening.position[1]
    );
    scene.add(mesh);
  }
}

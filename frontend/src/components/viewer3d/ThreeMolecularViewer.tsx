import React, { useRef, useEffect, useState, useMemo } from 'react';
import * as THREE from 'three';
import {
  getStructureForModel,
  generateTfR1VhhComplex,
  MacromolecularStructureData,
  PdbResidue,
  SidechainBond,
  SidechainAtom,
  HydrogenBond,
} from './pdbCoordinates';
import {
  Maximize2,
  Minimize2,
  RotateCcw,
  Play,
  Pause,
  Focus,
  Sparkles,
  Layers,
  ChevronDown,
  Eye,
  Info,
} from 'lucide-react';

export interface ThreeMolecularViewerProps {
  targetId?: string;
  sequence?: string;
  plddtScores?: number[];
  selectedResidueIndex?: number | null;
  onSelectResidue?: (index: number | null) => void;
  className?: string;
  height?: number | string;
  isSimulatedDemo?: boolean;
  minimalHud?: boolean;
}

export type RepresentationMode = 'ribbon' | 'surface' | 'sticks';
export type ColorMode = 'chain' | 'plddt' | 'secondary';

// ---------------------------------------------------------------------------
// DOUBLE-REFLECTION ROTATION MINIMIZING FRAME (RMF / BISHOP FRAME)
// Guarantees smooth, continuous ribbon transport with zero gimbal flipping
// ---------------------------------------------------------------------------
function computeRotationMinimizingFrames(points: THREE.Vector3[]): {
  tangents: THREE.Vector3[];
  normals: THREE.Vector3[];
  binormals: THREE.Vector3[];
} {
  const n = points.length;
  const tangents: THREE.Vector3[] = [];
  const normals: THREE.Vector3[] = [];
  const binormals: THREE.Vector3[] = [];

  if (n < 2) return { tangents, normals, binormals };

  // 1. Tangents
  for (let i = 0; i < n; i++) {
    const prev = points[Math.max(0, i - 1)];
    const next = points[Math.min(n - 1, i + 1)];
    const t = new THREE.Vector3().subVectors(next, prev).normalize();
    if (t.lengthSq() < 0.0001) t.set(0, 1, 0);
    tangents.push(t);
  }

  // 2. Initial Frame
  const t0 = tangents[0];
  let initUp = new THREE.Vector3(0, 1, 0);
  if (Math.abs(t0.dot(initUp)) > 0.85) {
    initUp = new THREE.Vector3(1, 0, 0);
  }
  const n0 = new THREE.Vector3().crossVectors(t0, initUp).normalize();
  const b0 = new THREE.Vector3().crossVectors(t0, n0).normalize();
  normals.push(n0);
  binormals.push(b0);

  // 3. Double-reflection parallel transport
  for (let i = 0; i < n - 1; i++) {
    const x1 = points[i];
    const x2 = points[i + 1];
    const t1 = tangents[i];
    const t2 = tangents[i + 1];

    const v1 = new THREE.Vector3().subVectors(x2, x1);
    const c1 = v1.lengthSq();
    if (c1 < 0.00001) {
      normals.push(normals[i].clone());
      binormals.push(binormals[i].clone());
      continue;
    }

    const nL = normals[i].clone().sub(v1.clone().multiplyScalar((2 / c1) * v1.dot(normals[i])));
    const tL = t1.clone().sub(v1.clone().multiplyScalar((2 / c1) * v1.dot(t1)));

    const v2 = new THREE.Vector3().subVectors(t2, tL);
    const c2 = v2.lengthSq();
    let nextNormal: THREE.Vector3;
    if (c2 > 0.00001) {
      nextNormal = nL.clone().sub(v2.clone().multiplyScalar((2 / c2) * v2.dot(nL))).normalize();
    } else {
      nextNormal = normals[i].clone();
    }

    const nextBinormal = new THREE.Vector3().crossVectors(t2, nextNormal).normalize();
    normals.push(nextNormal);
    binormals.push(nextBinormal);
  }

  return { tangents, normals, binormals };
}

// ---------------------------------------------------------------------------
// Continuous Protein Cartoon Ribbon Extrusion with Parallel Transport
// Single unbroken Catmull-Rom spline per chain with continuous frame & variable cross-section
// Helices: smooth flat oval ribbon
// Sheets: sleek flat ribbon with tapered terminal arrowheads
// Loops: rounded tube
// ---------------------------------------------------------------------------
function createContinuousChainRibbon(
  chainRes: PdbResidue[],
  getResColor: (r: PdbResidue) => THREE.Color,
  subdivisions: number = 6
): THREE.BufferGeometry {
  const n = chainRes.length;
  if (n < 2) return new THREE.BufferGeometry();

  const points = chainRes.map((r) => new THREE.Vector3(...r.ca));
  const curve = new THREE.CatmullRomCurve3(points, false, 'centripetal', 0.5);
  const totalSteps = Math.max(8, (n - 1) * subdivisions);
  const sampledPoints = curve.getPoints(totalSteps);

  const { normals, binormals } = computeRotationMinimizingFrames(sampledPoints);

  const positions: number[] = [];
  const normAttrs: number[] = [];
  const colors: number[] = [];
  const indices: number[] = [];

  const getDims = (sec: 'helix' | 'sheet' | 'loop') => {
    switch (sec) {
      case 'helix':
        return { w: 1.65, t: 0.28 };
      case 'sheet':
        return { w: 2.10, t: 0.20 };
      case 'loop':
      default:
        return { w: 0.45, t: 0.45 };
    }
  };

  for (let i = 0; i <= totalSteps; i++) {
    const p = sampledPoints[i];
    const b = binormals[i];
    const norm = normals[i];

    const u = (i / totalSteps) * (n - 1);
    const idx0 = Math.min(Math.floor(u), n - 1);
    const idx1 = Math.min(idx0 + 1, n - 1);
    const frac = u - idx0;

    const r0 = chainRes[idx0];
    const r1 = chainRes[idx1];

    const d0 = getDims(r0.sec);
    const d1 = getDims(r1.sec);

    let w = d0.w * (1 - frac) + d1.w * frac;
    let t = d0.t * (1 - frac) + d1.t * frac;

    // Arrowhead taper if leaving a beta strand
    if (r0.sec === 'sheet' && r1.sec !== 'sheet') {
      w = d0.w * (1.25 - frac * 0.85);
    }

    const c0 = getResColor(r0);
    const c1 = getResColor(r1);
    const rCol = c0.r * (1 - frac) + c1.r * frac;
    const gCol = c0.g * (1 - frac) + c1.g * frac;
    const bCol = c0.b * (1 - frac) + c1.b * frac;

    const hw = w / 2;
    const ht = t / 2;

    // 4 profile vertices per slice
    // 0: top right
    positions.push(p.x + b.x * hw + norm.x * ht, p.y + b.y * hw + norm.y * ht, p.z + b.z * hw + norm.z * ht);
    normAttrs.push(norm.x, norm.y, norm.z);
    colors.push(rCol, gCol, bCol);

    // 1: top left
    positions.push(p.x - b.x * hw + norm.x * ht, p.y - b.y * hw + norm.y * ht, p.z - b.z * hw + norm.z * ht);
    normAttrs.push(norm.x, norm.y, norm.z);
    colors.push(rCol, gCol, bCol);

    // 2: bottom left
    positions.push(p.x - b.x * hw - norm.x * ht, p.y - b.y * hw - norm.y * ht, p.z - b.z * hw - norm.z * ht);
    normAttrs.push(-norm.x, -norm.y, -norm.z);
    colors.push(rCol, gCol, bCol);

    // 3: bottom right
    positions.push(p.x + b.x * hw - norm.x * ht, p.y + b.y * hw - norm.y * ht, p.z + b.z * hw - norm.z * ht);
    normAttrs.push(-norm.x, -norm.y, -norm.z);
    colors.push(rCol, gCol, bCol);
  }

  for (let i = 0; i < totalSteps; i++) {
    const c = i * 4;
    const next = (i + 1) * 4;

    // Top face
    indices.push(c + 0, c + 1, next + 0);
    indices.push(c + 1, next + 1, next + 0);

    // Bottom face
    indices.push(c + 2, c + 3, next + 2);
    indices.push(c + 3, next + 3, next + 2);

    // Right edge
    indices.push(c + 3, c + 0, next + 3);
    indices.push(c + 0, next + 0, next + 3);

    // Left edge
    indices.push(c + 1, c + 2, next + 1);
    indices.push(c + 2, next + 2, next + 1);
  }

  const geom = new THREE.BufferGeometry();
  geom.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
  geom.setAttribute('normal', new THREE.Float32BufferAttribute(normAttrs, 3));
  geom.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));
  geom.setIndex(indices);
  geom.computeVertexNormals();

  return geom;
}

export const ThreeMolecularViewer: React.FC<ThreeMolecularViewerProps> = ({
  targetId = 'tfr1_vhh',
  sequence,
  plddtScores,
  selectedResidueIndex = null,
  onSelectResidue,
  className = '',
  height = 540,
  isSimulatedDemo = false,
  minimalHud = false,
}) => {
  const mountRef = useRef<HTMLDivElement | null>(null);

  // Manual Model Selection Override (null = follow targetId prop)
  const [selectedModelKey, setSelectedModelKey] = useState<string | null>(null);

  // Reset manual selection when targetId prop changes so candidate switcher immediately updates 3D view
  useEffect(() => {
    setSelectedModelKey(null);
  }, [targetId]);

  // Active Structure Data dynamically computed from props and state
  const complexData: MacromolecularStructureData = useMemo(() => {
    const effectiveKey = selectedModelKey || targetId || 'tfr1_vhh';
    return getStructureForModel(effectiveKey, sequence, plddtScores);
  }, [selectedModelKey, targetId, sequence, plddtScores]);

  // Viewport Settings
  const [isFullscreen, setIsFullscreen] = useState<boolean>(false);
  const [isRotating, setIsRotating] = useState<boolean>(true);
  const [representation, setRepresentation] = useState<RepresentationMode>('ribbon');
  const [colorMode, setColorMode] = useState<ColorMode>('chain');
  const [showSticks, setShowSticks] = useState<boolean>(true);
  const [showHbonds, setShowHbonds] = useState<boolean>(true);

  // Hover Tooltip State
  const [hoveredResidue, setHoveredResidue] = useState<PdbResidue | null>(null);
  const [mouseCoord, setMouseCoord] = useState<{ x: number; y: number }>({ x: 0, y: 0 });

  // Three.js Scene References
  const sceneRef = useRef<THREE.Scene | null>(null);
  const cameraRef = useRef<THREE.PerspectiveCamera | null>(null);
  const rendererRef = useRef<THREE.WebGLRenderer | null>(null);
  const rootGroupRef = useRef<THREE.Group | null>(null);
  const animFrameRef = useRef<number>(0);

  // Orbit Control References
  const isDraggingRef = useRef<boolean>(false);
  const dragButtonRef = useRef<number>(0);
  const mousePosRef = useRef<{ x: number; y: number }>({ x: 0, y: 0 });
  const rotVelocityRef = useRef<{ x: number; y: number }>({ x: 0, y: 0 });
  const zoomDistRef = useRef<number>(100);

  // Raycaster for residue picking
  const raycasterRef = useRef<THREE.Raycaster>(new THREE.Raycaster());
  const mouseVecRef = useRef<THREE.Vector2>(new THREE.Vector2());

  // Handle Escape key to exit fullscreen
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isFullscreen) {
        setIsFullscreen(false);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isFullscreen]);

  // 1. Initialize Scene & Renderer
  useEffect(() => {
    const container = mountRef.current;
    if (!container) return;

    const width = container.clientWidth || 800;
    const height = container.clientHeight || 540;

    // Deep charcoal studio background
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x080808);
    sceneRef.current = scene;

    const camera = new THREE.PerspectiveCamera(38, width / height, 0.1, 1000);
    camera.position.set(0, 2, zoomDistRef.current);
    camera.lookAt(0, 0, 0);
    cameraRef.current = camera;

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false, powerPreference: 'high-performance' });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.25;
    rendererRef.current = renderer;

    while (container.firstChild) {
      container.removeChild(container.firstChild);
    }
    container.appendChild(renderer.domElement);

    // Studio Lighting (Crisp directional key light + cool rim light + fill)
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.7);
    scene.add(ambientLight);

    // Key light (top-left)
    const keyLight = new THREE.DirectionalLight(0xffffff, 2.2);
    keyLight.position.set(30, 45, 40);
    scene.add(keyLight);

    // Rim light (bottom-right blue rim to highlight the dark ribbon edges!)
    const rimLight = new THREE.DirectionalLight(0x38bdf8, 1.4);
    rimLight.position.set(-30, -20, -35);
    scene.add(rimLight);

    // Fill light
    const fillLight = new THREE.DirectionalLight(0xffeedd, 0.8);
    fillLight.position.set(-25, 20, 30);
    scene.add(fillLight);

    const rootGroup = new THREE.Group();
    // Initial aesthetic orientation matching Dyno Phi's showcase angle
    rootGroup.rotation.set(-0.15, 0.45, 0.05);
    scene.add(rootGroup);
    rootGroupRef.current = rootGroup;

    // Resize Handler
    const handleResize = () => {
      if (!container || !camera || !renderer) return;
      camera.aspect = container.clientWidth / container.clientHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(container.clientWidth, container.clientHeight);
    };

    const resizeObserver = new ResizeObserver(handleResize);
    resizeObserver.observe(container);

    // Animation loop
    const animate = () => {
      if (rootGroupRef.current) {
        if (isRotating && !isDraggingRef.current) {
          rootGroupRef.current.rotation.y += 0.0035;
        }

        if (!isDraggingRef.current) {
          rootGroupRef.current.rotation.y += rotVelocityRef.current.y;
          rootGroupRef.current.rotation.x += rotVelocityRef.current.x;
          rotVelocityRef.current.x *= 0.92;
          rotVelocityRef.current.y *= 0.92;
        }
      }

      renderer.render(scene, camera);
      animFrameRef.current = requestAnimationFrame(animate);
    };

    animate();

    return () => {
      cancelAnimationFrame(animFrameRef.current);
      resizeObserver.disconnect();
      if (renderer.domElement && container.contains(renderer.domElement)) {
        container.removeChild(renderer.domElement);
      }
      renderer.dispose();
    };
  }, []);

  // Handle Fullscreen / Resize changes
  useEffect(() => {
    const container = mountRef.current;
    const camera = cameraRef.current;
    const renderer = rendererRef.current;
    if (!container || !camera || !renderer) return;

    const timer = setTimeout(() => {
      camera.aspect = container.clientWidth / container.clientHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(container.clientWidth, container.clientHeight);
    }, 60);

    return () => clearTimeout(timer);
  }, [isFullscreen]);

  // Helper to get color for a residue based on colorMode
  const getResidueColor = (r: PdbResidue): THREE.Color => {
    if (colorMode === 'plddt') {
      const p = r.defaultPlddt;
      if (p >= 90) return new THREE.Color(0x1d4ed8); // Deep royal blue
      if (p >= 70) return new THREE.Color(0x06b6d4); // Cyan
      if (p >= 50) return new THREE.Color(0xeab308); // Yellow
      return new THREE.Color(0xf97316); // Orange
    }

    if (colorMode === 'secondary') {
      if (r.sec === 'helix') return new THREE.Color(0x8b5cf6); // Violet
      if (r.sec === 'sheet') return new THREE.Color(0x0284c7); // Sky blue
      return new THREE.Color(0x475569); // Slate grey
    }

    // Default: Chain coloring (Dyno style)
    if (r.chain === 'B') {
      return new THREE.Color(0x2563eb); // Vibrant electric cobalt blue
    }
    return new THREE.Color(0x2d323e); // Matte dark charcoal/slate
  };

  // 2. Build 3D Molecular Objects (Ribbon, Surface, Sticks)
  useEffect(() => {
    const rootGroup = rootGroupRef.current;
    if (!rootGroup) return;

    // Clear old meshes safely
    while (rootGroup.children.length > 0) {
      const child = rootGroup.children[0] as any;
      rootGroup.remove(child);
      if (child.geometry) child.geometry.dispose();
      if (child.material) {
        if (Array.isArray(child.material)) child.material.forEach((m: any) => m.dispose());
        else child.material.dispose();
      }
    }

    const residues = complexData.residues;
    if (residues.length === 0) return;

    // -------------------------------------------------------------------------
    // A. CARTOON RIBBON REPRESENTATION
    // -------------------------------------------------------------------------
    if (representation === 'ribbon') {
      const chains = Array.from(new Set(residues.map((r) => r.chain)));

      chains.forEach((chainId) => {
        const chainRes = residues.filter((r) => r.chain === chainId);
        if (chainRes.length < 2) return;

        const geom = createContinuousChainRibbon(chainRes, getResidueColor, 6);
        const mat = new THREE.MeshStandardMaterial({
          vertexColors: true,
          roughness: chainId === 'B' ? 0.22 : 0.38,
          metalness: 0.15,
          side: THREE.DoubleSide,
        });
        const mesh = new THREE.Mesh(geom, mat);
        rootGroup.add(mesh);
      });
    }

    // -------------------------------------------------------------------------
    // B. MOLECULAR SURFACE REPRESENTATION
    // -------------------------------------------------------------------------
    if (representation === 'surface') {
      const sphereGeom = new THREE.SphereGeometry(1.4, 16, 16);
      residues.forEach((r) => {
        const color = getResidueColor(r);
        const mat = new THREE.MeshStandardMaterial({
          color,
          roughness: 0.45,
          metalness: 0.1,
          transparent: true,
          opacity: 0.88,
        });
        const sphere = new THREE.Mesh(sphereGeom, mat);
        sphere.position.set(...r.ca);
        rootGroup.add(sphere);
      });
    }

    // -------------------------------------------------------------------------
    // C. ATOMIC STICKS (Backbone Trace + Sidechain Sticks)
    // -------------------------------------------------------------------------
    if (representation === 'sticks') {
      const atomGeom = new THREE.SphereGeometry(0.5, 12, 12);

      // C-alpha spheres
      residues.forEach((r) => {
        const color = getResidueColor(r);
        const mat = new THREE.MeshStandardMaterial({ color, roughness: 0.3, metalness: 0.2 });
        const sphere = new THREE.Mesh(atomGeom, mat);
        sphere.position.set(...r.ca);
        rootGroup.add(sphere);
      });

      // Backbone connection cylinders
      for (let i = 0; i < residues.length - 1; i++) {
        if (residues[i].chain !== residues[i + 1].chain) continue;
        const p1 = new THREE.Vector3(...residues[i].ca);
        const p2 = new THREE.Vector3(...residues[i + 1].ca);
        const dist = p1.distanceTo(p2);
        if (dist > 5.0) continue; // Skip strand jumps

        const cylGeom = new THREE.CylinderGeometry(0.25, 0.25, dist, 10);
        const cylMat = new THREE.MeshStandardMaterial({
          color: getResidueColor(residues[i]),
          roughness: 0.3,
          metalness: 0.2,
        });
        const cyl = new THREE.Mesh(cylGeom, cylMat);
        cyl.position.copy(p1).add(p2).multiplyScalar(0.5);
        cyl.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), p2.clone().sub(p1).normalize());
        rootGroup.add(cyl);
      }
    }

    // -------------------------------------------------------------------------
    // D. INTERFACE SIDECHAIN STICKS (CPK: Green C, Red O, Blue N, Yellow S)
    // -------------------------------------------------------------------------
    if (showSticks && complexData.interfaceBonds.length > 0) {
      const elementColors: Record<string, number> = {
        C: 0x22c55e, // Emerald green carbon (signature active-site stick)
        N: 0x3b82f6, // Blue nitrogen
        O: 0xef4444, // Red oxygen
        S: 0xeab308, // Yellow sulfur
      };

      const sphereGeom = new THREE.SphereGeometry(0.32, 12, 12);
      complexData.interfaceAtoms.forEach((atom) => {
        const atomMat = new THREE.MeshStandardMaterial({
          color: elementColors[atom.element] || 0x22c55e,
          roughness: 0.25,
          metalness: 0.15,
        });
        const sphere = new THREE.Mesh(sphereGeom, atomMat);
        sphere.position.set(...atom.pos);
        rootGroup.add(sphere);
      });

      complexData.interfaceBonds.forEach((bond) => {
        const p1 = new THREE.Vector3(...bond.from);
        const p2 = new THREE.Vector3(...bond.to);
        const dist = p1.distanceTo(p2);
        if (dist === 0) return;

        const cylGeom = new THREE.CylinderGeometry(0.18, 0.18, dist, 10);
        const bondMat = new THREE.MeshStandardMaterial({
          color: elementColors[bond.elementFrom] || 0x22c55e,
          roughness: 0.25,
          metalness: 0.15,
        });

        const cyl = new THREE.Mesh(cylGeom, bondMat);
        cyl.position.copy(p1).add(p2).multiplyScalar(0.5);
        cyl.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), p2.clone().sub(p1).normalize());
        rootGroup.add(cyl);
      });
    }

    // -------------------------------------------------------------------------
    // E. HYDROGEN BOND DASHED LINES
    // -------------------------------------------------------------------------
    if (showHbonds && complexData.hydrogenBonds.length > 0) {
      complexData.hydrogenBonds.forEach((hb) => {
        const p1 = new THREE.Vector3(...hb.donor);
        const p2 = new THREE.Vector3(...hb.acceptor);

        const lineGeom = new THREE.BufferGeometry().setFromPoints([p1, p2]);
        const lineMat = new THREE.LineDashedMaterial({
          color: 0xfacc15, // Golden yellow dashed H-bond
          dashSize: 0.6,
          gapSize: 0.35,
        });

        const line = new THREE.Line(lineGeom, lineMat);
        line.computeLineDistances();
        rootGroup.add(line);
      });
    }
  }, [complexData, representation, colorMode, showSticks, showHbonds]);

  // Mouse Orbit, Pan, and Raycasting
  const handleMouseDown = (e: React.MouseEvent<HTMLDivElement>) => {
    isDraggingRef.current = true;
    dragButtonRef.current = e.button;
    mousePosRef.current = { x: e.clientX, y: e.clientY };
  };

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    const container = mountRef.current;
    if (container) {
      const rect = container.getBoundingClientRect();
      setMouseCoord({ x: e.clientX - rect.left, y: e.clientY - rect.top });
    }

    if (!isDraggingRef.current || !rootGroupRef.current || !cameraRef.current) return;

    const dx = e.clientX - mousePosRef.current.x;
    const dy = e.clientY - mousePosRef.current.y;

    if (dragButtonRef.current === 0 && !e.shiftKey) {
      const rotSpeed = 0.0075;
      rootGroupRef.current.rotation.y += dx * rotSpeed;
      rootGroupRef.current.rotation.x += dy * rotSpeed;
      rotVelocityRef.current = { x: dy * rotSpeed * 0.35, y: dx * rotSpeed * 0.35 };
    } else {
      cameraRef.current.position.x -= dx * 0.08;
      cameraRef.current.position.y += dy * 0.08;
    }

    mousePosRef.current = { x: e.clientX, y: e.clientY };
  };

  const handleMouseUp = () => {
    isDraggingRef.current = false;
  };

  const handleWheel = (e: React.WheelEvent<HTMLDivElement>) => {
    e.preventDefault();
    if (!cameraRef.current) return;
    const zoomFactor = e.deltaY < 0 ? 0.92 : 1.08;
    zoomDistRef.current = Math.max(25, Math.min(160, zoomDistRef.current * zoomFactor));
    cameraRef.current.position.set(0, 8, zoomDistRef.current);
  };

  const handleResetCamera = () => {
    if (!cameraRef.current || !rootGroupRef.current) return;
    rootGroupRef.current.rotation.set(-0.15, 0.45, 0.05);
    rotVelocityRef.current = { x: 0, y: 0 };
    zoomDistRef.current = 100;
    cameraRef.current.position.set(0, 2, 100);
    cameraRef.current.lookAt(0, 0, 0);
  };

  return (
    <div
      className={`relative select-none overflow-hidden bg-[#080808] ${
        isFullscreen
          ? 'fixed inset-0 z-50 bg-[#080808] w-screen h-screen'
          : `w-full ${className}`
      }`}
      style={{ height: isFullscreen ? '100vh' : height }}
    >
      {/* 3D Canvas Mount */}
      <div
        ref={mountRef}
        className="w-full h-full cursor-grab active:cursor-grabbing block"
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
        onWheel={handleWheel}
        onContextMenu={(e) => e.preventDefault()}
      />

      {/* Minimal Top Header inside Viewer (Dyno Phi Minimalist) */}
      <div className="absolute top-3 left-4 right-4 z-10 flex flex-wrap items-center justify-between gap-3 pointer-events-none">
        {/* Model Title & Clean Minimal Selector */}
        <div className="pointer-events-auto flex items-center space-x-3">
          <span className="text-[#F5F5F5] font-medium text-xs tracking-wide font-sans">
            {complexData.title}
          </span>

          <select
            value={selectedModelKey || targetId || 'tfr1_vhh'}
            onChange={(e) => setSelectedModelKey(e.target.value)}
            className="bg-[#141414]/90 hover:bg-[#1C1C1C] text-[#A3A3A3] hover:text-[#F5F5F5] border border-[#282828] rounded px-2 py-0.5 text-[11px] font-sans focus:outline-none transition-colors cursor-pointer"
          >
            {targetId && (
              <option value={targetId} className="bg-[#141414] text-[#F5F5F5]">
                Active: {targetId}
              </option>
            )}
            <option value="tfr1_vhh" className="bg-[#141414] text-[#F5F5F5]">TfR1 with a VHH</option>
            <option value="1UBQ" className="bg-[#141414] text-[#F5F5F5]">Ubiquitin (1UBQ)</option>
            <option value="1n5u" className="bg-[#141414] text-[#F5F5F5]">1N5U Coiled Coil</option>
          </select>
        </div>

        {/* Minimal Monochrome Controls */}
        <div className="pointer-events-auto flex items-center space-x-3 text-xs">
          {/* Representation Selector */}
          <div className="flex items-center space-x-1.5 text-[11px] font-sans text-[#666666]">
            <button
              onClick={() => setRepresentation('ribbon')}
              className={`px-1.5 py-0.5 rounded transition-colors ${
                representation === 'ribbon' ? 'text-[#F5F5F5] font-medium bg-white/10' : 'hover:text-[#F5F5F5]'
              }`}
            >
              Ribbon
            </button>
            <span>·</span>
            <button
              onClick={() => setRepresentation('surface')}
              className={`px-1.5 py-0.5 rounded transition-colors ${
                representation === 'surface' ? 'text-[#F5F5F5] font-medium bg-white/10' : 'hover:text-[#F5F5F5]'
              }`}
            >
              Surface
            </button>
            <span>·</span>
            <button
              onClick={() => setRepresentation('sticks')}
              className={`px-1.5 py-0.5 rounded transition-colors ${
                representation === 'sticks' ? 'text-[#F5F5F5] font-medium bg-white/10' : 'hover:text-[#F5F5F5]'
              }`}
            >
              Sticks
            </button>
          </div>

          <div className="h-3 w-px bg-[#262938]" />

          {/* Color Mode */}
          <select
            value={colorMode}
            onChange={(e) => setColorMode(e.target.value as ColorMode)}
            className="bg-transparent text-[#666666] hover:text-[#F5F5F5] text-[11px] font-sans focus:outline-none cursor-pointer"
            title="Color mode"
          >
            <option value="chain" className="bg-[#141414] text-[#F5F5F5]">Chain</option>
            <option value="plddt" className="bg-[#141414] text-[#F5F5F5]">pLDDT</option>
            <option value="secondary" className="bg-[#141414] text-[#F5F5F5]">2° Structure</option>
          </select>

          <div className="h-3 w-px bg-[#262938]" />

          {/* Recenter */}
          <button
            onClick={handleResetCamera}
            className="text-[#666666] hover:text-[#F5F5F5] transition-colors"
            title="Recenter camera"
          >
            <Focus className="w-3.5 h-3.5" />
          </button>

          {/* Fullscreen */}
          <button
            onClick={() => setIsFullscreen(!isFullscreen)}
            className="text-[#666666] hover:text-[#F5F5F5] transition-colors"
            title={isFullscreen ? 'Exit fullscreen' : 'Fullscreen'}
          >
            {isFullscreen ? <Minimize2 className="w-3.5 h-3.5" /> : <Maximize2 className="w-3.5 h-3.5" />}
          </button>
        </div>
      </div>

      {/* Dyno-Style Minimal Floating Legend (Directly on canvas, zero container box) */}
      <div className="absolute bottom-3 left-4 right-4 z-10 pointer-events-none">
        <div className="pointer-events-auto text-[11px] font-sans text-[#A3A3A3] space-y-1.5">
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-1.5">
              <span className="w-2 h-2 rounded-full bg-[#4b5563]" />
              <span className="text-neutral-300">{complexData.chainA.name}</span>
            </div>
            {complexData.chainB && (
              <div className="flex items-center space-x-1.5">
                <span className="w-2 h-2 rounded-full bg-[#2563eb]" />
                <span className="text-[#F5F5F5] font-medium">{complexData.chainB.name}</span>
              </div>
            )}
            <div className="flex items-center space-x-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-[#22c55e]" />
              <span className="text-[#666666]">Active-site sticks</span>
            </div>
            <div className="ml-auto">
              <button
                onClick={() => setIsRotating(!isRotating)}
                className="text-[#666666] hover:text-[#F5F5F5] transition-colors"
                title={isRotating ? 'Pause rotation' : 'Resume rotation'}
              >
                {isRotating ? <Pause className="w-3 h-3 text-neutral-300" /> : <Play className="w-3 h-3" />}
              </button>
            </div>
          </div>

          <div className="flex items-center space-x-6 text-[10px] text-[#666666] pt-1 border-t border-white/5">
            <div>
              <span className="text-[#A3A3A3] mr-1.5">{complexData.chainA.name}:</span>
              <span>{complexData.chainA.protein}</span>
            </div>
            {complexData.chainB && (
              <div>
                <span className="text-[#38BDF8] mr-1.5">{complexData.chainB.name}:</span>
                <span>{complexData.chainB.protein} ({complexData.chainB.designRegions})</span>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

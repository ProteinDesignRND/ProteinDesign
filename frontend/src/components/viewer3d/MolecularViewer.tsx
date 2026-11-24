import React, { useRef, useEffect, useState, useMemo, useCallback } from 'react';
import {
  generateFoldCoordinates,
  getPlddtColor,
  ProteinStructureData,
  AtomCoord,
} from './structureModels';
import {
  RotateCcw,
  Play,
  Pause,
  ZoomIn,
  ZoomOut,
  Maximize2,
  Download,
  Camera,
  Layers,
  Palette,
  ExternalLink,
  Info,
} from 'lucide-react';

export interface MolecularViewerProps {
  targetId: string;
  sequence: string;
  plddtScores?: number[];
  selectedResidueIndex?: number | null;
  onSelectResidue?: (index: number | null) => void;
  className?: string;
  height?: number | string;
  isSimulatedDemo?: boolean;
}

export const MolecularViewer: React.FC<MolecularViewerProps> = ({
  targetId,
  sequence,
  plddtScores,
  selectedResidueIndex = null,
  onSelectResidue,
  className = '',
  height = 520,
  isSimulatedDemo = false,
}) => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const containerRef = useRef<HTMLDivElement | null>(null);

  // Viewer state
  const [style, setStyle] = useState<'cartoon' | 'stick' | 'sphere' | 'surface'>('cartoon');
  const [colorScheme, setColorScheme] = useState<'plddt' | 'secondary' | 'rainbow'>('plddt');
  const [showSidechains, setShowSidechains] = useState<boolean>(false);
  const [isRotating, setIsRotating] = useState<boolean>(true);
  const [hoveredResidue, setHoveredResidue] = useState<AtomCoord | null>(null);

  // Camera transforms
  const cameraRef = useRef({
    rotX: 0.35,
    rotY: -0.45,
    zoom: 1.0,
    panX: 0,
    panY: 0,
    isDragging: false,
    dragButton: 0,
    lastMouseX: 0,
    lastMouseY: 0,
  });

  const structureData: ProteinStructureData = useMemo(() => {
    return generateFoldCoordinates(targetId, sequence, plddtScores);
  }, [targetId, sequence, plddtScores]);

  // Project 3D point to 2D screen coordinates
  const projectPoint = useCallback(
    (
      x: number,
      y: number,
      z: number,
      width: number,
      height: number
    ): { px: number; py: number; depth: number } => {
      const cam = cameraRef.current;

      // Center offset
      const cx = x + cam.panX;
      const cy = y + cam.panY;
      const cz = z;

      // Rotation around Y axis
      const cosY = Math.cos(cam.rotY);
      const sinY = Math.sin(cam.rotY);
      const x1 = cx * cosY + cz * sinY;
      const z1 = -cx * sinY + cz * cosY;

      // Rotation around X axis
      const cosX = Math.cos(cam.rotX);
      const sinX = Math.sin(cam.rotX);
      const y2 = cy * cosX - z1 * sinX;
      const z2 = cy * sinX + z1 * cosX;

      // Perspective projection
      const distance = 160;
      const perspective = distance / (distance + z2 * 0.4);
      const scale = 7.5 * cam.zoom * perspective;

      const px = width / 2 + x1 * scale;
      const py = height / 2 + y2 * scale;

      return { px, py, depth: z2 };
    },
    []
  );

  // Render loop
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let animationFrameId: number;

    const render = () => {
      const width = canvas.width;
      const height = canvas.height;

      ctx.clearRect(0, 0, width, height);

      // Deep scientific space background with subtle radial gradient
      const bgGrad = ctx.createRadialGradient(
        width / 2,
        height / 2,
        40,
        width / 2,
        height / 2,
        width * 0.65
      );
      bgGrad.addColorStop(0, '#0F172A');
      bgGrad.addColorStop(0.7, '#090D16');
      bgGrad.addColorStop(1, '#05070C');
      ctx.fillStyle = bgGrad;
      ctx.fillRect(0, 0, width, height);

      // Subtle scientific coordinate grid lines in background
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.025)';
      ctx.lineWidth = 1;
      const gridSize = 40;
      for (let x = 0; x < width; x += gridSize) {
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, height);
        ctx.stroke();
      }
      for (let y = 0; y < height; y += gridSize) {
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(width, y);
        ctx.stroke();
      }

      if (isRotating && !cameraRef.current.isDragging) {
        cameraRef.current.rotY += 0.006;
      }

      const atoms = structureData.atoms;
      const projectedAtoms = atoms.map((atom) => {
        const proj = projectPoint(atom.x, atom.y, atom.z, width, height);
        return {
          ...atom,
          px: proj.px,
          py: proj.py,
          depth: proj.depth,
        };
      });

      // Sort by depth (painter's algorithm)
      const sorted = [...projectedAtoms].sort((a, b) => b.depth - a.depth);

      // Resolve atom color
      const resolveColor = (atom: AtomCoord): string => {
        if (colorScheme === 'plddt') {
          return getPlddtColor(atom.plddt);
        }
        if (colorScheme === 'secondary') {
          if (atom.secondaryStructure === 'helix') return '#A855F7'; // Purple
          if (atom.secondaryStructure === 'sheet') return '#F59E0B'; // Amber
          return '#38BDF8'; // Sky blue
        }
        // Rainbow from N-term to C-term
        const ratio = atom.residueIndex / atoms.length;
        const hue = Math.round(240 * (1 - ratio));
        return `hsl(${hue}, 85%, 60%)`;
      };

      // 1. Draw backbone ribbon / tube
      if (style === 'cartoon' || style === 'surface') {
        ctx.lineCap = 'round';
        ctx.lineJoin = 'round';

        for (let i = 0; i < projectedAtoms.length - 1; i++) {
          const a1 = projectedAtoms[i];
          const a2 = projectedAtoms[i + 1];

          const color = resolveColor(a1);
          const isHelix = a1.secondaryStructure === 'helix';
          const isSheet = a1.secondaryStructure === 'sheet';

          // Ribbon thickness based on depth & secondary structure
          const depthAlpha = Math.max(0.35, Math.min(1, 1 - a1.depth / 150));
          const baseWidth = isHelix ? 8.5 : isSheet ? 7.0 : 4.0;
          const ribbonWidth = baseWidth * cameraRef.current.zoom * (150 / (150 + a1.depth * 0.3));

          ctx.beginPath();
          ctx.moveTo(a1.px, a1.py);
          ctx.lineTo(a2.px, a2.py);

          ctx.strokeStyle = color;
          ctx.globalAlpha = depthAlpha * (style === 'surface' ? 0.45 : 0.95);
          ctx.lineWidth = Math.max(2, ribbonWidth);
          ctx.stroke();

          // Ribbon shine/highlight
          ctx.beginPath();
          ctx.moveTo(a1.px, a1.py);
          ctx.lineTo(a2.px, a2.py);
          ctx.strokeStyle = 'rgba(255, 255, 255, 0.4)';
          ctx.globalAlpha = depthAlpha * 0.4;
          ctx.lineWidth = Math.max(1, ribbonWidth * 0.25);
          ctx.stroke();
        }
        ctx.globalAlpha = 1.0;
      }

      // 2. Draw atoms / spheres / sidechains
      sorted.forEach((atom) => {
        const isSelected = selectedResidueIndex === atom.residueIndex;
        const isHovered = hoveredResidue?.residueIndex === atom.residueIndex;
        const color = resolveColor(atom);

        // Perspective radius
        const scaleFactor = 150 / (150 + atom.depth * 0.35);
        let radius = (style === 'sphere' ? 14 : style === 'stick' ? 6 : 4.5) * cameraRef.current.zoom * scaleFactor;
        radius = Math.max(2.5, radius);

        const depthFade = Math.max(0.4, Math.min(1, 1 - atom.depth / 180));

        // Draw atom sphere with radial specular lighting
        const grad = ctx.createRadialGradient(
          atom.px - radius * 0.35,
          atom.py - radius * 0.35,
          radius * 0.1,
          atom.px,
          atom.py,
          radius
        );
        grad.addColorStop(0, '#FFFFFF');
        grad.addColorStop(0.3, color);
        grad.addColorStop(1, '#050B14');

        ctx.beginPath();
        ctx.arc(atom.px, atom.py, radius, 0, Math.PI * 2);
        ctx.fillStyle = grad;
        ctx.globalAlpha = depthFade;
        ctx.fill();

        // Selected / Hovered residue halo & annotation pin
        if (isSelected || isHovered) {
          ctx.beginPath();
          ctx.arc(atom.px, atom.py, radius + 7, 0, Math.PI * 2);
          ctx.strokeStyle = isSelected ? '#3B82F6' : '#60A5FA';
          ctx.lineWidth = 2.5;
          ctx.globalAlpha = 0.9;
          ctx.stroke();

          // Outer pulsing ring
          ctx.beginPath();
          ctx.arc(atom.px, atom.py, radius + 12, 0, Math.PI * 2);
          ctx.strokeStyle = 'rgba(59, 130, 246, 0.4)';
          ctx.lineWidth = 1.5;
          ctx.stroke();

          // 3D Callout Pin
          const pinX = atom.px + 24;
          const pinY = atom.py - 24;
          ctx.beginPath();
          ctx.moveTo(atom.px, atom.py);
          ctx.lineTo(pinX, pinY);
          ctx.lineTo(pinX + 70, pinY);
          ctx.strokeStyle = '#60A5FA';
          ctx.lineWidth = 1.5;
          ctx.stroke();

          // Tooltip badge
          ctx.fillStyle = 'rgba(15, 23, 42, 0.92)';
          ctx.strokeStyle = '#3B82F6';
          ctx.lineWidth = 1;
          ctx.fillRect(pinX + 5, pinY - 18, 110, 28);
          ctx.strokeRect(pinX + 5, pinY - 18, 110, 28);

          ctx.fillStyle = '#FFFFFF';
          ctx.font = '600 11px Inter, sans-serif';
          ctx.fillText(`${atom.residueName} ${atom.residueIndex} (pLDDT: ${atom.plddt})`, pinX + 10, pinY);
        }

        // Sidechain sticks (if enabled)
        if (showSidechains) {
          const scX = atom.px + Math.sin(atom.residueIndex) * 12 * cameraRef.current.zoom;
          const scY = atom.py + Math.cos(atom.residueIndex) * 12 * cameraRef.current.zoom;
          ctx.beginPath();
          ctx.moveTo(atom.px, atom.py);
          ctx.lineTo(scX, scY);
          ctx.strokeStyle = color;
          ctx.lineWidth = 1.5;
          ctx.globalAlpha = depthFade * 0.7;
          ctx.stroke();

          ctx.beginPath();
          ctx.arc(scX, scY, 2.5, 0, Math.PI * 2);
          ctx.fillStyle = '#E2E8F0';
          ctx.fill();
        }
      });

      ctx.globalAlpha = 1.0;
      animationFrameId = requestAnimationFrame(render);
    };

    render();

    return () => {
      cancelAnimationFrame(animationFrameId);
    };
  }, [
    structureData,
    style,
    colorScheme,
    showSidechains,
    isRotating,
    selectedResidueIndex,
    hoveredResidue,
    projectPoint,
  ]);

  // Handle canvas sizing on mount and resize
  useEffect(() => {
    const canvas = canvasRef.current;
    const container = containerRef.current;
    if (!canvas || !container) return;

    const resizeObserver = new ResizeObserver(() => {
      const rect = container.getBoundingClientRect();
      const dpr = window.devicePixelRatio || 1;
      canvas.width = rect.width * dpr;
      canvas.height = rect.height * dpr;
      const ctx = canvas.getContext('2d');
      if (ctx) ctx.scale(dpr, dpr);
    });

    resizeObserver.observe(container);
    return () => resizeObserver.disconnect();
  }, []);

  // Mouse interaction for orbit, pan, zoom
  const handleMouseDown = (e: React.MouseEvent<HTMLCanvasElement>) => {
    cameraRef.current.isDragging = true;
    cameraRef.current.dragButton = e.button;
    cameraRef.current.lastMouseX = e.clientX;
    cameraRef.current.lastMouseY = e.clientY;
  };

  const handleMouseMove = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    if (cameraRef.current.isDragging) {
      const deltaX = e.clientX - cameraRef.current.lastMouseX;
      const deltaY = e.clientY - cameraRef.current.lastMouseY;

      if (cameraRef.current.dragButton === 0 && !e.shiftKey) {
        // Left click drag: Orbit
        cameraRef.current.rotY += deltaX * 0.008;
        cameraRef.current.rotX += deltaY * 0.008;
      } else {
        // Right click or Shift+drag: Pan
        cameraRef.current.panX += deltaX * 0.15;
        cameraRef.current.panY += deltaY * 0.15;
      }

      cameraRef.current.lastMouseX = e.clientX;
      cameraRef.current.lastMouseY = e.clientY;
      return;
    }

    // Hit test hovered residue
    const rect = canvas.getBoundingClientRect();
    const mouseX = e.clientX - rect.left;
    const mouseY = e.clientY - rect.top;

    let closest: AtomCoord | null = null;
    let minDistance = 14;

    const width = canvas.width / (window.devicePixelRatio || 1);
    const height = canvas.height / (window.devicePixelRatio || 1);

    structureData.atoms.forEach((atom) => {
      const proj = projectPoint(atom.x, atom.y, atom.z, width, height);
      const dist = Math.hypot(proj.px - mouseX, proj.py - mouseY);
      if (dist < minDistance) {
        minDistance = dist;
        closest = atom;
      }
    });

    setHoveredResidue(closest);
  };

  const handleMouseUp = () => {
    cameraRef.current.isDragging = false;
  };

  const handleClick = () => {
    if (hoveredResidue && onSelectResidue) {
      if (selectedResidueIndex === hoveredResidue.residueIndex) {
        onSelectResidue(null);
      } else {
        onSelectResidue(hoveredResidue.residueIndex);
      }
    }
  };

  const handleWheel = (e: React.WheelEvent<HTMLCanvasElement>) => {
    e.preventDefault();
    const zoomFactor = e.deltaY < 0 ? 1.08 : 0.92;
    cameraRef.current.zoom = Math.max(0.35, Math.min(3.5, cameraRef.current.zoom * zoomFactor));
  };

  const handleResetCamera = () => {
    cameraRef.current = {
      rotX: 0.35,
      rotY: -0.45,
      zoom: 1.0,
      panX: 0,
      panY: 0,
      isDragging: false,
      dragButton: 0,
      lastMouseX: 0,
      lastMouseY: 0,
    };
    if (onSelectResidue) onSelectResidue(null);
  };

  const handleTakeScreenshot = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const link = document.createElement('a');
    link.download = `${targetId}_3D_structure.png`;
    link.href = canvas.toDataURL('image/png');
    link.click();
  };

  return (
    <div
      ref={containerRef}
      className={`relative w-full rounded-xl overflow-hidden border border-gray-800 bg-[#090D16] shadow-2xl flex flex-col ${className}`}
      style={{ height }}
    >
      {/* Top Header / Status Strip */}
      <div className="absolute top-0 left-0 right-0 z-10 px-4 py-3 flex items-center justify-between bg-gradient-to-b from-[#090D16]/90 via-[#090D16]/60 to-transparent pointer-events-none">
        <div className="flex items-center space-x-3 pointer-events-auto">
          <span className="font-mono text-sm font-semibold text-white tracking-wider flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-blue-500 animate-pulse"></span>
            {targetId}
          </span>
          <span className="text-xs text-gray-400 font-mono">
            {structureData.atoms.length} Residues
          </span>
          {isSimulatedDemo && (
            <span className="px-2 py-0.5 text-[10px] uppercase font-mono tracking-wider font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/30 rounded">
              Simulated 3D Model
            </span>
          )}
        </div>

        {/* Mol* Sidecar Link Button */}
        <div className="flex items-center space-x-2 pointer-events-auto">
          <a
            href="sidecar://structural-biology/biomolecular_structure_viewer/ui.html"
            target="_blank"
            rel="noopener noreferrer"
            title="Open sidecar viewer for full Mol* visualizer"
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-blue-600/20 hover:bg-blue-600/30 text-blue-400 border border-blue-500/30 transition-colors shadow-sm"
          >
            <ExternalLink className="w-3.5 h-3.5" />
            <span>Open Mol* Sidecar</span>
          </a>
        </div>
      </div>

      {/* Main 3D Canvas */}
      <canvas
        ref={canvasRef}
        className="w-full h-full cursor-grab active:cursor-grabbing block"
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
        onClick={handleClick}
        onWheel={handleWheel}
        onContextMenu={(e) => e.preventDefault()}
      />

      {/* Bottom Floating Toolbar */}
      <div className="absolute bottom-4 left-4 right-4 z-10 flex flex-wrap items-center justify-between gap-3 pointer-events-none">
        {/* Left: pLDDT Legend */}
        <div className="pointer-events-auto flex items-center space-x-2 bg-gray-900/85 backdrop-blur-md px-3 py-1.5 rounded-lg border border-gray-800 text-xs shadow-lg">
          <span className="text-gray-400 font-mono text-[11px] mr-1">pLDDT:</span>
          <div className="flex items-center space-x-1">
            <span className="w-2.5 h-2.5 rounded-sm bg-[#0053D6]" title="Very high (>= 90)"></span>
            <span className="text-[11px] text-gray-300 font-mono">{structureData.plddtSpectrum.veryHigh}%</span>
          </div>
          <div className="flex items-center space-x-1">
            <span className="w-2.5 h-2.5 rounded-sm bg-[#65CBF3]" title="Confident (70-90)"></span>
            <span className="text-[11px] text-gray-300 font-mono">{structureData.plddtSpectrum.high}%</span>
          </div>
          <div className="flex items-center space-x-1">
            <span className="w-2.5 h-2.5 rounded-sm bg-[#FFDB13]" title="Low (50-70)"></span>
            <span className="text-[11px] text-gray-300 font-mono">{structureData.plddtSpectrum.medium}%</span>
          </div>
          <div className="flex items-center space-x-1">
            <span className="w-2.5 h-2.5 rounded-sm bg-[#FF7D45]" title="Very low (< 50)"></span>
            <span className="text-[11px] text-gray-300 font-mono">{structureData.plddtSpectrum.low}%</span>
          </div>
        </div>

        {/* Center / Right: Interactive Controls */}
        <div className="pointer-events-auto flex items-center space-x-1.5 bg-gray-900/85 backdrop-blur-md p-1 rounded-lg border border-gray-800 shadow-lg">
          {/* Representation Style */}
          <div className="flex items-center border-r border-gray-800 pr-1 mr-1">
            {(['cartoon', 'stick', 'sphere', 'surface'] as const).map((s) => (
              <button
                key={s}
                onClick={() => setStyle(s)}
                className={`px-2.5 py-1 text-xs capitalize rounded font-medium transition-colors ${
                  style === s
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-400 hover:text-white hover:bg-gray-800'
                }`}
                title={`Switch representation to ${s}`}
              >
                {s}
              </button>
            ))}
          </div>

          {/* Color Scheme */}
          <div className="flex items-center border-r border-gray-800 pr-1 mr-1">
            {(['plddt', 'secondary', 'rainbow'] as const).map((c) => (
              <button
                key={c}
                onClick={() => setColorScheme(c)}
                className={`px-2 py-1 text-xs uppercase font-mono rounded transition-colors ${
                  colorScheme === c
                    ? 'bg-blue-600 text-white font-semibold'
                    : 'text-gray-400 hover:text-white hover:bg-gray-800'
                }`}
                title={`Color scheme: ${c}`}
              >
                {c === 'plddt' ? 'pLDDT' : c === 'secondary' ? '2nd' : 'Rainbow'}
              </button>
            ))}
          </div>

          {/* Sidechains Toggle */}
          <button
            onClick={() => setShowSidechains(!showSidechains)}
            className={`p-1.5 rounded transition-colors ${
              showSidechains ? 'bg-blue-600 text-white' : 'text-gray-400 hover:text-white hover:bg-gray-800'
            }`}
            title="Toggle sidechains"
          >
            <Layers className="w-4 h-4" />
          </button>

          {/* Rotation Toggle */}
          <button
            onClick={() => setIsRotating(!isRotating)}
            className={`p-1.5 rounded transition-colors ${
              isRotating ? 'text-blue-400 hover:bg-gray-800' : 'text-gray-500 hover:bg-gray-800'
            }`}
            title={isRotating ? 'Pause rotation' : 'Resume rotation'}
          >
            {isRotating ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
          </button>

          {/* Reset View */}
          <button
            onClick={handleResetCamera}
            className="p-1.5 text-gray-400 hover:text-white hover:bg-gray-800 rounded transition-colors"
            title="Reset camera view"
          >
            <RotateCcw className="w-4 h-4" />
          </button>

          {/* Screenshot */}
          <button
            onClick={handleTakeScreenshot}
            className="p-1.5 text-gray-400 hover:text-white hover:bg-gray-800 rounded transition-colors"
            title="Save 3D screenshot"
          >
            <Camera className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
};

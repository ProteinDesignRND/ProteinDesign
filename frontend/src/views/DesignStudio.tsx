import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Play,
  Lock,
  Unlock,
  ChevronDown,
  ChevronUp,
} from 'lucide-react';
import { CATH_TARGETS_A3 } from '../services/mockData';
import { TargetStructure, FROZEN_PARAMETERS_A3, ScientificParameters } from '../types';
import { createDesignJob } from '../services/api';
import { ThreeMolecularViewer } from '../components/viewer3d/ThreeMolecularViewer';
import { SequenceInspector } from '../components/viewer3d/SequenceInspector';

export const DesignStudio: React.FC = () => {
  const navigate = useNavigate();
  const [targets] = useState<TargetStructure[]>(CATH_TARGETS_A3);
  const [selectedTargetId, setSelectedTargetId] = useState<string>(CATH_TARGETS_A3[1].id); // 1UBQ
  const [designMode, setDesignMode] = useState<'all_masked' | 'hotspot' | 'core'>('all_masked');
  const [isLockedToA3, setIsLockedToA3] = useState<boolean>(true);
  const [customParams] = useState<ScientificParameters>({ ...FROZEN_PARAMETERS_A3 });
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [selectedResidue, setSelectedResidue] = useState<number | null>(null);
  const [showAdvancedSettings, setShowAdvancedSettings] = useState<boolean>(false);

  const selectedTarget = targets.find((t) => t.id === selectedTargetId) || targets[0];

  const handleLaunchJob = async () => {
    setIsSubmitting(true);
    try {
      await createDesignJob(selectedTarget.id, customParams);
      setTimeout(() => {
        navigate('/jobs');
      }, 500);
    } catch (err) {
      console.error(err);
      setIsSubmitting(false);
    }
  };

  return (
    <div className="space-y-6 pb-12 font-sans">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-[#282828]">
        <div>
          <h1 className="text-xl font-semibold text-[#F5F5F5] tracking-tight">
            Design Configuration
          </h1>
          <p className="text-xs text-[#A3A3A3] mt-0.5">
            Structure-conditioned inverse folding sequence design.
          </p>
        </div>

        <div className="text-xs text-[#A3A3A3] bg-[#141414] border border-[#282828] px-3 py-1.5 rounded">
          Target: <span className="text-[#F5F5F5] font-mono font-medium">{selectedTarget.name.split(' ')[0]}</span>
        </div>
      </div>

      {/* Main 2-Column Split */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left Guided Configuration Column */}
        <div className="lg:col-span-5 space-y-4 text-xs font-sans">
          {/* Step 1 – Target Backbone */}
          <div className="bg-[#141414] border border-[#282828] rounded-lg p-5 space-y-3">
            <span className="text-[#666666] uppercase tracking-wider text-[10px] block">
              01 · Target Backbone
            </span>

            <div className="space-y-1.5">
              <label className="text-[#F5F5F5] block font-medium">
                Select target structure
              </label>
              <select
                value={selectedTargetId}
                onChange={(e) => {
                  setSelectedTargetId(e.target.value);
                  setSelectedResidue(null);
                }}
                className="w-full bg-[#1C1C1C] text-[#F5F5F5] border border-[#282828] rounded px-3 py-2 text-xs focus:outline-none focus:border-[#38BDF8] transition-colors cursor-pointer font-sans"
              >
                {targets.map((target) => (
                  <option key={target.id} value={target.id}>
                    {target.name} ({target.length} AA · {target.cathId})
                  </option>
                ))}
              </select>
            </div>

            <div className="p-3 bg-[#1C1C1C] border border-[#282828] rounded text-[11px] text-[#A3A3A3] space-y-1">
              <div className="flex justify-between py-0.5">
                <span>CATH Topology:</span>
                <span className="font-mono text-[#F5F5F5] font-medium">{selectedTarget.cathId}</span>
              </div>
              <div className="flex justify-between py-0.5">
                <span>Residue Count:</span>
                <span className="font-mono text-[#F5F5F5] font-medium">{selectedTarget.length} residues</span>
              </div>
              <p className="pt-1 text-[#666666] leading-relaxed border-t border-[#282828]">
                {selectedTarget.description}
              </p>
            </div>

            {selectedTarget.isContaminatedTarget && (
              <div className="p-2.5 bg-[#B99B6A]/15 border border-[#B99B6A]/30 rounded text-[11px] text-amber-300 leading-relaxed">
                Quarantine Notice: 1n5uA03 was held as historical baseline audit (41.30% recovery).
              </div>
            )}
          </div>

          {/* Step 2 – Design Scope */}
          <div className="bg-[#141414] border border-[#282828] rounded-lg p-5 space-y-3">
            <span className="text-[#666666] uppercase tracking-wider text-[10px] block">
              02 · Design Scope
            </span>

            <div className="space-y-2">
              {[
                {
                  id: 'all_masked',
                  title: 'De Novo Sequence',
                  subtitle: 'All-Masked Inverse Folding',
                  desc: 'Redesigns the complete sequence to fold into the target geometry.',
                },
                {
                  id: 'hotspot',
                  title: 'Binding Loops',
                  subtitle: 'Interface & Hotspot Masking',
                  desc: 'Redesigns surface binding loops while scaffold core remains fixed.',
                },
                {
                  id: 'core',
                  title: 'Core Stabilization',
                  subtitle: 'Hydrophobic Repack',
                  desc: 'Repacks interior hydrophobic residues for enhanced stability.',
                },
              ].map((m) => {
                const isSelected = designMode === m.id;
                return (
                  <div
                    key={m.id}
                    onClick={() => setDesignMode(m.id as any)}
                    className={`p-3 rounded border cursor-pointer transition-colors ${
                      isSelected
                        ? 'border-[#38BDF8] bg-[#38BDF8]/10 text-[#F5F5F5]'
                        : 'border-[#282828] bg-[#1C1C1C] text-[#A3A3A3] hover:border-neutral-500'
                    }`}
                  >
                    <div className="flex items-baseline justify-between">
                      <span className="font-medium text-xs text-[#F5F5F5]">{m.title}</span>
                      <span className="text-[10px] text-[#38BDF8] font-mono">{m.subtitle}</span>
                    </div>
                    <p className="text-[11px] text-[#666666] mt-1 leading-relaxed">
                      {m.desc}
                    </p>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Step 3 – Parameters */}
          <div className="bg-[#141414] border border-[#282828] rounded-lg p-5 space-y-3">
            <div className="flex items-center justify-between pb-2 border-b border-[#282828]">
              <span className="text-[#666666] uppercase tracking-wider text-[10px]">
                03 · Parameters
              </span>
              <span className="text-[10px] text-[#38BDF8] font-mono">
                Amendment A3 Locked
              </span>
            </div>

            <div className="grid grid-cols-2 gap-2 text-[11px]">
              <div className="p-2.5 bg-[#1C1C1C] border border-[#282828] rounded">
                <span className="text-[#666666] text-[10px] block">Model Strategy</span>
                <span className="text-[#F5F5F5] font-medium">Dual Consensus</span>
              </div>
              <div className="p-2.5 bg-[#1C1C1C] border border-[#282828] rounded">
                <span className="text-[#666666] text-[10px] block">Quality Filter</span>
                <span className="text-[#38BDF8] font-medium font-mono">scRMSD &le; 2.0 Å</span>
              </div>
            </div>

            {/* Expandable Advanced Settings */}
            <div className="pt-1">
              <button
                onClick={() => setShowAdvancedSettings(!showAdvancedSettings)}
                className="flex items-center space-x-1.5 text-[#38BDF8] hover:text-[#B99B6A] transition-colors text-xs"
              >
                <span>{showAdvancedSettings ? 'Hide parameters' : 'Show parameters & formulas'}</span>
                {showAdvancedSettings ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
              </button>

              {showAdvancedSettings && (
                <div className="mt-3 p-3 bg-[#1C1C1C] border border-[#282828] rounded space-y-2 text-xs text-[#A3A3A3]">
                  <div className="flex justify-between py-0.5 border-b border-[#282828]">
                    <span>ProteinMPNN Temp</span>
                    <span className="font-mono text-[#F5F5F5] font-medium">T = 0.1</span>
                  </div>
                  <div className="flex justify-between py-0.5 border-b border-[#282828]">
                    <span>ProteinSolver Temp</span>
                    <span className="font-mono text-[#F5F5F5] font-medium">T = 1.0</span>
                  </div>
                  <div className="flex justify-between py-0.5 border-b border-[#282828]">
                    <span>Blending Weight (λ)</span>
                    <span className="font-mono text-[#F5F5F5] font-medium">λ = 0.5</span>
                  </div>
                  <div className="flex justify-between py-0.5 border-b border-[#282828]">
                    <span>Diversity Penalty (γ)</span>
                    <span className="font-mono text-[#F5F5F5] font-medium">γ = 0.0</span>
                  </div>
                  <p className="text-[10px] text-[#666666] pt-1 leading-relaxed">
                    z_blend = λ · z_mpnn + (1 - λ) · z_ps.
                  </p>
                </div>
              )}
            </div>
          </div>

          {/* Step 4 – Launch Button */}
          <div className="space-y-2">
            <button
              onClick={handleLaunchJob}
              disabled={isSubmitting}
              className="w-full py-2.5 px-4 bg-[#38BDF8] hover:bg-[#7DD3FC] text-[#080808] font-semibold font-medium text-xs rounded transition-colors flex items-center justify-center space-x-2 disabled:opacity-50"
            >
              <Play className="w-3.5 h-3.5 fill-current" />
              <span>{isSubmitting ? 'Submitting Design...' : 'Run Design Simulation'}</span>
            </button>
            <p className="text-[10px] text-[#666666] text-center">
              Dispatches job to async queue and tracks convergence telemetry.
            </p>
          </div>
        </div>

        {/* Right 3D Visualizer & Sequence Strip (7 cols) */}
        <div className="lg:col-span-7 space-y-4">
          <div className="relative bg-[#080808] border border-[#282828] rounded-lg overflow-hidden">
            <ThreeMolecularViewer
              targetId={selectedTarget.id}
              sequence={selectedTarget.nativeSequence}
              selectedResidueIndex={selectedResidue}
              onSelectResidue={setSelectedResidue}
              height={560}
              isSimulatedDemo={selectedTarget.isContaminatedTarget}
            />
          </div>

          <div className="bg-[#141414] border border-[#282828] rounded-lg p-4">
            <SequenceInspector
              sequence={selectedTarget.nativeSequence}
              selectedResidueIndex={selectedResidue}
              onSelectResidue={setSelectedResidue}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

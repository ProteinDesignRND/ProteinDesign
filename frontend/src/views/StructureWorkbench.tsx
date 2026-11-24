import React, { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Download, ExternalLink, ChevronDown, ChevronUp } from 'lucide-react';
import { ThreeMolecularViewer } from '../components/viewer3d/ThreeMolecularViewer';
import { SequenceInspector } from '../components/viewer3d/SequenceInspector';
import { Candidate, TargetStructure } from '../types';
import { getCandidates, getTargets, downloadTextFile } from '../services/api';
import { getPlddtColor } from '../components/viewer3d/structureModels';

export const StructureWorkbench: React.FC = () => {
  const [searchParams] = useSearchParams();
  const candidateIdFromUrl = searchParams.get('candidateId');

  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [targets, setTargets] = useState<TargetStructure[]>([]);
  const [selectedCandidateId, setSelectedCandidateId] = useState<string>('');
  const [selectedResidueIndex, setSelectedResidueIndex] = useState<number | null>(null);
  const [showAdvancedTelemetry, setShowAdvancedTelemetry] = useState(false);

  useEffect(() => {
    const load = async () => {
      const [candList, targetList] = await Promise.all([getCandidates(), getTargets()]);
      setCandidates(candList);
      setTargets(targetList);

      if (candidateIdFromUrl) {
        setSelectedCandidateId(candidateIdFromUrl);
      } else if (candList.length > 0) {
        setSelectedCandidateId(candList[0].id);
      }
    };
    load();
  }, [candidateIdFromUrl]);

  const activeCandidate = candidates.find((c) => c.id === selectedCandidateId) || candidates[0];
  const activeTarget = targets.find((t) => t.id === activeCandidate?.targetId) || targets[0];

  const handleDownloadPdb = () => {
    if (!activeCandidate) return;
    const pdbContent = `HEADER    PROTEIN DESIGN CANDIDATE ${activeCandidate.id}
TITLE     FUSE HYBRID CO-DESIGN (LAMBDA=0.5, GAMMA=0.0)
REMARK    TARGET ID: ${activeCandidate.targetId}
REMARK    RECOVERY RATE: ${(activeCandidate.recoveryRate * 100).toFixed(2)}%
REMARK    scRMSD: ${activeCandidate.scRMSD.toFixed(2)} ANGSTROMS
REMARK    SCALED pLDDT: ${activeCandidate.scaledPLDDT.toFixed(1)}
SEQRES   1 A   ${activeCandidate.length}  ${activeCandidate.sequence}
END\n`;
    downloadTextFile(`${activeCandidate.id}_model.pdb`, pdbContent, 'text/plain');
  };

  return (
    <div className="space-y-6 pb-12 font-sans">
      {/* Sub-Header: Candidate Selector & Actions */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-[#282828]">
        <div className="flex items-center space-x-3">
          <label className="text-xs text-[#A3A3A3] font-sans">
            Candidate:
          </label>
          <select
            value={selectedCandidateId}
            onChange={(e) => {
              setSelectedCandidateId(e.target.value);
              setSelectedResidueIndex(null);
            }}
            className="bg-[#141414] text-xs text-[#F5F5F5] border border-[#282828] rounded px-3 py-1.5 focus:outline-none focus:border-[#38BDF8] transition-colors cursor-pointer font-sans"
          >
            {candidates.map((c) => (
              <option key={c.id} value={c.id} className="bg-[#141414] text-[#F5F5F5]">
                {c.id} · {c.targetName} (pLDDT: {c.scaledPLDDT.toFixed(1)}, RMSD: {c.scRMSD.toFixed(2)} Å)
              </option>
            ))}
          </select>
        </div>

        <div className="flex items-center space-x-3 text-xs font-sans">
          <button
            onClick={handleDownloadPdb}
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded bg-[#141414] hover:bg-[#1C1C1C] text-[#F5F5F5] border border-[#282828] transition-colors"
            title="Download PDB coordinates"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Export PDB</span>
          </button>

          <a
            href="sidecar://structural-biology/biomolecular_structure_viewer/ui.html"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded bg-[#38BDF8]/10 hover:bg-[#38BDF8]/20 text-[#38BDF8] border border-[#38BDF8]/30 transition-colors"
            title="Open Biomolecular Structure Viewer sidecar"
          >
            <ExternalLink className="w-3.5 h-3.5" />
            <span>Mol* Sidecar</span>
          </a>
        </div>
      </div>

      {activeCandidate && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
          {/* Main 3D Molecular Viewport & Synchronized Sequence Track (8 Columns) */}
          <div className="lg:col-span-8 space-y-4">
            {/* 3D Viewport with subtle workstation border */}
            <div className="relative bg-[#080808] border border-[#282828] rounded-lg overflow-hidden">
              <ThreeMolecularViewer
                targetId={activeCandidate.id}
                sequence={activeCandidate.sequence}
                plddtScores={activeCandidate.plddtPerResidue}
                selectedResidueIndex={selectedResidueIndex}
                onSelectResidue={setSelectedResidueIndex}
                height={560}
                isSimulatedDemo={activeCandidate.isSimulatedDemo}
              />
            </div>

            {/* Synchronized Sequence Inspector Panel */}
            <div className="bg-[#141414] border border-[#282828] rounded-lg p-4">
              <SequenceInspector
                sequence={activeCandidate.sequence}
                nativeSequence={activeCandidate.nativeSequence}
                plddtScores={activeCandidate.plddtPerResidue}
                selectedResidueIndex={selectedResidueIndex}
                onSelectResidue={setSelectedResidueIndex}
              />
            </div>
          </div>

          {/* Right Information Rail (4 Columns, Elevated Dark Surface) */}
          <div className="lg:col-span-4 bg-[#141414] border border-[#282828] rounded-lg p-5 space-y-5 text-xs font-sans">
            {/* Target Header */}
            <div className="space-y-1 pb-3 border-b border-[#282828]">
              <span className="text-[#666666] uppercase tracking-wider text-[10px]">
                Target Backbone
              </span>
              <h2 className="text-base font-semibold text-[#F5F5F5] tracking-tight">
                {activeTarget?.name || activeCandidate.targetName}
              </h2>
              <p className="text-[#A3A3A3] text-xs leading-relaxed pt-1">
                {activeTarget?.description}
              </p>
            </div>

            {/* Essential Metrics: Crisp Elevated Metric Tiles */}
            <div className="space-y-2.5">
              <span className="text-[#666666] uppercase tracking-wider text-[10px] block">
                Validation Metrics
              </span>

              {/* RMSD */}
              <div className="p-3 bg-[#1C1C1C] border border-[#282828] rounded flex items-center justify-between">
                <div>
                  <span className="text-[#F5F5F5] font-medium block">scRMSD</span>
                  <span className="text-[#666666] text-[10px]">Threshold &le; 2.0 Å</span>
                </div>
                <span
                  className={`font-mono text-sm font-semibold ${
                    activeCandidate.scRMSD <= 2.0 ? 'text-[#38BDF8]' : 'text-[#C47F70]'
                  }`}
                >
                  {activeCandidate.scRMSD.toFixed(2)} Å
                </span>
              </div>

              {/* Confidence */}
              <div className="p-3 bg-[#1C1C1C] border border-[#282828] rounded flex items-center justify-between">
                <div>
                  <span className="text-[#F5F5F5] font-medium block">Confidence (pLDDT)</span>
                  <span className="text-[#666666] text-[10px]">Threshold &ge; 80.0</span>
                </div>
                <span
                  className="font-mono text-sm font-semibold"
                  style={{ color: getPlddtColor(activeCandidate.scaledPLDDT) }}
                >
                  {activeCandidate.scaledPLDDT.toFixed(1)} / 100
                </span>
              </div>

              {/* Recovery */}
              <div className="p-3 bg-[#1C1C1C] border border-[#282828] rounded flex items-center justify-between">
                <div>
                  <span className="text-[#F5F5F5] font-medium block">Sequence Recovery</span>
                  <span className="text-[#666666] text-[10px]">Wild-type match</span>
                </div>
                <span className="text-[#F5F5F5] font-mono text-sm font-semibold">
                  {(activeCandidate.recoveryRate * 100).toFixed(1)}%
                </span>
              </div>

              {/* Status */}
              <div className="p-3 bg-[#1C1C1C] border border-[#282828] rounded flex items-center justify-between">
                <div>
                  <span className="text-[#F5F5F5] font-medium block">Validation Status</span>
                  <span className="text-[#666666] text-[10px]">Amendment A3 Gate</span>
                </div>
                <span
                  className={`font-medium text-xs px-2 py-0.5 rounded ${
                    activeCandidate.gateStatus === 'passed'
                      ? 'bg-[#38BDF8]/15 text-[#38BDF8] border border-[#38BDF8]/30'
                      : 'bg-[#B99B6A]/15 text-[#B99B6A] border border-[#B99B6A]/30'
                  }`}
                >
                  {activeCandidate.gateStatus === 'passed' ? 'Self-Consistent' : 'Flagged'}
                </span>
              </div>
            </div>

            {/* Expandable Advanced Telemetry */}
            <div className="pt-2 border-t border-[#282828]">
              <button
                onClick={() => setShowAdvancedTelemetry(!showAdvancedTelemetry)}
                className="flex items-center space-x-1.5 text-[#38BDF8] hover:text-[#B99B6A] transition-colors text-xs"
              >
                <span>{showAdvancedTelemetry ? 'Hide parameters' : 'Show parameters & telemetry'}</span>
                {showAdvancedTelemetry ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
              </button>

              {showAdvancedTelemetry && (
                <div className="mt-3 p-3 bg-[#1C1C1C] border border-[#282828] rounded space-y-2 text-xs text-[#A3A3A3]">
                  <div className="flex justify-between py-0.5 border-b border-[#282828]">
                    <span>Mutations vs wild-type</span>
                    <span className="font-mono text-[#F5F5F5]">
                      {activeCandidate.mutationsCount} / {activeCandidate.length}
                    </span>
                  </div>

                  <div className="flex justify-between py-0.5 border-b border-[#282828]">
                    <span>Model perplexity</span>
                    <span className="font-mono text-[#F5F5F5]">{activeCandidate.perplexity.toFixed(2)}</span>
                  </div>

                  <div className="flex justify-between py-0.5 border-b border-[#282828]">
                    <span>Hybrid score</span>
                    <span className="font-mono text-[#F5F5F5]">{activeCandidate.hybridScore.toFixed(3)}</span>
                  </div>

                  <div className="flex justify-between py-0.5 border-b border-[#282828]">
                    <span>CATH</span>
                    <span className="font-mono text-[#F5F5F5]">{activeTarget?.cathId}</span>
                  </div>

                  <div className="flex justify-between py-0.5 border-b border-[#282828]">
                    <span>Resolution</span>
                    <span className="font-mono text-[#F5F5F5]">{activeTarget?.resolution}</span>
                  </div>

                  <div className="text-[10px] text-[#666666] pt-1 leading-relaxed">
                    Frozen constraints: ProteinMPNN T=0.1, ProteinSolver T=1.0, λ=0.5, γ=0.0.
                  </div>
                </div>
              )}
            </div>

            {/* Quarantine Notice if applicable */}
            {activeTarget?.isContaminatedTarget && (
              <div className="p-3 bg-[#B99B6A]/15 border border-[#B99B6A]/30 rounded text-xs text-[#A3A3A3] leading-relaxed">
                <span className="text-[#B99B6A] font-semibold block mb-1">Target Quarantine</span>
                Target 1n5uA03 (41.30% baseline recovery) is held as an audited historical reference.
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

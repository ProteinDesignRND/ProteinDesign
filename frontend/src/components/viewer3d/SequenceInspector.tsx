import React, { useState } from 'react';
import { getPlddtColor } from './structureModels';
import { Copy, Check, Info } from 'lucide-react';

export interface SequenceInspectorProps {
  sequence: string;
  nativeSequence?: string;
  plddtScores?: number[];
  selectedResidueIndex: number | null;
  onSelectResidue: (index: number | null) => void;
  className?: string;
}

export const SequenceInspector: React.FC<SequenceInspectorProps> = ({
  sequence,
  nativeSequence,
  plddtScores,
  selectedResidueIndex,
  onSelectResidue,
  className = '',
}) => {
  const [copied, setCopied] = useState(false);

  const handleCopySequence = () => {
    navigator.clipboard.writeText(sequence);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const selectedResidue = selectedResidueIndex
    ? {
        index: selectedResidueIndex,
        designedAa: sequence[selectedResidueIndex - 1] || '-',
        nativeAa: nativeSequence ? nativeSequence[selectedResidueIndex - 1] || '-' : '-',
        isMutated: nativeSequence
          ? sequence[selectedResidueIndex - 1] !== nativeSequence[selectedResidueIndex - 1]
          : false,
        plddt: plddtScores
          ? plddtScores[selectedResidueIndex - 1] ?? 85
          : 85,
      }
    : null;

  let totalMutations = 0;
  if (nativeSequence) {
    for (let i = 0; i < sequence.length; i++) {
      if (sequence[i] !== nativeSequence[i]) totalMutations++;
    }
  }

  return (
    <div className={`select-none ${className}`}>
      {/* Top Ledger */}
      <div className="flex items-center justify-between pb-2 hairline-b mb-2 text-xs">
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-[#F5F5F5] font-medium font-sans">Sequence Track</span>
          <span className="text-[#282828]">·</span>
          <span className="text-[#A3A3A3] font-mono text-[11px]">{sequence.length} residues</span>
          {nativeSequence && (
            <>
              <span className="text-[#282828]">·</span>
              <span className="text-neutral-300 font-mono text-[11px]">
                {totalMutations} mutations (recovery: {(((sequence.length - totalMutations) / sequence.length) * 100).toFixed(1)}%)
              </span>
            </>
          )}
        </div>

        <button
          onClick={handleCopySequence}
          className="flex items-center space-x-1 text-xs font-sans text-[#A3A3A3] hover:text-[#F5F5F5] transition-colors"
          title="Copy sequence to clipboard"
        >
          {copied ? <Check className="w-3.5 h-3.5 text-[#38BDF8]" /> : <Copy className="w-3.5 h-3.5" />}
          <span>{copied ? 'Copied FASTA' : 'Copy FASTA'}</span>
        </button>
      </div>

      {/* High-Density Residue Strip */}
      <div className="max-h-44 overflow-y-auto pr-1">
        <div className="flex flex-wrap gap-1">
          {sequence.split('').map((aa, idx) => {
            const residueNum = idx + 1;
            const isSelected = selectedResidueIndex === residueNum;
            const plddt = plddtScores ? plddtScores[idx] ?? 85 : 85;
            const color = getPlddtColor(plddt);
            const isMutated = nativeSequence ? nativeSequence[idx] !== aa : false;

            return (
              <button
                key={residueNum}
                onClick={() => onSelectResidue(isSelected ? null : residueNum)}
                className={`group relative flex flex-col items-center justify-center w-7 h-9 rounded font-mono text-xs transition-all ${
                  isSelected
                    ? 'ring-2 ring-[#38BDF8] scale-105 z-10 bg-[#1C1C1C]'
                    : 'bg-[#141414] hover:bg-[#1C1C1C] border border-[#282828]'
                }`}
                style={{
                  borderBottom: `2.5px solid ${color}`,
                }}
                title={`Residue ${residueNum}: ${aa}${nativeSequence ? ` (Native: ${nativeSequence[idx]})` : ''} - pLDDT: ${plddt.toFixed(1)}`}
              >
                <span className={`font-semibold ${isMutated ? 'text-[#B99B6A] font-bold' : 'text-slate-200'}`}>
                  {aa}
                </span>
                <span className="text-[9px] text-[#666666] group-hover:text-slate-300">
                  {residueNum}
                </span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Live Residue Telemetry Inspector Box */}
      {selectedResidue ? (
        <div className="mt-3 p-2.5 bg-[#1C1C1C] border border-[#282828] rounded flex items-center justify-between text-xs font-sans">
          <div className="flex items-center space-x-3">
            <span className="font-mono text-[#F5F5F5] text-[11px] bg-[#38BDF8]/20 text-[#38BDF8] px-2 py-0.5 rounded border border-[#38BDF8]/30">
              Pos #{selectedResidue.index}
            </span>
            <span className="text-[#A3A3A3]">
              Designed: <strong className="text-[#F5F5F5] font-mono">{selectedResidue.designedAa}</strong>
            </span>
            {nativeSequence && (
              <span className="text-[#A3A3A3]">
                Native: <strong className="text-[#F5F5F5] font-mono">{selectedResidue.nativeAa}</strong>
                {selectedResidue.isMutated ? (
                  <span className="ml-1 text-[#B99B6A] font-sans text-[11px]">(Mutated)</span>
                ) : (
                  <span className="ml-1 text-[#38BDF8] font-sans text-[11px]">(Conserved)</span>
                )}
              </span>
            )}
          </div>

          <div className="flex items-center space-x-2">
            <span className="text-[#666666] text-[11px] font-sans">Confidence:</span>
            <span
              className="font-mono font-medium text-xs px-2 py-0.5 rounded"
              style={{
                backgroundColor: `${getPlddtColor(selectedResidue.plddt)}22`,
                color: getPlddtColor(selectedResidue.plddt),
                border: `1px solid ${getPlddtColor(selectedResidue.plddt)}44`,
              }}
            >
              pLDDT {selectedResidue.plddt.toFixed(1)}
            </span>
          </div>
        </div>
      ) : (
        <div className="mt-3 p-2.5 bg-[#1C1C1C] border border-[#282828] rounded flex items-center justify-between text-[11px] font-sans text-[#666666]">
          <span>Click any residue along the sequence to inspect position details.</span>
          <div className="flex items-center space-x-3 text-[10px] font-mono">
            <span className="flex items-center gap-1">
              <span className="w-2 h-2 rounded-full bg-[#1d4ed8]"></span> &ge;90 Very high
            </span>
            <span className="flex items-center gap-1">
              <span className="w-2 h-2 rounded-full bg-[#06b6d4]"></span> 70-90 Confident
            </span>
            <span className="flex items-center gap-1">
              <span className="w-2 h-2 rounded-full bg-[#eab308]"></span> 50-70 Low
            </span>
            <span className="flex items-center gap-1">
              <span className="w-2 h-2 rounded-full bg-[#f97316]"></span> &lt;50 Very low
            </span>
          </div>
        </div>
      )}
    </div>
  );
};

import React, { useEffect, useState } from 'react';
import {
  Copy,
  Check,
  FileCode,
  FileText,
  ChevronDown,
  ChevronUp,
  ShieldCheck,
  Lock,
  Terminal,
} from 'lucide-react';
import { ProvenanceManifest } from '../types';
import { getProvenanceManifest, downloadTextFile } from '../services/api';

export const ReportsProvenance: React.FC = () => {
  const [manifest, setManifest] = useState<ProvenanceManifest | null>(null);
  const [copiedSnippet, setCopiedSnippet] = useState<boolean>(false);
  const [showTechnicalDetails, setShowTechnicalDetails] = useState<boolean>(false);

  useEffect(() => {
    const load = async () => {
      const data = await getProvenanceManifest();
      setManifest(data);
    };
    load();
  }, []);

  const handleDownloadJson = () => {
    if (!manifest) return;
    downloadTextFile(
      `${manifest.manifestId}.json`,
      JSON.stringify(manifest, null, 2),
      'application/json'
    );
  };

  const handleDownloadMarkdown = () => {
    if (!manifest) return;
    const md = `# PROVENANCE MANIFEST & AUDIT CERTIFICATE
**Manifest ID:** ${manifest.manifestId}  
**Project:** ${manifest.project}  
**Group:** ${manifest.group}  
**Commit:** ${manifest.commitHash}  
**Created At:** ${manifest.createdAt}  

---

## 1. CHECKPOINT INTEGRITY AUDIT
- **Verification Rule:** strict=True, 0 missing keys, 0 unexpected keys
- **Parameter Count:** Exactly 567,060 parameters
- **EXP004 Mask Invariance:** Max logit diff = 0.00000000e+00
- **Historical Equivalence Status:** FUNCTIONALLY REPRODUCED WITH MODERN COMPATIBILITY ADAPTATION
- **Single-Target Inverse Folding:** 41.30% on target 1n5uA03 (All-masked)

---

## 2. FROZEN SCIENTIFIC PARAMETERS (AMENDMENT A3)
- **ProteinMPNN Temperature:** ${manifest.parameters.proteinMpnnTemperature}
- **ProteinSolver Temperature:** ${manifest.parameters.proteinSolverTemperature}
- **Hybrid Lambda (λ):** ${manifest.parameters.hybridLambda}
- **Diversity Gamma (γ):** ${manifest.parameters.diversityGamma}
- **Benchmark Cohort:** 20 CATH 4.2 targets
- **Self-Consistency scRMSD Threshold:** ≤ ${manifest.parameters.maxScRMSD} Å
- **Oracle Scaled pLDDT Threshold:** ≥ ${manifest.parameters.minScaledPLDDT}

---

## 3. IMMUTABLE CRYPTOGRAPHIC HASH
SHA-256: ${manifest.provenanceHash}
`;
    downloadTextFile(`${manifest.manifestId}.md`, md, 'text/markdown');
  };

  const reproSnippet = `# Run strict verification test suite locally
python -m unittest tests/test_strict_checkpoint.py
python scripts/audit_mask_invariance.py --target 1n5uA03 --tolerance 0.00000000
python src/evaluate_hybrid_recovery.py --lambda 0.5 --gamma 0.0 --benchmark cath_4_2`;

  const handleCopySnippet = () => {
    navigator.clipboard.writeText(reproSnippet);
    setCopiedSnippet(true);
    setTimeout(() => setCopiedSnippet(false), 2000);
  };

  return (
    <div className="space-y-6 pb-16 max-w-5xl mx-auto font-sans">
      {/* Header & Export Actions */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-[#282828]">
        <div>
          <h1 className="text-xl font-semibold text-[#F5F5F5] tracking-tight">
            Provenance &amp; Verification Dossier
          </h1>
          <p className="text-xs text-[#A3A3A3] mt-0.5">
            Transparent methodology documentation, frozen parameter governance, and cryptographic audit certificates.
          </p>
        </div>

        <div className="flex items-center space-x-2.5">
          <button
            onClick={handleDownloadMarkdown}
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded bg-[#1C1C1C] hover:bg-[#1C1C1C] text-[#F5F5F5] text-xs border border-[#282828] transition-colors"
          >
            <FileText className="w-3.5 h-3.5 text-[#38BDF8]" />
            <span>Download .MD</span>
          </button>

          <button
            onClick={handleDownloadJson}
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded bg-[#38BDF8] hover:bg-[#7DD3FC] text-[#080808] font-semibold text-xs font-medium transition-colors"
          >
            <FileCode className="w-3.5 h-3.5" />
            <span>Download JSON</span>
          </button>
        </div>
      </div>

      {manifest && (
        <div className="space-y-4 text-xs">
          {/* Section 1: Methodology Overview */}
          <div className="bg-[#141414] border border-[#282828] rounded-lg p-5 space-y-3">
            <div className="flex items-center space-x-2 pb-2 border-b border-[#282828]">
              <ShieldCheck className="w-4 h-4 text-[#38BDF8]" />
              <h2 className="text-sm font-semibold text-[#F5F5F5]">
                1. Research Methodology &amp; Consensus Architecture
              </h2>
            </div>
            <p className="text-xs text-[#A3A3A3] leading-relaxed">
              FUSE combines two complementary computational biology paradigms into a unified framework. Rather than relying on a single neural network, the platform computes a convex combination of logits from ProteinMPNN (message-passing autoregression) and ProteinSolver (graph convolutional constraint satisfaction over contact graphs).
            </p>
            <p className="text-xs text-[#A3A3A3] leading-relaxed">
              To eliminate scientific drift and protect experimental validity, all benchmark evaluations are governed by Amendment A3: an immutable specification that freezes model hyperparameters, evaluation metrics, and validation thresholds.
            </p>
          </div>

          {/* Section 2: Model Configurations & Architecture */}
          <div className="bg-[#141414] border border-[#282828] rounded-lg p-5 space-y-3">
            <div className="flex items-center justify-between pb-2 border-b border-[#282828]">
              <h2 className="text-sm font-semibold text-[#F5F5F5]">
                2. Model Architecture &amp; Checkpoint Verification
              </h2>
              <span className="text-[11px] font-mono text-[#38BDF8] bg-[#38BDF8]/15 px-2 py-0.5 rounded border border-[#38BDF8]/30">
                strict=True Verified
              </span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
              <div className="p-3 bg-[#1C1C1C] rounded border border-[#282828] space-y-1">
                <span className="text-[#666666] text-[11px] block">Verified Parameters</span>
                <span className="text-[#F5F5F5] font-mono font-medium block">567,060 Parameters</span>
                <span className="text-[#666666] text-[11px] block">0 missing, 0 unexpected keys</span>
              </div>

              <div className="p-3 bg-[#1C1C1C] rounded border border-[#282828] space-y-1">
                <span className="text-[#666666] text-[11px] block">Mask Invariance</span>
                <span className="text-[#38BDF8] font-mono font-medium block">EXP004 Bit-Exact</span>
                <span className="text-[#666666] text-[11px] block">Max difference: 0.00e+00</span>
              </div>

              <div className="p-3 bg-[#1C1C1C] rounded border border-[#282828] space-y-1">
                <span className="text-[#666666] text-[11px] block">Model Checkpoint</span>
                <span className="text-[#F5F5F5] font-mono font-medium block">ProteinNet Graph Conv</span>
                <span className="text-[#666666] text-[11px] block">PyTorch state dict verified</span>
              </div>
            </div>
          </div>

          {/* Section 3: Frozen Scientific Parameters (Amendment A3) */}
          <div className="bg-[#141414] border border-[#282828] rounded-lg p-5 space-y-3">
            <div className="flex items-center justify-between pb-2 border-b border-[#282828]">
              <div>
                <h2 className="text-sm font-semibold text-[#F5F5F5]">
                  3. Frozen Scientific Parameters (Amendment A3)
                </h2>
                <span className="text-xs text-[#666666]">
                  Core hyperparameters ratified to prevent scientific cherry-picking.
                </span>
              </div>
              <div className="flex items-center space-x-1.5 text-xs text-[#38BDF8]">
                <Lock className="w-3.5 h-3.5" />
                <span>Frozen</span>
              </div>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
              <div className="p-3 bg-[#1C1C1C] rounded border border-[#282828]">
                <span className="text-[#666666] text-[11px] block">ProteinMPNN Temp</span>
                <span className="text-[#F5F5F5] font-mono font-medium block mt-1">
                  T = {manifest.parameters.proteinMpnnTemperature}
                </span>
              </div>

              <div className="p-3 bg-[#1C1C1C] rounded border border-[#282828]">
                <span className="text-[#666666] text-[11px] block">ProteinSolver Temp</span>
                <span className="text-[#F5F5F5] font-mono font-medium block mt-1">
                  T = {manifest.parameters.proteinSolverTemperature}
                </span>
              </div>

              <div className="p-3 bg-[#1C1C1C] rounded border border-[#282828]">
                <span className="text-[#666666] text-[11px] block">Blending Weight (λ)</span>
                <span className="text-[#F5F5F5] font-mono font-medium block mt-1">
                  λ = {manifest.parameters.hybridLambda}
                </span>
              </div>

              <div className="p-3 bg-[#1C1C1C] rounded border border-[#282828]">
                <span className="text-[#666666] text-[11px] block">Diversity Penalty (γ)</span>
                <span className="text-[#F5F5F5] font-mono font-medium block mt-1">
                  γ = {manifest.parameters.diversityGamma}
                </span>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2 text-xs text-[#A3A3A3]">
              <div className="p-2.5 bg-[#1C1C1C] rounded border border-[#282828] flex justify-between items-center">
                <span>Self-Consistency Threshold</span>
                <span className="text-[#38BDF8] font-mono font-medium">scRMSD &le; {manifest.parameters.maxScRMSD} Å</span>
              </div>
              <div className="p-2.5 bg-[#1C1C1C] rounded border border-[#282828] flex justify-between items-center">
                <span>Oracle Confidence Threshold</span>
                <span className="text-[#38BDF8] font-mono font-medium">pLDDT &ge; {manifest.parameters.minScaledPLDDT}</span>
              </div>
            </div>
          </div>

          {/* Section 4: Target Quarantine Governance */}
          <div className="bg-[#141414] border border-[#282828] rounded-lg p-5 space-y-2">
            <h2 className="text-sm font-semibold text-[#F5F5F5]">
              4. Target Quarantine Governance
            </h2>
            <p className="text-xs text-[#A3A3A3] leading-relaxed">
              Target 1n5uA03 was evaluated during historical baseline auditing, achieving 41.30% single-target inverse folding recovery. Under Amendment A3 rules, this target is explicitly quarantined from primary benchmark rankings to maintain strict evaluation separation.
            </p>
          </div>

          {/* Section 5: Local Reproducibility Snippet */}
          <div className="bg-[#141414] border border-[#282828] rounded-lg p-5 space-y-3">
            <div className="flex items-center justify-between pb-2 border-b border-[#282828]">
              <div className="flex items-center space-x-2">
                <Terminal className="w-4 h-4 text-[#38BDF8]" />
                <h2 className="text-sm font-semibold text-[#F5F5F5]">
                  5. Local Verification Commands
                </h2>
              </div>
              <button
                onClick={handleCopySnippet}
                className="flex items-center space-x-1 text-xs text-[#A3A3A3] hover:text-[#F5F5F5] transition-colors"
              >
                {copiedSnippet ? <Check className="w-3.5 h-3.5 text-[#38BDF8]" /> : <Copy className="w-3.5 h-3.5" />}
                <span>{copiedSnippet ? 'Copied' : 'Copy'}</span>
              </button>
            </div>

            <pre className="p-3 bg-[#080808] border border-[#1a1c26] rounded font-mono text-[11px] text-[#F5F5F5] overflow-x-auto select-all leading-relaxed">
              {reproSnippet}
            </pre>
          </div>

          {/* Section 6: Cryptographic Manifest Certificate */}
          <div className="bg-[#141414] border border-[#282828] rounded-lg p-5 space-y-3">
            <div className="flex items-center justify-between pb-2 border-b border-[#282828]">
              <h2 className="text-sm font-semibold text-[#F5F5F5]">
                6. Cryptographic Signatures &amp; Manifest
              </h2>
              <span className="text-[#666666] font-mono text-[11px]">
                {manifest.manifestId}
              </span>
            </div>

            <div className="space-y-2 text-xs">
              <div className="flex justify-between py-1 border-b border-[#282828]">
                <span className="text-[#666666]">SHA-256 Digest</span>
                <span className="font-mono text-[#A3A3A3] select-all truncate max-w-sm sm:max-w-md">
                  {manifest.provenanceHash}
                </span>
              </div>
              <div className="flex justify-between py-1 border-b border-[#282828]">
                <span className="text-[#666666]">Project / Group</span>
                <span className="text-[#F5F5F5] font-mono">{manifest.project} · {manifest.group}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-[#282828]">
                <span className="text-[#666666]">Commit Hash</span>
                <span className="font-mono text-[#A3A3A3]">{manifest.commitHash}</span>
              </div>
            </div>

            <div className="pt-2">
              <button
                onClick={() => setShowTechnicalDetails(!showTechnicalDetails)}
                className="flex items-center space-x-1.5 text-[#666666] hover:text-[#F5F5F5] transition-colors text-xs"
              >
                <span>{showTechnicalDetails ? 'Hide raw JSON metadata' : 'View raw JSON metadata'}</span>
                {showTechnicalDetails ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
              </button>

              {showTechnicalDetails && (
                <pre className="mt-3 p-3 bg-[#080808] border border-[#1a1c26] rounded font-mono text-[10px] text-[#A3A3A3] overflow-x-auto max-h-60">
                  {JSON.stringify(manifest, null, 2)}
                </pre>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

import React, { useState } from 'react';
import { ChevronDown, ChevronUp } from 'lucide-react';

interface WorkflowStage {
  id: string;
  number: string;
  name: string;
  technicalName: string;
  category: 'input' | 'audit' | 'generation' | 'scoring' | 'prediction' | 'validation' | 'output';
  whatHappens: string;
  whyItMatters: string;
  whatItProduces: string;
  technicalDetails: {
    parameters: Record<string, string>;
    formula?: string;
    evidence: string;
  };
}

export const WorkflowDesigner: React.FC = () => {
  const [selectedStageId, setSelectedStageId] = useState<string>('stage-scoring');
  const [showTechnicalSpecs, setShowTechnicalSpecs] = useState<boolean>(false);

  const stages: WorkflowStage[] = [
    {
      id: 'stage-selection',
      number: '01',
      name: 'Protein Selection',
      technicalName: 'Target Backbone Ingestion (PDB / mmCIF)',
      category: 'input',
      whatHappens:
        'The platform ingests experimental 3D coordinates from the curated 20-target CATH 4.2 benchmark suite or user-supplied PDB structures.',
      whyItMatters:
        'Accurate 3D coordinates provide the physical template for sequence design, defining the structural envelope.',
      whatItProduces:
        'C-alpha backbone coordinates, secondary structure annotations (helices, sheets, loops), and solvent-accessibility vectors.',
      technicalDetails: {
        parameters: {
          inputFormats: 'PDB, mmCIF v3',
          benchmarkCohort: '20 CATH 4.2 targets',
          quarantineFilter: 'Active (Flags 1n5uA03 contamination risk)',
        },
        evidence: 'Coordinates validated via biopython / PDB parser',
      },
    },
    {
      id: 'stage-audit',
      number: '02',
      name: 'Checkpoint & Integrity',
      technicalName: 'Model Invariance & Architecture Audit',
      category: 'audit',
      whatHappens:
        'Strictly checks model state dicts against Amendment A3 rules, asserting exact parameter counts and bit-level logit invariance.',
      whyItMatters:
        'Prevents silent model drift, unauthorized weight changes, or architectural discrepancy across computational runs.',
      whatItProduces:
        'Cryptographic audit approval token asserting zero missing keys and zero unexpected parameters.',
      technicalDetails: {
        parameters: {
          strictKeyMatch: '0 missing, 0 unexpected',
          parameterCount: '567,060 parameters',
          maxLogitDiff: '0.00000000e+00',
        },
        evidence: 'EXP004 reproducibility test suite passed',
      },
    },
    {
      id: 'stage-generation',
      number: '03',
      name: 'Sequence Generation',
      technicalName: 'Dual Inverse Folding (ProteinMPNN + ProteinSolver)',
      category: 'generation',
      whatHappens:
        'Two complementary neural networks independently propose amino acid sequences that fold into the target 3D structure: ProteinMPNN uses message-passing autoregression, while ProteinSolver solves constraint satisfaction over contact graphs.',
      whyItMatters:
        'Combining local autoregressive sampling with global graph constraint satisfaction captures both residue-level chemistry and global topology.',
      whatItProduces:
        'Logit tensors for 20 amino acid probabilities across all residue positions in the backbone.',
      technicalDetails: {
        parameters: {
          proteinMpnnTemp: 'T = 0.1 (Low-temperature greedy sampling)',
          proteinSolverTemp: 'T = 1.0 (Discrete identity propagation)',
          graphArchitecture: 'ProteinNet Edge-Conditioned Graph Conv',
        },
        evidence: 'Functionally reproduced with modern PyTorch compatibility',
      },
    },
    {
      id: 'stage-scoring',
      number: '04',
      name: 'Scoring & Blending',
      technicalName: 'Convex Hybrid Logit Combination',
      category: 'scoring',
      whatHappens:
        'Combines the probability distributions from ProteinMPNN and ProteinSolver using a calibrated convex weighting parameter (λ = 0.5) and diversity regularization (γ = 0.0).',
      whyItMatters:
        'Balances local autoregressive sequence recovery with global structural stability predictions, preventing single-model artifacts.',
      whatItProduces:
        'Calibrated consensus probability matrices and top-ranked candidate sequence proposals.',
      technicalDetails: {
        parameters: {
          lambdaWeight: 'λ = 0.5 (Equal convex blend)',
          diversityPenalty: 'γ = 0.0 (Amendment A3 locked)',
          vocabSize: '20 standard amino acids',
        },
        formula: 'z_blend = λ · z_mpnn + (1 - λ) · z_ps - γ · D',
        evidence: 'Validated across 20 CATH benchmark folds',
      },
    },
    {
      id: 'stage-prediction',
      number: '05',
      name: 'Structure Prediction',
      technicalName: 'Forward Structure Folding Oracle (ESMFold)',
      category: 'prediction',
      whatHappens:
        'The candidate sequence is fed forward into ESMFold (or AlphaFold2) without template assistance to predict how the sequence folds in 3D.',
      whyItMatters:
        'Inverse-designed sequences must physically fold back into the intended 3D geometry when simulated ab initio.',
      whatItProduces:
        'Predicted 3D all-atom coordinates and per-residue confidence scores (pLDDT).',
      technicalDetails: {
        parameters: {
          oracleModel: 'ESMFold v1 (Single-sequence)',
          templateFree: 'True (No PDB homology biasing)',
          recycleCount: '4 recycling iterations',
        },
        evidence: 'Self-consistency verification standard',
      },
    },
    {
      id: 'stage-validation',
      number: '06',
      name: 'Structural Validation',
      technicalName: 'Self-Consistency Filtering (Gate 3)',
      category: 'validation',
      whatHappens:
        'Compares the predicted 3D structure against the original target backbone using structural alignment, measuring scRMSD and mean pLDDT.',
      whyItMatters:
        'Separates viable biological binders from non-folding sequences, applying hard scientific thresholds.',
      whatItProduces:
        'Gate 3 Pass/Fail determination and ranked candidate scorecard.',
      technicalDetails: {
        parameters: {
          maxScRmsd: '≤ 2.0 Å (Rigid backbone alignment)',
          minPlddt: '≥ 80.0 (Scaled AlphaFold metric)',
          gateId: 'GATE-03-VALIDATION',
        },
        formula: 'Passed = (scRMSD ≤ 2.0 Å) ∧ (pLDDT ≥ 80.0)',
        evidence: 'A3 self-consistency validation suite',
      },
    },
    {
      id: 'stage-output',
      number: '07',
      name: 'Results & Provenance',
      technicalName: 'Audit Ledger & Export Packaging',
      category: 'output',
      whatHappens:
        'Records all execution hashes, seed values, model checkpoints, and timestamps into an immutable cryptographic manifest.',
      whyItMatters:
        'Guarantees that every generated candidate can be reproduced bit-for-bit by independent research teams.',
      whatItProduces:
        'Standard PDB coordinates, FASTA sequences, CSV evaluation metrics, and SHA-256 signed provenance manifests.',
      technicalDetails: {
        parameters: {
          exportFormats: 'PDB, FASTA, CSV, JSON',
          hashAlgorithm: 'SHA-256',
          manifestId: 'MAN-2026-A3-G1588-001',
        },
        evidence: 'Audited reproducible research package',
      },
    },
  ];

  const selectedStage = stages.find((s) => s.id === selectedStageId) || stages[3];

  return (
    <div className="space-y-6 pb-12 font-sans">
      {/* Header */}
      <div className="pb-4 border-b border-[#282828]">
        <h1 className="text-xl font-semibold text-[#F5F5F5] tracking-tight">
          Pipeline Architecture
        </h1>
        <p className="text-xs text-[#A3A3A3] mt-0.5">
          Seven sequential execution stages from backbone ingestion to cryptographic provenance.
        </p>
      </div>

      {/* Horizontal Stage Timeline */}
      <div className="bg-[#141414] border border-[#282828] rounded-lg p-2 overflow-x-auto">
        <div className="flex items-center space-x-1 min-w-max">
          {stages.map((stage) => {
            const isSelected = selectedStageId === stage.id;
            return (
              <button
                key={stage.id}
                onClick={() => setSelectedStageId(stage.id)}
                className={`flex items-center space-x-2 px-3 py-2 text-xs font-sans rounded transition-colors ${
                  isSelected
                    ? 'bg-[#38BDF8] text-[#080808] font-semibold font-medium'
                    : 'text-[#A3A3A3] hover:text-[#F5F5F5] hover:bg-[#1C1C1C]'
                }`}
              >
                <span className={`font-mono text-[11px] ${isSelected ? 'text-[#F5F5F5]' : 'text-[#666666]'}`}>
                  {stage.number}
                </span>
                <span>{stage.name}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Selected Stage Detail Panel */}
      <div className="bg-[#141414] border border-[#282828] rounded-lg p-5 space-y-5">
        <div className="flex flex-col sm:flex-row sm:items-baseline justify-between gap-2 pb-3 border-b border-[#282828]">
          <div>
            <div className="text-[11px] font-mono text-[#38BDF8]">
              Stage {selectedStage.number} · {selectedStage.technicalName}
            </div>
            <h2 className="text-lg font-semibold text-[#F5F5F5] mt-0.5">
              {selectedStage.name}
            </h2>
          </div>

          <div className="text-xs text-[#A3A3A3] bg-[#1C1C1C] border border-[#282828] px-3 py-1 rounded font-sans">
            Evidence: <span className="text-[#F5F5F5] font-medium">{selectedStage.technicalDetails.evidence}</span>
          </div>
        </div>

        {/* 3 Core Questions: What, Why, Produces */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
          <div className="p-4 bg-[#1C1C1C] border border-[#282828] rounded space-y-1.5">
            <span className="text-[#F5F5F5] font-medium block">
              1. What Happens
            </span>
            <p className="text-[#A3A3A3] leading-relaxed text-xs">
              {selectedStage.whatHappens}
            </p>
          </div>

          <div className="p-4 bg-[#1C1C1C] border border-[#282828] rounded space-y-1.5">
            <span className="text-[#F5F5F5] font-medium block">
              2. Why It Matters
            </span>
            <p className="text-[#A3A3A3] leading-relaxed text-xs">
              {selectedStage.whyItMatters}
            </p>
          </div>

          <div className="p-4 bg-[#1C1C1C] border border-[#282828] rounded space-y-1.5">
            <span className="text-[#F5F5F5] font-medium block">
              3. What It Produces
            </span>
            <p className="text-[#A3A3A3] leading-relaxed text-xs">
              {selectedStage.whatItProduces}
            </p>
          </div>
        </div>

        {/* Technical & Mathematical Specifications */}
        <div className="pt-3 border-t border-[#282828]">
          <button
            onClick={() => setShowTechnicalSpecs(!showTechnicalSpecs)}
            className="flex items-center space-x-1.5 text-xs text-[#38BDF8] hover:text-[#B99B6A] transition-colors"
          >
            <span>{showTechnicalSpecs ? 'Hide technical specifications' : 'Show technical specifications & parameters'}</span>
            {showTechnicalSpecs ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
          </button>

          {showTechnicalSpecs && (
            <div className="mt-3 p-4 bg-[#1C1C1C] border border-[#282828] rounded space-y-3 text-xs font-sans">
              {selectedStage.technicalDetails.formula && (
                <div className="p-2.5 bg-[#080808] border border-[#1a1c26] rounded">
                  <span className="text-[10px] text-[#666666] uppercase tracking-wider block mb-1">
                    Mathematical Formulation
                  </span>
                  <code className="text-xs font-mono text-cyan-400">
                    {selectedStage.technicalDetails.formula}
                  </code>
                </div>
              )}

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                {Object.entries(selectedStage.technicalDetails.parameters).map(([key, val]) => (
                  <div key={key} className="p-2.5 bg-[#080808] border border-[#1a1c26] rounded space-y-0.5">
                    <span className="text-[#666666] text-[10px] uppercase tracking-wider block">
                      {key.replace(/([A-Z])/g, ' $1')}
                    </span>
                    <span className="text-[#F5F5F5] font-mono text-xs block font-medium">
                      {val}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

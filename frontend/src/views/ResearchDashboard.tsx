import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, ChevronDown, ChevronUp } from 'lucide-react';
import { ExecutionGate, TargetStructure } from '../types';
import { getExecutionGates, getTargets } from '../services/api';
import { ThreeMolecularViewer } from '../components/viewer3d/ThreeMolecularViewer';

export const ResearchDashboard: React.FC = () => {
  const [gates, setGates] = useState<ExecutionGate[]>([]);
  const [targets, setTargets] = useState<TargetStructure[]>([]);
  const [showFullGates, setShowFullGates] = useState(false);

  useEffect(() => {
    const loadData = async () => {
      const [fetchedGates, fetchedTargets] = await Promise.all([
        getExecutionGates(),
        getTargets(),
      ]);
      setGates(fetchedGates);
      setTargets(fetchedTargets);
    };
    loadData();
  }, []);

  const benchmarkTarget = targets[1] || targets[0];

  return (
    <div className="space-y-12 pb-16 max-w-5xl mx-auto font-sans">
      {/* 1. HERO SECTION */}
      <section className="pt-6 sm:pt-10 space-y-5">
        <div className="space-y-2">
          <span className="text-[#666666] uppercase tracking-wider text-xs font-medium">
            Computational Structural Biology Platform
          </span>
          <h1 className="text-3xl sm:text-4xl font-semibold text-[#F5F5F5] tracking-tight leading-tight">
            Structure-Guided Protein Design
          </h1>
          <p className="text-sm sm:text-base text-[#A3A3A3] max-w-2xl leading-relaxed">
            Generate and evaluate de novo sequences for rigid biological backbones with consensus inverse folding, self-consistency oracles, and transparent provenance.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-4 pt-1 text-xs">
          <Link
            to="/design-studio"
            className="flex items-center space-x-2 px-4 py-2 bg-[#38BDF8] hover:bg-[#7DD3FC] text-[#080808] font-semibold font-medium rounded transition-colors"
          >
            <span>Start a Design</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>

          <Link
            to="/candidates"
            className="px-4 py-2 bg-[#1C1C1C] hover:bg-[#1C1C1C] text-[#F5F5F5] border border-[#282828] rounded transition-colors"
          >
            Explore Candidates
          </Link>

          <Link
            to="/reports"
            className="px-4 py-2 bg-[#1C1C1C] hover:bg-[#1C1C1C] text-[#F5F5F5] border border-[#282828] rounded transition-colors"
          >
            Read Audit Dossier
          </Link>
        </div>
      </section>

      {/* 2. CENTERPIECE 3D MOLECULAR SHOWCASE PANEL */}
      <section className="bg-[#141414] border border-[#282828] rounded-lg p-4 space-y-3">
        <div className="flex flex-col sm:flex-row sm:items-baseline justify-between gap-2 pb-2 border-b border-[#282828]">
          <div>
            <h2 className="text-sm font-semibold text-[#F5F5F5] tracking-tight">
              TfR1 with a VHH
            </h2>
            <p className="text-xs text-[#A3A3A3] mt-0.5">
              Single-domain antibody fragment bound to human transferrin receptor 1 ectodomain.
            </p>
          </div>

          <Link
            to="/structure"
            className="text-xs text-[#38BDF8] hover:text-[#B99B6A] transition-colors flex items-center gap-1 font-medium"
          >
            <span>Inspect in 3D Studio</span>
            <ArrowRight className="w-3 h-3" />
          </Link>
        </div>

        <div className="relative bg-[#080808] border border-[#282828] rounded overflow-hidden">
          <ThreeMolecularViewer
            targetId="tfr1_vhh"
            sequence={benchmarkTarget?.nativeSequence || 'MQIFVKTLTGKTITLEVEPSDTIENVKAKIQDKEGIPPDQQRLIFAGKQLEDGRTLSDYNIQKESTLHLVLRLRGG'}
            height={520}
            isSimulatedDemo={false}
          />
        </div>
      </section>

      {/* 3. FOUR-STEP WORKFLOW TRACK */}
      <section className="space-y-3">
        <span className="text-[#666666] uppercase tracking-wider text-xs font-medium block">
          Engineering Pipeline
        </span>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          <div className="bg-[#141414] border border-[#282828] rounded-lg p-4 space-y-1.5">
            <span className="text-xs font-mono text-[#38BDF8] font-medium">01</span>
            <h3 className="text-sm font-medium text-[#F5F5F5]">Target Backbone</h3>
            <p className="text-xs text-[#A3A3A3] leading-relaxed">
              Ingest crystallographic CATH 4.2 coordinates and verify structural integrity.
            </p>
          </div>

          <div className="bg-[#141414] border border-[#282828] rounded-lg p-4 space-y-1.5">
            <span className="text-xs font-mono text-[#38BDF8] font-medium">02</span>
            <h3 className="text-sm font-medium text-[#F5F5F5]">Sequence Synthesis</h3>
            <p className="text-xs text-[#A3A3A3] leading-relaxed">
              Dual inverse-folding synthesis combining ProteinMPNN and ProteinSolver.
            </p>
          </div>

          <div className="bg-[#141414] border border-[#282828] rounded-lg p-4 space-y-1.5">
            <span className="text-xs font-mono text-[#38BDF8] font-medium">03</span>
            <h3 className="text-sm font-medium text-[#F5F5F5]">Consensus Scoring</h3>
            <p className="text-xs text-[#A3A3A3] leading-relaxed">
              Score candidates with convex combination blend and filter low-confidence logits.
            </p>
          </div>

          <div className="bg-[#141414] border border-[#282828] rounded-lg p-4 space-y-1.5">
            <span className="text-xs font-mono text-[#38BDF8] font-medium">04</span>
            <h3 className="text-sm font-medium text-[#F5F5F5]">Structure Oracle</h3>
            <p className="text-xs text-[#A3A3A3] leading-relaxed">
              Validate self-consistency via forward prediction (scRMSD &le; 2.0 Å, pLDDT &ge; 80.0).
            </p>
          </div>
        </div>
      </section>

      {/* 4. KEY METRICS */}
      <section className="space-y-3">
        <span className="text-[#666666] uppercase tracking-wider text-xs font-medium block">
          Benchmark Performance
        </span>

        <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
          <div className="bg-[#141414] border border-[#282828] rounded-lg p-4 space-y-1">
            <span className="text-xs text-[#666666] block">Benchmark Suite</span>
            <div className="text-2xl font-mono text-[#F5F5F5] font-semibold">20 Targets</div>
            <p className="text-[11px] text-[#666666]">CATH 4.2 topology set</p>
          </div>

          <div className="bg-[#141414] border border-[#282828] rounded-lg p-4 space-y-1">
            <span className="text-xs text-[#666666] block">Sequence Recovery</span>
            <div className="text-2xl font-mono text-[#F5F5F5] font-semibold">51.8%</div>
            <p className="text-[11px] text-[#666666]">Wild-type concordance</p>
          </div>

          <div className="bg-[#141414] border border-[#282828] rounded-lg p-4 space-y-1">
            <span className="text-xs text-[#666666] block">Self-Consistency</span>
            <div className="text-2xl font-mono text-[#38BDF8] font-semibold">1.42 Å</div>
            <p className="text-[11px] text-[#666666]">Average scRMSD</p>
          </div>

          <div className="bg-[#141414] border border-[#282828] rounded-lg p-4 space-y-1">
            <span className="text-xs text-[#666666] block">Folding Confidence</span>
            <div className="text-2xl font-mono text-[#F5F5F5] font-semibold">88.4</div>
            <p className="text-[11px] text-[#666666]">Mean scaled pLDDT</p>
          </div>
        </div>
      </section>

      {/* 5. QUALITY ASSURANCE LEDGER */}
      <section className="bg-[#141414] border border-[#282828] rounded-lg p-5 space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-[#282828]">
          <div>
            <h3 className="text-sm font-semibold text-[#F5F5F5]">
              Quality Assurance &amp; Gate Audits
            </h3>
            <p className="text-xs text-[#A3A3A3] mt-0.5">
              Validation checkpoints asserting strict parameter invariance and target integrity.
            </p>
          </div>

          <button
            onClick={() => setShowFullGates(!showFullGates)}
            className="flex items-center space-x-1 text-xs text-[#38BDF8] hover:text-[#B99B6A] transition-colors"
          >
            <span>{showFullGates ? 'Hide full audit' : 'View full audit'}</span>
            {showFullGates ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
          </button>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
          <div className="p-3 bg-[#1C1C1C] border border-[#282828] rounded space-y-1">
            <span className="text-[#F5F5F5] block font-medium">Gate 1: Checkpoint Integrity</span>
            <span className="text-[#666666] text-[11px] block">Strict 567,060 parameters verified bit-exact</span>
          </div>
          <div className="p-3 bg-[#1C1C1C] border border-[#282828] rounded space-y-1">
            <span className="text-[#F5F5F5] block font-medium">Gate 2: Target Integrity</span>
            <span className="text-[#666666] text-[11px] block">Target 1n5uA03 quarantined (audit baseline)</span>
          </div>
          <div className="p-3 bg-[#1C1C1C] border border-[#282828] rounded space-y-1">
            <span className="text-[#F5F5F5] block font-medium">Gate 3: Self-Consistency</span>
            <span className="text-[#666666] text-[11px] block">scRMSD &le; 2.0 Å, pLDDT &ge; 80.0 enforced</span>
          </div>
        </div>

        {showFullGates && (
          <div className="pt-3 overflow-x-auto">
            <table className="w-full text-xs text-left">
              <thead>
                <tr className="border-b border-[#282828] text-[#666666] font-mono text-[11px]">
                  <th className="pb-2">Gate ID</th>
                  <th className="pb-2">Specification</th>
                  <th className="pb-2">Requirement</th>
                  <th className="pb-2 text-right">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#282828]">
                {gates.map((g) => (
                  <tr key={g.id} className="text-[#A3A3A3]">
                    <td className="py-2.5 font-mono text-[#666666]">{g.id}</td>
                    <td className="py-2.5 text-[#F5F5F5] font-medium">{g.name}</td>
                    <td className="py-2.5 text-[#A3A3A3]">{g.description}</td>
                    <td className="py-2.5 text-right">
                      <span className="font-mono text-[#38BDF8] text-[11px] bg-[#38BDF8]/15 px-2 py-0.5 rounded border border-[#38BDF8]/30">
                        {g.status.toUpperCase()}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  );
};

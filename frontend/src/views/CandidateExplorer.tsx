import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Search,
  FileSpreadsheet,
  FileCode,
  ExternalLink,
  ChevronDown,
  ChevronUp,
} from 'lucide-react';
import { Candidate } from '../types';
import { getCandidates, exportToCsv, exportToFasta, downloadTextFile } from '../services/api';
import { getPlddtColor } from '../components/viewer3d/structureModels';

export const CandidateExplorer: React.FC = () => {
  const navigate = useNavigate();
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [targetFilter, setTargetFilter] = useState<string>('all');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [minPlddt] = useState<number>(70);
  const [maxScRmsd] = useState<number>(2.5);
  const [expandedCandidateId, setExpandedCandidateId] = useState<string | null>(null);

  useEffect(() => {
    const load = async () => {
      const data = await getCandidates();
      setCandidates(data);
    };
    load();
  }, []);

  const filteredCandidates = candidates.filter((c) => {
    if (targetFilter !== 'all' && c.targetId !== targetFilter) return false;
    if (statusFilter !== 'all' && c.gateStatus !== statusFilter) return false;
    if (c.scaledPLDDT < minPlddt) return false;
    if (c.scRMSD > maxScRmsd) return false;
    if (
      searchQuery &&
      !c.id.toLowerCase().includes(searchQuery.toLowerCase()) &&
      !c.sequence.toLowerCase().includes(searchQuery.toLowerCase())
    ) {
      return false;
    }
    return true;
  });

  const handleExportCsv = () => {
    const csv = exportToCsv(filteredCandidates);
    downloadTextFile(`fuse_candidates_${Date.now()}.csv`, csv, 'text/csv');
  };

  const handleExportFasta = () => {
    const fasta = exportToFasta(filteredCandidates);
    downloadTextFile(`fuse_candidates_${Date.now()}.fasta`, fasta, 'text/plain');
  };

  const uniqueTargets = Array.from(new Set(candidates.map((c) => c.targetId)));

  return (
    <div className="space-y-6 pb-12 font-sans">
      {/* Header & Export Actions */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-[#282828]">
        <div>
          <h1 className="text-xl font-semibold text-[#F5F5F5] tracking-tight">
            Candidate Library
          </h1>
          <p className="text-xs text-[#A3A3A3] mt-0.5">
            Evaluated design sequences, mutation tracks, and structural validation scores.
          </p>
        </div>

        <div className="flex items-center space-x-2.5 text-xs font-sans">
          <button
            onClick={handleExportCsv}
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded bg-[#1C1C1C] hover:bg-[#1C1C1C] text-[#F5F5F5] border border-[#282828] transition-colors"
          >
            <FileSpreadsheet className="w-3.5 h-3.5 text-[#38BDF8]" />
            <span>Export CSV</span>
          </button>

          <button
            onClick={handleExportFasta}
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded bg-[#38BDF8] hover:bg-[#7DD3FC] text-[#080808] font-semibold font-medium transition-colors"
          >
            <FileCode className="w-3.5 h-3.5" />
            <span>Export FASTA</span>
          </button>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-[#141414] border border-[#282828] rounded-lg p-3.5">
        <div className="grid grid-cols-1 sm:grid-cols-4 gap-3 text-xs">
          <div className="relative">
            <Search className="w-3.5 h-3.5 absolute left-3 top-2.5 text-[#666666]" />
            <input
              type="text"
              placeholder="Search candidate ID..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-[#1C1C1C] border border-[#282828] rounded pl-8 pr-3 py-1.5 text-xs text-[#F5F5F5] placeholder-[#64748b] focus:outline-none focus:border-[#38BDF8] font-sans"
            />
          </div>

          <div>
            <select
              value={targetFilter}
              onChange={(e) => setTargetFilter(e.target.value)}
              className="w-full bg-[#1C1C1C] border border-[#282828] rounded px-3 py-1.5 text-xs text-[#A3A3A3] focus:outline-none focus:border-[#38BDF8] cursor-pointer font-sans"
            >
              <option value="all">All Targets ({uniqueTargets.length})</option>
              {uniqueTargets.map((t) => (
                <option key={t} value={t}>
                  Target: {t}
                </option>
              ))}
            </select>
          </div>

          <div>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="w-full bg-[#1C1C1C] border border-[#282828] rounded px-3 py-1.5 text-xs text-[#A3A3A3] focus:outline-none focus:border-[#38BDF8] cursor-pointer font-sans"
            >
              <option value="all">All Gate Statuses</option>
              <option value="passed">Passed Gate (scRMSD &le; 2.0 Å, pLDDT &ge; 80)</option>
              <option value="rejected">Rejected</option>
              <option value="held">Audit Hold</option>
            </select>
          </div>

          <div className="flex items-center justify-between text-xs text-[#666666] bg-[#1C1C1C] px-3 py-1.5 rounded border border-[#282828] font-mono">
            <span>Filter: &ge;{minPlddt} pLDDT</span>
            <span>{filteredCandidates.length} matches</span>
          </div>
        </div>
      </div>

      {/* Scannable Candidate Table Panel */}
      <div className="bg-[#141414] border border-[#282828] rounded-lg overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-[#161824] text-[#666666] text-[11px] border-b border-[#282828]">
              <tr>
                <th className="px-4 py-3 font-medium">Candidate</th>
                <th className="px-4 py-3 font-medium">Target</th>
                <th className="px-4 py-3 font-medium">Validation</th>
                <th className="px-4 py-3 font-medium">pLDDT</th>
                <th className="px-4 py-3 font-medium">scRMSD</th>
                <th className="px-4 py-3 font-medium">Recovery</th>
                <th className="px-4 py-3 font-medium text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#282828] text-[#A3A3A3]">
              {filteredCandidates.map((c) => {
                const isPassed = c.gateStatus === 'passed';
                const isExpanded = expandedCandidateId === c.id;

                return (
                  <React.Fragment key={c.id}>
                    <tr className={`hover:bg-[#161824] transition-colors ${isExpanded ? 'bg-[#161824]' : ''}`}>
                      <td className="px-4 py-3 font-mono text-[#F5F5F5]">
                        <div className="flex items-center space-x-2">
                          <span>{c.id}</span>
                          {c.isSimulatedDemo && (
                            <span className="text-[10px] px-1.5 py-0.2 rounded bg-[#B99B6A]/15 text-[#B99B6A] border border-[#B99B6A]/30 font-sans">
                              Demo
                            </span>
                          )}
                          {!c.isSimulatedDemo && c.targetId === '1n5uA03' && (
                            <span className="text-[10px] px-1.5 py-0.2 rounded bg-[#B99B6A]/15 text-[#B99B6A] border border-[#B99B6A]/30 font-sans">
                              Quarantine
                            </span>
                          )}
                        </div>
                      </td>
                      <td className="px-4 py-3 text-[#A3A3A3]">
                        <span>{c.targetName}</span>
                        <span className="text-[#666666] font-mono text-[10px] block">{c.targetId}</span>
                      </td>
                      <td className="px-4 py-3">
                        <span
                          className={`text-[11px] font-medium px-2 py-0.5 rounded ${
                            isPassed
                              ? 'bg-[#38BDF8]/15 text-[#38BDF8] border border-[#38BDF8]/30'
                              : 'bg-[#C47F70]/15 text-[#C47F70] border border-[#C47F70]/30'
                          }`}
                        >
                          {isPassed ? 'Self-Consistent' : 'Rejected'}
                        </span>
                      </td>
                      <td className="px-4 py-3 font-mono font-medium" style={{ color: getPlddtColor(c.scaledPLDDT) }}>
                        {c.scaledPLDDT.toFixed(1)}
                      </td>
                      <td className="px-4 py-3 font-mono">
                        <span className={c.scRMSD <= 2.0 ? 'text-[#38BDF8]' : 'text-[#C47F70]'}>
                          {c.scRMSD.toFixed(2)} Å
                        </span>
                      </td>
                      <td className="px-4 py-3 font-mono text-[#F5F5F5]">
                        {(c.recoveryRate * 100).toFixed(1)}%
                      </td>
                      <td className="px-4 py-3 text-right">
                        <div className="flex items-center justify-end space-x-3">
                          <button
                            onClick={() => setExpandedCandidateId(isExpanded ? null : c.id)}
                            className="text-[#A3A3A3] hover:text-[#F5F5F5] transition-colors text-[11px] flex items-center space-x-1"
                          >
                            <span>{isExpanded ? 'Hide' : 'Inspect'}</span>
                            {isExpanded ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
                          </button>

                          <button
                            onClick={() => navigate(`/structure?candidateId=${c.id}`)}
                            className="text-[#38BDF8] hover:text-[#B99B6A] transition-colors text-[11px] flex items-center space-x-1"
                            title="Open in 3D Studio"
                          >
                            <span>3D</span>
                            <ExternalLink className="w-3 h-3" />
                          </button>
                        </div>
                      </td>
                    </tr>

                    {/* Expandable Inspection Drawer */}
                    {isExpanded && (
                      <tr className="bg-[#0e1017]">
                        <td colSpan={7} className="p-4 border-b border-[#282828]">
                          <div className="space-y-3 text-xs">
                            <div className="flex flex-wrap items-center justify-between gap-2 text-[#A3A3A3]">
                              <div>
                                <span>Candidate Sequence · </span>
                                <strong className="text-[#F5F5F5] font-mono">{c.mutationsCount}</strong> mutations across {c.length} positions
                              </div>
                              <div className="flex items-center space-x-4 text-[#666666] font-mono text-[11px]">
                                <span>Perplexity: <strong className="text-[#F5F5F5]">{c.perplexity.toFixed(2)}</strong></span>
                                <span>Hybrid Score: <strong className="text-[#F5F5F5]">{c.hybridScore.toFixed(3)}</strong></span>
                              </div>
                            </div>

                            {/* Monospace Sequence with Mutations Highlighted */}
                            <div className="p-3 bg-[#08090d] border border-[#1a1c26] rounded font-mono text-[11px] leading-relaxed break-all select-all">
                              {c.sequence.split('').map((aa, idx) => {
                                const isMutated = c.nativeSequence ? c.nativeSequence[idx] !== aa : false;
                                return (
                                  <span
                                    key={idx}
                                    className={isMutated ? 'text-amber-300 font-bold' : 'text-[#666666]'}
                                    title={`Pos ${idx + 1}: ${aa} ${isMutated ? `(Wild-type: ${c.nativeSequence?.[idx]})` : ''}`}
                                  >
                                    {aa}
                                  </span>
                                );
                              })}
                            </div>

                            <div className="flex justify-end">
                              <button
                                onClick={() => navigate(`/structure?candidateId=${c.id}`)}
                                className="text-xs text-[#38BDF8] hover:text-[#B99B6A] transition-colors flex items-center gap-1 font-medium"
                              >
                                <span>Open in 3D Studio</span>
                                <ExternalLink className="w-3 h-3" />
                              </button>
                            </div>
                          </div>
                        </td>
                      </tr>
                    )}
                  </React.Fragment>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

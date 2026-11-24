import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Play, Pause, ArrowRight, Terminal } from 'lucide-react';
import { Job } from '../types';
import { getJobs, toggleJobHold } from '../services/api';

export const JobMonitor: React.FC = () => {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [selectedJobId, setSelectedJobId] = useState<string>('');
  const [logFilter, setLogFilter] = useState<string>('ALL');

  useEffect(() => {
    const fetchJobsList = async () => {
      const data = await getJobs();
      setJobs(data);
      if (data.length > 0 && !selectedJobId) {
        setSelectedJobId(data[0].id);
      }
    };
    fetchJobsList();
  }, []);

  const selectedJob = jobs.find((j) => j.id === selectedJobId) || jobs[0];

  const handleToggleHold = async (jobId: string) => {
    const updated = await toggleJobHold(jobId);
    if (updated) {
      setJobs((prev) => prev.map((j) => (j.id === jobId ? updated : j)));
    }
  };

  const filteredLogs = selectedJob?.logs.filter((log) => {
    if (logFilter === 'ALL') return true;
    return log.level === logFilter;
  });

  const completedCount = jobs.filter((j) => j.status === 'completed').length;
  const runningCount = jobs.filter((j) => j.status === 'running').length;
  const heldCount = jobs.filter((j) => j.status === 'held').length;

  return (
    <div className="space-y-6 pb-12 font-sans">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-[#282828]">
        <div>
          <h1 className="text-xl font-semibold text-[#F5F5F5] tracking-tight">
            Job Telemetry
          </h1>
          <p className="text-xs text-[#A3A3A3] mt-0.5">
            Active computations, device metrics, and log stream.
          </p>
        </div>

        {/* Status Count Summary */}
        <div className="flex items-center space-x-2 text-xs font-mono">
          <span className="px-2.5 py-1 bg-[#141414] border border-[#282828] rounded text-[#A3A3A3]">
            Total: <strong className="text-[#F5F5F5] font-sans">{jobs.length}</strong>
          </span>
          <span className="px-2.5 py-1 bg-blue-500/10 border border-[#38BDF8]/20 rounded text-[#38BDF8]">
            Running: <strong className="font-sans">{runningCount}</strong>
          </span>
          <span className="px-2.5 py-1 bg-[#38BDF8]/15 border border-[#38BDF8]/30 rounded text-[#38BDF8]">
            Completed: <strong className="font-sans">{completedCount}</strong>
          </span>
          {heldCount > 0 && (
            <span className="px-2.5 py-1 bg-[#B99B6A]/15 border border-[#B99B6A]/30 rounded text-[#B99B6A]">
              Held: <strong className="font-sans">{heldCount}</strong>
            </span>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left Column: Job Queue List (5 Columns) */}
        <div className="lg:col-span-5 bg-[#141414] border border-[#282828] rounded-lg p-4 space-y-3">
          <span className="text-[#666666] uppercase tracking-wider text-[10px] block pb-2 border-b border-[#282828]">
            Active Task Queue
          </span>

          <div className="space-y-2">
            {jobs.map((job) => {
              const isSelected = selectedJob?.id === job.id;
              const isHeld = job.status === 'held';
              const isComplete = job.status === 'completed';

              return (
                <div
                  key={job.id}
                  onClick={() => setSelectedJobId(job.id)}
                  className={`p-3 rounded border cursor-pointer transition-colors ${
                    isSelected
                      ? 'border-[#38BDF8] bg-[#1C1C1C] text-[#F5F5F5]'
                      : 'border-[#282828] bg-[#141414] text-[#A3A3A3] hover:border-neutral-500'
                  }`}
                >
                  <div className="flex items-baseline justify-between text-xs mb-1">
                    <span className="font-medium text-[#F5F5F5] truncate max-w-[210px]">
                      {job.name}
                    </span>
                    <span
                      className={`text-[10px] font-mono px-2 py-0.5 rounded ${
                        isHeld
                          ? 'bg-[#B99B6A]/15 text-[#B99B6A] border border-[#B99B6A]/30'
                          : isComplete
                          ? 'bg-[#38BDF8]/15 text-[#38BDF8] border border-[#38BDF8]/30'
                          : 'bg-blue-500/10 text-[#38BDF8] border border-[#38BDF8]/30'
                      }`}
                    >
                      {isComplete ? 'Complete' : isHeld ? 'Audit Hold' : 'Running'}
                    </span>
                  </div>

                  <div className="text-[11px] text-[#666666] mb-2">
                    Target: <strong className="text-[#F5F5F5] font-mono">{job.targetId}</strong> · {job.currentStage}
                  </div>

                  {/* Progress Line */}
                  <div className="w-full bg-[#080808] border border-[#1a1c26] rounded-full h-1.5 mb-2 overflow-hidden">
                    <div
                      className={`h-full transition-all duration-300 ${
                        isHeld ? 'bg-amber-400' : isComplete ? 'bg-[#38BDF8]' : 'bg-blue-500'
                      }`}
                      style={{ width: `${job.progress}%` }}
                    />
                  </div>

                  <div className="flex items-center justify-between text-[10px] text-[#666666] font-mono">
                    <span>{job.progress}% Complete</span>
                    <span>{new Date(job.createdAt).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Right Column: Selected Job Details & Telemetry (7 Columns) */}
        {selectedJob && (
          <div className="lg:col-span-7 bg-[#141414] border border-[#282828] rounded-lg p-5 space-y-5 text-xs font-sans">
            <div className="flex flex-col sm:flex-row sm:items-baseline justify-between gap-3 pb-3 border-b border-[#282828]">
              <div>
                <div className="text-[11px] text-[#666666] font-mono">
                  {selectedJob.id} · Target: {selectedJob.targetId}
                </div>
                <h2 className="text-base font-semibold text-[#F5F5F5] mt-0.5">{selectedJob.name}</h2>
              </div>

              <div className="flex items-center space-x-2">
                {selectedJob.status === 'completed' ? (
                  <Link
                    to="/candidates"
                    className="flex items-center space-x-1 px-3 py-1.5 bg-[#38BDF8] hover:bg-[#7DD3FC] text-[#080808] font-semibold rounded font-medium text-xs transition-colors"
                  >
                    <span>View Candidates</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </Link>
                ) : (
                  <button
                    onClick={() => handleToggleHold(selectedJob.id)}
                    className="flex items-center space-x-1 px-3 py-1.5 rounded bg-[#1C1C1C] hover:bg-[#1C1C1C] text-[#F5F5F5] border border-[#282828] text-xs transition-colors"
                  >
                    {selectedJob.status === 'held' ? (
                      <>
                        <Play className="w-3 h-3 fill-current text-[#38BDF8]" />
                        <span>Resume Job</span>
                      </>
                    ) : (
                      <>
                        <Pause className="w-3 h-3 fill-current text-[#B99B6A]" />
                        <span>Pause Execution</span>
                      </>
                    )}
                  </button>
                )}
              </div>
            </div>

            {selectedJob.status === 'held' && (
              <div className="p-3 bg-[#B99B6A]/15 border border-[#B99B6A]/30 rounded text-xs text-amber-300 leading-relaxed">
                <strong>Execution Hold Active:</strong> Computation paused for validation under Amendment A3 governance. Click &quot;Resume Job&quot; to continue.
              </div>
            )}

            {/* Hardware & Execution Telemetry */}
            {selectedJob.gpuTelemetry && (
              <div className="p-3.5 bg-[#1C1C1C] border border-[#282828] rounded space-y-2.5">
                <span className="text-[#F5F5F5] font-medium block">
                  Execution Environment &amp; Hardware Telemetry
                </span>

                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
                  <div>
                    <span className="text-[#666666] text-[10px] block">Compute Unit</span>
                    <span className="text-[#F5F5F5] font-mono truncate block mt-0.5 font-medium">{selectedJob.gpuTelemetry.device}</span>
                  </div>
                  <div>
                    <span className="text-[#666666] text-[10px] block">GPU Utilization</span>
                    <span className="text-[#38BDF8] font-mono block mt-0.5 font-medium">{selectedJob.gpuTelemetry.utilizationPercent}%</span>
                  </div>
                  <div>
                    <span className="text-[#666666] text-[10px] block">VRAM Allocated</span>
                    <span className="text-[#F5F5F5] font-mono block mt-0.5 font-medium">{selectedJob.gpuTelemetry.vramUsedMb} / {selectedJob.gpuTelemetry.vramTotalMb} MB</span>
                  </div>
                  <div>
                    <span className="text-[#666666] text-[10px] block">Temperature</span>
                    <span className="text-[#F5F5F5] font-mono block mt-0.5 font-medium">{selectedJob.gpuTelemetry.temperatureC}°C</span>
                  </div>
                </div>
              </div>
            )}

            {/* Live Terminal Log Stream */}
            <div className="space-y-2 pt-1">
              <div className="flex items-center justify-between text-xs">
                <div className="flex items-center space-x-1.5 text-[#F5F5F5] font-medium">
                  <Terminal className="w-3.5 h-3.5 text-[#38BDF8]" />
                  <span>Execution Log Stream</span>
                </div>

                <div className="flex items-center space-x-1 text-[11px] font-mono">
                  {['ALL', 'INFO', 'WARN', 'ERROR'].map((lvl) => (
                    <button
                      key={lvl}
                      onClick={() => setLogFilter(lvl)}
                      className={`px-2 py-0.5 rounded transition-colors ${
                        logFilter === lvl
                          ? 'bg-[#38BDF8] text-[#080808] font-semibold font-medium'
                          : 'bg-[#1C1C1C] text-[#666666] hover:text-[#F5F5F5] border border-[#282828]'
                      }`}
                    >
                      {lvl}
                    </button>
                  ))}
                </div>
              </div>

              <div className="bg-[#080808] border border-[#1a1c26] rounded p-3 font-mono text-xs text-[#A3A3A3] max-h-60 overflow-y-auto space-y-1">
                {filteredLogs.map((log, idx) => (
                  <div key={idx} className="flex items-start space-x-2 leading-relaxed">
                    <span className="text-[#666666] select-none shrink-0 text-[10px]">
                      {new Date(log.timestamp).toLocaleTimeString()}
                    </span>
                    <span
                      className={`text-[10px] shrink-0 font-medium ${
                        log.level === 'ERROR'
                          ? 'text-[#C47F70]'
                          : log.level === 'WARN'
                          ? 'text-[#B99B6A]'
                          : 'text-[#38BDF8]'
                      }`}
                    >
                      [{log.level}]
                    </span>
                    <span className="text-[#A3A3A3] break-all">{log.message}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

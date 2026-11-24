import {
  Candidate,
  ExecutionGate,
  FROZEN_PARAMETERS_A3,
  Job,
  ProvenanceManifest,
  ScientificParameters,
  TargetStructure,
} from '../types';
import {
  CATH_TARGETS_A3,
  INITIAL_CANDIDATES,
  INITIAL_EXECUTION_GATES,
  INITIAL_JOBS,
  PROVENANCE_MANIFEST_A3,
} from './mockData';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

export interface BackendStatus {
  isLive: boolean;
  endpointUrl: string;
  checkedAt: string;
  version?: string;
  error?: string;
}

// In-memory state for prototype interaction if live backend is not connected
let memoryJobs: Job[] = [...INITIAL_JOBS];
let memoryCandidates: Candidate[] = [...INITIAL_CANDIDATES];
let memoryGates: ExecutionGate[] = [...INITIAL_EXECUTION_GATES];

export const checkBackendStatus = async (): Promise<BackendStatus> => {
  const timestamp = new Date().toISOString();
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 2000);
    const response = await fetch(`${API_BASE_URL}/health`, {
      signal: controller.signal,
    });
    clearTimeout(timeoutId);

    if (response.ok) {
      const data = await response.json();
      return {
        isLive: true,
        endpointUrl: API_BASE_URL,
        checkedAt: timestamp,
        version: data.version || '1.0.0-live',
      };
    }
    return {
      isLive: false,
      endpointUrl: API_BASE_URL,
      checkedAt: timestamp,
      error: `Server responded with status ${response.status}`,
    };
  } catch (err: any) {
    return {
      isLive: false,
      endpointUrl: API_BASE_URL,
      checkedAt: timestamp,
      error: err?.message || 'Connection refused — running in isolated prototype mode',
    };
  }
};

export const getTargets = async (): Promise<TargetStructure[]> => {
  try {
    const res = await fetch(`${API_BASE_URL}/targets`);
    if (res.ok) return await res.json();
  } catch (_) {
    // Fallback to verified CATH targets
  }
  return CATH_TARGETS_A3;
};

export const getJobs = async (): Promise<Job[]> => {
  try {
    const res = await fetch(`${API_BASE_URL}/jobs`);
    if (res.ok) return await res.json();
  } catch (_) {
    // Fallback to local memory jobs
  }
  return [...memoryJobs];
};

export const createDesignJob = async (
  targetId: string,
  parameters: ScientificParameters = FROZEN_PARAMETERS_A3
): Promise<Job> => {
  try {
    const res = await fetch(`${API_BASE_URL}/jobs`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ targetId, parameters }),
    });
    if (res.ok) return await res.json();
  } catch (_) {
    // Isolated prototype simulation flow (clearly marked)
  }

  const target = CATH_TARGETS_A3.find((t) => t.id === targetId) || CATH_TARGETS_A3[1];
  const newJob: Job = {
    id: `job-proto-${Date.now().toString(36)}`,
    name: `Co-Design: ${target.name} [PROTOTYPE]`,
    targetId: target.id,
    status: 'running',
    progress: 15,
    currentStage: 'Feature extraction & checkpoint verification',
    createdAt: new Date().toISOString(),
    parameters,
    candidateCount: 0,
    logs: [
      { timestamp: new Date().toLocaleTimeString(), level: 'INFO', message: 'Prototype job started (simulated sandbox execution)' },
      { timestamp: new Date().toLocaleTimeString(), level: 'INFO', message: `Frozen Amendment A3 parameters applied: MPNN T=${parameters.proteinMpnnTemperature}, Solver T=${parameters.proteinSolverTemperature}, λ=${parameters.hybridLambda}` },
      { timestamp: new Date().toLocaleTimeString(), level: 'GATE', message: 'Gate 0 Checkpoint verification: 567,060 parameters verified' },
    ],
    gpuTelemetry: {
      device: 'Simulation / Prototype Telemetry',
      vramUsedMb: 5240,
      vramTotalMb: 24576,
      utilizationPercent: 68,
      temperatureC: 49,
      isSimulated: true,
    },
  };

  memoryJobs = [newJob, ...memoryJobs];
  return newJob;
};

export const toggleJobHold = async (jobId: string): Promise<Job | null> => {
  try {
    const res = await fetch(`${API_BASE_URL}/jobs/${jobId}/hold`, { method: 'POST' });
    if (res.ok) return await res.json();
  } catch (_) {}

  const jobIndex = memoryJobs.findIndex((j) => j.id === jobId);
  if (jobIndex === -1) return null;

  const job = memoryJobs[jobIndex];
  const newStatus = job.status === 'held' ? 'running' : 'held';
  const updatedJob: Job = {
    ...job,
    status: newStatus,
    currentStage: newStatus === 'held' ? 'Execution Hold: Awaiting Human PI Review' : 'Resuming design stream',
    logs: [
      ...job.logs,
      {
        timestamp: new Date().toLocaleTimeString(),
        level: 'GATE',
        message: newStatus === 'held' ? 'Execution hold asserted manually' : 'Execution hold released by operator',
      },
    ],
  };
  memoryJobs[jobIndex] = updatedJob;
  return updatedJob;
};

export const getCandidates = async (targetIdFilter?: string): Promise<Candidate[]> => {
  try {
    const res = await fetch(`${API_BASE_URL}/candidates${targetIdFilter ? `?targetId=${targetIdFilter}` : ''}`);
    if (res.ok) return await res.json();
  } catch (_) {}

  if (targetIdFilter && targetIdFilter !== 'all') {
    return memoryCandidates.filter((c) => c.targetId === targetIdFilter);
  }
  return [...memoryCandidates];
};

export const getCandidateById = async (id: string): Promise<Candidate | null> => {
  try {
    const res = await fetch(`${API_BASE_URL}/candidates/${id}`);
    if (res.ok) return await res.json();
  } catch (_) {}

  return memoryCandidates.find((c) => c.id === id) || null;
};

export const getExecutionGates = async (): Promise<ExecutionGate[]> => {
  try {
    const res = await fetch(`${API_BASE_URL}/gates`);
    if (res.ok) return await res.json();
  } catch (_) {}
  return [...memoryGates];
};

export const getProvenanceManifest = async (): Promise<ProvenanceManifest> => {
  try {
    const res = await fetch(`${API_BASE_URL}/provenance`);
    if (res.ok) return await res.json();
  } catch (_) {}
  return PROVENANCE_MANIFEST_A3;
};

// Export Helpers
export const exportToFasta = (candidates: Candidate[]): string => {
  return candidates
    .map(
      (c) =>
        `>${c.id} | Target=${c.targetId} | Recovery=${(c.recoveryRate * 100).toFixed(2)}% | scRMSD=${c.scRMSD.toFixed(2)}A | pLDDT=${c.scaledPLDDT.toFixed(1)} | Score=${c.hybridScore.toFixed(3)}${c.isSimulatedDemo ? ' [SIMULATED_DEMO]' : ''}\n${c.sequence}`
    )
    .join('\n\n');
};

export const exportToCsv = (candidates: Candidate[]): string => {
  const headers = [
    'Candidate_ID',
    'Target_ID',
    'Target_Name',
    'Recovery_Rate',
    'scRMSD_Angstrom',
    'Scaled_pLDDT',
    'Perplexity',
    'Hybrid_Score',
    'Mutations_Count',
    'Length',
    'Gate_Status',
    'Is_Simulated_Demo',
    'Created_At',
    'Sequence',
  ];

  const rows = candidates.map((c) => [
    c.id,
    c.targetId,
    `"${c.targetName}"`,
    c.recoveryRate.toFixed(4),
    c.scRMSD.toFixed(2),
    c.scaledPLDDT.toFixed(1),
    c.perplexity.toFixed(2),
    c.hybridScore.toFixed(3),
    c.mutationsCount,
    c.length,
    c.gateStatus,
    c.isSimulatedDemo,
    c.createdAt,
    `"${c.sequence}"`,
  ]);

  return [headers.join(','), ...rows.map((r) => r.join(','))].join('\n');
};

export const downloadTextFile = (filename: string, content: string, contentType: string = 'text/plain') => {
  const blob = new Blob([content], { type: contentType });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
};

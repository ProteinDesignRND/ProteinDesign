export type JobStatus = 'queued' | 'running' | 'completed' | 'failed' | 'held';

export interface ScientificParameters {
  amendment: string;
  proteinMpnnTemperature: number;
  proteinSolverTemperature: number;
  hybridLambda: number;
  diversityGamma: number;
  cathTargetsCount: number;
  maxScRMSD: number;
  minScaledPLDDT: number;
  checkpointParamsCount: number;
  maskInvarianceVerified: boolean;
}

export const FROZEN_PARAMETERS_A3: ScientificParameters = {
  amendment: 'Amendment A3',
  proteinMpnnTemperature: 0.1,
  proteinSolverTemperature: 1.0,
  hybridLambda: 0.5,
  diversityGamma: 0.0,
  cathTargetsCount: 20,
  maxScRMSD: 2.0, // Angstroms
  minScaledPLDDT: 80.0,
  checkpointParamsCount: 567060,
  maskInvarianceVerified: true,
};

export interface JobLogEntry {
  timestamp: string;
  level: 'INFO' | 'WARN' | 'ERROR' | 'METRIC' | 'GATE';
  message: string;
}

export interface Job {
  id: string;
  name: string;
  targetId: string;
  status: JobStatus;
  progress: number;
  currentStage: string;
  createdAt: string;
  completedAt?: string;
  parameters: ScientificParameters;
  logs: JobLogEntry[];
  candidateCount: number;
  gpuTelemetry?: {
    device: string;
    vramUsedMb: number;
    vramTotalMb: number;
    utilizationPercent: number;
    temperatureC: number;
    isSimulated: boolean;
  };
}

export interface Candidate {
  id: string;
  jobId: string;
  targetId: string;
  targetName: string;
  sequence: string;
  nativeSequence: string;
  recoveryRate: number; // e.g. 0.4130 for 41.3%
  scRMSD: number; // e.g. 1.42 Angstroms
  scaledPLDDT: number; // e.g. 84.6
  perplexity: number;
  hybridScore: number;
  mutationsCount: number;
  length: number;
  plddtPerResidue: number[];
  gateStatus: 'passed' | 'held' | 'rejected';
  isSimulatedDemo: boolean;
  createdAt: string;
}

export interface ExecutionGate {
  id: string;
  name: string;
  stage: string;
  description: string;
  status: 'passed' | 'held' | 'running' | 'pending';
  threshold: string;
  measured: string;
  evidence: string;
  timestamp: string;
}

export interface ProvenanceManifest {
  manifestId: string;
  project: string;
  group: string;
  createdAt: string;
  commitHash: string;
  checkpoints: {
    model: string;
    sha256: string;
    parameterCount: number;
    strictLoadVerified: boolean;
  }[];
  parameters: ScientificParameters;
  verificationAudit: {
    checkpointIntegrity: string;
    maskInvarianceMaxLogitDiff: number;
    featurePipelineDiff: number;
    singleTargetIntegrationRecovery: string;
    statusClassification: string;
  };
  provenanceHash: string;
}

export interface TargetStructure {
  id: string;
  name: string;
  cathId: string;
  length: number;
  resolution: string;
  nativeSequence: string;
  description: string;
  isContaminatedTarget?: boolean;
}

export interface WorkflowNode {
  id: string;
  label: string;
  type: 'input' | 'process' | 'model' | 'gate' | 'output';
  description: string;
  status: 'idle' | 'active' | 'completed' | 'held';
  config: Record<string, any>;
}

import React from 'react';
import { useLocation } from 'react-router-dom';
import { BackendStatus } from '../../services/api';
import { Lock, Cpu, ShieldCheck } from 'lucide-react';

export interface ContextualHeaderProps {
  backendStatus: BackendStatus | null;
}

export const ContextualHeader: React.FC<ContextualHeaderProps> = ({ backendStatus }) => {
  const location = useLocation();

  const getBreadcrumb = () => {
    switch (location.pathname) {
      case '/structure':
        return 'Structure & Validation Workbench';
      case '/design-studio':
        return 'Co-Design Studio // Inverse Folding';
      case '/workflow':
        return 'Workflow Pipeline // DAG Engine';
      case '/jobs':
        return 'Job Monitor // Execution Queue';
      case '/candidates':
        return 'Candidate Explorer // Evaluation Filter';
      case '/reports':
        return 'Reports & Provenance // Cryptographic Signatures';
      default:
        return 'Research Console // Milestone E0 Hardening';
    }
  };

  return (
    <header className="h-11 bg-fuse-panel border-b border-fuse-border px-4 flex items-center justify-between shrink-0 select-none text-xs">
      {/* Left: Scientific Breadcrumb */}
      <div className="flex items-center space-x-2.5 font-mono text-2xs">
        <span className="font-semibold text-gray-400">FUSE</span>
        <span className="text-fuse-border">/</span>
        <span className="text-gray-200">{getBreadcrumb()}</span>
      </div>

      {/* Right: Telemetry & Frozen Parameter Pills */}
      <div className="flex items-center space-x-3">
        {/* Amendment A3 Lock Status */}
        <div className="hidden sm:flex items-center space-x-1.5 px-2 py-0.5 rounded bg-fuse-elevated border border-fuse-border text-2xs font-mono text-gray-300">
          <Lock className="w-3 h-3 text-fuse-mint" />
          <span>A3 FROZEN: T<sub>mpnn</sub>=0.1 · T<sub>ps</sub>=1.0 · λ=0.5 · scRMSD≤2.0Å</span>
        </div>

        {/* Live vs Prototype Status Indicator */}
        {backendStatus?.isLive ? (
          <span className="flex items-center space-x-1.5 px-2 py-0.5 rounded bg-fuse-elevated border border-fuse-mint/30 text-2xs font-mono text-fuse-mint">
            <span className="w-1.5 h-1.5 rounded-full bg-fuse-mint animate-pulse"></span>
            <span>GPU LIVE</span>
          </span>
        ) : (
          <span
            className="flex items-center space-x-1.5 px-2 py-0.5 rounded bg-fuse-elevated border border-fuse-amber/30 text-2xs font-mono text-fuse-amber"
            title="Backend disconnected. Displaying verified historical audits in isolated prototype mode."
          >
            <span className="w-1.5 h-1.5 rounded-full bg-fuse-amber"></span>
            <span>PROTOTYPE AUDIT</span>
          </span>
        )}
      </div>
    </header>
  );
};

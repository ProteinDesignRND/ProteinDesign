import React, { useState } from 'react';
import { ChevronDown, ChevronUp } from 'lucide-react';
import { BackendStatus } from '../../services/api';

export interface SystemBannerProps {
  backendStatus: BackendStatus | null;
}

export const SystemBanner: React.FC<SystemBannerProps> = ({ backendStatus }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  if (backendStatus?.isLive) {
    return null;
  }

  return (
    <div className="bg-[#0E0E0E] hairline-b px-4 py-1.5 text-xs text-[#A3A3A3]">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <span className="w-1.5 h-1.5 rounded-full bg-[#38BDF8]"></span>
          <span className="text-[#F5F5F5]">
            Amendment A3 verified constraints active
          </span>
          <span className="hidden sm:inline text-[#282828]">·</span>
          <span className="hidden sm:inline text-[#B99B6A] font-mono text-[11px]">
            Target 1n5uA03 quarantined (audit baseline)
          </span>
        </div>

        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="flex items-center space-x-1 text-[#666666] hover:text-[#F5F5F5] transition-colors text-[11px]"
        >
          <span>{isExpanded ? 'Hide audit' : 'Audit baseline'}</span>
          {isExpanded ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
        </button>
      </div>

      {isExpanded && (
        <div className="max-w-7xl mx-auto pt-2 pb-1 border-t border-[#282828] mt-1.5 text-[11px] text-[#A3A3A3] space-y-1">
          <p>
            • Checkpoint verification: Strict key match (567,060 parameters, EXP004 mask-invariance verified with max logit diff = 0.00e+00).
          </p>
          <p>
            • Quarantine: Target 1n5uA03 demonstrated 41.30% single-target recovery in E0 baseline audit; flagged due to unverified training corpus membership.
          </p>
        </div>
      )}
    </div>
  );
};

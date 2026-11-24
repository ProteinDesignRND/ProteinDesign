import React, { useEffect, useState } from 'react';
import { Outlet } from 'react-router-dom';
import { Navbar } from './Navbar';
import { SystemBanner } from './SystemBanner';
import { BackendStatus, checkBackendStatus } from '../../services/api';
import { ExternalLink } from 'lucide-react';

export const Layout: React.FC = () => {
  const [backendStatus, setBackendStatus] = useState<BackendStatus | null>(null);

  useEffect(() => {
    const verifyStatus = async () => {
      const status = await checkBackendStatus();
      setBackendStatus(status);
    };

    verifyStatus();
    const interval = setInterval(verifyStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen bg-[#080808] text-[#F5F5F5] flex flex-col font-sans selection:bg-[#38BDF8] selection:text-white">
      {/* 44px Top Navigation with Nocturne Botanica Mulberry elevation */}
      <Navbar backendStatus={backendStatus} />

      {/* Verification & Truthfulness Banner */}
      <SystemBanner backendStatus={backendStatus} />

      {/* Main Dynamic View Area */}
      <main className="flex-1 w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Outlet />
      </main>

      {/* Scientific Provenance Footer */}
      <footer className="hairline-t bg-[#0E0E0E] py-4 px-4 sm:px-6 lg:px-8 text-xs text-[#A3A3A3]">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-3">
          <div className="flex items-center space-x-3">
            <span className="font-medium text-[#F5F5F5] font-sans">FUSE</span>
            <span className="text-[#282828]">·</span>
            <span className="text-[#A3A3A3] font-sans text-xs">
              Group G1588 · Framework for Unified Structure-guided Engineering
            </span>
            <span className="text-[#282828]">·</span>
            <span className="text-[#38BDF8] font-mono text-[11px]">
              A3 Frozen Baseline
            </span>
          </div>

          <div className="flex items-center space-x-4 text-xs font-mono text-[#666666]">
            <span>T_mpnn=0.1 · T_ps=1.0 · λ=0.5 · γ=0.0</span>
            <a
              href="sidecar://structural-biology/biomolecular_structure_viewer/ui.html"
              target="_blank"
              rel="noopener noreferrer"
              className="text-[#38BDF8] hover:text-[#B99B6A] flex items-center gap-1 font-sans transition-colors"
            >
              <span>Mol* Sidecar</span>
              <ExternalLink className="w-3 h-3" />
            </a>
          </div>
        </div>
      </footer>
    </div>
  );
};

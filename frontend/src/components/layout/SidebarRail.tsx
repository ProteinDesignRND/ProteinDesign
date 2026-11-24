import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Eye,
  Dna,
  GitFork,
  Activity,
  ListFilter,
  FileCheck2,
  ExternalLink,
  Code2,
} from 'lucide-react';

export const SidebarRail: React.FC = () => {
  const navItems = [
    { to: '/', label: 'Research Dashboard', icon: LayoutDashboard },
    { to: '/structure', label: 'Structure Workbench', icon: Eye },
    { to: '/design-studio', label: 'Design Studio', icon: Dna },
    { to: '/workflow', label: 'Workflow DAG', icon: GitFork },
    { to: '/jobs', label: 'Job Monitor', icon: Activity },
    { to: '/candidates', label: 'Candidate Explorer', icon: ListFilter },
    { to: '/reports', label: 'Reports & Provenance', icon: FileCheck2 },
  ];

  return (
    <aside className="w-[52px] bg-fuse-panel border-r border-fuse-border flex flex-col justify-between shrink-0 select-none z-40">
      {/* Top: FUSE Logo Monogram */}
      <div className="flex flex-col items-center">
        <NavLink
          to="/"
          className="w-[52px] h-[52px] flex items-center justify-center border-b border-fuse-border group"
          title="FUSE: Framework for Unified Structure-guided Engineering"
        >
          <div className="w-7 h-7 rounded bg-fuse-accent/15 border border-fuse-accent/40 flex items-center justify-center text-fuse-accent font-mono font-bold text-xs tracking-tighter group-hover:bg-fuse-accent group-hover:text-white transition-all">
            FU
          </div>
        </NavLink>

        {/* Navigation Icons */}
        <nav className="flex flex-col items-center py-2 space-y-1 w-full">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  `relative w-10 h-10 rounded flex items-center justify-center transition-colors group ${
                    isActive
                      ? 'bg-fuse-elevated text-fuse-accent font-semibold border border-fuse-border'
                      : 'text-gray-400 hover:text-gray-200 hover:bg-fuse-elevated/50'
                  }`
                }
              >
                {({ isActive }) => (
                  <>
                    <Icon className="w-4 h-4 stroke-[1.8]" />
                    {/* Active Left Indicator Pip */}
                    {isActive && (
                      <span className="absolute left-0 top-2 bottom-2 w-[2px] bg-fuse-accent rounded-r"></span>
                    )}

                    {/* Clean Micro Tooltip */}
                    <div className="absolute left-[54px] px-2 py-1 bg-fuse-elevated text-gray-200 text-2xs font-mono rounded border border-fuse-border whitespace-nowrap opacity-0 pointer-events-none group-hover:opacity-100 transition-opacity z-50 shadow-lg">
                      {item.label}
                    </div>
                  </>
                )}
              </NavLink>
            );
          })}
        </nav>
      </div>

      {/* Bottom Utilities */}
      <div className="flex flex-col items-center py-3 border-t border-fuse-border space-y-2">
        {/* Mol* Sidecar Trigger */}
        <a
          href="sidecar://structural-biology/biomolecular_structure_viewer/ui.html"
          target="_blank"
          rel="noopener noreferrer"
          className="relative w-8 h-8 rounded flex items-center justify-center text-gray-400 hover:text-fuse-cyan hover:bg-fuse-elevated transition-colors group"
          title="Open Mol* Sidecar Viewer"
        >
          <ExternalLink className="w-3.5 h-3.5" />
          <div className="absolute left-[54px] px-2 py-1 bg-fuse-elevated text-gray-200 text-2xs font-mono rounded border border-fuse-border whitespace-nowrap opacity-0 pointer-events-none group-hover:opacity-100 transition-opacity z-50 shadow-lg">
            Mol* Sidecar
          </div>
        </a>

        {/* GitHub / Repository */}
        <a
          href="https://github.com/ProteinDesignRND"
          target="_blank"
          rel="noopener noreferrer"
          className="relative w-8 h-8 rounded flex items-center justify-center text-gray-400 hover:text-white hover:bg-fuse-elevated transition-colors group"
          title="GitHub: ProteinDesignRND"
        >
          <Code2 className="w-3.5 h-3.5" />
          <div className="absolute left-[54px] px-2 py-1 bg-fuse-elevated text-gray-200 text-2xs font-mono rounded border border-fuse-border whitespace-nowrap opacity-0 pointer-events-none group-hover:opacity-100 transition-opacity z-50 shadow-lg">
            Repository
          </div>
        </a>
      </div>
    </aside>
  );
};

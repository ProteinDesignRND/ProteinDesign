import React from 'react';
import { NavLink } from 'react-router-dom';
import { BackendStatus } from '../../services/api';

export interface NavbarProps {
  backendStatus: BackendStatus | null;
}

export const Navbar: React.FC<NavbarProps> = () => {
  const navItems = [
    { to: '/', label: 'Overview' },
    { to: '/structure', label: '3D Studio' },
    { to: '/design-studio', label: 'Design' },
    { to: '/workflow', label: 'Workflow' },
    { to: '/jobs', label: 'Jobs' },
    { to: '/candidates', label: 'Candidates' },
    { to: '/reports', label: 'Provenance' },
  ];

  return (
    <header className="sticky top-0 z-50 bg-[#0E0E0E]/95 backdrop-blur hairline-b h-[44px]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex items-center justify-between h-full">
        {/* Brand */}
        <div className="flex items-center space-x-8">
          <NavLink to="/" className="flex items-center space-x-2.5 group">
            <span className="font-semibold text-sm text-[#F5F5F5] tracking-tight font-sans">
              FUSE
            </span>
            <span className="text-[#A3A3A3] text-xs hidden sm:inline">
              Protein Design
            </span>
          </NavLink>

          {/* Navigation Links */}
          <nav className="hidden md:flex items-center space-x-1 h-full">
            {navItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  `h-[44px] flex items-center px-3 text-xs font-sans transition-colors relative border-b-2 ${
                    isActive
                      ? 'border-[#38BDF8] text-[#F5F5F5] font-medium'
                      : 'border-transparent text-[#A3A3A3] hover:text-[#F5F5F5]'
                  }`
                }
              >
                {item.label}
              </NavLink>
            ))}
          </nav>
        </div>

        {/* Right Actions */}
        <div className="flex items-center space-x-4 text-xs font-sans">
          <span className="hidden lg:inline text-[#666666] text-[11px]">
            Amendment A3
          </span>

          <NavLink
            to="/design-studio"
            className="text-[#38BDF8] hover:text-[#B99B6A] font-medium transition-colors"
          >
            + New Design
          </NavLink>
        </div>
      </div>
    </header>
  );
};

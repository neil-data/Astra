import React from 'react';
import { Link } from 'react-router-dom';
import { Satellite, Server, Cpu, Database } from 'lucide-react';

interface FooterProps {
  postgresqlHealthy?: boolean;
  redisHealthy?: boolean;
  apiHealthy?: boolean;
}

export default function Footer({
  postgresqlHealthy = true,
  redisHealthy = true,
  apiHealthy = true
}: FooterProps) {
  return (
    <footer
      id="footer_section"
      className="bg-bg-void border-t border-border-hairline py-16 px-6 lg:px-12 relative overflow-hidden"
    >
      {/* Background Orbs */}
      <div className="absolute right-0 bottom-0 w-80 h-80 glow-violet opacity-30 rounded-full blur-[100px] pointer-events-none" />

      <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-12 relative z-10">
        
        {/* Column 1: Brand & Tagline */}
        <div className="flex flex-col gap-4">
          <div className="flex items-center gap-3">
            <div className="flex items-center justify-center w-8 h-8 border border-teal/30 rounded-full bg-bg-card/40">
              <Satellite className="w-4 h-4 text-teal animate-spin [animation-duration:20s]" />
            </div>
            <span className="font-space font-bold text-lg text-teal tracking-wider">ASTRA</span>
          </div>
          <p className="text-sm text-text-secondary leading-relaxed max-w-sm font-sans">
            Advanced Space Terrain &amp; Radiation Analytics forecasting system for geostationary orbital assets. Engineered for real-time risk assessment, mitigation, and solar particle events prediction.
          </p>
          <div className="font-mono text-[9px] text-text-muted mt-2 tracking-widest uppercase">
            CODENAME: ASTRA // PROTOTYPE V1.0.0
          </div>
        </div>

        {/* Column 2: Structural Link Columns */}
        <div className="grid grid-cols-2 gap-8">
          <div>
            <h4 className="font-mono text-xs text-text-primary tracking-widest uppercase mb-4">SYSTEMS</h4>
            <ul className="space-y-2.5 text-xs font-sans">
              <li>
                <Link to="/login" className="text-text-secondary hover:text-teal transition-colors">
                  Operator Terminal
                </Link>
              </li>
              <li>
                <a href="#architecture" className="text-text-secondary hover:text-teal transition-colors">
                  ML Pipeline Flow
                </a>
              </li>
              <li>
                <a href="#capabilities" className="text-text-secondary hover:text-teal transition-colors">
                  Satellite Shields
                </a>
              </li>
              <li>
                <a href="#mission" className="text-text-secondary hover:text-teal transition-colors">
                  Telemetry Specs
                </a>
              </li>
            </ul>
          </div>
          <div>
            <h4 className="font-mono text-xs text-text-primary tracking-widest uppercase mb-4">PROJECT</h4>
            <ul className="space-y-2.5 text-xs font-sans">
              <li>
                <span className="text-text-secondary cursor-not-allowed">
                  ISRO Hackathon
                </span>
              </li>
              <li>
                <span className="text-text-secondary cursor-not-allowed">
                  GitHub Codebase
                </span>
              </li>
              <li>
                <span className="text-text-secondary cursor-not-allowed">
                  Model Weights
                </span>
              </li>
              <li>
                <span className="text-text-secondary cursor-not-allowed">
                  API Documentation
                </span>
              </li>
            </ul>
          </div>
        </div>

        {/* Column 3: Live System Status */}
        <div className="flex flex-col gap-6">
          <div>
            <h4 className="font-mono text-xs text-text-primary tracking-widest uppercase mb-4">INFRASTRUCTURE</h4>
            <div className="space-y-3 font-mono text-xs">
              <div className="flex items-center justify-between border border-border-hairline bg-bg-card/40 px-3 py-2 rounded">
                <span className="flex items-center gap-2 text-text-secondary">
                  <Database className="w-3.5 h-3.5 text-text-muted" />
                  PostgreSQL
                </span>
                <span className="flex items-center gap-1.5 text-teal font-bold text-[10px]">
                  <span className={`h-1.5 w-1.5 rounded-full bg-teal ${postgresqlHealthy ? 'animate-pulse' : 'bg-danger'}`} />
                  {postgresqlHealthy ? 'CONNECTED' : 'OFFLINE'}
                </span>
              </div>

              <div className="flex items-center justify-between border border-border-hairline bg-bg-card/40 px-3 py-2 rounded">
                <span className="flex items-center gap-2 text-text-secondary">
                  <Server className="w-3.5 h-3.5 text-text-muted" />
                  Redis Cache
                </span>
                <span className="flex items-center gap-1.5 text-teal font-bold text-[10px]">
                  <span className={`h-1.5 w-1.5 rounded-full bg-teal ${redisHealthy ? 'animate-pulse' : 'bg-danger'}`} />
                  {redisHealthy ? 'SYNCHRONIZED' : 'OFFLINE'}
                </span>
              </div>

              <div className="flex items-center justify-between border border-border-hairline bg-bg-card/40 px-3 py-2 rounded">
                <span className="flex items-center gap-2 text-text-secondary">
                  <Cpu className="w-3.5 h-3.5 text-text-muted" />
                  API Service
                </span>
                <span className="flex items-center gap-1.5 text-teal font-bold text-[10px]">
                  <span className={`h-1.5 w-1.5 rounded-full bg-teal ${apiHealthy ? 'animate-pulse' : 'bg-danger'}`} />
                  {apiHealthy ? 'SECURE' : 'OFFLINE'}
                </span>
              </div>
            </div>
          </div>
        </div>

      </div>

      {/* Bottom Bar */}
      <div className="max-w-7xl mx-auto border-t border-border-hairline mt-12 pt-8 flex flex-col sm:flex-row items-center justify-between gap-4 relative z-10">
        <p className="font-mono text-[10px] text-text-muted tracking-wider">
          © 2026 ASTRA · DEVELOPED FOR ISRO BHARATIYA ANTARIKSH HACKATHON 2026
        </p>
        <div className="flex items-center gap-2 font-mono text-[10px] text-teal tracking-wider uppercase">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-teal opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-teal"></span>
          </span>
          All systems operational
        </div>
      </div>
    </footer>
  );
}

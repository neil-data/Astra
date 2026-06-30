import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { motion, AnimatePresence } from 'motion/react';
import { Satellite, ArrowRight, Activity } from 'lucide-react';

interface HeaderProps {
  currentKp?: number;
  currentRisk?: string;
  isDashboard?: boolean;
}

export default function Header({ currentKp = 3.2, currentRisk = 'LOW', isDashboard = false }: HeaderProps) {
  const [scrolled, setScrolled] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 100);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  // Magnetic button effect handler
  const [coords, setCoords] = useState({ x: 0, y: 0 });
  const [isHovered, setIsHovered] = useState(false);

  const handleMouseMove = (e: React.MouseEvent<HTMLButtonElement>) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const x = e.clientX - rect.left - rect.width / 2;
    const y = e.clientY - rect.top - rect.height / 2;
    // limit transform range to 10px radius
    setCoords({ x: x * 0.35, y: y * 0.35 });
  };

  const handleMouseLeave = () => {
    setIsHovered(false);
    setCoords({ x: 0, y: 0 });
  };

  const riskColor = 
    currentRisk === 'EXTREME' ? 'text-danger border-danger/30 bg-danger/10' :
    currentRisk === 'HIGH' ? 'text-warning border-warning/30 bg-warning/10' :
    currentRisk === 'MEDIUM' ? 'text-yellow-400 border-yellow-400/30 bg-yellow-400/10' :
    'text-teal border-teal/30 bg-teal/10';

  const scrollToSection = (id: string) => {
    if (isDashboard) {
      navigate('/');
      setTimeout(() => {
        document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' });
      }, 100);
    } else {
      document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <header
      id="header_main"
      className={`fixed top-0 left-0 right-0 h-[72px] z-50 transition-all duration-300 flex items-center justify-between px-6 lg:px-12 ${
        scrolled 
          ? 'bg-bg-void/90 backdrop-blur-md border-b border-border-hairline' 
          : 'bg-transparent border-b border-transparent'
      }`}
    >
      {/* Left: Brand Logotype */}
      <Link 
        id="logo_link"
        to="/" 
        className="flex items-center gap-3 group focus:outline-none"
      >
        <div className="relative flex items-center justify-center w-9 h-9 border border-teal/40 rounded-full bg-bg-card/40 group-hover:border-teal group-hover:shadow-[0_0_12px_rgba(0,255,209,0.3)] transition-all duration-300">
          <Satellite className="w-5 h-5 text-teal group-hover:rotate-[360deg] transition-transform duration-700 ease-out" />
          <span className="absolute inset-0 border border-dotted border-teal-dim/20 rounded-full animate-spin [animation-duration:15s]" />
        </div>
        <div className="flex flex-col">
          <span className="font-space font-bold text-lg text-teal tracking-wider leading-none">ASTRA</span>
          <span className="font-mono text-[8px] text-text-muted tracking-[0.2em] leading-none uppercase mt-0.5">ISRO · BAH 2026</span>
        </div>
      </Link>

      {/* Center: Interactive Nav Links (Only if not on active dashboard screen) */}
      {!isDashboard ? (
        <nav id="landing_nav" className="hidden md:flex items-center gap-8">
          {[
            { name: 'Mission', id: 'mission' },
            { name: 'Architecture', id: 'architecture' },
            { name: 'Capabilities', id: 'capabilities' },
            { name: 'Team', id: 'team' }
          ].map((item) => (
            <button
              id={`nav_btn_${item.name.toLowerCase()}`}
              key={item.id}
              onClick={() => scrollToSection(item.id)}
              className="relative text-sm font-sans font-medium text-text-secondary hover:text-text-primary transition-colors py-2 group cursor-pointer"
            >
              {item.name}
              <span className="absolute bottom-0 left-0 w-0 h-[2px] bg-teal group-hover:w-full transition-all duration-300 ease-out" />
            </button>
          ))}
        </nav>
      ) : (
        <div id="dashboard_title" className="hidden md:flex items-center gap-2">
          <Activity className="w-4 h-4 text-teal animate-pulse" />
          <span className="font-mono text-[11px] text-teal tracking-[0.25em] uppercase">SPACE RADIATION REAL-TIME MONITORING</span>
        </div>
      )}

      {/* Right: Live Ticker / Actions */}
      <div id="header_right" className="flex items-center gap-6">
        <div className="hidden lg:flex items-center gap-3 border border-border-hairline bg-bg-card/60 px-3 py-1.5 rounded font-mono text-[10px] tracking-wider">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-teal opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-teal"></span>
          </span>
          <span className="text-teal font-bold">LIVE FEED</span>
          <span className="text-text-muted">|</span>
          <span className="text-text-secondary">KP: <span className="text-text-primary font-bold">{currentKp.toFixed(1)}</span></span>
          <span className="text-text-muted">|</span>
          <span className={`px-1.5 py-0.2 rounded font-bold uppercase text-[9px] border ${riskColor}`}>
            RISK {currentRisk}
          </span>
        </div>

        {!isDashboard ? (
          <motion.button
            id="cta_mission_control"
            onMouseMove={handleMouseMove}
            onMouseLeave={handleMouseLeave}
            onMouseEnter={() => setIsHovered(true)}
            onClick={() => navigate('/login')}
            style={{
              transform: isHovered ? `translate3d(${coords.x}px, ${coords.y}px, 0)` : 'none'
            }}
            className="btn-magnetic relative group overflow-hidden bg-teal text-bg-void px-5 py-2.5 rounded font-space font-medium text-xs tracking-wider uppercase cursor-pointer flex items-center gap-2 hover:shadow-[0_0_20px_rgba(0,255,209,0.5)] transition-shadow duration-300"
          >
            <span className="relative z-10 flex items-center gap-2">
              Mission Control
              <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform" />
            </span>
          </motion.button>
        ) : (
          <button
            id="header_logout_btn"
            onClick={() => {
              localStorage.removeItem('operatorName');
              navigate('/login');
            }}
            className="text-xs font-mono border border-border-hairline bg-bg-card text-text-secondary hover:text-danger hover:border-danger/30 px-3 py-1.5 rounded cursor-pointer transition-colors"
          >
            TERMINATE SESSION
          </button>
        )}
      </div>
    </header>
  );
}

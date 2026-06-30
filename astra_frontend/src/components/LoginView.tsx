import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { motion } from 'motion/react';
import { Satellite, Eye, EyeOff, ShieldCheck, HelpCircle } from 'lucide-react';

interface LoginViewProps {
  health: any;
}

export default function LoginView({ health }: LoginViewProps) {
  const navigate = useNavigate();
  const [operatorId, setOperatorId] = useState('');
  const [accessCode, setAccessCode] = useState('');
  const [showCode, setShowCode] = useState(false);
  const [rememberMe, setRememberMe] = useState(true);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [showSuccess, setShowSuccess] = useState(false);

  // Quick autofill for grading/testing convenience if they want to click
  const handleAutofill = () => {
    setOperatorId('isro.operator@astra.gov.in');
    setAccessCode('ASTRA-2026-SECURE');
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage('');

    if (!operatorId.trim()) {
      setErrorMessage('OPERATOR ID REQUIRED');
      return;
    }
    if (!accessCode.trim()) {
      setErrorMessage('ACCESS CODE REQUIRED');
      return;
    }

    setIsLoading(true);

    // Simulate secure handshakes
    setTimeout(() => {
      setIsLoading(false);
      setShowSuccess(true);
      
      // Store operator name from email or default
      const name = operatorId.split('@')[0].replace('.', ' ').toUpperCase() || 'CHIEF OPERATOR';
      localStorage.setItem('operatorName', name);

      setTimeout(() => {
        navigate('/dashboard');
      }, 1000);
    }, 1500);
  };

  return (
    <div id="login_view_root" className="min-h-screen w-screen bg-bg-void relative flex items-center justify-center p-4 overflow-hidden select-none">
      
      {/* Background Layers */}
      <div className="absolute inset-0 dot-grid opacity-20 pointer-events-none" />
      <div className="scanline-effect opacity-30 pointer-events-none" />

      {/* Orbiting Ring SVG */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] pointer-events-none z-0">
        <svg className="w-full h-full animate-spin [animation-duration:60s]" viewBox="0 0 200 200">
          <circle 
            cx="100" 
            cy="100" 
            r="85" 
            fill="none" 
            stroke="#00FFD1" 
            strokeWidth="0.5" 
            strokeDasharray="4 8" 
            className="opacity-10" 
          />
          <circle 
            cx="100" 
            cy="100" 
            r="70" 
            fill="none" 
            stroke="#7C3AED" 
            strokeWidth="0.25" 
            className="opacity-15" 
          />
        </svg>
      </div>

      {/* Floating coordinates for maximalist texture */}
      <div className="absolute top-8 left-8 font-mono text-[9px] text-text-ghost uppercase space-y-1 select-none pointer-events-none">
        <p>TERMINAL: GEO_TERM_09</p>
        <p>LAT 23.0225° N // LON 72.5714° E</p>
        <p>ORBIT GEO-STAT // ALT 35,786 KM</p>
      </div>
      
      <div className="absolute bottom-8 right-8 font-mono text-[9px] text-text-ghost uppercase text-right space-y-1 select-none pointer-events-none">
        <p>SECURE PROTOCOL TLS 1.3</p>
        <p>SHIELD HARDENING: SECURE</p>
        <p>BAH ISRO // 2026</p>
      </div>

      {/* Top Left Branding Mark Link */}
      <div className="absolute top-8 left-1/2 md:left-8 -translate-x-1/2 md:translate-x-0 z-20">
        <Link to="/" className="flex items-center gap-3 group">
          <div className="flex items-center justify-center w-8 h-8 border border-teal/30 rounded-full bg-bg-card">
            <Satellite className="w-4 h-4 text-teal group-hover:rotate-180 transition-transform duration-500" />
          </div>
          <span className="font-space font-bold tracking-widest text-teal text-sm">ASTRA</span>
        </Link>
      </div>

      {/* Main Glass Morphic Login Card */}
      <motion.div
        initial={{ opacity: 0, y: 15, scale: 0.98 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        transition={{ duration: 0.5, ease: 'easeOut' }}
        className="w-full max-w-[460px] bg-bg-card/70 backdrop-blur-xl border border-border-hairline rounded-lg p-8 relative z-10 shadow-[0_20px_50px_rgba(0,0,0,0.5)] focus-within:border-teal/30 focus-within:shadow-[0_0_30px_rgba(0,255,209,0.06)] transition-all duration-300"
      >
        {/* Success Overlay Flash */}
        {showSuccess && (
          <div className="absolute inset-0 bg-bg-card/95 backdrop-blur-md rounded-lg z-20 flex flex-col items-center justify-center p-6 border border-teal text-center animate-fade-in">
            <div className="h-12 w-12 rounded-full border border-teal bg-teal/10 flex items-center justify-center text-teal shadow-[0_0_20px_rgba(0,255,209,0.3)] mb-4 animate-bounce">
              <ShieldCheck className="w-6 h-6" />
            </div>
            <h3 className="font-space font-bold text-lg text-teal tracking-widest uppercase">
              SESSION HANDSHAKE OK
            </h3>
            <p className="font-mono text-[11px] text-text-secondary mt-1">
              Establishing satellite proxy tunnels...
            </p>
            <div className="w-24 bg-bg-void h-1 rounded overflow-hidden mt-6 relative">
              <div className="bg-teal h-full w-full animate-pulse" />
            </div>
          </div>
        )}

        {/* Card Header Info */}
        <div className="flex flex-col items-center text-center gap-2 mb-8">
          <div className="flex items-center justify-center w-10 h-10 border border-teal/40 rounded-full bg-bg-card shadow-[0_0_12px_rgba(0,255,209,0.15)]">
            <Satellite className="w-5 h-5 text-teal animate-pulse" />
          </div>
          <h2 className="font-space font-bold text-text-primary text-xl tracking-widest uppercase mt-2">
            MISSION CONTROL ACCESS
          </h2>
          <p className="font-mono text-[10px] text-text-muted uppercase tracking-widest">
            Authorized Space Terrain Operators Only
          </p>
        </div>

        {/* Action Form */}
        <form onSubmit={handleSubmit} className="space-y-6">
          
          {errorMessage && (
            <div className="border border-danger/40 bg-danger/5 px-4 py-2.5 rounded text-danger font-mono text-[11px] font-bold text-center tracking-wider animate-shake">
              ERROR: {errorMessage}
            </div>
          )}

          {/* Email / ID Input */}
          <div className="space-y-2">
            <div className="flex justify-between items-center">
              <label className="font-mono text-[10px] font-bold text-text-muted tracking-widest uppercase">
                OPERATOR CREDENTIAL ID
              </label>
              <button
                type="button"
                onClick={handleAutofill}
                className="font-mono text-[9px] text-teal/60 hover:text-teal underline cursor-pointer"
              >
                AUTOFILL DEMO
              </button>
            </div>
            <input
              id="operator_id_input"
              type="email"
              autoComplete="username"
              value={operatorId}
              onChange={(e) => setOperatorId(e.target.value)}
              placeholder="isro.operator@astra.gov.in"
              className="w-full bg-bg-void/80 border border-border-hairline text-text-primary px-4 py-3 rounded text-sm font-mono placeholder:text-text-ghost focus:outline-none focus:border-teal/60 focus:ring-1 focus:ring-teal/30 transition-colors"
            />
          </div>

          {/* Password / Access Code Input */}
          <div className="space-y-2">
            <div className="flex justify-between items-center">
              <label className="font-mono text-[10px] font-bold text-text-muted tracking-widest uppercase">
                SECURE ACCESS SHA CODE
              </label>
              <span className="font-mono text-[9px] text-text-ghost uppercase">AES-256</span>
            </div>
            <div className="relative">
              <input
                id="access_code_input"
                type={showCode ? 'text' : 'password'}
                autoComplete="current-password"
                value={accessCode}
                onChange={(e) => setAccessCode(e.target.value)}
                placeholder="••••••••••••••••"
                className="w-full bg-bg-void/80 border border-border-hairline text-text-primary pl-4 pr-10 py-3 rounded text-sm font-mono placeholder:text-text-ghost focus:outline-none focus:border-teal/60 focus:ring-1 focus:ring-teal/30 transition-colors"
              />
              <button
                type="button"
                onClick={() => setShowCode(!showCode)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-text-muted hover:text-teal cursor-pointer"
              >
                {showCode ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
          </div>

          {/* Remember & Forgot Checkboxes */}
          <div className="flex items-center justify-between font-mono text-[10px] tracking-wider text-text-secondary select-none">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={rememberMe}
                onChange={(e) => setRememberMe(e.target.checked)}
                className="accent-teal rounded border-border-hairline w-3.5 h-3.5"
              />
              Remember terminal
            </label>
            <div className="flex items-center gap-1 hover:text-teal cursor-help">
              <HelpCircle className="w-3 h-3" />
              <span>Forgot access?</span>
            </div>
          </div>

          {/* Initiate Session Submit Button */}
          <button
            id="login_submit_btn"
            type="submit"
            disabled={isLoading}
            className="w-full bg-teal hover:bg-teal-dim text-bg-void disabled:bg-teal/40 disabled:text-bg-void/70 py-4 rounded font-space font-bold text-xs uppercase tracking-widest flex items-center justify-center gap-2 cursor-pointer shadow-[0_4px_15px_rgba(0,255,209,0.15)] hover:shadow-[0_0_20px_rgba(0,255,209,0.4)] transition-all duration-300"
          >
            {isLoading ? (
              <span className="flex items-center gap-2">
                <svg className="animate-spin h-4 w-4 text-bg-void" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
                HANDSHAKING ENCRYPTORS
              </span>
            ) : (
              'INITIATE SESSION →'
            )}
          </button>

        </form>

        {/* Divider status line */}
        <div className="my-8 flex items-center justify-center font-mono text-[9px] text-text-ghost tracking-[0.2em] uppercase select-none">
          <span className="w-12 h-[1px] bg-border-hairline" />
          <span className="mx-3">SYSTEM HARDWARE STATUS</span>
          <span className="w-12 h-[1px] bg-border-hairline" />
        </div>

        {/* Live status indicators */}
        <div className="grid grid-cols-3 gap-2 text-center font-mono text-[9px] tracking-widest text-text-secondary select-none">
          <div className="border border-border-hairline/60 bg-bg-void/40 p-2 rounded flex flex-col items-center">
            <span className="text-text-muted mb-1 uppercase">POSTGRES</span>
            <div className="flex items-center gap-1 text-[8px] font-bold text-teal">
              <span className={`h-1.5 w-1.5 rounded-full ${health?.postgresql === 'healthy' ? 'bg-teal animate-pulse' : 'bg-danger'}`} />
              {health?.postgresql === 'healthy' ? 'OK' : 'DOWN'}
            </div>
          </div>

          <div className="border border-border-hairline/60 bg-bg-void/40 p-2 rounded flex flex-col items-center">
            <span className="text-text-muted mb-1 uppercase">REDIS</span>
            <div className="flex items-center gap-1 text-[8px] font-bold text-teal">
              <span className={`h-1.5 w-1.5 rounded-full ${health?.redis === 'healthy' ? 'bg-teal animate-pulse' : 'bg-danger'}`} />
              {health?.redis === 'healthy' ? 'OK' : 'DOWN'}
            </div>
          </div>

          <div className="border border-border-hairline/60 bg-bg-void/40 p-2 rounded flex flex-col items-center">
            <span className="text-text-muted mb-1 uppercase">API SWPC</span>
            <div className="flex items-center gap-1 text-[8px] font-bold text-teal">
              <span className={`h-1.5 w-1.5 rounded-full ${health?.api === 'healthy' ? 'bg-teal animate-pulse' : 'bg-danger'}`} />
              {health?.api === 'healthy' ? 'OK' : 'DOWN'}
            </div>
          </div>
        </div>

        {/* Card bottom branding footer */}
        <div className="mt-8 text-center font-mono text-[8px] text-text-ghost uppercase select-none">
          ASTRA SEC_PORTAL v1.0.0 · BHARATIYA ANTARIKSH HACKATHON 2026
        </div>

      </motion.div>
    </div>
  );
}

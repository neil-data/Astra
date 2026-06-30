import React, { useEffect, useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence, useScroll, useTransform, useInView } from 'motion/react';
import gsap from 'gsap';
import {
  Satellite,
  ArrowRight,
  Shield,
  Zap,
  Bell,
  CheckCircle,
  TrendingUp,
  RefreshCw,
  Clock,
  Database,
  Terminal,
  Server,
  Code,
  Radio,
  Sliders,
  Play,
  Activity,
  ChevronRight,
  ShieldAlert,
  Cpu
} from 'lucide-react';
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import Header from './Header';
import Footer from './Footer';
import HeroSatelliteCanvas from './HeroSatelliteCanvas';
import InsideAstraCanvas from './InsideAstraCanvas';
import { Telemetry, ForecastSummary, Alert } from '../types';

interface LandingViewProps {
  currentTelemetry: Telemetry | null;
  historyData: Telemetry[];
  forecastSummary: ForecastSummary[];
  activeAlerts: Alert[];
  health: any;
}

export default function LandingView({
  currentTelemetry,
  historyData,
  forecastSummary,
  activeAlerts,
  health
}: LandingViewProps) {
  const navigate = useNavigate();

  // --- PERSISTENT LOADING SCREEN STATE ---
  const [showLoader, setShowLoader] = useState(true);
  const [percent, setPercent] = useState(0);
  const [loaderMessage, setLoaderMessage] = useState('SYSTEM_INITIALIZATION');
  const [exitLoader, setExitLoader] = useState(false);

  useEffect(() => {
    // Check if loaded in this session
    const alreadyLoaded = sessionStorage.getItem('astra_loaded');
    if (alreadyLoaded) {
      setShowLoader(false);
      return;
    }

    // Loader percentages loop over 2.5s with slight jitter & ease
    let startTimestamp: number | null = null;
    const duration = 2400; // ms

    const step = (timestamp: number) => {
      if (!startTimestamp) startTimestamp = timestamp;
      const progress = timestamp - startTimestamp;
      const progressPercent = Math.min(progress / duration, 1);

      // Quadratic ease out
      const easedPercent = Math.floor(100 * (1 - Math.pow(1 - progressPercent, 3.5)));
      
      // Slight random jitter around the numbers for high-tech feeling
      const jitter = Math.random() > 0.82 && easedPercent < 98 ? Math.floor(Math.random() * 2) - 1 : 0;
      const displayPercent = Math.max(0, Math.min(100, easedPercent + jitter));

      setPercent(displayPercent);

      // Transition loading texts based on percentages
      if (displayPercent < 25) {
        setLoaderMessage('CONNECTING TO NOAA SWPC...');
      } else if (displayPercent < 52) {
        setLoaderMessage('SYNCING GOES-16 TELEMETRY...');
      } else if (displayPercent < 78) {
        setLoaderMessage('LOADING NASA DONKI FEED...');
      } else if (displayPercent < 100) {
        setLoaderMessage('CALIBRATING RISK MODELS...');
      } else {
        setLoaderMessage('SYSTEM OPERATIONAL // FULL RECOV');
      }

      if (progress < duration) {
        window.requestAnimationFrame(step);
      } else {
        setPercent(100);
        // Completed loading, fade out screen
        setTimeout(() => {
          setExitLoader(true);
          setTimeout(() => {
            setShowLoader(false);
            sessionStorage.setItem('astra_loaded', 'true');
          }, 600);
        }, 400);
      }
    };

    window.requestAnimationFrame(step);
  }, []);

  // --- TIME COUNTERS & PREVIEW CALCULATIONS ---
  const [syncedTime, setSyncedTime] = useState('0s ago');
  useEffect(() => {
    if (!currentTelemetry) return;
    const interval = setInterval(() => {
      const elapsed = Math.round((Date.now() - new Date(currentTelemetry.timestamp).getTime()) / 1000);
      if (elapsed < 60) {
        setSyncedTime(`${elapsed}s ago`);
      } else {
        setSyncedTime(`${Math.floor(elapsed / 60)}m ago`);
      }
    }, 1000);
    return () => clearInterval(interval);
  }, [currentTelemetry]);

  // Map real API response to telemetry shape, with safe fallbacks
  const telemetry = currentTelemetry ? {
    solarWind: currentTelemetry.predicted_solar_wind ?? 432.1,
    Kp: currentTelemetry.predicted_kp_index ?? 3.2,
    protonFlux: currentTelemetry.predicted_proton_flux ?? 1205.4,
    Bz: currentTelemetry.predicted_bz ?? 2.1,
    risk: (currentTelemetry.risk_level ?? 'LOW') as Telemetry['risk'],
    timestamp: currentTelemetry.forecast_time ?? new Date().toISOString(),
    source: 'NOAA' as Telemetry['source']
  } : {
    solarWind: 432.1,
    Kp: 3.2,
    protonFlux: 1205.4,
    Bz: 2.1,
    risk: 'LOW' as Telemetry['risk'],
    timestamp: new Date().toISOString(),
    source: 'NOAA' as Telemetry['source']
  };

  // --- SCROLL-DRIVEN TIMELINE CONFIGS (Framer Motion) ---
  const [timelineSection, setTimelineSection] = useState<HTMLDivElement | null>(null);
  
  // Track scroll position in the timeline section
  const { scrollYProgress } = useScroll({
    target: timelineSection ? { current: timelineSection } : undefined,
    offset: ["start center", "end end"]
  });

  // Grow vertical timeline height based on scroll progress
  const lineHeight = useTransform(scrollYProgress, [0, 0.95], ["0%", "100%"]);

  // Set up view detectors for step animations
  const step1Ref = useRef(null);
  const step2Ref = useRef(null);
  const step3Ref = useRef(null);
  const step4Ref = useRef(null);

  const step1InView = useInView(step1Ref, { once: false, amount: 0.45 });
  const step2InView = useInView(step2Ref, { once: false, amount: 0.45 });
  const step3InView = useInView(step3Ref, { once: false, amount: 0.45 });
  const step4InView = useInView(step4Ref, { once: false, amount: 0.45 });

  // Fallback charts dataset
  const mockChartData = historyData.length > 0 ? historyData.slice(-15) : [
    { timestamp: '12:00', Kp: 2.1, protonFlux: 1000, solarWind: 400 },
    { timestamp: '14:00', Kp: 3.2, protonFlux: 1100, solarWind: 420 },
    { timestamp: '16:00', Kp: 2.8, protonFlux: 1250, solarWind: 430 },
    { timestamp: '18:00', Kp: 3.5, protonFlux: 1050, solarWind: 410 },
    { timestamp: '20:00', Kp: 4.1, protonFlux: 1300, solarWind: 440 },
    { timestamp: '22:00', Kp: 3.0, protonFlux: 1205, solarWind: 432 },
    { timestamp: '00:00', Kp: 3.2, protonFlux: 1205, solarWind: 432 },
  ];

  // Helper formatting for charts
  const formatXAxis = (tickItem: string) => {
    try {
      const d = new Date(tickItem);
      if (isNaN(d.getTime())) return tickItem;
      return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: false });
    } catch {
      return tickItem;
    }
  };

  return (
    <div id="landing_view_root" className="min-h-screen bg-bg-void text-text-primary selection:bg-teal selection:text-bg-void font-sans overflow-x-hidden">

      {/* ── BACKGROUND LAYOUTS ── */}
      <div className="absolute inset-0 dot-grid opacity-20 pointer-events-none z-0" />
      <div className="scanline-effect pointer-events-none opacity-20" />

      {/* Ambient glowing orbs */}
      <div className="absolute top-[25vh] left-[-10vw] w-[65vw] h-[65vw] glow-teal opacity-10 rounded-full blur-[140px] pointer-events-none" />
      <div className="absolute top-[120vh] right-[-10vw] w-[55vw] h-[55vw] glow-violet opacity-12 rounded-full blur-[120px] pointer-events-none" />

      {/* ── SEQUENCE 1: INITIALIZATION LOADING SCREEN ── */}
      <AnimatePresence>
        {showLoader && (
          <motion.div
            id="initial_systems_loader"
            initial={{ opacity: 1 }}
            animate={exitLoader ? { opacity: 0, scale: 0.95 } : { opacity: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
            className="fixed inset-0 z-50 bg-[#020305] flex flex-col justify-between p-8"
          >
            {/* Top mini progress bar */}
            <div 
              id="top_loader_progress_bar" 
              className="absolute top-0 left-0 h-[2.5px] bg-teal transition-all duration-75"
              style={{ width: `${percent}%` }}
            />

            {/* Header labels */}
            <div className="flex justify-between items-center border-b border-border-hairline pb-4 font-mono text-[9px] text-text-muted tracking-widest uppercase">
              <span>SYSTEM_INITIALIZATION</span>
              <span>V 1.0.0</span>
            </div>

            {/* Centered large counter */}
            <div className="flex flex-col items-start justify-center flex-1 max-w-5xl mx-auto w-full md:pl-12">
              <span className="font-mono text-xs text-teal tracking-widest uppercase font-bold mb-4">
                LOADING DATA REPOSITORY
              </span>
              <h2 className="font-space font-bold tracking-tighter text-text-primary select-none flex items-baseline leading-none">
                <span className="text-[clamp(80px,16vw,200px)]">{percent}</span>
                <span className="font-mono text-[clamp(40px,8vw,100px)] text-teal font-normal">%</span>
              </h2>

              <div className="h-5 overflow-hidden mt-6">
                <AnimatePresence mode="wait">
                  <motion.div
                    key={loaderMessage}
                    initial={{ opacity: 0, y: 12 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -12 }}
                    transition={{ duration: 0.35 }}
                    className="font-mono text-xs text-text-secondary tracking-widest uppercase font-bold"
                  >
                    {loaderMessage}
                  </motion.div>
                </AnimatePresence>
              </div>
            </div>

            {/* Footer tags */}
            <div className="flex flex-col sm:flex-row justify-between items-center border-t border-border-hairline pt-4 font-mono text-[8px] text-text-ghost tracking-widest uppercase gap-2">
              <span>ASTRA LABS // DEEP SPACE FORECAST MODEL</span>
              <span>ISRO BHARATIYA ANTARIKSH HACKATHON 2026</span>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Render core landing page */}
      <div className="w-full relative">
          
          {/* Sticky Header Nav */}
          <Header currentKp={telemetry.Kp} currentRisk={telemetry.risk} />

          {/* ── SEQUENCE 2: LOGO REVEAL SECTION (Pins for full height) ── */}
          <section id="logo_reveal_section" className="w-full h-screen bg-bg-void flex flex-col items-center justify-center relative select-none">
            
            {/* Ambient centered backlighting */}
            <div className="absolute w-[600px] h-[600px] bg-gradient-to-tr from-teal/5 to-violet/10 rounded-full blur-[140px] pointer-events-none" />

            {/* Staggered entry name */}
            <div className="flex flex-col items-center max-w-5xl px-6 text-center z-10">
              <h1 className="font-space font-bold text-text-primary tracking-tighter select-none leading-none mb-4">
                {Array.from("ASTRA").map((letter, index) => (
                  <motion.span
                    key={index}
                    initial={{ opacity: 0, y: 35 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{
                      duration: 0.8,
                      delay: 0.1 + index * 0.08,
                      ease: [0.16, 1, 0.3, 1],
                    }}
                    className="inline-block text-[clamp(80px,14vw,180px)]"
                  >
                    {letter}
                  </motion.span>
                ))}
              </h1>

              {/* Tagline flanked by elegant teal line segments */}
              <motion.div
                initial={{ opacity: 0, scaleX: 0 }}
                animate={{ opacity: 1, scaleX: 1 }}
                transition={{ duration: 1, delay: 0.6, ease: 'easeOut' }}
                className="flex items-center gap-4 w-full justify-center max-w-3xl mt-2 overflow-hidden"
              >
                <div className="h-[1px] bg-teal/50 flex-1 hidden sm:block" />
                <span className="font-mono text-[10px] md:text-xs text-teal tracking-[0.2em] font-bold uppercase whitespace-nowrap px-4">
                  ADVANCED SPACE TERRAIN &amp; RADIATION ANALYTICS
                </span>
                <div className="h-[1px] bg-teal/50 flex-1 hidden sm:block" />
              </motion.div>
            </div>

            {/* Bottom Scroll afforance */}
            <motion.div
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 1.2 }}
              className="absolute bottom-10 left-1/2 -translate-x-1/2 flex flex-col items-center gap-2 z-10 text-center cursor-pointer"
              onClick={() => document.getElementById('mission')?.scrollIntoView({ behavior: 'smooth' })}
            >
              <span className="font-mono text-[9px] text-text-muted uppercase tracking-[0.2em] font-bold animate-pulse">
                SCROLL TO EXPLORE
              </span>
              <div className="w-[1.5px] h-12 bg-border-hairline relative overflow-hidden rounded-full">
                <motion.div
                  animate={{
                    y: ["-100%", "100%"]
                  }}
                  transition={{
                    duration: 1.8,
                    repeat: Infinity,
                    ease: "easeInOut"
                  }}
                  className="absolute top-0 left-0 w-full h-1/2 bg-teal shadow-[0_0_8px_rgba(0,255,209,1)]"
                />
              </div>
            </motion.div>
          </section>

          {/* ── SEQUENCE 3: MAIN HERO ── */}
          <section id="mission" className="relative min-h-[105vh] flex flex-col justify-center pt-28 pb-12 px-6 lg:px-12 max-w-7xl mx-auto z-10 border-b border-border-hairline/60 scroll-mt-24">
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center w-full mt-4">
              
              {/* Hero Left Side */}
              <div className="lg:col-span-7 flex flex-col gap-6 text-left relative z-10">
                
                {/* Antariksh Hackathon badge with rise effect */}
                <motion.div
                  initial={{ opacity: 0, y: 15 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.5, ease: 'easeOut' }}
                  className="inline-flex items-center gap-2 border border-teal/30 bg-teal/5 px-3 py-1.5 rounded-full self-start"
                >
                  <span className="h-1.5 w-1.5 rounded-full bg-teal animate-pulse" />
                  <span className="font-mono text-[10px] uppercase tracking-widest text-teal font-bold">
                    ISRO BHARATIYA ANTARIKSH HACKATHON 2026
                  </span>
                </motion.div>

                {/* Main Headline */}
                <h2 className="font-space font-bold tracking-tight text-text-primary leading-[0.9] flex flex-col">
                  <span className="text-[clamp(48px,7.5vw,90px)] font-bold">
                    Predict space
                  </span>
                  <span className="text-[clamp(48px,7.5vw,90px)] font-bold text-teal drop-shadow-[0_0_15px_rgba(0,255,209,0.22)]">
                    radiation.
                  </span>
                  <span className="font-space font-medium text-[clamp(18px,3.2vw,32px)] text-text-secondary tracking-normal mt-4 border-l-2 border-teal/40 pl-4">
                    Protect ISRO satellites.
                  </span>
                </h2>

                <p className="text-text-secondary text-sm md:text-base leading-relaxed max-w-[500px] font-sans">
                  Real-time AI forecasting for energetic particle radiation around geostationary satellites — 1h, 3h, and 24h ahead. Analyzing live telemetric signals with deep LSTM networks to secure orbital hardware.
                </p>

                {/* Dual-action Buttons */}
                <div className="flex flex-wrap items-center gap-4 mt-2">
                  <button
                    id="hero_launch_dashboard_btn"
                    onClick={() => navigate('/login')}
                    className="group relative flex items-center gap-2 bg-teal text-bg-void hover:bg-teal-dim font-space font-bold text-xs uppercase tracking-wider px-6 py-4 rounded cursor-pointer hover:shadow-[0_0_25px_rgba(0,255,209,0.5)] transition-all duration-300"
                  >
                    Launch Dashboard
                    <ArrowRight className="w-4 h-4 group-hover:translate-x-1.5 transition-transform" />
                  </button>
                  <button
                    id="hero_view_demo_btn"
                    onClick={() => document.getElementById('dashboard-preview')?.scrollIntoView({ behavior: 'smooth' })}
                    className="flex items-center gap-2 border border-border-strong text-text-secondary hover:text-teal hover:border-teal/50 hover:bg-teal/5 bg-bg-card/40 font-space font-bold text-xs uppercase tracking-wider px-6 py-4 rounded cursor-pointer transition-all duration-300"
                  >
                    <Play className="w-3.5 h-3.5 fill-current" />
                    View Live Demo
                  </button>
                </div>
              </div>

              {/* Hero Right Side: Three.js Satellite Viewport with Floating Card */}
              <div className="lg:col-span-5 flex flex-col items-center justify-center relative min-h-[400px] sm:min-h-[500px]">
                
                {/* Raw Three.js Low-poly Satellite Canvas */}
                <div className="w-full absolute inset-0 z-0">
                  <HeroSatelliteCanvas />
                </div>

                {/* Overlapping Floating Telemetry Card */}
                <motion.div
                  initial={{ opacity: 0, y: 30, scale: 0.95 }}
                  whileInView={{ opacity: 1, y: 0, scale: 1 }}
                  viewport={{ once: true, margin: "-100px" }}
                  transition={{ duration: 0.7, delay: 0.2 }}
                  className="w-full max-w-[360px] border border-border-hairline hover:border-teal/30 bg-bg-card/85 backdrop-blur-md rounded-lg p-5 shadow-2xl relative z-10 mt-auto ml-auto group transition-colors"
                >
                  {/* Glowing corners */}
                  <div className="absolute top-0 left-0 w-2.5 h-2.5 border-t border-l border-teal/40 group-hover:border-teal" />
                  <div className="absolute top-0 right-0 w-2.5 h-2.5 border-t border-r border-teal/40 group-hover:border-teal" />
                  <div className="absolute bottom-0 left-0 w-2.5 h-2.5 border-b border-l border-teal/40 group-hover:border-teal" />
                  <div className="absolute bottom-0 right-0 w-2.5 h-2.5 border-b border-r border-teal/40 group-hover:border-teal" />

                  {/* Header */}
                  <div className="flex items-center justify-between border-b border-border-hairline/60 pb-3.5 mb-3.5">
                    <div className="flex items-center gap-2">
                      <span className="relative flex h-2 w-2">
                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-teal opacity-75"></span>
                        <span className="relative inline-flex rounded-full h-2 w-2 bg-teal"></span>
                      </span>
                      <span className="font-mono text-[10px] font-bold text-teal tracking-widest uppercase">LIVE FEED</span>
                    </div>
                    <span className="font-mono text-[8px] text-text-muted">NOAA-SWPC REPO</span>
                  </div>

                  {/* Body values with counts */}
                  <div className="space-y-3 font-mono text-[11px]">
                    <div className="flex justify-between items-center border-b border-border-hairline/20 pb-1.5">
                      <span className="text-text-muted">SOLAR WIND</span>
                      <div className="flex items-baseline gap-1">
                        <span className="text-text-primary font-bold">{telemetry.solarWind.toFixed(1)}</span>
                        <span className="text-[9px] text-text-muted">km/s</span>
                      </div>
                    </div>

                    <div className="flex justify-between items-center border-b border-border-hairline/20 pb-1.5">
                      <span className="text-text-muted">GEOMAGNETIC Kp</span>
                      <span className="text-teal font-bold">{telemetry.Kp.toFixed(1)}</span>
                    </div>

                    <div className="flex justify-between items-center border-b border-border-hairline/20 pb-1.5">
                      <span className="text-text-muted">PROTON FLUX</span>
                      <div className="flex items-baseline gap-1">
                        <span className="text-text-primary font-bold">{telemetry.protonFlux.toFixed(1)}</span>
                        <span className="text-[9px] text-text-muted">pfu</span>
                      </div>
                    </div>

                    <div className="flex justify-between items-center">
                      <span className="text-text-muted">ASSESSED RISK</span>
                      <span className={`px-2 py-0.2 rounded text-[10px] font-bold border ${
                        telemetry.risk === 'EXTREME' ? 'border-danger/30 text-danger bg-danger/10 animate-pulse' :
                        telemetry.risk === 'HIGH' ? 'border-orange-500/30 text-orange-500 bg-orange-500/10' :
                        telemetry.risk === 'MEDIUM' ? 'border-yellow-400/30 text-yellow-400 bg-yellow-400/10' :
                        'border-teal/30 text-teal bg-teal/10'
                      }`}>
                        {telemetry.risk}
                      </span>
                    </div>
                  </div>

                  {/* Live clock synced tag */}
                  <div className="flex items-center justify-between border-t border-border-hairline/60 pt-3 mt-3.5 font-mono text-[8px] text-text-muted">
                    <span className="flex items-center gap-1.5">
                      <RefreshCw className="w-2.5 h-2.5 animate-spin [animation-duration:10s]" />
                      Synced {syncedTime}
                    </span>
                    <span>ONLINE // ACTIVE</span>
                  </div>
                </motion.div>
              </div>

            </div>

            {/* Bottom Trusted Source Row */}
            <div className="border-t border-border-hairline/40 pt-8 mt-16">
              <span className="font-mono text-[9px] text-text-muted tracking-[0.25em] uppercase block mb-4">
                INTEGRATED SENSOR NETWORK SOURCES
              </span>
              <div className="flex flex-wrap items-center gap-8 md:gap-12">
                {[
                  { name: 'NOAA SWPC', sub: 'Primary Geomagnetic' },
                  { name: 'GOES-16', sub: 'High-energy Protons' },
                  { name: 'NASA DONKI', sub: 'Solar CME Feeds' },
                  { name: 'ACE/DSCOVR', sub: 'Real-time Solar Wind' }
                ].map((src, idx) => (
                  <div 
                    key={src.name}
                    className="group flex flex-col font-mono text-left transition-all duration-300 hover:translate-y-[-1px] select-none"
                  >
                    <span className="text-xs font-bold text-text-secondary group-hover:text-teal group-hover:drop-shadow-[0_0_6px_rgba(0,255,209,0.3)] transition-colors">
                      {src.name}
                    </span>
                    <span className="text-[8px] text-text-ghost uppercase tracking-wider group-hover:text-text-muted transition-colors mt-0.5">
                      {src.sub}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </section>

          {/* ── SEQUENCE 4: FEATURES GRID ── */}
          <section id="capabilities" className="py-24 px-6 lg:px-12 bg-bg-primary/20 border-b border-border-hairline relative scroll-mt-24">
            <div className="max-w-7xl mx-auto space-y-16">
              
              <div className="text-center max-w-3xl mx-auto space-y-4">
                <span className="font-sans text-xs text-teal tracking-widest font-bold block">System capabilities</span>
                <h2 className="font-space font-bold text-text-primary text-3xl md:text-5xl leading-tight">
                  Everything you need to <span className="text-teal">forecast risk</span>
                </h2>
                <p className="text-text-secondary text-sm md:text-base leading-relaxed max-w-lg mx-auto font-sans">
                  ASTRA provides a complete automated pipeline from raw satellite telemetry Ingestion to real-time operator alarms.
                </p>
              </div>

              {/* 4 Cards Grid Row */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                {[
                  {
                    icon: <Radio className="w-5 h-5 text-teal" />,
                    color: 'teal',
                    title: 'Data Ingestion',
                    desc: 'Real-time polling from NOAA SWPC, GOES-16, NASA DONKI and ACE/DSCOVR every 15 minutes.'
                  },
                  {
                    icon: <Code className="w-5 h-5 text-violet" />,
                    color: 'violet',
                    title: 'AI Forecasting',
                    desc: 'LSTM time-series models and XGBoost classifiers predict risk 1h, 3h, and 24h ahead.'
                  },
                  {
                    icon: <Shield className="w-5 h-5 text-teal" />,
                    color: 'teal',
                    title: 'Risk Classification',
                    desc: 'Automatic LOW to EXTREME tiering with confidence-scored predictions for every forecast.'
                  },
                  {
                    icon: <Bell className="w-5 h-5 text-violet" />,
                    color: 'violet',
                    title: 'Operator Alerts',
                    desc: 'Threshold-triggered alert engine pushes instant notifications via secure WebSockets.'
                  }
                ].map((card, idx) => (
                  <motion.div
                    key={card.title}
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true, margin: "-100px" }}
                    transition={{ duration: 0.5, delay: idx * 0.12 }}
                    className={`bg-bg-card border border-border-hairline hover:border-${card.color}/30 p-6 rounded relative group transition-all duration-300 hover:translate-y-[-4px] hover:shadow-[0_8px_30px_rgba(0,0,0,0.4)]`}
                  >
                    {/* Glowing highlight under card */}
                    <div className={`absolute bottom-0 left-0 right-0 h-[2px] bg-${card.color} opacity-0 group-hover:opacity-100 transition-opacity duration-300 rounded-b`} />

                    {/* Styled small icon box */}
                    <div className="h-10 w-10 rounded bg-[#090b13] border border-border-hairline flex items-center justify-center mb-6 group-hover:border-teal/30 group-hover:scale-105 transition-all">
                      {card.icon}
                    </div>

                    <h3 className="font-space font-bold text-sm text-text-primary tracking-wider uppercase mb-3 group-hover:text-text-primary transition-colors">
                      {card.title}
                    </h3>
                    <p className="text-xs text-text-secondary leading-relaxed font-sans">
                      {card.desc}
                    </p>
                  </motion.div>
                ))}
              </div>

            </div>
          </section>

          {/* ── SEQUENCE 5: SCROLL-DRIVEN TIMELINE (Vertical line draw) ── */}
          <section 
            id="architecture" 
            ref={setTimelineSection} 
            className="py-24 px-6 lg:px-12 max-w-7xl mx-auto relative z-10 border-b border-border-hairline/60 scroll-mt-24"
          >
            <div className="max-w-3xl mx-auto text-center mb-24 space-y-3">
              <span className="font-sans text-xs text-teal tracking-widest font-bold block">Sequence timeline</span>
              <h2 className="font-space font-bold text-text-primary text-3xl md:text-5xl leading-tight">
                From telemetry to <span className="text-teal">alert</span>
              </h2>
              <div className="w-12 h-[1px] bg-teal/50 mx-auto mt-4" />
            </div>

            {/* Timeline wrapper */}
            <div className="relative max-w-4xl mx-auto grid grid-cols-1 md:grid-cols-12 gap-12 mt-12 pb-16">
              
              {/* Vertical line running down the left side (desktop) or absolute center (for alternate grids) */}
              <div className="absolute left-4 md:left-1/2 md:-translate-x-1/2 top-4 bottom-4 w-[2px] bg-border-hairline/40 rounded-full overflow-hidden">
                {/* Scroll-animated fill line */}
                <motion.div 
                  className="w-full bg-gradient-to-b from-teal to-violet origin-top"
                  style={{ height: lineHeight }}
                />
              </div>

              {/* Step 1: Ingest */}
              <div className="md:col-span-12 grid grid-cols-1 md:grid-cols-12 items-center relative" ref={step1Ref}>
                {/* Circle Marker on the line */}
                <div className="absolute left-4 md:left-1/2 -translate-x-1/2 z-10">
                  <div className={`h-3 w-3 rounded-full border-2 transition-all duration-300 ${step1InView ? 'bg-teal border-teal shadow-[0_0_10px_rgba(0,255,209,1)] scale-125' : 'bg-bg-void border-border-hairline'}`} />
                </div>

                {/* Left content block (offset to left on desktop) */}
                <motion.div
                  initial={{ opacity: 0, x: -30 }}
                  animate={step1InView ? { opacity: 1, x: 0 } : { opacity: 0, x: -30 }}
                  transition={{ duration: 0.6 }}
                  className="pl-12 md:pl-0 md:col-span-5 text-left md:text-right pr-4"
                >
                  <span className="font-mono text-xs text-teal font-bold tracking-widest block mb-1">01 / Stream</span>
                  <h3 className="font-space font-bold text-lg text-text-primary uppercase mb-2">Ingest</h3>
                  <p className="text-xs text-text-secondary leading-relaxed font-sans max-w-sm md:ml-auto">
                    Raw space weather telemetry streamed from 4 independent sources into PostgreSQL in real-time.
                  </p>
                </motion.div>
                
                {/* Blank col for right */}
                <div className="hidden md:block md:col-span-7" />
              </div>

              {/* Step 2: Process */}
              <div className="md:col-span-12 grid grid-cols-1 md:grid-cols-12 items-center relative" ref={step2Ref}>
                {/* Circle Marker */}
                <div className="absolute left-4 md:left-1/2 -translate-x-1/2 z-10">
                  <div className={`h-3 w-3 rounded-full border-2 transition-all duration-300 ${step2InView ? 'bg-teal border-teal shadow-[0_0_10px_rgba(0,255,209,1)] scale-125' : 'bg-bg-void border-border-hairline'}`} />
                </div>

                {/* Blank col for left */}
                <div className="hidden md:block md:col-span-7" />

                {/* Right content block (offset to right on desktop) */}
                <motion.div
                  initial={{ opacity: 0, x: 30 }}
                  animate={step2InView ? { opacity: 1, x: 0 } : { opacity: 0, x: 30 }}
                  transition={{ duration: 0.6 }}
                  className="pl-12 md:pl-0 md:col-span-5 text-left pl-4"
                >
                  <span className="font-mono text-xs text-violet font-bold tracking-widest block mb-1">02 / Arrays</span>
                  <h3 className="font-space font-bold text-lg text-text-primary uppercase mb-2">Process</h3>
                  <p className="text-xs text-text-secondary leading-relaxed font-sans max-w-sm">
                    Feature engineering extracts lag windows, rolling stats, and solar activity scores to feed predictive neural grids.
                  </p>
                </motion.div>
              </div>

              {/* Step 3: Forecast */}
              <div className="md:col-span-12 grid grid-cols-1 md:grid-cols-12 items-center relative" ref={step3Ref}>
                {/* Circle Marker */}
                <div className="absolute left-4 md:left-1/2 -translate-x-1/2 z-10">
                  <div className={`h-3 w-3 rounded-full border-2 transition-all duration-300 ${step3InView ? 'bg-teal border-teal shadow-[0_0_10px_rgba(0,255,209,1)] scale-125' : 'bg-bg-void border-border-hairline'}`} />
                </div>

                {/* Left content block */}
                <motion.div
                  initial={{ opacity: 0, x: -30 }}
                  animate={step3InView ? { opacity: 1, x: 0 } : { opacity: 0, x: -30 }}
                  transition={{ duration: 0.6 }}
                  className="pl-12 md:pl-0 md:col-span-5 text-left md:text-right pr-4"
                >
                  <span className="font-mono text-xs text-teal font-bold tracking-widest block mb-1">03 / Intel</span>
                  <h3 className="font-space font-bold text-lg text-text-primary uppercase mb-2">Forecast</h3>
                  <p className="text-xs text-text-secondary leading-relaxed font-sans max-w-sm md:ml-auto">
                    LSTM and XGBoost models generate risk predictions across three time horizons with real-time accuracy scoring.
                  </p>
                </motion.div>
                
                <div className="hidden md:block md:col-span-7" />
              </div>

              {/* Step 4: Alert */}
              <div className="md:col-span-12 grid grid-cols-1 md:grid-cols-12 items-center relative" ref={step4Ref}>
                {/* Circle Marker */}
                <div className="absolute left-4 md:left-1/2 -translate-x-1/2 z-10">
                  <div className={`h-3 w-3 rounded-full border-2 transition-all duration-300 ${step4InView ? 'bg-teal border-teal shadow-[0_0_10px_rgba(0,255,209,1)] scale-125' : 'bg-bg-void border-border-hairline'}`} />
                </div>

                <div className="hidden md:block md:col-span-7" />

                {/* Right content block */}
                <motion.div
                  initial={{ opacity: 0, x: 30 }}
                  animate={step4InView ? { opacity: 1, x: 0 } : { opacity: 0, x: 30 }}
                  transition={{ duration: 0.6 }}
                  className="pl-12 md:pl-0 md:col-span-5 text-left pl-4"
                >
                  <span className="font-mono text-xs text-violet font-bold tracking-widest block mb-1">04 / Dispatch</span>
                  <h3 className="font-space font-bold text-lg text-text-primary uppercase mb-2">Alert</h3>
                  <p className="text-xs text-text-secondary leading-relaxed font-sans max-w-sm">
                    Threshold engine evaluates risks every 5 minutes and pushes instant notifications to on-duty ISRO operators.
                  </p>
                </motion.div>
              </div>

            </div>
          </section>

          {/* ── SEQUENCE 6: 3D VISUALIZATION SECTION (Full-bleed with wireframe grids) ── */}
          <section id="visualization" className="w-full min-h-[500px] md:min-h-[600px] relative bg-bg-void flex items-center justify-center overflow-hidden border-b border-border-hairline/60">
            
            {/* Raw Three.js WebGL canvas background */}
            <InsideAstraCanvas />

            {/* Overlapping Glass Card */}
            <div className="max-w-2xl px-6 relative z-10 text-center">
              <motion.div
                initial={{ opacity: 0, scale: 0.96 }}
                whileInView={{ opacity: 1, scale: 1 }}
                viewport={{ once: true }}
                transition={{ duration: 0.6 }}
                className="bg-bg-card/70 backdrop-blur-lg border border-border-hairline hover:border-teal/20 p-8 sm:p-12 rounded-lg shadow-[0_12px_40px_rgba(0,0,0,0.6)] space-y-5"
              >
                <div className="inline-flex items-center gap-2 border border-violet/30 bg-violet/5 px-2.5 py-1 rounded-full">
                  <span className="h-1.5 w-1.5 rounded-full bg-violet animate-pulse" />
                  <span className="font-mono text-[9px] uppercase tracking-widest text-violet font-bold">Forecasting Core</span>
                </div>
                
                <h2 className="font-space font-bold text-text-primary text-3xl sm:text-5xl leading-tight uppercase">
                  Inside ASTRA
                </h2>
                <p className="text-text-secondary text-sm md:text-base leading-relaxed max-w-md mx-auto font-sans">
                  Experience the radiation forecasting engine. Visualized in real-time. Continuous pipelines processing solar wind coordinates, proton density, and IMF components.
                </p>

                {/* Live Stat readout below */}
                <div className="border-t border-border-hairline/60 pt-6 mt-6">
                  <span className="font-mono text-[10px] text-teal font-bold tracking-[0.2em] uppercase">
                    PROCESSING 1,247 DATA POINTS/HOUR
                  </span>
                </div>
              </motion.div>
            </div>
          </section>

          {/* ── SEQUENCE 7: LIVE DASHBOARD PREVIEW ── */}
          <section id="dashboard-preview" className="py-24 px-6 lg:px-12 max-w-7xl mx-auto z-10 relative">
            <div className="text-center mb-16 space-y-3">
              <span className="font-sans text-xs text-teal tracking-widest font-bold block">Interaction playground</span>
              <h2 className="font-space font-bold text-text-primary text-3xl md:text-5xl leading-tight">
                See it in <span className="text-teal">action</span>
              </h2>
              <p className="text-text-secondary text-xs sm:text-sm max-w-lg mx-auto font-sans">
                Below is a miniature functional representation of our main telemetry forecasting board. High-precision datasets fed dynamically.
              </p>
            </div>

            {/* Browser Chrome Frame */}
            <motion.div 
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-100px" }}
              transition={{ duration: 0.7 }}
              className="border border-border-strong bg-bg-void rounded-lg shadow-2xl overflow-hidden"
            >
              {/* Browser Header Bar */}
              <div className="bg-bg-card border-b border-border-hairline px-4 py-3.5 flex items-center justify-between font-mono text-xs text-text-muted select-none">
                <div className="flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-[#FF5F56]" />
                  <span className="w-2.5 h-2.5 rounded-full bg-[#FFBD2E]" />
                  <span className="w-2.5 h-2.5 rounded-full bg-[#27C93F]" />
                  <span className="ml-2 font-mono text-[9px] text-text-muted uppercase tracking-widest hidden sm:inline">ASTRA_OPERATOR_FRAME</span>
                </div>
                <div className="bg-bg-void border border-border-hairline px-6 py-1 rounded text-[9px] text-teal truncate max-w-[180px] sm:max-w-[320px]">
                  https://astra.isro.gov.in/dashboard
                </div>
                <div className="flex items-center gap-1.5">
                  <span className="h-1.5 w-1.5 rounded-full bg-teal animate-pulse" />
                  <span className="text-[9px] text-teal">CONNECTED</span>
                </div>
              </div>

              {/* Mini App Content (4 small stat cards + Recharts area curve) */}
              <div className="bg-bg-primary/95 p-6 space-y-6">
                
                {/* Cards row */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  
                  {/* Card 1 */}
                  <div className="bg-bg-card border border-border-hairline p-4 rounded flex flex-col justify-between">
                    <span className="font-mono text-[9px] text-text-muted tracking-wider uppercase">Risk Assess</span>
                    <span className={`text-base font-space font-bold mt-2 border-l border-teal pl-2 ${
                      telemetry.risk === 'EXTREME' ? 'text-danger' : telemetry.risk === 'HIGH' ? 'text-orange-500' : 'text-teal'
                    }`}>
                      {telemetry.risk}
                    </span>
                    <span className="font-mono text-[8px] text-text-ghost mt-3 uppercase">ACTIVE COHORT</span>
                  </div>

                  {/* Card 2 */}
                  <div className="bg-bg-card border border-border-hairline p-4 rounded flex flex-col justify-between">
                    <span className="font-mono text-[9px] text-text-muted tracking-wider uppercase">Geomagnetic Kp</span>
                    <span className="text-base font-mono font-bold text-teal mt-2">
                      {telemetry.Kp.toFixed(1)} <span className="text-[9px] text-text-muted font-normal">/ 9.0</span>
                    </span>
                    <div className="w-full bg-bg-void h-1 rounded overflow-hidden relative mt-3 border border-border-hairline/40">
                      <div className="bg-teal h-full rounded" style={{ width: `${(telemetry.Kp / 9.0) * 100}%` }} />
                    </div>
                  </div>

                  {/* Card 3 */}
                  <div className="bg-bg-card border border-border-hairline p-4 rounded flex flex-col justify-between">
                    <span className="font-mono text-[9px] text-text-muted tracking-wider uppercase">Proton Flux</span>
                    <span className="text-base font-mono font-bold text-text-primary mt-2">
                      {telemetry.protonFlux.toFixed(0)} <span className="text-[9px] text-text-muted font-normal">pfu</span>
                    </span>
                    <span className="font-mono text-[8px] text-teal flex items-center gap-0.5 mt-3">
                      <TrendingUp className="w-2.5 h-2.5" /> STABLE
                    </span>
                  </div>

                  {/* Card 4 */}
                  <div className="bg-bg-card border border-border-hairline p-4 rounded flex flex-col justify-between">
                    <span className="font-mono text-[9px] text-text-muted tracking-wider uppercase">Threat Alerts</span>
                    <span className={`text-base font-space font-bold mt-2 ${activeAlerts.length > 0 ? 'text-danger animate-pulse' : 'text-teal'}`}>
                      {activeAlerts.length > 0 ? `${activeAlerts.length} FLAGGED` : 'ALL NORMAL'}
                    </span>
                    <span className="font-mono text-[8px] text-text-ghost mt-3 uppercase">REAL-TIME GUARD</span>
                  </div>

                </div>

                {/* Area Chart block */}
                <div className="bg-bg-card border border-border-hairline p-4 rounded">
                  <div className="flex items-center justify-between border-b border-border-hairline/60 pb-3 mb-4 font-mono text-[10px] text-text-secondary">
                    <span>GEOMAGNETIC RADIATION TRENDS — PAST 24H</span>
                    <span className="text-[8px] text-text-muted hidden sm:inline">UNITS: GEOMAGNETIC K-INDEX CURVE</span>
                  </div>

                  <div className="h-44 sm:h-56 w-full font-mono text-xs">
                    <ResponsiveContainer width="100%" height="100%">
                      <AreaChart data={mockChartData} margin={{ top: 10, right: 5, left: -25, bottom: 0 }}>
                        <defs>
                          <linearGradient id="miniKpGradient" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="#00ffd1" stopOpacity={0.25}/>
                            <stop offset="95%" stopColor="#00ffd1" stopOpacity={0.0}/>
                          </linearGradient>
                        </defs>
                        <XAxis 
                          dataKey="timestamp" 
                          stroke="#2e3650" 
                          tickFormatter={formatXAxis} 
                          tickLine={false}
                          style={{ fontSize: 9 }}
                        />
                        <YAxis 
                          stroke="#2e3650" 
                          domain={[0, 9]} 
                          tickLine={false}
                          style={{ fontSize: 9 }}
                        />
                        <Tooltip contentStyle={{ backgroundColor: '#10141f', borderColor: '#1e2740', fontSize: 10 }} />
                        <Area 
                          type="monotone" 
                          dataKey="Kp" 
                          stroke="#00ffd1" 
                          strokeWidth={2} 
                          fillOpacity={1} 
                          fill="url(#miniKpGradient)" 
                        />
                      </AreaChart>
                    </ResponsiveContainer>
                  </div>
                </div>

              </div>

              {/* Browser Preview Bottom CTA bar */}
              <div className="bg-bg-card border-t border-border-hairline p-4 flex flex-col sm:flex-row items-center justify-between gap-4 font-mono">
                <span className="text-[10px] text-text-muted text-center sm:text-left leading-normal max-w-xl">
                  Pipeline active / Direct streaming link synchronized with local development database pipelines on port 3000.
                </span>
                <button
                  id="preview_full_dashboard_cta"
                  onClick={() => navigate('/login')}
                  className="bg-teal text-bg-void hover:bg-teal-dim px-5 py-2.5 rounded font-space font-bold text-xs uppercase tracking-wider cursor-pointer flex items-center gap-1.5 hover:shadow-[0_0_15px_rgba(0,255,209,0.3)] transition-all whitespace-nowrap"
                >
                  Open full dashboard
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
              </div>
            </motion.div>
          </section>

          {/* ── SEQUENCE 8: TEAM / HACKATHON CONTEXT ── */}
          <section id="team" className="py-24 bg-bg-void border-t border-border-hairline px-6 lg:px-12 relative scroll-mt-24">
            <div className="max-w-7xl mx-auto text-center space-y-12">
              
              <div className="space-y-4 max-w-2xl mx-auto">
                <span className="font-sans text-xs text-teal tracking-widest font-bold block">Team credentials</span>
                <h2 className="font-space font-bold text-text-primary text-3xl md:text-5xl leading-tight">
                  ISRO Bharatiya Antariksh Hackathon 2026
                </h2>
                <p className="text-text-secondary text-xs sm:text-sm max-w-md mx-auto leading-relaxed">
                  Developed in 8 days to satisfy strict orbital radiation risk forecast standards. Optimized machine learning pipelines backed by a highly secure operators terminal.
                </p>
              </div>

              {/* Staggered role pills */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 max-w-3xl mx-auto">
                {[
                  { id: 'M1', role: 'AI/ML PIPELINES', name: 'MANTHAN BALANI', task: 'M1 · LSTM MODEL' },
                  { id: 'M2', role: 'DATA INGESTION', name: 'DEVASHYA JETHVA', task: 'M2 · DATA REPO' },
                  { id: 'M3', role: 'BACKEND SERVICES', name: 'NEIL BANERJEE', task: 'M3 · API ROUTERS' },
                  { id: 'M4', role: 'OPERATOR WEB APP', name: 'RAJVARDHAN SINGH CHAUHAN', task: 'M4 · CLIENT PANEL' }
                ].map((member, index) => (
                  <motion.div
                    key={member.id}
                    initial={{ opacity: 0, scale: 0.95 }}
                    whileInView={{ opacity: 1, scale: 1 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.4, delay: index * 0.1 }}
                    className="border border-border-hairline bg-bg-card/40 p-5 rounded text-center relative group hover:border-teal/20 transition-all duration-300 flex flex-col justify-between min-h-[160px]"
                  >
                    <div>
                      <div className="font-space font-bold text-teal text-lg mb-1">{member.id}</div>
                      <div className="font-space font-bold text-text-primary text-[10px] tracking-wider uppercase mb-1 leading-snug">{member.name}</div>
                      <div className="font-mono text-[8px] text-text-muted uppercase tracking-wider">{member.role}</div>
                    </div>
                    <div className="mt-3">
                      <div className="font-mono text-[8px] border border-border-hairline bg-bg-void px-2 py-0.5 rounded text-text-ghost inline-block">
                        {member.task}
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>

              {/* Smaller Tech Ticker Marquee */}
              <div className="border border-border-hairline bg-bg-card/40 py-4 max-w-4xl mx-auto rounded flex overflow-hidden justify-center relative">
                <div className="ticker-wrap flex select-none">
                  <div className="ticker-content flex gap-12 font-mono text-[9px] text-text-secondary uppercase tracking-[0.2em] font-medium [animation-duration:18s]">
                    <span>PYTHON</span>
                    <span>FASTAPI</span>
                    <span>POSTGRESQL</span>
                    <span>REDIS</span>
                    <span>DOCKER</span>
                    <span>PYTORCH</span>
                    <span>XGBOOST</span>
                    <span>REACT 19</span>
                    <span>TYPESCRIPT</span>
                    <span>RECHARTS</span>
                    <span>FRAMER MOTION</span>

                    {/* Loop duplication */}
                    <span>PYTHON</span>
                    <span>FASTAPI</span>
                    <span>POSTGRESQL</span>
                    <span>REDIS</span>
                    <span>DOCKER</span>
                    <span>PYTORCH</span>
                    <span>XGBOOST</span>
                    <span>REACT 19</span>
                    <span>TYPESCRIPT</span>
                    <span>RECHARTS</span>
                    <span>FRAMER MOTION</span>
                  </div>
                </div>
              </div>

            </div>
          </section>

          {/* ── FOOTER ── */}
          <Footer
            postgresqlHealthy={health?.postgresql === 'healthy'}
            redisHealthy={health?.redis === 'healthy'}
            apiHealthy={health?.api === 'healthy'}
          />

        </div>

    </div>
  );
}




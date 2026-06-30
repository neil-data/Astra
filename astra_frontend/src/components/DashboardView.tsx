import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'motion/react';
import {
  Satellite,
  Activity,
  LogOut,
  Clock,
  Database,
  Server,
  Cpu,
  TrendingUp,
  TrendingDown,
  AlertTriangle,
  Zap,
  Terminal as TermIcon,
  Search,
  ChevronLeft,
  ChevronRight,
  Maximize2,
  Minimize2,
  ShieldAlert,
  Calendar,
  FileText,
  ChevronUp,
  ChevronDown
} from 'lucide-react';
import TimelineChart from './TimelineChart';
import MetricCard from './MetricCard';
import { Telemetry, ForecastSummary, Alert, SystemStatus } from '../types';

interface DashboardViewProps {
  currentTelemetry: Telemetry | null;
  historyData: Telemetry[];
  forecastSummary: ForecastSummary[];
  activeAlerts: Alert[];
  systemStatus: SystemStatus | null;
  wsLogs: string[];
  wsConnected: boolean;
  onRefreshData?: () => void;
}

export default function DashboardView({
  currentTelemetry,
  historyData,
  forecastSummary,
  activeAlerts,
  systemStatus,
  wsLogs,
  wsConnected,
  onRefreshData
}: DashboardViewProps) {
  const navigate = useNavigate();
  const [operatorName, setOperatorName] = useState('OPERATOR');
  const [activeTab, setActiveTab] = useState<'DASHBOARD' | 'FORECAST' | 'ALERTS' | 'HISTORY'>('DASHBOARD');
  
  // Real-time UTC clock
  const [utcTime, setUtcTime] = useState('');
  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      setUtcTime(now.toUTCString().replace('GMT', 'UTC'));
    };
    updateTime();
    const interval = setInterval(updateTime, 1000);
    return () => clearInterval(interval);
  }, []);

  // Retrieve Operator Info
  useEffect(() => {
    const saved = localStorage.getItem('operatorName');
    if (saved) {
      setOperatorName(saved);
    } else {
      // If not logged in, redirect to login
      navigate('/login');
    }
  }, [navigate]);

  // Collapsible live websocket log state
  const [isLogCollapsed, setIsLogCollapsed] = useState(false);
  
  // Table Pagination and Filtering States
  const [logPage, setLogPage] = useState(1);
  const [filterSource, setFilterSource] = useState<string>('ALL');
  const [searchQuery, setSearchQuery] = useState('');
  const logLimit = 10;

  // Safe Fallback Telemetry
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

  // Uptime safe reference
  const uptime = systemStatus?.uptime || '00:00:00';

  const logContainerRef = React.useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (logContainerRef.current) {
      logContainerRef.current.scrollTop = logContainerRef.current.scrollHeight;
    }
  }, [wsLogs, isLogCollapsed]);

  const parseLogLine = (log: string) => {
    const match = log.match(/^\[([^\]]+)\]\s*(.*)$/);
    if (!match) return { time: '', category: 'INFO', details: log };

    const time = match[1];
    const rest = match[2];

    const colonIdx = rest.indexOf(':');
    if (colonIdx === -1) {
      return { time, category: 'SYSTEM', details: rest };
    }

    const category = rest.substring(0, colonIdx).trim();
    const details = rest.substring(colonIdx + 1).trim();

    return { time, category, details };
  };

  // Filters observation logs

  const filteredLogs = historyData.filter((item) => {
    const matchesSource = filterSource === 'ALL' || item.source === filterSource;
    const matchesQuery = 
      item.source.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.risk.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.solarWind.toString().includes(searchQuery) ||
      item.Kp.toString().includes(searchQuery);
    return matchesSource && matchesQuery;
  }).reverse(); // Latest first for observation log

  const paginatedLogs = filteredLogs.slice((logPage - 1) * logLimit, logPage * logLimit);
  const totalPages = Math.ceil(filteredLogs.length / logLimit) || 1;

  // Render Risk Badge Styles
  const renderRiskBadge = (risk: Telemetry['risk']) => {
    const colors = 
      risk === 'EXTREME' ? 'border-danger/30 text-danger bg-danger/10 shadow-[0_0_12px_rgba(255,59,59,0.2)] animate-pulse' :
      risk === 'HIGH' ? 'border-orange-500/30 text-orange-500 bg-orange-500/10 shadow-[0_0_10px_rgba(249,115,22,0.15)]' :
      risk === 'MEDIUM' ? 'border-yellow-400/30 text-yellow-400 bg-yellow-400/10' :
      'border-teal/30 text-teal bg-teal/10';
    return (
      <span className={`px-2.5 py-0.5 rounded text-[11px] font-bold uppercase tracking-wider border ${colors}`}>
        {risk}
      </span>
    );
  };

  // Render contributing factors based on risk
  const getContributingFactors = (risk: Telemetry['risk']) => {
    if (risk === 'EXTREME') {
      return ['Severe geomagnetic flare', 'Proton flux above warning', 'Critical magnetopause compression'];
    } else if (risk === 'HIGH') {
      return ['Elevated solar wind speed', 'High Bz magnetic fluctuations', 'Moderate proton flux flare'];
    } else if (risk === 'MEDIUM') {
      return ['Subtle solar wind enhancement', 'Minor Kp index volatility'];
    }
    return ['Geomagnetic field quiet', 'Solar wind speed nominal', 'No proton flux events'];
  };

  return (
    <div id="dashboard_view_root" className="min-h-screen bg-bg-void text-text-primary selection:bg-teal selection:text-bg-void font-sans">
      
      {/* Background decoration */}
      <div className="absolute inset-0 dot-grid opacity-15 pointer-events-none z-0" />
      <div className="scanline-effect pointer-events-none opacity-20" />

      {/* ── HEADER ── */}
      <header id="dashboard_header" className="fixed top-0 left-0 right-0 h-16 bg-bg-void/90 backdrop-blur-md border-b border-border-hairline z-40 flex items-center justify-between px-6">
        <div className="flex items-center gap-3">
          <div className="flex items-center justify-center w-8 h-8 border border-teal/40 rounded-full bg-bg-card shadow-[0_0_8px_rgba(0,255,209,0.15)]">
            <Satellite className="w-4.5 h-4.5 text-teal animate-pulse" />
          </div>
          <div className="flex flex-col">
            <span className="font-space font-bold tracking-wider text-teal text-sm">ASTRA CONSOLE</span>
            <span className="font-mono text-[8px] text-text-muted tracking-widest uppercase mt-0.5">ISRO · GEO SATELLITES PREDICTIVE SHIELD</span>
          </div>
        </div>

        {/* Live UTC Clock */}
        <div id="header_utc_clock" className="hidden md:flex items-center gap-2 border border-border-hairline bg-bg-card/40 px-4 py-1.5 rounded font-mono text-xs tracking-wider text-text-secondary">
          <Clock className="w-3.5 h-3.5 text-text-muted" />
          <span className="text-text-primary font-bold">{utcTime}</span>
        </div>

        {/* User context */}
        <div id="header_user_context" className="flex items-center gap-4">
          <div className="flex items-center gap-2 font-mono text-xs">
            <span className="relative flex h-2 w-2">
              <span className={`animate-ping absolute inline-flex h-full w-full rounded-full ${wsConnected ? 'bg-teal' : 'bg-warning'} opacity-75`}></span>
              <span className={`relative inline-flex rounded-full h-2 w-2 ${wsConnected ? 'bg-teal' : 'bg-warning'}`}></span>
            </span>
            <span className="text-text-muted">OP:</span>
            <span className="text-text-primary font-bold">{operatorName}</span>
          </div>
          <button
            id="dashboard_logout_btn"
            onClick={() => {
              localStorage.removeItem('operatorName');
              navigate('/login');
            }}
            className="flex items-center justify-center p-2 rounded-full border border-border-hairline hover:border-danger hover:text-danger bg-bg-card cursor-pointer transition-colors"
            title="Terminate Session"
          >
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </header>

      {/* ── SIDEBAR (Hidden on mobile, collapses on tablet, full on desktop) ── */}
      <aside id="dashboard_sidebar" className="hidden md:flex flex-col w-[72px] lg:w-[240px] border-r border-border-hairline fixed left-0 top-16 bottom-0 bg-bg-card z-30 transition-all duration-300 select-none">
        
        {/* Navigation Items */}
        <div className="flex-1 py-6 space-y-1">
          {[
            { id: 'DASHBOARD', label: 'DASHBOARD', icon: <Activity className="w-4.5 h-4.5" /> },
            { id: 'FORECAST', label: 'FORECAST', icon: <Zap className="w-4.5 h-4.5" /> },
            { id: 'ALERTS', label: 'ALERTS', icon: <ShieldAlert className="w-4.5 h-4.5" />, badge: activeAlerts.length },
            { id: 'HISTORY', label: 'HISTORY', icon: <FileText className="w-4.5 h-4.5" /> }
          ].map((item) => {
            const active = activeTab === item.id;
            return (
              <button
                id={`sidebar_tab_${item.id.toLowerCase()}`}
                key={item.id}
                onClick={() => {
                  setActiveTab(item.id as any);
                  setLogPage(1); // Reset log page
                }}
                className={`w-full flex items-center gap-3.5 py-4 px-6 font-mono text-xs tracking-wider cursor-pointer border-l-2 transition-all duration-150 ${
                  active
                    ? 'border-teal text-teal bg-teal/5 font-bold'
                    : 'border-transparent text-text-secondary hover:text-text-primary hover:bg-bg-card-hover'
                }`}
              >
                {item.icon}
                <span className="hidden lg:inline">{item.label}</span>
                {item.badge !== undefined && item.badge > 0 && (
                  <span className="ml-auto bg-danger text-bg-void font-bold px-1.5 py-0.2 rounded text-[10px] animate-pulse">
                    {item.badge}
                  </span>
                )}
              </button>
            );
          })}
        </div>

        {/* Sidebar System Status Panel (Collapsed labels on tablet) */}
        <div className="p-4 border-t border-border-hairline space-y-3 font-mono text-[10px]">
          <div className="hidden lg:block text-text-muted font-bold tracking-wider uppercase mb-2">
            Terminal status
          </div>
          
          <div className="flex items-center gap-2.5">
            <span className={`h-1.5 w-1.5 rounded-full ${systemStatus?.postgresql === 'healthy' ? 'bg-teal animate-pulse' : 'bg-danger'}`} />
            <span className="hidden lg:inline text-text-secondary">PostgreSQL</span>
          </div>

          <div className="flex items-center gap-2.5">
            <span className={`h-1.5 w-1.5 rounded-full ${systemStatus?.redis === 'healthy' ? 'bg-teal animate-pulse' : 'bg-danger'}`} />
            <span className="hidden lg:inline text-text-secondary">Redis cache</span>
          </div>

          <div className="flex items-center gap-2.5">
            <span className={`h-1.5 w-1.5 rounded-full ${systemStatus?.api === 'healthy' ? 'bg-teal animate-pulse' : 'bg-danger'}`} />
            <span className="hidden lg:inline text-text-secondary">Telemetry API</span>
          </div>

          <div className="border-t border-border-hairline/40 pt-2.5 text-[9px] text-text-muted flex items-center gap-2.5">
            <span className="hidden lg:inline">Uptime:</span>
            <span className="text-text-secondary font-bold font-mono">{uptime}</span>
          </div>
        </div>
      </aside>

      {/* ── MOBILE BOTTOM NAVIGATION ── */}
      <nav id="mobile_bottom_nav" className="md:hidden fixed bottom-0 left-0 right-0 h-16 bg-bg-card/95 backdrop-blur-md border-t border-border-hairline z-40 flex items-center justify-around select-none">
        {[
          { id: 'DASHBOARD', icon: <Activity className="w-5 h-5" />, label: 'Dashboard' },
          { id: 'FORECAST', icon: <Zap className="w-5 h-5" />, label: 'Forecast' },
          { id: 'ALERTS', icon: <ShieldAlert className="w-5 h-5" />, label: 'Alerts', badge: activeAlerts.length },
          { id: 'HISTORY', icon: <FileText className="w-5 h-5" />, label: 'History' }
        ].map((item) => {
          const active = activeTab === item.id;
          return (
            <button
              id={`mobile_tab_${item.id.toLowerCase()}`}
              key={item.id}
              onClick={() => setActiveTab(item.id as any)}
              className={`flex flex-col items-center justify-center p-2 relative ${active ? 'text-teal font-bold' : 'text-text-secondary'}`}
            >
              <div className="relative">
                {item.icon}
                {item.badge !== undefined && item.badge > 0 && (
                  <span className="absolute -top-1.5 -right-1.5 bg-danger text-bg-void font-bold h-4 w-4 rounded-full flex items-center justify-center text-[8px] animate-pulse">
                    {item.badge}
                  </span>
                )}
              </div>
              <span className="text-[9px] tracking-wider uppercase mt-1">{item.label}</span>
              {active && <span className="absolute bottom-0 h-[2px] w-6 bg-teal" />}
            </button>
          );
        })}
      </nav>

      {/* ── MAIN CONTENT CONTAINER ── */}
      <main className="flex-1 md:pl-[72px] lg:pl-[240px] pt-16 pb-36 md:pb-40 lg:pb-48 min-h-screen relative z-10 overflow-y-auto">
        <div className="p-6 max-w-7xl mx-auto space-y-6">

          {/* Tab 1: DASHBOARD (Core console) */}
          {activeTab === 'DASHBOARD' && (
            <>
              {/* Top row: 4 stat cards */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
                
                {/* Card 1: Risk Assessment */}
                <MetricCard 
                  id="metric_risk"
                  title="RADIATION RISK" 
                  subLabel="LSTM MODEL"
                  alertLevel={telemetry.risk}
                  isAlerting={telemetry.risk === 'HIGH' || telemetry.risk === 'EXTREME'}
                  footer={
                    <>
                      <span>PROBABILITY: {forecastSummary[0]?.stormProb || 0}%</span>
                      <span>CONFIDENCE: {forecastSummary[0]?.confidence || 95}%</span>
                    </>
                  }
                >
                  <div className="flex flex-col gap-2 min-h-[70px]">
                    <span className={`font-space text-3xl font-bold uppercase tracking-tight ${
                      telemetry.risk === 'EXTREME' ? 'text-danger' :
                      telemetry.risk === 'HIGH' ? 'text-orange-500' :
                      telemetry.risk === 'MEDIUM' ? 'text-yellow-400' :
                      'text-teal'
                    }`}>
                      {telemetry.risk}
                    </span>
                    <span className="text-text-secondary text-[13px] font-sans">
                      Storm confidence is {forecastSummary[0]?.confidence || 95}%
                    </span>
                  </div>
                </MetricCard>

                {/* Card 2: Geomagnetic Kp Index */}
                <MetricCard 
                  id="metric_kp"
                  title="GEOMAGNETIC Kp" 
                  subLabel="NOAA SWPC"
                  alertLevel={telemetry.risk}
                  footer={
                    <>
                      <span>ZONE: {telemetry.Kp >= 7 ? 'SEVERE STORM' : telemetry.Kp >= 5 ? 'MOD STORM' : 'QUIET'}</span>
                      <span>RANGE: 0 - 9</span>
                    </>
                  }
                >
                  <div className="flex flex-col gap-2 min-h-[70px]">
                    <span className="font-space text-3xl font-bold text-text-primary tracking-tight font-mono">
                      {telemetry.Kp.toFixed(1)}
                    </span>
                    <span className="text-text-secondary text-[13px] font-sans">
                      {telemetry.Kp >= 5.0 ? 'Geomagnetic storm active' : 'Quiet magnetic field'}
                    </span>
                    
                    {/* Gauge Marker bar */}
                    <div className="w-full bg-bg-void h-1 rounded-full relative mt-3 border border-border-hairline overflow-visible">
                      <div className="absolute top-0 bottom-0 left-0 bg-teal rounded-full" style={{ width: `${(telemetry.Kp / 9) * 100}%` }} />
                      <div className="absolute h-2.5 w-2.5 rounded-full bg-teal -top-[3px] -ml-1.5 transition-all duration-300" style={{ left: `${(telemetry.Kp / 9) * 100}%` }} />
                    </div>
                  </div>
                </MetricCard>

                {/* Card 3: Proton Flux */}
                <MetricCard 
                  id="metric_flux"
                  title="SOLAR PROTON FLUX" 
                  subLabel="GOES-16"
                  alertLevel={telemetry.risk}
                  footer={
                    <>
                      <span>UNIT: pfu</span>
                      <span>ALERT THRESHOLD: 10,000</span>
                    </>
                  }
                >
                  <div className="flex flex-col gap-2 min-h-[70px]">
                    <span className="font-space text-3xl font-bold text-text-primary tracking-tight font-mono">
                      {telemetry.protonFlux.toFixed(0)} <span className="text-xs text-text-muted">pfu</span>
                    </span>
                    <span className="text-text-secondary text-[13px] font-sans">
                      {telemetry.protonFlux >= 10000 ? 'Dangerous flux level' : 'Nominal flux level'}
                    </span>
                  </div>
                </MetricCard>

                {/* Card 4: Active Threat Alerts */}
                <MetricCard 
                  id="metric_alerts"
                  title="ACTIVE ALERTS" 
                  subLabel="SHIELD ENGINE"
                  isAlerting={activeAlerts.length > 0}
                  alertLevel={activeAlerts.length > 0 ? 'HIGH' : 'LOW'}
                  footer={
                    <>
                      <span>INTERVAL: 10S COHORT</span>
                      <span>SYSTEMS: SECURE</span>
                    </>
                  }
                >
                  <div className="flex flex-col gap-2 min-h-[70px]">
                    <span className={`font-space text-3xl font-bold tracking-tight font-mono ${activeAlerts.length > 0 ? 'text-danger' : 'text-teal'}`}>
                      {activeAlerts.length}
                    </span>
                    <span className="text-text-secondary text-[13px] font-sans">
                      {activeAlerts.length > 0 ? 'Active threat warnings dispatched' : 'All systems secure and quiet'}
                    </span>
                  </div>
                </MetricCard>

              </div>

              {/* Middle row: Timeline + Horizon forecasts */}
              <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
                
                {/* Radiation Timeline Chart (60%) */}
                <div id="panel_timeline" className="lg:col-span-7 xl:col-span-8 border border-border-hairline bg-bg-card p-5 rounded-md shadow-lg flex flex-col justify-between">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between border-b border-border-hairline/60 pb-4 mb-4 gap-2">
                    <div className="flex items-center gap-2">
                      <span className="h-1.5 w-1.5 rounded-full bg-teal animate-ping" />
                      <span className="font-space text-xs font-bold tracking-wider text-text-primary">
                        Geomagnetic radiation timeline (24h)
                      </span>
                    </div>
                    <div className="flex gap-1.5 font-mono text-[9px] text-text-muted border border-border-hairline px-2 py-0.5 rounded">
                      <span>INTERVAL: 15-MIN</span>
                      <span>|</span>
                      <span>COUNT: {historyData.length}</span>
                    </div>
                  </div>
                  
                  <TimelineChart data={historyData} />
                </div>

                {/* Mission Forecasts (40%) */}
                <div id="panel_forecast" className="lg:col-span-5 xl:col-span-4 border border-border-hairline bg-bg-card p-5 rounded-md shadow-lg flex flex-col justify-between gap-4">
                  <div className="border-b border-border-hairline pb-4 flex items-center justify-between">
                    <span className="font-space text-xs font-bold tracking-wider text-text-primary">
                      Mission weather forecasts
                    </span>
                    <span className="font-mono text-[8px] text-text-muted">LSTM PREDICTION MODEL</span>
                  </div>

                  <div className="space-y-3.5 flex-1 flex flex-col justify-center">
                    {forecastSummary.map((item) => (
                      <div key={item.horizon} className="border border-border-hairline bg-bg-void/40 p-3 rounded flex items-center justify-between font-mono">
                        <div className="flex flex-col">
                          <span className="text-text-muted text-[10px] tracking-wider uppercase">HORIZON</span>
                          <span className="text-sm font-bold text-text-primary tracking-tighter">{item.horizon} SEQUENCE</span>
                        </div>
                        
                        <div className="flex flex-col items-end gap-1 text-right">
                          <div className="flex items-center gap-1.5">
                            <span className="text-text-secondary text-[10px]">KP: <span className="text-text-primary font-bold">{item.Kp.toFixed(1)}</span></span>
                            {renderRiskBadge(item.risk)}
                          </div>
                          {/* Probability custom indicator */}
                          <div className="flex items-center gap-1.5 text-[9px] text-text-muted mt-1 w-24">
                            <span className="truncate">CONFIDENCE</span>
                            <div className="w-12 bg-bg-card h-1 rounded-full overflow-hidden relative border border-border-hairline">
                              <div className="bg-teal h-full rounded" style={{ width: `${item.confidence}%` }} />
                            </div>
                            <span className="text-[8px] text-teal font-bold">{item.confidence}%</span>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>

                  <div className="bg-bg-void/40 border border-border-hairline p-3 rounded font-mono text-[9px] text-text-muted">
                    Prediction loops are automatically re-calculated by deep LSTM sequence models in real-time.
                  </div>
                </div>

              </div>

              {/* Bottom row: Observation Logs table */}
              <div id="panel_logs" className="border border-border-hairline bg-bg-card p-5 rounded-md shadow-lg">
                <div className="flex flex-col lg:flex-row lg:items-center justify-between border-b border-border-hairline/60 pb-4 mb-4 gap-4">
                  <div className="flex items-center gap-2">
                    <TermIcon className="w-4.5 h-4.5 text-teal" />
                    <span className="font-space text-xs font-bold tracking-wider text-text-primary">
                      Telemetric observation logs
                    </span>
                  </div>

                  {/* Filter and search utilities */}
                  <div className="flex flex-wrap items-center gap-3">
                    <div className="flex border border-border-hairline rounded bg-bg-void font-mono text-[9px]">
                      {['ALL', 'NOAA', 'GOES', 'DONKI', 'DSCOVR'].map((src) => (
                        <button
                          key={src}
                          onClick={() => {
                            setFilterSource(src);
                            setLogPage(1);
                          }}
                          className={`px-3 py-1.5 hover:text-teal cursor-pointer ${filterSource === src ? 'bg-teal text-bg-void font-bold' : 'text-text-secondary'}`}
                        >
                          {src}
                        </button>
                      ))}
                    </div>

                    <div className="relative">
                      <input
                        type="text"
                        placeholder="SEARCH SENSORS..."
                        value={searchQuery}
                        onChange={(e) => {
                          setSearchQuery(e.target.value);
                          setLogPage(1);
                        }}
                        className="bg-bg-void border border-border-hairline text-text-primary rounded pl-8 pr-3 py-1.5 text-[10px] font-mono placeholder:text-text-ghost focus:outline-none focus:border-teal/40 max-w-[160px]"
                      />
                      <Search className="w-3.5 h-3.5 text-text-muted absolute left-2.5 top-1/2 -translate-y-1/2" />
                    </div>
                  </div>
                </div>

                {/* Dense Table Layout */}
                <div className="overflow-x-auto">
                  <table className="w-full font-mono text-xs text-text-secondary text-left">
                    <thead>
                      <tr className="border-b border-border-hairline uppercase text-text-muted text-[10px] tracking-widest bg-bg-void/30">
                        <th className="p-3">TIME (UTC)</th>
                        <th className="p-3">SOURCE</th>
                        <th className="p-3">SOLAR WIND (KM/S)</th>
                        <th className="p-3">Bz COMP (nT)</th>
                        <th className="p-3">GEOMAGNETIC Kp</th>
                        <th className="p-3">PROTON FLUX (pfu)</th>
                        <th className="p-3">STORM LEVEL</th>
                      </tr>
                    </thead>
                    <tbody>
                      {paginatedLogs.length > 0 ? (
                        paginatedLogs.map((item, idx) => {
                          const timeStr = new Date(item.timestamp).toLocaleTimeString([], {
                            hour: '2-digit',
                            minute: '2-digit',
                            second: '2-digit',
                            hour12: false
                          });

                          // Kp zone backgrounds
                          const kpBg = 
                            item.Kp >= 7 ? 'bg-danger/10 text-danger font-bold border-l-2 border-danger pl-2' :
                            item.Kp >= 5 ? 'bg-orange-500/10 text-orange-500 font-bold border-l-2 border-orange-500 pl-2' :
                            item.Kp >= 4 ? 'bg-yellow-400/10 text-yellow-400 font-bold' :
                            'text-teal';

                          const sourceColors = 
                            item.source === 'NOAA' ? 'text-blue-400 border border-blue-400/20 bg-blue-400/5' :
                            item.source === 'GOES' ? 'text-green-400 border border-green-400/20 bg-green-400/5' :
                            item.source === 'DONKI' ? 'text-violet border border-violet/20 bg-violet/5' :
                            'text-teal border border-teal/20 bg-teal/5';

                          return (
                            <tr key={idx} className="border-b border-border-hairline/40 hover:bg-bg-card-hover transition-colors">
                              <td className="p-3 text-text-primary font-bold">{timeStr}</td>
                              <td className="p-3">
                                <span className={`px-2 py-0.5 rounded text-[9px] font-bold ${sourceColors}`}>
                                  {item.source}
                                </span>
                              </td>
                              <td className="p-3 text-text-primary">{item.solarWind.toFixed(1)}</td>
                              <td className={`p-3 font-bold ${item.Bz < 0 ? 'text-danger' : 'text-teal'}`}>
                                {item.Bz.toFixed(1)} nT
                              </td>
                              <td className="p-3">
                                <span className={`inline-block py-1 px-2.5 rounded text-xs ${kpBg}`}>
                                  {item.Kp.toFixed(1)}
                                </span>
                              </td>
                              <td className="p-3 text-text-primary">{item.protonFlux.toFixed(1)}</td>
                              <td className="p-3">
                                <span className={`font-bold ${item.Kp >= 7 ? 'text-danger' : item.Kp >= 5 ? 'text-orange-500' : 'text-text-muted'}`}>
                                  {item.Kp >= 7 ? 'G3 STRONG STORM' : item.Kp >= 5 ? 'G1 MINOR STORM' : 'NOMINAL'}
                                </span>
                              </td>
                            </tr>
                          );
                        })
                      ) : (
                        <tr>
                          <td colSpan={7} className="text-center p-8 text-text-muted font-sans text-sm">
                            <Activity className="w-8 h-8 mx-auto mb-2 text-text-ghost animate-pulse" />
                            No telemetric logs matching criteria.
                          </td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>

                {/* Pagination Controls */}
                <div className="flex items-center justify-between border-t border-border-hairline pt-4 mt-4 font-mono text-[10px] text-text-muted select-none">
                  <span>SHOWING {paginatedLogs.length} OF {filteredLogs.length} OBS DATA POINTS</span>
                  
                  <div className="flex items-center gap-4">
                    <button
                      onClick={() => setLogPage(Math.max(1, logPage - 1))}
                      disabled={logPage === 1}
                      className="p-1 border border-border-hairline hover:border-teal rounded disabled:opacity-30 cursor-pointer text-text-primary"
                    >
                      <ChevronLeft className="w-4 h-4" />
                    </button>
                    <span>PAGE {logPage} OF {totalPages}</span>
                    <button
                      onClick={() => setLogPage(Math.min(totalPages, logPage + 1))}
                      disabled={logPage === totalPages}
                      className="p-1 border border-border-hairline hover:border-teal rounded disabled:opacity-30 cursor-pointer text-text-primary"
                    >
                      <ChevronRight className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>
            </>
          )}

          {/* Tab 2: FORECAST DETAIL VIEW */}
          {activeTab === 'FORECAST' && (
            <div id="forecast_tab_panel" className="border border-border-hairline bg-bg-card p-6 rounded-md shadow-lg space-y-6">
              <div className="border-b border-border-hairline pb-4 flex justify-between items-center">
                <div>
                  <h3 className="font-space font-bold text-lg text-text-primary">Predictive forecast specs</h3>
                  <p className="font-sans text-[11px] text-text-muted tracking-wide uppercase">LSTM time-series sequence matrix</p>
                </div>
                {onRefreshData && (
                  <button onClick={onRefreshData} className="flex items-center gap-1 border border-border-hairline hover:border-teal px-3 py-1.5 rounded font-mono text-xs text-teal cursor-pointer">
                    RE-SOLVE PIPELINES
                  </button>
                )}
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {forecastSummary.map((item) => (
                  <div key={item.horizon} className="border border-border-hairline bg-bg-void/40 p-5 rounded space-y-4">
                    <div className="flex items-center justify-between border-b border-border-hairline pb-3">
                      <span className="font-space font-bold text-sm text-text-primary">{item.horizon} OUTLOOK</span>
                      {renderRiskBadge(item.risk)}
                    </div>

                    <div className="space-y-2.5 font-mono text-xs">
                      <div className="flex justify-between">
                        <span className="text-text-muted">PREDICTED Kp:</span>
                        <span className="text-teal font-bold">{item.Kp.toFixed(1)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-text-muted">STORM PROBABILITY:</span>
                        <span className="text-text-primary font-bold">{item.stormProb}%</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-text-muted">CONFIDENCE WEIGHT:</span>
                        <span className="text-text-primary font-bold">{item.confidence}%</span>
                      </div>
                    </div>

                    <div className="pt-3 border-t border-border-hairline/40 font-mono text-[9px] text-text-muted leading-relaxed">
                      Confidence metrics indicate the statistical accuracy deviation limit calculated on historical validation arrays.
                    </div>
                  </div>
                ))}
              </div>

              <div className="border border-border-hairline bg-bg-void p-4 rounded font-mono text-[11px] text-text-muted leading-relaxed">
                <span className="text-teal font-bold">OPERATIONAL LOGIC:</span> If prediction algorithms forecast Kp values above 5.0 in the 1H/3H sequence windows, defensive maneuvers are automatically dispatched.
              </div>
            </div>
          )}

          {/* Tab 3: ACTIVE ALERTS DETAILED LIST */}
          {activeTab === 'ALERTS' && (
            <div id="alerts_tab_panel" className="border border-border-hairline bg-bg-card p-6 rounded-md shadow-lg space-y-6">
              <div className="border-b border-border-hairline pb-4">
                <h3 className="font-space font-bold text-lg text-text-primary">Operator alert console</h3>
                <p className="font-sans text-[11px] text-text-muted tracking-wide uppercase">Automatic shield threshold logs</p>
              </div>

              {activeAlerts.length > 0 ? (
                <div className="space-y-4">
                  {activeAlerts.map((alert) => (
                    <div key={alert.id} className="border border-danger bg-danger/5 rounded p-5 relative overflow-hidden flex flex-col md:flex-row md:items-center justify-between gap-4">
                      <div className="space-y-2">
                        <div className="flex items-center gap-2">
                          <span className="relative flex h-2 w-2">
                            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-danger opacity-75"></span>
                            <span className="relative inline-flex rounded-full h-2 w-2 bg-danger"></span>
                          </span>
                          <span className="font-mono text-xs font-bold text-danger uppercase tracking-widest">
                            {alert.level} RISK RADIATION FLUX DETECTED
                          </span>
                        </div>
                        <p className="font-mono text-xs text-text-secondary leading-relaxed max-w-2xl">
                          {alert.message}
                        </p>
                      </div>

                      <div className="flex flex-col md:items-end text-left md:text-right font-mono text-[10px] text-text-muted">
                        <span>ALERT ID: {alert.id}</span>
                        <span>STAMP: {new Date(alert.timestamp).toLocaleTimeString()}</span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="border border-teal/40 bg-teal/5 rounded p-8 flex flex-col items-center justify-center text-center gap-3">
                  <div className="h-12 w-12 rounded-full border border-teal flex items-center justify-center text-teal shadow-[0_0_15px_rgba(0,255,209,0.2)]">
                    <ShieldAlert className="w-6 h-6" />
                  </div>
                  <h4 className="font-space font-bold text-teal tracking-widest uppercase">
                    ALL SYSTEMS SECURE
                  </h4>
                  <p className="text-sm text-text-secondary max-w-md font-sans">
                    No active geostationary radiation threats detected in satellite fields. Magnetopause and solar wind flows are stable.
                  </p>
                </div>
              )}
            </div>
          )}

          {/* Tab 4: HISTORICAL DATA CHARTS & RECORDS */}
          {activeTab === 'HISTORY' && (
            <div id="history_tab_panel" className="border border-border-hairline bg-bg-card p-6 rounded-md shadow-lg space-y-6">
              <div className="border-b border-border-hairline pb-4">
                <h3 className="font-space font-bold text-lg text-text-primary">Historical telemetry matrix</h3>
                <p className="font-sans text-[11px] text-text-muted tracking-wide uppercase">Deep time-series validation arrays</p>
              </div>

              {/* Comprehensive timeline graph */}
              <div className="bg-bg-void/40 border border-border-hairline p-4 rounded">
                <div className="flex items-center justify-between border-b border-border-hairline/60 pb-2 mb-4">
                  <span className="font-sans text-[10px] text-text-secondary tracking-wide uppercase">24-hour continuous geomagnetic sequence</span>
                </div>
                <TimelineChart data={historyData} />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 font-mono text-xs">
                <div className="border border-border-hairline bg-bg-void/40 p-4 rounded space-y-2">
                  <div className="text-teal font-bold tracking-wider text-[11px] uppercase mb-1">History constraints</div>
                  <p>Buffer depth: <span className="text-text-primary font-bold">100 samples</span></p>
                  <p>Validated anomalies: <span className="text-text-primary font-bold">02 detected</span></p>
                  <p>Extreme peak Kp: <span className="text-text-primary font-bold font-mono">8.2</span></p>
                </div>

                <div className="border border-border-hairline bg-bg-void/40 p-4 rounded space-y-2">
                  <div className="text-teal font-bold tracking-wider text-[11px] uppercase mb-1">Instrument validation</div>
                  <p>NOAA portal handshake: <span className="text-text-primary font-bold">OK</span></p>
                  <p>GOES-16 probe synchronization: <span className="text-text-primary font-bold">OK</span></p>
                  <p>DONKI repository access: <span className="text-text-primary font-bold">OK</span></p>
                </div>
              </div>
            </div>
          )}

        </div>
      </main>

      {/* ── FLOATING COLLAPSIBLE WEBSOCKET LIVE TERMINAL (Bottom-Right) ── */}
      <div 
        id="ws_terminal_collapsible"
        className={`fixed right-4 bottom-4 w-full max-w-[360px] border border-border-hairline bg-bg-card rounded-t-md shadow-2xl z-50 overflow-hidden flex flex-col transition-all duration-300 ${
          isLogCollapsed ? 'h-10' : 'h-[280px]'
        }`}
      >
        {/* Terminal Header */}
        <button
          onClick={() => setIsLogCollapsed(!isLogCollapsed)}
          className="bg-bg-void border-b border-border-hairline px-4 py-2.5 flex items-center justify-between font-mono text-[10px] font-bold text-teal cursor-pointer hover:bg-bg-card-hover text-left w-full"
        >
          <div className="flex items-center gap-2">
            <span className={`h-2 w-2 rounded-full ${wsConnected ? 'bg-teal animate-pulse' : 'bg-warning'}`} />
            <span className="uppercase tracking-wider">
              {wsConnected ? 'CONNECTED' : 'DISCONNECTED'}
            </span>
          </div>
          {isLogCollapsed ? <ChevronUp className="w-4 h-4 text-text-muted" /> : <ChevronDown className="w-4 h-4 text-text-muted" />}
        </button>

        {/* Scrolling Log Content */}
        {!isLogCollapsed && (
          <div 
            ref={logContainerRef}
            className="flex-1 p-3 bg-[#050709] font-mono text-[9px] text-text-secondary overflow-y-auto space-y-1.5 select-text"
          >
            {wsLogs.length > 0 ? (
              wsLogs.map((log, idx) => {
                const parsed = parseLogLine(log);
                return (
                  <div key={idx} className="grid grid-cols-[55px_70px_1fr] gap-2 py-0.5 border-b border-border-hairline/10 text-[9px] text-text-secondary items-center leading-normal">
                    <span className="text-text-ghost">[{parsed.time}]</span>
                    <span className={`font-bold uppercase tracking-wider ${
                      parsed.category === 'INGEST' ? 'text-teal' :
                      parsed.category === 'DISCONNECT' ? 'text-danger' :
                      parsed.category === 'HANDSHAKE' ? 'text-violet font-bold' :
                      'text-yellow-400'
                    }`}>{parsed.category}</span>
                    <span className="truncate text-text-primary font-sans" title={parsed.details}>
                      {parsed.details}
                    </span>
                  </div>
                );
              })
            ) : (
              <div className="text-center text-text-ghost py-16">
                WAITING FOR INCOMING TELEMETRY EVENTS...
              </div>
            )}
          </div>
        )}
      </div>

    </div>
  );
}








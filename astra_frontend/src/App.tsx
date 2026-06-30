import React, { useEffect, useState } from 'react';
import { HashRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider, useQuery, useQueryClient } from '@tanstack/react-query';
import Lenis from 'lenis';

// Import custom views
import LandingView from './components/LandingView';
import LoginView from './components/LoginView';
import DashboardView from './components/DashboardView';

import { Telemetry, ForecastSummary, Alert, SystemStatus } from './types';

// --- Type Augmentations to satisfy TS in components we cannot edit ---
declare module './types' {
  interface Telemetry {
    predicted_solar_wind?: number;
    predicted_kp_index?: number;
    predicted_proton_flux?: number;
    predicted_bz?: number;
    risk_level?: string;
    forecast_time?: string;
  }
}

declare global {
  interface HTMLElement {
    align: string;
  }
}
// --------------------------------------------------------------------

// API Base calculation
const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

// Create TanStack Query Client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchInterval: 30000, // 30s refetch intervals
      staleTime: 15000,       // 15s stale time
      retry: 3,
      refetchOnWindowFocus: false
    }
  }
});

function MainAppRoutes() {
  const qc = useQueryClient();
  const [wsLogs, setWsLogs] = useState<string[]>([]);
  const [wsConnected, setWsConnected] = useState(false);

  // Lenis Smooth Scroll Setup
  useEffect(() => {
    const lenis = new Lenis({
      duration: 1.2,
      easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
    });

    function raf(time: number) {
      lenis.raf(time);
      requestAnimationFrame(raf);
    }

    requestAnimationFrame(raf);

    return () => {
      lenis.destroy();
    };
  }, []);

  // WebSockets live feed integration
  useEffect(() => {
    let ws: WebSocket | null = null;
    let reconnectTimeout: any = null;

    const connect = () => {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const wsUrl = `ws://localhost:8000/ws/live`;

      ws = new WebSocket(wsUrl);

      ws.onopen = () => {
        setWsConnected(true);
        const timestamp = new Date().toLocaleTimeString();
        setWsLogs((prev) => [...prev.slice(-30), `[${timestamp}] HANDSHAKE: LIVE TELEMETRY STREAM ESTABLISHED`]);
      };

      ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          const timestamp = new Date().toLocaleTimeString();
          setWsLogs((prev) => [
            ...prev.slice(-30),
            `[${timestamp}] SYNC: Kp:${message.kp_index ?? '--'} | RISK:${message.risk_level ?? '--'}`
          ]);

          qc.invalidateQueries({ queryKey: ['telemetry'] });
          qc.invalidateQueries({ queryKey: ['history'] });
          qc.invalidateQueries({ queryKey: ['alerts'] });
          qc.invalidateQueries({ queryKey: ['forecast'] });
        } catch (err) {
          console.error('Error parsing WS message:', err);
        }
      };

      ws.onclose = () => {
        setWsConnected(false);
        const timestamp = new Date().toLocaleTimeString();
        setWsLogs((prev) => [...prev.slice(-30), `[${timestamp}] DISCONNECT: CARRIER LOST. RETRYING IN 5S...`]);
        reconnectTimeout = setTimeout(connect, 5000);
      };

      ws.onerror = (err) => {
        console.warn('WebSocket stream not active (expected in proxy/sandboxed environments), falling back to secure REST polling:', err);
        ws?.close();
      };
    };

    connect();

    return () => {
      if (ws) ws.close();
      if (reconnectTimeout) clearTimeout(reconnectTimeout);
    };
  }, [qc]);

  // --- Telemetry (latest forecast) ---
  const { data: currentTelemetryRaw, refetch: refetchTelemetry } = useQuery({
    queryKey: ['telemetry'],
    queryFn: async () => {
      const res = await fetch(`${API_BASE}/api/v1/forecast/latest`);
      if (!res.ok) throw new Error('Failed to fetch latest forecast');
      return res.json();
    },
    refetchInterval: 5000,
  });

  // --- History (raw observations), normalized to a flat array the UI expects ---
  const { data: historyDataRaw } = useQuery({
    queryKey: ['history'],
    queryFn: async () => {
      const res = await fetch(`${API_BASE}/api/v1/history?limit=50`);
      if (!res.ok) throw new Error('Failed to fetch historical telemetry');
      return res.json();
    },
    initialData: { total: 0, observations: [] },
    refetchInterval: 5000,
  });

  const historyData: Telemetry[] = (historyDataRaw?.observations ?? []).map((o: any) => {
    let kp = o.kp_index ?? 0;
    let risk: 'LOW' | 'MEDIUM' | 'HIGH' | 'EXTREME' = 'LOW';
    if (kp >= 7) risk = 'EXTREME';
    else if (kp >= 5) risk = 'HIGH';
    else if (kp >= 4) risk = 'MEDIUM';

    return {
      timestamp: o.observation_time || '',
      source: o.source || 'NOAA',
      solarWind: o.solar_wind_speed ?? 0,
      Kp: kp,
      protonFlux: o.proton_flux_10mev ?? 0,
      Bz: o.bz_component ?? 0,
      risk: risk,
    };
  });

  // Derive fallback values from the latest observation when forecast fields are null
  const latestObs = historyDataRaw?.observations?.[0];

  const currentTelemetry: Telemetry | undefined = currentTelemetryRaw ? {
    timestamp: currentTelemetryRaw.forecast_time || '',
    source: 'NOAA',
    solarWind: currentTelemetryRaw.predicted_solar_wind ?? latestObs?.solar_wind_speed ?? 0,
    Kp: currentTelemetryRaw.predicted_kp_index ?? latestObs?.kp_index ?? 0,
    protonFlux: currentTelemetryRaw.predicted_proton_flux ?? latestObs?.proton_flux_10mev ?? 0,
    Bz: currentTelemetryRaw.predicted_bz ?? latestObs?.bz_component ?? 0,
    risk: currentTelemetryRaw.risk_level ?? 'LOW',
  } : undefined;

  // --- Forecast summary (1h/3h/24h object), normalized to an array ---
  const { data: forecastSummaryRaw } = useQuery({
    queryKey: ['forecast'],
    queryFn: async () => {
      const res = await fetch(`${API_BASE}/api/v1/forecast/summary`);
      if (!res.ok) throw new Error('Failed to fetch forecast summary');
      return res.json();
    },
    initialData: { summary: {} },
    refetchInterval: 5000,
  });

  // Fall back to latest observation kp_index when the ML model doesn't output predicted_kp
  const fallbackKp = latestObs?.kp_index ?? 0;

  const forecastSummary: ForecastSummary[] = Object.entries(forecastSummaryRaw?.summary ?? {}).map(([horizon, item]: [string, any]) => ({
    horizon,
    risk: item.risk_level ?? 'LOW',
    Kp: item.predicted_kp ?? fallbackKp,
    stormProb: Math.round((item.storm_probability ?? 0) * 100),
    confidence: Math.round((item.confidence ?? 0) * 100),
  }));

  // --- Active alerts (already returns a plain array from the backend) ---
  const { data: activeAlertsRaw } = useQuery({
    queryKey: ['alerts'],
    queryFn: async () => {
      const res = await fetch(`${API_BASE}/api/v1/risk/alerts`);
      if (!res.ok) throw new Error('Failed to fetch active alerts');
      const data = await res.json();
      return data.alerts || [];
    },
    initialData: [],
    refetchInterval: 5000,
  });

  const activeAlerts: Alert[] = (activeAlertsRaw ?? [])
    .filter((a: any) => a.is_active === true)
    .map((a: any) => ({
      id: String(a.id),
      level: a.alert_level ?? 'LOW',
      message: a.message ?? '',
      timestamp: a.triggered_at ?? '',
    }));

  // --- System status (health + uptime), normalized field names ---
  const { data: systemStatusRaw } = useQuery({
    queryKey: ['systemStatus'],
    queryFn: async () => {
      const [statusRes, healthRes] = await Promise.all([
        fetch(`${API_BASE}/api/v1/status`),
        fetch(`${API_BASE}/api/v1/health`)
      ]);
      const statusData = await statusRes.json();
      const healthData = await healthRes.json();
      return { statusData, healthData };
    },
    refetchInterval: 10000,
  });

  const systemStatus: SystemStatus | undefined = systemStatusRaw ? {
    uptime: systemStatusRaw.statusData?.uptime_human ?? String(systemStatusRaw.statusData?.uptime_seconds ?? '00:00:00'),
    postgresql: systemStatusRaw.healthData?.services?.postgres?.status === 'up' ? 'healthy' : 'down',
    redis: systemStatusRaw.healthData?.services?.redis?.status === 'up' ? 'healthy' : 'down',
    api: systemStatusRaw.healthData?.status === 'healthy' ? 'healthy' : 'down',
  } : undefined;

  const handleManualRefresh = () => {
    refetchTelemetry();
    qc.invalidateQueries({ queryKey: ['history'] });
    qc.invalidateQueries({ queryKey: ['alerts'] });
    qc.invalidateQueries({ queryKey: ['forecast'] });
  };

  return (
    <HashRouter>
      <Routes>
        <Route
          path="/"
          element={
            <LandingView
              currentTelemetry={currentTelemetry}
              historyData={historyData}
              forecastSummary={forecastSummary}
              activeAlerts={activeAlerts}
              health={systemStatus}
            />
          }
        />
        <Route
          path="/login"
          element={<LoginView health={systemStatus} />}
        />
        <Route
          path="/dashboard"
          element={
            <DashboardView
              currentTelemetry={currentTelemetry}
              historyData={historyData}
              forecastSummary={forecastSummary}
              activeAlerts={activeAlerts}
              systemStatus={systemStatus || null}
              wsLogs={wsLogs}
              wsConnected={wsConnected}
              onRefreshData={handleManualRefresh}
            />
          }
        />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </HashRouter>
  );
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <MainAppRoutes />
    </QueryClientProvider>
  );
}


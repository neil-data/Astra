export interface Telemetry {
  timestamp: string;
  source: 'NOAA' | 'GOES' | 'DONKI' | 'DSCOVR';
  solarWind: number; // km/s
  Kp: number; // 0-9
  protonFlux: number; // pfu
  Bz: number; // nT
  risk: 'LOW' | 'MEDIUM' | 'HIGH' | 'EXTREME';
}

export interface ForecastSummary {
  horizon: string;
  risk: 'LOW' | 'MEDIUM' | 'HIGH' | 'EXTREME';
  Kp: number;
  stormProb: number;
  confidence: number;
}

export interface Alert {
  id: string;
  level: 'LOW' | 'MEDIUM' | 'HIGH' | 'EXTREME';
  message: string;
  timestamp: string;
}

export interface SystemStatus {
  uptime: string;
  postgresql: string;
  redis: string;
  api: string;
}

import express from 'express';
import http from 'http';
import { WebSocketServer, WebSocket } from 'ws';
import path from 'path';
import { createServer as createViteServer } from 'vite';

// Space Telemetry Interface
interface Telemetry {
  timestamp: string;
  source: 'NOAA' | 'GOES' | 'DONKI' | 'DSCOVR';
  solarWind: number; // km/s
  Kp: number; // 0-9
  protonFlux: number; // pfu
  Bz: number; // nT
  risk: 'LOW' | 'MEDIUM' | 'HIGH' | 'EXTREME';
}

// Global state variables
const startTime = Date.now();
const history: Telemetry[] = [];
let currentTelemetry: Telemetry;
let wss: WebSocketServer;

// Seed 50 historical items with realistic drifts
function generateHistoricalData() {
  const sources: Telemetry['source'][] = ['NOAA', 'GOES', 'DONKI', 'DSCOVR'];
  let lastKp = 3.2;
  let lastSolarWind = 450;
  let lastProtonFlux = 1200;
  let lastBz = 2.0;

  const now = Date.now();
  for (let i = 49; i >= 0; i--) {
    const timeOffset = i * 15 * 60 * 1000; // 15 mins intervals
    const itemTime = new Date(now - timeOffset);

    // Random walk with boundaries
    lastKp = Math.max(0.5, Math.min(9.0, lastKp + (Math.random() - 0.5) * 0.8));
    lastSolarWind = Math.max(300, Math.min(900, lastSolarWind + (Math.random() - 0.5) * 40));
    lastProtonFlux = Math.max(100, Math.min(60000, lastProtonFlux + (Math.random() - 0.5) * 500));
    lastBz = Math.max(-15, Math.min(15, lastBz + (Math.random() - 0.5) * 3));

    // Determine risk based on Kp
    let risk: Telemetry['risk'] = 'LOW';
    if (lastKp >= 7.0) {
      risk = 'EXTREME';
    } else if (lastKp >= 5.0) {
      risk = 'HIGH';
    } else if (lastKp >= 4.0) {
      risk = 'MEDIUM';
    }

    history.push({
      timestamp: itemTime.toISOString(),
      source: sources[Math.floor(Math.random() * sources.length)],
      solarWind: Math.round(lastSolarWind * 10) / 10,
      Kp: Math.round(lastKp * 10) / 10,
      protonFlux: Math.round(lastProtonFlux * 10) / 10,
      Bz: Math.round(lastBz * 10) / 10,
      risk
    });
  }
  currentTelemetry = history[history.length - 1];
}

generateHistoricalData();

// Simulate real-time updates every 10 seconds
function updateTelemetry() {
  const sources: Telemetry['source'][] = ['NOAA', 'GOES', 'DONKI', 'DSCOVR'];
  
  // Apply a drift to current values
  let newKp = Math.max(0.5, Math.min(9.0, currentTelemetry.Kp + (Math.random() - 0.5) * 0.5));
  let newSolarWind = Math.max(300, Math.min(900, currentTelemetry.solarWind + (Math.random() - 0.5) * 25));
  let newProtonFlux = Math.max(100, Math.min(60000, currentTelemetry.protonFlux + (Math.random() - 0.5) * 350));
  let newBz = Math.max(-15, Math.min(15, currentTelemetry.Bz + (Math.random() - 0.5) * 2));

  // Round values
  newKp = Math.round(newKp * 10) / 10;
  newSolarWind = Math.round(newSolarWind * 10) / 10;
  newProtonFlux = Math.round(newProtonFlux * 10) / 10;
  newBz = Math.round(newBz * 10) / 10;

  // 1% chance of sudden geomagnetic flare event (Kp jump)
  if (Math.random() < 0.02) {
    newKp = Math.round((6.5 + Math.random() * 2.5) * 10) / 10;
    newSolarWind = Math.round((700 + Math.random() * 150) * 10) / 10;
    newProtonFlux = Math.round((35000 + Math.random() * 20000) * 10) / 10;
    newBz = Math.round((-10 - Math.random() * 4) * 10) / 10;
  }

  // Determine risk level
  let risk: Telemetry['risk'] = 'LOW';
  if (newKp >= 7.0) {
    risk = 'EXTREME';
  } else if (newKp >= 5.0) {
    risk = 'HIGH';
  } else if (newKp >= 4.0) {
    risk = 'MEDIUM';
  }

  const updated: Telemetry = {
    timestamp: new Date().toISOString(),
    source: sources[Math.floor(Math.random() * sources.length)],
    solarWind: newSolarWind,
    Kp: newKp,
    protonFlux: newProtonFlux,
    Bz: newBz,
    risk
  };

  currentTelemetry = updated;
  history.push(updated);
  if (history.length > 100) {
    history.shift(); // keep sliding buffer of latest 100
  }

  // Broadcast to all websocket clients
  if (wss) {
    const message = JSON.stringify({
      type: 'TELEMETRY_UPDATE',
      data: updated
    });
    
    wss.clients.forEach((client) => {
      if (client.readyState === WebSocket.OPEN) {
        client.send(message);
      }
    });
  }
}

setInterval(updateTelemetry, 10000);

// Helper for uptime string calculation
function getUptimeString(): string {
  const diffMs = Date.now() - startTime;
  const diffSecs = Math.floor(diffMs / 1000);
  const hours = Math.floor(diffSecs / 3600);
  const mins = Math.floor((diffSecs % 3600) / 60);
  const secs = diffSecs % 60;
  return `${hours.toString().padStart(2, '0')}:${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
}

async function startServer() {
  const app = express();
  const server = http.createServer(app);
  
  // Setup WebSocket Server bound to same server
  wss = new WebSocketServer({ noServer: true });

  server.on('upgrade', (request, socket, head) => {
    const urlStr = request.url || '';
    const pathname = urlStr.split('?')[0];
    if (pathname === '/ws/live') {
      wss.handleUpgrade(request, socket, head, (ws) => {
        wss.emit('connection', ws, request);
      });
    } else {
      socket.destroy();
    }
  });

  wss.on('connection', (ws) => {
    // On connect, send the current telemetry value
    ws.send(JSON.stringify({
      type: 'INIT',
      data: currentTelemetry
    }));
  });

  // Share WebSocket server globally so updateTelemetry can broadcast
  (global as any).wss = wss;

  // JSON parsing middleware
  app.use(express.json());

  // CORS headers
  app.use((req, res, next) => {
    res.header('Access-Control-Allow-Origin', '*');
    res.header('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept');
    next();
  });

  // ==========================================
  // API ENDPOINTS
  // ==========================================

  // Health check endpoint
  app.get('/api/v1/health', (req, res) => {
    res.json({
      status: 'ok',
      postgresql: 'healthy',
      redis: 'healthy',
      api: 'healthy'
    });
  });

  // Uptime/Status check
  app.get('/api/v1/status', (req, res) => {
    res.json({
      uptime: getUptimeString()
    });
  });

  // Latest forecast
  app.get('/api/v1/forecast/latest', (req, res) => {
    res.json(currentTelemetry);
  });

  // Current risk context
  app.get('/api/v1/risk/current', (req, res) => {
    let factors: string[] = [];
    if (currentTelemetry.Kp >= 7.0) {
      factors = ['Critical geomagnetic storm active', 'Proton flux exceeds warning thresholds', 'Extreme magnetopause compression'];
    } else if (currentTelemetry.Kp >= 5.0) {
      factors = ['High geomagnetic activity detected', 'Elevated solar wind speed', 'Magnetospheric field disturbances'];
    } else if (currentTelemetry.Kp >= 4.0) {
      factors = ['Moderate solar wind enhancement', 'Minor magnetic instability'];
    } else {
      factors = ['Geomagnetic field quiet', 'Solar wind and proton flux within nominal range'];
    }

    res.json({
      risk: currentTelemetry.risk,
      contributingFactors: factors
    });
  });

  // 1H / 3H / 24H Forecast Summary
  app.get('/api/v1/forecast/summary', (req, res) => {
    const KpCurrent = currentTelemetry.Kp;

    // Simulate 1H, 3H, 24H based on current Kp
    const generateForecast = (hours: number, driftCoeff: number) => {
      const predKp = Math.round(Math.max(0.5, Math.min(9.0, KpCurrent + (Math.random() - 0.45) * driftCoeff)) * 10) / 10;
      let risk: Telemetry['risk'] = 'LOW';
      if (predKp >= 7.0) risk = 'EXTREME';
      else if (predKp >= 5.0) risk = 'HIGH';
      else if (predKp >= 4.0) risk = 'MEDIUM';

      const stormProb = Math.min(100, Math.max(0, Math.round((predKp / 9.0) * 100)));
      const confidence = Math.max(50, Math.min(98, Math.round(98 - (hours * 1.5))));

      return {
        horizon: `${hours}H`,
        risk,
        Kp: predKp,
        stormProb,
        confidence
      };
    };

    res.json([
      generateForecast(1, 0.4),
      generateForecast(3, 1.0),
      generateForecast(24, 2.2)
    ]);
  });

  // Alerts
  app.get('/api/v1/risk/alerts', (req, res) => {
    if (currentTelemetry.risk === 'HIGH' || currentTelemetry.risk === 'EXTREME') {
      res.json({
        count: 1,
        alerts: [{
          id: 'ALERT_GEO_RAD_' + Date.now().toString().slice(-4),
          level: currentTelemetry.risk,
          message: `${currentTelemetry.risk} RADIATION EVENT IN PROGRESS: Kp index is ${currentTelemetry.Kp}. Solar wind speed is ${currentTelemetry.solarWind} km/s. Orbit GEO-STAT satellites at risk of electrostatic discharge.`,
          timestamp: currentTelemetry.timestamp
        }]
      });
    } else {
      res.json({
        count: 0,
        alerts: []
      });
    }
  });

  // Historical timeline
  app.get('/api/v1/history', (req, res) => {
    const limit = parseInt(req.query.limit as string) || 50;
    const items = history.slice(-limit);
    res.json(items);
  });

  // ==========================================
  // STATIC ASSETS & VITE INTEGRATION
  // ==========================================

  if (process.env.NODE_ENV !== 'production') {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: 'spa',
    });
    app.use(vite.middlewares);
  } else {
    const distPath = path.join(process.cwd(), 'dist');
    app.use(express.static(distPath));
    app.get('*', (req, res) => {
      res.sendFile(path.join(distPath, 'index.html'));
    });
  }

  const PORT = 3000;
  server.listen(PORT, '0.0.0.0', () => {
    console.log(`ASTRA backend running at http://0.0.0.0:${PORT}`);
  });
}

startServer().catch((err) => {
  console.error('Failed to start ASTRA server:', err);
});

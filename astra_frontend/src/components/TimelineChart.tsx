import React from 'react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine
} from 'recharts';
import { Telemetry } from '../types';

interface TimelineChartProps {
  data: Telemetry[];
}

const CustomTooltip = ({ active, payload }: any) => {
  if (active && payload && payload.length) {
    const data = payload[0].payload as Telemetry;
    const timeStr = new Date(data.timestamp).toLocaleTimeString([], {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: false
    });
    
    return (
      <div className="bg-bg-card border border-border-strong p-3 rounded-md shadow-2xl font-mono text-[10px] leading-relaxed max-w-[240px]">
        <div className="flex items-center justify-between border-b border-border-hairline pb-2 mb-2 font-bold text-text-primary">
          <span>UTC {timeStr}</span>
          <span className="text-[9px] border border-border-hairline bg-bg-elevated px-1.5 py-0.2 rounded text-text-secondary uppercase">
            {data.source}
          </span>
        </div>
        <div className="space-y-1 text-text-secondary">
          <div className="flex justify-between">
            <span>Kp INDEX:</span>
            <span className="text-teal font-bold">{data.Kp}</span>
          </div>
          <div className="flex justify-between">
            <span>SOLAR WIND:</span>
            <span className="text-text-primary font-bold">{data.solarWind} km/s</span>
          </div>
          <div className="flex justify-between">
            <span>PROTON FLUX:</span>
            <span className="text-text-primary font-bold">{data.protonFlux} pfu</span>
          </div>
          <div className="flex justify-between">
            <span>Bz FIELD:</span>
            <span className={data.Bz < 0 ? 'text-danger font-bold' : 'text-teal font-bold'}>
              {data.Bz} nT
            </span>
          </div>
          <div className="flex justify-between pt-1 border-t border-border-hairline/40 mt-1">
            <span>RISK:</span>
            <span className={`font-bold uppercase ${
              data.risk === 'EXTREME' ? 'text-danger' :
              data.risk === 'HIGH' ? 'text-orange-500' :
              data.risk === 'MEDIUM' ? 'text-yellow-400' :
              'text-teal'
            }`}>
              {data.risk}
            </span>
          </div>
        </div>
      </div>
    );
  }
  return null;
};

export default function TimelineChart({ data }: TimelineChartProps) {
  // Format X Axis values
  const formatXAxis = (tickItem: string) => {
    try {
      const date = new Date(tickItem);
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: false });
    } catch {
      return '';
    }
  };

  return (
    <div id="timeline_chart_container" className="w-full h-[320px] font-mono relative">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart
          data={data}
          margin={{ top: 15, right: 10, left: -20, bottom: 0 }}
        >
          <defs>
            <linearGradient id="colorKp" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#00FFD1" stopOpacity={0.25} />
              <stop offset="95%" stopColor="#00FFD1" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid
            strokeDasharray="3 3"
            stroke="#1E2740"
            vertical={false}
          />
          <XAxis
            dataKey="timestamp"
            tickFormatter={formatXAxis}
            stroke="#5C6580"
            tick={{ fontSize: 9, fill: '#5C6580' }}
            tickLine={{ stroke: '#1E2740' }}
            axisLine={{ stroke: '#1E2740' }}
            dy={8}
          />
          <YAxis
            domain={[0, 9]}
            tickCount={10}
            stroke="#5C6580"
            tick={{ fontSize: 9, fill: '#5C6580' }}
            tickLine={{ stroke: '#1E2740' }}
            axisLine={{ stroke: '#1E2740' }}
            dx={-8}
          />
          <Tooltip content={<CustomTooltip />} cursor={{ stroke: '#2A3450', strokeWidth: 1 }} />
          
          {/* Danger Alert Threshold (Kp = 7.0) */}
          <ReferenceLine
            y={7}
            stroke="#FF3B3B"
            strokeDasharray="4 4"
            label={{
              value: 'EXTREME STORM THRESHOLD',
              fill: '#FF3B3B',
              fontSize: 8,
              position: 'top',
              offset: 4,
              fontFamily: 'JetBrains Mono'
            }}
          />

          {/* High Warning Threshold (Kp = 5.0) */}
          <ReferenceLine
            y={5}
            stroke="#FFB020"
            strokeDasharray="4 4"
            label={{
              value: 'HIGH RADIATION THRESHOLD',
              fill: '#FFB020',
              fontSize: 8,
              position: 'top',
              offset: 4,
              fontFamily: 'JetBrains Mono'
            }}
          />

          <Area
            type="monotone"
            dataKey="Kp"
            stroke="#00FFD1"
            strokeWidth={2}
            fillOpacity={1}
            fill="url(#colorKp)"
            activeDot={{ r: 5, stroke: '#050709', strokeWidth: 2, fill: '#00FFD1' }}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}

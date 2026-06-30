import React, { ReactNode } from 'react';
import { motion } from 'motion/react';

interface MetricCardProps {
  id?: string;
  title: string;
  subLabel?: string;
  children: ReactNode;
  footer?: ReactNode;
  isAlerting?: boolean;
  alertLevel?: 'LOW' | 'MEDIUM' | 'HIGH' | 'EXTREME';
}

export default function MetricCard({
  id,
  title,
  subLabel,
  children,
  footer,
  isAlerting = false,
  alertLevel = 'LOW'
}: MetricCardProps) {
  // Border colors based on alert states
  const borderClass = 
    isAlerting && alertLevel === 'EXTREME' ? 'border-danger animate-pulse shadow-[0_0_15px_rgba(255,59,59,0.15)] bg-danger/5' :
    isAlerting && alertLevel === 'HIGH' ? 'border-orange-500 animate-pulse shadow-[0_0_12px_rgba(249,115,22,0.12)] bg-orange-500/5' :
    alertLevel === 'MEDIUM' ? 'border-warning/60 bg-warning/5' :
    'border-border-hairline hover:border-teal/40 bg-bg-card';

  const glowClass = 
    alertLevel === 'EXTREME' ? 'shadow-[inset_0_0_20px_rgba(255,59,59,0.06)]' :
    alertLevel === 'HIGH' ? 'shadow-[inset_0_0_20px_rgba(249,115,22,0.05)]' :
    alertLevel === 'MEDIUM' ? 'shadow-[inset_0_0_20px_rgba(255,176,32,0.03)]' :
    'shadow-[inset_0_0_20px_rgba(0,255,209,0.02)]';

  return (
    <motion.div
      id={id}
      whileHover={{ y: -4, transition: { duration: 0.2, ease: 'easeOut' } }}
      className={`relative w-full rounded border p-5 flex flex-col justify-between transition-colors duration-200 ${borderClass} ${glowClass}`}
    >
      {/* Dynamic scan line overlay for higher levels */}
      {(alertLevel === 'HIGH' || alertLevel === 'EXTREME') && (
        <div className="absolute inset-0 overflow-hidden rounded pointer-events-none">
          <div className="absolute inset-x-0 h-[1.5px] bg-danger/30 animate-scanline [animation-duration:3s]" />
        </div>
      )}

      <div>
        {/* Card Header */}
        <div className="flex items-center justify-between mb-3">
          <span className="font-mono text-[10px] tracking-[0.15em] text-text-muted uppercase font-bold">
            {title}
          </span>
          {subLabel && (
            <span className="font-mono text-[9px] text-text-ghost uppercase tracking-widest">
              {subLabel}
            </span>
          )}
        </div>

        {/* Content Slot */}
        <div className="my-2">
          {children}
        </div>
      </div>

      {/* Card Footer Slot */}
      {footer && (
        <div className="mt-4 pt-3 border-t border-border-hairline/40 flex items-center justify-between font-mono text-[10px] text-text-muted">
          {footer}
        </div>
      )}
    </motion.div>
  );
}

import React from 'react';
import { 
  Clock, Calendar, AlertTriangle, CheckCircle2, 
  HelpCircle, ShieldAlert, ArrowRight, Layers
} from 'lucide-react';
import { TemporalAudit } from '../../types';

interface TemporalRadarViewProps {
  temporalAudits: TemporalAudit[];
}

export const TemporalRadarView: React.FC<TemporalRadarViewProps> = ({ temporalAudits }) => {
  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'current':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
            <CheckCircle2 className="w-3.5 h-3.5" /> Current Applicable Cycle
          </span>
        );
      case 'potentially_outdated':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-500/15 text-amber-400 border border-amber-500/30">
            <AlertTriangle className="w-3.5 h-3.5" /> Prior Cycle Warning
          </span>
        );
      case 'outdated':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-rose-500/15 text-rose-400 border border-rose-500/30">
            <ShieldAlert className="w-3.5 h-3.5" /> Superseded / Stale
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-slate-800 text-slate-400 border border-slate-700">
            <HelpCircle className="w-3.5 h-3.5" /> Date Unverified
          </span>
        );
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto p-4 sm:p-6 lg:p-8">
      {/* Header */}
      <div className="p-5 rounded-2xl bg-[#111827] border border-amber-500/30 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <Clock className="w-5 h-5 text-amber-400" />
            <h2 className="text-base font-bold text-slate-100">Temporal Decay Radar</h2>
            <span className="text-xs font-mono font-semibold px-2 py-0.5 rounded bg-amber-950 text-amber-300 border border-amber-800">
              Reference Year: 2026
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1 max-w-2xl leading-relaxed">
            Audits academic cycles, four-digit years, and calendar deadlines embedded in source text. Disentangles the webpage retrieval timestamp from actual policy applicability.
          </p>
        </div>

        <div className="flex items-center gap-2 bg-[#0B0F19] p-2.5 rounded-xl border border-[#1F293D] text-xs font-mono">
          <span className="text-slate-400">Total Audited Sources:</span>
          <span className="text-cyan-400 font-bold">{temporalAudits.length}</span>
        </div>
      </div>

      {/* Temporal Timeline / Radar Cards */}
      <div className="space-y-4">
        {temporalAudits.map((audit) => {
          const isCurrent = audit.temporal_status === 'current';
          const isStale = audit.temporal_status === 'potentially_outdated' || audit.temporal_status === 'outdated';

          return (
            <div
              key={audit.id}
              className={`p-5 rounded-2xl transition-all ${
                isCurrent 
                  ? 'bg-[#111827] border border-emerald-500/30' 
                  : (isStale 
                      ? 'bg-[#111827] border border-amber-500/40 shadow-md shadow-amber-950/10' 
                      : 'bg-[#111827] border border-[#1F293D]')
              }`}
            >
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-[#1F293D]">
                <div>
                  <h3 className="text-sm font-bold text-slate-100 truncate max-w-xl">
                    {audit.source_title || 'Source Document'}
                  </h3>
                  <span className="text-[11px] font-mono text-slate-400">
                    {audit.source_url || 'source-url'}
                  </span>
                </div>
                <div>{getStatusBadge(audit.temporal_status)}</div>
              </div>

              {/* Rationale & Staleness Reason */}
              <div className="my-3 p-3 rounded-xl bg-[#161F30] border border-[#1F293D] text-xs text-slate-300 leading-relaxed">
                <span className="font-semibold text-slate-200">Temporal Audit Finding: </span>
                {audit.staleness_reason || 'No specific temporal anomaly detected.'}
              </div>

              {/* Detected Temporal Entities */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-2 text-xs">
                {/* Academic Cycles */}
                <div className="p-3 rounded-lg bg-[#0E1524] border border-[#1F293D]">
                  <span className="text-[10px] font-mono text-slate-400 uppercase tracking-wider block mb-1">
                    Detected Academic Cycles
                  </span>
                  <div className="flex flex-wrap gap-1">
                    {audit.detected_cycles.length > 0 ? (
                      audit.detected_cycles.map((c, i) => (
                        <span key={i} className="px-1.5 py-0.5 rounded font-mono text-xs bg-cyan-950 text-cyan-300 border border-cyan-800">
                          {c}
                        </span>
                      ))
                    ) : (
                      <span className="text-slate-400 text-xs italic">None detected</span>
                    )}
                  </div>
                </div>

                {/* Detected Calendar Years */}
                <div className="p-3 rounded-lg bg-[#0E1524] border border-[#1F293D]">
                  <span className="text-[10px] font-mono text-slate-400 uppercase tracking-wider block mb-1">
                    Referenced Calendar Years
                  </span>
                  <div className="flex flex-wrap gap-1">
                    {audit.detected_years.length > 0 ? (
                      audit.detected_years.map((y, i) => (
                        <span key={i} className="px-1.5 py-0.5 rounded font-mono text-xs bg-slate-800 text-slate-300 border border-slate-700">
                          {y}
                        </span>
                      ))
                    ) : (
                      <span className="text-slate-400 text-xs italic">None detected</span>
                    )}
                  </div>
                </div>

                {/* Calendar Deadlines */}
                <div className="p-3 rounded-lg bg-[#0E1524] border border-[#1F293D]">
                  <span className="text-[10px] font-mono text-slate-400 uppercase tracking-wider block mb-1">
                    Explicit Deadlines
                  </span>
                  <div className="space-y-0.5">
                    {audit.calendar_deadlines.length > 0 ? (
                      audit.calendar_deadlines.map((d, i) => (
                        <div key={i} className="text-emerald-400 font-mono text-[11px] truncate">
                          • {d}
                        </div>
                      ))
                    ) : (
                      <span className="text-slate-400 text-xs italic">None detected</span>
                    )}
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};


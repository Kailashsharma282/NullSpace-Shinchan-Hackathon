import React, { useState } from 'react';
import { 
  CheckCircle2, AlertOctagon, Clock, EyeOff, AlertTriangle, 
  HelpCircle, ExternalLink, ArrowRight, ShieldAlert, Sparkles, Filter
} from 'lucide-react';
import { AnalysisResults, EpistemicMatrixItem } from '../../types';

interface OverviewViewProps {
  results: AnalysisResults | null;
  onNavigate: (tab: any) => void;
}

export const OverviewView: React.FC<OverviewViewProps> = ({ results, onNavigate }) => {
  const [selectedReq, setSelectedReq] = useState<EpistemicMatrixItem | null>(null);
  const [statusFilter, setStatusFilter] = useState<string>('all');

  if (!results) {
    return (
      <div className="flex flex-col items-center justify-center p-12 text-center text-slate-400">
        <div className="w-12 h-12 rounded-full bg-slate-800 flex items-center justify-center mb-3 animate-pulse">
          <EyeOff className="w-6 h-6 text-slate-500" />
        </div>
        <h3 className="text-sm font-semibold text-slate-300">No Epistemic Results Loaded</h3>
        <p className="text-xs text-slate-500 mt-1">Select or create a research project or click "Load Scholarship Demo" to begin.</p>
      </div>
    );
  }

  const { kpis, matrix } = results;

  const filteredMatrix = matrix.filter(item => {
    if (statusFilter === 'all') return true;
    return item.status === statusFilter;
  });

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'verified':
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
            <CheckCircle2 className="w-3 h-3" /> Grounded & Supported
          </span>
        );
      case 'conflict':
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-semibold bg-rose-500/15 text-rose-400 border border-rose-500/30">
            <AlertOctagon className="w-3 h-3" /> Factual Contradiction
          </span>
        );
      case 'stale':
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-semibold bg-amber-500/15 text-amber-400 border border-amber-500/30">
            <Clock className="w-3 h-3" /> Temporal Risk / Stale
          </span>
        );
      case 'dark_spot':
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-semibold bg-cyan-950/40 text-cyan-300 border border-cyan-500/40 border-dashed">
            <EyeOff className="w-3 h-3 text-cyan-400" /> Digital Dark Spot
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-semibold bg-purple-500/15 text-purple-400 border border-purple-500/30">
            <HelpCircle className="w-3 h-3" /> Review Required
          </span>
        );
    }
  };

  return (
    <div className="space-y-8 max-w-7xl mx-auto p-4 sm:p-6 lg:p-8">
      {/* 1. Dashboard KPI Cards */}
      <div>
        <h2 className="text-xs font-bold text-slate-400 uppercase tracking-wider font-mono mb-3">
          Epistemic Metrics & Surface Telemetry
        </h2>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
          {/* Total Requirements */}
          <div className="p-4 rounded-xl bg-[#111827] border border-[#1F293D] shadow-sm">
            <span className="text-[11px] font-medium text-slate-400">Total Requirements</span>
            <div className="mt-1 flex items-baseline justify-between">
              <span className="text-2xl font-bold font-mono text-slate-100">{kpis.total_requirements}</span>
              <span className="text-[10px] text-cyan-400 font-mono">Schema</span>
            </div>
          </div>

          {/* Evidence Coverage */}
          <div className="p-4 rounded-xl bg-[#111827] border border-[#1F293D] shadow-sm">
            <span className="text-[11px] font-medium text-slate-400">Evidence Coverage</span>
            <div className="mt-1 flex items-baseline justify-between">
              <span className="text-2xl font-bold font-mono text-emerald-400">{kpis.evidence_coverage_pct}%</span>
              <span className="text-[10px] text-slate-400 font-mono">Grounded</span>
            </div>
          </div>

          {/* Dark Spots */}
          <div 
            onClick={() => onNavigate('darkspots')}
            className="p-4 rounded-xl bg-[#111827] border border-rose-500/30 hover:border-rose-500/60 transition-all cursor-pointer shadow-sm group"
          >
            <div className="flex items-center justify-between">
              <span className="text-[11px] font-medium text-rose-300">Digital Dark Spots</span>
              <ArrowRight className="w-3 h-3 text-rose-400 opacity-0 group-hover:opacity-100 transition-opacity" />
            </div>
            <div className="mt-1 flex items-baseline justify-between">
              <span className="text-2xl font-bold font-mono text-rose-400">{kpis.dark_spots_count}</span>
              <span className="text-[10px] font-mono text-rose-400/80">InDegree=0</span>
            </div>
          </div>

          {/* Contradictions */}
          <div 
            onClick={() => onNavigate('conflicts')}
            className="p-4 rounded-xl bg-[#111827] border border-red-500/30 hover:border-red-500/60 transition-all cursor-pointer shadow-sm group"
          >
            <div className="flex items-center justify-between">
              <span className="text-[11px] font-medium text-red-300">Contradictions</span>
              <ArrowRight className="w-3 h-3 text-red-400 opacity-0 group-hover:opacity-100 transition-opacity" />
            </div>
            <div className="mt-1 flex items-baseline justify-between">
              <span className="text-2xl font-bold font-mono text-red-400">{kpis.detected_conflicts_count}</span>
              <span className="text-[10px] font-mono text-red-400/80">Pairwise</span>
            </div>
          </div>

          {/* Stale Claims */}
          <div 
            onClick={() => onNavigate('temporal')}
            className="p-4 rounded-xl bg-[#111827] border border-amber-500/30 hover:border-amber-500/60 transition-all cursor-pointer shadow-sm group"
          >
            <div className="flex items-center justify-between">
              <span className="text-[11px] font-medium text-amber-300">Stale Sources</span>
              <ArrowRight className="w-3 h-3 text-amber-400 opacity-0 group-hover:opacity-100 transition-opacity" />
            </div>
            <div className="mt-1 flex items-baseline justify-between">
              <span className="text-2xl font-bold font-mono text-amber-400">{kpis.stale_claims_count}</span>
              <span className="text-[10px] font-mono text-amber-400/80">Temporal</span>
            </div>
          </div>

          {/* Verification Risk Score */}
          <div 
            onClick={() => onNavigate('checklist')}
            className="p-4 rounded-xl bg-[#111827] border border-[#1F293D] hover:border-cyan-500/40 transition-all cursor-pointer shadow-sm group"
          >
            <div className="flex items-center justify-between">
              <span className="text-[11px] font-medium text-slate-400">Risk Score</span>
              <ArrowRight className="w-3 h-3 text-cyan-400 opacity-0 group-hover:opacity-100 transition-opacity" />
            </div>
            <div className="mt-1 flex items-baseline justify-between">
              <span className={`text-2xl font-bold font-mono ${
                kpis.overall_risk_score >= 60 ? 'text-rose-400' : (kpis.overall_risk_score >= 35 ? 'text-amber-400' : 'text-emerald-400')
              }`}>
                {kpis.overall_risk_score}
              </span>
              <span className="text-[10px] font-mono text-slate-400">/ 100</span>
            </div>
          </div>
        </div>
      </div>

      {/* 2. Epistemic Coverage Matrix */}
      <div className="p-5 rounded-2xl bg-[#111827] border border-[#1F293D]">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
          <div>
            <h3 className="text-sm font-bold text-slate-100">Epistemic Coverage Matrix</h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Multi-source alignment across mandatory decision requirements. Hover or click a requirement to inspect grounded claims.
            </p>
          </div>

          {/* Filter Pills */}
          <div className="flex items-center gap-1.5 overflow-x-auto text-xs">
            <button
              onClick={() => setStatusFilter('all')}
              className={`px-2.5 py-1 rounded-lg font-medium transition-colors ${
                statusFilter === 'all' ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40' : 'bg-[#161F30] text-slate-400 hover:text-slate-200'
              }`}
            >
              All ({matrix.length})
            </button>
            <button
              onClick={() => setStatusFilter('dark_spot')}
              className={`px-2.5 py-1 rounded-lg font-medium transition-colors ${
                statusFilter === 'dark_spot' ? 'bg-cyan-950 text-cyan-300 border border-cyan-400' : 'bg-[#161F30] text-slate-400 hover:text-slate-200'
              }`}
            >
              Dark Spots ({matrix.filter(m => m.status === 'dark_spot').length})
            </button>
            <button
              onClick={() => setStatusFilter('conflict')}
              className={`px-2.5 py-1 rounded-lg font-medium transition-colors ${
                statusFilter === 'conflict' ? 'bg-rose-950 text-rose-300 border border-rose-400' : 'bg-[#161F30] text-slate-400 hover:text-slate-200'
              }`}
            >
              Conflicts ({matrix.filter(m => m.status === 'conflict').length})
            </button>
            <button
              onClick={() => setStatusFilter('verified')}
              className={`px-2.5 py-1 rounded-lg font-medium transition-colors ${
                statusFilter === 'verified' ? 'bg-emerald-950 text-emerald-300 border border-emerald-400' : 'bg-[#161F30] text-slate-400 hover:text-slate-200'
              }`}
            >
              Supported ({matrix.filter(m => m.status === 'verified').length})
            </button>
          </div>
        </div>

        {/* Matrix Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          {filteredMatrix.map((item) => {
            const isDark = item.status === 'dark_spot';
            const isConf = item.status === 'conflict';
            const isStale = item.status === 'stale';
            const isVer = item.status === 'verified';

            return (
              <div
                key={item.requirement_id}
                onClick={() => setSelectedReq(item)}
                className={`p-4 rounded-xl transition-all cursor-pointer relative overflow-hidden ${
                  isDark 
                    ? 'bg-[#111827] border-2 border-dashed border-cyan-500/40 hover:border-cyan-400/80 shadow-md shadow-cyan-950/20' 
                    : (isConf 
                        ? 'bg-rose-950/20 border border-rose-500/40 hover:border-rose-500/80' 
                        : (isStale 
                            ? 'bg-amber-950/20 border border-amber-500/40 hover:border-amber-500/80'
                            : (isVer 
                                ? 'bg-emerald-950/15 border border-emerald-500/30 hover:border-emerald-500/60' 
                                : 'bg-[#161F30] border border-[#1F293D] hover:border-slate-500')))
                }`}
              >
                <div className="flex items-start justify-between gap-2">
                  <h4 className="text-xs font-bold text-slate-100 line-clamp-1">{item.requirement_name}</h4>
                  <span className="text-[10px] font-mono font-semibold px-1.5 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700 flex-shrink-0">
                    Imp: {item.importance}/5
                  </span>
                </div>

                <div className="mt-3 flex items-center justify-between">
                  {getStatusBadge(item.status)}
                  <span className="text-[11px] font-mono text-slate-400">
                    {item.mapped_claims_count} {item.mapped_claims_count === 1 ? 'claim' : 'claims'}
                  </span>
                </div>

                {isDark && (
                  <p className="mt-2 text-[11px] text-cyan-300/80 line-clamp-2">
                    Zero reviewed sources provide claims. High omission risk.
                  </p>
                )}
                {isConf && (
                  <p className="mt-2 text-[11px] text-rose-300/80 line-clamp-2">
                    Material factual divergence detected between source claims.
                  </p>
                )}
              </div>
            );
          })}
        </div>

        {/* Disclaimer note */}
        <p className="mt-4 text-[11px] text-slate-400 italic">
          Disclaimer: "Grounded & Supported" describes consistent evidence coverage across analyzed sources, not independent verification that the underlying claim is universally factual.
        </p>
      </div>

      {/* 3. STRICT FACT VERSUS AI SEPARATION (Signature Feature) */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <div>
            <h2 className="text-sm font-bold text-slate-100 flex items-center gap-2">
              <span>Strict Fact vs. AI Uncertainty Separation</span>
              <span className="px-2 py-0.5 text-[10px] font-mono font-semibold uppercase bg-indigo-950 border border-indigo-700 text-indigo-300 rounded">
                Signature Feature
              </span>
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Grounded source quotes are strictly isolated from system-generated uncertainty signals and inferences.
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* LEFT: Grounded Evidence Vault */}
          <div className="p-5 rounded-2xl bg-[#0E1524] border border-emerald-500/30 shadow-lg shadow-emerald-950/10">
            <div className="flex items-center justify-between pb-3 border-b border-[#1F293D]">
              <div className="flex items-center gap-2">
                <div className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse" />
                <h3 className="text-xs font-bold font-mono tracking-wider text-emerald-400 uppercase">
                  Grounded Evidence Vault
                </h3>
              </div>
              <span className="text-[10px] font-mono text-slate-400">Source Verbatim Only</span>
            </div>

            <div className="mt-4 space-y-3 max-h-[460px] overflow-y-auto pr-1">
              {results.matrix.flatMap(m => m.claims).slice(0, 5).map((claim) => (
                <div key={claim.id} className="p-3.5 rounded-xl bg-[#111827] border border-[#1F293D] space-y-2">
                  <div className="flex items-center justify-between text-[11px]">
                    <span className="font-semibold text-slate-300 truncate max-w-[220px]">
                      {claim.source_title || 'Source Document'}
                    </span>
                    <span className="text-[10px] font-mono text-emerald-400 bg-emerald-950 px-1.5 py-0.5 rounded border border-emerald-800">
                      Offsets [{claim.char_start} : {claim.char_end}]
                    </span>
                  </div>

                  {/* Exact Verbatim Quote */}
                  <blockquote className="p-2.5 rounded-lg bg-[#0B0F19] border-l-2 border-emerald-500 text-xs font-mono text-slate-200 leading-relaxed">
                    "{claim.exact_quote}"
                  </blockquote>

                  <div className="flex items-center justify-between text-[10px] text-slate-400 pt-1">
                    <span className="truncate max-w-[200px] text-slate-400">
                      {claim.source_domain || 'source-domain'}
                    </span>
                    <span className="font-mono text-slate-400">
                      Confidence: {Math.round(claim.confidence * 100)}%
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* RIGHT: Uncertainty & Gap Signals */}
          <div className="p-5 rounded-2xl bg-[#0E1524] border border-rose-500/30 shadow-lg shadow-rose-950/10">
            <div className="flex items-center justify-between pb-3 border-b border-[#1F293D]">
              <div className="flex items-center gap-2">
                <div className="w-2.5 h-2.5 rounded-full bg-rose-400 animate-pulse" />
                <h3 className="text-xs font-bold font-mono tracking-wider text-rose-400 uppercase">
                  Uncertainty & Gap Signals
                </h3>
              </div>
              <span className="text-[10px] font-mono text-slate-400">AI & Heuristic Inference</span>
            </div>

            <div className="mt-4 space-y-3 max-h-[460px] overflow-y-auto pr-1">
              {/* Dark Spot Signals */}
              {results.dark_spots.map(ds => (
                <div key={ds.requirement_id} className="p-3.5 rounded-xl bg-cyan-950/30 border border-cyan-500/40 space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="px-2 py-0.5 rounded text-[10px] font-bold font-mono uppercase bg-cyan-900 text-cyan-200 border border-cyan-700">
                      AI-INFERRED GAP (DARK SPOT)
                    </span>
                    <span className="text-[10px] font-mono text-cyan-400">InDegree = 0</span>
                  </div>
                  <h4 className="text-xs font-bold text-slate-100">{ds.requirement_name}</h4>
                  <p className="text-xs text-slate-300">
                    Mandatory decision requirement completely omitted by reviewed sources.
                  </p>
                  {ds.recommended_dork && (
                    <div className="p-2 rounded bg-[#0B0F19] text-[11px] font-mono text-cyan-300 select-all border border-cyan-900">
                      {ds.recommended_dork}
                    </div>
                  )}
                </div>
              ))}

              {/* Contradiction Signals */}
              {results.conflicts.map(cf => (
                <div key={cf.id} className="p-3.5 rounded-xl bg-red-950/30 border border-red-500/40 space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="px-2 py-0.5 rounded text-[10px] font-bold font-mono uppercase bg-red-900 text-red-200 border border-red-700">
                      DETECTED CONTRADICTION
                    </span>
                    <span className="text-[10px] font-mono text-red-300 font-semibold">{cf.status.toUpperCase()}</span>
                  </div>
                  <h4 className="text-xs font-bold text-slate-100">{cf.requirement_name || 'Requirement Conflict'}</h4>
                  <p className="text-xs text-slate-300 leading-relaxed">
                    {cf.explanation}
                  </p>
                </div>
              ))}

              {/* Temporal Staleness Signals */}
              {results.temporal_audits.filter(t => t.temporal_status !== 'current').map(t => (
                <div key={t.id} className="p-3.5 rounded-xl bg-amber-950/30 border border-amber-500/40 space-y-1.5">
                  <div className="flex items-center justify-between">
                    <span className="px-2 py-0.5 rounded text-[10px] font-bold font-mono uppercase bg-amber-900 text-amber-200 border border-amber-700">
                      HEURISTIC TEMPORAL WARNING
                    </span>
                    <span className="text-[10px] font-mono text-amber-300 capitalize">{t.temporal_status}</span>
                  </div>
                  <h4 className="text-xs font-bold text-slate-100 truncate">{t.source_title || 'Source'}</h4>
                  <p className="text-xs text-amber-200/90 leading-relaxed">
                    {t.staleness_reason}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};


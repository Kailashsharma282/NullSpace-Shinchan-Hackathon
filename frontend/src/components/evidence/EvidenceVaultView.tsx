import React, { useState } from 'react';
import { 
  ShieldCheck, Filter, ExternalLink, Hash, Calendar, 
  Search, Eye, CheckCircle2, ChevronRight
} from 'lucide-react';
import { AnalysisResults, ExtractedClaim, SourceDocument } from '../../types';

interface EvidenceVaultViewProps {
  results: AnalysisResults | null;
  sources: SourceDocument[];
}

export const EvidenceVaultView: React.FC<EvidenceVaultViewProps> = ({ results, sources }) => {
  const [selectedReqId, setSelectedReqId] = useState<string>('all');
  const [selectedSourceId, setSelectedSourceId] = useState<string>('all');
  const [inspectClaim, setInspectClaim] = useState<ExtractedClaim | null>(null);

  if (!results) {
    return <div className="p-8 text-center text-slate-400">No evidence loaded.</div>;
  }

  const allClaims = results.matrix.flatMap(m => m.claims);
  const requirements = results.matrix.map(m => ({ id: m.requirement_id, name: m.requirement_name }));

  const filteredClaims = allClaims.filter(claim => {
    if (selectedReqId !== 'all' && claim.requirement_id !== selectedReqId) return false;
    if (selectedSourceId !== 'all' && claim.source_id !== selectedSourceId) return false;
    return true;
  });

  const inspectedSource = inspectClaim ? sources.find(s => s.id === inspectClaim.source_id) : null;

  return (
    <div className="space-y-6 max-w-7xl mx-auto p-4 sm:p-6 lg:p-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-5 rounded-2xl bg-[#111827] border border-emerald-500/30">
        <div>
          <div className="flex items-center gap-2">
            <ShieldCheck className="w-5 h-5 text-emerald-400" />
            <h2 className="text-base font-bold text-slate-100">Grounded Evidence Vault</h2>
          </div>
          <p className="text-xs text-slate-400 mt-1 max-w-xl">
            Immutable repository of verbatim source passages with verified character offsets. AI paraphrases are never stored here.
          </p>
        </div>

        {/* Filters */}
        <div className="flex flex-wrap items-center gap-2">
          <select
            value={selectedReqId}
            onChange={(e) => setSelectedReqId(e.target.value)}
            className="bg-[#161F30] border border-[#1F293D] rounded-lg px-2.5 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
          >
            <option value="all">All Requirements ({requirements.length})</option>
            {requirements.map(r => (
              <option key={r.id} value={r.id}>{r.name}</option>
            ))}
          </select>

          <select
            value={selectedSourceId}
            onChange={(e) => setSelectedSourceId(e.target.value)}
            className="bg-[#161F30] border border-[#1F293D] rounded-lg px-2.5 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
          >
            <option value="all">All Sources ({sources.length})</option>
            {sources.map(s => (
              <option key={s.id} value={s.id}>{s.title.substring(0, 30)}...</option>
            ))}
          </select>
        </div>
      </div>

      {/* Main Grid: Claims List & Offset Inspector */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Claims List */}
        <div className={`space-y-3 ${inspectClaim ? 'lg:col-span-7' : 'lg:col-span-12'}`}>
          {filteredClaims.length === 0 ? (
            <div className="p-12 text-center text-slate-400 bg-[#111827] rounded-xl border border-[#1F293D]">
              No grounded claims matching current filters.
            </div>
          ) : (
            filteredClaims.map((claim) => {
              const isSelected = inspectClaim?.id === claim.id;
              const req = requirements.find(r => r.id === claim.requirement_id);

              return (
                <div
                  key={claim.id}
                  onClick={() => setInspectClaim(claim)}
                  className={`p-4 rounded-xl border transition-all cursor-pointer ${
                    isSelected 
                      ? 'bg-[#161F30] border-emerald-500 shadow-md shadow-emerald-950/20' 
                      : 'bg-[#111827] border-[#1F293D] hover:border-slate-600'
                  }`}
                >
                  <div className="flex items-center justify-between gap-2 text-xs">
                    <span className="font-semibold text-cyan-400 bg-cyan-950/60 px-2 py-0.5 rounded border border-cyan-800">
                      {req?.name || 'Unmapped'}
                    </span>
                    <span className="font-mono text-[11px] text-emerald-400 bg-emerald-950/60 px-2 py-0.5 rounded border border-emerald-800 flex items-center gap-1">
                      <Hash className="w-3 h-3" />
                      Span: [{claim.char_start} : {claim.char_end}]
                    </span>
                  </div>

                  {/* Verbatim quote */}
                  <blockquote className="my-2.5 p-3 rounded-lg bg-[#0B0F19] border-l-2 border-emerald-500 text-xs font-mono text-slate-200 leading-relaxed">
                    "{claim.exact_quote}"
                  </blockquote>

                  <div className="flex flex-wrap items-center justify-between text-[11px] text-slate-400 pt-1 border-t border-[#1F293D]/60 gap-2">
                    <div className="flex items-center gap-2 truncate max-w-sm">
                      <span className="font-medium text-slate-300 truncate">{claim.source_title || 'Source'}</span>
                      <span className="text-slate-400">•</span>
                      <span className="text-slate-400 font-mono text-[10px]">{claim.source_domain}</span>
                    </div>

                    <div className="flex items-center gap-3">
                      <span className="font-mono text-[10px] text-slate-400">
                        Confidence: {(claim.confidence * 100).toFixed(0)}%
                      </span>
                      <button className="flex items-center gap-1 text-cyan-400 hover:text-cyan-300 text-xs font-medium">
                        <span>Inspect Span</span>
                        <ChevronRight className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </div>
                </div>
              );
            })
          )}
        </div>

        {/* Offset Inspector Side Panel */}
        {inspectClaim && (
          <div className="lg:col-span-5 p-5 rounded-2xl bg-[#0E1524] border border-[#1F293D] space-y-4 sticky top-20 self-start">
            <div className="flex items-center justify-between pb-3 border-b border-[#1F293D]">
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                <h3 className="text-xs font-bold font-mono tracking-wider text-slate-200 uppercase">
                  Source Grounding Verification
                </h3>
              </div>
              <button 
                onClick={() => setInspectClaim(null)}
                className="text-xs text-slate-400 hover:text-slate-200"
              >
                Close
              </button>
            </div>

            <div className="space-y-2 text-xs">
              <div className="flex items-center justify-between">
                <span className="text-slate-400">Grounding Status:</span>
                <span className="px-2 py-0.5 rounded font-mono font-semibold bg-emerald-950 text-emerald-300 border border-emerald-800 text-[10px]">
                  VERIFIED MATHEMATICAL MATCH
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-slate-400">Character Range:</span>
                <span className="font-mono text-slate-200">
                  {inspectClaim.char_start} to {inspectClaim.char_end} ({inspectClaim.char_end - inspectClaim.char_start} chars)
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-slate-400">Extraction Method:</span>
                <span className="font-mono text-slate-200">{inspectClaim.extraction_method}</span>
              </div>
            </div>

            {/* Source Raw Text with Highlight */}
            {inspectedSource && inspectedSource.raw_text && (
              <div>
                <label className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block mb-1.5 font-mono">
                  Full Source Snapshot Context
                </label>
                <div className="p-3.5 rounded-xl bg-[#0B0F19] border border-[#1F293D] max-h-72 overflow-y-auto text-xs font-mono text-slate-300 leading-relaxed whitespace-pre-wrap select-text">
                  <span>{inspectedSource.raw_text.substring(0, inspectClaim.char_start)}</span>
                  <mark className="bg-emerald-500/30 text-emerald-200 font-semibold px-1 rounded border-b-2 border-emerald-400">
                    {inspectedSource.raw_text.substring(inspectClaim.char_start, inspectClaim.char_end)}
                  </mark>
                  <span>{inspectedSource.raw_text.substring(inspectClaim.char_end)}</span>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};


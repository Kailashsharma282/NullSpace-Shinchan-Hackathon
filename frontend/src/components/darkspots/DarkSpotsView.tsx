import React, { useState } from 'react';
import { 
  EyeOff, Copy, ExternalLink, Check, AlertTriangle, 
  Search, ShieldAlert, Sparkles, BookOpen
} from 'lucide-react';
import { EpistemicMatrixItem } from '../../types';

interface DarkSpotsViewProps {
  darkSpots: EpistemicMatrixItem[];
}

export const DarkSpotsView: React.FC<DarkSpotsViewProps> = ({ darkSpots }) => {
  const [copiedId, setCopiedId] = useState<string | null>(null);

  const handleCopy = (reqId: string, text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(reqId);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const handleOpenGoogle = (query: string) => {
    const url = `https://www.google.com/search?q=${encodeURIComponent(query)}`;
    window.open(url, '_blank');
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto p-4 sm:p-6 lg:p-8">
      {/* Mathematical Principle Header */}
      <div className="p-5 rounded-2xl bg-[#111827] border border-cyan-500/40 relative overflow-hidden">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-cyan-950 flex items-center justify-center border border-cyan-800">
                <EyeOff className="w-4 h-4 text-cyan-400" />
              </div>
              <h2 className="text-base font-bold text-slate-100">Digital Dark Spot Engine</h2>
              <span className="font-mono text-xs font-semibold px-2 py-0.5 rounded bg-cyan-950 text-cyan-300 border border-cyan-800">
                InDegree(v) = 0
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-2 max-w-2xl leading-relaxed">
              A <strong>Digital Dark Spot</strong> occurs when a mandatory requirement in the decision schema receives zero mapped claims across all ingested sources. Traditional LLMs silently hallucinate or gloss over these omissions; NullSpace treats them as high-priority epistemic risks.
            </p>
          </div>

          <div className="flex items-center gap-3 bg-[#0B0F19] p-3 rounded-xl border border-[#1F293D] self-start md:self-auto">
            <div className="text-right">
              <span className="text-[10px] text-slate-400 block font-mono">DETECTED GAPS</span>
              <span className="text-2xl font-bold font-mono text-rose-400">{darkSpots.length}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Dark Spots List */}
      {darkSpots.length === 0 ? (
        <div className="p-12 text-center rounded-2xl bg-[#111827] border border-[#1F293D] space-y-2">
          <div className="w-12 h-12 rounded-full bg-emerald-950/40 border border-emerald-800/40 flex items-center justify-center mx-auto text-emerald-400">
            <Check className="w-6 h-6" />
          </div>
          <h3 className="text-sm font-semibold text-slate-200">No Digital Dark Spots Detected</h3>
          <p className="text-xs text-slate-400 max-w-md mx-auto">
            All mandatory decision requirements have at least one verified grounded claim from the reviewed sources.
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {darkSpots.map((spot) => {
            const dork = spot.recommended_dork || `site:gov.in "${spot.requirement_name}" guidelines 2026 filetype:pdf`;
            const isCopied = copiedId === spot.requirement_id;

            return (
              <div
                key={spot.requirement_id}
                className="p-5 rounded-2xl bg-[#111827] border-2 border-dashed border-cyan-500/40 space-y-4 hover:border-cyan-400 transition-all shadow-md shadow-cyan-950/20"
              >
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                  <div className="flex items-center gap-2">
                    <span className="px-2 py-0.5 rounded text-[10px] font-bold font-mono uppercase bg-rose-950 text-rose-300 border border-rose-800">
                      CRITICAL OMISSION
                    </span>
                    <h3 className="text-sm font-bold text-slate-100">{spot.requirement_name}</h3>
                  </div>
                  <div className="flex items-center gap-2 font-mono text-xs">
                    <span className="text-slate-400">Mapped Claims:</span>
                    <span className="text-rose-400 font-bold">0</span>
                    <span className="text-slate-400 ml-2">Importance:</span>
                    <span className="text-amber-400 font-bold">{spot.importance}/5</span>
                  </div>
                </div>

                {/* Observation & Why it matters */}
                <div className="p-3.5 rounded-xl bg-[#161F30] border border-[#1F293D] text-xs text-slate-300 leading-relaxed space-y-1.5">
                  <div className="flex items-center gap-1.5 text-cyan-400 font-semibold font-mono text-[11px]">
                    <AlertTriangle className="w-3.5 h-3.5" />
                    <span>Epistemic Observation</span>
                  </div>
                  <p>
                    None of the reviewed sources provide information about <strong className="text-white">"{spot.requirement_name}"</strong>. 
                    Because this is flagged as a mandatory requirement, proceeding without verified guidance exposes applicants or decision-makers to disqualification or compliance failure.
                  </p>
                </div>

                {/* Search Dork Generator */}
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <label className="text-[11px] font-mono font-semibold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
                      <Search className="w-3.5 h-3.5 text-cyan-400" />
                      <span>Targeted Verification Search Dork</span>
                    </label>
                    <span className="text-[10px] text-slate-400">Direct query tailored to bypass surface noise</span>
                  </div>

                  <div className="flex items-center gap-2">
                    <div className="flex-1 p-2.5 rounded-xl bg-[#0B0F19] border border-[#1F293D] font-mono text-xs text-cyan-300 truncate select-all">
                      {dork}
                    </div>

                    <button
                      onClick={() => handleCopy(spot.requirement_id, dork)}
                      className="flex items-center gap-1 px-3 py-2 rounded-xl text-xs font-semibold bg-[#161F30] border border-[#1F293D] text-slate-200 hover:text-white hover:bg-slate-800 transition-colors"
                      title="Copy search query"
                    >
                      {isCopied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                      <span className="hidden sm:inline">{isCopied ? 'Copied' : 'Copy'}</span>
                    </button>

                    <button
                      onClick={() => handleOpenGoogle(dork)}
                      className="flex items-center gap-1 px-3 py-2 rounded-xl text-xs font-semibold bg-cyan-600 text-white hover:bg-cyan-500 transition-colors shadow-sm shadow-cyan-600/30"
                      title="Open search in new tab"
                    >
                      <ExternalLink className="w-3.5 h-3.5" />
                      <span className="hidden sm:inline">Search</span>
                    </button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};


import React, { useState } from 'react';
import { 
  Scale, AlertOctagon, CheckCircle2, HelpCircle, 
  ArrowRightLeft, ExternalLink, MessageSquare, Check, X
} from 'lucide-react';
import { ConflictRecord } from '../../types';
import { api } from '../../services/api';

interface ContradictionMatrixViewProps {
  conflicts: ConflictRecord[];
  onRefresh: () => void;
}

export const ContradictionMatrixView: React.FC<ContradictionMatrixViewProps> = ({
  conflicts,
  onRefresh
}) => {
  const [filter, setFilter] = useState<string>('all');
  const [updatingId, setUpdatingId] = useState<string | null>(null);

  const filteredConflicts = conflicts.filter(c => {
    if (filter === 'all') return true;
    return c.status === filter;
  });

  const handleUpdateStatus = async (conflictId: string, newStatus: string) => {
    setUpdatingId(conflictId);
    try {
      await api.updateConflictStatus(conflictId, newStatus);
      onRefresh();
    } catch (err) {
      alert('Failed to update conflict: ' + String(err));
    } finally {
      setUpdatingId(null);
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto p-4 sm:p-6 lg:p-8">
      {/* Header */}
      <div className="p-5 rounded-2xl bg-[#111827] border border-red-500/30 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <Scale className="w-5 h-5 text-red-400" />
            <h2 className="text-base font-bold text-slate-100">Cross-Source Contradiction Matrix</h2>
          </div>
          <p className="text-xs text-slate-400 mt-1 max-w-2xl leading-relaxed">
            Pairwise comparative evaluation across claims mapped to the identical decision requirement. Exposes numeric threshold discrepancies, policy negations, and conflicting documentation rules.
          </p>
        </div>

        {/* Status Filters */}
        <div className="flex items-center gap-1.5 overflow-x-auto text-xs">
          {['all', 'confirmed', 'requires_review', 'resolved', 'false_positive'].map(st => (
            <button
              key={st}
              onClick={() => setFilter(st)}
              className={`px-2.5 py-1 rounded-lg font-medium capitalize transition-colors ${
                filter === st 
                  ? 'bg-red-500/20 text-red-300 border border-red-500/40' 
                  : 'bg-[#161F30] text-slate-400 hover:text-slate-200'
              }`}
            >
              {st.replace('_', ' ')}
            </button>
          ))}
        </div>
      </div>

      {/* Contradictions List */}
      {filteredConflicts.length === 0 ? (
        <div className="p-12 text-center rounded-2xl bg-[#111827] border border-[#1F293D] text-slate-400">
          No contradiction records matching current filter.
        </div>
      ) : (
        <div className="space-y-6">
          {filteredConflicts.map((conflict) => {
            const isUpdating = updatingId === conflict.id;

            return (
              <div
                key={conflict.id}
                className="p-5 rounded-2xl bg-[#111827] border border-red-500/30 space-y-4 hover:border-red-500/60 transition-all shadow-lg shadow-red-950/10"
              >
                {/* Header row */}
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3 border-b border-[#1F293D]">
                  <div className="flex items-center gap-2">
                    <span className="px-2 py-0.5 rounded text-[10px] font-bold font-mono uppercase bg-red-950 text-red-300 border border-red-800">
                      FACTUAL DIVERGENCE
                    </span>
                    <h3 className="text-sm font-bold text-slate-100">
                      Requirement: {conflict.requirement_name || conflict.requirement_id}
                    </h3>
                  </div>

                  <div className="flex items-center gap-3 text-xs">
                    <span className="font-mono text-slate-400">
                      Confidence: {(conflict.confidence * 100).toFixed(0)}%
                    </span>
                    <span className={`px-2 py-0.5 rounded font-mono text-[10px] font-semibold uppercase ${
                      conflict.status === 'confirmed' 
                        ? 'bg-red-950 text-red-300 border border-red-800'
                        : (conflict.status === 'resolved' 
                            ? 'bg-emerald-950 text-emerald-300 border border-emerald-800'
                            : 'bg-amber-950 text-amber-300 border border-amber-800')
                    }`}>
                      {conflict.status.replace('_', ' ')}
                    </span>
                  </div>
                </div>

                {/* Plain-English Conflict Finding */}
                <div className="p-3.5 rounded-xl bg-red-950/20 border border-red-500/30 text-xs text-red-200 leading-relaxed font-medium">
                  {conflict.explanation}
                </div>

                {/* Side-by-Side Comparative Quotes */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {/* Claim A */}
                  <div className="p-4 rounded-xl bg-[#0E1524] border border-[#1F293D] space-y-2">
                    <div className="flex items-center justify-between text-[11px]">
                      <span className="font-semibold text-cyan-400 font-mono">Source A</span>
                      <span className="font-mono text-slate-400 text-[10px]">
                        Offsets [{conflict.claim_a?.char_start} : {conflict.claim_a?.char_end}]
                      </span>
                    </div>
                    <blockquote className="p-2.5 rounded-lg bg-[#0B0F19] border-l-2 border-cyan-500 text-xs font-mono text-slate-200 leading-relaxed">
                      "{conflict.claim_a?.exact_quote}"
                    </blockquote>
                    <p className="text-[11px] text-slate-400 truncate">
                      {conflict.claim_a?.source_title || 'Document A'} ({conflict.claim_a?.source_domain})
                    </p>
                  </div>

                  {/* Claim B */}
                  <div className="p-4 rounded-xl bg-[#0E1524] border border-[#1F293D] space-y-2">
                    <div className="flex items-center justify-between text-[11px]">
                      <span className="font-semibold text-rose-400 font-mono">Source B</span>
                      <span className="font-mono text-slate-400 text-[10px]">
                        Offsets [{conflict.claim_b?.char_start} : {conflict.claim_b?.char_end}]
                      </span>
                    </div>
                    <blockquote className="p-2.5 rounded-lg bg-[#0B0F19] border-l-2 border-rose-500 text-xs font-mono text-slate-200 leading-relaxed">
                      "{conflict.claim_b?.exact_quote}"
                    </blockquote>
                    <p className="text-[11px] text-slate-400 truncate">
                      {conflict.claim_b?.source_title || 'Document B'} ({conflict.claim_b?.source_domain})
                    </p>
                  </div>
                </div>

                {/* Human Review Actions */}
                <div className="pt-3 border-t border-[#1F293D] flex flex-wrap items-center justify-between gap-3 text-xs">
                  <span className="text-[11px] text-slate-400 font-mono">
                    HUMAN-IN-THE-LOOP RESOLUTION:
                  </span>

                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => handleUpdateStatus(conflict.id, 'confirmed')}
                      disabled={isUpdating || conflict.status === 'confirmed'}
                      className="px-2.5 py-1 rounded-lg font-medium text-xs bg-red-950/60 hover:bg-red-900 border border-red-700 text-red-200 transition-colors disabled:opacity-40"
                    >
                      Confirm Contradiction
                    </button>
                    <button
                      onClick={() => handleUpdateStatus(conflict.id, 'resolved')}
                      disabled={isUpdating || conflict.status === 'resolved'}
                      className="px-2.5 py-1 rounded-lg font-medium text-xs bg-emerald-950/60 hover:bg-emerald-900 border border-emerald-700 text-emerald-200 transition-colors disabled:opacity-40"
                    >
                      Mark Resolved
                    </button>
                    <button
                      onClick={() => handleUpdateStatus(conflict.id, 'false_positive')}
                      disabled={isUpdating || conflict.status === 'false_positive'}
                      className="px-2.5 py-1 rounded-lg font-medium text-xs bg-slate-800 hover:bg-slate-700 border border-slate-600 text-slate-300 transition-colors disabled:opacity-40"
                    >
                      False Positive
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


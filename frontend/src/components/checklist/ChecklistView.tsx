import React, { useState } from 'react';
import { 
  CheckSquare, AlertCircle, Copy, ExternalLink, Check, 
  Search, ShieldAlert, ArrowUpRight, Filter
} from 'lucide-react';
import { ChecklistItem } from '../../types';
import { api } from '../../services/api';

interface ChecklistViewProps {
  items: ChecklistItem[];
  onRefresh: () => void;
}

export const ChecklistView: React.FC<ChecklistViewProps> = ({ items, onRefresh }) => {
  const [filter, setFilter] = useState<'all' | 'unresolved' | 'resolved'>('all');
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [updatingId, setUpdatingId] = useState<string | null>(null);

  const filteredItems = items.filter(item => {
    if (filter === 'unresolved') return !item.is_resolved;
    if (filter === 'resolved') return item.is_resolved;
    return true;
  });

  const handleToggleResolve = async (item: ChecklistItem) => {
    setUpdatingId(item.id);
    try {
      await api.updateChecklistStatus(item.id, !item.is_resolved);
      onRefresh();
    } catch (err) {
      alert('Failed to update item: ' + String(err));
    } finally {
      setUpdatingId(null);
    }
  };

  const handleCopyDork = (id: string, text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const getRiskBadge = (category: string) => {
    switch (category) {
      case 'Critical':
        return (
          <span className="px-2.5 py-0.5 rounded text-[10px] font-bold font-mono uppercase bg-rose-950 text-rose-300 border border-rose-800">
            CRITICAL RISK
          </span>
        );
      case 'High':
        return (
          <span className="px-2.5 py-0.5 rounded text-[10px] font-bold font-mono uppercase bg-red-950 text-red-300 border border-red-800">
            HIGH RISK
          </span>
        );
      case 'Medium':
        return (
          <span className="px-2.5 py-0.5 rounded text-[10px] font-bold font-mono uppercase bg-amber-950 text-amber-300 border border-amber-800">
            MEDIUM RISK
          </span>
        );
      default:
        return (
          <span className="px-2.5 py-0.5 rounded text-[10px] font-bold font-mono uppercase bg-slate-800 text-slate-300 border border-slate-700">
            LOW RISK
          </span>
        );
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto p-4 sm:p-6 lg:p-8">
      {/* Header */}
      <div className="p-5 rounded-2xl bg-[#111827] border border-cyan-500/30 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <CheckSquare className="w-5 h-5 text-cyan-400" />
            <h2 className="text-base font-bold text-slate-100">Entropy-Ranked Verification Checklist</h2>
          </div>
          <p className="text-xs text-slate-400 mt-1 max-w-2xl leading-relaxed">
            Prioritizes verification actions mathematically using normalized Shannon entropy <span className="font-mono text-cyan-300">H_norm(X)</span>, requirement importance, and missingness uncertainty. Focuses human verification where epistemic uncertainty is highest.
          </p>
        </div>

        {/* Filter Pills */}
        <div className="flex items-center gap-1.5 text-xs">
          <button
            onClick={() => setFilter('all')}
            className={`px-3 py-1.5 rounded-lg font-medium transition-colors ${
              filter === 'all' ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40' : 'bg-[#161F30] text-slate-400 hover:text-slate-200'
            }`}
          >
            All ({items.length})
          </button>
          <button
            onClick={() => setFilter('unresolved')}
            className={`px-3 py-1.5 rounded-lg font-medium transition-colors ${
              filter === 'unresolved' ? 'bg-cyan-950 text-cyan-300 border border-cyan-400' : 'bg-[#161F30] text-slate-400 hover:text-slate-200'
            }`}
          >
            Pending ({items.filter(i => !i.is_resolved).length})
          </button>
          <button
            onClick={() => setFilter('resolved')}
            className={`px-3 py-1.5 rounded-lg font-medium transition-colors ${
              filter === 'resolved' ? 'bg-emerald-950 text-emerald-300 border border-emerald-400' : 'bg-[#161F30] text-slate-400 hover:text-slate-200'
            }`}
          >
            Resolved ({items.filter(i => i.is_resolved).length})
          </button>
        </div>
      </div>

      {/* Checklist Items */}
      {filteredItems.length === 0 ? (
        <div className="p-12 text-center rounded-2xl bg-[#111827] border border-[#1F293D] text-slate-400">
          No verification checklist items matching filter.
        </div>
      ) : (
        <div className="space-y-4">
          {filteredItems.map((item, index) => {
            const isCopied = copiedId === item.id;
            const isUpdating = updatingId === item.id;

            return (
              <div
                key={item.id}
                className={`p-5 rounded-2xl transition-all ${
                  item.is_resolved 
                    ? 'bg-[#0E1524]/50 border border-[#1F293D] opacity-60' 
                    : 'bg-[#111827] border border-[#1F293D] hover:border-slate-600 shadow-md'
                }`}
              >
                <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-3 pb-3 border-b border-[#1F293D]">
                  <div className="flex items-start gap-3">
                    <input
                      type="checkbox"
                      checked={item.is_resolved}
                      disabled={isUpdating}
                      onChange={() => handleToggleResolve(item)}
                      className="mt-1 h-4 w-4 rounded border-[#1F293D] bg-[#0B0F19] text-cyan-500 focus:ring-0 cursor-pointer"
                    />
                    <div>
                      <div className="flex items-center gap-2">
                        {getRiskBadge(item.risk_category)}
                        <h3 className={`text-sm font-bold ${item.is_resolved ? 'line-through text-slate-400' : 'text-slate-100'}`}>
                          {item.title}
                        </h3>
                      </div>
                      <p className="text-xs text-slate-400 mt-1 leading-relaxed">{item.reason}</p>
                    </div>
                  </div>

                  <div className="flex items-center gap-3 sm:flex-col sm:items-end flex-shrink-0">
                    <div className="text-right">
                      <span className="text-[10px] text-slate-400 block font-mono">PRIORITY SCORE</span>
                      <span className="text-lg font-bold font-mono text-cyan-400">{item.priority_score} / 100</span>
                    </div>
                    <span className="text-[10px] font-mono text-slate-400">
                      Entropy H_norm: {item.entropy}
                    </span>
                  </div>
                </div>

                {/* Recommended Next Action */}
                <div className="mt-3 p-3 rounded-xl bg-[#161F30] border border-[#1F293D] text-xs text-slate-300 leading-relaxed">
                  <span className="font-semibold text-cyan-300">Recommended Action: </span>
                  {item.recommended_action}
                </div>

                {/* Targeted Search Dork */}
                {item.search_dork && (
                  <div className="mt-3 flex items-center gap-2">
                    <div className="flex-1 p-2 rounded-lg bg-[#0B0F19] border border-[#1F293D] font-mono text-[11px] text-cyan-300 truncate select-all">
                      {item.search_dork}
                    </div>
                    <button
                      onClick={() => handleCopyDork(item.id, item.search_dork)}
                      className="p-2 rounded-lg bg-[#161F30] border border-[#1F293D] text-slate-300 hover:text-white transition-colors"
                      title="Copy search query"
                    >
                      {isCopied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                    </button>
                    <button
                      onClick={() => window.open(`https://www.google.com/search?q=${encodeURIComponent(item.search_dork)}`, '_blank')}
                      className="flex items-center gap-1 px-2.5 py-1.5 rounded-lg text-xs font-semibold bg-cyan-600/80 hover:bg-cyan-500 text-white transition-colors"
                      title="Search in Google"
                    >
                      <ExternalLink className="w-3 h-3" />
                      <span className="hidden sm:inline">Search</span>
                    </button>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};


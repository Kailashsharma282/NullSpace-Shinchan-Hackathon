import React, { useState } from 'react';
import { 
  Globe, Plus, Trash2, ShieldCheck, AlertTriangle, 
  FileText, Hash, CheckCircle2, RefreshCw, ExternalLink, Eye
} from 'lucide-react';
import { SourceDocument } from '../../types';
import { api } from '../../services/api';

interface SourcesManagerViewProps {
  researchId: string;
  sources: SourceDocument[];
  onRefresh: () => void;
  onRunAudit: () => void;
  isAnalyzing: boolean;
}

export const SourcesManagerView: React.FC<SourcesManagerViewProps> = ({
  researchId,
  sources,
  onRefresh,
  onRunAudit,
  isAnalyzing
}) => {
  const [activeTab, setActiveTab] = useState<'url' | 'manual'>('url');
  const [urlInput, setUrlInput] = useState('');
  const [manualTitle, setManualTitle] = useState('');
  const [manualText, setManualText] = useState('');
  const [manualDate, setManualDate] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [inspectSource, setInspectSource] = useState<SourceDocument | null>(null);

  const handleAddUrl = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!urlInput.trim()) return;
    setIsSubmitting(true);
    try {
      const doc = await api.addSourceUrl(researchId, urlInput.trim());
      if (doc.status === 'failed') {
        alert('Ingestion note: ' + (doc.error_message || 'Failed to fetch source'));
      }
      setUrlInput('');
      onRefresh();
    } catch (err) {
      alert('Error adding source: ' + String(err));
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleAddManual = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!manualTitle.trim() || !manualText.trim()) return;
    setIsSubmitting(true);
    try {
      await api.addManualSource(researchId, {
        title: manualTitle.trim(),
        text: manualText.trim(),
        published_date: manualDate.trim() || undefined
      });
      setManualTitle('');
      setManualText('');
      setManualDate('');
      onRefresh();
    } catch (err) {
      alert('Error adding manual text: ' + String(err));
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDelete = async (sourceId: string) => {
    if (!confirm('Remove this source document?')) return;
    try {
      await api.deleteSource(researchId, sourceId);
      onRefresh();
    } catch (err) {
      alert('Error deleting source: ' + String(err));
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto p-4 sm:p-6 lg:p-8">
      {/* Header */}
      <div className="p-5 rounded-2xl bg-[#111827] border border-[#1F293D] flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <Globe className="w-5 h-5 text-cyan-400" />
            <h2 className="text-base font-bold text-slate-100">Multi-Source Ingestion & Evidence Vault</h2>
          </div>
          <p className="text-xs text-slate-400 mt-1 max-w-2xl leading-relaxed">
            Ingest web pages or raw text. Every source is sanitized, stripped of scripts, hashed via SHA-256, and stored as an immutable normalized snapshot. All character offsets anchor directly to this snapshot.
          </p>
        </div>

        <button
          onClick={onRunAudit}
          disabled={isAnalyzing || sources.length === 0}
          className="flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold bg-cyan-600 text-white hover:bg-cyan-500 transition-colors disabled:opacity-50 self-start md:self-auto"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isAnalyzing ? 'animate-spin' : ''}`} />
          <span>{isAnalyzing ? 'Analyzing Sources...' : 'Run Epistemic Analysis'}</span>
        </button>
      </div>

      {/* Ingestion Input Tabs */}
      <div className="p-5 rounded-2xl bg-[#161F30] border border-[#1F293D] space-y-4">
        <div className="flex items-center gap-3 border-b border-[#1F293D] pb-3 text-xs font-medium">
          <button
            onClick={() => setActiveTab('url')}
            className={`pb-1 transition-colors ${
              activeTab === 'url' ? 'text-cyan-400 border-b-2 border-cyan-400 font-bold' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Add Web URL (SSRF-Protected)
          </button>
          <button
            onClick={() => setActiveTab('manual')}
            className={`pb-1 transition-colors ${
              activeTab === 'manual' ? 'text-cyan-400 border-b-2 border-cyan-400 font-bold' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Add Manual Text / Offline Document
          </button>
        </div>

        {activeTab === 'url' ? (
          <form onSubmit={handleAddUrl} className="space-y-3">
            <div className="flex gap-2">
              <input
                type="url"
                value={urlInput}
                onChange={(e) => setUrlInput(e.target.value)}
                placeholder="https://example.com/scholarship-guidelines"
                className="flex-1 bg-[#0B0F19] border border-[#1F293D] rounded-xl px-3.5 py-2 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
                required
              />
              <button
                type="submit"
                disabled={isSubmitting}
                className="px-4 py-2 rounded-xl text-xs font-semibold bg-cyan-600 text-white hover:bg-cyan-500 transition-colors disabled:opacity-50 flex items-center gap-1.5"
              >
                <Plus className="w-4 h-4" />
                <span>{isSubmitting ? 'Fetching...' : 'Ingest URL'}</span>
              </button>
            </div>
            <div className="flex items-center gap-2 text-[11px] text-slate-400">
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
              <span>SSRF protected: private IPs, loopbacks, and cloud metadata endpoints are strictly blocked.</span>
            </div>
          </form>
        ) : (
          <form onSubmit={handleAddManual} className="space-y-3">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <input
                type="text"
                value={manualTitle}
                onChange={(e) => setManualTitle(e.target.value)}
                placeholder="Document Title (e.g. State Notification 2026)"
                className="bg-[#0B0F19] border border-[#1F293D] rounded-xl px-3.5 py-2 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
                required
              />
              <input
                type="text"
                value={manualDate}
                onChange={(e) => setManualDate(e.target.value)}
                placeholder="Publication Date (YYYY-MM-DD, optional)"
                className="bg-[#0B0F19] border border-[#1F293D] rounded-xl px-3.5 py-2 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
              />
            </div>
            <textarea
              value={manualText}
              onChange={(e) => setManualText(e.target.value)}
              placeholder="Paste raw text content here..."
              rows={4}
              className="w-full bg-[#0B0F19] border border-[#1F293D] rounded-xl px-3.5 py-2 text-xs text-slate-200 focus:outline-none focus:border-cyan-500 font-mono"
              required
            />
            <div className="flex justify-end">
              <button
                type="submit"
                disabled={isSubmitting}
                className="px-4 py-2 rounded-xl text-xs font-semibold bg-cyan-600 text-white hover:bg-cyan-500 transition-colors disabled:opacity-50"
              >
                {isSubmitting ? 'Saving...' : 'Save Manual Source'}
              </button>
            </div>
          </form>
        )}
      </div>

      {/* Sources List */}
      <div className="space-y-3">
        <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider font-mono">
          Ingested Sources ({sources.length})
        </h3>

        {sources.length === 0 ? (
          <div className="p-8 text-center rounded-xl bg-[#111827] border border-[#1F293D] text-slate-400 text-xs">
            No sources ingested yet. Add a URL or manual text above.
          </div>
        ) : (
          sources.map((src) => {
            const isFailed = src.status === 'failed';

            return (
              <div
                key={src.id}
                className={`p-4 rounded-xl border transition-all flex flex-col sm:flex-row sm:items-center justify-between gap-3 ${
                  isFailed ? 'bg-red-950/20 border-red-500/40' : 'bg-[#111827] border-[#1F293D] hover:border-slate-600'
                }`}
              >
                <div className="space-y-1 max-w-2xl">
                  <div className="flex items-center gap-2">
                    <h4 className="text-sm font-semibold text-slate-100 truncate">{src.title}</h4>
                    {src.is_fixture && (
                      <span className="px-1.5 py-0.2 rounded text-[10px] font-mono bg-amber-950 text-amber-300 border border-amber-800">
                        Synthetic Demo
                      </span>
                    )}
                    <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-semibold uppercase ${
                      isFailed ? 'bg-red-950 text-red-300 border border-red-800' : 'bg-emerald-950 text-emerald-300 border border-emerald-800'
                    }`}>
                      {src.status}
                    </span>
                  </div>

                  <p className="text-xs text-slate-400 font-mono truncate">{src.url}</p>

                  <div className="flex items-center gap-3 text-[11px] text-slate-400 pt-0.5">
                    <span>Domain: <strong className="text-slate-300">{src.domain}</strong></span>
                    <span>•</span>
                    <span className="font-mono text-[10px]">Hash: {src.content_hash.substring(0, 12)}...</span>
                    {src.published_date && (
                      <>
                        <span>•</span>
                        <span>Pub: {src.published_date}</span>
                      </>
                    )}
                  </div>

                  {isFailed && src.error_message && (
                    <p className="text-xs text-red-400 pt-1 font-mono">
                      Error: {src.error_message}
                    </p>
                  )}
                </div>

                <div className="flex items-center gap-2 self-end sm:self-auto">
                  <button
                    onClick={() => setInspectSource(src)}
                    className="p-1.5 rounded-lg text-slate-400 hover:text-cyan-300 hover:bg-[#161F30] transition-colors"
                    title="View Snapshot"
                  >
                    <Eye className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => handleDelete(src.id)}
                    className="p-1.5 rounded-lg text-slate-400 hover:text-rose-400 hover:bg-rose-950/30 transition-colors"
                    title="Delete Source"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            );
          })
        )}
      </div>

      {/* Snapshot Modal */}
      {inspectSource && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm">
          <div className="bg-[#111827] border border-[#1F293D] rounded-2xl p-6 max-w-2xl w-full max-h-[80vh] flex flex-col space-y-4">
            <div className="flex items-center justify-between pb-2 border-b border-[#1F293D]">
              <h3 className="text-sm font-bold text-slate-100 truncate">{inspectSource.title}</h3>
              <button 
                onClick={() => setInspectSource(null)}
                className="text-xs text-slate-400 hover:text-slate-200"
              >
                Close
              </button>
            </div>
            <div className="text-[11px] font-mono text-slate-400 space-y-1">
              <div>URL: {inspectSource.url}</div>
              <div>SHA-256: {inspectSource.content_hash}</div>
            </div>
            <div className="flex-1 overflow-y-auto p-4 rounded-xl bg-[#0B0F19] border border-[#1F293D] text-xs font-mono text-slate-300 leading-relaxed whitespace-pre-wrap select-text">
              {inspectSource.raw_text || 'No text stored.'}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};


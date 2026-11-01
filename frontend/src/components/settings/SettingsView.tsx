import React, { useState } from 'react';
import { 
  Settings, Cpu, ShieldCheck, Database, Key, 
  Sliders, Info, CheckCircle2
} from 'lucide-react';

export const SettingsView: React.FC = () => {
  const [provider, setProvider] = useState<'local_fallback' | 'gemini' | 'openai'>('local_fallback');
  const [apiKey, setApiKey] = useState('');
  const [refYear, setRefYear] = useState(2026);
  const [saved, setSaved] = useState(false);

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    setSaved(true);
    setTimeout(() => setSaved(false), 2500);
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto p-4 sm:p-6 lg:p-8">
      {/* Header */}
      <div className="p-5 rounded-2xl bg-[#111827] border border-[#1F293D] flex items-center gap-3">
        <div className="w-9 h-9 rounded-xl bg-slate-800 flex items-center justify-center border border-slate-700">
          <Settings className="w-5 h-5 text-cyan-400" />
        </div>
        <div>
          <h2 className="text-base font-bold text-slate-100">System Configuration & Epistemic Parameters</h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Manage provider-independent AI layers, deterministic fallbacks, and mathematical weighting rules.
          </p>
        </div>
      </div>

      <form onSubmit={handleSave} className="space-y-6">
        {/* AI Provider Layer */}
        <div className="p-5 rounded-2xl bg-[#111827] border border-[#1F293D] space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-bold font-mono uppercase text-slate-300 flex items-center gap-2">
              <Cpu className="w-4 h-4 text-cyan-400" />
              <span>AI & Inference Layer</span>
            </h3>
            <span className="px-2 py-0.5 rounded text-[10px] font-mono font-semibold bg-emerald-950 text-emerald-300 border border-emerald-800">
              OFFLINE READY
            </span>
          </div>

          <div className="space-y-3 text-xs">
            <p className="text-slate-400 leading-relaxed">
              NullSpace uses a provider-independent AI service layer. When no API key is supplied, it runs in <strong className="text-emerald-400">Deterministic Local Fallback Mode</strong> using linguistic markers, conservative heuristics, and synthetic templates without degrading core functionality.
            </p>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-1">
              <label className={`p-3 rounded-xl border cursor-pointer transition-all ${
                provider === 'local_fallback' ? 'bg-cyan-950/40 border-cyan-500 text-cyan-200' : 'bg-[#161F30] border-[#1F293D] text-slate-400'
              }`}>
                <input
                  type="radio"
                  name="provider"
                  value="local_fallback"
                  checked={provider === 'local_fallback'}
                  onChange={() => setProvider('local_fallback')}
                  className="sr-only"
                />
                <div className="font-bold text-xs mb-1">Local Fallback (Active)</div>
                <div className="text-[11px] opacity-80">100% deterministic, zero cost, instant offline fixtures.</div>
              </label>

              <label className={`p-3 rounded-xl border cursor-pointer transition-all ${
                provider === 'gemini' ? 'bg-cyan-950/40 border-cyan-500 text-cyan-200' : 'bg-[#161F30] border-[#1F293D] text-slate-400'
              }`}>
                <input
                  type="radio"
                  name="provider"
                  value="gemini"
                  checked={provider === 'gemini'}
                  onChange={() => setProvider('gemini')}
                  className="sr-only"
                />
                <div className="font-bold text-xs mb-1">Google Gemini API</div>
                <div className="text-[11px] opacity-80">Provider-independent LLM structured generation.</div>
              </label>

              <label className={`p-3 rounded-xl border cursor-pointer transition-all ${
                provider === 'openai' ? 'bg-cyan-950/40 border-cyan-500 text-cyan-200' : 'bg-[#161F30] border-[#1F293D] text-slate-400'
              }`}>
                <input
                  type="radio"
                  name="provider"
                  value="openai"
                  checked={provider === 'openai'}
                  onChange={() => setProvider('openai')}
                  className="sr-only"
                />
                <div className="font-bold text-xs mb-1">OpenAI API</div>
                <div className="text-[11px] opacity-80">GPT-4o structured JSON and NLI inference.</div>
              </label>
            </div>

            {provider !== 'local_fallback' && (
              <div className="pt-2">
                <label className="text-[11px] font-mono text-slate-400 block mb-1">
                  API Key for {provider.toUpperCase()}
                </label>
                <input
                  type="password"
                  value={apiKey}
                  onChange={(e) => setApiKey(e.target.value)}
                  placeholder="Paste optional API key..."
                  className="w-full bg-[#0B0F19] border border-[#1F293D] rounded-xl px-3.5 py-2 text-xs text-slate-200 focus:outline-none focus:border-cyan-500 font-mono"
                />
              </div>
            )}
          </div>
        </div>

        {/* Temporal & Scoring Parameters */}
        <div className="p-5 rounded-2xl bg-[#111827] border border-[#1F293D] space-y-4">
          <h3 className="text-xs font-bold font-mono uppercase text-slate-300 flex items-center gap-2">
            <Sliders className="w-4 h-4 text-cyan-400" />
            <span>Mathematical Audit Parameters</span>
          </h3>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
            <div>
              <label className="text-slate-400 block mb-1">Temporal Reference Year</label>
              <input
                type="number"
                value={refYear}
                onChange={(e) => setRefYear(parseInt(e.target.value))}
                className="w-full bg-[#0B0F19] border border-[#1F293D] rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-cyan-500 font-mono"
              />
              <span className="text-[10px] text-slate-400 mt-1 block">Active application cycle anchor</span>
            </div>

            <div>
              <label className="text-slate-400 block mb-1">Database Store</label>
              <div className="p-2.5 rounded-xl bg-[#0B0F19] border border-[#1F293D] font-mono text-xs text-emerald-400 flex items-center gap-2">
                <Database className="w-3.5 h-3.5" />
                <span>nullspace.db (SQLite with WAL)</span>
              </div>
              <span className="text-[10px] text-slate-400 mt-1 block">Zero-configuration local persistence</span>
            </div>
          </div>

          <div className="pt-2 border-t border-[#1F293D] text-[11px] text-slate-400 space-y-1">
            <div className="font-semibold text-slate-300">Entropy Priority Scoring Formula:</div>
            <div className="font-mono text-cyan-300 bg-[#0B0F19] p-2 rounded-lg border border-[#1F293D]">
              Score = min(100, (0.35 × Importance) + (0.30 × Missingness) + (0.20 × Contradiction) + (0.15 × Temporal))
            </div>
          </div>
        </div>

        <div className="flex items-center justify-end gap-3">
          {saved && (
            <span className="text-xs text-emerald-400 flex items-center gap-1 font-medium">
              <CheckCircle2 className="w-3.5 h-3.5" /> Settings saved successfully
            </span>
          )}
          <button
            type="submit"
            className="px-5 py-2 rounded-xl text-xs font-semibold bg-cyan-600 text-white hover:bg-cyan-500 transition-colors shadow-sm shadow-cyan-600/30"
          >
            Apply Configuration
          </button>
        </div>
      </form>
    </div>
  );
};


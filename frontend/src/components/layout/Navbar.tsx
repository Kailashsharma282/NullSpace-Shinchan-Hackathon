import React from 'react';
import { 
  Sparkles, ShieldAlert, Download, FileText, Play, PlusCircle, 
  RefreshCw, CheckCircle2, AlertTriangle, Layers
} from 'lucide-react';
import { ResearchProject, DashboardKPIs } from '../../types';
import { api } from '../../services/api';

interface NavbarProps {
  project: ResearchProject | null;
  kpis: DashboardKPIs | null;
  onLoadDemo: () => void;
  onNewResearch: () => void;
  onReAnalyze: () => void;
  isAnalyzing: boolean;
}

export const Navbar: React.FC<NavbarProps> = ({
  project,
  kpis,
  onLoadDemo,
  onNewResearch,
  onReAnalyze,
  isAnalyzing
}) => {
  const isDemo = project?.id.includes('demo');

  const handleExportPdf = () => {
    if (!project) return;
    window.open(api.getExportPdfUrl(project.id), '_blank');
  };

  const handleExportJson = () => {
    if (!project) return;
    window.open(api.getExportJsonUrl(project.id), '_blank');
  };

  return (
    <header className="sticky top-0 z-40 w-full border-b border-[#1F293D] bg-[#0B0F19]/90 backdrop-blur-md">
      {/* Synthetic Banner if demo */}
      {isDemo && (
        <div className="bg-gradient-to-r from-amber-950/80 via-amber-900/60 to-amber-950/80 border-b border-amber-500/30 px-4 py-1 text-center">
          <div className="flex items-center justify-center gap-2 text-xs font-semibold tracking-wider text-amber-300">
            <AlertTriangle className="w-3.5 h-3.5 text-amber-400 animate-pulse" />
            <span>SYNTHETIC DEMO DATA — NOT FOR REAL-WORLD DECISIONS</span>
            <span className="text-amber-400/60">|</span>
            <span className="text-slate-300 font-normal">Offline deterministic fixture with verified groundings</span>
          </div>
        </div>
      )}

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Left: Brand & Tagline */}
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2.5">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-cyan-500 to-indigo-600 flex items-center justify-center shadow-lg shadow-cyan-500/20">
              <Layers className="w-5 h-5 text-white" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-xl font-bold tracking-tight text-white font-mono">NullSpace</span>
                <span className="px-1.5 py-0.5 text-[10px] font-semibold tracking-wide uppercase bg-cyan-950 border border-cyan-800 text-cyan-300 rounded">
                  v1.0
                </span>
              </div>
              <p className="text-[11px] text-slate-400 -mt-0.5 font-medium">
                See What the Sources Don't Say
              </p>
            </div>
          </div>

          {/* Current Active Project Title */}
          {project && (
            <div className="hidden lg:flex items-center gap-2 pl-4 border-l border-[#1F293D]">
              <div className="max-w-md truncate">
                <span className="text-xs text-slate-400 font-mono">ACTIVE PROJECT:</span>
                <h2 className="text-sm font-semibold text-slate-200 truncate">{project.title}</h2>
              </div>
              <span className="px-2 py-0.5 text-xs font-medium rounded-full bg-slate-800 text-slate-300 border border-slate-700 capitalize">
                {project.domain}
              </span>
            </div>
          )}
        </div>

        {/* Right: Actions */}
        <div className="flex items-center gap-2 sm:gap-3">
          {/* 1-Click Scholarship Demo Button */}
          <button
            onClick={onLoadDemo}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-gradient-to-r from-amber-500/20 to-orange-500/20 border border-amber-500/40 text-amber-300 hover:bg-amber-500/30 transition-all shadow-sm shadow-amber-500/10 active:scale-95"
            title="Load instant offline scholarship demo with deliberate contradictions and dark spots"
          >
            <Sparkles className="w-3.5 h-3.5 text-amber-400" />
            <span>Load Scholarship Demo</span>
          </button>

          {/* New Research Button */}
          <button
            onClick={onNewResearch}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-[#161F30] border border-[#1F293D] text-slate-200 hover:bg-[#1D283A] hover:border-slate-600 transition-all active:scale-95"
          >
            <PlusCircle className="w-3.5 h-3.5 text-cyan-400" />
            <span className="hidden sm:inline">New Research</span>
          </button>

          {/* Re-Analyze */}
          {project && (
            <button
              onClick={onReAnalyze}
              disabled={isAnalyzing}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-cyan-950/80 border border-cyan-700 text-cyan-300 hover:bg-cyan-900 transition-all disabled:opacity-50 active:scale-95"
              title="Run full epistemic alignment & contradiction engine"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${isAnalyzing ? 'animate-spin' : ''}`} />
              <span className="hidden sm:inline">{isAnalyzing ? 'Analyzing...' : 'Run Audit'}</span>
            </button>
          )}

          {/* Export Dropdown / Buttons */}
          {project && (
            <div className="flex items-center gap-1.5 pl-2 border-l border-[#1F293D]">
              <button
                onClick={handleExportPdf}
                className="flex items-center gap-1 px-2.5 py-1.5 rounded-lg text-xs font-medium bg-[#111827] border border-[#1F293D] text-slate-300 hover:text-white hover:border-slate-600 transition-all"
                title="Download Epistemic Audit Report PDF"
              >
                <Download className="w-3.5 h-3.5 text-indigo-400" />
                <span className="hidden md:inline">PDF</span>
              </button>
              <button
                onClick={handleExportJson}
                className="flex items-center gap-1 px-2.5 py-1.5 rounded-lg text-xs font-medium bg-[#111827] border border-[#1F293D] text-slate-300 hover:text-white hover:border-slate-600 transition-all"
                title="Export complete analysis JSON"
              >
                <FileText className="w-3.5 h-3.5 text-emerald-400" />
                <span className="hidden md:inline">JSON</span>
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};


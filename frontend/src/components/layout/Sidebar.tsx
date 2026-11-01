import React from 'react';
import { 
  LayoutDashboard, GitFork, ShieldCheck, EyeOff, Scale, 
  Clock, CheckSquare, Globe, Settings, AlertCircle
} from 'lucide-react';
import { AnalysisResults, ResearchProject } from '../../types';

export type NavTab = 
  | 'overview' 
  | 'graph' 
  | 'evidence' 
  | 'darkspots' 
  | 'conflicts' 
  | 'temporal' 
  | 'checklist' 
  | 'sources' 
  | 'settings';

interface SidebarProps {
  activeTab: NavTab;
  onSelectTab: (tab: NavTab) => void;
  results: AnalysisResults | null;
  projects: ResearchProject[];
  activeProjectId: string | null;
  onSelectProject: (id: string) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  activeTab,
  onSelectTab,
  results,
  projects,
  activeProjectId,
  onSelectProject,
}) => {
  const darkSpotsCount = results?.kpis?.dark_spots_count || 0;
  const conflictsCount = results?.kpis?.detected_conflicts_count || 0;
  const staleCount = results?.kpis?.stale_claims_count || 0;
  const checklistCount = results?.checklist?.filter(c => !c.is_resolved).length || 0;

  const navItems = [
    {
      id: 'overview' as NavTab,
      label: 'Overview',
      icon: LayoutDashboard,
      badge: null,
      desc: 'KPIs & Epistemic Matrix'
    },
    {
      id: 'graph' as NavTab,
      label: 'Decision Graph',
      icon: GitFork,
      badge: results?.kpis?.total_requirements || null,
      desc: 'Counterfactual Schema'
    },
    {
      id: 'evidence' as NavTab,
      label: 'Evidence Vault',
      icon: ShieldCheck,
      badge: null,
      desc: 'Source Fact Grounding'
    },
    {
      id: 'darkspots' as NavTab,
      label: 'Dark Spots',
      icon: EyeOff,
      badge: darkSpotsCount > 0 ? darkSpotsCount : null,
      badgeColor: 'bg-rose-500/20 text-rose-300 border-rose-500/30',
      desc: 'Missing Information'
    },
    {
      id: 'conflicts' as NavTab,
      label: 'Contradictions',
      icon: Scale,
      badge: conflictsCount > 0 ? conflictsCount : null,
      badgeColor: 'bg-red-500/20 text-red-300 border-red-500/30',
      desc: 'Cross-Source Conflicts'
    },
    {
      id: 'temporal' as NavTab,
      label: 'Temporal Radar',
      icon: Clock,
      badge: staleCount > 0 ? staleCount : null,
      badgeColor: 'bg-amber-500/20 text-amber-300 border-amber-500/30',
      desc: 'Cycle & Staleness Audit'
    },
    {
      id: 'checklist' as NavTab,
      label: 'Verification Checklist',
      icon: CheckSquare,
      badge: checklistCount > 0 ? checklistCount : null,
      badgeColor: 'bg-cyan-500/20 text-cyan-300 border-cyan-500/30',
      desc: 'Entropy-Ranked Priority'
    },
    {
      id: 'sources' as NavTab,
      label: 'Sources',
      icon: Globe,
      badge: null,
      desc: 'SSRF-Safe Ingestion'
    },
    {
      id: 'settings' as NavTab,
      label: 'Settings',
      icon: Settings,
      badge: null,
      desc: 'Heuristics & Config'
    },
  ];

  return (
    <aside className="w-64 flex-shrink-0 border-r border-[#1F293D] bg-[#0E1524] flex flex-col justify-between min-h-[calc(100vh-4rem)]">
      <div className="p-4 space-y-6">
        {/* Project Switcher */}
        {projects.length > 0 && (
          <div>
            <label className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block mb-1.5 font-mono">
              Research Project
            </label>
            <select
              value={activeProjectId || ''}
              onChange={(e) => onSelectProject(e.target.value)}
              className="w-full bg-[#161F30] border border-[#1F293D] rounded-lg px-2.5 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-cyan-500 transition-colors"
            >
              {projects.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.title.length > 28 ? p.title.substring(0, 28) + '...' : p.title}
                </option>
              ))}
            </select>
          </div>
        )}

        {/* Navigation items */}
        <nav className="space-y-1">
          <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider px-2 font-mono">
            Epistemic Engine
          </span>
          <div className="pt-1.5 space-y-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => onSelectTab(item.id)}
                  className={`w-full flex items-center justify-between px-3 py-2 rounded-lg text-xs font-medium transition-all group ${
                    isActive 
                      ? 'bg-cyan-500/10 text-cyan-300 border border-cyan-500/30 shadow-sm shadow-cyan-500/10' 
                      : 'text-slate-400 hover:text-slate-200 hover:bg-[#161F30]/60 border border-transparent'
                  }`}
                >
                  <div className="flex items-center gap-2.5 min-w-0">
                    <Icon className={`w-4 h-4 flex-shrink-0 ${isActive ? 'text-cyan-400' : 'text-slate-400 group-hover:text-slate-300'}`} />
                    <span className="truncate">{item.label}</span>
                  </div>
                  {item.badge !== null && (
                    <span className={`px-1.5 py-0.2 rounded-full text-[10px] font-mono border ${item.badgeColor || 'bg-slate-800 text-slate-300 border-slate-700'}`}>
                      {item.badge}
                    </span>
                  )}
                </button>
              );
            })}
          </div>
        </nav>
      </div>

      {/* Epistemic Principle Callout */}
      <div className="p-4 border-t border-[#1F293D] bg-[#0B0F19]/60">
        <div className="p-3 rounded-lg bg-[#111827] border border-[#1F293D] text-[11px] space-y-1.5">
          <div className="flex items-center gap-1.5 text-cyan-400 font-semibold font-mono">
            <AlertCircle className="w-3.5 h-3.5" />
            <span>Counterfactual Rule</span>
          </div>
          <p className="text-slate-400 leading-relaxed text-[11px]">
            Decision graphs are generated <strong className="text-slate-200">prior</strong> to reading sources. Omitted requirements create <strong className="text-rose-400">Dark Spots</strong>.
          </p>
        </div>
      </div>
    </aside>
  );
};


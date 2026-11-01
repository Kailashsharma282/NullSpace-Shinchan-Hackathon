import React, { useState, useEffect } from 'react';
import { QueryClient, QueryClientProvider, useQuery, useMutation } from '@tanstack/react-query';
import { Navbar } from './components/layout/Navbar';
import { Sidebar, NavTab } from './components/layout/Sidebar';
import { OverviewView } from './components/dashboard/OverviewView';
import { DecisionGraphView } from './components/ontology/DecisionGraphView';
import { EvidenceVaultView } from './components/evidence/EvidenceVaultView';
import { DarkSpotsView } from './components/darkspots/DarkSpotsView';
import { ContradictionMatrixView } from './components/conflicts/ContradictionMatrixView';
import { TemporalRadarView } from './components/temporal/TemporalRadarView';
import { ChecklistView } from './components/checklist/ChecklistView';
import { SourcesManagerView } from './components/sources/SourcesManagerView';
import { SettingsView } from './components/settings/SettingsView';
import { InitiateResearchModal } from './components/dashboard/InitiateResearchModal';
import { api } from './services/api';
import { ResearchProject, AnalysisResults } from './types';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      staleTime: 5000,
    },
  },
});

function NullSpaceDashboard() {
  const [activeTab, setActiveTab] = useState<NavTab>('overview');
  const [activeProjectId, setActiveProjectId] = useState<string | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  // 1. Fetch all projects
  const { 
    data: projects = [], 
    refetch: refetchProjects,
    isLoading: isLoadingProjects 
  } = useQuery({
    queryKey: ['projects'],
    queryFn: api.getProjects,
  });

  // 2. Select initial project or load demo if none exist
  useEffect(() => {
    if (projects.length > 0 && !activeProjectId) {
      setActiveProjectId(projects[0].id);
    }
  }, [projects, activeProjectId]);

  // 3. Fetch active project details
  const { 
    data: projectDetail = null, 
    refetch: refetchProjectDetail 
  } = useQuery({
    queryKey: ['project', activeProjectId],
    queryFn: () => (activeProjectId ? api.getProject(activeProjectId) : null),
    enabled: !!activeProjectId,
  });

  // 4. Fetch analysis results
  const { 
    data: results = null, 
    refetch: refetchResults,
    isLoading: isLoadingResults 
  } = useQuery({
    queryKey: ['results', activeProjectId],
    queryFn: () => (activeProjectId ? api.getAnalysisResults(activeProjectId) : null),
    enabled: !!activeProjectId,
  });

  const handleRefreshAll = () => {
    refetchProjects();
    refetchProjectDetail();
    refetchResults();
  };

  // One-Click Scholarship Demo loader
  const handleLoadDemo = async () => {
    setIsAnalyzing(true);
    try {
      const res = await api.loadScholarshipDemo();
      await refetchProjects();
      setActiveProjectId(res.research_id);
      setActiveTab('overview');
      await refetchResults();
    } catch (err) {
      alert('Failed to load demo: ' + String(err));
    } finally {
      setIsAnalyzing(false);
    }
  };

  // Re-run Epistemic Analysis Pipeline
  const handleReAnalyze = async () => {
    if (!activeProjectId) return;
    setIsAnalyzing(true);
    try {
      await api.runAnalysis(activeProjectId);
      await refetchResults();
    } catch (err) {
      alert('Analysis failed: ' + String(err));
    } finally {
      setIsAnalyzing(false);
    }
  };

  const activeProject = projects.find(p => p.id === activeProjectId) || projectDetail;

  return (
    <div className="min-h-screen flex flex-col bg-[#0B0F19] text-slate-100">
      {/* Top Navbar */}
      <Navbar
        project={activeProject}
        kpis={results?.kpis || null}
        onLoadDemo={handleLoadDemo}
        onNewResearch={() => setIsModalOpen(true)}
        onReAnalyze={handleReAnalyze}
        isAnalyzing={isAnalyzing}
      />

      {/* Main Workspace Body */}
      <div className="flex-1 flex flex-col md:flex-row overflow-hidden">
        {/* Left Navigation Sidebar */}
        <Sidebar
          activeTab={activeTab}
          onSelectTab={setActiveTab}
          results={results}
          projects={projects}
          activeProjectId={activeProjectId}
          onSelectProject={(id) => {
            setActiveProjectId(id);
            setActiveTab('overview');
          }}
        />

        {/* Center Canvas View */}
        <main className="flex-1 overflow-y-auto min-h-[calc(100vh-4rem)] pb-12">
          {isLoadingProjects && !activeProject ? (
            <div className="flex items-center justify-center h-64 text-slate-400 text-sm">
              Connecting to Epistemic Engine...
            </div>
          ) : !activeProjectId ? (
            <div className="flex flex-col items-center justify-center p-16 text-center max-w-md mx-auto space-y-4">
              <div className="w-14 h-14 rounded-2xl bg-cyan-950/60 border border-cyan-800 flex items-center justify-center text-cyan-400">
                <span className="font-mono text-xl font-bold">∅</span>
              </div>
              <h2 className="text-lg font-bold text-slate-200">Welcome to NullSpace</h2>
              <p className="text-xs text-slate-400 leading-relaxed">
                Discover what unstructured sources don't say. Click below to load the synthetic scholarship demo or define your own research goal.
              </p>
              <div className="flex items-center gap-3 pt-2">
                <button
                  onClick={handleLoadDemo}
                  className="px-4 py-2 rounded-xl text-xs font-semibold bg-amber-500/20 text-amber-300 border border-amber-500/40 hover:bg-amber-500/30 transition-all shadow-md shadow-amber-500/10"
                >
                  Load Scholarship Demo
                </button>
                <button
                  onClick={() => setIsModalOpen(true)}
                  className="px-4 py-2 rounded-xl text-xs font-medium bg-[#161F30] border border-[#1F293D] text-slate-200 hover:text-white transition-all"
                >
                  Create New Research
                </button>
              </div>
            </div>
          ) : (
            <>
              {activeTab === 'overview' && (
                <OverviewView results={results} onNavigate={setActiveTab} />
              )}
              {activeTab === 'graph' && (
                <DecisionGraphView
                  researchId={activeProjectId}
                  requirements={projectDetail?.requirements || []}
                  onRefresh={handleRefreshAll}
                />
              )}
              {activeTab === 'evidence' && (
                <EvidenceVaultView
                  results={results}
                  sources={projectDetail?.sources || []}
                />
              )}
              {activeTab === 'darkspots' && (
                <DarkSpotsView darkSpots={results?.dark_spots || []} />
              )}
              {activeTab === 'conflicts' && (
                <ContradictionMatrixView
                  conflicts={results?.conflicts || []}
                  onRefresh={handleRefreshAll}
                />
              )}
              {activeTab === 'temporal' && (
                <TemporalRadarView temporalAudits={results?.temporal_audits || []} />
              )}
              {activeTab === 'checklist' && (
                <ChecklistView
                  items={results?.checklist || []}
                  onRefresh={handleRefreshAll}
                />
              )}
              {activeTab === 'sources' && (
                <SourcesManagerView
                  researchId={activeProjectId}
                  sources={projectDetail?.sources || []}
                  onRefresh={handleRefreshAll}
                  onRunAudit={handleReAnalyze}
                  isAnalyzing={isAnalyzing}
                />
              )}
              {activeTab === 'settings' && <SettingsView />}
            </>
          )}
        </main>
      </div>

      {/* New Research Initiation Modal */}
      <InitiateResearchModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onCreated={async (newId) => {
          await refetchProjects();
          setActiveProjectId(newId);
          setActiveTab('graph');
          await refetchProjectDetail();
        }}
      />
    </div>
  );
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <NullSpaceDashboard />
    </QueryClientProvider>
  );
}


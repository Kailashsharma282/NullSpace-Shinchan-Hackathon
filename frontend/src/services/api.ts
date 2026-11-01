import { 
  ResearchProject, AnalysisResults, RequirementNode, SourceDocument, 
  ConflictRecord, ChecklistItem 
} from '../types';

const API_BASE = '/api';

export const api = {
  async getHealth(): Promise<{ status: string; service: string }> {
    const res = await fetch(`${API_BASE}/health`);
    if (!res.ok) throw new Error('Health check failed');
    return res.json();
  },

  async getProjects(): Promise<ResearchProject[]> {
    const res = await fetch(`${API_BASE}/research`);
    if (!res.ok) throw new Error('Failed to load projects');
    return res.json();
  },

  async getProject(id: string): Promise<ResearchProject> {
    const res = await fetch(`${API_BASE}/research/${id}`);
    if (!res.ok) throw new Error('Failed to load project details');
    return res.json();
  },

  async createProject(data: { title: string; objective: string; domain?: string }): Promise<ResearchProject> {
    const res = await fetch(`${API_BASE}/research`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error('Failed to create research project');
    return res.json();
  },

  async deleteProject(id: string): Promise<void> {
    const res = await fetch(`${API_BASE}/research/${id}`, { method: 'DELETE' });
    if (!res.ok) throw new Error('Failed to delete project');
  },

  async loadScholarshipDemo(): Promise<{ research_id: string; title: string }> {
    const res = await fetch(`${API_BASE}/demo/load`, { method: 'POST' });
    if (!res.ok) throw new Error('Failed to load scholarship demo');
    return res.json();
  },

  async addRequirement(researchId: string, data: { name: string; description: string; mandatory: boolean; importance: number }): Promise<RequirementNode> {
    const res = await fetch(`${API_BASE}/research/${researchId}/requirements`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error('Failed to add requirement');
    return res.json();
  },

  async updateRequirement(researchId: string, nodeId: string, data: Partial<RequirementNode>): Promise<RequirementNode> {
    const res = await fetch(`${API_BASE}/research/${researchId}/requirements/${nodeId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error('Failed to update requirement');
    return res.json();
  },

  async deleteRequirement(researchId: string, nodeId: string): Promise<void> {
    const res = await fetch(`${API_BASE}/research/${researchId}/requirements/${nodeId}`, { method: 'DELETE' });
    if (!res.ok) throw new Error('Failed to delete requirement');
  },

  async addSourceUrl(researchId: string, url: string): Promise<SourceDocument> {
    const res = await fetch(`${API_BASE}/research/${researchId}/sources`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url }),
    });
    if (!res.ok) throw new Error('Failed to add source URL');
    return res.json();
  },

  async addManualSource(researchId: string, data: { title: string; text: string; published_date?: string }): Promise<SourceDocument> {
    const res = await fetch(`${API_BASE}/research/${researchId}/sources/manual`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error('Failed to add manual source');
    return res.json();
  },

  async deleteSource(researchId: string, sourceId: string): Promise<void> {
    const res = await fetch(`${API_BASE}/research/${researchId}/sources/${sourceId}`, { method: 'DELETE' });
    if (!res.ok) throw new Error('Failed to delete source');
  },

  async runAnalysis(researchId: string): Promise<AnalysisResults> {
    const res = await fetch(`${API_BASE}/research/${researchId}/analyze`, { method: 'POST' });
    if (!res.ok) throw new Error('Failed to run analysis pipeline');
    return res.json();
  },

  async getAnalysisResults(researchId: string): Promise<AnalysisResults> {
    const res = await fetch(`${API_BASE}/research/${researchId}/results`);
    if (!res.ok) throw new Error('Failed to load analysis results');
    return res.json();
  },

  async updateConflictStatus(conflictId: string, status: string, userNotes?: string): Promise<ConflictRecord> {
    const res = await fetch(`${API_BASE}/conflicts/${conflictId}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status, user_notes: userNotes }),
    });
    if (!res.ok) throw new Error('Failed to update conflict status');
    return res.json();
  },

  async updateChecklistStatus(itemId: string, isResolved: boolean): Promise<ChecklistItem> {
    const res = await fetch(`${API_BASE}/checklist/${itemId}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ is_resolved: isResolved }),
    });
    if (!res.ok) throw new Error('Failed to update checklist item');
    return res.json();
  },

  getExportJsonUrl(researchId: string): string {
    return `${API_BASE}/research/${researchId}/export/json`;
  },

  getExportPdfUrl(researchId: string): string {
    return `${API_BASE}/research/${researchId}/export/pdf`;
  }
};


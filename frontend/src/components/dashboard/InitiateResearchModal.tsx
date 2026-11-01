import React, { useState } from 'react';
import { 
  X, PlusCircle, Sparkles, BookOpen, Layers, 
  HelpCircle, ArrowRight
} from 'lucide-react';
import { api } from '../../services/api';

interface InitiateResearchModalProps {
  isOpen: boolean;
  onClose: () => void;
  onCreated: (projectId: string) => void;
}

export const InitiateResearchModal: React.FC<InitiateResearchModalProps> = ({
  isOpen,
  onClose,
  onCreated
}) => {
  const [title, setTitle] = useState('');
  const [objective, setObjective] = useState('');
  const [domain, setDomain] = useState('scholarship');
  const [isLoading, setIsLoading] = useState(false);

  if (!isOpen) return null;

  const exampleChips = [
    {
      title: 'State Postgraduate Merit Scholarship',
      obj: 'Find all eligibility requirements, family income limits, renewal policies, and required documents for applying for state postgraduate scholarship schemes.',
      domain: 'scholarship'
    },
    {
      title: 'Schengen Student Visa Requirements',
      obj: 'Find all mandatory financial solvency proofs, biometrics, required documents, and appeal procedures for university student visa application.',
      domain: 'visa'
    },
    {
      title: 'Public Infrastructure Vendor Procurement',
      obj: 'Identify technical qualification thresholds, EMD deposit exemptions, performance guarantees, and closing deadlines for municipal procurement tenders.',
      domain: 'procurement'
    }
  ];

  const handleApplyChip = (chip: typeof exampleChips[0]) => {
    setTitle(chip.title);
    setObjective(chip.obj);
    setDomain(chip.domain);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim() || !objective.trim()) return;
    setIsLoading(true);
    try {
      const proj = await api.createProject({
        title: title.trim(),
        objective: objective.trim(),
        domain: domain
      });
      onCreated(proj.id);
      onClose();
    } catch (err) {
      alert('Failed to initiate research: ' + String(err));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-sm">
      <div className="bg-[#111827] border border-[#1F293D] rounded-2xl p-6 max-w-xl w-full shadow-2xl space-y-5 animate-in fade-in zoom-in-95 duration-150">
        <div className="flex items-center justify-between pb-3 border-b border-[#1F293D]">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-cyan-950 border border-cyan-800 flex items-center justify-center">
              <Layers className="w-4 h-4 text-cyan-400" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-slate-100">Initiate Epistemic Research</h3>
              <p className="text-[11px] text-slate-400">Stage 1: Define Goal & Counterfactual Ontology</p>
            </div>
          </div>
          <button 
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Quick Example Chips */}
        <div>
          <span className="text-[10px] font-mono font-semibold text-slate-400 uppercase tracking-wider block mb-1.5">
            Quick Domain Presets
          </span>
          <div className="flex flex-wrap gap-1.5">
            {exampleChips.map((chip, i) => (
              <button
                key={i}
                type="button"
                onClick={() => handleApplyChip(chip)}
                className="px-2.5 py-1 rounded-lg text-[11px] font-medium bg-[#161F30] border border-[#1F293D] text-slate-300 hover:text-cyan-300 hover:border-cyan-500/40 transition-colors"
              >
                {chip.title}
              </button>
            ))}
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="text-xs font-medium text-slate-300 block mb-1">Research Project Title</label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="e.g. National Scholarship Portal Guidelines Audit"
              className="w-full bg-[#0B0F19] border border-[#1F293D] rounded-xl px-3.5 py-2 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
              required
            />
          </div>

          <div>
            <label className="text-xs font-medium text-slate-300 block mb-1">Domain Taxonomy</label>
            <select
              value={domain}
              onChange={(e) => setDomain(e.target.value)}
              className="w-full bg-[#0B0F19] border border-[#1F293D] rounded-xl px-3.5 py-2 text-xs text-slate-200 focus:outline-none focus:border-cyan-500 capitalize"
            >
              <option value="scholarship">Scholarships & Fellowships</option>
              <option value="visa">Visa & Immigration</option>
              <option value="procurement">Government Procurement & Tenders</option>
              <option value="admissions">University Admissions & Courses</option>
              <option value="general">General Regulatory / Policy Scheme</option>
            </select>
          </div>

          <div>
            <label className="text-xs font-medium text-slate-300 block mb-1">
              Research Objective & Decision Criteria
            </label>
            <textarea
              value={objective}
              onChange={(e) => setObjective(e.target.value)}
              placeholder="State what information you need to uncover across multiple sources..."
              rows={3}
              className="w-full bg-[#0B0F19] border border-[#1F293D] rounded-xl px-3.5 py-2 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
              required
            />
          </div>

          <div className="p-3 rounded-xl bg-cyan-950/30 border border-cyan-800/40 text-[11px] text-cyan-300 leading-relaxed">
            <strong>Stage 2 Automation:</strong> Submitting will automatically generate the mandatory Decision Requirement Graph <em>before</em> any source URLs are added.
          </div>

          <div className="flex items-center justify-end gap-2 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded-xl text-xs font-medium text-slate-400 hover:text-slate-200"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isLoading}
              className="px-5 py-2 rounded-xl text-xs font-semibold bg-cyan-600 text-white hover:bg-cyan-500 transition-colors disabled:opacity-50 flex items-center gap-1.5 shadow-md shadow-cyan-600/30"
            >
              <Sparkles className="w-3.5 h-3.5" />
              <span>{isLoading ? 'Synthesizing Ontology...' : 'Create & Generate Ontology'}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};


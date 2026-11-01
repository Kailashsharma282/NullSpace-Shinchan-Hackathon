import React, { useState } from 'react';
import { 
  GitFork, Plus, Trash2, Edit2, Check, X, Shield, Star, 
  HelpCircle, AlertCircle, ArrowUpDown
} from 'lucide-react';
import { RequirementNode } from '../../types';
import { api } from '../../services/api';

interface DecisionGraphViewProps {
  researchId: string;
  requirements: RequirementNode[];
  onRefresh: () => void;
}

export const DecisionGraphView: React.FC<DecisionGraphViewProps> = ({
  researchId,
  requirements,
  onRefresh
}) => {
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editName, setEditName] = useState('');
  const [editDesc, setEditDesc] = useState('');
  const [editImportance, setEditImportance] = useState(5);
  const [editMandatory, setEditMandatory] = useState(true);

  const [isAdding, setIsAdding] = useState(false);
  const [newName, setNewName] = useState('');
  const [newDesc, setNewDesc] = useState('');
  const [newImportance, setNewImportance] = useState(5);
  const [newMandatory, setNewMandatory] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const startEdit = (req: RequirementNode) => {
    setEditingId(req.id);
    setEditName(req.name);
    setEditDesc(req.description);
    setEditImportance(req.importance);
    setEditMandatory(req.mandatory);
  };

  const cancelEdit = () => {
    setEditingId(null);
  };

  const saveEdit = async (reqId: string) => {
    try {
      await api.updateRequirement(researchId, reqId, {
        name: editName,
        description: editDesc,
        importance: editImportance,
        mandatory: editMandatory
      });
      setEditingId(null);
      onRefresh();
    } catch (err) {
      alert('Failed to update requirement: ' + String(err));
    }
  };

  const handleDelete = async (reqId: string) => {
    if (!confirm('Are you sure you want to remove this requirement node?')) return;
    try {
      await api.deleteRequirement(researchId, reqId);
      onRefresh();
    } catch (err) {
      alert('Failed to delete requirement: ' + String(err));
    }
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newName.trim() || !newDesc.trim()) return;
    setIsSubmitting(true);
    try {
      await api.addRequirement(researchId, {
        name: newName.trim(),
        description: newDesc.trim(),
        importance: newImportance,
        mandatory: newMandatory
      });
      setNewName('');
      setNewDesc('');
      setIsAdding(false);
      onRefresh();
    } catch (err) {
      alert('Failed to add requirement: ' + String(err));
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto p-4 sm:p-6 lg:p-8">
      {/* Header Banner */}
      <div className="p-5 rounded-2xl bg-[#111827] border border-cyan-500/30 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <GitFork className="w-5 h-5 text-cyan-400" />
            <h2 className="text-base font-bold text-slate-100">Counterfactual Decision Requirement Graph</h2>
          </div>
          <p className="text-xs text-slate-400 mt-1 max-w-2xl leading-relaxed">
            This graph defines all mandatory criteria that a decision-maker must evaluate. 
            <strong className="text-cyan-300"> Crucially, it exists independently of and prior to any source ingestion.</strong> If ingested sources fail to provide evidence for a mandatory node, a Digital Dark Spot is flagged.
          </p>
        </div>

        <button
          onClick={() => setIsAdding(!isAdding)}
          className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-semibold bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 hover:bg-cyan-500/30 transition-all self-start md:self-auto"
        >
          <Plus className="w-4 h-4" />
          <span>Add Custom Requirement</span>
        </button>
      </div>

      {/* Add New Requirement Modal / Inline Form */}
      {isAdding && (
        <form onSubmit={handleCreate} className="p-5 rounded-2xl bg-[#161F30] border border-[#1F293D] space-y-4">
          <h3 className="text-xs font-bold font-mono uppercase text-cyan-400">Add Decision Requirement Node</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="text-xs font-medium text-slate-300 block mb-1">Requirement Name</label>
              <input
                type="text"
                value={newName}
                onChange={(e) => setNewName(e.target.value)}
                placeholder="e.g. Parental Income Limit"
                className="w-full bg-[#0B0F19] border border-[#1F293D] rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
                required
              />
            </div>
            <div>
              <label className="text-xs font-medium text-slate-300 block mb-1">Importance (1 to 5)</label>
              <div className="flex items-center gap-2">
                <input
                  type="range"
                  min="1"
                  max="5"
                  value={newImportance}
                  onChange={(e) => setNewImportance(parseInt(e.target.value))}
                  className="w-full accent-cyan-400"
                />
                <span className="font-mono font-bold text-xs text-cyan-300 w-6 text-center">{newImportance}</span>
              </div>
            </div>
          </div>

          <div>
            <label className="text-xs font-medium text-slate-300 block mb-1">Evaluation Description & Guiding Question</label>
            <textarea
              value={newDesc}
              onChange={(e) => setNewDesc(e.target.value)}
              placeholder="What specific factual assertion or rule must be evaluated?"
              rows={2}
              className="w-full bg-[#0B0F19] border border-[#1F293D] rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
              required
            />
          </div>

          <div className="flex items-center justify-between pt-2">
            <label className="flex items-center gap-2 cursor-pointer text-xs text-slate-300">
              <input
                type="checkbox"
                checked={newMandatory}
                onChange={(e) => setNewMandatory(e.target.checked)}
                className="rounded border-[#1F293D] bg-[#0B0F19] text-cyan-500 focus:ring-0"
              />
              <span>Mandatory Requirement (Triggers Dark Spot if ungrounded)</span>
            </label>

            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={() => setIsAdding(false)}
                className="px-3 py-1.5 rounded-lg text-xs font-medium text-slate-400 hover:text-slate-200 bg-transparent"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={isSubmitting}
                className="px-4 py-1.5 rounded-lg text-xs font-semibold bg-cyan-600 text-white hover:bg-cyan-500 transition-colors disabled:opacity-50"
              >
                {isSubmitting ? 'Adding...' : 'Save Node'}
              </button>
            </div>
          </div>
        </form>
      )}

      {/* Requirement Nodes List */}
      <div className="space-y-3">
        {requirements.map((req, index) => {
          const isEditing = editingId === req.id;

          if (isEditing) {
            return (
              <div key={req.id} className="p-4 rounded-xl bg-[#161F30] border border-cyan-500/50 space-y-3">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  <input
                    type="text"
                    value={editName}
                    onChange={(e) => setEditName(e.target.value)}
                    className="bg-[#0B0F19] border border-[#1F293D] rounded px-3 py-1.5 text-xs text-slate-200"
                  />
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-slate-400">Importance:</span>
                    <input
                      type="range"
                      min="1"
                      max="5"
                      value={editImportance}
                      onChange={(e) => setEditImportance(parseInt(e.target.value))}
                      className="accent-cyan-400 flex-1"
                    />
                    <span className="font-mono text-xs text-cyan-300">{editImportance}</span>
                  </div>
                </div>

                <textarea
                  value={editDesc}
                  onChange={(e) => setEditDesc(e.target.value)}
                  rows={2}
                  className="w-full bg-[#0B0F19] border border-[#1F293D] rounded px-3 py-1.5 text-xs text-slate-200"
                />

                <div className="flex items-center justify-between">
                  <label className="flex items-center gap-2 text-xs text-slate-300">
                    <input
                      type="checkbox"
                      checked={editMandatory}
                      onChange={(e) => setEditMandatory(e.target.checked)}
                      className="rounded border-[#1F293D] text-cyan-500"
                    />
                    <span>Mandatory</span>
                  </label>

                  <div className="flex items-center gap-2">
                    <button
                      onClick={cancelEdit}
                      className="p-1.5 rounded hover:bg-slate-800 text-slate-400"
                    >
                      <X className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => saveEdit(req.id)}
                      className="p-1.5 rounded bg-cyan-600 hover:bg-cyan-500 text-white"
                    >
                      <Check className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>
            );
          }

          return (
            <div
              key={req.id}
              className="p-4 rounded-xl bg-[#111827] border border-[#1F293D] hover:border-slate-600 transition-all flex flex-col sm:flex-row sm:items-center justify-between gap-3"
            >
              <div className="space-y-1 max-w-3xl">
                <div className="flex items-center gap-2">
                  <span className="font-mono text-xs font-bold text-slate-400">#{index + 1}</span>
                  <h4 className="text-sm font-semibold text-slate-100">{req.name}</h4>
                  {req.mandatory ? (
                    <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-rose-500/10 text-rose-300 border border-rose-500/30">
                      Mandatory
                    </span>
                  ) : (
                    <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-slate-800 text-slate-400 border border-slate-700">
                      Optional
                    </span>
                  )}
                  <div className="flex items-center gap-0.5 text-amber-400 text-xs ml-2">
                    {Array.from({ length: req.importance }).map((_, i) => (
                      <Star key={i} className="w-3 h-3 fill-amber-400" />
                    ))}
                  </div>
                </div>
                <p className="text-xs text-slate-400 leading-relaxed pl-6">{req.description}</p>
              </div>

              <div className="flex items-center gap-2 self-end sm:self-auto">
                <button
                  onClick={() => startEdit(req)}
                  className="p-1.5 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-[#161F30] transition-colors"
                  title="Edit requirement"
                >
                  <Edit2 className="w-3.5 h-3.5" />
                </button>
                <button
                  onClick={() => handleDelete(req.id)}
                  className="p-1.5 rounded-lg text-slate-400 hover:text-rose-400 hover:bg-rose-950/30 transition-colors"
                  title="Delete requirement"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};


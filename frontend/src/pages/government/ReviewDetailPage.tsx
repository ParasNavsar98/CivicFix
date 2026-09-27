import React, { useEffect, useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { api } from '../../services/api';
import { Problem, DomainType, SeverityLevel } from '../../types';
import { AIInsightCard } from '../../components/common/AIInsightCard';
import { Modal } from '../../components/common/Modal';
import { StatusBadge } from '../../components/common/StatusBadge';
import { SeverityBadge } from '../../components/common/SeverityBadge';
import { ArrowLeft, Check, Edit3, HelpCircle, AlertOctagon, XCircle, MapPin, Calendar, User, Sparkles } from 'lucide-react';
import { Skeleton } from '../../components/common/Skeleton';

export const ReviewDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [problem, setProblem] = useState<Problem | null>(null);
  const [loading, setLoading] = useState(true);

  // Correction Modal state
  const [showCorrectModal, setShowCorrectModal] = useState(false);
  const [corrDomain, setCorrDomain] = useState<DomainType>('Sanitation');
  const [corrSubcategory, setCorrSubcategory] = useState('Toilets');
  const [corrSeverity, setCorrSeverity] = useState<SeverityLevel>('HIGH');
  const [corrReason, setCorrReason] = useState('');

  useEffect(() => {
    if (id) {
      api.getProblemById(id).then((res) => {
        setProblem(res || null);
        if (res?.primaryDomain) setCorrDomain(res.primaryDomain);
        if (res?.subcategory) setCorrSubcategory(res.subcategory);
        if (res?.severity) setCorrSeverity(res.severity);
        setLoading(false);
      });
    }
  }, [id]);

  if (loading) return <Skeleton className="h-96 rounded-3xl" />;
  if (!problem) return <div className="p-8 text-white">Problem not found.</div>;

  const handleAccept = async () => {
    const updated = await api.executeReviewerAction(problem.problemId, 'ACCEPT');
    setProblem({ ...updated });
    alert('AI Classification accepted successfully!');
    navigate('/government/review');
  };

  const handleCorrectSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!corrReason.trim()) return;

    const updated = await api.executeReviewerAction(problem.problemId, 'CORRECT', {
      primaryDomain: corrDomain,
      subcategory: corrSubcategory,
      severity: corrSeverity,
      reason: corrReason,
    });
    setProblem({ ...updated });
    setShowCorrectModal(false);
    alert('Category correction saved and new reviewer version snapshot created.');
    navigate('/government/review');
  };

  return (
    <div className="space-y-6 animate-in fade-in">
      {/* Top Header */}
      <div className="flex items-center justify-between">
        <Link to="/government/review" className="text-xs text-[#66736F] hover:text-[#17332F] transition flex items-center gap-1">
          <ArrowLeft className="w-4 h-4" /> Back to Review Queue
        </Link>
        <div className="flex items-center gap-2">
          <span className="text-xs font-mono font-bold text-[#6A5ACD]">{problem.problemId}</span>
          <StatusBadge status={problem.status} />
        </div>
      </div>

      {/* Reviewer Action Bar */}
      <div className="glass-card rounded-2xl p-4 flex flex-wrap items-center justify-between gap-3 border border-[#B7791F]/30 bg-[#FFFDF5] shadow-sm">
        <div className="text-xs font-semibold text-[#B7791F] flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-[#B7791F]" />
          <span>Reviewer Controls (Human-in-the-Loop Decision Authority)</span>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <button
            onClick={handleAccept}
            className="px-4 py-2 rounded-xl text-xs font-bold bg-[#034F46] text-white hover:bg-[#0F766E] transition flex items-center gap-1.5 shadow-md cursor-pointer"
          >
            <Check className="w-3.5 h-3.5" /> Accept AI Finding
          </button>
          <button
            onClick={() => setShowCorrectModal(true)}
            className="px-4 py-2 rounded-xl text-xs font-bold bg-[#E9DFFF] text-[#6A5ACD] hover:bg-[#E9DFFF]/80 border border-[#6A5ACD]/30 transition flex items-center gap-1.5 cursor-pointer"
          >
            <Edit3 className="w-3.5 h-3.5" /> Correct Classification
          </button>
          <button
            onClick={() => alert('Clarification request sent to submitter.')}
            className="px-3.5 py-2 rounded-xl text-xs font-semibold bg-[#FFFDF5] hover:bg-[#F7F5E8] text-[#17332F] border border-[#D8D8C8] transition flex items-center gap-1.5 cursor-pointer"
          >
            <HelpCircle className="w-3.5 h-3.5" /> Clarification
          </button>
        </div>
      </div>

      {/* Split Screen Layout: Left = Citizen Submission, Right = AI Analysis */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* LEFT COLUMN: ORIGINAL CITIZEN SUBMISSION */}
        <div className="glass-card rounded-3xl p-6 space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-[#D8D8C8]">
            <h3 className="text-sm font-bold text-[#17332F] uppercase tracking-wider">Original Citizen Submission</h3>
            <span className="text-[10px] text-[#66736F] font-mono">RAW SUBMISSION</span>
          </div>

          <div>
            <h2 className="text-xl font-bold text-[#17332F]">{problem.title}</h2>
            <p className="text-xs text-[#17332F] mt-2 leading-relaxed">{problem.description}</p>
          </div>

          <div className="space-y-2 pt-3 text-xs text-[#66736F]">
            <div className="flex items-center gap-2">
              <MapPin className="w-4 h-4 text-[#6A5ACD]" />
              <span>Location: {problem.location.address || `${problem.location.district}, ${problem.location.state}`}</span>
            </div>
            <div className="flex items-center gap-2">
              <Calendar className="w-4 h-4 text-[#0F766E]" />
              <span>Submitted: {new Date(problem.submittedAt).toLocaleString()}</span>
            </div>
            <div className="flex items-center gap-2">
              <User className="w-4 h-4 text-[#087F6B]" />
              <span>Submitter ID: {problem.submitterId || 'CIT-ANONYMOUS'}</span>
            </div>
          </div>

          {problem.evidenceFiles && problem.evidenceFiles.length > 0 && (
            <div className="pt-3 border-t border-[#D8D8C8]">
              <span className="text-xs font-semibold text-[#17332F] block mb-2">Attached Evidence</span>
              <div className="flex flex-wrap gap-2">
                {problem.evidenceFiles.map((file) => (
                  <span key={file} className="px-2.5 py-1 rounded-lg bg-[#F7F5E8] border border-[#D8D8C8] text-[11px] font-mono text-[#17332F]">
                    📷 {file}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* RIGHT COLUMN: AI ANALYSIS FROM GEMMA 3 4B */}
        <div>
          {problem.aiClassification ? (
            <AIInsightCard classification={problem.aiClassification} />
          ) : (
            <div className="glass-card rounded-3xl p-6 text-xs text-[#66736F]">AI analysis pending.</div>
          )}
        </div>
      </div>

      {/* CORRECTION MODAL */}
      <Modal
        isOpen={showCorrectModal}
        onClose={() => setShowCorrectModal(false)}
        title="Correct Classification Category"
        subtitle="Creating a new Reviewer Version snapshot while strictly preserving historical AI interpretations."
      >
        <form onSubmit={handleCorrectSubmit} className="space-y-4 text-xs">
          <div>
            <label className="block font-semibold text-[#17332F] mb-1">Primary Domain</label>
            <select
              value={corrDomain}
              onChange={(e) => setCorrDomain(e.target.value as DomainType)}
              className="w-full px-3.5 py-2.5 rounded-xl bg-[#FFFDF5] border border-[#D8D8C8] text-[#17332F]"
            >
              {[
                'Education',
                'Healthcare',
                'Agriculture',
                'Water Resources',
                'Sanitation',
                'Environment',
                'Energy',
                'Urban Infrastructure',
                'Accessibility',
                'Public Administration',
                'Rural Livelihoods',
                'Other',
              ].map((d) => (
                <option key={d} value={d}>{d}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block font-semibold text-[#17332F] mb-1">Subcategory</label>
            <input
              type="text"
              required
              value={corrSubcategory}
              onChange={(e) => setCorrSubcategory(e.target.value)}
              className="w-full px-3.5 py-2.5 rounded-xl bg-[#FFFDF5] border border-[#D8D8C8] text-[#17332F]"
            />
          </div>

          <div>
            <label className="block font-semibold text-[#17332F] mb-1">Severity Level</label>
            <select
              value={corrSeverity}
              onChange={(e) => setCorrSeverity(e.target.value as SeverityLevel)}
              className="w-full px-3.5 py-2.5 rounded-xl bg-[#FFFDF5] border border-[#D8D8C8] text-[#17332F]"
            >
              <option value="CRITICAL">CRITICAL</option>
              <option value="HIGH">HIGH</option>
              <option value="MODERATE">MODERATE</option>
              <option value="LOW">LOW</option>
            </select>
          </div>

          <div>
            <label className="block font-semibold text-[#B7791F] mb-1">Reason for Correction (Mandatory Audit Requirement)</label>
            <textarea
              rows={3}
              required
              value={corrReason}
              onChange={(e) => setCorrReason(e.target.value)}
              placeholder="Explain why the AI category is being corrected (e.g., Primary impact is public health respiratory illness)..."
              className="w-full px-3.5 py-2.5 rounded-xl bg-[#FFFDF5] border border-[#B7791F]/30 text-[#17332F] placeholder-[#66736F] focus:outline-none"
            />
          </div>

          <div className="pt-3 flex justify-end gap-3">
            <button
              type="button"
              onClick={() => setShowCorrectModal(false)}
              className="px-4 py-2 rounded-xl bg-[#FFFDF5] border border-[#D8D8C8] text-[#17332F] font-semibold hover:bg-[#F7F5E8] transition cursor-pointer"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={!corrReason.trim()}
              className="px-5 py-2 rounded-xl bg-[#034F46] text-white font-bold hover:bg-[#0F766E] disabled:opacity-50 transition shadow-md cursor-pointer"
            >
              Save Correction Snapshot
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};

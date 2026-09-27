import React, { useEffect, useState } from 'react';
import { api } from '../../services/api';
import { UniversityAssignment } from '../../types';
import { BookOpen, Check, X, Clock, AlertTriangle, ArrowRight } from 'lucide-react';
import { Modal } from '../../components/common/Modal';
import { DashboardSkeleton } from '../../components/common/Skeleton';

export const AssignmentsPage: React.FC = () => {
  const [assignments, setAssignments] = useState<UniversityAssignment[]>([]);
  const [loading, setLoading] = useState(true);

  // Reject modal
  const [showRejectModal, setShowRejectModal] = useState(false);
  const [selectedAsn, setSelectedAsn] = useState<UniversityAssignment | null>(null);
  const [rejectReason, setRejectReason] = useState('');

  useEffect(() => {
    api.getAssignments().then((res) => {
      setAssignments(res);
      setLoading(false);
    });
  }, []);

  if (loading) return <DashboardSkeleton />;

  const handleAccept = async (asnId: string) => {
    const updated = await api.acceptAssignment(asnId);
    setAssignments(assignments.map((a) => (a.assignmentId === asnId ? updated : a)));
    alert('Assignment accepted! Status updated to ACCEPTED. Sequential chain stopped & pending sibling ranks cancelled.');
  };

  const handleRejectSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedAsn || !rejectReason.trim()) return;

    const updated = await api.rejectAssignment(selectedAsn.assignmentId, rejectReason);
    setAssignments(assignments.map((a) => (a.assignmentId === selectedAsn.assignmentId ? updated : a)));
    setShowRejectModal(false);
    alert('Assignment rejected. Rank 2 university candidate automatically activated.');
  };

  return (
    <div className="space-y-6 animate-in fade-in">
      <div>
        <h1 className="text-2xl font-extrabold text-[#17332F]">Sequential University Assignments Queue</h1>
        <p className="text-xs text-[#66736F] mt-1">
          Rank-1 university assignments arrive sequentially. Accepting stops the chain; rejecting automatically activates the next rank candidate.
        </p>
      </div>

      <div className="space-y-4">
        {assignments.map((asn) => (
          <div key={asn.assignmentId} className="glass-card rounded-3xl p-6 border border-[#6A5ACD]/30 space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-[#D8D8C8]">
              <div>
                <div className="flex items-center gap-2">
                  <span className="text-xs font-mono font-bold text-[#6A5ACD]">{asn.assignmentId}</span>
                  <span className="text-xs font-bold px-2.5 py-0.5 rounded-full bg-[#E9DFFF] text-[#6A5ACD] border border-[#6A5ACD]/30">
                    Rank #{asn.rank} Candidate
                  </span>
                  <span
                    className={`text-xs px-2.5 py-0.5 rounded-full font-bold ${
                      asn.status === 'ACCEPTED'
                        ? 'bg-[#087F6B]/15 text-[#087F6B]'
                        : asn.status === 'REJECTED'
                        ? 'bg-[#B83A3A]/15 text-[#B83A3A]'
                        : 'bg-[#B7791F]/15 text-[#B7791F] animate-pulse'
                    }`}
                  >
                    {asn.status}
                  </span>
                </div>
                <h3 className="text-lg font-bold text-[#17332F] mt-1">Unsafe school toilets causing students to miss classes</h3>
                <p className="text-xs text-[#66736F] mt-0.5">Problem ID: CF-2026-001 • Match Score: {asn.score}/100</p>
              </div>

              {asn.status === 'SENT' && (
                <div className="flex items-center gap-2 self-start sm:self-auto">
                  <button
                    onClick={() => handleAccept(asn.assignmentId)}
                    className="px-4 py-2 rounded-xl text-xs font-bold bg-[#034F46] text-white hover:bg-[#0F766E] transition shadow-md flex items-center gap-1.5 cursor-pointer"
                  >
                    <Check className="w-4 h-4" /> Accept Assignment
                  </button>
                  <button
                    onClick={() => {
                      setSelectedAsn(asn);
                      setShowRejectModal(true);
                    }}
                    className="px-4 py-2 rounded-xl text-xs font-bold bg-[#FFFDF5] text-[#B83A3A] hover:bg-[#B83A3A]/10 border border-[#B83A3A]/30 transition flex items-center gap-1.5 cursor-pointer"
                  >
                    <X className="w-4 h-4" /> Reject
                  </button>
                </div>
              )}
            </div>

            <p className="text-xs text-[#17332F] leading-relaxed bg-[#F7F5E8] p-3.5 rounded-xl border border-[#D8D8C8]">
              {asn.explanation}
            </p>
          </div>
        ))}
      </div>

      {/* REJECT MODAL */}
      <Modal
        isOpen={showRejectModal}
        onClose={() => setShowRejectModal(false)}
        title="Reject University Assignment"
        subtitle="Mandatory reason required to automatically activate the Rank-2 university candidate."
      >
        <form onSubmit={handleRejectSubmit} className="space-y-4 text-xs">
          <div>
            <label className="block font-semibold text-[#B83A3A] mb-1">Reason for Rejection (Mandatory)</label>
            <textarea
              rows={4}
              required
              value={rejectReason}
              onChange={(e) => setRejectReason(e.target.value)}
              placeholder="Explain why the university is rejecting (e.g. Current research team capacity exhausted)..."
              className="w-full px-3.5 py-2.5 rounded-xl bg-[#FFFDF5] border border-[#B83A3A]/30 text-[#17332F] placeholder-[#66736F] focus:outline-none"
            />
          </div>

          <div className="pt-2 flex justify-end gap-3">
            <button type="button" onClick={() => setShowRejectModal(false)} className="px-4 py-2 rounded-xl bg-[#FFFDF5] border border-[#D8D8C8] text-[#17332F] hover:bg-[#F7F5E8] cursor-pointer">
              Cancel
            </button>
            <button
              type="submit"
              disabled={!rejectReason.trim()}
              className="px-5 py-2 rounded-xl bg-[#B83A3A] text-white font-bold hover:bg-[#B83A3A]/80 transition cursor-pointer"
            >
              Confirm Rejection & Activate Rank 2
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};

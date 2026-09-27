import React, { useState } from 'react';
import { CheckSquare, Upload, Send, ShieldCheck } from 'lucide-react';

export const VerificationPage: React.FC = () => {
  const [officer, setOfficer] = useState('Er. R. K. Shrivastava');
  const [condition, setCondition] = useState('VERIFIED_VALID');
  const [notes, setNotes] = useState('On-site physical inspection confirmed severe toilet facility structural damage at Namkum school.');
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitted(true);
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6 animate-in fade-in">
      <div>
        <h1 className="text-2xl font-extrabold text-[#17332F]">Field Verification Report</h1>
        <p className="text-xs text-[#66736F] mt-1">Submit official on-site inspection findings and site photos.</p>
      </div>

      {!submitted ? (
        <form onSubmit={handleSubmit} className="glass-card rounded-3xl p-6 sm:p-8 space-y-4 border border-[#D8D8C8] text-xs">
          <div>
            <label className="block font-semibold text-[#17332F] mb-1">Inspecting Officer Name</label>
            <input
              type="text"
              required
              value={officer}
              onChange={(e) => setOfficer(e.target.value)}
              className="w-full px-3.5 py-2.5 rounded-xl bg-[#FFFDF5] border border-[#D8D8C8] text-[#17332F]"
            />
          </div>

          <div>
            <label className="block font-semibold text-[#17332F] mb-1">Observed Field Condition</label>
            <select
              value={condition}
              onChange={(e) => setCondition(e.target.value)}
              className="w-full px-3.5 py-2.5 rounded-xl bg-[#FFFDF5] border border-[#D8D8C8] text-[#17332F] font-medium"
            >
              <option value="VERIFIED_VALID">Verified Valid - Urgent Action Recommended</option>
              <option value="PARTIALLY_VERIFIED">Partially Verified - Minor Repairs Needed</option>
              <option value="INVALID_SUBMISSION">Invalid / Exaggerated Citizen Report</option>
            </select>
          </div>

          <div>
            <label className="block font-semibold text-[#17332F] mb-1">Inspection Notes & Findings</label>
            <textarea
              rows={4}
              required
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              className="w-full px-3.5 py-2.5 rounded-xl bg-[#FFFDF5] border border-[#D8D8C8] text-[#17332F]"
            />
          </div>

          <div className="p-4 rounded-xl bg-[#F7F5E8] border border-[#D8D8C8] text-center">
            <Upload className="w-6 h-6 text-[#66736F] mx-auto mb-1" />
            <span className="font-semibold text-[#17332F] block">Attach Inspection Photos / Site Evidence</span>
            <span className="text-[10px] text-[#66736F]">Attach GPS geotagged photo files</span>
          </div>

          <div className="pt-2 flex justify-end">
            <button
              type="submit"
              className="px-6 py-2.5 rounded-full font-bold bg-[#034F46] text-white hover:bg-[#0F766E] transition shadow-md flex items-center gap-2 cursor-pointer"
            >
              Submit Verification Report <Send className="w-4 h-4" />
            </button>
          </div>
        </form>
      ) : (
        <div className="glass-card rounded-3xl p-8 text-center space-y-3 border border-[#087F6B]/30 bg-[#FFFDF5]">
          <ShieldCheck className="w-10 h-10 text-[#087F6B] mx-auto" />
          <h3 className="text-lg font-bold text-[#17332F]">Verification Report Logged</h3>
          <p className="text-xs text-[#66736F]">Inspection record saved to audit log for problem CF-2026-001.</p>
        </div>
      )}
    </div>
  );
};

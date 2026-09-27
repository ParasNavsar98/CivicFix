import React, { useState } from 'react';
import { HelpCircle, Send, Clock, CheckCircle2 } from 'lucide-react';

export const CitizenClarificationsPage: React.FC = () => {
  const [response, setResponse] = useState('');
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!response.trim()) return;
    setSubmitted(true);
  };

  return (
    <div className="max-w-3xl mx-auto space-y-6 animate-in fade-in">
      <div>
        <h1 className="text-2xl font-extrabold text-[#17332F]">Additional Information Requested</h1>
        <p className="text-xs text-[#66736F] mt-1">Reviewers or government officers requested further details to complete validation.</p>
      </div>

      {!submitted ? (
        <div className="glass-card rounded-3xl p-6 sm:p-8 space-y-6 border border-[#B7791F]/30 bg-[#FFFDF5]">
          <div className="flex items-center justify-between pb-4 border-b border-[#D8D8C8]">
            <div className="flex items-center gap-2">
              <span className="p-2 rounded-xl bg-[#B7791F]/10 text-[#B7791F]">
                <HelpCircle className="w-5 h-5" />
              </span>
              <div>
                <span className="text-xs font-mono font-bold text-[#6A5ACD]">CF-2026-004</span>
                <h3 className="text-sm font-bold text-[#17332F]">Voltage Surge Microgrid Issue</h3>
              </div>
            </div>

            <span className="text-xs px-2.5 py-1 rounded-full bg-[#B7791F]/10 text-[#B7791F] font-semibold flex items-center gap-1">
              <Clock className="w-3.5 h-3.5" /> Due in 2 days
            </span>
          </div>

          <div className="bg-[#F7F5E8] p-4 rounded-2xl border border-[#D8D8C8] space-y-2 text-xs">
            <span className="text-[10px] font-bold text-[#B7791F] uppercase tracking-wider block">Requested by Reviewer</span>
            <p className="text-[#17332F] font-medium">
              "Please specify if the voltage spikes occur at specific hours of the evening, and whether the microgrid is solar-diesel hybrid or pure solar storage."
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-[#17332F] mb-1">Your Clarification Response</label>
              <textarea
                rows={4}
                required
                value={response}
                onChange={(e) => setResponse(e.target.value)}
                placeholder="Provide the requested details here..."
                className="w-full px-4 py-3 rounded-xl bg-[#FFFDF5] border border-[#D8D8C8] text-xs text-[#17332F] placeholder-[#66736F] focus:outline-none focus:border-[#034F46] transition"
              />
            </div>

            <div className="flex justify-end">
              <button
                type="submit"
                disabled={!response.trim()}
                className="px-6 py-2.5 rounded-full text-xs font-bold bg-[#034F46] text-white hover:bg-[#0F766E] disabled:opacity-50 transition shadow-md flex items-center gap-2 cursor-pointer"
              >
                Submit Clarification <Send className="w-4 h-4" />
              </button>
            </div>
          </form>
        </div>
      ) : (
        <div className="glass-card rounded-3xl p-8 text-center space-y-3 border border-[#087F6B]/30 bg-[#FFFDF5]">
          <CheckCircle2 className="w-10 h-10 text-[#087F6B] mx-auto" />
          <h3 className="text-lg font-bold text-[#17332F]">Clarification Submitted</h3>
          <p className="text-xs text-[#66736F]">Thank you! Your response has been submitted to the human reviewer queue.</p>
        </div>
      )}
    </div>
  );
};

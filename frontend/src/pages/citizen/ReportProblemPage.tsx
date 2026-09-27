import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { api } from '../../services/api';
import { Problem } from '../../types';
import {
  Sparkles,
  MapPin,
  Upload,
  CheckCircle2,
  ArrowRight,
  ArrowLeft,
  X,
  Navigation,
  ShieldCheck,
  FileText,
} from 'lucide-react';
import { ProblemTimeline } from '../../components/common/ProblemTimeline';

export const ReportProblemPage: React.FC = () => {
  const navigate = useNavigate();

  const [step, setStep] = useState<1 | 2 | 3 | 4>(1);
  const [submitting, setSubmitting] = useState(false);
  const [submittedProblem, setSubmittedProblem] = useState<Problem | null>(null);

  // Form State
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [address, setAddress] = useState('');
  const [district, setDistrict] = useState('Ranchi');
  const [state, setState] = useState('Jharkhand');
  const [latitude, setLatitude] = useState<number | undefined>(23.3441);
  const [longitude, setLongitude] = useState<number | undefined>(85.3096);
  const [evidenceFiles, setEvidenceFiles] = useState<string[]>([
    'damaged_toilet_photo_01.jpeg',
  ]);
  const [confirmed, setConfirmed] = useState(false);

  // Use Browser Geolocation
  const handleUseLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          setLatitude(Number(pos.coords.latitude.toFixed(4)));
          setLongitude(Number(pos.coords.longitude.toFixed(4)));
        },
        (err) => {
          alert('Could not retrieve browser location. You can enter location manually.');
        }
      );
    }
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const newFiles = Array.from(e.target.files).map((f) => f.name);
      setEvidenceFiles([...evidenceFiles, ...newFiles]);
    }
  };

  const removeFile = (name: string) => {
    setEvidenceFiles(evidenceFiles.filter((f) => f !== name));
  };

  const handleSubmit = async () => {
    if (!confirmed) return;
    setSubmitting(true);

    try {
      const created = await api.submitProblem({
        title,
        description,
        location: {
          address,
          district,
          state,
          latitude,
          longitude,
        },
        evidenceFiles,
      });

      setSubmittedProblem(created);
    } catch (e) {
      console.error(e);
    } finally {
      setSubmitting(false);
    }
  };

  // SUCCESS SCREEN
  if (submittedProblem) {
    return (
      <div className="max-w-3xl mx-auto py-8 space-y-8 animate-in fade-in">
        <div className="glass-card rounded-3xl p-8 border border-[#087F6B]/30 text-center relative overflow-hidden bg-[#FFFDF5] shadow-xl">
          <div className="w-16 h-16 rounded-full bg-[#087F6B]/10 text-[#087F6B] border border-[#087F6B]/20 flex items-center justify-center mx-auto mb-4">
            <CheckCircle2 className="w-8 h-8" />
          </div>

          <span className="text-xs font-bold text-[#087F6B] uppercase tracking-wider">Submission Received</span>
          <h1 className="text-3xl font-extrabold text-[#17332F] mt-1">Problem Submitted Successfully</h1>

          <div className="mt-4 inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-[#F7F5E8] border border-[#D8D8C8] text-xs font-mono font-bold text-[#6A5ACD]">
            Problem ID: <span className="text-[#17332F] text-base">{submittedProblem.problemId}</span>
          </div>

          <p className="mt-4 text-xs text-[#66736F] max-w-md mx-auto leading-relaxed">
            Your problem has been submitted. The AI Classification Engine (Gemma 3 4B) is analyzing the report for taxonomy domain, severity, and duplicate candidates.
          </p>

          <div className="mt-8 pt-6 border-t border-[#D8D8C8] flex items-center justify-center gap-4">
            <Link
              to={`/citizen/problems/${submittedProblem.problemId}`}
              className="px-6 py-3 rounded-full text-xs font-bold bg-[#034F46] hover:bg-[#0F766E] text-white transition shadow-md flex items-center gap-2"
            >
              Track Problem Progress <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        </div>

        <ProblemTimeline currentStage={submittedProblem.stage} />
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto space-y-6 animate-in fade-in">
      {/* Header */}
      <div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-[#17332F] tracking-tight">Report a Community Problem</h1>
        <p className="text-xs text-[#66736F] mt-1">Submit issues to connect with AI understanding, human review, and university matching.</p>
      </div>

      {/* Stepper Navigation */}
      <div className="glass-card rounded-2xl p-4 grid grid-cols-4 gap-2 text-center text-xs">
        {[
          { num: 1, label: 'Describe' },
          { num: 2, label: 'Location' },
          { num: 3, label: 'Evidence' },
          { num: 4, label: 'Review' },
        ].map((s) => (
          <div
            key={s.num}
            className={`p-2.5 rounded-xl border transition ${
              step === s.num
                ? 'bg-[#E9DFFF] border-[#6A5ACD]/40 text-[#6A5ACD] font-bold'
                : step > s.num
                ? 'bg-[#087F6B]/10 border-[#087F6B]/20 text-[#087F6B]'
                : 'bg-[#F7F5E8] border-[#D8D8C8] text-[#66736F]'
            }`}
          >
            Step {s.num}: {s.label}
          </div>
        ))}
      </div>

      {/* Form Card */}
      <div className="glass-card rounded-3xl p-6 sm:p-8 space-y-6">
        {/* STEP 1: DESCRIBE */}
        {step === 1 && (
          <div className="space-y-4 animate-in fade-in">
            <h3 className="text-lg font-bold text-[#17332F] flex items-center gap-2">
              <FileText className="w-5 h-5 text-[#6A5ACD]" /> Step 1: Describe the Problem
            </h3>

            <div>
              <label className="block text-xs font-semibold text-[#17332F] mb-1">Problem Title</label>
              <input
                type="text"
                placeholder="e.g., Unsafe damaged school toilets causing student absenteeism"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                className="w-full px-4 py-3 rounded-xl bg-[#FFFDF5] border border-[#D8D8C8] text-xs text-[#17332F] placeholder-[#66736F] focus:outline-none focus:border-[#034F46] transition"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-[#17332F] mb-1">Detailed Description</label>
              <textarea
                rows={5}
                placeholder="Describe what is happening, where it is happening, who is affected, and how long it has been happening..."
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                className="w-full px-4 py-3 rounded-xl bg-[#FFFDF5] border border-[#D8D8C8] text-xs text-[#17332F] placeholder-[#66736F] focus:outline-none focus:border-[#034F46] transition"
              />
              <p className="text-[11px] text-[#66736F] mt-1.5">
                Tip: Include specific details (e.g. affected facilities, safety impacts) so the AI engine can accurately assess taxonomy domain and required expertise.
              </p>
            </div>

            <div className="pt-4 flex justify-end">
              <button
                disabled={!title.trim() || !description.trim()}
                onClick={() => setStep(2)}
                className="px-6 py-2.5 rounded-full text-xs font-bold bg-[#034F46] hover:bg-[#0F766E] disabled:opacity-50 text-white transition flex items-center gap-2 cursor-pointer"
              >
                Next: Location <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}

        {/* STEP 2: LOCATION */}
        {step === 2 && (
          <div className="space-y-4 animate-in fade-in">
            <h3 className="text-lg font-bold text-[#17332F] flex items-center gap-2">
              <MapPin className="w-5 h-5 text-[#0F766E]" /> Step 2: Geographic Location
            </h3>

            <div>
              <label className="block text-xs font-semibold text-[#17332F] mb-1">Specific Address / Landmark</label>
              <input
                type="text"
                placeholder="e.g., Government Girls High School, Namkum"
                value={address}
                onChange={(e) => setAddress(e.target.value)}
                className="w-full px-4 py-3 rounded-xl bg-[#FFFDF5] border border-[#D8D8C8] text-xs text-[#17332F] placeholder-[#66736F] focus:outline-none focus:border-[#034F46] transition"
              />
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-[#17332F] mb-1">District</label>
                <select
                  value={district}
                  onChange={(e) => setDistrict(e.target.value)}
                  className="w-full px-4 py-3 rounded-xl bg-[#FFFDF5] border border-[#D8D8C8] text-xs text-[#17332F] focus:outline-none focus:border-[#034F46] transition"
                >
                  <option value="Ranchi">Ranchi</option>
                  <option value="Dhanbad">Dhanbad</option>
                  <option value="Jamshedpur">Jamshedpur (East Singhbhum)</option>
                  <option value="Hazaribagh">Hazaribagh</option>
                  <option value="Bokaro">Bokaro</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-[#17332F] mb-1">State</label>
                <input
                  type="text"
                  value={state}
                  onChange={(e) => setState(e.target.value)}
                  className="w-full px-4 py-3 rounded-xl bg-[#FFFDF5] border border-[#D8D8C8] text-xs text-[#17332F] focus:outline-none focus:border-[#034F46] transition"
                />
              </div>
            </div>

            {/* Geolocation Controls */}
            <div className="p-4 rounded-2xl bg-[#F7F5E8] border border-[#D8D8C8] flex items-center justify-between">
              <div>
                <span className="text-xs font-bold text-[#17332F] block">Geographic Coordinates</span>
                <span className="text-[11px] text-[#66736F]">
                  Lat: {latitude || 'N/A'}, Long: {longitude || 'N/A'}
                </span>
              </div>
              <button
                type="button"
                onClick={handleUseLocation}
                className="px-3.5 py-1.5 rounded-xl bg-[#0F766E]/10 text-[#0F766E] hover:bg-[#0F766E]/20 border border-[#0F766E]/30 text-xs font-semibold transition flex items-center gap-1.5 cursor-pointer"
              >
                <Navigation className="w-3.5 h-3.5" /> Use My Location
              </button>
            </div>

            <div className="pt-4 flex items-center justify-between">
              <button
                onClick={() => setStep(1)}
                className="px-5 py-2.5 rounded-full text-xs font-semibold bg-[#FFFDF5] hover:bg-[#F7F5E8] text-[#17332F] border border-[#D8D8C8] transition flex items-center gap-1 cursor-pointer"
              >
                <ArrowLeft className="w-4 h-4" /> Back
              </button>
              <button
                onClick={() => setStep(3)}
                className="px-6 py-2.5 rounded-full text-xs font-bold bg-[#034F46] hover:bg-[#0F766E] text-white transition flex items-center gap-2 cursor-pointer"
              >
                Next: Evidence <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}

        {/* STEP 3: EVIDENCE */}
        {step === 3 && (
          <div className="space-y-4 animate-in fade-in">
            <h3 className="text-lg font-bold text-[#17332F] flex items-center gap-2">
              <Upload className="w-5 h-5 text-[#6A5ACD]" /> Step 3: Media & Evidence Upload
            </h3>

            {/* File Drop Area */}
            <div className="border-2 border-dashed border-[#D8D8C8] rounded-2xl p-8 text-center bg-[#F7F5E8] hover:border-[#0F766E] transition">
              <Upload className="w-8 h-8 text-[#66736F] mx-auto mb-2" />
              <p className="text-xs font-semibold text-[#17332F]">Upload Photos, Videos, or Documents</p>
              <p className="text-[11px] text-[#66736F] mt-1">PNG, JPG, MP4, PDF up to 25MB</p>
              <label className="mt-4 inline-block px-4 py-2 rounded-xl bg-[#034F46] text-white text-xs font-bold hover:bg-[#0F766E] cursor-pointer transition">
                Browse Files
                <input type="file" multiple onChange={handleFileUpload} className="hidden" />
              </label>
            </div>

            {/* Attached File Previews */}
            {evidenceFiles.length > 0 && (
              <div className="space-y-2">
                <span className="text-xs font-semibold text-[#17332F]">Attached Files ({evidenceFiles.length})</span>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                  {evidenceFiles.map((file) => (
                    <div key={file} className="p-3 rounded-xl bg-[#FFFDF5] border border-[#D8D8C8] flex items-center justify-between text-xs">
                      <span className="truncate text-[#17332F] font-mono">{file}</span>
                      <button onClick={() => removeFile(file)} className="text-[#B83A3A] hover:text-[#B83A3A]/80 p-1 cursor-pointer">
                        <X className="w-4 h-4" />
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div className="pt-4 flex items-center justify-between">
              <button
                onClick={() => setStep(2)}
                className="px-5 py-2.5 rounded-full text-xs font-semibold bg-[#FFFDF5] hover:bg-[#F7F5E8] text-[#17332F] border border-[#D8D8C8] transition flex items-center gap-1 cursor-pointer"
              >
                <ArrowLeft className="w-4 h-4" /> Back
              </button>
              <button
                onClick={() => setStep(4)}
                className="px-6 py-2.5 rounded-full text-xs font-bold bg-[#034F46] hover:bg-[#0F766E] text-white transition flex items-center gap-2 cursor-pointer"
              >
                Next: Review Submission <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}

        {/* STEP 4: REVIEW & CONFIRM */}
        {step === 4 && (
          <div className="space-y-5 animate-in fade-in">
            <h3 className="text-lg font-bold text-[#17332F] flex items-center gap-2">
              <ShieldCheck className="w-5 h-5 text-[#087F6B]" /> Step 4: Review Submission
            </h3>

            <div className="space-y-3 bg-[#F7F5E8] p-5 rounded-2xl border border-[#D8D8C8] text-xs">
              <div>
                <span className="text-[10px] font-semibold text-[#66736F] uppercase tracking-wider block">Title</span>
                <span className="text-sm font-bold text-[#17332F]">{title}</span>
              </div>
              <div>
                <span className="text-[10px] font-semibold text-[#66736F] uppercase tracking-wider block">Description</span>
                <p className="text-[#17332F] leading-relaxed">{description}</p>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <span className="text-[10px] font-semibold text-[#66736F] uppercase tracking-wider block">Address</span>
                  <span className="text-[#17332F]">{address || 'N/A'}</span>
                </div>
                <div>
                  <span className="text-[10px] font-semibold text-[#66736F] uppercase tracking-wider block">District / State</span>
                  <span className="text-[#17332F]">{district}, {state}</span>
                </div>
              </div>
              <div>
                <span className="text-[10px] font-semibold text-[#66736F] uppercase tracking-wider block">Evidence Files</span>
                <span className="text-[#17332F] font-mono">{evidenceFiles.join(', ') || 'None'}</span>
              </div>
            </div>

            {/* Confirmation Checkbox */}
            <label className="flex items-start gap-3 p-4 rounded-xl bg-[#E9DFFF]/40 border border-[#6A5ACD]/20 cursor-pointer">
              <input
                type="checkbox"
                checked={confirmed}
                onChange={(e) => setConfirmed(e.target.checked)}
                className="mt-0.5 rounded border-[#D8D8C8] text-[#034F46] focus:ring-0"
              />
              <span className="text-xs text-[#17332F] leading-relaxed">
                I confirm that the information submitted is accurate to the best of my knowledge and complies with CivicFix community reporting guidelines.
              </span>
            </label>

            <div className="pt-4 flex items-center justify-between">
              <button
                onClick={() => setStep(3)}
                className="px-5 py-2.5 rounded-full text-xs font-semibold bg-[#FFFDF5] hover:bg-[#F7F5E8] text-[#17332F] border border-[#D8D8C8] transition flex items-center gap-1 cursor-pointer"
              >
                <ArrowLeft className="w-4 h-4" /> Back
              </button>
              <button
                disabled={!confirmed || submitting}
                onClick={handleSubmit}
                className="px-8 py-3 rounded-full text-xs font-bold bg-[#034F46] hover:bg-[#0F766E] disabled:opacity-50 text-white transition shadow-md flex items-center gap-2 cursor-pointer"
              >
                {submitting ? 'Submitting & Classifying...' : 'Submit Problem'} <CheckCircle2 className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

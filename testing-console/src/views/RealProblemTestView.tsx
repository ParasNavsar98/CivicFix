import React, { useState } from 'react';
import { backendApi } from '../api/backend';
import { HTTPInspectorData, Problem } from '../types';
import { RequestResponseInspector } from '../components/RequestResponseInspector';
import { StatusBadge } from '../components/StatusBadge';
import { JsonViewer } from '../components/JsonViewer';
import { NavTab } from '../components/Sidebar';
import {
  FilePlus,
  Play,
  RotateCcw,
  CheckCircle2,
  AlertTriangle,
  Clock,
  ArrowRight,
  Sparkles,
} from 'lucide-react';

interface Props {
  onNavigate: (tab: NavTab) => void;
  onSelectProblem?: (problem: Problem) => void;
}

const SAMPLE_PRESETS = [
  {
    name: '1. Garbage Burning Near School',
    title: 'Open garbage burning near school premises',
    description: 'Unprocessed municipal waste is being burned in an open area near a primary school. Thick smoke and toxic fumes spread into classrooms during morning hours, exposing children to severe health risks.',
    lat: 18.5204,
    long: 73.8567,
    address: 'Sector 4, Near Model Primary School',
    expected: 'Domain: Environment / Public Health. High confidence expected.',
  },
  {
    name: '2. Water Pipe Leakage',
    title: 'Severe drinking water main pipe burst in Sector 7',
    description: 'A major clean drinking water distribution pipe has burst near the community hall in Sector 7. Thousands of gallons of potable water are wasting onto the street while residential areas face severe shortage.',
    lat: 18.5301,
    long: 73.8452,
    address: 'Main Street, Sector 7 Community Center',
    expected: 'Domain: Water & Sanitation. High severity expected.',
  },
  {
    name: '3. Pothole Accident Hazard',
    title: 'Deep crater potholes causing repeated vehicle accidents',
    description: 'Multiple deep potholes have formed on the main arterial road connecting the highway to the station. Two motorcyclists skid and broke bones last night due to lack of streetlights over the craters.',
    lat: 18.5123,
    long: 73.8612,
    address: 'Highway Connector Junction, Ward 12',
    expected: 'Domain: Infrastructure & Roads. Critical urgency expected.',
  },
  {
    name: '4. Hospital Medical Supply Shortage',
    title: 'Primary Health Center lacking basic emergency medicines',
    description: 'The local government primary health clinic has run out of essential emergency drugs, snakebite antivenom, and basic surgical gloves for the past two weeks. Patients are being turned away.',
    lat: 18.5089,
    long: 73.8701,
    address: 'Ward 5 Government Clinic',
    expected: 'Domain: Public Health. High priority expected.',
  },
  {
    name: '5. Vague Citizen Report',
    title: 'Something is wrong in the area',
    description: 'Some strange noise and smell is happening near the market area since yesterday. Needs attention.',
    lat: 18.5100,
    long: 73.8500,
    address: 'Market Square',
    expected: 'Vague text -> Low AI confidence (< 0.85). Should route to REVIEW_REQUIRED queue.',
  },
  {
    name: '6. Unrelated General Text',
    title: 'General query regarding municipal tax payment deadline',
    description: 'Can someone tell me where to pay the quarterly property tax bill online and what is the last date without penalty?',
    lat: 18.5200,
    long: 73.8550,
    address: 'Civic Center',
    expected: 'Governance / Administrative query or Low confidence review flag.',
  },
];

export const RealProblemTestView: React.FC<Props> = ({ onNavigate, onSelectProblem }) => {
  const [problemIdInput, setProblemIdInput] = useState('');
  const [title, setTitle] = useState(SAMPLE_PRESETS[0].title);
  const [description, setDescription] = useState(SAMPLE_PRESETS[0].description);
  const [lat, setLat] = useState<number | undefined>(SAMPLE_PRESETS[0].lat);
  const [long, setLong] = useState<number | undefined>(SAMPLE_PRESETS[0].long);
  const [address, setAddress] = useState(SAMPLE_PRESETS[0].address);
  const [privacyClass, setPrivacyClass] = useState('PUBLIC');
  const [userId, setUserId] = useState('citizen_001');
  const [userRole, setUserRole] = useState('citizen');

  const [loading, setLoading] = useState(false);
  const [inspector, setInspector] = useState<HTTPInspectorData | null>(null);
  const [resultProblem, setResultProblem] = useState<Problem | null>(null);
  const [error, setError] = useState<string | null>(null);

  const applyPreset = (preset: typeof SAMPLE_PRESETS[0]) => {
    setTitle(preset.title);
    setDescription(preset.description);
    setLat(preset.lat);
    setLong(preset.long);
    setAddress(preset.address);
    setProblemIdInput(`P-${Math.random().toString(36).substring(2, 9).toUpperCase()}`);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResultProblem(null);
    setInspector(null);

    const payload = {
      problemId: problemIdInput.trim() || undefined,
      title: title.trim(),
      description: description.trim(),
      location: (lat || long || address) ? { lat, long, address } : undefined,
      privacyClass,
    };

    const res = await backendApi.createProblem(payload, userId, userRole);
    setInspector(res.inspector);

    if (res.data && res.data.success && res.data.data) {
      setResultProblem(res.data.data);
      if (onSelectProblem) {
        onSelectProblem(res.data.data);
      }
    } else {
      setError(res.error || 'Problem submission failed');
    }

    setLoading(false);
  };

  return (
    <div className="space-y-6">
      {/* View Header */}
      <div className="p-5 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-between">
        <div>
          <h2 className="text-lg font-bold text-slate-100 flex items-center gap-2">
            <FilePlus className="w-5 h-5 text-cyan-400" />
            <span>Test Real Problem Submission (`POST /api/problems`)</span>
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Submit a real societal problem to the backend pipeline: Storage FIRST → AI Classification (Gemma 3 4B) → Duplicate Detection (BGE-small) → Workflow evaluation.
          </p>
        </div>
      </div>

      {/* Preset Buttons */}
      <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-2">
        <div className="text-xs font-bold text-slate-300 flex items-center gap-1.5 mb-2">
          <Sparkles className="w-4 h-4 text-cyan-400" />
          <span>Quick Sample Presets (Click to load):</span>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-2">
          {SAMPLE_PRESETS.map((p, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => applyPreset(p)}
              className="text-left p-2.5 rounded-lg bg-slate-800/80 hover:bg-slate-800 border border-slate-700/80 transition-colors"
            >
              <div className="font-semibold text-xs text-cyan-300 truncate">{p.name}</div>
              <div className="text-[10px] text-slate-400 truncate mt-0.5">{p.expected}</div>
            </button>
          ))}
        </div>
      </div>

      {/* Main Submission Form */}
      <form onSubmit={handleSubmit} className="p-5 rounded-xl bg-slate-900 border border-slate-800 space-y-4 text-xs">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-slate-300 font-semibold mb-1">Custom Problem ID (Optional)</label>
            <input
              type="text"
              placeholder="e.g. P-TEST-001 (auto-generated if empty)"
              value={problemIdInput}
              onChange={(e) => setProblemIdInput(e.target.value)}
              className="w-full px-3 py-2 rounded bg-slate-800 border border-slate-700 font-mono text-slate-200 focus:outline-none focus:border-cyan-500"
            />
          </div>

          <div>
            <label className="block text-slate-300 font-semibold mb-1">X-User-ID (Header)</label>
            <input
              type="text"
              value={userId}
              onChange={(e) => setUserId(e.target.value)}
              className="w-full px-3 py-2 rounded bg-slate-800 border border-slate-700 font-mono text-slate-200 focus:outline-none focus:border-cyan-500"
            />
          </div>

          <div>
            <label className="block text-slate-300 font-semibold mb-1">X-User-Role (Header)</label>
            <select
              value={userRole}
              onChange={(e) => setUserRole(e.target.value)}
              className="w-full px-3 py-2 rounded bg-slate-800 border border-slate-700 text-slate-200 focus:outline-none focus:border-cyan-500"
            >
              <option value="citizen">citizen</option>
              <option value="reviewer">reviewer</option>
              <option value="admin">admin</option>
            </select>
          </div>
        </div>

        <div>
          <label className="block text-slate-300 font-semibold mb-1">Problem Title (Required)</label>
          <input
            type="text"
            required
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="w-full px-3 py-2 rounded bg-slate-800 border border-slate-700 text-slate-100 font-medium focus:outline-none focus:border-cyan-500"
          />
        </div>

        <div>
          <label className="block text-slate-300 font-semibold mb-1">Detailed Description (Required)</label>
          <textarea
            required
            rows={4}
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            className="w-full px-3 py-2 rounded bg-slate-800 border border-slate-700 text-slate-200 focus:outline-none focus:border-cyan-500"
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-slate-300 font-semibold mb-1">Latitude</label>
            <input
              type="number"
              step="any"
              value={lat || ''}
              onChange={(e) => setLat(e.target.value ? parseFloat(e.target.value) : undefined)}
              className="w-full px-3 py-2 rounded bg-slate-800 border border-slate-700 text-slate-200 font-mono focus:outline-none focus:border-cyan-500"
            />
          </div>

          <div>
            <label className="block text-slate-300 font-semibold mb-1">Longitude</label>
            <input
              type="number"
              step="any"
              value={long || ''}
              onChange={(e) => setLong(e.target.value ? parseFloat(e.target.value) : undefined)}
              className="w-full px-3 py-2 rounded bg-slate-800 border border-slate-700 text-slate-200 font-mono focus:outline-none focus:border-cyan-500"
            />
          </div>

          <div>
            <label className="block text-slate-300 font-semibold mb-1">Address Description</label>
            <input
              type="text"
              value={address}
              onChange={(e) => setAddress(e.target.value)}
              className="w-full px-3 py-2 rounded bg-slate-800 border border-slate-700 text-slate-200 focus:outline-none focus:border-cyan-500"
            />
          </div>

          <div>
            <label className="block text-slate-300 font-semibold mb-1">Privacy Classification</label>
            <select
              value={privacyClass}
              onChange={(e) => setPrivacyClass(e.target.value)}
              className="w-full px-3 py-2 rounded bg-slate-800 border border-slate-700 text-slate-200 focus:outline-none focus:border-cyan-500"
            >
              <option value="PUBLIC">PUBLIC</option>
              <option value="INTERNAL">INTERNAL</option>
              <option value="RESTRICTED">RESTRICTED</option>
              <option value="CONFIDENTIAL">CONFIDENTIAL</option>
            </select>
          </div>
        </div>

        <div className="flex items-center justify-end gap-3 pt-2">
          <button
            type="button"
            onClick={() => {
              setTitle('');
              setDescription('');
              setLat(undefined);
              setLong(undefined);
              setAddress('');
              setProblemIdInput('');
            }}
            className="px-4 py-2 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 font-medium text-xs border border-slate-700"
          >
            Clear Form
          </button>

          <button
            type="submit"
            disabled={loading}
            className="flex items-center gap-2 px-5 py-2.5 rounded bg-cyan-600 hover:bg-cyan-500 text-white font-bold text-xs shadow-md transition-colors disabled:opacity-50"
          >
            <Play className="w-4 h-4 fill-white" />
            <span>{loading ? 'Executing Pipeline (AI Services...)' : 'Submit Real Problem'}</span>
          </button>
        </div>
      </form>

      {/* Execution Results */}
      {resultProblem && (
        <div className="p-5 rounded-xl bg-slate-900 border border-emerald-800/80 space-y-4">
          <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-800 pb-3">
            <div>
              <div className="text-xs text-emerald-400 font-mono font-bold flex items-center gap-1.5">
                <CheckCircle2 className="w-4 h-4" />
                <span>Problem Processed Successfully!</span>
              </div>
              <h3 className="text-base font-bold text-slate-100 mt-1">{resultProblem.title}</h3>
              <div className="text-xs text-slate-400 font-mono">ID: {resultProblem.problemId}</div>
            </div>

            <div className="flex items-center gap-2">
              <StatusBadge status={resultProblem.status} />
              <button
                onClick={() => onNavigate('timeline')}
                className="px-3 py-1.5 rounded bg-slate-800 hover:bg-slate-700 text-cyan-300 text-xs font-semibold border border-slate-700 flex items-center gap-1"
              >
                <span>View Timeline</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>

          {/* Quick Result Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-3 text-xs">
            <div className="p-3 rounded bg-slate-800/70 border border-slate-700">
              <div className="text-slate-400 font-semibold">Workflow Status</div>
              <div className="font-mono font-bold text-slate-100 mt-1">{resultProblem.status}</div>
              <div className="text-[11px] text-slate-500 mt-0.5">State Machine Target</div>
            </div>

            <div className="p-3 rounded bg-slate-800/70 border border-slate-700">
              <div className="text-slate-400 font-semibold">Primary Domain</div>
              <div className="font-mono font-bold text-cyan-300 mt-1">{resultProblem.primaryDomain || 'Unassigned'}</div>
              <div className="text-[11px] text-slate-500 mt-0.5">{resultProblem.subcategory || 'No Subcategory'}</div>
            </div>

            <div className="p-3 rounded bg-slate-800/70 border border-slate-700">
              <div className="text-slate-400 font-semibold">Human Review Flag</div>
              <div className={`font-mono font-bold mt-1 ${resultProblem.reviewRequired ? 'text-amber-400' : 'text-emerald-400'}`}>
                {resultProblem.reviewRequired ? 'REQUIRED' : 'NOT NEEDED'}
              </div>
              <div className="text-[11px] text-slate-500 mt-0.5">
                {resultProblem.reviewReasons?.length ? resultProblem.reviewReasons[0] : 'High AI confidence'}
              </div>
            </div>

            <div className="p-3 rounded bg-slate-800/70 border border-slate-700">
              <div className="text-slate-400 font-semibold">Duplicate Status</div>
              <div className="font-mono font-bold text-purple-300 mt-1">{resultProblem.duplicateStatus || 'none'}</div>
              <div className="text-[11px] text-slate-500 mt-0.5">State: {resultProblem.duplicateDetectionState}</div>
            </div>
          </div>

          {/* Visual Execution Pipeline Steps */}
          <div className="p-4 rounded bg-slate-800/50 border border-slate-700">
            <div className="text-xs font-bold text-slate-300 mb-3">Live Execution Pipeline Journey</div>
            <div className="grid grid-cols-2 md:grid-cols-5 gap-2 text-xs">
              <div className="p-2 rounded bg-emerald-950/80 border border-emerald-700 text-emerald-300 font-medium">
                ✓ 1. DB Persisted FIRST
              </div>
              <div className="p-2 rounded bg-emerald-950/80 border border-emerald-700 text-emerald-300 font-medium">
                ✓ 2. AI Classification ({resultProblem.classificationState})
              </div>
              <div className="p-2 rounded bg-emerald-950/80 border border-emerald-700 text-emerald-300 font-medium">
                ✓ 3. Duplicate Analysis ({resultProblem.duplicateDetectionState})
              </div>
              <div className={`p-2 rounded font-medium border ${resultProblem.reviewRequired ? 'bg-amber-950/80 border-amber-700 text-amber-300' : 'bg-emerald-950/80 border-emerald-700 text-emerald-300'}`}>
                {resultProblem.reviewRequired ? '⚠ 4. Review Flagged' : '✓ 4. Auto Validated'}
              </div>
              <div className="p-2 rounded bg-slate-900 border border-slate-700 text-slate-300 font-medium">
                ○ 5. {resultProblem.status}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* HTTP Inspector */}
      {inspector && (
        <div className="mt-4">
          <h3 className="text-sm font-bold text-slate-200">Raw HTTP Inspection</h3>
          <RequestResponseInspector inspector={inspector} />
        </div>
      )}
    </div>
  );
};

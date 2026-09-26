import React, { useState } from 'react';
import { classificationApi } from '../api/classification';
import { ClassificationResponse, HTTPInspectorData } from '../types';
import { RequestResponseInspector } from '../components/RequestResponseInspector';
import { JsonViewer } from '../components/JsonViewer';
import { Brain, Play, Sparkles, CheckCircle2, AlertTriangle, HelpCircle } from 'lucide-react';

export const ClassificationLabView: React.FC = () => {
  const [problemId, setProblemId] = useState('P-CLS-LAB-01');
  const [title, setTitle] = useState('Open garbage burning near school');
  const [description, setDescription] = useState('Unprocessed waste is being burned near a school. Smoke is spreading into classrooms.');
  const [district, setDistrict] = useState('Pune');
  const [state, setState] = useState('Maharashtra');
  const [lat, setLat] = useState<number | undefined>(18.5204);
  const [long, setLong] = useState<number | undefined>(73.8567);

  const [loading, setLoading] = useState(false);
  const [inspector, setInspector] = useState<HTTPInspectorData | null>(null);
  const [result, setResult] = useState<ClassificationResponse | null>(null);

  const handleClassify = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setResult(null);

    const payload = {
      problemId: problemId.trim(),
      title: title.trim(),
      description: description.trim(),
      location: {
        district: district.trim(),
        state: state.trim(),
        latitude: lat,
        longitude: long,
      },
    };

    const res = await classificationApi.classifyProblem(payload);
    setInspector(res.inspector);
    if (res.data) {
      setResult(res.data);
    }
    setLoading(false);
  };

  const cls = result?.classification;

  return (
    <div className="space-y-6">
      <div className="p-5 rounded-xl bg-slate-900 border border-slate-800">
        <h2 className="text-lg font-bold text-slate-100 flex items-center gap-2">
          <Brain className="w-5 h-5 text-purple-400" />
          <span>AI Classification Engine Lab (`POST /classify` @ Port 8000)</span>
        </h2>
        <p className="text-xs text-slate-400 mt-1">
          Directly query the standalone FastAPI + Ollama Gemma 3 4B Classification Engine. Tests taxonomy enforcement, structured JSON formatting, confidence scoring, and reasoning.
        </p>
      </div>

      <form onSubmit={handleClassify} className="p-5 rounded-xl bg-slate-900 border border-slate-800 space-y-4 text-xs">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-slate-300 font-semibold mb-1">Problem ID</label>
            <input
              type="text"
              required
              value={problemId}
              onChange={(e) => setProblemId(e.target.value)}
              className="w-full px-3 py-2 rounded bg-slate-800 border border-slate-700 font-mono text-slate-200 focus:outline-none focus:border-cyan-500"
            />
          </div>

          <div>
            <label className="block text-slate-300 font-semibold mb-1">District</label>
            <input
              type="text"
              required
              value={district}
              onChange={(e) => setDistrict(e.target.value)}
              className="w-full px-3 py-2 rounded bg-slate-800 border border-slate-700 text-slate-200 focus:outline-none focus:border-cyan-500"
            />
          </div>

          <div>
            <label className="block text-slate-300 font-semibold mb-1">State</label>
            <input
              type="text"
              required
              value={state}
              onChange={(e) => setState(e.target.value)}
              className="w-full px-3 py-2 rounded bg-slate-800 border border-slate-700 text-slate-200 focus:outline-none focus:border-cyan-500"
            />
          </div>
        </div>

        <div>
          <label className="block text-slate-300 font-semibold mb-1">Problem Title</label>
          <input
            type="text"
            required
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="w-full px-3 py-2 rounded bg-slate-800 border border-slate-700 text-slate-100 font-medium focus:outline-none focus:border-cyan-500"
          />
        </div>

        <div>
          <label className="block text-slate-300 font-semibold mb-1">Description</label>
          <textarea
            required
            rows={3}
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            className="w-full px-3 py-2 rounded bg-slate-800 border border-slate-700 text-slate-200 focus:outline-none focus:border-cyan-500"
          />
        </div>

        <div className="flex justify-end pt-2">
          <button
            type="submit"
            disabled={loading}
            className="flex items-center gap-2 px-5 py-2.5 rounded bg-purple-600 hover:bg-purple-500 text-white font-bold text-xs shadow transition-colors disabled:opacity-50"
          >
            <Play className="w-4 h-4 fill-white" />
            <span>{loading ? 'Running Gemma 3 4B Inference...' : 'Execute /classify'}</span>
          </button>
        </div>
      </form>

      {/* Structured Output Breakdown */}
      {cls && (
        <div className="p-5 rounded-xl bg-slate-900 border border-purple-800/80 space-y-4 text-xs">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <div>
              <div className="text-purple-400 font-mono font-bold text-xs">Classification Outcome Status: {result.status}</div>
              <h3 className="text-base font-bold text-slate-100 mt-0.5">{cls.primaryDomain}</h3>
            </div>
            <div className="text-right">
              <div className="text-slate-400">AI Confidence</div>
              <div className="text-base font-mono font-bold text-cyan-300">{(cls.confidence * 100).toFixed(1)}%</div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
            <div className="p-3 rounded bg-slate-800/70 border border-slate-700">
              <div className="text-slate-400 font-semibold">Subcategory</div>
              <div className="font-mono font-bold text-slate-200 mt-1">{cls.subcategory}</div>
            </div>

            <div className="p-3 rounded bg-slate-800/70 border border-slate-700">
              <div className="text-slate-400 font-semibold">Severity</div>
              <div className="font-mono font-bold text-amber-400 mt-1">{cls.severity}</div>
            </div>

            <div className="p-3 rounded bg-slate-800/70 border border-slate-700">
              <div className="text-slate-400 font-semibold">Urgency</div>
              <div className="font-mono font-bold text-rose-400 mt-1">{cls.urgency}</div>
            </div>

            <div className="p-3 rounded bg-slate-800/70 border border-slate-700">
              <div className="text-slate-400 font-semibold">Routing Flags</div>
              <div className="font-mono text-[11px] text-slate-300 mt-1">
                Govt: {cls.governmentActionPossible ? 'Yes' : 'No'} • Research: {cls.researchRequired ? 'Yes' : 'No'}
              </div>
            </div>
          </div>

          <div className="p-3 rounded bg-slate-800/70 border border-slate-700 space-y-1">
            <div className="text-slate-400 font-semibold">AI Reasoning</div>
            <div className="text-slate-200 font-sans italic">{cls.reasoning}</div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            <div className="p-3 rounded bg-slate-800/70 border border-slate-700">
              <div className="text-slate-400 font-semibold mb-1">Required Expertise</div>
              <div className="flex flex-wrap gap-1">
                {cls.requiredExpertise?.map((e, idx) => (
                  <span key={idx} className="px-2 py-0.5 rounded bg-slate-700 text-slate-300 font-mono text-[11px]">
                    {e}
                  </span>
                )) || <span className="text-slate-500">None specified</span>}
              </div>
            </div>

            <div className="p-3 rounded bg-slate-800/70 border border-slate-700">
              <div className="text-slate-400 font-semibold mb-1">Required Resources</div>
              <div className="flex flex-wrap gap-1">
                {cls.requiredResources?.map((r, idx) => (
                  <span key={idx} className="px-2 py-0.5 rounded bg-slate-700 text-slate-300 font-mono text-[11px]">
                    {r}
                  </span>
                )) || <span className="text-slate-500">None specified</span>}
              </div>
            </div>
          </div>
        </div>
      )}

      {inspector && <RequestResponseInspector inspector={inspector} />}
    </div>
  );
};

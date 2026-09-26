import React, { useState } from 'react';
import { duplicateApi } from '../api/duplicate';
import { DuplicateCheckResponse, HTTPInspectorData } from '../types';
import { RequestResponseInspector } from '../components/RequestResponseInspector';
import { JsonViewer } from '../components/JsonViewer';
import {
  Layers,
  Play,
  Sparkles,
  AlertTriangle,
  ShieldAlert,
  MapPin,
  CheckCircle2,
  XCircle,
  HelpCircle,
  Calculator,
  Cpu,
  Sliders,
  ChevronDown,
  ChevronUp,
} from 'lucide-react';

const DUPLICATE_SCENARIOS = [
  {
    name: 'Scenario A: Same Issue + Similar Wording + Nearby Location',
    probA: {
      problemId: 'P-MASTER-101',
      title: 'Open garbage burning near primary school in Sector 4',
      description: 'Unprocessed municipal garbage is being openly burned near the school. Thick toxic smoke is spreading to classrooms.',
      lat: 18.5204,
      long: 73.8567,
      address: 'Sector 4 Main Road',
      primaryDomain: 'Environment',
      subcategory: 'Waste Dumping',
    },
    probB: {
      problemId: 'P-CANDIDATE-102',
      title: 'Garbage smoke spreading into school from waste burning',
      description: 'Smoke from open trash burning near the school is choking students in Sector 4.',
      lat: 18.5210,
      long: 73.8570,
      address: 'Sector 4 School Gate',
      primaryDomain: 'Environment',
      subcategory: 'Waste Dumping',
    },
    expected: 'Expected: Strong Candidate (High Semantic Similarity > 0.85 & Nearby Location).',
  },
  {
    name: 'Scenario B: Hospital Medicine Shortage (MISSING TAXONOMY REGRESSION)',
    probA: {
      problemId: 'P-MASTER-601',
      title: 'Hospital medicine shortage',
      description: 'Primary health center lacks basic emergency medicines.',
      lat: 28.7041,
      long: 77.1025,
      address: 'PHC Ward 5',
      primaryDomain: '',
      subcategory: '',
    },
    probB: {
      problemId: 'P-CANDIDATE-602',
      title: 'Shortage of Medicines in a nearby hospital',
      description: 'Hospitals lack medicines.',
      lat: 28.7041,
      long: 77.1025,
      address: 'PHC Ward 5',
      primaryDomain: '',
      subcategory: '',
    },
    expected: 'Expected: Strong Candidate (High Semantic + 0km Location, Missing Metadata treated as UNKNOWN, score ~88.8%).',
  },
  {
    name: 'Scenario C: Same Location + Different Issue (Contradiction Protection)',
    probA: {
      problemId: 'P-MASTER-603',
      title: 'Hospital medicine shortage',
      description: 'Primary health center lacks basic emergency medicines.',
      lat: 28.7041,
      long: 77.1025,
      address: 'PHC Ward 5',
      primaryDomain: '',
      subcategory: '',
    },
    probB: {
      problemId: 'P-CANDIDATE-604',
      title: 'Hospital electricity outage',
      description: 'Primary health center power cut past 6 hours, total electricity blackout.',
      lat: 28.7041,
      long: 77.1025,
      address: 'PHC Ward 5',
      primaryDomain: '',
      subcategory: '',
    },
    expected: 'Expected: No Candidate (Fingerprint Contradiction: medicine shortage vs electricity outage).',
  },
  {
    name: 'Scenario D: Same Issue + Different Wording + Nearby Location',
    probA: {
      problemId: 'P-MASTER-201',
      title: 'Water main line burst flooding Sector 7 street',
      description: 'Clean drinking water main pipe ruptured. Water gushing uncontrollably near community center.',
      lat: 18.5301,
      long: 73.8452,
      address: 'Sector 7 Main Road',
      primaryDomain: 'Water & Sanitation',
      subcategory: 'Water Leakage',
    },
    probB: {
      problemId: 'P-CANDIDATE-202',
      title: 'Drinking water pipeline leakage wasting gallons of water',
      description: 'Massive underground pipe failure causing street inundation in Sector 7 area.',
      lat: 18.5305,
      long: 73.8458,
      address: 'Sector 7 Lane 3',
      primaryDomain: 'Water & Sanitation',
      subcategory: 'Water Leakage',
    },
    expected: 'Expected: Potential Duplicate / Strong Candidate (Semantic embedding captures concept match).',
  },
  {
    name: 'Scenario E: Related Issue + Nearby Location',
    probA: {
      problemId: 'P-MASTER-301',
      title: 'Deep potholes on station road',
      description: 'Deep road craters causing traffic jams and vehicle damage.',
      lat: 18.5123,
      long: 73.8612,
      address: 'Station Road',
      primaryDomain: 'Infrastructure & Roads',
      subcategory: 'Potholes',
    },
    probB: {
      problemId: 'P-CANDIDATE-302',
      title: 'Streetlights out on station road',
      description: 'All streetlights are dark on station road creating night hazard.',
      lat: 18.5125,
      long: 73.8615,
      address: 'Station Road Junction',
      primaryDomain: 'Infrastructure & Roads',
      subcategory: 'Streetlight Failure',
    },
    expected: 'Expected: Low duplicate score / Mismatch subcategory prevents duplicate false positive.',
  },
  {
    name: 'Scenario F: Same Issue Type + Far Away Location (100km+)',
    probA: {
      problemId: 'P-MASTER-501',
      title: 'Garbage burning in Pune Sector 4',
      description: 'Waste burning near school in Pune city.',
      lat: 18.5204,
      long: 73.8567,
      address: 'Pune Sector 4',
      primaryDomain: 'Environment',
      subcategory: 'Waste Dumping',
    },
    probB: {
      problemId: 'P-CANDIDATE-502',
      title: 'Garbage burning in Mumbai Sector 4',
      description: 'Waste burning near school in Mumbai area.',
      lat: 19.0760,
      long: 72.8777,
      address: 'Mumbai Area',
      primaryDomain: 'Environment',
      subcategory: 'Waste Dumping',
    },
    expected: 'Expected: High semantic similarity, but location distance score drops composite score.',
  },
];

export const DuplicateDetectionLabView: React.FC = () => {
  const [scenario, setScenario] = useState(DUPLICATE_SCENARIOS[0]);

  const [probAId, setProbAId] = useState(scenario.probA.problemId);
  const [probATitle, setProbATitle] = useState(scenario.probA.title);
  const [probADesc, setProbADesc] = useState(scenario.probA.description);
  const [probALat, setProbALat] = useState<number | undefined>(scenario.probA.lat);
  const [probALong, setProbALong] = useState<number | undefined>(scenario.probA.long);
  const [probAPrimary, setProbAPrimary] = useState<string>(scenario.probA.primaryDomain || '');
  const [probASub, setProbASub] = useState<string>(scenario.probA.subcategory || '');

  const [probBId, setProbBId] = useState(scenario.probB.problemId);
  const [probBTitle, setProbBTitle] = useState(scenario.probB.title);
  const [probBDesc, setProbBDesc] = useState(scenario.probB.description);
  const [probBLat, setProbBLat] = useState<number | undefined>(scenario.probB.lat);
  const [probBLong, setProbBLong] = useState<number | undefined>(scenario.probB.long);
  const [probBPrimary, setProbBPrimary] = useState<string>(scenario.probB.primaryDomain || '');
  const [probBSub, setProbBSub] = useState<string>(scenario.probB.subcategory || '');

  const [loading, setLoading] = useState(false);
  const [inspector, setInspector] = useState<HTTPInspectorData | null>(null);
  const [result, setResult] = useState<DuplicateCheckResponse | null>(null);
  const [showFormula, setShowFormula] = useState(false);
  const [showEmbeddings, setShowEmbeddings] = useState(false);
  const [debugMode, setDebugMode] = useState(false);

  const applyScenario = (sc: typeof DUPLICATE_SCENARIOS[0]) => {
    setScenario(sc);
    setProbAId(sc.probA.problemId);
    setProbATitle(sc.probA.title);
    setProbADesc(sc.probA.description);
    setProbALat(sc.probA.lat);
    setProbALong(sc.probA.long);
    setProbAPrimary(sc.probA.primaryDomain || '');
    setProbASub(sc.probA.subcategory || '');

    setProbBId(sc.probB.problemId);
    setProbBTitle(sc.probB.title);
    setProbBDesc(sc.probB.description);
    setProbBLat(sc.probB.lat);
    setProbBLong(sc.probB.long);
    setProbBPrimary(sc.probB.primaryDomain || '');
    setProbBSub(sc.probB.subcategory || '');
  };

  const handleRunDuplicateCheck = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setResult(null);

    const payload = {
      problem: {
        problemId: probBId,
        title: probBTitle,
        description: probBDesc,
        location: probBLat !== undefined && probBLong !== undefined ? { lat: probBLat, long: probBLong, address: scenario.probB.address } : undefined,
        primaryDomain: probBPrimary && probBPrimary.trim() ? probBPrimary.trim() : undefined,
        subcategory: probBSub && probBSub.trim() ? probBSub.trim() : undefined,
      },
      candidates: [
        {
          problemId: probAId,
          title: probATitle,
          description: probADesc,
          location: probALat !== undefined && probALong !== undefined ? { lat: probALat, long: probALong, address: scenario.probA.address } : undefined,
          primaryDomain: probAPrimary && probAPrimary.trim() ? probAPrimary.trim() : undefined,
          subcategory: probASub && probASub.trim() ? probASub.trim() : undefined,
        },
      ],
      topK: 10,
    };

    const res = await duplicateApi.checkDuplicates(payload);
    setInspector(res.inspector);
    if (res.data) {
      setResult(res.data);
    }
    setLoading(false);
  };

  const match = result?.duplicateCandidates?.[0];

  const renderStateBadge = (state?: string) => {
    if (state === 'MATCH') {
      return (
        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-950 text-emerald-300 border border-emerald-700">
          <CheckCircle2 className="w-3 h-3" /> MATCH
        </span>
      );
    }
    if (state === 'MISMATCH') {
      return (
        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-bold bg-rose-950 text-rose-300 border border-rose-700">
          <XCircle className="w-3 h-3" /> MISMATCH
        </span>
      );
    }
    if (state === 'AVAILABLE') {
      return (
        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-bold bg-cyan-950 text-cyan-300 border border-cyan-700">
          <CheckCircle2 className="w-3 h-3" /> AVAILABLE
        </span>
      );
    }
    if (state === 'UNAVAILABLE') {
      return (
        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-bold bg-slate-800 text-slate-400 border border-slate-700">
          <HelpCircle className="w-3 h-3" /> UNAVAILABLE
        </span>
      );
    }
    return (
      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-bold bg-amber-950 text-amber-300 border border-amber-800">
        <HelpCircle className="w-3 h-3" /> UNKNOWN / NOT PROVIDED
      </span>
    );
  };

  return (
    <div className="space-y-6">
      {/* Engine Overview */}
      <div className="p-5 rounded-xl bg-slate-900 border border-slate-800 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h2 className="text-lg font-bold text-slate-100 flex items-center gap-2">
            <Layers className="w-5 h-5 text-purple-400" />
            <span>Duplicate Detection Engine Lab (`POST /duplicate-check` @ Port 8001)</span>
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Surfaces semantic vector similarity (`BAAI/bge-small-en-v1.5`), Available-Signal Normalized Scoring, taxonomy state analysis, and Haversine distance.
          </p>
        </div>
        <div className="flex items-center gap-3 shrink-0">
          <span className="px-2.5 py-1 rounded font-mono text-xs bg-purple-950/80 text-purple-300 border border-purple-800">
            Engine Version: {result?.scoringVersion || 'duplicate-v2'}
          </span>
          <label className="flex items-center gap-2 text-xs text-slate-300 font-semibold cursor-pointer bg-slate-800 px-3 py-1.5 rounded border border-slate-700 hover:bg-slate-700 transition">
            <input
              type="checkbox"
              checked={debugMode}
              onChange={(e) => setDebugMode(e.target.checked)}
              className="rounded accent-purple-600"
            />
            <span>Developer Score Details</span>
          </label>
        </div>
      </div>

      {/* Human Decision Boundary Notice */}
      <div className="text-xs font-mono text-amber-400 bg-amber-950/60 border border-amber-800/80 px-3.5 py-2 rounded-lg flex items-center gap-2">
        <ShieldAlert className="w-4 h-4 shrink-0 text-amber-400" />
        <span>HUMAN REVIEW BOUNDARY: AI engine identifies and ranks candidate recommendations only. Automatic record merging or deletion is strictly prohibited.</span>
      </div>

      {/* Preset Scenarios */}
      <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-2">
        <div className="text-xs font-bold text-slate-300 flex items-center gap-1.5 mb-2">
          <Sparkles className="w-4 h-4 text-purple-400" />
          <span>Duplicate Test Scenarios (Click to load):</span>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-2 text-xs">
          {DUPLICATE_SCENARIOS.map((sc, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => applyScenario(sc)}
              className={`text-left p-2.5 rounded-lg border transition-colors ${
                scenario.name === sc.name
                  ? 'bg-purple-950/80 border-purple-600 text-purple-200'
                  : 'bg-slate-800/80 hover:bg-slate-800 border-slate-700/80 text-slate-300'
              }`}
            >
              <div className="font-semibold text-xs truncate">{sc.name}</div>
              <div className="text-[10px] text-slate-400 truncate mt-0.5">{sc.expected}</div>
            </button>
          ))}
        </div>
      </div>

      {/* Dual Problem Form */}
      <form onSubmit={handleRunDuplicateCheck} className="space-y-4 text-xs">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Problem A (Candidate Master) */}
          <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-3">
            <div className="font-bold text-cyan-400 border-b border-slate-800 pb-2 flex items-center justify-between">
              <span>Problem A (Existing Master in System)</span>
              <span className="font-mono text-[11px] text-slate-400">{probAId}</span>
            </div>

            <div>
              <label className="block text-slate-400 font-semibold mb-1">Title A</label>
              <input
                type="text"
                required
                value={probATitle}
                onChange={(e) => setProbATitle(e.target.value)}
                className="w-full px-3 py-2 rounded bg-slate-800 border border-slate-700 text-slate-200 font-medium"
              />
            </div>

            <div>
              <label className="block text-slate-400 font-semibold mb-1">Description A</label>
              <textarea
                required
                rows={3}
                value={probADesc}
                onChange={(e) => setProbADesc(e.target.value)}
                className="w-full px-3 py-2 rounded bg-slate-800 border border-slate-700 text-slate-200"
              />
            </div>

            <div className="grid grid-cols-2 gap-2">
              <div>
                <label className="block text-slate-400 font-semibold mb-1">Primary Domain A</label>
                <input
                  type="text"
                  value={probAPrimary}
                  placeholder="(Optional taxonomy)"
                  onChange={(e) => setProbAPrimary(e.target.value)}
                  className="w-full px-2.5 py-1.5 rounded bg-slate-800 border border-slate-700 text-slate-200"
                />
              </div>
              <div>
                <label className="block text-slate-400 font-semibold mb-1">Subcategory A</label>
                <input
                  type="text"
                  value={probASub}
                  placeholder="(Optional taxonomy)"
                  onChange={(e) => setProbASub(e.target.value)}
                  className="w-full px-2.5 py-1.5 rounded bg-slate-800 border border-slate-700 text-slate-200"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-2 font-mono">
              <div>
                <label className="block text-slate-400 text-[10px]">Latitude A</label>
                <input
                  type="number"
                  step="any"
                  value={probALat !== undefined ? probALat : ''}
                  onChange={(e) => setProbALat(e.target.value !== '' ? parseFloat(e.target.value) : undefined)}
                  className="w-full px-2.5 py-1.5 rounded bg-slate-800 border border-slate-700 text-slate-200"
                />
              </div>
              <div>
                <label className="block text-slate-400 text-[10px]">Longitude A</label>
                <input
                  type="number"
                  step="any"
                  value={probALong !== undefined ? probALong : ''}
                  onChange={(e) => setProbALong(e.target.value !== '' ? parseFloat(e.target.value) : undefined)}
                  className="w-full px-2.5 py-1.5 rounded bg-slate-800 border border-slate-700 text-slate-200"
                />
              </div>
            </div>
          </div>

          {/* Problem B (Query Submission) */}
          <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-3">
            <div className="font-bold text-purple-400 border-b border-slate-800 pb-2 flex items-center justify-between">
              <span>Problem B (New Incoming Submission)</span>
              <span className="font-mono text-[11px] text-slate-400">{probBId}</span>
            </div>

            <div>
              <label className="block text-slate-400 font-semibold mb-1">Title B</label>
              <input
                type="text"
                required
                value={probBTitle}
                onChange={(e) => setProbBTitle(e.target.value)}
                className="w-full px-3 py-2 rounded bg-slate-800 border border-slate-700 text-slate-200 font-medium"
              />
            </div>

            <div>
              <label className="block text-slate-400 font-semibold mb-1">Description B</label>
              <textarea
                required
                rows={3}
                value={probBDesc}
                onChange={(e) => setProbBDesc(e.target.value)}
                className="w-full px-3 py-2 rounded bg-slate-800 border border-slate-700 text-slate-200"
              />
            </div>

            <div className="grid grid-cols-2 gap-2">
              <div>
                <label className="block text-slate-400 font-semibold mb-1">Primary Domain B</label>
                <input
                  type="text"
                  value={probBPrimary}
                  placeholder="(Optional taxonomy)"
                  onChange={(e) => setProbBPrimary(e.target.value)}
                  className="w-full px-2.5 py-1.5 rounded bg-slate-800 border border-slate-700 text-slate-200"
                />
              </div>
              <div>
                <label className="block text-slate-400 font-semibold mb-1">Subcategory B</label>
                <input
                  type="text"
                  value={probBSub}
                  placeholder="(Optional taxonomy)"
                  onChange={(e) => setProbBSub(e.target.value)}
                  className="w-full px-2.5 py-1.5 rounded bg-slate-800 border border-slate-700 text-slate-200"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-2 font-mono">
              <div>
                <label className="block text-slate-400 text-[10px]">Latitude B</label>
                <input
                  type="number"
                  step="any"
                  value={probBLat !== undefined ? probBLat : ''}
                  onChange={(e) => setProbBLat(e.target.value !== '' ? parseFloat(e.target.value) : undefined)}
                  className="w-full px-2.5 py-1.5 rounded bg-slate-800 border border-slate-700 text-slate-200"
                />
              </div>
              <div>
                <label className="block text-slate-400 text-[10px]">Longitude B</label>
                <input
                  type="number"
                  step="any"
                  value={probBLong !== undefined ? probBLong : ''}
                  onChange={(e) => setProbBLong(e.target.value !== '' ? parseFloat(e.target.value) : undefined)}
                  className="w-full px-2.5 py-1.5 rounded bg-slate-800 border border-slate-700 text-slate-200"
                />
              </div>
            </div>
          </div>
        </div>

        <div className="flex justify-end">
          <button
            type="submit"
            disabled={loading}
            className="flex items-center gap-2 px-5 py-2.5 rounded bg-purple-600 hover:bg-purple-500 text-white font-bold text-xs shadow transition-colors disabled:opacity-50"
          >
            <Play className="w-4 h-4 fill-white" />
            <span>{loading ? 'Running BGE-small Embeddings Engine...' : 'Run Duplicate Check'}</span>
          </button>
        </div>
      </form>

      {/* Results Breakdown Matrix */}
      {result && (
        <div className="p-5 rounded-xl bg-slate-900 border border-purple-800/80 space-y-6 text-xs">
          {/* SECTION 1: EXECUTIVE RESULT HEADER */}
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <div>
              <div className="text-purple-400 font-mono font-bold text-xs">
                Check Status: {result.status === 'candidate_found' ? 'CANDIDATE FOUND' : 'NO CANDIDATE'}
              </div>
              <h3 className="text-sm font-bold text-slate-100 mt-0.5">
                Surfaced Candidate Recommendations: {result.duplicateCandidates.length}
              </h3>
            </div>
            {match && (
              <div className="flex items-center gap-3">
                <span
                  className={`px-3.5 py-1.5 rounded-full text-xs font-bold font-mono border ${
                    match.candidateStatus === 'strong_candidate'
                      ? 'bg-rose-950 text-rose-300 border-rose-700'
                      : match.candidateStatus === 'potential_duplicate'
                      ? 'bg-amber-950 text-amber-300 border-amber-700'
                      : 'bg-slate-800 text-slate-400 border-slate-700'
                  }`}
                >
                  {match.candidateStatus === 'strong_candidate'
                    ? 'STRONG DUPLICATE CANDIDATE'
                    : match.candidateStatus === 'potential_duplicate'
                    ? 'POTENTIAL DUPLICATE CANDIDATE'
                    : 'NO CANDIDATE'}
                </span>
                <span className="text-lg font-mono font-bold text-purple-300">
                  {(match.duplicateScore * 100).toFixed(1)}%
                </span>
              </div>
            )}
          </div>

          {match ? (
            <div className="space-y-6">
              {/* SECTION 2: SCORE SUMMARY CARDS */}
              <div className="grid grid-cols-2 md:grid-cols-6 gap-3">
                <div className="p-3 rounded bg-slate-800/70 border border-slate-700">
                  <div className="text-slate-400 font-semibold">Semantic Similarity</div>
                  <div className="text-base font-mono font-bold text-cyan-300 mt-1">
                    {(match.semanticSimilarity * 100).toFixed(1)}%
                  </div>
                  <div className="text-[10px] text-slate-500 mt-0.5">BGE-small 384d Cosine</div>
                </div>

                <div className="p-3 rounded bg-slate-800/70 border border-slate-700">
                  <div className="text-slate-400 font-semibold">Location Signal</div>
                  <div className="text-base font-mono font-bold text-emerald-300 mt-1">
                    {match.locationDistanceKm !== null && match.locationDistanceKm !== undefined
                      ? `${match.locationDistanceKm.toFixed(2)} km`
                      : 'N/A'}
                  </div>
                  <div className="mt-1">{renderStateBadge(match.signalStates?.location)}</div>
                </div>

                <div className="p-3 rounded bg-slate-800/70 border border-slate-700">
                  <div className="text-slate-400 font-semibold">Primary Domain</div>
                  <div className="mt-2">{renderStateBadge(match.signalStates?.primaryDomain)}</div>
                </div>

                <div className="p-3 rounded bg-slate-800/70 border border-slate-700">
                  <div className="text-slate-400 font-semibold">Subcategory</div>
                  <div className="mt-2">{renderStateBadge(match.signalStates?.subcategory)}</div>
                </div>

                <div className="p-3 rounded bg-slate-800/70 border border-slate-700">
                  <div className="text-slate-400 font-semibold">Secondary Overlap</div>
                  <div className="mt-2">{renderStateBadge(match.signalStates?.secondaryDomains)}</div>
                </div>

                <div className="p-3 rounded bg-purple-950/60 border border-purple-700">
                  <div className="text-purple-300 font-semibold">Final Composite Score</div>
                  <div className="text-base font-mono font-bold text-purple-200 mt-1">
                    {(match.duplicateScore * 100).toFixed(1)}%
                  </div>
                  <div className="text-[10px] text-purple-400 mt-0.5">Available-Weight Normalized</div>
                </div>
              </div>

              {/* SECTION 3: SCORE CONTRIBUTION BREAKDOWN */}
              <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-3">
                <div className="flex items-center justify-between">
                  <div className="text-sm font-bold text-slate-200 flex items-center gap-2">
                    <Calculator className="w-4 h-4 text-purple-400" />
                    <span>Score Calculation & Contribution Breakdown</span>
                  </div>
                  <div className="text-xs font-mono text-purple-300">
                    Available Weight Denominator: {((match.availableWeight || 1.0) * 100).toFixed(0)}%
                  </div>
                </div>

                <div className="overflow-x-auto">
                  <table className="w-full text-left font-mono text-xs border-collapse">
                    <thead>
                      <tr className="border-b border-slate-800 text-slate-400">
                        <th className="py-2 px-3">Signal</th>
                        <th className="py-2 px-3">State</th>
                        <th className="py-2 px-3">Raw Value</th>
                        <th className="py-2 px-3">Base Weight</th>
                        <th className="py-2 px-3">Weighted Contribution</th>
                        <th className="py-2 px-3">Used in Score?</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800/60">
                      {match.scoreBreakdown &&
                        Object.entries(match.scoreBreakdown).map(([key, details]) => (
                          <tr key={key} className={details.used ? 'bg-slate-900/60' : 'opacity-60'}>
                            <td className="py-2 px-3 font-semibold text-slate-200 capitalize">{key}</td>
                            <td className="py-2 px-3">{renderStateBadge(details.state)}</td>
                            <td className="py-2 px-3 text-cyan-300">
                              {details.rawValue !== null && details.rawValue !== undefined
                                ? details.rawValue.toFixed(3)
                                : '—'}
                            </td>
                            <td className="py-2 px-3 text-slate-300">{(details.weight * 100).toFixed(0)}%</td>
                            <td className="py-2 px-3 text-purple-300">
                              {details.contribution !== null && details.contribution !== undefined
                                ? details.contribution.toFixed(3)
                                : '—'}
                            </td>
                            <td className="py-2 px-3 font-bold">
                              {details.used ? (
                                <span className="text-emerald-400">YES</span>
                              ) : (
                                <span className="text-slate-500">NO (Excluded)</span>
                              )}
                            </td>
                          </tr>
                        ))}
                    </tbody>
                  </table>
                </div>

                {/* SECTION 4: FORMULA VIEW */}
                <div className="pt-2 border-t border-slate-800">
                  <button
                    type="button"
                    onClick={() => setShowFormula(!showFormula)}
                    className="flex items-center gap-1.5 text-xs text-purple-400 font-semibold hover:text-purple-300"
                  >
                    <span>Scoring Formula Expression</span>
                    {showFormula ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
                  </button>

                  {showFormula && match.scoreBreakdown && (
                    <div className="mt-2 p-3 rounded bg-slate-900 border border-slate-800 font-mono text-xs text-slate-300 space-y-1">
                      <div>
                        Normalized Score = Sum(Available Contributions) / Sum(Available Weights)
                      </div>
                      <div className="text-purple-300 font-bold">
                        = ({' '}
                        {Object.values(match.scoreBreakdown)
                          .filter((d) => d.used)
                          .map((d) => `${d.weight.toFixed(2)} × ${(d.rawValue || 0).toFixed(3)}`)
                          .join(' + ')}{' '}
                        ) / {match.availableWeight?.toFixed(2)}
                      </div>
                      <div className="text-emerald-400 font-bold">
                        = {(match.duplicateScore * 100).toFixed(1)}%
                      </div>
                    </div>
                  )}
                </div>
              </div>

              {/* SECTION 5: SIGNAL COMPARISON TABLE */}
              <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-3">
                <div className="text-sm font-bold text-slate-200">Structured Signal Comparison Matrix</div>
                <div className="overflow-x-auto">
                  <table className="w-full text-left font-mono text-xs border-collapse">
                    <thead>
                      <tr className="border-b border-slate-800 text-slate-400">
                        <th className="py-2 px-3">Signal</th>
                        <th className="py-2 px-3 text-cyan-400">Problem A (Master)</th>
                        <th className="py-2 px-3 text-purple-400">Problem B (Candidate)</th>
                        <th className="py-2 px-3">Evaluation Result</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800/60">
                      <tr>
                        <td className="py-2 px-3 font-semibold text-slate-200">Primary Domain</td>
                        <td className="py-2 px-3 text-slate-300">{scenario.probA.primaryDomain || 'Not provided'}</td>
                        <td className="py-2 px-3 text-slate-300">{scenario.probB.primaryDomain || 'Not provided'}</td>
                        <td className="py-2 px-3">{renderStateBadge(match.signalStates?.primaryDomain)}</td>
                      </tr>
                      <tr>
                        <td className="py-2 px-3 font-semibold text-slate-200">Subcategory</td>
                        <td className="py-2 px-3 text-slate-300">{scenario.probA.subcategory || 'Not provided'}</td>
                        <td className="py-2 px-3 text-slate-300">{scenario.probB.subcategory || 'Not provided'}</td>
                        <td className="py-2 px-3">{renderStateBadge(match.signalStates?.subcategory)}</td>
                      </tr>
                      <tr>
                        <td className="py-2 px-3 font-semibold text-slate-200">Location Coordinates</td>
                        <td className="py-2 px-3 text-slate-300">
                          {probALat !== undefined && probALong !== undefined ? `${probALat}, ${probALong}` : 'Not provided'}
                        </td>
                        <td className="py-2 px-3 text-slate-300">
                          {probBLat !== undefined && probBLong !== undefined ? `${probBLat}, ${probBLong}` : 'Not provided'}
                        </td>
                        <td className="py-2 px-3 font-bold text-emerald-400">
                          {match.locationDistanceKm !== null && match.locationDistanceKm !== undefined
                            ? `${match.locationDistanceKm.toFixed(2)} km`
                            : 'UNAVAILABLE'}
                        </td>
                      </tr>
                      <tr>
                        <td className="py-2 px-3 font-semibold text-slate-200">Semantic Similarity</td>
                        <td className="py-2 px-3 text-slate-400" colSpan={2}>
                          Title & Description embedding cosine comparison
                        </td>
                        <td className="py-2 px-3 font-bold text-cyan-300 font-mono">
                          {(match.semanticSimilarity * 100).toFixed(1)}% (Cosine)
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>

              {/* SECTION 6: CATEGORIZED REASONS */}
              <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-3">
                <div className="text-sm font-bold text-slate-200">Explainable Decision Evidence</div>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                  <div className="p-3 rounded bg-emerald-950/40 border border-emerald-800/60 space-y-1">
                    <div className="text-xs font-bold text-emerald-300 flex items-center gap-1">
                      <CheckCircle2 className="w-3.5 h-3.5" /> Positive Signals
                    </div>
                    <ul className="list-disc list-inside text-xs font-mono text-emerald-200 space-y-0.5">
                      {match.reasons
                        .filter(
                          (r) =>
                            r.startsWith('High') ||
                            r.startsWith('Same') ||
                            r.startsWith('Geographically very close') ||
                            r.startsWith('Geographically nearby') ||
                            r.startsWith('Surfaced')
                        )
                        .map((r, idx) => (
                          <li key={idx}>{r}</li>
                        ))}
                    </ul>
                  </div>

                  <div className="p-3 rounded bg-amber-950/40 border border-amber-800/60 space-y-1">
                    <div className="text-xs font-bold text-amber-300 flex items-center gap-1">
                      <HelpCircle className="w-3.5 h-3.5" /> Missing / Unknown Signals
                    </div>
                    <ul className="list-disc list-inside text-xs font-mono text-amber-200 space-y-0.5">
                      {match.reasons
                        .filter(
                          (r) =>
                            r.includes('not provided') ||
                            r.includes('missing or incomplete') ||
                            r.includes('unavailable')
                        )
                        .map((r, idx) => (
                          <li key={idx}>{r}</li>
                        ))}
                    </ul>
                  </div>

                  <div className="p-3 rounded bg-rose-950/40 border border-rose-800/60 space-y-1">
                    <div className="text-xs font-bold text-rose-300 flex items-center gap-1">
                      <XCircle className="w-3.5 h-3.5" /> Negative / Contradictory Signals
                    </div>
                    <ul className="list-disc list-inside text-xs font-mono text-rose-200 space-y-0.5">
                      {match.reasons
                        .filter(
                          (r) =>
                            r.startsWith('Different') ||
                            r.startsWith('Low') ||
                            r.startsWith('Contradictory') ||
                            r.startsWith('Geographically distant')
                        )
                        .map((r, idx) => (
                          <li key={idx}>{r}</li>
                        ))}
                      {match.reasons.filter(
                        (r) =>
                          r.startsWith('Different') ||
                          r.startsWith('Low') ||
                          r.startsWith('Contradictory') ||
                          r.startsWith('Geographically distant')
                      ).length === 0 && <li className="italic text-slate-500">None detected</li>}
                    </ul>
                  </div>
                </div>
              </div>

              {/* SECTION 7, 8, 9: TECHNICAL EMBEDDING & THRESHOLD INFORMATION */}
              <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-3">
                <button
                  type="button"
                  onClick={() => setShowEmbeddings(!showEmbeddings)}
                  className="flex items-center gap-1.5 text-xs text-purple-400 font-semibold hover:text-purple-300"
                >
                  <Cpu className="w-4 h-4" />
                  <span>Technical Embedding & Threshold Details</span>
                  {showEmbeddings ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
                </button>

                {showEmbeddings && (
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 font-mono text-xs pt-2">
                    <div className="p-3 rounded bg-slate-950 border border-slate-800 space-y-1">
                      <div className="font-bold text-slate-200">Embedding Specs</div>
                      <div className="text-slate-400">Model: BAAI/bge-small-en-v1.5</div>
                      <div className="text-slate-400">Dimension: 384 float32</div>
                      <div className="text-slate-400">Metric: Cosine Similarity</div>
                      <div className="text-slate-400">Normalized: Yes (L2 norm)</div>
                    </div>

                    <div className="p-3 rounded bg-slate-950 border border-slate-800 space-y-1">
                      <div className="font-bold text-slate-200">Location Settings</div>
                      <div className="text-slate-400">Formula: Haversine distance</div>
                      <div className="text-slate-400">Max Radius: 5.0 km</div>
                      <div className="text-slate-400">Distance: {match.locationDistanceKm ?? 'N/A'} km</div>
                      <div className="text-slate-400">Score: {match.locationScore.toFixed(3)}</div>
                    </div>

                    <div className="p-3 rounded bg-slate-950 border border-slate-800 space-y-1">
                      <div className="font-bold text-slate-200">Threshold Decision Rules</div>
                      <div className="text-slate-400">Candidate Threshold: 0.75</div>
                      <div className="text-slate-400">Strong Candidate Threshold: 0.85</div>
                      <div className="text-purple-300 font-bold">Evaluated Score: {match.duplicateScore.toFixed(3)}</div>
                      <div className="text-emerald-400 font-bold">
                        Decision: {match.candidateStatus.toUpperCase()}
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* SECTION 10: DEBUG MODE JSON INSPECTOR */}
              {debugMode && (
                <div className="p-4 rounded-xl bg-slate-950 border border-purple-900/60 space-y-2">
                  <div className="text-xs font-bold font-mono text-purple-300 flex items-center gap-2">
                    <Sliders className="w-4 h-4" />
                    <span>Developer Score Details (Raw API Payload)</span>
                  </div>
                  <JsonViewer data={match} />
                </div>
              )}
            </div>
          ) : (
            <div className="text-slate-400 italic">No duplicate candidates surfaced above threshold.</div>
          )}
        </div>
      )}

      {inspector && <RequestResponseInspector inspector={inspector} />}
    </div>
  );
};

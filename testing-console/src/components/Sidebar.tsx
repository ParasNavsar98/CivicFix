import React from 'react';
import {
  LayoutDashboard,
  HeartPulse,
  FilePlus,
  Brain,
  CopyCheck,
  Workflow,
  Inbox,
  CheckSquare,
  Building2,
  Clock,
  ShieldCheck,
  AlertTriangle,
  History,
  FileSearch,
} from 'lucide-react';

export type NavTab =
  | 'dashboard'
  | 'health'
  | 'problem-test'
  | 'classification-lab'
  | 'duplicate-lab'
  | 'e2e-pipeline'
  | 'reviewer-queue'
  | 'reviewer-actions'
  | 'routing'
  | 'timeline'
  | 'audit'
  | 'security'
  | 'failure'
  | 'history';

interface SidebarProps {
  activeTab: NavTab;
  onTabChange: (tab: NavTab) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ activeTab, onTabChange }) => {
  const items: { id: NavTab; label: string; icon: React.ReactNode; category?: string }[] = [
    { id: 'dashboard', label: 'Dashboard', icon: <LayoutDashboard className="w-4 h-4" /> },
    { id: 'health', label: 'System Health Probes', icon: <HeartPulse className="w-4 h-4" /> },

    { id: 'problem-test', label: 'Real Problem Test', icon: <FilePlus className="w-4 h-4" />, category: 'Core Pipeline' },
    { id: 'classification-lab', label: 'Classification Lab', icon: <Brain className="w-4 h-4" />, category: 'Core Pipeline' },
    { id: 'duplicate-lab', label: 'Duplicate Detection Lab', icon: <CopyCheck className="w-4 h-4" />, category: 'Core Pipeline' },
    { id: 'e2e-pipeline', label: 'E2E Session Wizard', icon: <Workflow className="w-4 h-4" />, category: 'Core Pipeline' },

    { id: 'reviewer-queue', label: 'Reviewer Queue', icon: <Inbox className="w-4 h-4" />, category: 'Review & Routing' },
    { id: 'reviewer-actions', label: 'Reviewer Actions', icon: <CheckSquare className="w-4 h-4" />, category: 'Review & Routing' },
    { id: 'routing', label: 'Government Routing', icon: <Building2 className="w-4 h-4" />, category: 'Review & Routing' },

    { id: 'timeline', label: 'Citizen Timeline', icon: <Clock className="w-4 h-4" />, category: 'Observability' },
    { id: 'audit', label: 'Audit Log Viewer', icon: <FileSearch className="w-4 h-4" />, category: 'Observability' },

    { id: 'security', label: 'Security & RBAC Tests', icon: <ShieldCheck className="w-4 h-4" />, category: 'QA & Resilience' },
    { id: 'failure', label: 'Failure Testing', icon: <AlertTriangle className="w-4 h-4" />, category: 'QA & Resilience' },
    { id: 'history', label: 'Test History', icon: <History className="w-4 h-4" />, category: 'QA & Resilience' },
  ];

  let currentCategory = '';

  return (
    <aside className="w-64 bg-slate-900 border-r border-slate-800 flex flex-col shrink-0 min-h-[calc(100vh-65px)]">
      <nav className="p-3 space-y-1 overflow-y-auto">
        {items.map((item) => {
          const showCategoryHeader = item.category && item.category !== currentCategory;
          if (item.category) currentCategory = item.category;

          return (
            <React.Fragment key={item.id}>
              {showCategoryHeader && (
                <div className="pt-3 pb-1 px-3 text-[10px] font-mono font-bold tracking-wider text-slate-500 uppercase">
                  {item.category}
                </div>
              )}
              <button
                onClick={() => onTabChange(item.id)}
                className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-xs font-medium transition-all ${
                  activeTab === item.id
                    ? 'bg-cyan-950 text-cyan-300 font-semibold border border-cyan-800/80 shadow-sm'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
                }`}
              >
                <span className={activeTab === item.id ? 'text-cyan-400' : 'text-slate-400'}>
                  {item.icon}
                </span>
                <span>{item.label}</span>
              </button>
            </React.Fragment>
          );
        })}
      </nav>
    </aside>
  );
};

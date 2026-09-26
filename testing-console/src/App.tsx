import React, { useState } from 'react';
import { Header } from './components/Header';
import { Sidebar, NavTab } from './components/Sidebar';
import { DashboardView } from './views/DashboardView';
import { SystemHealthView } from './views/SystemHealthView';
import { RealProblemTestView } from './views/RealProblemTestView';
import { ClassificationLabView } from './views/ClassificationLabView';
import { DuplicateDetectionLabView } from './views/DuplicateDetectionLabView';
import { E2EPipelineView } from './views/E2EPipelineView';
import { ReviewerQueueView } from './views/ReviewerQueueView';
import { ReviewerActionsView } from './views/ReviewerActionsView';
import { GovernmentRoutingView } from './views/GovernmentRoutingView';
import { TimelineView } from './views/TimelineView';
import { AuditView } from './views/AuditView';
import { SecurityRbacView } from './views/SecurityRbacView';
import { FailureTestingView } from './views/FailureTestingView';
import { TestHistoryView } from './views/TestHistoryView';

export function App() {
  const [activeTab, setActiveTab] = useState<NavTab>('dashboard');

  const renderActiveView = () => {
    switch (activeTab) {
      case 'dashboard':
        return <DashboardView onNavigate={(tab) => setActiveTab(tab)} />;
      case 'health':
        return <SystemHealthView />;
      case 'problem-test':
        return <RealProblemTestView onNavigate={(tab) => setActiveTab(tab)} />;
      case 'classification-lab':
        return <ClassificationLabView />;
      case 'duplicate-lab':
        return <DuplicateDetectionLabView />;
      case 'e2e-pipeline':
        return <E2EPipelineView />;
      case 'reviewer-queue':
        return <ReviewerQueueView onNavigate={(tab) => setActiveTab(tab)} />;
      case 'reviewer-actions':
        return <ReviewerActionsView onNavigate={(tab) => setActiveTab(tab)} />;
      case 'routing':
        return <GovernmentRoutingView />;
      case 'timeline':
        return <TimelineView />;
      case 'audit':
        return <AuditView />;
      case 'security':
        return <SecurityRbacView />;
      case 'failure':
        return <FailureTestingView />;
      case 'history':
        return <TestHistoryView />;
      default:
        return <DashboardView onNavigate={(tab) => setActiveTab(tab)} />;
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans antialiased selection:bg-cyan-500 selection:text-slate-950">
      <Header />
      <div className="flex flex-1 overflow-hidden">
        <Sidebar activeTab={activeTab} onTabChange={(tab) => setActiveTab(tab)} />
        <main className="flex-1 p-6 overflow-y-auto max-w-7xl mx-auto">
          {renderActiveView()}
        </main>
      </div>
    </div>
  );
}

export default App;

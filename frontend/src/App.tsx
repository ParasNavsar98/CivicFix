import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './services/auth';
import { AppShell } from './components/layout/AppShell';
import { ProtectedRoute } from './components/layout/ProtectedRoute';

// Public Pages
import { LandingPage } from './pages/public/LandingPage';

// Auth Pages
import { RoleSelectionPage } from './pages/auth/RoleSelectionPage';
import { CitizenLoginPage } from './pages/auth/CitizenLoginPage';
import { GovernmentLoginPage } from './pages/auth/GovernmentLoginPage';
import { UniversityLoginPage } from './pages/auth/UniversityLoginPage';
import { IndustryLoginPage } from './pages/auth/IndustryLoginPage';

// Citizen Portal
import { CitizenDashboard } from './pages/citizen/CitizenDashboard';
import { ReportProblemPage } from './pages/citizen/ReportProblemPage';
import { CitizenProblemsPage } from './pages/citizen/CitizenProblemsPage';
import { ProblemDetailPage } from './pages/citizen/ProblemDetailPage';
import { CitizenClarificationsPage } from './pages/citizen/CitizenClarificationsPage';
import { CitizenMapPage } from './pages/citizen/CitizenMapPage';
import { CitizenProfilePage } from './pages/citizen/CitizenProfilePage';

// Government & Review Portal
import { GovernmentDashboard } from './pages/government/GovernmentDashboard';
import { ReviewQueuePage } from './pages/government/ReviewQueuePage';
import { ReviewDetailPage } from './pages/government/ReviewDetailPage';
import { DuplicateReviewPage } from './pages/government/DuplicateReviewPage';
import { GovernmentCasesPage } from './pages/government/GovernmentCasesPage';
import { VerificationPage } from './pages/government/VerificationPage';
import { RoutingPage } from './pages/government/RoutingPage';
import { AnalyticsPage } from './pages/government/AnalyticsPage';

// University & Research Portal
import { UniversityDashboard } from './pages/university/UniversityDashboard';
import { MatchDetailPage } from './pages/university/MatchDetailPage';
import { AssignmentsPage } from './pages/university/AssignmentsPage';
import { ProjectsPage } from './pages/university/ProjectsPage';
import { UniversityProfilePage } from './pages/university/UniversityProfilePage';

// Industry & CSR Portal
import { IndustryDashboard } from './pages/industry/IndustryDashboard';
import { MarketplacePage } from './pages/industry/MarketplacePage';
import { MyInterestsPage } from './pages/industry/MyInterestsPage';
import { CollaborationsPage } from './pages/industry/CollaborationsPage';
import { OrganizationProfilePage } from './pages/industry/OrganizationProfilePage';

export const App: React.FC = () => {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          {/* Public Landing & Role Selection */}
          <Route path="/" element={<LandingPage />} />
          <Route path="/login" element={<RoleSelectionPage />} />
          <Route path="/login/citizen" element={<CitizenLoginPage />} />
          <Route path="/login/government" element={<GovernmentLoginPage />} />
          <Route path="/login/university" element={<UniversityLoginPage />} />
          <Route path="/login/industry" element={<IndustryLoginPage />} />

          {/* Citizen Portal */}
          <Route element={<ProtectedRoute allowedRoles={['citizen']} />}>
            <Route element={<AppShell />}>
              <Route path="/citizen/dashboard" element={<CitizenDashboard />} />
              <Route path="/citizen/report" element={<ReportProblemPage />} />
              <Route path="/citizen/problems" element={<CitizenProblemsPage />} />
              <Route path="/citizen/problems/:id" element={<ProblemDetailPage />} />
              <Route path="/citizen/map" element={<CitizenMapPage />} />
              <Route path="/citizen/clarifications" element={<CitizenClarificationsPage />} />
              <Route path="/citizen/notifications" element={<CitizenProblemsPage />} />
              <Route path="/citizen/profile" element={<CitizenProfilePage />} />
            </Route>
          </Route>

          {/* Government & Review Portal */}
          <Route element={<ProtectedRoute allowedRoles={['government']} />}>
            <Route element={<AppShell />}>
              <Route path="/government/dashboard" element={<GovernmentDashboard />} />
              <Route path="/government/review" element={<ReviewQueuePage />} />
              <Route path="/government/review/:id" element={<ReviewDetailPage />} />
              <Route path="/government/duplicates" element={<DuplicateReviewPage />} />
              <Route path="/government/cases" element={<GovernmentCasesPage />} />
              <Route path="/government/verification" element={<VerificationPage />} />
              <Route path="/government/routing" element={<RoutingPage />} />
              <Route path="/government/escalations" element={<ReviewQueuePage />} />
              <Route path="/government/analytics" element={<AnalyticsPage />} />
              <Route path="/government/notifications" element={<ReviewQueuePage />} />
            </Route>
          </Route>

          {/* University & Research Portal */}
          <Route element={<ProtectedRoute allowedRoles={['university']} />}>
            <Route element={<AppShell />}>
              <Route path="/university/dashboard" element={<UniversityDashboard />} />
              <Route path="/university/matches" element={<UniversityDashboard />} />
              <Route path="/university/matches/:id" element={<MatchDetailPage />} />
              <Route path="/university/assignments" element={<AssignmentsPage />} />
              <Route path="/university/projects" element={<ProjectsPage />} />
              <Route path="/university/teams" element={<ProjectsPage />} />
              <Route path="/university/faculty" element={<ProjectsPage />} />
              <Route path="/university/milestones" element={<ProjectsPage />} />
              <Route path="/university/reports" element={<ProjectsPage />} />
              <Route path="/university/profile" element={<UniversityProfilePage />} />
              <Route path="/university/notifications" element={<AssignmentsPage />} />
            </Route>
          </Route>

          {/* Industry & CSR Portal */}
          <Route element={<ProtectedRoute allowedRoles={['industry']} />}>
            <Route element={<AppShell />}>
              <Route path="/industry/dashboard" element={<IndustryDashboard />} />
              <Route path="/industry/marketplace" element={<MarketplacePage />} />
              <Route path="/industry/interests" element={<MyInterestsPage />} />
              <Route path="/industry/offers" element={<MyInterestsPage />} />
              <Route path="/industry/collaborations" element={<CollaborationsPage />} />
              <Route path="/industry/profile" element={<OrganizationProfilePage />} />
              <Route path="/industry/notifications" element={<MyInterestsPage />} />
            </Route>
          </Route>

          {/* Catch-all redirect */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
};

export default App;

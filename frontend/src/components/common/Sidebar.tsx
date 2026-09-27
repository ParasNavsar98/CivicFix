import React from 'react';
import { NavLink } from 'react-router-dom';
import { useAuth } from '../../services/auth';
import { UserRole } from '../../types';
import {
  LayoutDashboard,
  PlusCircle,
  FileText,
  MapPin,
  HelpCircle,
  Bell,
  User,
  ShieldAlert,
  Layers,
  Briefcase,
  CheckSquare,
  Compass,
  BarChart3,
  Award,
  BookOpen,
  Users,
  Building,
  Target,
  FileBarChart,
  ShoppingBag,
  HeartHandshake,
  Handshake,
} from 'lucide-react';

interface SidebarProps {
  onCloseMobile?: () => void;
}

interface MenuItem {
  to: string;
  label: string;
  icon: React.ReactNode;
}

export const Sidebar: React.FC<SidebarProps> = ({ onCloseMobile }) => {
  const { user } = useAuth();
  const role = user?.role || 'citizen';

  const menuConfig: Record<UserRole, MenuItem[]> = {
    citizen: [
      { to: '/citizen/dashboard', label: 'Dashboard', icon: <LayoutDashboard className="w-4 h-4" /> },
      { to: '/citizen/report', label: 'Report Problem', icon: <PlusCircle className="w-4 h-4" /> },
      { to: '/citizen/problems', label: 'My Problems', icon: <FileText className="w-4 h-4" /> },
      { to: '/citizen/map', label: 'Problem Map', icon: <MapPin className="w-4 h-4" /> },
      { to: '/citizen/clarifications', label: 'Clarifications', icon: <HelpCircle className="w-4 h-4" /> },
      { to: '/citizen/notifications', label: 'Notifications', icon: <Bell className="w-4 h-4" /> },
      { to: '/citizen/profile', label: 'Profile', icon: <User className="w-4 h-4" /> },
    ],
    government: [
      { to: '/government/dashboard', label: 'Dashboard', icon: <LayoutDashboard className="w-4 h-4" /> },
      { to: '/government/review', label: 'Review Queue', icon: <ShieldAlert className="w-4 h-4" /> },
      { to: '/government/duplicates', label: 'Duplicate Review', icon: <Layers className="w-4 h-4" /> },
      { to: '/government/cases', label: 'Government Cases', icon: <Briefcase className="w-4 h-4" /> },
      { to: '/government/verification', label: 'Verification', icon: <CheckSquare className="w-4 h-4" /> },
      { to: '/government/routing', label: 'Routing', icon: <Compass className="w-4 h-4" /> },
      { to: '/government/escalations', label: 'Escalations', icon: <ShieldAlert className="w-4 h-4 text-[#B83A3A]" /> },
      { to: '/government/analytics', label: 'Analytics', icon: <BarChart3 className="w-4 h-4" /> },
      { to: '/government/notifications', label: 'Notifications', icon: <Bell className="w-4 h-4" /> },
    ],
    university: [
      { to: '/university/dashboard', label: 'Dashboard', icon: <LayoutDashboard className="w-4 h-4" /> },
      { to: '/university/matches', label: 'Matched Problems', icon: <Award className="w-4 h-4" /> },
      { to: '/university/assignments', label: 'Assignments', icon: <BookOpen className="w-4 h-4" /> },
      { to: '/university/projects', label: 'Projects', icon: <Briefcase className="w-4 h-4" /> },
      { to: '/university/teams', label: 'Teams', icon: <Users className="w-4 h-4" /> },
      { to: '/university/faculty', label: 'Faculty', icon: <Building className="w-4 h-4" /> },
      { to: '/university/milestones', label: 'Milestones', icon: <Target className="w-4 h-4" /> },
      { to: '/university/reports', label: 'Reports', icon: <FileBarChart className="w-4 h-4" /> },
      { to: '/university/profile', label: 'University Profile', icon: <User className="w-4 h-4" /> },
      { to: '/university/notifications', label: 'Notifications', icon: <Bell className="w-4 h-4" /> },
    ],
    industry: [
      { to: '/industry/dashboard', label: 'Dashboard', icon: <LayoutDashboard className="w-4 h-4" /> },
      { to: '/industry/marketplace', label: 'Marketplace', icon: <ShoppingBag className="w-4 h-4" /> },
      { to: '/industry/interests', label: 'My Interests', icon: <HeartHandshake className="w-4 h-4" /> },
      { to: '/industry/collaborations', label: 'Collaborations', icon: <Handshake className="w-4 h-4" /> },
      { to: '/industry/profile', label: 'Organization Profile', icon: <Building className="w-4 h-4" /> },
      { to: '/industry/notifications', label: 'Notifications', icon: <Bell className="w-4 h-4" /> },
    ],
  };

  const currentMenu = menuConfig[role] || menuConfig.citizen;

  return (
    <aside className="w-64 bg-[#FFFDF5] border-r border-[#D8D8C8] flex flex-col h-[calc(100vh-4rem)] sticky top-16 shadow-xs">
      {/* Role Header */}
      <div className="p-4 border-b border-[#D8D8C8] bg-[#F7F5E8]">
        <div className="text-[10px] font-bold text-[#66736F] uppercase tracking-wider mb-1">Active Portal</div>
        <div className="text-sm font-bold text-[#17332F] capitalize flex items-center justify-between">
          <span>{role} Portal</span>
          <span className="w-2 h-2 rounded-full bg-[#087F6B] animate-ping" />
        </div>
      </div>

      {/* Navigation List */}
      <nav className="flex-1 p-3 space-y-1 overflow-y-auto">
        {currentMenu.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            onClick={onCloseMobile}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-xs font-medium transition-all ${
                isActive
                  ? 'bg-[#034F46] text-white font-semibold shadow-md'
                  : 'text-[#66736F] hover:bg-[#E9DFFF]/60 hover:text-[#17332F]'
              }`
            }
          >
            {item.icon}
            <span>{item.label}</span>
          </NavLink>
        ))}
      </nav>

      {/* Sidebar Footer Banner */}
      <div className="p-4 border-t border-[#D8D8C8] bg-[#F7F5E8]">
        <div className="p-3 rounded-xl bg-[#E9DFFF]/70 border border-[#6A5ACD]/20 text-[11px] text-[#17332F]">
          <p className="font-bold text-[#034F46]">CivicFix Engine</p>
          <p className="text-[10px] text-[#66736F] mt-0.5">FastAPI :8000 • Gemma 3 4B</p>
        </div>
      </div>
    </aside>
  );
};

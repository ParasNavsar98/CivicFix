import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../services/auth';
import { UserRole } from '../../types';
import { INITIAL_NOTIFICATIONS } from '../../services/mockData';
import {
  Bell,
  Search,
  User as UserIcon,
  LogOut,
  ChevronDown,
  Sparkles,
  Shield,
  BookOpen,
  Briefcase,
  Menu,
} from 'lucide-react';

interface NavbarProps {
  onToggleSidebar?: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({ onToggleSidebar }) => {
  const { user, logout, login } = useAuth();
  const navigate = useNavigate();

  const [searchQuery, setSearchQuery] = useState('');
  const [showNotifs, setShowNotifs] = useState(false);
  const [showProfile, setShowProfile] = useState(false);
  const [notifications, setNotifications] = useState(INITIAL_NOTIFICATIONS);

  const unreadCount = notifications.filter((n) => !n.read).length;

  const roleConfig: Record<UserRole, { label: string; bg: string; text: string; icon: React.ReactNode }> = {
    citizen: {
      label: 'Citizen Portal',
      bg: 'bg-[#087F6B]/10 border-[#087F6B]/20',
      text: 'text-[#087F6B]',
      icon: <UserIcon className="w-3.5 h-3.5 mr-1" />,
    },
    government: {
      label: 'Government & Review',
      bg: 'bg-[#B7791F]/10 border-[#B7791F]/20',
      text: 'text-[#B7791F]',
      icon: <Shield className="w-3.5 h-3.5 mr-1" />,
    },
    university: {
      label: 'University & Research',
      bg: 'bg-[#E9DFFF] border-[#6A5ACD]/30',
      text: 'text-[#6A5ACD]',
      icon: <BookOpen className="w-3.5 h-3.5 mr-1" />,
    },
    industry: {
      label: 'Industry & CSR',
      bg: 'bg-[#0F766E]/10 border-[#0F766E]/20',
      text: 'text-[#0F766E]',
      icon: <Briefcase className="w-3.5 h-3.5 mr-1" />,
    },
  };

  const currentRoleConfig = user ? roleConfig[user.role] : roleConfig.citizen;

  const handleRoleSwitch = (newRole: UserRole) => {
    login(newRole);
    setShowProfile(false);
    navigate(`/${newRole}/dashboard`);
  };

  return (
    <header className="sticky top-0 z-40 bg-[#FFFDF5]/90 backdrop-blur-xl border-b border-[#D8D8C8] h-16 flex items-center justify-between px-4 sm:px-6 shadow-xs">
      {/* Left: Mobile Menu Toggle & Brand Logo */}
      <div className="flex items-center gap-3">
        {onToggleSidebar && (
          <button
            onClick={onToggleSidebar}
            className="md:hidden p-2 rounded-xl bg-[#F7F5E8] hover:bg-[#E9DFFF] text-[#17332F] transition"
          >
            <Menu className="w-5 h-5" />
          </button>
        )}

        <Link to="/" className="flex items-center gap-2.5 group">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-[#034F46] to-[#0F766E] flex items-center justify-center text-white shadow-md group-hover:scale-105 transition">
            <Sparkles className="w-5 h-5" />
          </div>
          <div>
            <span className="text-lg font-extrabold tracking-tight text-[#17332F] flex items-center">
              Civic<span className="text-transparent bg-clip-text bg-gradient-to-r from-[#034F46] to-[#6A5ACD]">Fix</span>
            </span>
          </div>
        </Link>
      </div>

      {/* Center: Search Bar */}
      <div className="hidden md:flex items-center flex-1 max-w-md mx-8">
        <div className="relative w-full">
          <Search className="w-4 h-4 text-[#66736F] absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search problems, domains, districts, solutions..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 rounded-full bg-[#F7F5E8] border border-[#D8D8C8] text-xs text-[#17332F] placeholder-[#66736F] focus:outline-none focus:border-[#0F766E] focus:bg-[#FFFDF5] transition"
          />
        </div>
      </div>

      {/* Right Controls: Role Badge, Notifications, Profile */}
      <div className="flex items-center gap-3">
        {/* Role Badge Indicator */}
        {user && (
          <div className={`hidden sm:inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold border ${currentRoleConfig.bg} ${currentRoleConfig.text}`}>
            {currentRoleConfig.icon}
            {currentRoleConfig.label}
          </div>
        )}

        {/* Notifications Dropdown */}
        <div className="relative">
          <button
            onClick={() => {
              setShowNotifs(!showNotifs);
              setShowProfile(false);
            }}
            className="relative p-2 rounded-xl bg-[#F7F5E8] hover:bg-[#E9DFFF] text-[#17332F] transition border border-[#D8D8C8]"
          >
            <Bell className="w-5 h-5" />
            {unreadCount > 0 && (
              <span className="absolute top-1 right-1 w-4 h-4 rounded-full bg-[#6A5ACD] text-white text-[10px] font-bold flex items-center justify-center">
                {unreadCount}
              </span>
            )}
          </button>

          {showNotifs && (
            <div className="absolute right-0 mt-3 w-80 sm:w-96 bg-[#FFFDF5] border border-[#D8D8C8] rounded-2xl p-4 shadow-xl z-50 animate-in fade-in zoom-in-95">
              <div className="flex items-center justify-between pb-3 border-b border-[#D8D8C8]">
                <h4 className="text-xs font-bold text-[#17332F] uppercase tracking-wider">Notifications</h4>
                <button
                  onClick={() => setNotifications(notifications.map((n) => ({ ...n, read: true })))}
                  className="text-[11px] text-[#6A5ACD] hover:underline font-semibold"
                >
                  Mark all as read
                </button>
              </div>

              <div className="mt-3 space-y-2 max-h-72 overflow-y-auto pr-1">
                {notifications.map((n) => (
                  <Link
                    key={n.id}
                    to={n.link || '#'}
                    onClick={() => setShowNotifs(false)}
                    className={`block p-3 rounded-xl border transition ${
                      n.read ? 'bg-[#F7F5E8]/60 border-[#D8D8C8]' : 'bg-[#E9DFFF]/40 border-[#6A5ACD]/30'
                    }`}
                  >
                    <div className="flex items-start justify-between">
                      <h5 className="text-xs font-semibold text-[#17332F]">{n.title}</h5>
                      <span className="text-[10px] text-[#66736F]">{n.timestamp}</span>
                    </div>
                    <p className="text-xs text-[#66736F] mt-1 line-clamp-2">{n.message}</p>
                  </Link>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* User Profile Dropdown */}
        {user ? (
          <div className="relative">
            <button
              onClick={() => {
                setShowProfile(!showProfile);
                setShowNotifs(false);
              }}
              className="flex items-center gap-2 p-1.5 pl-2 rounded-full bg-[#F7F5E8] hover:bg-[#E9DFFF] border border-[#D8D8C8] transition"
            >
              <img
                src={user.avatarUrl || 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=150&q=80'}
                alt={user.name}
                className="w-7 h-7 rounded-full object-cover border border-[#034F46]"
              />
              <span className="hidden md:inline text-xs font-semibold text-[#17332F] max-w-[100px] truncate">
                {user.name}
              </span>
              <ChevronDown className="w-3.5 h-3.5 text-[#66736F]" />
            </button>

            {showProfile && (
              <div className="absolute right-0 mt-3 w-72 bg-[#FFFDF5] border border-[#D8D8C8] rounded-2xl p-4 shadow-xl z-50 animate-in fade-in zoom-in-95">
                <div className="pb-3 border-b border-[#D8D8C8] flex items-center gap-3">
                  <img src={user.avatarUrl} alt={user.name} className="w-10 h-10 rounded-full object-cover border border-[#034F46]" />
                  <div>
                    <h5 className="text-sm font-bold text-[#17332F]">{user.name}</h5>
                    <p className="text-xs text-[#66736F] truncate">{user.email}</p>
                    <span className="text-[10px] text-[#034F46] font-semibold">{user.organization || user.role}</span>
                  </div>
                </div>

                {/* Quick Role Switcher */}
                <div className="py-3 border-b border-[#D8D8C8]">
                  <div className="text-[10px] font-bold text-[#66736F] uppercase tracking-wider mb-2">Switch Active Portal</div>
                  <div className="grid grid-cols-2 gap-1.5">
                    {(['citizen', 'government', 'university', 'industry'] as UserRole[]).map((r) => (
                      <button
                        key={r}
                        onClick={() => handleRoleSwitch(r)}
                        className={`text-xs p-2 rounded-xl text-left capitalize font-medium transition ${
                          user.role === r ? 'bg-[#034F46] text-white font-bold' : 'bg-[#F7F5E8] hover:bg-[#E9DFFF] text-[#17332F]'
                        }`}
                      >
                        {r}
                      </button>
                    ))}
                  </div>
                </div>

                <div className="pt-3 space-y-1">
                  <Link
                    to={`/${user.role}/profile`}
                    onClick={() => setShowProfile(false)}
                    className="block px-3 py-2 rounded-xl text-xs font-medium text-[#17332F] hover:bg-[#F7F5E8] transition"
                  >
                    Manage Profile & Settings
                  </Link>
                  <button
                    onClick={() => {
                      logout();
                      setShowProfile(false);
                      navigate('/login');
                    }}
                    className="w-full text-left px-3 py-2 rounded-xl text-xs font-semibold text-[#B83A3A] hover:bg-[#B83A3A]/10 transition flex items-center gap-2"
                  >
                    <LogOut className="w-4 h-4" /> Sign Out
                  </button>
                </div>
              </div>
            )}
          </div>
        ) : (
          <Link
            to="/login"
            className="px-4 py-2 rounded-full text-xs font-bold bg-[#034F46] text-white hover:bg-[#0F766E] transition shadow-md"
          >
            Sign In
          </Link>
        )}
      </div>
    </header>
  );
};

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { User, UserRole } from '../types';

interface AuthContextType {
  user: User | null;
  login: (role: UserRole, options?: { email?: string; name?: string; subRole?: string; organization?: string }) => void;
  logout: () => void;
  isAuthenticated: boolean;
  isDemoMode: boolean;
  setDemoMode: (val: boolean) => void;
}

const DEMO_USERS: Record<UserRole, User> = {
  citizen: {
    id: 'CIT-901',
    name: 'Ramesh Kumar',
    email: 'ramesh.kumar@gmail.com',
    role: 'citizen',
    organization: 'Namkum Citizen Committee',
    avatarUrl: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=150&q=80',
  },
  government: {
    id: 'GOV-OFF-402',
    name: 'Dr. Priya Verma',
    email: 'priya.verma@gov.in',
    role: 'government',
    subRole: 'Reviewer / Government Officer',
    department: 'Urban Development & Public Works',
    organization: 'Jharkhand State Urban Development Agency',
    avatarUrl: 'https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?auto=format&fit=crop&w=150&q=80',
  },
  university: {
    id: 'UNI-SPOC-101',
    name: 'Prof. Rajesh Sharma',
    email: 'r.sharma@bitmesra.ac.in',
    role: 'university',
    subRole: 'University SPOC & Research Director',
    organization: 'Birla Institute of Technology (BIT Mesra)',
    universityId: 'UNI-BIT-001',
    avatarUrl: 'https://images.unsplash.com/photo-1560250097-0b93528c311a?auto=format&fit=crop&w=150&q=80',
  },
  industry: {
    id: 'IND-EXEC-88',
    name: 'Vikram Mehta',
    email: 'vikram.mehta@cleantech.com',
    role: 'industry',
    subRole: 'CSR & Partnerships Lead',
    organization: 'CleanTech Innovations Pvt Ltd',
    avatarUrl: 'https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?auto=format&fit=crop&w=150&q=80',
  },
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(() => {
    const saved = localStorage.getItem('civicfix_user');
    return saved ? JSON.parse(saved) : DEMO_USERS.citizen; // Default demo user for instant explore
  });

  const [isDemoMode, setDemoMode] = useState<boolean>(true);

  useEffect(() => {
    if (user) {
      localStorage.setItem('civicfix_user', JSON.stringify(user));
    } else {
      localStorage.removeItem('civicfix_user');
    }
  }, [user]);

  const login = (role: UserRole, options?: { email?: string; name?: string; subRole?: string; organization?: string }) => {
    const baseUser = DEMO_USERS[role];
    const newUser: User = {
      ...baseUser,
      email: options?.email || baseUser.email,
      name: options?.name || (options?.email ? options.email.split('@')[0] : baseUser.name),
      subRole: options?.subRole || baseUser.subRole,
      organization: options?.organization || baseUser.organization,
    };
    setUser(newUser);
  };

  const logout = () => {
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        login,
        logout,
        isAuthenticated: !!user,
        isDemoMode,
        setDemoMode,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

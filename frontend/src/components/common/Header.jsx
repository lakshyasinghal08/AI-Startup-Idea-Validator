import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Rocket, Sparkles, BarChart3, FileText } from 'lucide-react';
import { APP_NAME } from '@/utils/constants';

export const Header = () => {
  const location = useLocation();

  const navLinks = [
    { to: '/', label: 'Home', icon: Rocket },
    { to: '/validator', label: 'Idea Validator', icon: Sparkles },
    { to: '/reports', label: 'Reports', icon: FileText },
  ];

  return (
    <header className="sticky top-0 z-50 bg-white/80 backdrop-blur-md border-b border-slate-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <Link to="/" className="flex items-center space-x-2 text-slate-900 hover:opacity-90 transition">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-emerald-600 to-green-500 flex items-center justify-center text-white shadow-md shadow-emerald-500/20">
            <Rocket className="w-5 h-5" />
          </div>
          <div>
            <span className="font-bold text-lg leading-tight tracking-tight block text-slate-900">{APP_NAME}</span>
            <span className="text-xs text-slate-500 block">Infosys Springboard 7.0</span>
          </div>
        </Link>

        <nav className="flex items-center space-x-1 sm:space-x-4">
          {navLinks.map((link) => {
            const Icon = link.icon;
            const isActive = location.pathname === link.to;
            return (
              <Link
                key={link.to}
                to={link.to}
                className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-sm font-medium transition ${
                  isActive
                    ? 'bg-emerald-50 text-emerald-700 font-semibold'
                    : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
                }`}
              >
                <Icon className="w-4 h-4" />
                <span>{link.label}</span>
              </Link>
            );
          })}
        </nav>
      </div>
    </header>
  );
};

export default Header;

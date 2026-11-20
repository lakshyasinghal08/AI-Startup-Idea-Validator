import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Menu, X, ExternalLink } from 'lucide-react';
import { APP_NAME } from '@/utils/constants';

export const Header = () => {
  const location = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const navLinks = [
    { to: '/', label: 'Home' },
    { to: '/validator', label: 'Validator' },
    { to: '/about', label: 'About' },
  ];

  const githubUrl = 'https://github.com/lakshyasinghal08/AI-Startup-Idea-Validator';

  return (
    <header className="sticky top-0 z-50 bg-white border-b border-slate-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand */}
        <Link to="/" className="flex items-center space-x-3 text-slate-900 hover:opacity-90">
          <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center text-white font-bold text-sm">
            AI
          </div>
          <div>
            <span className="font-semibold text-base text-slate-900 block leading-tight">
              {APP_NAME}
            </span>
            <span className="text-xs text-slate-500 block leading-none mt-0.5">
              Infosys Springboard 7.0
            </span>
          </div>
        </Link>

        {/* Desktop Navigation */}
        <nav className="hidden md:flex items-center space-x-1 sm:space-x-2">
          {navLinks.map((link) => {
            const isActive = location.pathname === link.to;
            return (
              <Link
                key={link.to}
                to={link.to}
                className={`px-3 py-2 rounded-md text-sm font-medium transition ${
                  isActive
                    ? 'text-blue-600 bg-blue-50 font-semibold'
                    : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
                }`}
              >
                {link.label}
              </Link>
            );
          })}

          <a
            href={githubUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center space-x-1 px-3 py-2 rounded-md text-sm font-medium text-slate-600 hover:text-slate-900 hover:bg-slate-50 transition"
          >
            <span>GitHub</span>
            <ExternalLink className="w-3.5 h-3.5" />
          </a>
        </nav>

        {/* Mobile menu button */}
        <div className="md:hidden">
          <button
            type="button"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="p-2 rounded-md text-slate-600 hover:text-slate-900 hover:bg-slate-100"
            aria-label="Toggle navigation menu"
          >
            {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>
      </div>

      {/* Mobile Menu Dropdown */}
      {mobileMenuOpen && (
        <div className="md:hidden border-t border-slate-200 bg-white px-4 pt-2 pb-4 space-y-1">
          {navLinks.map((link) => {
            const isActive = location.pathname === link.to;
            return (
              <Link
                key={link.to}
                to={link.to}
                onClick={() => setMobileMenuOpen(false)}
                className={`block px-3 py-2 rounded-md text-base font-medium ${
                  isActive
                    ? 'text-blue-600 bg-blue-50 font-semibold'
                    : 'text-slate-700 hover:bg-slate-50'
                }`}
              >
                {link.label}
              </Link>
            );
          })}
          <a
            href={githubUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center justify-between px-3 py-2 rounded-md text-base font-medium text-slate-700 hover:bg-slate-50"
          >
            <span>GitHub</span>
            <ExternalLink className="w-4 h-4" />
          </a>
        </div>
      )}
    </header>
  );
};

export default Header;

import React from 'react';

export const Footer = () => {
  return (
    <footer className="mt-auto border-t border-slate-200 bg-white py-6">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center text-sm text-slate-500">
        <p>
          AI-Based Startup Idea Validator with Market Analysis Assistance &bull; Infosys Springboard Virtual Internship 7.0
        </p>
        <p className="mt-1 text-xs text-slate-400">
          Powered by React 19, FastAPI, Tailwind CSS & Multi-Agent Architecture
        </p>
      </div>
    </footer>
  );
};

export default Footer;

import React from 'react';

export const Footer = () => {
  return (
    <footer className="mt-auto border-t border-slate-200 bg-white py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center text-sm text-slate-500 space-y-2">
        <p className="font-medium text-slate-700">
          AI-Based Startup Idea Validator with Market Analysis Assistance
        </p>
        <p className="text-xs text-slate-500">
          Infosys Springboard Virtual Internship 7.0 &bull; Built with React 19 & FastAPI
        </p>
        <p className="text-xs">
          <a
            href="https://github.com/lakshyasinghal08/AI-Startup-Idea-Validator"
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-600 hover:underline"
          >
            GitHub Repository
          </a>
        </p>
      </div>
    </footer>
  );
};

export default Footer;

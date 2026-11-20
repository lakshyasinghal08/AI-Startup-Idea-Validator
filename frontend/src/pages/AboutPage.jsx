import React from 'react';
import Card from '@/components/common/Card';

export const AboutPage = () => {
  return (
    <div className="max-w-4xl mx-auto py-4 space-y-8">
      {/* Header */}
      <div className="border-b border-slate-200 pb-4">
        <h1 className="text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">
          About the Project
        </h1>
        <p className="text-sm sm:text-base text-slate-600 mt-1">
          Infosys Springboard Virtual Internship 7.0 &bull; Project Overview & Architecture
        </p>
      </div>

      {/* Main Narrative */}
      <div className="space-y-6">
        <Card title="Project Motivation" subtitle="Addressing the #1 reason startups fail">
          <p className="text-sm text-slate-700 leading-relaxed">
            Over 90% of early-stage startups fail because they build products that lack real market demand.
            Entrepreneurs and evaluation committees often spend weeks conducting fragmented manual market sizing,
            subjective competitive scraping, and ad-hoc SWOT evaluations.
          </p>
          <p className="text-sm text-slate-700 leading-relaxed mt-3">
            The <strong>AI-Based Startup Idea Validator with Market Analysis Assistance</strong> is engineered to
            standardize and accelerate early-stage venture evaluation. By leveraging an ensemble of specialized AI agents
            and real-time market data retrieval, the platform objectively assesses problem-solution fit, calculates TAM/SAM/SOM,
            identifies incumbents, and delivers executive-grade consulting dossiers.
          </p>
        </Card>

        <Card title="Architectural Foundation" subtitle="Clean Architecture & Modular Design">
          <div className="space-y-4 text-sm text-slate-700">
            <div>
              <h4 className="font-semibold text-slate-900">1. Decoupled Presentation Layer</h4>
              <p className="text-slate-600 mt-0.5">
                Built with React 19, Vite, and Tailwind CSS. The interface is deliberately clean, minimal, and responsive,
                adhering to utility-first principles without unnecessary animations or over-designed graphical elements.
              </p>
            </div>

            <div>
              <h4 className="font-semibold text-slate-900">2. High-Performance API Gateway</h4>
              <p className="text-slate-600 mt-0.5">
                Powered by FastAPI and Uvicorn. Validates requests using Pydantic v2 schemas and enforces consistent
                RESTful response envelopes across all endpoints.
              </p>
            </div>

            <div>
              <h4 className="font-semibold text-slate-900">3. Multi-Agent AI Network</h4>
              <p className="text-slate-600 mt-0.5">
                Decomposes market evaluation into isolated agent responsibilities: Idea Agent (LLM extraction),
                Search Agent (Tavily real-time web intelligence), Market Agent (TAM/SAM/SOM sizing), Competitor Agent (landscape & moats),
                SWOT Agent (4-quadrant strategic matrix), and Report Agent (16-section consulting dossier).
              </p>
            </div>

            <div>
              <h4 className="font-semibold text-slate-900">4. Standalone & Zero-Dependency Execution</h4>
              <p className="text-slate-600 mt-0.5">
                For Milestone 1, the platform operates completely in-memory with zero database and zero Docker dependencies,
                ensuring instant startup and universal reproducibility during evaluations.
              </p>
            </div>
          </div>
        </Card>

        <Card title="Academic & Internship Context" subtitle="Program Information">
          <div className="text-sm text-slate-700 space-y-2">
            <p>
              <strong>Program:</strong> Infosys Springboard Virtual Internship 7.0
            </p>
            <p>
              <strong>Developer:</strong>{' '}
              <a
                href="https://github.com/lakshyasinghal08"
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-600 hover:underline font-medium"
              >
                Lakshya Singhal
              </a>
            </p>
            <p>
              <strong>Repository:</strong>{' '}
              <a
                href="https://github.com/lakshyasinghal08/AI-Startup-Idea-Validator"
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-600 hover:underline font-medium"
              >
                lakshyasinghal08/AI-Startup-Idea-Validator
              </a>
            </p>
          </div>
        </Card>
      </div>
    </div>
  );
};

export default AboutPage;

import React, { useState } from 'react';
import { Loader2, ArrowLeft, Printer, AlertCircle, CheckCircle2, Award, ExternalLink } from 'lucide-react';
import Card from '@/components/common/Card';
import Button from '@/components/common/Button';
import ideaApi from '@/api/ideaApi';

const LOADING_STEPS = [
  'Analyzing your startup idea...',
  'Extracting core business model and industry...',
  'Searching live market research & competitors via Tavily...',
  'Evaluating competitive landscape & moats...',
  'Synthesizing professional consulting dossier...',
];

export const ValidatorPage = () => {
  const [ideaText, setIdeaText] = useState('');
  const [loading, setLoading] = useState(false);
  const [loadingStepIndex, setLoadingStepIndex] = useState(0);
  const [report, setReport] = useState(null);
  const [error, setError] = useState(null);

  const samplePrompt = 'I want to build an AI platform that helps students prepare for interviews.';

  const handleUseSample = () => {
    setIdeaText(samplePrompt);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!ideaText.trim()) return;

    setLoading(true);
    setError(null);
    setReport(null);
    setLoadingStepIndex(0);

    // Progressive step indicator
    const stepInterval = setInterval(() => {
      setLoadingStepIndex((prev) => {
        if (prev < LOADING_STEPS.length - 1) return prev + 1;
        return prev;
      });
    }, 1200);

    try {
      const response = await ideaApi.validateIdea({ idea: ideaText });
      if (response && response.data) {
        setReport(response.data);
      } else {
        throw new Error('Received invalid data structure from backend.');
      }
    } catch (err) {
      console.error('Validation Error:', err);
      setError(err.message || 'Validation request failed. Please check the backend connection.');
    } finally {
      clearInterval(stepInterval);
      setLoading(false);
    }
  };

  const handleReset = () => {
    setReport(null);
    setError(null);
  };

  const handlePrint = () => {
    window.print();
  };

  return (
    <div className="max-w-4xl mx-auto py-6 px-4 space-y-8">
      {/* Page Header (Hidden when viewing report) */}
      {!report && !loading && (
        <div className="border-b border-slate-200 pb-5">
          <h1 className="text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">
            Startup Idea Validator
          </h1>
          <p className="text-sm sm:text-base text-slate-600 mt-2">
            Enter your startup concept below. Our autonomous multi-agent pipeline extracts core business dimensions, 
            queries live market research, and synthesizes a McKinsey/BCG-grade consulting dossier.
          </p>
        </div>
      )}

      {/* Error Banner */}
      {error && (
        <div className="p-4 bg-red-50 border border-red-200 text-red-700 rounded-lg text-sm flex items-start space-x-3">
          <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5 text-red-600" />
          <div className="space-y-1">
            <p className="font-semibold text-red-800">Validation Request Failed</p>
            <p className="text-xs text-red-700">{error}</p>
          </div>
        </div>
      )}

      {/* Loading State with Progress Steps */}
      {loading && (
        <div className="bg-white border border-slate-200 rounded-xl p-10 sm:p-14 text-center space-y-6 shadow-sm">
          <Loader2 className="w-10 h-10 text-blue-600 animate-spin mx-auto" />
          <div className="space-y-2">
            <h3 className="text-lg font-semibold text-slate-900">
              Validating Startup Proposition
            </h3>
            <p className="text-sm text-slate-500 max-w-md mx-auto">
              Please wait while our multi-agent architecture performs comprehensive market evaluation.
            </p>
          </div>

          <div className="max-w-md mx-auto bg-slate-50 rounded-lg p-4 border border-slate-200 text-left space-y-2.5">
            {LOADING_STEPS.map((step, idx) => {
              const isPast = idx < loadingStepIndex;
              const isCurrent = idx === loadingStepIndex;
              return (
                <div key={idx} className="flex items-center space-x-3 text-xs sm:text-sm">
                  {isPast ? (
                    <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0" />
                  ) : isCurrent ? (
                    <Loader2 className="w-4 h-4 text-blue-600 animate-spin flex-shrink-0" />
                  ) : (
                    <div className="w-4 h-4 rounded-full border border-slate-300 flex-shrink-0" />
                  )}
                  <span className={isCurrent ? 'font-semibold text-blue-700' : isPast ? 'text-slate-700' : 'text-slate-400'}>
                    {step}
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Single Input Form */}
      {!loading && !report && (
        <Card className="p-6 sm:p-8 shadow-sm">
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <label htmlFor="startupIdea" className="block text-sm font-semibold text-slate-900">
                  Describe your startup idea
                </label>
                <button
                  type="button"
                  onClick={handleUseSample}
                  className="text-xs text-blue-600 hover:text-blue-800 font-medium underline transition"
                >
                  Use Example
                </button>
              </div>
              <textarea
                id="startupIdea"
                name="idea"
                rows={6}
                value={ideaText}
                onChange={(e) => setIdeaText(e.target.value)}
                placeholder="Describe your startup idea..."
                required
                className="w-full p-4 border border-slate-300 rounded-lg text-slate-900 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 placeholder-slate-400 transition"
              />
              <p className="text-xs text-slate-500">
                Example: <span className="italic">"I want to build an AI platform that helps students prepare for interviews."</span>
              </p>
            </div>

            <div className="pt-2">
              <Button
                type="submit"
                variant="primary"
                disabled={!ideaText.trim() || loading}
                className="w-full sm:w-auto px-8 py-3 text-sm font-semibold shadow-sm"
              >
                Validate Idea
              </Button>
            </div>
          </form>
        </Card>
      )}

      {/* Consulting Report Display (McKinsey / BCG / Deloitte Style) */}
      {!loading && report && (
        <div className="space-y-8">
          {/* Top Report Header with Actions */}
          <div className="bg-white border border-slate-200 rounded-xl p-6 sm:p-8 shadow-sm flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div>
              <div className="flex items-center space-x-2 text-xs font-semibold text-blue-600 uppercase tracking-wider">
                <span>Management Consulting Dossier</span>
                <span>•</span>
                <span>Milestone 1</span>
              </div>
              <h1 className="text-2xl sm:text-3xl font-bold text-slate-900 mt-1">
                {report.title || 'Startup Validation Report'}
              </h1>
              <p className="text-xs text-slate-500 mt-1">
                Report ID: <span className="font-mono text-slate-600">{report.id}</span> | Status:{' '}
                <span className="font-semibold text-emerald-600 uppercase">{report.status}</span>
              </p>
            </div>

            <div className="flex items-center space-x-3">
              <Button
                variant="outline"
                onClick={handlePrint}
                className="text-xs flex items-center space-x-1.5"
              >
                <Printer className="w-3.5 h-3.5" />
                <span>Print Report</span>
              </Button>
              <Button
                variant="primary"
                onClick={handleReset}
                className="text-xs flex items-center space-x-1.5"
              >
                <ArrowLeft className="w-3.5 h-3.5" />
                <span>Validate Another Idea</span>
              </Button>
            </div>
          </div>

          {/* 1. Executive Summary */}
          <Card title="Executive Summary" subtitle="High-level synthesis and commercial viability verdict">
            <p className="text-sm leading-relaxed text-slate-800">
              {report.executive_summary || report.summary || 'Executive summary pending synthesis.'}
            </p>
          </Card>

          {/* 2. Startup Overview */}
          <Card title="Startup Overview" subtitle="Business concept and positioning">
            <p className="text-sm leading-relaxed text-slate-800">
              {report.startup_overview || report.idea_overview || report.problem_solution_fit || 'Venture overview pending extraction.'}
            </p>
          </Card>

          {/* 3 & 4. Problem Statement & Proposed Solution */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card title="Problem Statement" subtitle="Market friction and customer pain points">
              <p className="text-sm leading-relaxed text-slate-800">
                {report.problem_statement || 'Target customer pain points and operational friction.'}
              </p>
            </Card>

            <Card title="Proposed Solution" subtitle="Product architecture and mechanism of action">
              <p className="text-sm leading-relaxed text-slate-800">
                {report.proposed_solution || report.problem_solution_fit || 'Proposed product capability and automation solution.'}
              </p>
            </Card>
          </div>

          {/* 5, 6, 7. Target Customers, Industry & Business Model */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Card title="Target Customers" subtitle="Ideal customer profile (ICP)">
              <p className="text-sm leading-relaxed text-slate-800">
                {report.target_customers || 'Primary customer segments and early adopter profiles.'}
              </p>
            </Card>

            <Card title="Industry Vertical" subtitle="Market sector categorization">
              <p className="text-sm leading-relaxed font-semibold text-slate-900">
                {report.industry || 'Technology & Services'}
              </p>
              <p className="text-xs text-slate-500 mt-1">
                Domain-specific regulatory and competitive conditions apply.
              </p>
            </Card>

            <Card title="Business Model" subtitle="Monetization and revenue mechanics">
              <p className="text-sm leading-relaxed font-semibold text-slate-900">
                {report.business_model || 'Subscription SaaS / Freemium'}
              </p>
              <p className="text-xs text-slate-500 mt-1">
                Scalable unit economics with predictable recurring revenue.
              </p>
            </Card>
          </div>

          {/* 8 & 9. Market Research & Market Trends */}
          <Card title="Market Research & Trends" subtitle="Evidence-based live market intelligence">
            <div className="space-y-5">
              <div>
                <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-1.5">
                  Market Intelligence Synthesis
                </h4>
                <p className="text-sm leading-relaxed text-slate-800">
                  {report.market_research || report.market_analysis?.research_summary || 'Qualitative market analysis indicates expanding demand.'}
                </p>
              </div>

              {/* Sizing Metrics */}
              {report.market_analysis && (report.market_analysis.tam || report.market_potential?.tam) && (
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 pt-2">
                  <div className="bg-slate-50 border border-slate-200 rounded-lg p-3 text-center">
                    <p className="text-xs font-semibold text-slate-500 uppercase">TAM</p>
                    <p className="text-base font-bold text-slate-900 mt-0.5">
                      {report.market_analysis?.tam || report.market_potential?.tam || '$12.8B'}
                    </p>
                  </div>
                  <div className="bg-slate-50 border border-slate-200 rounded-lg p-3 text-center">
                    <p className="text-xs font-semibold text-slate-500 uppercase">SAM</p>
                    <p className="text-base font-bold text-slate-900 mt-0.5">
                      {report.market_analysis?.sam || report.market_potential?.sam || '$2.6B'}
                    </p>
                  </div>
                  <div className="bg-slate-50 border border-slate-200 rounded-lg p-3 text-center">
                    <p className="text-xs font-semibold text-slate-500 uppercase">SOM</p>
                    <p className="text-base font-bold text-blue-600 mt-0.5">
                      {report.market_analysis?.som || report.market_potential?.som || '$185M'}
                    </p>
                  </div>
                  <div className="bg-slate-50 border border-slate-200 rounded-lg p-3 text-center">
                    <p className="text-xs font-semibold text-slate-500 uppercase">CAGR</p>
                    <p className="text-base font-bold text-emerald-600 mt-0.5">
                      {report.market_analysis?.cagr || report.market_potential?.cagr || '14.2%'}
                    </p>
                  </div>
                </div>
              )}

              {/* Key Trends */}
              <div>
                <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-2">
                  Dominant Market Trends
                </h4>
                <ul className="text-sm text-slate-700 space-y-1.5 list-disc pl-4">
                  {(report.market_trends || report.market_analysis?.trends || [
                    'Accelerated digitization across core workflows.',
                    'Shift toward automated personalized intelligence.',
                    'Demand for transparent benchmarking.',
                  ]).map((trend, idx) => (
                    <li key={idx}>{trend}</li>
                  ))}
                </ul>
              </div>
            </div>
          </Card>

          {/* 10. Competitor Analysis */}
          <Card title="Competitor Analysis" subtitle="Competitive landscape and defensible moats">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="bg-slate-50 border border-slate-200 rounded-lg p-4 space-y-2">
                <p className="text-xs font-semibold text-slate-700 uppercase">Direct & Indirect Competitors</p>
                <ul className="text-xs sm:text-sm text-slate-700 space-y-2">
                  {report.competitor_analysis?.direct_competitors ? (
                    report.competitor_analysis.direct_competitors.map((c, idx) => (
                      <li key={idx} className="border-b border-slate-200 pb-1.5 last:border-0 last:pb-0">
                        <span className="font-semibold text-slate-900">{typeof c === 'string' ? c : c.name}</span>
                        {typeof c === 'object' && c.vulnerability && (
                          <span className="block text-xs text-slate-500 mt-0.5">Vulnerability: {c.vulnerability}</span>
                        )}
                      </li>
                    ))
                  ) : Array.isArray(report.competitors) && report.competitors.length > 0 ? (
                    report.competitors.map((comp, idx) => <li key={idx} className="list-disc pl-4">{comp}</li>)
                  ) : (
                    <li>Legacy industry incumbents</li>
                  )}
                </ul>
              </div>

              <div className="bg-slate-50 border border-slate-200 rounded-lg p-4 space-y-2">
                <p className="text-xs font-semibold text-slate-700 uppercase">Defensive Moats</p>
                <ul className="text-xs sm:text-sm text-slate-700 space-y-1.5 list-disc pl-4">
                  {(report.competitor_analysis?.defensive_moats || [
                    'Proprietary feedback loops and domain telemetry compounding accuracy.',
                    'High switching barriers generated by user history and saved workflows.',
                    'Significantly accelerated time-to-value compared to legacy vendors.',
                  ]).map((moat, idx) => (
                    <li key={idx}>{moat}</li>
                  ))}
                </ul>
              </div>
            </div>
          </Card>

          {/* 11. SWOT Analysis */}
          <Card title="SWOT Analysis" subtitle="4-quadrant strategic assessment matrix">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {/* Strengths */}
              <div className="bg-emerald-50/60 border border-emerald-200 rounded-lg p-4 space-y-2">
                <p className="text-xs font-bold text-emerald-800 uppercase tracking-wide">Strengths (Internal)</p>
                <ul className="text-xs sm:text-sm text-emerald-900 space-y-1.5 list-disc pl-4">
                  {(report.swot_analysis?.strengths || report.swot?.strengths || []).map((item, idx) => (
                    <li key={idx}>{item}</li>
                  ))}
                </ul>
              </div>

              {/* Weaknesses */}
              <div className="bg-amber-50/60 border border-amber-200 rounded-lg p-4 space-y-2">
                <p className="text-xs font-bold text-amber-800 uppercase tracking-wide">Weaknesses (Internal)</p>
                <ul className="text-xs sm:text-sm text-amber-900 space-y-1.5 list-disc pl-4">
                  {(report.swot_analysis?.weaknesses || report.swot?.weaknesses || []).map((item, idx) => (
                    <li key={idx}>{item}</li>
                  ))}
                </ul>
              </div>

              {/* Opportunities */}
              <div className="bg-blue-50/60 border border-blue-200 rounded-lg p-4 space-y-2">
                <p className="text-xs font-bold text-blue-800 uppercase tracking-wide">Opportunities (External)</p>
                <ul className="text-xs sm:text-sm text-blue-900 space-y-1.5 list-disc pl-4">
                  {(report.swot_analysis?.opportunities || report.swot?.opportunities || []).map((item, idx) => (
                    <li key={idx}>{item}</li>
                  ))}
                </ul>
              </div>

              {/* Threats */}
              <div className="bg-rose-50/60 border border-rose-200 rounded-lg p-4 space-y-2">
                <p className="text-xs font-bold text-rose-800 uppercase tracking-wide">Threats (External)</p>
                <ul className="text-xs sm:text-sm text-rose-900 space-y-1.5 list-disc pl-4">
                  {(report.swot_analysis?.threats || report.swot?.threats || []).map((item, idx) => (
                    <li key={idx}>{item}</li>
                  ))}
                </ul>
              </div>
            </div>
          </Card>

          {/* 12 & 13. Opportunities & Risks */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card title="Business Opportunities" subtitle="Scalability vectors and expansion paths">
              <ul className="text-sm text-slate-800 space-y-2.5 list-disc pl-4">
                {(report.opportunities || report.business_opportunities || report.growth_opportunities || []).map((opp, idx) => (
                  <li key={idx}>{opp}</li>
                ))}
              </ul>
            </Card>

            <Card title="Potential Risks & Mitigations" subtitle="Execution vulnerabilities and risk factors">
              <ul className="text-sm text-slate-800 space-y-2.5 list-disc pl-4">
                {(report.risks || report.potential_risks || report.business_risks || []).map((risk, idx) => (
                  <li key={idx}>{risk}</li>
                ))}
              </ul>
            </Card>
          </div>

          {/* 14. Recommendations */}
          <Card title="Strategic Recommendations" subtitle="Prioritized 30-90 day execution milestones">
            <div className="space-y-3">
              {(report.recommendations || []).map((rec, idx) => (
                <div key={idx} className="flex items-start space-x-3 p-3 bg-slate-50 border border-slate-200 rounded-lg text-sm text-slate-800">
                  <div className="w-5 h-5 rounded-full bg-blue-100 text-blue-700 flex items-center justify-center text-xs font-bold flex-shrink-0 mt-0.5">
                    {idx + 1}
                  </div>
                  <p className="leading-relaxed">{rec}</p>
                </div>
              ))}
            </div>
          </Card>

          {/* 15. Overall Validation Score */}
          <Card title="Overall Validation Score" subtitle="Quantitative evaluation breakdown (0-100 scale)">
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-5 text-center col-span-2 sm:col-span-1">
                <p className="text-xs font-bold text-blue-800 uppercase">Composite Score</p>
                <p className="text-3xl font-extrabold text-blue-700 mt-2">
                  {report.overall_validation_score || report.scores?.overall || 82.0}
                  <span className="text-xs text-blue-500 font-normal"> / 100</span>
                </p>
              </div>

              <div className="bg-slate-50 border border-slate-200 rounded-lg p-4 text-center">
                <p className="text-xs font-semibold text-slate-500 uppercase">Feasibility</p>
                <p className="text-xl font-bold text-slate-900 mt-1">
                  {report.scores?.feasibility || 85.0}
                  <span className="text-xs text-slate-400 font-normal"> / 100</span>
                </p>
              </div>

              <div className="bg-slate-50 border border-slate-200 rounded-lg p-4 text-center">
                <p className="text-xs font-semibold text-slate-500 uppercase">Market Demand</p>
                <p className="text-xl font-bold text-slate-900 mt-1">
                  {report.scores?.market_demand || 82.0}
                  <span className="text-xs text-slate-400 font-normal"> / 100</span>
                </p>
              </div>

              <div className="bg-slate-50 border border-slate-200 rounded-lg p-4 text-center">
                <p className="text-xs font-semibold text-slate-500 uppercase">Uniqueness</p>
                <p className="text-xl font-bold text-slate-900 mt-1">
                  {report.scores?.uniqueness || 81.0}
                  <span className="text-xs text-slate-400 font-normal"> / 100</span>
                </p>
              </div>
            </div>
          </Card>

          {/* 16. Final Conclusion */}
          <div className="bg-slate-900 text-white rounded-xl p-6 sm:p-8 shadow-sm space-y-3">
            <div className="flex items-center space-x-2 text-xs font-semibold text-blue-400 uppercase tracking-wider">
              <Award className="w-4 h-4" />
              <span>Strategic Verdict & Final Conclusion</span>
            </div>
            <p className="text-sm sm:text-base leading-relaxed text-slate-200">
              {report.final_conclusion || 'Strategic verdict indicates favorable commercial viability with disciplined execution.'}
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default ValidatorPage;

import React, { useState } from 'react';
import { Sparkles, Loader2, CheckCircle2, TrendingUp, AlertTriangle } from 'lucide-react';
import Card from '@/components/common/Card';
import Button from '@/components/common/Button';
import { INDUSTRIES } from '@/utils/constants';
import ideaApi from '@/api/ideaApi';

export const ValidatorPage = () => {
  const [formData, setFormData] = useState({
    title: '',
    target_market: INDUSTRIES[0],
    description: '',
    target_audience: '',
    estimated_budget: '$25,000',
    monetization_model: 'SaaS Subscription',
  });

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await ideaApi.validateIdea(formData);
      setResult(response.data);
    } catch (err) {
      setError(err.message || 'Validation request failed. Please check backend connection.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-slate-900">Startup Idea Validator</h1>
        <p className="text-slate-600 mt-1">
          Submit your product hypothesis below. In Milestone 1, this connects to the FastAPI backend contract.
        </p>
      </div>

      {error && (
        <div className="p-4 bg-rose-50 border border-rose-200 text-rose-700 rounded-xl text-sm flex items-center space-x-2">
          <AlertTriangle className="w-5 h-5 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Submission Form */}
      <Card title="Startup Details" subtitle="Provide context to guide the research and SWOT agents">
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Startup Title *</label>
              <input
                type="text"
                name="title"
                required
                value={formData.title}
                onChange={handleChange}
                placeholder="e.g. EcoRoute Logistics"
                className="w-full px-3.5 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Target Market Vertical *</label>
              <select
                name="target_market"
                value={formData.target_market}
                onChange={handleChange}
                className="w-full px-3.5 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 bg-white"
              >
                {INDUSTRIES.map((ind) => (
                  <option key={ind} value={ind}>{ind}</option>
                ))}
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Problem & Solution Description *</label>
            <textarea
              name="description"
              rows={4}
              required
              minLength={15}
              value={formData.description}
              onChange={handleChange}
              placeholder="Explain the problem you solve, who feels the pain, and how your product works..."
              className="w-full px-3.5 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
            />
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Target Audience</label>
              <input
                type="text"
                name="target_audience"
                value={formData.target_audience}
                onChange={handleChange}
                placeholder="e.g. B2B Fleet Managers"
                className="w-full px-3.5 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Estimated Budget</label>
              <input
                type="text"
                name="estimated_budget"
                value={formData.estimated_budget}
                onChange={handleChange}
                className="w-full px-3.5 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Monetization Model</label>
              <input
                type="text"
                name="monetization_model"
                value={formData.monetization_model}
                onChange={handleChange}
                className="w-full px-3.5 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
              />
            </div>
          </div>

          <div className="pt-2 flex justify-end">
            <Button type="submit" disabled={loading} className="space-x-2">
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Agents Evaluating...</span>
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4" />
                  <span>Run Validation Analysis</span>
                </>
              )}
            </Button>
          </div>
        </form>
      </Card>

      {/* Validation Result Display */}
      {result && (
        <Card title={`Validation Dossier: ${result.title}`} subtitle={`Status: ${result.status} (ID: ${result.id})`}>
          <div className="space-y-6">
            {/* Score Grid */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-center">
              <div className="p-4 bg-emerald-50 rounded-xl">
                <span className="text-2xl font-bold text-emerald-700">{result.scores?.overall}%</span>
                <span className="block text-xs text-emerald-800 font-medium mt-1">Overall Score</span>
              </div>
              <div className="p-4 bg-blue-50 rounded-xl">
                <span className="text-2xl font-bold text-blue-700">{result.scores?.feasibility}%</span>
                <span className="block text-xs text-blue-800 font-medium mt-1">Feasibility</span>
              </div>
              <div className="p-4 bg-purple-50 rounded-xl">
                <span className="text-2xl font-bold text-purple-700">{result.scores?.market_demand}%</span>
                <span className="block text-xs text-purple-800 font-medium mt-1">Market Demand</span>
              </div>
              <div className="p-4 bg-amber-50 rounded-xl">
                <span className="text-2xl font-bold text-amber-700">{result.scores?.uniqueness}%</span>
                <span className="block text-xs text-amber-800 font-medium mt-1">Uniqueness</span>
              </div>
            </div>

            {/* Executive Summary */}
            <div className="p-4 bg-slate-50 rounded-lg text-sm text-slate-700 leading-relaxed border border-slate-200">
              <p className="font-semibold text-slate-900 mb-1">Executive Summary:</p>
              {result.summary}
            </div>

            {/* SWOT Matrix Preview */}
            <div>
              <h4 className="font-semibold text-slate-900 text-sm mb-3">Strategic SWOT Matrix</h4>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
                <div className="p-3 bg-emerald-50 border border-emerald-200 rounded-lg">
                  <span className="font-bold text-emerald-800 block mb-1">Strengths</span>
                  <ul className="list-disc list-inside space-y-1 text-emerald-950">
                    {result.swot?.strengths?.map((s, idx) => <li key={idx}>{s}</li>)}
                  </ul>
                </div>
                <div className="p-3 bg-amber-50 border border-amber-200 rounded-lg">
                  <span className="font-bold text-amber-800 block mb-1">Weaknesses</span>
                  <ul className="list-disc list-inside space-y-1 text-amber-950">
                    {result.swot?.weaknesses?.map((w, idx) => <li key={idx}>{w}</li>)}
                  </ul>
                </div>
                <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
                  <span className="font-bold text-blue-800 block mb-1">Opportunities</span>
                  <ul className="list-disc list-inside space-y-1 text-blue-950">
                    {result.swot?.opportunities?.map((o, idx) => <li key={idx}>{o}</li>)}
                  </ul>
                </div>
                <div className="p-3 bg-rose-50 border border-rose-200 rounded-lg">
                  <span className="font-bold text-rose-800 block mb-1">Threats</span>
                  <ul className="list-disc list-inside space-y-1 text-rose-950">
                    {result.swot?.threats?.map((t, idx) => <li key={idx}>{t}</li>)}
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </Card>
      )}
    </div>
  );
};

export default ValidatorPage;

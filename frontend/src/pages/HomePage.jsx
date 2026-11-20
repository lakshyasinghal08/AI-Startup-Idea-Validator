import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, CheckCircle2 } from 'lucide-react';
import Button from '@/components/common/Button';
import Card from '@/components/common/Card';

export const HomePage = () => {
  const features = [
    {
      title: 'Problem-Solution Fit',
      description:
        'Analyzes the clarity of your core problem statement and checks if your proposed solution directly addresses verifiable customer friction.',
    },
    {
      title: 'Market Sizing & Demand',
      description:
        'Calculates Total Addressable Market (TAM), Serviceable Available Market (SAM), and Serviceable Obtainable Market (SOM) estimates.',
    },
    {
      title: 'Competitor Intelligence',
      description:
        'Identifies direct incumbents, indirect substitutes, and evaluates your product’s defensive moats and pricing defensibility.',
    },
    {
      title: 'Strategic SWOT Analysis',
      description:
        'Compiles an objective, four-quadrant strategic matrix highlighting internal advantages, critical vulnerabilities, and macro threats.',
    },
  ];

  const steps = [
    {
      step: '01',
      title: 'Enter Startup Details',
      description:
        'Provide your startup name, core problem, proposed solution, target audience, industry, and business model.',
    },
    {
      step: '02',
      title: 'Multi-Agent Evaluation',
      description:
        'The validation engine structures the hypothesis and evaluates market viability, demand signals, and feasibility indices.',
    },
    {
      step: '03',
      title: 'Review Consulting Report',
      description:
        'Receive an executive-grade strategic brief formatted with quantitative scores, SWOT analysis, and prioritized recommendations.',
    },
  ];

  return (
    <div className="space-y-16 py-4">
      {/* Hero Section */}
      <section className="text-center max-w-3xl mx-auto space-y-6 pt-6 sm:pt-10">
        <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-slate-100 text-slate-700 text-xs font-medium">
          <span>Infosys Springboard Virtual Internship 7.0</span>
        </div>

        <h1 className="text-3xl sm:text-5xl font-bold tracking-tight text-slate-900 leading-tight">
          AI-Based Startup Idea Validator with Market Analysis Assistance
        </h1>

        <p className="text-base sm:text-lg text-slate-600 leading-relaxed max-w-2xl mx-auto">
          An enterprise-grade evaluation platform designed to help founders, evaluators, and accelerators
          stress-test startup ideas, assess market sizing, analyze competitors, and generate strategic consulting reports.
        </p>

        <div className="pt-2">
          <Link to="/validator">
            <Button variant="primary" className="text-base px-6 py-3 space-x-2">
              <span>Start Validation</span>
              <ArrowRight className="w-4 h-4" />
            </Button>
          </Link>
        </div>
      </section>

      {/* Features Section */}
      <section className="space-y-6">
        <div className="text-center max-w-2xl mx-auto">
          <h2 className="text-2xl font-bold text-slate-900">Key Capabilities</h2>
          <p className="text-sm text-slate-500 mt-1">
            Engineered to replace fragmented manual research with structured analysis.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-5xl mx-auto">
          {features.map((feature, idx) => (
            <Card key={idx} className="p-6">
              <h3 className="text-base font-semibold text-slate-900 mb-2">{feature.title}</h3>
              <p className="text-sm text-slate-600 leading-relaxed">{feature.description}</p>
            </Card>
          ))}
        </div>
      </section>

      {/* How It Works Section */}
      <section className="bg-slate-50 border border-slate-200 rounded-xl p-8 sm:p-10 max-w-5xl mx-auto space-y-8">
        <div className="text-center max-w-2xl mx-auto">
          <h2 className="text-2xl font-bold text-slate-900">How It Works</h2>
          <p className="text-sm text-slate-500 mt-1">
            A simple, three-step methodology for startup feasibility validation.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {steps.map((item, idx) => (
            <div key={idx} className="bg-white border border-slate-200 rounded-lg p-6 space-y-3">
              <span className="text-xs font-bold text-blue-600 tracking-wider block">{item.step}</span>
              <h3 className="text-base font-semibold text-slate-900">{item.title}</h3>
              <p className="text-sm text-slate-600 leading-relaxed">{item.description}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Call to Action */}
      <section className="text-center py-6">
        <Link to="/validator">
          <Button variant="primary" className="text-base px-8 py-3 space-x-2">
            <span>Start Validation</span>
            <ArrowRight className="w-4 h-4" />
          </Button>
        </Link>
      </section>
    </div>
  );
};

export default HomePage;

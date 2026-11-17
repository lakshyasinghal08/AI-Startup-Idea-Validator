import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Rocket, ShieldCheck, Search, Cpu, FileCheck2, ArrowRight, CheckCircle2 } from 'lucide-react';
import Button from '@/components/common/Button';
import Card from '@/components/common/Card';
import ideaApi from '@/api/ideaApi';

export const HomePage = () => {
  const [backendHealth, setBackendHealth] = useState(null);
  const [loadingHealth, setLoadingHealth] = useState(true);

  useEffect(() => {
    // Verify connection to the FastAPI backend service
    ideaApi.checkHealth()
      .then((data) => {
        setBackendHealth(data);
        setLoadingHealth(false);
      })
      .catch(() => {
        setBackendHealth({ status: 'offline' });
        setLoadingHealth(false);
      });
  }, []);

  const features = [
    {
      icon: Search,
      title: 'Tavily Web Search Agent',
      desc: 'Retrieves live market reports, recent funding, and real-world competitor landscape signals.',
    },
    {
      icon: Cpu,
      title: 'Multi-Agent AI Network',
      desc: 'Specialized autonomous agents assessing problem-solution fit, market sizing, and defensibility.',
    },
    {
      icon: ShieldCheck,
      title: 'Automated SWOT Analysis',
      desc: 'Objective 4-quadrant strategic matrix highlighting internal advantages and external threats.',
    },
    {
      icon: FileCheck2,
      title: 'Validation Dossiers & PDFs',
      desc: 'Compiles investor-grade executive briefs ready for export and angel presentations.',
    },
  ];

  return (
    <div className="space-y-12">
      {/* Hero Section */}
      <section className="text-center max-w-3xl mx-auto space-y-6 pt-6">
        <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-emerald-100/80 text-emerald-800 text-xs font-semibold tracking-wide">
          <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
          <span>Infosys Springboard 7.0 &bull; Milestone 1 Initialized</span>
        </div>

        <h1 className="text-4xl sm:text-5xl font-extrabold tracking-tight text-slate-900 leading-tight">
          Validate Startup Ideas with <span className="text-emerald-600">Multi-Agent AI</span> & Market Intelligence
        </h1>

        <p className="text-lg text-slate-600">
          Transform your startup hypothesis into an evidence-backed validation report. Analyze TAM/SAM/SOM, detect market competitors, and construct SWOT matrices automatically.
        </p>

        <div className="flex flex-wrap items-center justify-center gap-4 pt-2">
          <Link to="/validator">
            <Button variant="primary" className="space-x-2 text-base px-6 py-3">
              <span>Start Idea Validation</span>
              <ArrowRight className="w-4 h-4" />
            </Button>
          </Link>
          <Link to="/reports">
            <Button variant="secondary" className="text-base px-6 py-3">
              View Sample Reports
            </Button>
          </Link>
        </div>
      </section>

      {/* Backend Status Probe Banner */}
      <section className="max-w-2xl mx-auto">
        <Card className="bg-slate-900 text-white border-slate-800">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className={`w-3 h-3 rounded-full ${backendHealth?.status === 'healthy' ? 'bg-emerald-400' : 'bg-amber-400'} animate-ping`}></div>
              <div>
                <h4 className="text-sm font-semibold text-white">FastAPI Backend Status</h4>
                <p className="text-xs text-slate-400">
                  {loadingHealth ? 'Pinging /api/v1/health...' : `Status: ${backendHealth?.status || 'Unknown'} (${backendHealth?.environment || 'local'})`}
                </p>
              </div>
            </div>
            <span className="text-xs font-mono bg-slate-800 px-2.5 py-1 rounded text-slate-300">
              v1.0.0
            </span>
          </div>
        </Card>
      </section>

      {/* Feature Grid */}
      <section className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-4">
        {features.map((feature, idx) => {
          const Icon = feature.icon;
          return (
            <Card key={idx} className="hover:border-emerald-200 transition">
              <div className="flex items-start space-x-4">
                <div className="p-3 bg-emerald-50 text-emerald-600 rounded-lg">
                  <Icon className="w-6 h-6" />
                </div>
                <div>
                  <h3 className="font-semibold text-slate-900 text-lg">{feature.title}</h3>
                  <p className="text-sm text-slate-600 mt-1 leading-relaxed">{feature.desc}</p>
                </div>
              </div>
            </Card>
          );
        })}
      </section>
    </div>
  );
};

export default HomePage;

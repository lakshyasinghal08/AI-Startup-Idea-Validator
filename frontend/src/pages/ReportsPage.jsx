import React from 'react';
import { FileText, Download, ExternalLink, Calendar, CheckCircle } from 'lucide-react';
import Card from '@/components/common/Card';
import Button from '@/components/common/Button';

export const ReportsPage = () => {
  const sampleReports = [
    {
      id: 'idea_sample_01',
      title: 'EcoLogix - Cold Chain Fleet Intelligence',
      market: 'Logistics & Supply Chain',
      score: 84,
      date: '2026-11-14',
      status: 'COMPLETED',
    },
    {
      id: 'idea_sample_02',
      title: 'NeuroLearn - Adaptive Math Tutor for K-12',
      market: 'EdTech & E-Learning',
      score: 79,
      date: '2026-11-13',
      status: 'COMPLETED',
    },
  ];

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-slate-900">Validation Reports & Analytics</h1>
        <p className="text-slate-600 mt-1">
          Review previous validation dossiers and download PDF summaries. In Milestone 5 & 6, this is linked to PostgreSQL history and ReportLab PDF downloads.
        </p>
      </div>

      <div className="space-y-4">
        {sampleReports.map((report) => (
          <Card key={report.id} className="hover:border-slate-300 transition">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div className="space-y-1">
                <div className="flex items-center space-x-2">
                  <h3 className="font-semibold text-slate-900 text-lg">{report.title}</h3>
                  <span className="px-2 py-0.5 rounded-full text-xs font-medium bg-emerald-100 text-emerald-800 flex items-center space-x-1">
                    <CheckCircle className="w-3 h-3" />
                    <span>{report.status}</span>
                  </span>
                </div>
                <div className="flex items-center space-x-4 text-xs text-slate-500">
                  <span>Sector: <strong>{report.market}</strong></span>
                  <span className="flex items-center space-x-1">
                    <Calendar className="w-3.5 h-3.5" />
                    <span>{report.date}</span>
                  </span>
                  <span>ID: <code className="font-mono">{report.id}</code></span>
                </div>
              </div>

              <div className="flex items-center space-x-3">
                <div className="text-right pr-2">
                  <span className="text-2xl font-bold text-emerald-600">{report.score}%</span>
                  <span className="block text-[10px] text-slate-400 uppercase tracking-wider">Score</span>
                </div>
                <Button variant="secondary" className="space-x-1 text-xs px-3 py-2">
                  <Download className="w-3.5 h-3.5" />
                  <span>PDF Brief</span>
                </Button>
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
};

export default ReportsPage;

/**
 * FILENAME: LandingPage.tsx
 * DESCRIPTION/PURPOSE: Main landing page with VVL design system styling and consistent branding
 * Author: JP + 2025-06-15
 */

import React from 'react';
import { useNavigate } from 'react-router-dom';
import Footer from '@/components/Footer';
import { Sparkles, Rocket, Play, Settings, ArrowRight, CheckCircle } from 'lucide-react';

const LandingPage: React.FC = () => {
  const navigate = useNavigate();

  const benefits = [
    { title: '10x Faster', description: 'Campaign Creation' },
    { title: 'AI-Optimized', description: 'Content Strategy' },
    { title: 'Data-Driven', description: 'Performance Insights' },
    { title: 'Multi-Platform', description: 'Social Reach' }
  ];

  return (
    <div className="min-h-screen vvl-gradient-bg">
      {/* Header */}
      <header className="vvl-header-blur">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 rounded-lg flex items-center justify-center border border-slate-200">
                <span className="text-xs font-semibold">AIPG</span>
              </div>
              <h1 className="text-xl font-bold vvl-text-primary">AI Marketing Campaign Post Generator</h1>
            </div>
            <nav className="flex items-center space-x-3">
              <button onClick={() => navigate('/about')} className="vvl-button-secondary text-sm">About</button>
              <button onClick={() => navigate('/campaigns')} className="vvl-button-secondary text-sm">Campaigns</button>
              <button onClick={() => navigate('/new-campaign')} className="vvl-button-primary text-sm">Create Campaign</button>
              <button onClick={() => navigate('/settings')} className="vvl-button-secondary p-2" aria-label="Settings">
                <Settings className="w-4 h-4" />
              </button>
            </nav>
          </div>
        </div>
      </header>

      {/* Hero */}
      <section className="pt-16 pb-20">
        <div className="container mx-auto px-6">
          <div className="text-center max-w-3xl mx-auto">
            <div className="flex justify-center mb-6">
              <div className="w-16 h-16 rounded-xl border border-slate-200 flex items-center justify-center">
                <Sparkles className="w-8 h-8 text-slate-700" />
              </div>
            </div>
            <h1 className="text-5xl font-bold vvl-text-primary mb-4 leading-tight">
              Crisp AI-Powered Marketing
            </h1>
            <p className="text-lg vvl-text-secondary mb-8 leading-relaxed">
              Analyze your business, generate on-brand content, and publish across platforms with a clean, minimal workflow.
            </p>
            <div className="flex flex-col sm:flex-row gap-3 justify-center items-center">
              <button className="vvl-button-primary text-base px-7 py-3 flex items-center gap-2" onClick={() => navigate('/new-campaign')}>
                <Rocket className="w-5 h-5" />
                Create Your Campaign
              </button>
              <button className="vvl-button-secondary text-base px-7 py-3 flex items-center gap-2" onClick={() => navigate('/campaigns')}>
                <Play className="w-5 h-5" />
                View Demo
              </button>
            </div>

            {/* Quick Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6 max-w-2xl mx-auto mt-10">
              {benefits.map((b) => (
                <div key={b.title} className="text-center">
                  <div className="text-sm font-semibold vvl-text-primary">{b.title}</div>
                  <div className="text-xs vvl-text-secondary">{b.description}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-16 border-t border-slate-200">
        <div className="container mx-auto px-6 text-center">
          <h2 className="text-3xl font-bold vvl-text-primary mb-2">Ready to start?</h2>
          <p className="text-base vvl-text-secondary mb-6 max-w-2xl mx-auto">
            Create a campaign and let AI handle the heavy lifting.
          </p>
          <div className="flex flex-col sm:flex-row gap-3 justify-center items-center">
            <button className="bg-white text-slate-800 border border-slate-300 hover:bg-slate-50 text-base px-7 py-3 font-semibold rounded-lg transition-all duration-200 flex items-center gap-2" onClick={() => navigate('/new-campaign')}>
              <Rocket className="w-5 h-5" />
              Create Your First Campaign
            </button>
            <button className="vvl-button-primary text-base px-7 py-3 flex items-center gap-2" onClick={() => navigate('/campaigns')}>
              Explore Features
              <ArrowRight className="w-5 h-5" />
            </button>
          </div>

          <div className="mt-6 text-slate-500 text-sm">
            <div className="flex items-center justify-center gap-4">
              <div className="flex items-center gap-1">
                <CheckCircle className="w-4 h-4 text-emerald-500" />
                <span>No credit card required</span>
              </div>
              <div className="flex items-center gap-1">
                <CheckCircle className="w-4 h-4 text-emerald-500" />
                <span>Minimal UI</span>
              </div>
              <div className="flex items-center gap-1">
                <CheckCircle className="w-4 h-4 text-emerald-500" />
                <span>Powered by Google AI</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
};

export default LandingPage; 
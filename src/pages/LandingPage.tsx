/**
 * FILENAME: LandingPage.tsx
 * DESCRIPTION/PURPOSE: Main landing page with VVL design system styling and consistent branding
 * Author: JP + 2025-06-15
 */

import React from 'react';
import { useNavigate } from 'react-router-dom';
// Removed Material components - using VVL design system
import Footer from '@/components/Footer';
import { 
  Rocket, 
  Zap, 
  Target, 
  BarChart3, 
  Users, 
  Clock, 
  Sparkles, 
  Brain, 
  Palette, 
  Calendar,
  Play,
  ArrowRight,
  CheckCircle,
  TrendingUp,
  Globe,
  Briefcase,
  ShoppingBag,
  Heart,
  Megaphone,
  Building,
  Settings
} from 'lucide-react';

const LandingPage: React.FC = () => {
  const navigate = useNavigate();

  const benefits = [
    {
      icon: <Zap className="w-8 h-8 text-blue-400" />,
      title: "10x Faster",
      description: "Campaign Creation"
    },
    {
      icon: <Target className="w-8 h-8 text-green-400" />,
      title: "AI-Optimized",
      description: "Content Strategy"
    },
    {
      icon: <BarChart3 className="w-8 h-8 text-purple-400" />,
      title: "Data-Driven",
      description: "Performance Insights"
    },
    {
      icon: <Users className="w-8 h-8 text-orange-400" />,
      title: "Multi-Platform",
      description: "Social Reach"
    }
  ];

  const features = [
    {
      icon: <Brain className="w-12 h-12" />,
      title: "Intelligent Business Analysis",
      description: "Upload your website, documents, or describe your business. Our AI extracts key insights, understands your value proposition, and identifies your target audience automatically."
    },
    {
      icon: <Palette className="w-12 h-12" />,
      title: "Multi-Format Content Creation",
      description: "Generate optimized text posts, eye-catching images, and engaging videos tailored for each social media platform. All content aligns with your brand voice and marketing objectives."
    },
    {
      icon: <Calendar className="w-12 h-12" />,
      title: "Smart Scheduling & Publishing",
      description: "Automated posting at optimal times for maximum engagement. Monitor performance, track metrics, and adjust strategies in real-time across all your social media channels."
    },
    {
      icon: <Target className="w-12 h-12" />,
      title: "Campaign Optimization",
      description: "Continuous learning from performance data to improve future campaigns. A/B testing, audience insights, and conversion tracking built right in."
    },
    {
      icon: <Sparkles className="w-12 h-12" />,
      title: "Creative Ideation Engine",
      description: "Never run out of content ideas. Our AI generates fresh, relevant concepts based on trending topics, seasonal events, and your industry insights."
    },
    {
      icon: <BarChart3 className="w-12 h-12" />,
      title: "Performance Analytics",
      description: "Comprehensive reporting and analytics dashboard. Track ROI, engagement rates, conversion metrics, and get actionable insights to grow your business."
    }
  ];

  const useCases = [
    {
      icon: <Rocket className="w-12 h-12 text-blue-400" />,
      title: "Product Launches",
      description: "Generate buzz and drive sales for new product releases with targeted campaigns across all platforms."
    },
    {
      icon: <Building className="w-12 h-12 text-green-400" />,
      title: "Brand Awareness",
      description: "Build recognition and establish your brand presence with consistent, engaging content strategies."
    },
    {
      icon: <Briefcase className="w-12 h-12 text-purple-400" />,
      title: "Service Promotion",
      description: "Showcase your expertise and attract new clients with professional service-focused campaigns."
    },
    {
      icon: <ShoppingBag className="w-12 h-12 text-orange-400" />,
      title: "E-commerce Growth",
      description: "Drive traffic and boost online sales with conversion-optimized social media marketing."
    }
  ];

  return (
    <div className="min-h-screen vvl-gradient-bg">
      {/* Header */}
      <header className="vvl-header-blur">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">AIPG</span>
              </div>
              <h1 className="text-xl font-bold vvl-text-primary">AI Marketing Campaign Post Generator</h1>
            </div>
            <nav className="flex items-center space-x-4">
              <button 
                onClick={() => navigate('/about')}
                className="vvl-button-secondary text-sm"
              >
                About
              </button>
              <button 
                onClick={() => navigate('/campaigns')}
                className="vvl-button-secondary text-sm"
              >
                View Campaigns
              </button>
              <button
                onClick={() => navigate('/new-campaign')}
                className="vvl-button-primary text-sm"
              >
                Create Your Campaign
              </button>
              <button
                onClick={() => navigate('/settings')}
                className="vvl-button-secondary p-2"
                aria-label="Settings"
              >
                <Settings className="w-4 h-4" />
              </button>
            </nav>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="pt-20 pb-32">
        <div className="container mx-auto px-6">
          <div className="text-center max-w-4xl mx-auto">
            <div className="flex justify-center mb-8">
              <div className="w-20 h-20 bg-gradient-to-r from-blue-500 to-purple-600 rounded-2xl flex items-center justify-center">
                <Sparkles className="w-10 h-10 text-white" />
              </div>
            </div>
            
            <h1 className="text-5xl md:text-7xl font-bold vvl-text-primary mb-6 leading-tight">
              AI-Powered Marketing
              <span className="block vvl-text-accent">That Actually Works</span>
            </h1>
            
            <p className="text-xl md:text-2xl vvl-text-secondary mb-12 leading-relaxed max-w-3xl mx-auto">
              Transform your business with intelligent marketing campaigns. Our agentic AI analyzes your business, 
              creates compelling content, and manages your entire social media presence automatically.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-12">
              <button 
                className="vvl-button-primary text-lg px-8 py-4 flex items-center gap-2"
                onClick={() => navigate('/new-campaign')}
              >
                <Rocket className="w-5 h-5" />
                Create Your Campaign
              </button>
              
              <button 
                className="vvl-button-secondary text-lg px-8 py-4 flex items-center gap-2"
                onClick={() => navigate('/campaigns')}
              >
                <Play className="w-5 h-5" />
                View Demo
              </button>
            </div>

            {/* Quick Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-8 max-w-2xl mx-auto">
              {benefits.map((benefit, index) => (
                <div key={index} className="text-center">
                  <div className="flex justify-center mb-2">
                    {benefit.icon}
                  </div>
                  <div className="text-lg font-semibold text-white">{benefit.title}</div>
                  <div className="text-sm text-gray-400">{benefit.description}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-slate-800/50">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-white mb-4">
              AI-Powered Marketing That Just Works
            </h2>
            <p className="text-xl text-gray-300 max-w-2xl mx-auto">
              Our agentic AI system handles every aspect of your marketing campaign, 
              from business analysis to content creation and automated publishing.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <div key={index} className="vvl-card vvl-card-hover p-6">
                <div className="text-blue-400 mb-4">
                  {feature.icon}
                </div>
                <h3 className="text-xl font-semibold text-white mb-3">
                  {feature.title}
                </h3>
                <p className="text-gray-300 leading-relaxed">
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Use Cases Section */}
      <section className="py-20">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-white mb-4">
              Perfect for Every Marketing Need
            </h2>
            <p className="text-xl text-gray-300 max-w-2xl mx-auto">
              Whether you're launching a product, building brand awareness, or promoting services, 
              our AI adapts to your specific goals and industry.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {useCases.map((useCase, index) => (
              <div key={index} className="vvl-card vvl-card-hover p-6 text-center group">
                <div className="flex justify-center mb-4 group-hover:scale-110 transition-transform duration-200">
                  {useCase.icon}
                </div>
                <h3 className="text-lg font-semibold text-white mb-3">
                  {useCase.title}
                </h3>
                <p className="text-gray-300 text-sm leading-relaxed">
                  {useCase.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="py-20 bg-slate-800/50">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-white mb-4">
              From Idea to Published in Minutes
            </h2>
            <p className="text-xl text-gray-300 max-w-2xl mx-auto">
              Our streamlined workflow gets you from concept to live campaigns faster than ever before.
            </p>
          </div>

          <div className="max-w-4xl mx-auto">
            <div className="grid md:grid-cols-3 gap-8">
              <div className="text-center">
                <div className="w-16 h-16 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-2xl font-bold text-white">1</span>
                </div>
                <h3 className="text-xl font-semibold text-white mb-3">Analyze Your Business</h3>
                <p className="text-gray-300">
                  Upload your website, documents, or describe your business. Our AI extracts key insights and context.
                </p>
              </div>

              <div className="text-center">
                <div className="w-16 h-16 bg-gradient-to-r from-purple-500 to-pink-600 rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-2xl font-bold text-white">2</span>
                </div>
                <h3 className="text-xl font-semibold text-white mb-3">Generate Content</h3>
                <p className="text-gray-300">
                  AI creates optimized text, images, and videos for each platform, tailored to your brand and audience.
                </p>
              </div>

              <div className="text-center">
                <div className="w-16 h-16 bg-gradient-to-r from-pink-500 to-orange-600 rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-2xl font-bold text-white">3</span>
                </div>
                <h3 className="text-xl font-semibold text-white mb-3">Schedule & Publish</h3>
                <p className="text-gray-300">
                  Automated scheduling ensures optimal posting times while you monitor performance in real-time.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-r from-blue-600 to-purple-700">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-4xl font-bold text-white mb-4">
            Ready to Transform Your Marketing?
          </h2>
          <p className="text-xl text-blue-100 mb-8 max-w-2xl mx-auto">
            Join the future of marketing with AI that understands your business and creates campaigns that convert.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <button 
              className="bg-white text-blue-600 hover:bg-gray-100 text-lg px-8 py-4 font-semibold rounded-lg transition-all duration-200 flex items-center gap-2"
              onClick={() => navigate('/new-campaign')}
            >
              <Rocket className="w-5 h-5" />
              Create Your First Campaign
            </button>
            
            <button 
              className="text-white border border-white/30 hover:border-white hover:bg-white/10 text-lg px-8 py-4 rounded-lg transition-all duration-200 flex items-center gap-2"
              onClick={() => navigate('/campaigns')}
            >
              Explore Features
              <ArrowRight className="w-5 h-5" />
            </button>
          </div>

          <div className="mt-8 text-blue-100 text-sm">
            <div className="flex items-center justify-center gap-4">
              <div className="flex items-center gap-1">
                <CheckCircle className="w-4 h-4" />
                <span>No credit card required</span>
              </div>
              <div className="flex items-center gap-1">
                <CheckCircle className="w-4 h-4" />
                <span>MVP-grade functionality</span>
              </div>
              <div className="flex items-center gap-1">
                <CheckCircle className="w-4 h-4" />
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
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMarketingContext } from '@/contexts/MarketingContext';
import { Textarea } from '@/components/ui/textarea';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Slider } from '@/components/ui/slider';
import { ArrowLeft, Link2, Sparkles, Save } from 'lucide-react';
import { toast } from 'sonner';
import SaveCampaignDialog from '@/components/SaveCampaignDialog';

const NewCampaignPage: React.FC = () => {
  const navigate = useNavigate();
  const { createNewCampaign } = useMarketingContext();
  
  // Basic campaign info
  const [name, setName] = useState('');
  const [objective, setObjective] = useState('');
  const [businessDescription, setBusinessDescription] = useState('');
  
  // Single primary URL (we can still pass it through later)
  const [businessUrl, setBusinessUrl] = useState('');

  // AI tuning
  const [creativityLevel, setCreativityLevel] = useState([7]); // 1-10 scale
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [showSaveDialog, setShowSaveDialog] = useState(false);

  const handleAnalyzeUrl = async () => {
    if (!businessUrl) {
      toast.error('Please provide your website URL');
      return;
    }

    setIsAnalyzing(true);
    try {
      const response = await fetch('http://localhost:8000/api/v1/analysis/url', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ urls: [businessUrl], analysis_depth: 'standard' }),
      });

      if (!response.ok) throw new Error(`Analysis failed: ${response.status}`);

      const analysisResult = await response.json();
      const businessAnalysis = analysisResult.business_analysis;
      if (businessAnalysis) {
        const autoDescription = `Company: ${businessAnalysis.company_name}\nIndustry: ${businessAnalysis.industry}\nTarget Audience: ${businessAnalysis.target_audience}\nBrand Voice: ${businessAnalysis.brand_voice}\n\nValue Propositions:\n${businessAnalysis.value_propositions?.map((vp: string) => `• ${vp}`).join('\n') || '• Not specified'}\n\nCompetitive Advantages:\n${businessAnalysis.competitive_advantages?.map((ca: string) => `• ${ca}`).join('\n') || '• Not specified'}\n\nMarket Positioning: ${businessAnalysis.market_positioning}`.trim();
        setBusinessDescription(autoDescription);
        toast.success('✨ AI analysis complete. Business context populated.');
      } else {
        toast.success('URL analyzed. Please review the extracted information.');
      }
    } catch (error) {
      console.error('URL analysis error:', error);
      toast.error('Failed to analyze URL. Please try again.');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!name || !objective) {
      toast.error('Please fill in campaign name and objective');
      return;
    }
    if (!businessDescription && !businessUrl) {
      toast.error('Please provide business context via description or URL');
      return;
    }

    createNewCampaign({
      name,
      businessDescription,
      objective,
      businessUrl,
      campaignType: 'product',
      creativityLevel: creativityLevel[0],
    });

    toast.success('Campaign created!');
    navigate('/ideation');
  };

  return (
    <div className="min-h-screen vvl-gradient-bg text-slate-900">
      <header className="vvl-header-blur sticky top-0 z-50">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <button onClick={() => navigate(-1)} className="vvl-button-secondary p-2 rounded-full">
                <ArrowLeft className="w-5 h-5" />
              </button>
              <h1 className="text-xl font-bold vvl-text-primary">Create New Campaign</h1>
            </div>
            <div className="flex items-center space-x-3">
              <button className="vvl-button-secondary text-sm" onClick={() => setShowSaveDialog(true)}>
                <Save className="w-4 h-4 mr-2" />
                Save as Template
              </button>
              <button className="vvl-button-primary text-sm" onClick={handleSubmit}>
                <Sparkles className="w-4 h-4 mr-2" />
                Start AI Generation
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="container mx-auto p-6">
        <form onSubmit={handleSubmit} className="space-y-8">
          {/* Basic Information */}
          <div className="vvl-card p-8">
            <h2 className="text-2xl font-bold mb-6 vvl-text-accent">Basic Information</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <Label htmlFor="name" className="text-sm mb-2 block">Campaign Name</Label>
                <Input id="name" value={name} onChange={(e) => setName(e.target.value)} placeholder="e.g., Summer 2025 Launch" className="vvl-input" />
              </div>
              <div>
                <Label htmlFor="objective" className="text-sm mb-2 block">Primary Objective</Label>
                <Input id="objective" value={objective} onChange={(e) => setObjective(e.target.value)} placeholder="e.g., Increase brand awareness" className="vvl-input" />
              </div>
            </div>
          </div>

          {/* Business Context */}
          <div className="vvl-card p-8">
            <h2 className="text-2xl font-bold mb-6 vvl-text-accent">Business Context</h2>

            {/* URL Analysis */}
            <div className="space-y-4 mb-6 p-6 border border-slate-200 rounded-lg">
              <h3 className="text-lg font-semibold flex items-center gap-2"><Link2 className="w-5 h-5"/>Analyze by URL</h3>
              <div className="grid grid-cols-1 gap-3">
                <Input value={businessUrl} onChange={(e) => setBusinessUrl(e.target.value)} placeholder="https://your-website.com" className="vvl-input" />
              </div>
              <button type="button" onClick={handleAnalyzeUrl} disabled={isAnalyzing} className={`vvl-button-secondary ${isAnalyzing ? 'state-in-progress' : ''}`}>
                {isAnalyzing ? 'Analyzing…' : 'Analyze URL with AI'}
              </button>
            </div>

            {/* Manual Description */}
            <div>
              <Label htmlFor="businessDescription" className="text-sm mb-2 block">Or describe your business</Label>
              <Textarea id="businessDescription" value={businessDescription} onChange={(e) => setBusinessDescription(e.target.value)} placeholder="Describe your company, products, services, and target audience…" rows={8} className="vvl-textarea" />
            </div>
          </div>

          {/* AI Settings */}
          <div className="vvl-card p-8">
            <h2 className="text-2xl font-bold mb-6 vvl-text-accent">AI Settings</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="md:col-span-2">
                <Label className="text-sm mb-2 block">Creativity Level: <span className="font-semibold vvl-text-accent">{creativityLevel[0]}</span></Label>
                <Slider defaultValue={[7]} min={1} max={10} step={1} onValueChange={setCreativityLevel} />
                <div className="flex justify-between text-xs vvl-text-secondary mt-1">
                  <span>Structured</span>
                  <span>Balanced</span>
                  <span>Creative</span>
                </div>
              </div>
            </div>
          </div>
        </form>
      </main>
      <SaveCampaignDialog open={showSaveDialog} onClose={() => setShowSaveDialog(false)} />
    </div>
  );
};

export default NewCampaignPage;

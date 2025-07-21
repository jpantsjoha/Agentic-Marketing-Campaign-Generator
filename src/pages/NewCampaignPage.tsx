import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMarketingContext } from '@/contexts/MarketingContext';
import { Textarea } from '@/components/ui/textarea';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Slider } from '@/components/ui/slider';
import { ArrowLeft, Upload, Link2, Image, FileText, Sparkles, Globe, Package, CloudUpload, Save } from 'lucide-react';
import { toast } from 'sonner';
import SaveCampaignDialog from '@/components/SaveCampaignDialog';

const NewCampaignPage: React.FC = () => {
  const navigate = useNavigate();
  const { createNewCampaign } = useMarketingContext();
  
  // Basic campaign info
  const [name, setName] = useState('');
  const [objective, setObjective] = useState('');
  const [businessDescription, setBusinessDescription] = useState('');
  const [exampleContent, setExampleContent] = useState('');
  
  // Enhanced features
  const [businessUrl, setBusinessUrl] = useState('');
  const [aboutPageUrl, setAboutPageUrl] = useState('');
  const [productServiceUrl, setProductServiceUrl] = useState('');
  const [campaignType, setCampaignType] = useState<'product' | 'service' | 'brand' | 'event'>('product');
  const [creativityLevel, setCreativityLevel] = useState([7]); // 1-10 scale
  
  // File uploads
  const [uploadedImages, setUploadedImages] = useState<File[]>([]);
  const [uploadedDocuments, setUploadedDocuments] = useState<File[]>([]);
  const [campaignAssets, setCampaignAssets] = useState<File[]>([]);
  
  // Campaign template upload
  const [campaignTemplate, setCampaignTemplate] = useState<File | null>(null);
  const [isLoadingTemplate, setIsLoadingTemplate] = useState(false);
  
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [showSaveDialog, setShowSaveDialog] = useState(false);

  const handleCampaignTemplateUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setCampaignTemplate(file);
      
      setIsLoadingTemplate(true);
      try {
        const reader = new FileReader();
        reader.onload = (event) => {
          try {
            const template = JSON.parse(event.target?.result as string);
            setName(template.name || '');
            setObjective(template.objective || '');
            setBusinessDescription(template.businessDescription || '');
            setCampaignType(template.campaignType || 'product');
            setCreativityLevel([template.creativityLevel || 7]);
            toast.success('Campaign template loaded successfully!');
          } catch (error) {
            toast.error('Invalid campaign template format');
          }
        };
        reader.readAsText(file);
      } catch (error) {
        toast.error('Failed to load campaign template');
      } finally {
        setIsLoadingTemplate(false);
      }
    }
  };

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setUploadedImages(prev => [...prev, ...Array.from(e.target.files!)]);
    }
  };

  const handleDocumentUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setUploadedDocuments(prev => [...prev, ...Array.from(e.target.files!)]);
    }
  };

  const handleAssetUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setCampaignAssets(prev => [...prev, ...Array.from(e.target.files!)]);
    }
  };

  const removeFile = (fileList: File[], setFileList: React.Dispatch<React.SetStateAction<File[]>>, index: number) => {
    setFileList(prev => prev.filter((_, i) => i !== index));
  };

  const handleAnalyzeUrls = async () => {
    if (!businessUrl && !aboutPageUrl && !productServiceUrl) {
      toast.error('Please provide at least one URL to analyze');
      return;
    }

    setIsAnalyzing(true);
    try {
      const urls = [businessUrl, aboutPageUrl, productServiceUrl].filter(url => url && url.trim());
      
      // Use the proper API client instead of hardcoded fetch
      const { VideoVentureLaunchAPI } = await import('@/lib/api');
      const analysisResult = await VideoVentureLaunchAPI.analyzeUrls({
        urls: urls,
        analysis_type: 'business_context'
      });
      const businessAnalysis = analysisResult.business_analysis;
      if (businessAnalysis) {
        const autoDescription = `Company: ${businessAnalysis.company_name}\nIndustry: ${businessAnalysis.industry}\nTarget Audience: ${businessAnalysis.target_audience}\nBrand Voice: ${businessAnalysis.brand_voice}\n\nValue Propositions:\n${businessAnalysis.value_propositions?.map((vp: string) => `• ${vp}`).join('\n') || '• Not specified'}\n\nCompetitive Advantages:\n${businessAnalysis.competitive_advantages?.map((ca: string) => `• ${ca}`).join('\n') || '• Not specified'}\n\nMarket Positioning: ${businessAnalysis.market_positioning}`.trim();
        setBusinessDescription(autoDescription);
        toast.success(`✨ AI Analysis Complete! \n\nCompany: ${businessAnalysis.company_name}\nIndustry: ${businessAnalysis.industry}\nConfidence: ${Math.round((analysisResult.confidence_score || 0.75) * 100)}%\n\nBusiness context has been automatically populated below.`, { duration: 6000 });
      } else {
        toast.success('URLs analyzed! Please review the extracted information.');
      }
    } catch (error) {
      console.error('URL analysis error:', error);
      toast.error('Failed to analyze URLs. Please check your connection and try again.');
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

    if (!businessDescription && !businessUrl && uploadedImages.length === 0 && uploadedDocuments.length === 0) {
      toast.error('Please provide business context through description, URL, or uploaded files');
      return;
    }
    
    createNewCampaign({
      name,
      businessDescription,
      objective,
      exampleContent,
      // Enhanced campaign data
      businessUrl,
      aboutPageUrl,
      productServiceUrl,
      campaignType,
      creativityLevel: creativityLevel[0],
      uploadedImages,
      uploadedDocuments,
      campaignAssets
    });
    
    toast.success('Campaign created! AI is analyzing your business context...');
    navigate('/ideation');
  };

  const creativityLabels = {
    1: 'Conservative',
    3: 'Balanced',
    5: 'Creative', 
    7: 'Innovative',
    10: 'Experimental'
  };
  
  return (
    <div className="min-h-screen vvl-gradient-bg text-white">
      <header className="vvl-header-blur sticky top-0 z-50">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <button onClick={() => navigate(-1)} className="vvl-button-secondary p-2 rounded-full">
                <ArrowLeft className="w-5 h-5" />
              </button>
              <h1 className="text-xl font-bold vvl-text-primary">Create New Campaign</h1>
            </div>
            <div className="flex items-center space-x-4">
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
          
          {/* Basic Campaign Information Card */}
          <div className="vvl-card p-8">
            <h2 className="text-2xl font-bold mb-6 vvl-text-accent flex items-center"><Package className="w-6 h-6 mr-3" />Basic Information</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <Label htmlFor="name" className="text-lg mb-2 block">Campaign Name</Label>
                <Input id="name" value={name} onChange={(e) => setName(e.target.value)} placeholder="e.g., Summer 2025 Product Launch" className="vvl-input" />
              </div>
              <div>
                <Label htmlFor="objective" className="text-lg mb-2 block">Primary Objective</Label>
                <Input id="objective" value={objective} onChange={(e) => setObjective(e.target.value)} placeholder="e.g., Increase brand awareness in North America" className="vvl-input" />
              </div>
            </div>
          </div>

          {/* Business Context Card */}
          <div className="vvl-card p-8">
            <h2 className="text-2xl font-bold mb-6 vvl-text-accent flex items-center"><Globe className="w-6 h-6 mr-3" />Business Context</h2>
            
            {/* URL Analysis Section */}
            <div className="space-y-4 mb-8 p-6 border border-white/20 rounded-lg">
                <h3 className="text-xl font-semibold flex items-center"><Link2 className="w-5 h-5 mr-2"/>Analyze by URL (Fastest)</h3>
                <p className="vvl-text-secondary">Provide your website URL and we'll automatically extract business context.</p>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <Input value={businessUrl} onChange={(e) => setBusinessUrl(e.target.value)} placeholder="https://your-main-website.com" className="vvl-input" />
                  <Input value={aboutPageUrl} onChange={(e) => setAboutPageUrl(e.target.value)} placeholder="Optional: About Us page URL" className="vvl-input" />
                  <Input value={productServiceUrl} onChange={(e) => setProductServiceUrl(e.target.value)} placeholder="Optional: Product/Service page URL" className="vvl-input" />
                </div>
                <button type="button" onClick={handleAnalyzeUrls} disabled={isAnalyzing} className="vvl-button-secondary">
                  {isAnalyzing ? 'Analyzing...' : 'Analyze URLs with AI'}
                </button>
            </div>

            {/* Manual Description Section */}
            <div className="mb-6">
              <Label htmlFor="businessDescription" className="text-lg mb-2 block">Or Describe Your Business Manually</Label>
              <Textarea id="businessDescription" value={businessDescription} onChange={(e) => setBusinessDescription(e.target.value)} placeholder="Describe your company, products, services, and target audience..." rows={8} className="vvl-textarea" />
            </div>

            {/* File Uploads Section */}
            <div className="space-y-4 p-6 border border-white/20 rounded-lg">
              <h3 className="text-xl font-semibold flex items-center"><CloudUpload className="w-5 h-5 mr-2"/>Upload Additional Context</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {renderFileUpload("Images", "images", uploadedImages, handleImageUpload, removeFile.bind(null, uploadedImages, setUploadedImages), <Image className="w-5 h-5 mr-2"/>)}
                {renderFileUpload("Documents", "documents", uploadedDocuments, handleDocumentUpload, removeFile.bind(null, uploadedDocuments, setUploadedDocuments), <FileText className="w-5 h-5 mr-2"/>)}
                {renderFileUpload("Campaign Assets", "assets", campaignAssets, handleAssetUpload, removeFile.bind(null, campaignAssets, setCampaignAssets), <Sparkles className="w-5 h-5 mr-2"/>)}
              </div>
            </div>
          </div>

          {/* AI Generation Settings Card */}
          <div className="vvl-card p-8">
            <h2 className="text-2xl font-bold mb-6 vvl-text-accent flex items-center"><Sparkles className="w-6 h-6 mr-3" />AI Settings</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              <div>
                <Label htmlFor="campaignType" className="text-lg mb-2 block">Campaign Type</Label>
                <select id="campaignType" value={campaignType} onChange={(e) => setCampaignType(e.target.value as any)} className="vvl-input w-full">
                  <option value="product">Product Launch</option>
                  <option value="service">Service Promotion</option>
                  <option value="brand">Brand Awareness</option>
                  <option value="event">Event Promotion</option>
                </select>
              </div>
              <div>
                <Label className="text-lg mb-2 block">Creativity Level: <span className="font-bold vvl-text-accent">{creativityLevel[0]}</span></Label>
                <Slider defaultValue={[7]} min={1} max={10} step={1} onValueChange={setCreativityLevel} />
                <div className="flex justify-between text-sm vvl-text-secondary mt-1">
                  <span>Structured</span>
                  <span>Balanced</span>
                  <span>Creative</span>
                </div>
              </div>
            </div>
          </div>
        </form>
      </main>
      
      <SaveCampaignDialog
        open={showSaveDialog}
        onClose={() => setShowSaveDialog(false)}
      />
    </div>
  );
};

const renderFileUpload = (title: string, id: string, files: File[], onChange: (e: React.ChangeEvent<HTMLInputElement>) => void, onRemove: (index: number) => void, icon: React.ReactNode) => (
  <div className="space-y-2">
    <Label htmlFor={id} className="text-lg flex items-center">{icon}{title}</Label>
    <div className="vvl-input flex items-center">
      <Input id={id} type="file" multiple onChange={onChange} className="hidden" />
      <label htmlFor={id} className="cursor-pointer text-blue-400 hover:text-blue-300">
        Choose files...
      </label>
    </div>
    <div className="space-y-1 mt-2 text-sm">
      {files.map((file, index) => (
        <div key={index} className="flex justify-between items-center bg-white/5 p-1 rounded">
          <span className="truncate">{file.name}</span>
          <button type="button" onClick={() => onRemove(index)} className="text-red-400 hover:text-red-300">X</button>
        </div>
      ))}
    </div>
  </div>
);

export default NewCampaignPage;

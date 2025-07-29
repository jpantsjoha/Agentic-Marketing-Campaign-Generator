import React, { createContext, useContext, useState, useEffect } from 'react';
import VideoVentureLaunchAPI from '../lib/api';

export type SocialMediaPost = {
  id: string;
  type: 'text-only' | 'text-with-image' | 'text-with-video';
  platform: 'linkedin' | 'twitter' | 'instagram' | 'facebook' | 'tiktok';
  content: {
    text: string;
    hashtags: string[];
    imageUrl?: string;
    videoUrl?: string;
    productUrl?: string; // For URL unfurling
  };
  generationPrompt: string; // Full prompt used to generate this post
  selected?: boolean;
  scheduledFor?: string; // ISO date string
  posted?: boolean;
  postId?: string; // Social media platform post ID
};

export type SocialMediaColumn = {
  id: string;
  title: string;
  description: string;
  mediaType: 'text-only' | 'text-with-image' | 'text-with-video';
  posts: SocialMediaPost[];
  isGenerating?: boolean;
};

export type ScheduledPost = {
  id: string;
  post: SocialMediaPost;
  scheduledTime: string;
  platform: string;
  status: 'pending' | 'posted' | 'failed';
  campaignId: string;
};

export type CampaignTemplate = {
  id: string;
  name: string;
  description: string;
  prompts: {
    summary: string;
    themes: string[];
    tags: string[];
    socialPosts: string;
  };
  settings: {
    creativityLevel: number;
    campaignType: string;
    preferredDesign: string;
  };
  createdAt: string;
};

export type Campaign = {
  id: string;
  name: string;
  businessDescription: string;
  objective: string;
  exampleContent?: string;
  preferredDesign?: string;
  createdAt: string;
  generatedIdeas?: IdeaType[];
  selectedThemes?: string[];
  selectedTags?: string[];
  // Enhanced campaign fields
  businessUrl?: string;
  aboutPageUrl?: string;
  productServiceUrl?: string;
  campaignType?: 'product' | 'service' | 'brand' | 'event';
  creativityLevel?: number;
  uploadedImages?: File[];
  uploadedDocuments?: File[];
  campaignAssets?: File[];
  // Social media enhancements
  socialMediaColumns?: SocialMediaColumn[];
  selectedPosts?: SocialMediaPost[];
  campaignTemplate?: CampaignTemplate;
  // AI Analysis results
  aiAnalysis?: {
    summary: string;
    businessAnalysis: any;
    campaignGuidance: any;
    lastUpdated: string;
  };
};

export type IdeaType = {
  id: string;
  title: string;
  description: string;
  videoUrl?: string;
  imageUrl?: string;
  platforms: {
    linkedin?: string;
    twitter?: string;
    instagram?: string;
  };
  tags: string[];
  themes: string[];
  selected?: boolean;
};

interface MarketingContextType {
  campaigns: Campaign[];
  currentCampaign: Campaign | null;
  generatedIdeas: IdeaType[];
  aiSummary: string;
  suggestedThemes: string[];
  suggestedTags: string[];
  selectedThemes: string[];
  selectedTags: string[];
  selectedIdeas: IdeaType[];
  createNewCampaign: (campaign: Omit<Campaign, 'id' | 'createdAt'>) => void;
  setCurrentCampaign: (campaignId: string) => void;
  updateCurrentCampaign: (updates: Partial<Campaign>) => void;
  updateAiSummary: (summary: string) => void;
  generateIdeas: () => Promise<void>;
  selectTheme: (theme: string) => void;
  unselectTheme: (theme: string) => void;
  selectTag: (tag: string) => void;
  unselectTag: (tag: string) => void;
  generateVideos: () => Promise<void>;
  toggleIdeaSelection: (ideaId: string) => void;
  saveCampaign: (campaignName: string) => Promise<void>;
  exportToText: () => void;
  loadCampaign: (campaignId: string) => Promise<void>;
  getSavedCampaigns: () => SavedCampaign[];
  deleteSavedCampaign: (campaignId: string) => void;
}

interface BusinessUrls {
  website?: string;
  aboutPage?: string;
  productPage?: string;
}

interface UploadedFile {
  id: string;
  name: string;
  type: string;
  url: string;
  category: 'images' | 'documents' | 'campaigns';
}

interface SavedCampaign {
  id: string;
  name: string;
  createdAt: Date;
  lastModified: Date;
  campaignData: {
    businessDescription: string;
    objective: string;
    targetAudience: string;
    campaignType: string;
    creativityLevel: number;
    businessUrls: BusinessUrls;
    uploadedFiles: UploadedFile[];
    selectedThemes: string[];
    selectedTags: string[];
    generatedColumns: SocialMediaColumn[];
    selectedPosts: string[];
    schedulingConfig: any;
  };
}

const MarketingContext = createContext<MarketingContextType | undefined>(undefined);

// Real AI analysis function using stored business analysis data
const generateRealAISummary = (campaign: Campaign, businessAnalysis?: any): string => {
  // If we have real business analysis data, use it
  if (businessAnalysis || campaign.aiAnalysis?.businessAnalysis) {
    const analysis = businessAnalysis || campaign.aiAnalysis?.businessAnalysis;
    
    const companyName = analysis.company_name || 'Your Company';
    const industry = analysis.industry || 'your industry';
    const targetAudience = analysis.target_audience || 'your target audience';
    const valuePropositions = analysis.value_propositions || [];
    const competitiveAdvantages = analysis.competitive_advantages || [];
    
    let summary = `AI Analysis: ${companyName} operates in ${industry}, targeting ${targetAudience}.`;
    
    if (valuePropositions.length > 0) {
      summary += ` Key value propositions: ${valuePropositions.slice(0, 2).join(', ')}.`;
    }
    
    if (competitiveAdvantages.length > 0) {
      summary += ` Competitive advantages: ${competitiveAdvantages.slice(0, 2).join(', ')}.`;
    }
    
    // Add campaign-specific insights
    if (campaign.objective) {
      summary += ` Campaign objective: ${campaign.objective}.`;
    }
    
    return summary;
  }
  
  // Fallback for when no business analysis is available
  if (campaign.businessDescription && campaign.objective) {
    return `Campaign Analysis: Targeting ${campaign.objective} objective. Business focus: ${campaign.businessDescription.slice(0, 100)}${campaign.businessDescription.length > 100 ? '...' : ''}. Analysis pending URL processing.`;
  }
  
  return 'AI Analysis: Campaign analysis will be generated once business context is provided.';
};

// Helper functions for generating themes and tags from AI analysis
const generateCreativeThemes = (businessAnalysis: any): string[] => {
  const industry = businessAnalysis.industry?.toLowerCase() || '';
  const targetAudience = businessAnalysis.target_audience?.toLowerCase() || '';
  
  // Industry-based creative theme selection
  if (industry.includes('tech') || industry.includes('software') || industry.includes('digital')) {
    return ["Modern", "Futuristic", "Clean", "Professional", "Dynamic"];
  } else if (industry.includes('fashion') || industry.includes('apparel') || industry.includes('clothing')) {
    return ["Trendy", "Colorful", "Modern", "Hipster", "Vibrant"];
  } else if (industry.includes('food') || industry.includes('restaurant')) {
    return ["Colorful", "Playful", "Modern", "Elegant", "Artistic"];
  } else if (industry.includes('finance') || industry.includes('banking')) {
    return ["Professional", "Clean", "Sophisticated", "Corporate", "Modern"];
  } else if (industry.includes('health') || industry.includes('medical')) {
    return ["Clean", "Professional", "Modern", "Elegant", "Minimalist"];
  } else {
    return ["Professional", "Modern", "Clean", "Sophisticated", "Dynamic"];
  }
};

const generateBusinessTags = (businessAnalysis: any): string[] => {
  const tags: string[] = [];
  
  // Extract from company name
  if (businessAnalysis.company_name) {
    const cleanName = businessAnalysis.company_name.replace(/\s+/g, '').replace(/[^a-zA-Z0-9]/g, '');
    if (cleanName.length > 2 && cleanName.length < 20) {
      tags.push(`#${cleanName}`);
    }
  }
  
  // Extract from value propositions
  if (businessAnalysis.value_propositions && Array.isArray(businessAnalysis.value_propositions)) {
    businessAnalysis.value_propositions.slice(0, 3).forEach((prop: string) => {
      const words = prop.split(/\s+/).slice(0, 2); // First 2 words
      words.forEach((word: string) => {
        const cleanWord = word.replace(/[^a-zA-Z0-9]/g, '');
        if (cleanWord.length > 3 && cleanWord.length < 15) {
          tags.push(`#${cleanWord}`);
        }
      });
    });
  }
  
  // Extract from industry
  if (businessAnalysis.industry) {
    const industryWords = businessAnalysis.industry.split(/[\s(),]+/).filter((word: string) => word.length > 3);
    industryWords.slice(0, 2).forEach((word: string) => {
      const cleanWord = word.replace(/[^a-zA-Z0-9]/g, '');
      if (cleanWord.length > 3) {
        tags.push(`#${cleanWord}`);
      }
    });
  }
  
  // Add default business-specific tags if none generated
  if (tags.length === 0) {
    // Determine business type from description for contextual default tags
    const businessType = description.toLowerCase();
    if (businessType.includes('photography') || businessType.includes('photographer')) {
      tags.push("#Photography", "#CreativeArt", "#ProfessionalPhotos", "#ArtisticVision", "#QualityService");
    } else if (businessType.includes('food') || businessType.includes('restaurant') || businessType.includes('catering')) {
      tags.push("#Food", "#Culinary", "#Dining", "#FreshIngredients", "#DeliciousEats");
    } else if (businessType.includes('fitness') || businessType.includes('gym') || businessType.includes('health')) {
      tags.push("#Fitness", "#Health", "#Wellness", "#ActiveLifestyle", "#HealthyLiving");
    } else if (businessType.includes('tech') || businessType.includes('software') || businessType.includes('digital')) {
      tags.push("#Technology", "#Innovation", "#Digital", "#TechSolutions", "#ModernTech");
    } else if (businessType.includes('art') || businessType.includes('creative') || businessType.includes('design')) {
      tags.push("#Art", "#Creative", "#Design", "#ArtisticExpression", "#CreativeWork");
    } else {
      // Generic professional tags as last resort
      tags.push("#Professional", "#Quality", "#Service", "#Excellence", "#Trusted");
    }
  }
  
  // Remove duplicates and limit
  return [...new Set(tags)].slice(0, 10);
};

const mockGenerateThemesAndTags = (description: string, objective: string): { themes: string[], tags: string[] } => {
  // Detect business type from description for contextual fallback tags
  const desc = description.toLowerCase();
  const obj = objective.toLowerCase();
  
  // Photography business detection
  if (desc.includes('photography') || desc.includes('photographer') || desc.includes('photo') || 
      desc.includes('wedding') || desc.includes('portrait') || desc.includes('studio') ||
      obj.includes('photography') || obj.includes('photographer')) {
    return {
      themes: ['Professional', 'Artistic', 'Creative', 'Elegant', 'Memorable'],
      tags: ['Photography', 'WeddingPhotographer', 'PortraitPhotography', 'ProfessionalHeadshots', 'ArtisticPhotography', 'StudioPhotography']
    };
  }
  
  // Food/Restaurant business detection
  if (desc.includes('food') || desc.includes('restaurant') || desc.includes('catering') ||
      desc.includes('chef') || desc.includes('cuisine') || desc.includes('dining')) {
    return {
      themes: ['Delicious', 'Fresh', 'Artisanal', 'Quality', 'Memorable'],
      tags: ['FoodPhotography', 'Restaurant', 'Catering', 'ChefSpecial', 'FreshIngredients', 'CulinaryArt']
    };
  }
  
  // Fitness business detection
  if (desc.includes('fitness') || desc.includes('gym') || desc.includes('workout') ||
      desc.includes('health') || desc.includes('wellness') || desc.includes('trainer')) {
    return {
      themes: ['Energetic', 'Motivational', 'Healthy', 'Strong', 'Transformative'],
      tags: ['Fitness', 'Gym', 'Workout', 'HealthyLifestyle', 'PersonalTrainer', 'WellnessJourney']
    };
  }
  
  // Tech business detection
  if (desc.includes('tech') || desc.includes('software') || desc.includes('app') ||
      desc.includes('digital') || desc.includes('developer') || desc.includes('startup')) {
    return {
      themes: ['Innovative', 'Modern', 'Efficient', 'Scalable', 'User-Friendly'],
      tags: ['Technology', 'Software', 'Innovation', 'DigitalTransformation', 'TechSolutions', 'StartupLife']
    };
  }
  
  // Generic business fallback
  return {
    themes: ['Professional', 'Modern', 'Innovative', 'Trustworthy', 'Friendly'],
    tags: ['Professional', 'QualityService', 'CustomerFocused', 'Innovation', 'Excellence', 'Growth']
  };
};

const mockGenerateIdeas = (description: string, objective: string, themes: string[], tags: string[]): IdeaType[] => {
  return Array(6).fill(null).map((_, idx) => ({
    id: `idea-${Date.now()}-${idx}`,
    title: `Marketing Idea ${idx + 1}`,
    description: `This is a generated marketing idea that aligns with your selected themes and tags. It would showcase your business in a way that meets your ${objective} objective.`,
    imageUrl: "https://picsum.photos/400/300?random=101",
    videoUrl: undefined, // Would be generated later
    platforms: {
      linkedin: "Sample LinkedIn post text would go here...",
      twitter: "Sample Twitter post text would go here... #hashtags",
      instagram: "Sample Instagram caption would go here... #hashtags"
    },
    tags: tags.slice(0, 3),
    themes: themes.slice(0, 2),
    selected: false
  }));
};

const mockGenerateVideos = (ideas: IdeaType[]): IdeaType[] => {
  return ideas.map(idea => ({
    ...idea,
    // ADR-020 REGRESSION PREVENTION: Remove forbidden demo video URL that caused generic content issue
    // FORBIDDEN: https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4 (generic demo video)
    videoUrl: null // Will be generated via real APIs or show placeholder with clear demo labeling
  }));
};

export const MarketingProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [currentCampaign, setCurrentCampaign] = useState<Campaign | null>(null);
  const [generatedIdeas, setGeneratedIdeas] = useState<IdeaType[]>([]);
  const [aiSummary, setAiSummary] = useState<string>('');
  const [suggestedThemes, setSuggestedThemes] = useState<string[]>([]);
  const [suggestedTags, setSuggestedTags] = useState<string[]>([]);
  const [selectedThemes, setSelectedThemes] = useState<string[]>([]);
  const [selectedTags, setSelectedTags] = useState<string[]>([]);
  const [selectedIdeas, setSelectedIdeas] = useState<IdeaType[]>([]);
  const [urlAnalysisCache, setUrlAnalysisCache] = useState<Record<string, boolean>>({});

  // Load campaigns from localStorage on initial render
  useEffect(() => {
    const savedCampaigns = localStorage.getItem('marketingCampaigns');
    if (savedCampaigns) {
      setCampaigns(JSON.parse(savedCampaigns));
    }
    
    const currentCampaignId = localStorage.getItem('currentCampaignId');
    if (currentCampaignId) {
      const savedCampaigns = JSON.parse(localStorage.getItem('marketingCampaigns') || '[]');
      const campaign = savedCampaigns.find((c: Campaign) => c.id === currentCampaignId);
      if (campaign) {
        setCurrentCampaignState(campaign);
      }
    }

    // Load URL analysis cache
    const analysisCache = localStorage.getItem('urlAnalysisCache');
    if (analysisCache) {
      setUrlAnalysisCache(JSON.parse(analysisCache));
    }
  }, []);

  // Save campaigns to localStorage whenever they change (debounced)
  useEffect(() => {
    if (campaigns.length > 0) {
      const timeoutId = setTimeout(() => {
        localStorage.setItem('marketingCampaigns', JSON.stringify(campaigns));
      }, 500); // Debounce to prevent excessive localStorage writes
      
      return () => clearTimeout(timeoutId);
    }
  }, [campaigns]);

  // AUTO URL ANALYSIS: Automatically analyze URLs and populate themes/tags when campaign changes
  useEffect(() => {
    if (currentCampaign && (currentCampaign.businessUrl || currentCampaign.aboutPageUrl || currentCampaign.productServiceUrl)) {
      const cacheKey = `${currentCampaign.id}-${[currentCampaign.businessUrl, currentCampaign.aboutPageUrl, currentCampaign.productServiceUrl].filter(Boolean).join(',')}`;
      
      // Only run auto-analysis if we haven't analyzed these URLs for this campaign before
      if (!urlAnalysisCache[cacheKey] && suggestedThemes.length === 0 && suggestedTags.length === 0) {
        performUrlAnalysis(currentCampaign, cacheKey);
      }
    }
  }, [currentCampaign?.id, currentCampaign?.businessUrl, currentCampaign?.aboutPageUrl, currentCampaign?.productServiceUrl]);

  const performUrlAnalysis = async (campaign: Campaign, cacheKey: string) => {
    try {
      const urls = [
        campaign.businessUrl,
        campaign.aboutPageUrl,
        campaign.productServiceUrl
      ].filter(url => url && url.trim());

      if (urls.length === 0) {
        console.log('No URLs provided, using mock themes/tags');
        // Fallback to mock themes/tags if no URLs
        const mockData = mockGenerateThemesAndTags(campaign.businessDescription, campaign.objective);
        setSuggestedThemes(mockData.themes);
        setSuggestedTags(mockData.tags);
        return;
      }

      console.log('🔍 Performing URL analysis with API client...', urls);

      // Use the proper API client instead of direct fetch
      const analysisResult = await VideoVentureLaunchAPI.analyzeUrls({
        urls: urls,
        analysis_type: 'business_context'
      });
      
      console.log('✅ URL analysis successful:', analysisResult);
      
      // Extract themes and tags from analysis result
      let themes = analysisResult.suggested_themes || [];
      let tags = analysisResult.suggested_tags || [];
      
      // Fallback: extract from nested structure if top-level fields are empty
      if (themes.length === 0) {
        const nestedThemes = (analysisResult as any)?.business_analysis?.campaign_guidance?.content_themes?.primary_themes;
        if (nestedThemes && Array.isArray(nestedThemes)) {
          themes = nestedThemes;
          console.log('📝 Context: Extracted themes from nested structure:', themes);
        }
      }
      
      if (tags.length === 0) {
        // Generate tags from business analysis
        const businessAnalysis = (analysisResult as any)?.business_analysis;
        if (businessAnalysis) {
          const generatedTags: string[] = [];
          
          // Extract from value propositions
          if (businessAnalysis.value_propositions && Array.isArray(businessAnalysis.value_propositions)) {
            businessAnalysis.value_propositions.slice(0, 3).forEach((prop: string) => {
              const tag = prop.replace(/[^a-zA-Z0-9]/g, '').slice(0, 15);
              if (tag.length > 3) generatedTags.push(tag);
            });
          }
          
          // Extract from industry
          if (businessAnalysis.industry && typeof businessAnalysis.industry === 'string') {
            const industryWords = businessAnalysis.industry.split(/[\s(),]+/).filter((word: string) => word.length > 3);
            generatedTags.push(...industryWords.slice(0, 3));
          }
          
          if (generatedTags.length > 0) {
            tags = [...new Set(generatedTags)].slice(0, 8);
            console.log('🏷️ Context: Generated tags from business analysis:', tags);
          }
        }
      }
      
      if (themes.length > 0) {
        console.log('📝 Setting suggested themes:', themes);
        setSuggestedThemes(themes);
        // Auto-select first few themes
        setSelectedThemes(themes.slice(0, 3));
      } else {
        // Fallback to mock themes if none returned
        const mockData = mockGenerateThemesAndTags(campaign.businessDescription, campaign.objective);
        setSuggestedThemes(mockData.themes);
        setSelectedThemes(mockData.themes.slice(0, 3));
      }
      
      if (tags.length > 0) {
        console.log('🏷️ Setting suggested tags:', tags);
        setSuggestedTags(tags);
        // Auto-select first few tags
        setSelectedTags(tags.slice(0, 4));
      } else {
        // Fallback to mock tags if none returned
        const mockData = mockGenerateThemesAndTags(campaign.businessDescription, campaign.objective);
        setSuggestedTags(mockData.tags);
        setSelectedTags(mockData.tags.slice(0, 4));
      }

      // Store COMPLETE AI analysis results in campaign
      if (analysisResult.business_analysis) {
        const businessAnalysis = analysisResult.business_analysis;
        const newSummary = generateRealAISummary(campaign, businessAnalysis);
        setAiSummary(newSummary);
        
        // Store FULL AI analysis in campaign for later use
        updateCurrentCampaign({
          aiAnalysis: {
            summary: newSummary,
            businessAnalysis: businessAnalysis,
            campaignGuidance: businessAnalysis.campaign_guidance || {},
            lastUpdated: new Date().toISOString()
          }
        });
        
        console.log('✅ AI Analysis stored in campaign:', {
          summary: newSummary,
          company: businessAnalysis.company_name,
          industry: businessAnalysis.industry
        });
      }

      // Cache successful analysis
      const newCache = { ...urlAnalysisCache, [cacheKey]: true };
      setUrlAnalysisCache(newCache);
      localStorage.setItem('urlAnalysisCache', JSON.stringify(newCache));
      
    } catch (error) {
      console.error('❌ Auto URL analysis failed:', error);
      console.log('🔄 Falling back to mock data...');
      
      // Fallback to mock data on error
      const mockData = mockGenerateThemesAndTags(campaign.businessDescription, campaign.objective);
      setSuggestedThemes(mockData.themes);
      setSuggestedTags(mockData.tags);
      
      // Auto-select some themes and tags for better UX
      setSelectedThemes(mockData.themes.slice(0, 3));
      setSelectedTags(mockData.tags.slice(0, 4));
      
      // Set a basic AI summary
      setAiSummary(generateRealAISummary(campaign));
    }
  };

  const createNewCampaign = (campaignData: Omit<Campaign, 'id' | 'createdAt'>) => {
    const newCampaign: Campaign = {
      ...campaignData,
      id: `campaign-${Date.now()}`,
      createdAt: new Date().toISOString(),
      generatedIdeas: [],
      selectedThemes: [],
      selectedTags: []
    };
    
    setCampaigns([...campaigns, newCampaign]);
    setCurrentCampaignState(newCampaign);
  };

  const setCurrentCampaignState = (campaign: Campaign | null) => {
    setCurrentCampaign(campaign);
    setGeneratedIdeas(campaign?.generatedIdeas || []);
    setSelectedThemes(campaign?.selectedThemes || []);
    setSelectedTags(campaign?.selectedTags || []);
    
    if (campaign) {
      localStorage.setItem('currentCampaignId', campaign.id);
      
      // Restore themes and tags from campaign or localStorage cache
      const campaignKey = `campaign-${campaign.id}-analysis`;
      const cachedAnalysis = localStorage.getItem(campaignKey);
      
      if (cachedAnalysis) {
        const analysis = JSON.parse(cachedAnalysis);
        setSuggestedThemes(analysis.suggestedThemes || []);
        setSuggestedTags(analysis.suggestedTags || []);
        setAiSummary(analysis.aiSummary || '');
      } else if (campaign.aiAnalysis?.businessAnalysis) {
        // FIXED: Properly restore AI analysis data from stored campaign
        console.log('🔄 Restoring AI analysis from stored campaign data');
        const businessAnalysis = campaign.aiAnalysis.businessAnalysis;
        
        // Restore AI summary
        setAiSummary(campaign.aiAnalysis.summary || generateRealAISummary(campaign, businessAnalysis));
        
        // Extract and restore themes from campaign guidance
        const campaignGuidance = businessAnalysis.campaign_guidance || {};
        const contentThemes = campaignGuidance.content_themes || {};
        const primaryThemes = contentThemes.primary_themes || [];
        
        // Use stored selected themes or extract from AI analysis
        if (campaign.selectedThemes && campaign.selectedThemes.length > 0) {
          setSuggestedThemes(campaign.selectedThemes);
        } else if (primaryThemes.length > 0) {
          // Generate creative style themes based on business analysis
          const creativeThemes = generateCreativeThemes(businessAnalysis);
          setSuggestedThemes(creativeThemes);
        } else {
          // Fallback to mock themes
          const { themes } = mockGenerateThemesAndTags(campaign.businessDescription, campaign.objective);
          setSuggestedThemes(themes);
        }
        
        // Use stored selected tags or extract from AI analysis
        if (campaign.selectedTags && campaign.selectedTags.length > 0) {
          setSuggestedTags(campaign.selectedTags);
        } else {
          // Generate tags from business analysis
          const businessTags = generateBusinessTags(businessAnalysis);
          setSuggestedTags(businessTags);
        }
        
        console.log('✅ AI analysis data restored successfully');
      } else if (campaign.businessDescription) {
        // Generate real AI summary using campaign data
        setAiSummary(generateRealAISummary(campaign));
        const { themes, tags } = mockGenerateThemesAndTags(campaign.businessDescription, campaign.objective);
        setSuggestedThemes(themes);
        setSuggestedTags(tags);
        
        // Auto-select some themes and tags for better UX
        setSelectedThemes(themes.slice(0, 3));
        setSelectedTags(tags.slice(0, 4));
      } else {
        // Ensure we always have some themes and tags available
        const { themes, tags } = mockGenerateThemesAndTags('', '');
        setSuggestedThemes(themes);
        setSuggestedTags(tags);
      }
    } else {
      localStorage.removeItem('currentCampaignId');
    }
  };

  const updateCurrentCampaign = (updates: Partial<Campaign>) => {
    if (!currentCampaign) return;
    
    const updatedCampaign = {
      ...currentCampaign,
      ...updates
    };
    
    // Update the current campaign state
    setCurrentCampaign(updatedCampaign);
    
    // Update campaigns array without triggering circular dependency
    setCampaigns(prevCampaigns => 
      prevCampaigns.map(c => c.id === updatedCampaign.id ? updatedCampaign : c)
    );
    
    // Save to localStorage immediately for session persistence
    localStorage.setItem('currentCampaignId', updatedCampaign.id);
    
    // Save analysis data to prevent re-analysis
    if (suggestedThemes.length > 0 || suggestedTags.length > 0) {
      const campaignKey = `campaign-${updatedCampaign.id}-analysis`;
      const analysisData = {
        suggestedThemes,
        suggestedTags,
        aiSummary
      };
      localStorage.setItem(campaignKey, JSON.stringify(analysisData));
    }
  };

  const updateAiSummary = (summary: string) => {
    setAiSummary(summary);
  };

  const generateIdeas = async () => {
    if (!currentCampaign) return;
    
    // In a real-world scenario, this would be an API call to Gemini
    const ideas = mockGenerateIdeas(
      currentCampaign.businessDescription,
      currentCampaign.objective,
      selectedThemes,
      selectedTags
    );
    
    setGeneratedIdeas(ideas);
    updateCurrentCampaign({ generatedIdeas: ideas });
  };

  const selectTheme = (theme: string) => {
    if (!selectedThemes.includes(theme)) {
      const newSelectedThemes = [...selectedThemes, theme];
      setSelectedThemes(newSelectedThemes);
      updateCurrentCampaign({ selectedThemes: newSelectedThemes });
    }
  };

  const unselectTheme = (theme: string) => {
    const newSelectedThemes = selectedThemes.filter(t => t !== theme);
    setSelectedThemes(newSelectedThemes);
    updateCurrentCampaign({ selectedThemes: newSelectedThemes });
  };

  const selectTag = (tag: string) => {
    if (!selectedTags.includes(tag)) {
      const newSelectedTags = [...selectedTags, tag];
      setSelectedTags(newSelectedTags);
      updateCurrentCampaign({ selectedTags: newSelectedTags });
    }
  };

  const unselectTag = (tag: string) => {
    const newSelectedTags = selectedTags.filter(t => t !== tag);
    setSelectedTags(newSelectedTags);
    updateCurrentCampaign({ selectedTags: newSelectedTags });
  };

  const toggleIdeaSelection = (ideaId: string) => {
    const updatedIdeas = generatedIdeas.map(idea => {
      if (idea.id === ideaId) {
        return { ...idea, selected: !idea.selected };
      }
      return idea;
    });
    
    setGeneratedIdeas(updatedIdeas);
    setSelectedIdeas(updatedIdeas.filter(idea => idea.selected));
    updateCurrentCampaign({ generatedIdeas: updatedIdeas });
  };

  const generateVideos = async () => {
    // In a real implementation, this would call Gemini's Veo3 API
    const ideasWithVideos = mockGenerateVideos(selectedIdeas.length > 0 ? selectedIdeas : generatedIdeas.slice(0, 1));
    const updatedIdeas = generatedIdeas.map(idea => {
      const updatedIdea = ideasWithVideos.find(i => i.id === idea.id);
      return updatedIdea || idea;
    });
    setGeneratedIdeas(updatedIdeas);
    updateCurrentCampaign({ generatedIdeas: updatedIdeas });
  };

  const saveCampaign = async (campaignName: string): Promise<void> => {
    const campaignData = {
      businessDescription: currentCampaign?.businessDescription || '',
      objective: currentCampaign?.objective || '',
      targetAudience: '',
      campaignType: currentCampaign?.campaignType || 'product',
      creativityLevel: currentCampaign?.creativityLevel || 0,
      businessUrls: {},
      uploadedFiles: [],
      selectedThemes: currentCampaign?.selectedThemes || [],
      selectedTags: currentCampaign?.selectedTags || [],
      generatedColumns: currentCampaign?.socialMediaColumns || [],
      selectedPosts: currentCampaign?.selectedPosts?.map(p => p.id) || [],
      schedulingConfig: {} // Add scheduling config when available
    };

    const savedCampaign: SavedCampaign = {
      id: `campaign_${Date.now()}`,
      name: campaignName,
      createdAt: new Date(),
      lastModified: new Date(),
      campaignData
    };

    // Save to localStorage for now (in production, this would be an API call)
    const existingSavedCampaigns = JSON.parse(localStorage.getItem('savedCampaigns') || '[]');
    const updatedCampaigns = [...existingSavedCampaigns, savedCampaign];
    localStorage.setItem('savedCampaigns', JSON.stringify(updatedCampaigns));
  };

  const exportToText = () => {
    if (!currentCampaign) return;
    
    let text = `# Marketing Campaign: ${currentCampaign.name}\n\n`;
    text += `Created: ${new Date(currentCampaign.createdAt).toLocaleString()}\n`;
    text += `Objective: ${currentCampaign.objective}\n\n`;
    text += `Business Description:\n${currentCampaign.businessDescription}\n\n`;
    
    if (currentCampaign.generatedIdeas && currentCampaign.generatedIdeas.length > 0) {
      text += `## Generated Marketing Ideas\n\n`;
      currentCampaign.generatedIdeas.forEach((idea, index) => {
        text += `### Idea ${index + 1}: ${idea.title}\n`;
        text += `${idea.description}\n\n`;
        
        if (idea.platforms) {
          text += `#### Social Media Content\n`;
          if (idea.platforms.linkedin) {
            text += `LinkedIn: ${idea.platforms.linkedin}\n`;
          }
          if (idea.platforms.twitter) {
            text += `Twitter: ${idea.platforms.twitter}\n`;
          }
          if (idea.platforms.instagram) {
            text += `Instagram: ${idea.platforms.instagram}\n`;
          }
          text += `\n`;
        }
        
        text += `Tags: ${idea.tags.join(', ')}\n`;
        text += `Themes: ${idea.themes.join(', ')}\n\n`;
      });
    }
    
    const blob = new Blob([text], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    
    const link = document.createElement('a');
    link.download = `${currentCampaign.name.replace(/\s+/g, '-').toLowerCase()}-marketing-campaign.txt`;
    link.href = url;
    link.click();
  };

  const loadCampaign = async (campaignId: string): Promise<void> => {
    const savedCampaigns = JSON.parse(localStorage.getItem('savedCampaigns') || '[]');
    const campaign = savedCampaigns.find((c: SavedCampaign) => c.id === campaignId);
    
         if (campaign) {
       const { campaignData } = campaign;
       const loadedCampaign: Campaign = {
         id: campaign.id,
         name: campaign.name,
         createdAt: campaign.createdAt,
         businessDescription: campaignData.businessDescription,
         objective: campaignData.objective,
         campaignType: campaignData.campaignType,
         creativityLevel: campaignData.creativityLevel,
         selectedThemes: campaignData.selectedThemes,
         selectedTags: campaignData.selectedTags,
         socialMediaColumns: campaignData.generatedColumns,
         selectedPosts: []
       };
       setCurrentCampaignState(loadedCampaign);
     }
  };

  const getSavedCampaigns = (): SavedCampaign[] => {
    return JSON.parse(localStorage.getItem('savedCampaigns') || '[]');
  };

  const deleteSavedCampaign = (campaignId: string): void => {
    try {
      // Delete from savedCampaigns (localStorage)
      const savedCampaigns = JSON.parse(localStorage.getItem('savedCampaigns') || '[]');
      const updatedSavedCampaigns = savedCampaigns.filter((c: SavedCampaign) => c.id !== campaignId);
      localStorage.setItem('savedCampaigns', JSON.stringify(updatedSavedCampaigns));
      
      // Also delete from campaigns array (context state)
      setCampaigns(prevCampaigns => prevCampaigns.filter(c => c.id !== campaignId));
      
      // If the deleted campaign is currently active, clear it
      if (currentCampaign?.id === campaignId) {
        setCurrentCampaign(null);
        localStorage.removeItem('currentCampaignId');
        // Clear campaign-specific localStorage data
        localStorage.removeItem(`campaign-${campaignId}-columns`);
        localStorage.removeItem(`campaign-${campaignId}-analysis`);
        
        // Reset all campaign-related state
        setGeneratedIdeas([]);
        setAiSummary('');
        setSuggestedThemes([]);
        setSuggestedTags([]);
        setSelectedThemes([]);
        setSelectedTags([]);
        setSelectedIdeas([]);
      }
      
      console.log(`Campaign ${campaignId} deleted successfully`);
    } catch (error) {
      console.error('Error deleting campaign:', error);
    }
  };

  const value: MarketingContextType = {
    campaigns,
    currentCampaign,
    generatedIdeas,
    aiSummary,
    suggestedThemes,
    suggestedTags,
    selectedThemes,
    selectedTags,
    selectedIdeas,
    createNewCampaign,
    setCurrentCampaign: loadCampaign,
    updateCurrentCampaign,
    updateAiSummary,
    generateIdeas,
    selectTheme,
    unselectTheme,
    selectTag,
    unselectTag,
    generateVideos,
    toggleIdeaSelection,
    saveCampaign,
    exportToText,
    loadCampaign,
    getSavedCampaigns,
    deleteSavedCampaign,
  };

  return (
    <MarketingContext.Provider value={value}>
      {children}
    </MarketingContext.Provider>
  );
};

export const useMarketingContext = () => {
  const context = useContext(MarketingContext);
  if (context === undefined) {
    throw new Error('useMarketingContext must be used within a MarketingProvider');
  }
  return context;
};

/**
 * API Client Configuration
 * 
 * Author: JP + 2025-06-18
 * 
 * Centralized API client for AI Marketing Campaign Post Generator frontend-backend communication.
 * Handles HTTP requests, error handling, and response formatting with comprehensive DEBUG logging.
 */

import axios, { AxiosInstance, AxiosResponse, AxiosError } from 'axios';
import { logApiRequest, logApiResponse, logApiError, debug, info, warn, error } from '@/utils/logger';

// API Configuration - Environment-based URL resolution
const getApiBaseUrl = (): string => {
  // Production/Cloud deployment - use environment variable
  if (import.meta.env.VITE_API_BASE_URL) {
    return import.meta.env.VITE_API_BASE_URL;
  }
  
  // Development environment - use relative URLs to work with Vite proxy
  const isDevelopment = import.meta.env.DEV;
  
  if (isDevelopment) {
    // Use relative URL in development to work with Vite proxy
    return '';
  }
  
  // Production fallback - same origin API
  return '/api';
};

const API_BASE_URL = getApiBaseUrl();

// Log configuration for debugging
debug(`🔗 API Base URL: ${API_BASE_URL}`, undefined, 'API');
debug(`🌍 Environment: ${import.meta.env.MODE}`, undefined, 'API');
info('🚀 API Client initialized', { baseURL: API_BASE_URL, timeout: 45000 }, 'API');

// Create axios instance with default configuration
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120000, // 120 seconds timeout for AI operations (video generation can be slow)
  headers: {
    'Content-Type': 'application/json',
  },
});

// Track request timing
const requestTimings = new Map<string, number>();

// Request interceptor for adding auth tokens and logging
apiClient.interceptors.request.use(
  (config) => {
    // Log API request and track timing
    const requestKey = `${config.method?.toUpperCase()}_${config.url}_${Date.now()}`;
    requestTimings.set(requestKey, Date.now());
    
    logApiRequest(
      config.method?.toUpperCase() || 'UNKNOWN', 
      config.url || 'unknown', 
      config.data
    );
    
    // Store request key for response timing
    config.headers['X-Request-ID'] = requestKey;
    
    // Add auth token when available
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
      debug('🔐 Auth token added to request', undefined, 'API');
    }

    const geminiKey = localStorage.getItem('gemini_api_key');
    if (geminiKey) {
      config.headers['X-Gemini-Key'] = JSON.parse(geminiKey);
    }
    
    return config;
  },
  (error) => {
    error('💥 Request interceptor error', error, 'API');
    return Promise.reject(error);
  }
);

// Response interceptor for error handling and logging
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    // Calculate request duration
    const requestKey = response.config.headers['X-Request-ID'] as string;
    const startTime = requestTimings.get(requestKey);
    const duration = startTime ? Date.now() - startTime : undefined;
    
    // Clean up timing map
    if (requestKey) {
      requestTimings.delete(requestKey);
    }
    
    // Log successful response
    logApiResponse(
      response.config.method?.toUpperCase() || 'UNKNOWN',
      response.config.url || 'unknown',
      response.status,
      response.data,
      duration
    );
    
    return response;
  },
  (axiosError: AxiosError) => {
    // Calculate request duration for failed requests
    const requestKey = axiosError.config?.headers?.['X-Request-ID'] as string;
    const startTime = requestKey ? requestTimings.get(requestKey) : undefined;
    const duration = startTime ? Date.now() - startTime : undefined;
    
    // Clean up timing map
    if (requestKey) {
      requestTimings.delete(requestKey);
    }
    
    // Log API error
    logApiError(
      axiosError.config?.method?.toUpperCase() || 'UNKNOWN',
      axiosError.config?.url || 'unknown',
      axiosError
    );
    
    // Handle common error scenarios
    if (axiosError.response?.status === 401) {
      // Unauthorized - clear auth and redirect to login (future)
      localStorage.removeItem('auth_token');
      warn('🔐 Unauthorized - clearing auth token', undefined, 'API');
    } else if (axiosError.response?.status === 429) {
      // Rate limited
      warn('⏰ API rate limit exceeded', { retryAfter: axiosError.response.headers['retry-after'] }, 'API');
    } else if (axiosError.code === 'ECONNABORTED') {
      // Timeout
      error('⏱️ API request timeout', { timeout: '45s', duration }, 'API');
    }
    
    return Promise.reject(axiosError);
  }
);

// Type definitions for API responses
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
}

export interface Campaign {
  id: string;
  name: string;
  objective: string;
  business_description: string;
  example_content?: string;
  business_url?: string;
  about_page_url?: string;
  product_service_url?: string;
  campaign_type: 'product' | 'service' | 'brand' | 'event';
  creativity_level: number;
  created_at: string;
  updated_at: string;
  status: 'draft' | 'analyzing' | 'ready' | 'published';
}

export interface CreateCampaignRequest {
  name: string;
  objective: string;
  businessDescription: string;
  exampleContent?: string;
  businessUrl?: string;
  aboutPageUrl?: string;
  productServiceUrl?: string;
  campaignType: 'product' | 'service' | 'brand' | 'event';
  creativityLevel: number;
  uploadedImages?: File[];
  uploadedDocuments?: File[];
  campaignAssets?: File[];
}

export interface ContentGenerationRequest {
  campaign_id: string;
  content_type: 'social_media' | 'blog' | 'email' | 'ad_copy';
  platform?: 'facebook' | 'instagram' | 'twitter' | 'linkedin' | 'tiktok';
  tone?: 'professional' | 'casual' | 'humorous' | 'inspirational';
  include_hashtags?: boolean;
  max_posts?: number;
}

export interface ContentGenerationResponse {
  campaign_id: string;
  content_type: string;
  platform?: string;
  posts: Array<{
    id: string;
    content: string;
    hashtags?: string[];
    platform_specific?: any;
  }>;
  total_posts: number;
  generation_metadata: {
    creativity_level: number;
    tone: string;
    generated_at: string;
  };
}

export interface UrlAnalysisRequest {
  urls: string[];
  analysis_type?: 'business_context' | 'competitor_analysis' | 'content_analysis';
}

export interface UrlAnalysisResponse {
  analysis_results: {
    business_context?: {
      industry: string;
      target_audience: string;
      key_products: string[];
      brand_voice: string;
      competitive_advantages: string[];
    };
    content_insights?: {
      main_topics: string[];
      content_style: string;
      key_messages: string[];
    };
    technical_details?: {
      site_structure: string[];
      performance_notes: string[];
    };
  };
  analysis_metadata: {
    urls_analyzed: string[];
    analysis_type: string;
    analyzed_at: string;
  };
  extracted_insights: string[];
  suggested_themes?: string[];
  suggested_tags?: string[];
  business_analysis?: {
    company_name?: string;
    business_description?: string;
    industry?: string;
    target_audience?: string;
    campaign_guidance?: {
      suggested_themes?: string[];
      suggested_tags?: string[];
      creative_direction?: string;
      visual_style?: any;
    };
  };
  processing_time: number;
}

export interface FileAnalysisRequest {
  analysis_type?: 'document_analysis' | 'image_analysis' | 'mixed_analysis';
}

export interface FileAnalysisResponse {
  analysis_results: {
    document_insights?: {
      key_topics: string[];
      content_summary: string;
      extracted_text: string;
    };
    image_insights?: {
      visual_elements: string[];
      brand_colors: string[];
      style_analysis: string;
    };
  };
  analysis_metadata: {
    files_analyzed: string[];
    analysis_type: string;
    analyzed_at: string;
  };
  extracted_insights: string[];
}

// API Client Class
export class VideoVentureLaunchAPI {
  
  // Campaign Management
  static async createCampaign(campaignData: CreateCampaignRequest): Promise<Campaign> {
    try {
      const formData = new FormData();
      
      // Append all the campaign data
      formData.append('name', campaignData.name);
      formData.append('objective', campaignData.objective);
      formData.append('businessDescription', campaignData.businessDescription);
      formData.append('campaignType', campaignData.campaignType);
      formData.append('creativityLevel', campaignData.creativityLevel.toString());
      
      if (campaignData.exampleContent) formData.append('exampleContent', campaignData.exampleContent);
      if (campaignData.businessUrl) formData.append('businessUrl', campaignData.businessUrl);
      if (campaignData.aboutPageUrl) formData.append('aboutPageUrl', campaignData.aboutPageUrl);
      if (campaignData.productServiceUrl) formData.append('productServiceUrl', campaignData.productServiceUrl);

      // Append files if they exist
      campaignData.uploadedImages?.forEach(file => formData.append('uploadedImages', file));
      campaignData.uploadedDocuments?.forEach(file => formData.append('uploadedDocuments', file));
      campaignData.campaignAssets?.forEach(file => formData.append('campaignAssets', file));

      const response = await apiClient.post<ApiResponse<Campaign>>('/api/v1/campaigns', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      
      if (!response.data.success || !response.data.data) {
        throw new Error(response.data.error || 'Failed to create campaign');
      }
      
      return response.data.data;
    } catch (err) {
      console.error('Create campaign error:', err);
      throw this.handleApiError(err);
    }
  }

  static async getCampaigns(page: number = 1, limit: number = 10): Promise<{ campaigns: Campaign[], total: number }> {
    try {
      const response = await apiClient.get<ApiResponse<{ campaigns: Campaign[], total: number }>>(`/api/v1/campaigns?page=${page}&limit=${limit}`);
      
      if (!response.data.success || !response.data.data) {
        throw new Error(response.data.error || 'Failed to fetch campaigns');
      }
      
      return response.data.data;
    } catch (err) {
      console.error('Get campaigns error:', err);
      throw this.handleApiError(err);
    }
  }

  static async getCampaign(campaignId: string): Promise<Campaign> {
    try {
      const response = await apiClient.get<ApiResponse<Campaign>>(`/api/v1/campaigns/${campaignId}`);
      
      if (!response.data.success || !response.data.data) {
        throw new Error(response.data.error || 'Failed to fetch campaign');
      }
      
      return response.data.data;
    } catch (err) {
      console.error('Get campaign error:', err);
      throw this.handleApiError(err);
    }
  }

  static async updateCampaign(campaignId: string, updates: Partial<CreateCampaignRequest>): Promise<Campaign> {
    try {
      const response = await apiClient.put<ApiResponse<Campaign>>(`/api/v1/campaigns/${campaignId}`, updates);
      
      if (!response.data.success || !response.data.data) {
        throw new Error(response.data.error || 'Failed to update campaign');
      }
      
      return response.data.data;
    } catch (err) {
      console.error('Update campaign error:', err);
      throw this.handleApiError(err);
    }
  }

  static async deleteCampaign(campaignId: string): Promise<void> {
    try {
      const response = await apiClient.delete<ApiResponse>(`/api/v1/campaigns/${campaignId}`);
      
      if (!response.data.success) {
        throw new Error(response.data.error || 'Failed to delete campaign');
      }
    } catch (err) {
      console.error('Delete campaign error:', err);
      throw this.handleApiError(err);
    }
  }

  // Content Generation
  static async generateContent(request: ContentGenerationRequest): Promise<ContentGenerationResponse> {
    try {
      const response = await apiClient.post<ApiResponse<ContentGenerationResponse>>('/api/v1/content/generate', request);
      
      if (!response.data.success || !response.data.data) {
        throw new Error(response.data.error || 'Failed to generate content');
      }
      
      return response.data.data;
    } catch (err) {
      console.error('Generate content error:', err);
      throw this.handleApiError(err);
    }
  }

  static async regenerateContent(campaignId: string, postId: string): Promise<ContentGenerationResponse> {
    try {
      const response = await apiClient.post<ApiResponse<ContentGenerationResponse>>('/api/v1/content/regenerate', {
        campaign_id: campaignId,
        post_id: postId
      });
      
      if (!response.data.success || !response.data.data) {
        throw new Error(response.data.error || 'Failed to regenerate content');
      }
      
      return response.data.data;
    } catch (err) {
      console.error('Regenerate content error:', err);
      throw this.handleApiError(err);
    }
  }

  // Bulk content generation for specific post types (used by IdeationPage)
  static async generateBulkContent(request: {
    post_type: 'text_url' | 'text_image' | 'text_video';
    regenerate_count: number;
    business_context: {
      company_name: string;
      objective: string;
      campaign_type: string;
      target_audience?: string;
      business_description?: string;
      business_website?: string;
      product_service_url?: string;
      campaign_media_tuning?: string;
      campaign_guidance?: any;
      product_context?: any;
    };
    creativity_level: number;
  }): Promise<{
    new_posts: Array<{
      id: string;
      type: string;
      content: string;
      url?: string;
      image_prompt?: string;
      image_url?: string;
      video_prompt?: string;
      video_url?: string;
      hashtags: string[];
      platform_optimized: any;
      engagement_score: number;
      selected: boolean;
    }>;
    regeneration_metadata: any;
    processing_time: number;
  }> {
    try {
      debug('🎯 Generating bulk content', request, 'API');
      
      const response = await apiClient.post('/api/v1/content/generate-bulk', request);
      
      info('✅ Bulk content generated successfully', { 
        postCount: response.data.new_posts?.length || 0,
        postType: request.post_type 
      }, 'API');
      
      return response.data;
    } catch (err) {
      console.error('❌ Bulk content generation failed', err);
      throw this.handleApiError(err);
    }
  }

  // Visual Content Generation
  static async generateVisualContent(request: {
    social_posts: Array<{
      id: string | number;
      type: 'text_image' | 'text_video' | 'text_url';
      content: string;
      platform: string;
      hashtags?: string[];
    }>;
    business_context: {
      business_name?: string;
      industry?: string;
      objective?: string;
      target_audience?: string;
      brand_voice?: string;
      company_name?: string;
      business_description?: string;
    };
    campaign_objective: string;
    target_platforms?: string[];
    // ENHANCED: Campaign guidance context for ADK agentic visual generation
    campaign_guidance?: {
      suggested_themes?: string[];
      suggested_tags?: string[];
      creative_direction?: string;
      visual_style?: any;
      brand_voice?: string;
      target_audience?: string;
    };
    campaign_media_tuning?: string;
    product_context?: any;
    visual_style?: any;
    creative_direction?: string;
    campaign_id?: string;
  }): Promise<{
    posts_with_visuals: Array<{
      id: string | number;
      type: string;
      content: string;
      platform: string;
      hashtags?: string[];
      image_prompt?: string;
      image_url?: string;
      video_prompt?: string;
      video_url?: string;
    }>;
    visual_strategy: any;
    generation_metadata: any;
  }> {
    try {
      debug('🎨 Generating visual content', request, 'API');
      
      const response = await apiClient.post('/api/v1/content/generate-visuals', request);
      
      info('✅ Visual content generated successfully', { 
        postsCount: response.data.posts_with_visuals?.length || 0 
      }, 'API');
      
      return response.data;
    } catch (err) {
      console.error('❌ Visual content generation failed', err);
      throw this.handleApiError(err);
    }
  }

  // URL Analysis
  static async analyzeUrls(request: UrlAnalysisRequest): Promise<UrlAnalysisResponse> {
    try {
      info('🔍 Starting URL analysis', { urls: request.urls, analysisType: request.analysis_type }, 'API');
      
      const response = await apiClient.post('/api/v1/analysis/url', request);
      
      // Backend returns URLAnalysisResponse directly, not wrapped in ApiResponse
      if (!response.data) {
        throw new Error('No response data received from backend');
      }
      
      info('✅ URL analysis completed successfully', { 
        businessAnalysis: !!response.data.business_analysis,
        themes: response.data.suggested_themes?.length || 0,
        tags: response.data.suggested_tags?.length || 0,
        processingTime: response.data.processing_time 
      }, 'API');
      
      return response.data;
    } catch (err) {
      console.error('❌ Analyze URLs error', err);
      throw this.handleApiError(err);
    }
  }

  // File Analysis
  static async analyzeFiles(files: File[], request?: FileAnalysisRequest): Promise<FileAnalysisResponse> {
    try {
      const formData = new FormData();
      files.forEach((file, index) => {
        formData.append(`files`, file);
      });
      
      if (request?.analysis_type) {
        formData.append('analysis_type', request.analysis_type);
      }

      const response = await apiClient.post<ApiResponse<FileAnalysisResponse>>('/api/v1/analysis/files', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      
      if (!response.data.success || !response.data.data) {
        throw new Error(response.data.error || 'Failed to analyze files');
      }
      
      return response.data.data;
    } catch (err) {
      console.error('Analyze files error:', err);
      throw this.handleApiError(err);
    }
  }

  static async setGeminiKey(key: string): Promise<void> {
    await apiClient.post('/api/v1/config/gemini-key', { gemini_api_key: key });
  }

  // Error handling helper
  private static handleApiError(error: any): Error {
    if (axios.isAxiosError(error)) {
      const axiosError = error as AxiosError<ApiResponse>;
      
      if (axiosError.response?.data?.error) {
        return new Error(axiosError.response.data.error);
      } else if (axiosError.response?.data?.message) {
        return new Error(axiosError.response.data.message);
      } else if (axiosError.message) {
        return new Error(`API Error: ${axiosError.message}`);
      }
    }
    
    return error instanceof Error ? error : new Error('Unknown API error');
  }
}

// Export default instance for convenience
export default VideoVentureLaunchAPI; 
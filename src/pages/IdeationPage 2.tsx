/**
 * FILENAME: IdeationPage.tsx
 * DESCRIPTION/PURPOSE: Social media post ideation and generation page with VVL design system styling
 * Author: JP + 2025-06-15
 */

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMarketingContext } from '@/contexts/MarketingContext';
import { MaterialVideoCard } from '@/components/MaterialVideoCard';
import { EditableCampaignGuidance } from '@/components/EditableCampaignGuidance';
import { CampaignGuidanceChat } from '@/components/CampaignGuidanceChat';
import { Textarea } from '@/components/ui/textarea';
import { ArrowLeft, ArrowRight, Sparkles, RefreshCw, Heart, MessageCircle, Share, ExternalLink, Image, Video, Hash, Calendar, Home, Wand2, Info, AlertTriangle, Palette, Edit, X } from 'lucide-react';
import { toast } from 'sonner';
import VideoVentureLaunchAPI from '../lib/api';
import { safeStorage } from '@/utils/safeStorage';
import { useAbortableApi } from '@/hooks/useAbortableApi';

// CRITICAL FIX: Add TypeScript interfaces for better type safety
interface SocialMediaColumn {
  id: string;
  title: string;
  description: string;
  mediaType: 'text-only' | 'text-with-image' | 'text-with-video';
  posts: Array<{
    id: string;
    type: 'text-only' | 'text-with-image' | 'text-with-video';
    platform: 'linkedin';
    content: {
      text: string;
      hashtags: string[];
      imageUrl?: string;
      videoUrl?: string;
      productUrl?: string;
    };
    generationPrompt: string;
    selected: boolean;
    engagement_score: number;
    platform_optimized: any;
  }>;
  isGenerating: boolean;
}

const IdeationPage: React.FC = () => {
  const navigate = useNavigate();
  const {
    currentCampaign,
    aiSummary,
    suggestedThemes,
    suggestedTags,
    selectedThemes,
    selectedTags,
    selectTheme,
    unselectTheme,
    selectTag,
    unselectTag,
    updateCurrentCampaign,
    updateAiSummary,
    generateIdeas
  } = useMarketingContext();
  
  const [preferredDesign, setPreferredDesign] = useState(currentCampaign?.preferredDesign || '');
  const [isLoading, setIsLoading] = useState(false);
  const [selectedPosts, setSelectedPosts] = useState<string[]>([]);
  const [suggestedHashtags, setSuggestedHashtags] = useState<string[]>([
    '#marketing', '#business', '#growth', '#innovation', '#success', '#entrepreneur'
  ]);
  const [isRegeneratingAnalysis, setIsRegeneratingAnalysis] = useState(false);
  
  // Campaign Guidance Chat State
  const [showGuidanceChat, setShowGuidanceChat] = useState(false);
  const [showGuidanceEdit, setShowGuidanceEdit] = useState(false);
  
  // Use the new abortable API hook
  const { executeAbortableCall, hasActiveRequest, abortCurrentRequest } = useAbortableApi();
  
  // CRITICAL FIX 1.1: Use useRef to track generation states and prevent race conditions
  const generationStateRef = useRef<Record<string, boolean>>({});
  
  // Mock social media columns data with proper TypeScript interface - REMOVED isGeneratingVisuals
  const [socialMediaColumns, setSocialMediaColumns] = useState<SocialMediaColumn[]>([
    {
      id: 'text-only',
      title: 'Text + URL Posts',
      description: 'Marketing text with product URL for link unfurling',
      mediaType: 'text-only',
      posts: [],
      isGenerating: false
    },
    {
      id: 'text-image',
      title: 'Text + Image Posts',
      description: 'Shortened text with AI-generated images',
      mediaType: 'text-with-image',
      posts: [],
      isGenerating: false
    },
    {
      id: 'text-video',
      title: 'Text + Video Posts',
      description: 'Marketing text with AI-generated videos',
      mediaType: 'text-with-video',
      posts: [],
      isGenerating: false
    }
  ]);
  
  // CRITICAL FIX: Clear any stuck generation states on component mount
  const clearStuckStates = useCallback(() => {
    console.log('🔧 Clearing any stuck generation states...');
    generationStateRef.current = {};
    setSocialMediaColumns(prev => prev.map(col => ({
      ...col,
      isGenerating: false
    })));
  }, []);
  
  // CRITICAL FIX 1.3: Cleanup function using the new hook
  useEffect(() => {
    console.log('🔧 Component mounted - clearing any stuck states');
    clearStuckStates();
  }, [clearStuckStates]);
  
  // CRITICAL FIX 1.4: Safe localStorage operations using new utility
  const saveColumnsToStorage = useCallback((columns: SocialMediaColumn[]) => {
    if (!currentCampaign?.id) {
      console.warn('⚠️ No current campaign ID - skipping localStorage save');
      return;
    }
    
    console.log(`💾 Saving columns for campaign: ${currentCampaign.id} (${currentCampaign.name})`);
    
    // Create minimal serializable snapshot to avoid size limits
    const minimalColumns = columns.map(col => ({
      id: col.id,
      title: col.title,
      description: col.description,
      mediaType: col.mediaType,
      posts: col.posts.map(post => ({
        id: post.id,
        type: post.type,
        content: {
          text: post.content.text,
          hashtags: post.content.hashtags,
          // Only store URLs, not full image/video data
          imageUrl: post.content.imageUrl,
          videoUrl: post.content.videoUrl,
          productUrl: post.content.productUrl
        },
        selected: post.selected,
        engagement_score: post.engagement_score
      })),
      isGenerating: false // Always reset loading states in storage
    }));
    
    const campaignColumnsKey = `campaign-${currentCampaign.id}-columns`;
    const success = safeStorage.set(campaignColumnsKey, minimalColumns);
    
    if (success) {
      console.log(`💾 Saved ${minimalColumns.length} columns to localStorage`);
    } else {
      console.warn('⚠️ Failed to save columns to localStorage - data too large or storage unavailable');
    }
  }, [currentCampaign?.id]);
  
  const loadColumnsFromStorage = useCallback((): SocialMediaColumn[] | null => {
    if (!currentCampaign?.id) {
      console.warn('⚠️ No current campaign ID - cannot load from localStorage');
      return null;
    }
    
    console.log(`📦 Loading columns for campaign: ${currentCampaign.id} (${currentCampaign.name})`);
    
    const campaignColumnsKey = `campaign-${currentCampaign.id}-columns`;
    const result = safeStorage.getWithResult<any[]>(campaignColumnsKey, []);
    
    if (!result.success || !result.data || result.data.length === 0) {
      return null;
    }
    
    // Transform back to full structure with safety checks
    const fullColumns: SocialMediaColumn[] = result.data.map((col: any) => ({
      id: col.id || '',
      title: col.title || '',
      description: col.description || '',
      mediaType: col.mediaType || 'text-only',
      posts: (col.posts || []).map((post: any) => ({
        id: post.id || '',
        type: post.type || 'text-only',
        platform: 'linkedin' as const,
        content: {
          text: post.content?.text || '',
          hashtags: Array.isArray(post.content?.hashtags) ? post.content.hashtags : [],
          imageUrl: post.content?.imageUrl,
          videoUrl: post.content?.videoUrl,
          productUrl: post.content?.productUrl
        },
        generationPrompt: `Generated content for ${col.id}`,
        selected: Boolean(post.selected),
        engagement_score: Number(post.engagement_score) || 7.0,
        platform_optimized: {}
      })),
      isGenerating: false // Always reset loading states
    }));
    
    console.log(`📦 Loaded ${fullColumns.length} columns from localStorage`);
    return fullColumns;
  }, [currentCampaign?.id]);

  const generateAllPosts = useCallback(async () => {
    if (selectedThemes.length === 0 || selectedTags.length === 0) {
      // Use default selections for quick start
      if (suggestedThemes.length > 0) selectTheme(suggestedThemes[0]);
      if (suggestedTags.length > 0) selectTag(suggestedTags[0]);
    }
    
    // CRITICAL: Only auto-generate Text+URL posts on page load (basic tier)
    // Enhanced and Premium content (images/videos) requires MANUAL user action
    // This prevents automatic visual content generation and associated costs
    console.log('🎯 Auto-generating only Text+URL posts on page load (cost control)');
    await generateColumnPosts('text-only');
    
    // CRITICAL: Ensure visual columns are NOT automatically processing
    setSocialMediaColumns(prev => prev.map(col => ({
      ...col,
      isGenerating: col.id === 'text-only' ? col.isGenerating : false
    })));
  }, [selectedThemes, selectedTags, suggestedThemes, suggestedTags, selectTheme, selectTag]);

  // MAJOR FIX: Combined text + visual generation in one function
  const generateColumnPosts = useCallback(async (columnId: string) => {
    // CRITICAL FIX: Prevent duplicate generation attempts
    if (generationStateRef.current[columnId]) {
      console.log(`⚠️ Generation already in progress for ${columnId}, skipping duplicate request`);
      return;
    }
    
    // Set generation state immediately
    generationStateRef.current[columnId] = true;
    
    // Update UI to show loading state and clear old posts for fresh generation
    setSocialMediaColumns(prev => prev.map(col => 
      col.id === columnId ? { 
        ...col, 
        isGenerating: true,
        posts: [] // Clear old posts to show fresh loading state
      } : col
    ));
    
    try {
      console.log(`🎯 Generating ${columnId} posts...`);
      
      // STEP 1: Generate text content first
      const postType = columnId === 'text-only' ? 'text_url' : 
                      columnId === 'text-image' ? 'text_image' : 'text_video';
      const mediaType = columnId === 'text-only' ? 'text-only' as const : 
                       columnId === 'text-image' ? 'text-with-image' as const : 
                       'text-with-video' as const;
      
      const textContentData = await VideoVentureLaunchAPI.generateBulkContent({
        post_type: postType,
        regenerate_count: 4,
        business_context: {
          company_name: currentCampaign?.aiAnalysis?.businessAnalysis?.company_name || currentCampaign?.name || 'Your Company',
          objective: currentCampaign?.objective || 'increase sales',
          campaign_type: currentCampaign?.campaignType || 'product',
          target_audience: currentCampaign?.aiAnalysis?.businessAnalysis?.target_audience || 'business professionals',
          business_description: currentCampaign?.businessDescription || currentCampaign?.aiAnalysis?.businessAnalysis?.business_description || 'Professional business',
          business_website: currentCampaign?.businessUrl,
          product_service_url: currentCampaign?.productServiceUrl,
          campaign_media_tuning: preferredDesign,
          campaign_guidance: currentCampaign?.aiAnalysis?.businessAnalysis?.campaign_guidance,
          product_context: currentCampaign?.aiAnalysis?.businessAnalysis?.product_context
        },
        creativity_level: currentCampaign?.creativityLevel || 7
      });
      
      // Transform posts to frontend format
      let transformedPosts = textContentData.new_posts.map((post: any, idx: number) => ({
        id: post.id || `${columnId}-post-${Date.now()}-${idx}`,
        type: mediaType, // Use captured mediaType to avoid stale closure
        platform: 'linkedin' as const,
        content: {
          text: post.content || `Generated ${postType.replace('_', ' + ')} content`,
          hashtags: post.hashtags || suggestedHashtags.slice(0, 3),
          // CRITICAL FIX: Initialize visual URLs as undefined - they'll be set by visual generation API
          imageUrl: undefined, // Will be set by visual generation API
          videoUrl: undefined, // Will be set by visual generation API
          // MARKETING FIX: ALL post types should include product URL for effective marketing
          productUrl: post.url || currentCampaign?.productServiceUrl || currentCampaign?.businessUrl
        },
        generationPrompt: `Generate ${columnId} post for ${currentCampaign?.campaignType} campaign about ${currentCampaign?.objective}`,
        selected: false,
        engagement_score: post.engagement_score || (7.0 + idx * 0.1),
        platform_optimized: post.platform_optimized || {}
      }));
      
      // STEP 2: Generate visual content (images/videos) if needed
      if ((columnId === 'text-image' || columnId === 'text-video') && 
          transformedPosts.length > 0 && 
          !transformedPosts.some(post => post.content.imageUrl || post.content.videoUrl)) {
        console.log(`🎨 Generating visual content for ${columnId} posts...`);
        
        // Update loading state to show visual generation in progress
        // CRITICAL FIX: Show posts but keep loading state active during visual generation
        setSocialMediaColumns(prev => prev.map(col => 
          col.id === columnId ? { 
            ...col, 
            posts: transformedPosts, 
            isGenerating: true // MUST keep generating state for visual content
          } : col
        ));
        
        const visualResponse = await VideoVentureLaunchAPI.generateVisualContent({
          social_posts: transformedPosts.map(post => ({
            id: post.id,
            content: post.content.text,
            type: columnId === 'text-image' ? 'text_image' : 'text_video',
            platform: post.platform || 'linkedin',
            hashtags: post.content.hashtags
          })),
          business_context: {
            // Use comprehensive business context from AI analysis
            business_name: currentCampaign?.aiAnalysis?.businessAnalysis?.company_name || currentCampaign?.name || 'Your Company',
            industry: currentCampaign?.aiAnalysis?.businessAnalysis?.industry || 'Professional Services',
            objective: currentCampaign?.objective || 'increase sales',
            target_audience: currentCampaign?.aiAnalysis?.businessAnalysis?.target_audience || 'business professionals',
            brand_voice: currentCampaign?.aiAnalysis?.businessAnalysis?.brand_voice || 'Professional'
          },
          campaign_objective: currentCampaign?.objective || 'increase sales',
          target_platforms: ['instagram', 'linkedin', 'facebook', 'twitter'],
          // CRITICAL FIX: Include campaign creative guidance for visual generation
          campaign_media_tuning: preferredDesign || '',
          campaign_guidance: currentCampaign?.aiAnalysis?.businessAnalysis?.campaign_guidance || {},
          visual_style: currentCampaign?.aiAnalysis?.businessAnalysis?.campaign_guidance?.visual_style || {},
          creative_direction: currentCampaign?.aiAnalysis?.businessAnalysis?.campaign_guidance?.creative_direction || '',
          product_context: currentCampaign?.aiAnalysis?.businessAnalysis?.product_context || {},
          campaign_id: currentCampaign?.id || 'default'
        });
        
        console.log(`🎨 Visual generation response:`, {
          postsCount: visualResponse.posts_with_visuals?.length || 0,
          hasVisualStrategy: !!visualResponse.visual_strategy,
          hasGenerationMetadata: !!visualResponse.generation_metadata
        });
        
        if (visualResponse.posts_with_visuals && visualResponse.posts_with_visuals.length > 0) {
          const visualData = visualResponse;
          
          transformedPosts = transformedPosts.map(post => {
            const visualPost = visualData.posts_with_visuals.find((vp: any) => vp.id === post.id);
            if (visualPost) {
              console.log(`🔗 Mapping visual content for post ${post.id}:`, {
                hasBackendImageUrl: !!visualPost.image_url,
                backendImageLength: visualPost.image_url?.length || 0,
                hasBackendVideoUrl: !!visualPost.video_url,
                backendVideoLength: visualPost.video_url?.length || 0,
                hasExistingImageUrl: !!post.content.imageUrl,
                existingImageLength: post.content.imageUrl?.length || 0,
                backendImageUrlPreview: visualPost.image_url?.substring(0, 100) || 'N/A',
                backendVideoUrlPreview: visualPost.video_url?.substring(0, 100) || 'N/A'
              });
              
              const updatedPost = {
                ...post,
                content: {
                  ...post.content,
                  // FIXED: Map backend field names to frontend field names
                  imageUrl: visualPost.image_url || post.content.imageUrl,
                  videoUrl: visualPost.video_url || post.content.videoUrl
                }
              };
              
              // ENHANCED VERIFICATION WITH DETAILED LOGGING
              console.log(`✅ POST UPDATE VERIFICATION for ${post.id}:`, {
                originalHadImage: !!post.content.imageUrl,
                originalHadVideo: !!post.content.videoUrl,
                updatedHasImage: !!updatedPost.content.imageUrl,
                updatedHasVideo: !!updatedPost.content.videoUrl,
                imageUrlLength: updatedPost.content.imageUrl?.length || 0,
                videoUrlLength: updatedPost.content.videoUrl?.length || 0,
                backendImageUrl: visualPost.image_url,
                backendVideoUrl: visualPost.video_url,
                finalImageUrl: updatedPost.content.imageUrl,
                finalVideoUrl: updatedPost.content.videoUrl
              });
              
              // CRITICAL: Log video URL details for debugging
              if (columnId === 'text-video') {
                console.log(`🎬 VIDEO_URL_MAPPING_DEBUG for ${post.id}:`, {
                  backendHasVideoUrl: !!visualPost.video_url,
                  backendVideoUrl: visualPost.video_url,
                  frontendVideoUrl: updatedPost.content.videoUrl,
                  mappingSuccessful: !!updatedPost.content.videoUrl,
                  urlLength: updatedPost.content.videoUrl?.length || 0
                });
              }
              
              return updatedPost;
            } else {
              console.warn(`⚠️ No visual data found for post ${post.id}`);
            }
            return post;
          });
          
          // DETAILED VISUAL URL LOGGING FOR DEBUGGING
          transformedPosts.forEach((post, index) => {
            if (post.content.imageUrl) {
              console.log(`🖼️ Post ${post.id} has imageUrl: ${post.content.imageUrl.substring(0, 50)}... (${post.content.imageUrl.length} chars)`);
              // STDOUT for test visibility
              console.log(`✅ FRONTEND_IMAGE_VALIDATION: Post ${post.id} has imageUrl (${post.content.imageUrl.length} chars)`);
            } else {
              console.log(`❌ Post ${post.id} missing imageUrl`);
            }
            if (post.content.videoUrl) {
              console.log(`🎬 Post ${post.id} has videoUrl: ${post.content.videoUrl.substring(0, 50)}... (${post.content.videoUrl.length} chars)`);
              // STDOUT for test visibility
              console.log(`✅ FRONTEND_VIDEO_VALIDATION: Post ${post.id} has videoUrl (${post.content.videoUrl.length} chars)`);
            } else if (columnId === 'text-video') {
              console.log(`❌ Post ${post.id} missing videoUrl (expected for text-video column)`);
            }
          });
          
          console.log(`🎨 Updated ${transformedPosts.length} posts with visual content`, {
            postsWithImages: transformedPosts.filter(p => p.content.imageUrl).length,
            postsWithVideos: transformedPosts.filter(p => p.content.videoUrl).length
          });
        } else {
          console.warn(`⚠️ No visual data returned for ${columnId} posts`);
        }
      }
      
      // STEP 3: Final state update with all content (text + visuals) - ONLY NOW clear loading state
      setSocialMediaColumns(prev => prev.map(col => 
        col.id === columnId ? { 
          ...col, 
          posts: transformedPosts, 
          isGenerating: false // Clear generation state ONLY after visuals are complete
        } : col
      ));
      
      // DEBUGGING: Log final state for verification
      console.log(`🔍 FINAL STATE UPDATE for ${columnId}:`, {
        postsCount: transformedPosts.length,
        postsWithImages: transformedPosts.filter(p => p.content.imageUrl).length,
        postsWithVideos: transformedPosts.filter(p => p.content.videoUrl).length,
        sampleImageUrl: transformedPosts.find(p => p.content.imageUrl)?.content.imageUrl?.substring(0, 50),
        sampleVideoUrl: transformedPosts.find(p => p.content.videoUrl)?.content.videoUrl?.substring(0, 50)
      });

      const visualType = columnId === 'text-image' ? 'with images' : 
                        columnId === 'text-video' ? 'with videos' : '';
      const visualCount = columnId === 'text-image' ? 
                         transformedPosts.filter(p => p.content.imageUrl).length :
                         columnId === 'text-video' ?
                         transformedPosts.filter(p => p.content.videoUrl).length : 0;
      
      const successMessage = visualType ? 
        `Generated ${transformedPosts.length} ${postType.replace('_', ' + ')} posts ${visualType} (${visualCount} visuals)!` :
        `Generated ${transformedPosts.length} ${postType.replace('_', ' + ')} posts successfully!`;
      
      toast.success(successMessage);
      
    } catch (err) {
      console.error(`❌ Failed to generate ${columnId} posts:`, err);
      
      // IMPROVED ERROR HANDLING: Keep loading state if it's a timeout/network issue
      const errorMessage = err instanceof Error ? err.message : 'Unknown error occurred';
      const isTimeoutError = errorMessage.includes('timeout') || errorMessage.includes('aborted') || errorMessage.includes('network');
      
      if (isTimeoutError) {
        // For timeout errors, keep the loading state and show retry option
        console.log(`⏳ Timeout detected for ${columnId}, keeping loading state for retry`);
        setSocialMediaColumns(prev => prev.map(col => 
          col.id === columnId ? { 
            ...col, 
            isGenerating: true, // Keep loading for timeout errors
            posts: [] // Clear any partial posts
          } : col
        ));
        
        toast.error(`Generation is taking longer than expected. Please wait or try again.`, {
          duration: 8000,
          action: {
            label: 'Retry',
            onClick: () => generateColumnPosts(columnId)
          }
        });
      } else {
        // For actual errors, reset the loading state
        setSocialMediaColumns(prev => prev.map(col => 
          col.id === columnId ? { 
            ...col, 
            isGenerating: false, 
            posts: [] // Keep posts empty on error for clean state
          } : col
        ));
        
        const postType = columnId === 'text-only' ? 'text_url' : 
                        columnId === 'text-image' ? 'text_image' : 'text_video';
        console.error(`Generation error details:`, { columnId, postType, error: err });
        
        toast.error(`Failed to generate ${columnId.replace('-', ' + ')} posts: ${errorMessage}. Please check your connection and try again.`);
      }
          } finally {
        // CRITICAL FIX: Always clear the ref state after processing
        // The loading state management is handled in the catch block
        generationStateRef.current[columnId] = false;
      }
  }, [currentCampaign, preferredDesign, suggestedHashtags, socialMediaColumns, executeAbortableCall]);



  const togglePostSelection = (postId: string) => {
    setSelectedPosts(prev => 
      prev.includes(postId) 
        ? prev.filter(id => id !== postId)
        : [...prev, postId]
    );
  };

  const regeneratePost = async (columnId: string, postId: string) => {
    // Regenerate single post
    toast.success('Regenerating post...');
    // TODO: Implement single post regeneration
  };

  const handleProceedToScheduling = () => {
    if (selectedPosts.length === 0) {
      toast.error('Please select at least one post to proceed');
      return;
    }
    
    toast.success(`${selectedPosts.length} posts selected for scheduling!`);
    navigate('/scheduling');
  };

  const regenerateAIAnalysis = useCallback(async () => {
    setIsRegeneratingAnalysis(true);
    try {
      // CRITICAL DEBUG: Log current campaign data to identify source of wrong URLs
      console.log('🔍 DEBUG: Current campaign data:', {
        id: currentCampaign?.id,
        name: currentCampaign?.name,
        businessUrl: currentCampaign?.businessUrl,
        aboutPageUrl: currentCampaign?.aboutPageUrl,
        productServiceUrl: currentCampaign?.productServiceUrl,
        objective: currentCampaign?.objective,
        campaignType: currentCampaign?.campaignType
      });
      
      // Real API call to analyze URLs and get themes/tags using proper API client
      if (currentCampaign && (currentCampaign.businessUrl || currentCampaign.aboutPageUrl || currentCampaign.productServiceUrl)) {
        const urls = [
          currentCampaign.businessUrl,
          currentCampaign.aboutPageUrl,
          currentCampaign.productServiceUrl
        ].filter(url => url && url.trim());

        console.log('🔄 Regenerating AI analysis for URLs:', urls);
        console.log('🔍 DEBUG: Sending URLs to backend:', { urls, analysis_type: 'business_context' });

        const analysisResult = await VideoVentureLaunchAPI.analyzeUrls({
          urls: urls,
          analysis_type: 'business_context'
        });
        
        console.log('📊 AI Analysis Result:', {
          hasSuggestedThemes: !!analysisResult.suggested_themes,
          themesCount: analysisResult.suggested_themes?.length || 0,
          themes: analysisResult.suggested_themes,
          hasSuggestedTags: !!analysisResult.suggested_tags,
          tagsCount: analysisResult.suggested_tags?.length || 0,
          tags: analysisResult.suggested_tags,
          hasBusinessAnalysis: !!analysisResult.business_analysis
        });
        
        // Use AI-generated themes and tags directly from backend
        let suggestedThemes = analysisResult.suggested_themes || [];
        let suggestedTags = analysisResult.suggested_tags || [];
        
        console.log('🎨 Using AI-generated themes:', suggestedThemes);
        console.log('🏷️ Using AI-generated tags:', suggestedTags);
        
        // Fallback only if AI didn't generate any themes/tags
        if (suggestedThemes.length === 0) {
          console.log('⚠️ No AI themes found, using fallback themes');
          suggestedThemes = ['Professional', 'Modern', 'Innovative', 'Quality', 'Growth'];
        }
        
        if (suggestedTags.length === 0) {
          console.log('⚠️ No AI tags found, using fallback tags');
          suggestedTags = ['Business', 'Quality', 'Innovation', 'Growth', 'Success'];
        }

        // Update the marketing context with real themes and tags
        if (suggestedThemes.length > 0) {
          // Clear existing themes and add new ones
          selectedThemes.forEach(theme => unselectTheme(theme));
          suggestedThemes.slice(0, 3).forEach((theme: string) => selectTheme(theme));
        }
        
        if (suggestedTags.length > 0) {
          // Clear existing tags and add new ones  
          selectedTags.forEach(tag => unselectTag(tag));
          suggestedTags.slice(0, 4).forEach((tag: string) => selectTag(tag));
        }

        // Update AI summary with business analysis
        if (analysisResult.business_analysis) {
          const businessAnalysis = (analysisResult as any).business_analysis;
          const companyName = businessAnalysis.company_name || 'Your Company';
          const industry = businessAnalysis.industry || 'your industry';
          const targetAudience = businessAnalysis.target_audience || 'your target audience';
          const valuePropositions = businessAnalysis.value_propositions || [];
          const competitiveAdvantages = businessAnalysis.competitive_advantages || [];
          
          // Debug logging for campaign guidance
          console.log('🔍 AI Analysis Debug - Business Analysis:', {
            companyName,
            industry,
            targetAudience,
            hasCampaignGuidance: !!businessAnalysis.campaign_guidance,
            campaignGuidanceKeys: businessAnalysis.campaign_guidance ? Object.keys(businessAnalysis.campaign_guidance) : [],
            campaignGuidance: businessAnalysis.campaign_guidance
          });
          
          // Create a comprehensive AI summary
          let newSummary = `AI Analysis: ${companyName} operates in ${industry}, targeting ${targetAudience}.`;
          
          if (valuePropositions.length > 0) {
            newSummary += ` Key value propositions: ${valuePropositions.slice(0, 2).join(', ')}.`;
          }
          
          if (competitiveAdvantages.length > 0) {
            newSummary += ` Competitive advantages: ${competitiveAdvantages.slice(0, 2).join(', ')}.`;
          }
          
          newSummary += ` Campaign analysis regenerated successfully with ${suggestedThemes.length} themes and ${suggestedTags.length} tags.`;
          
          // Update the AI summary in the context immediately
          updateAiSummary(newSummary);
          
          // Update the current campaign with the COMPLETE new analysis
          const updatedAnalysis = {
            summary: newSummary,
            businessAnalysis: businessAnalysis,
            campaignGuidance: businessAnalysis.campaign_guidance || {},
            lastUpdated: new Date().toISOString()
          };
          
          console.log('🔄 Updating Campaign with AI Analysis:', {
            hasBusinessAnalysis: !!updatedAnalysis.businessAnalysis,
            hasCampaignGuidance: !!updatedAnalysis.campaignGuidance,
            campaignGuidanceKeys: Object.keys(updatedAnalysis.campaignGuidance),
            updatedAnalysis
          });
          
          updateCurrentCampaign({
            aiAnalysis: updatedAnalysis
          });
        }

        toast.success(`✨ AI Analysis Complete! Found ${suggestedThemes.length} themes and ${suggestedTags.length} tags from your business context.`);
      } else {
        // Fallback for campaigns without URLs
        toast.warning('No URLs provided for analysis. Using default themes and tags.');
      }
      
    } catch (error) {
      console.error('AI analysis regeneration failed:', error);
      toast.error('Failed to regenerate AI analysis. Please check your connection and try again.');
    } finally {
      setIsRegeneratingAnalysis(false);
    }
  }, [currentCampaign, selectedThemes, selectedTags, unselectTheme, selectTheme, unselectTag, selectTag, updateAiSummary, updateCurrentCampaign]);
  
  // CRITICAL FIX 1.6: Fix missing dependencies and remove unused code
  useEffect(() => {
    if (!currentCampaign) {
      console.warn('⚠️ No current campaign - redirecting to dashboard');
      navigate('/');
      return;
    }
    
    // CRITICAL DEBUG: Log campaign validation
    console.log('🔍 Campaign validation:', {
      id: currentCampaign.id,
      name: currentCampaign.name,
      hasBusinessUrl: !!currentCampaign.businessUrl,
      hasAboutUrl: !!currentCampaign.aboutPageUrl,
      hasProductUrl: !!currentCampaign.productServiceUrl,
      hasAiAnalysis: !!currentCampaign.aiAnalysis,
      timestamp: new Date().toISOString()
    });
    
    if (currentCampaign.preferredDesign) {
      setPreferredDesign(currentCampaign.preferredDesign);
    }
    
    // FIXED: Check if AI analysis and campaign guidance are missing and trigger regeneration
    const hasAiAnalysis = currentCampaign.aiAnalysis?.businessAnalysis;
    const hasCampaignGuidance = currentCampaign.aiAnalysis?.businessAnalysis?.campaign_guidance;
    const hasCreativeDirection = hasCampaignGuidance?.creative_direction;
    const hasUrls = currentCampaign.businessUrl || currentCampaign.aboutPageUrl || currentCampaign.productServiceUrl;
    
    // CRITICAL FIX 1.5: Remove unused analysisKey
    
    if (!hasAiAnalysis && hasUrls && !isRegeneratingAnalysis) {
      console.log('🔄 Missing AI analysis detected, triggering automatic regeneration...');
      // Add small delay to prevent race conditions
      setTimeout(() => {
        if (!isRegeneratingAnalysis) {
          regenerateAIAnalysis();
        }
      }, 500);
    } else if (hasAiAnalysis && (!hasCampaignGuidance || !hasCreativeDirection) && hasUrls && !isRegeneratingAnalysis) {
      console.log('🔄 Missing campaign guidance detected, triggering automatic regeneration...');
      // Add small delay to prevent race conditions
      setTimeout(() => {
        if (!isRegeneratingAnalysis) {
          regenerateAIAnalysis();
        }
      }, 500);
    }
    
    // CRITICAL FIX 1.4: Use safe localStorage operations
    const savedColumns = loadColumnsFromStorage();
    
    if (savedColumns && savedColumns.length > 0) {
      console.log('📦 Restored social media columns from localStorage for campaign:', currentCampaign.id);
      setSocialMediaColumns(savedColumns);
    } else if (currentCampaign.socialMediaColumns && currentCampaign.socialMediaColumns.length > 0) {
      console.log('📦 Using campaign data columns');
      // CRITICAL FIX: Reset any stuck generation states when restoring from campaign data
      const cleanedColumns = currentCampaign.socialMediaColumns.map((col: any) => ({
        ...col,
        isGenerating: false,
        isGeneratingVisuals: false
      }));
      
      setSocialMediaColumns(cleanedColumns as SocialMediaColumn[]);
    } else {
      // CRITICAL FIX: Only auto-generate posts if campaign analysis is complete
      // This prevents generic, low-quality posts and token waste on new campaigns
      const hasCompletedAnalysis = currentCampaign.aiAnalysis?.businessAnalysis?.campaign_guidance;
      
      if (hasCompletedAnalysis) {
        console.log('🎯 No saved columns found - generating initial posts (analysis complete)');
        // Auto-generate initial posts when page loads
        generateAllPosts();
      } else {
        console.log('⏳ Campaign analysis not complete - skipping auto-generation to prevent generic posts');
        // Initialize empty columns for manual generation after analysis
        setSocialMediaColumns([
          {
            id: 'text-only',
            title: '# Text + URL Posts',
            description: 'Marketing text with product URL for link unfurling',
            mediaType: 'text-only',
            posts: [],
            isGenerating: false
          },
          {
            id: 'text-image',
            title: '📸 Text + Image Posts',
            description: 'Marketing text with AI-generated brand-aligned images',
            mediaType: 'text-with-image',
            posts: [],
            isGenerating: false
          },
          {
            id: 'text-video',
            title: '🎬 Text + Video Posts',
            description: 'Marketing text with AI-generated product demo videos',
            mediaType: 'text-with-video',
            posts: [],
            isGenerating: false
          }
        ]);
      }
    }
  }, [currentCampaign, navigate, isRegeneratingAnalysis, loadColumnsFromStorage, generateAllPosts, regenerateAIAnalysis]);

  // CRITICAL FIX 1.4: Safe localStorage persistence with debouncing
  useEffect(() => {
    if (currentCampaign && socialMediaColumns.some(col => col.posts.length > 0)) {
      // Debounce localStorage saves to avoid excessive writes
      const timeoutId = setTimeout(() => {
        saveColumnsToStorage(socialMediaColumns);
        // Also update the campaign in the marketing context
        updateCurrentCampaign({ socialMediaColumns });
      }, 1000); // 1 second debounce
      
      return () => clearTimeout(timeoutId);
    }
  }, [socialMediaColumns, currentCampaign, saveColumnsToStorage, updateCurrentCampaign]);
  
  if (!currentCampaign) return null;
  
  return (
    <div className="min-h-screen vvl-gradient-bg flex flex-col">
      {/* Header */}
      <header className="vvl-header-blur">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="flex items-center gap-3">
                <Wand2 className="text-blue-400" size={24} />
                <h1 className="text-xl font-bold vvl-text-primary">Social Media Post Generator</h1>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <button 
                onClick={() => navigate('/')}
                className="vvl-button-secondary text-sm flex items-center gap-2"
              >
                <Home size={16} />
                Dashboard
              </button>
              <button 
                onClick={() => navigate('/')}
                className="vvl-button-secondary text-sm flex items-center gap-2"
              >
                <ArrowLeft size={16} />
                Back
              </button>
            </div>
          </div>
        </div>
      </header>
      
      <div className="container mx-auto px-6 py-12 flex-grow">
        <div className="max-w-7xl mx-auto">
          {/* Campaign Summary */}
          <div className="vvl-card p-6 mb-8">
            <div className="flex items-center gap-3 vvl-text-primary mb-6">
              <Sparkles size={24} className="text-blue-400" />
              <h2 className="text-2xl font-bold">AI Campaign Summary</h2>
            </div>
            
            {/* Campaign Overview */}
            <div className="grid lg:grid-cols-2 gap-6 mb-6">
              <div className="lg:col-span-1">
                <h3 className="text-lg font-semibold vvl-text-primary mb-3">{currentCampaign.name}</h3>
                <p className="vvl-text-secondary mb-4 text-sm leading-relaxed">{currentCampaign.objective}</p>
                
                {/* Campaign Configuration */}
                <div className="grid md:grid-cols-2 gap-4 mb-4">
                  <div>
                    <h4 className="text-sm font-semibold vvl-text-primary mb-2">Campaign Type</h4>
                    <span className="text-xs bg-blue-500/20 text-blue-400 px-3 py-1 rounded-full">
                      {currentCampaign.campaignType || 'General'}
                    </span>
                  </div>
                  <div>
                    <h4 className="text-sm font-semibold vvl-text-primary mb-2">AI Creativity Level</h4>
                    <span className="text-xs bg-purple-500/20 text-purple-400 px-3 py-1 rounded-full">
                      Level {currentCampaign.creativityLevel || 7}/10
                    </span>
                  </div>
                </div>

                {/* Business Information */}
                {currentCampaign.businessDescription && (
                  <div className="mb-4">
                    <h4 className="text-sm font-semibold vvl-text-primary mb-2">Business Context</h4>
                    <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-3">
                      <p className="text-sm vvl-text-secondary leading-relaxed">
                        {currentCampaign.businessDescription}
                      </p>
                    </div>
                  </div>
                )}

                {/* URLs Analyzed */}
                {(currentCampaign.businessUrl || currentCampaign.aboutPageUrl || currentCampaign.productServiceUrl) && (
                  <div className="mb-4">
                    <h4 className="text-sm font-semibold vvl-text-primary mb-2">URLs Analyzed</h4>
                    <div className="space-y-2">
                      {currentCampaign.businessUrl && (
                        <div className="flex items-center gap-2 text-xs">
                          <ExternalLink size={12} className="text-blue-400" />
                          <span className="vvl-text-secondary">Business:</span>
                          <a href={currentCampaign.businessUrl} target="_blank" rel="noopener noreferrer" 
                             className="text-blue-400 hover:text-blue-300 truncate max-w-xs">
                            {currentCampaign.businessUrl}
                          </a>
                        </div>
                      )}
                      {currentCampaign.aboutPageUrl && (
                        <div className="flex items-center gap-2 text-xs">
                          <ExternalLink size={12} className="text-green-400" />
                          <span className="vvl-text-secondary">About:</span>
                          <a href={currentCampaign.aboutPageUrl} target="_blank" rel="noopener noreferrer" 
                             className="text-green-400 hover:text-green-300 truncate max-w-xs">
                            {currentCampaign.aboutPageUrl}
                          </a>
                        </div>
                      )}
                      {currentCampaign.productServiceUrl && (
                        <div className="flex items-center gap-2 text-xs">
                          <ExternalLink size={12} className="text-purple-400" />
                          <span className="vvl-text-secondary">Product/Service:</span>
                          <a href={currentCampaign.productServiceUrl} target="_blank" rel="noopener noreferrer" 
                             className="text-purple-400 hover:text-purple-300 truncate max-w-xs">
                            {currentCampaign.productServiceUrl}
                          </a>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {/* Uploaded Assets */}
                {(currentCampaign.uploadedImages?.length || currentCampaign.uploadedDocuments?.length || currentCampaign.campaignAssets?.length) && (
                  <div className="mb-4">
                    <h4 className="text-sm font-semibold vvl-text-primary mb-2">Uploaded Assets</h4>
                    <div className="grid grid-cols-3 gap-4">
                      {currentCampaign.uploadedImages?.length > 0 && (
                        <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-3 text-center">
                          <Image size={16} className="text-green-400 mx-auto mb-1" />
                          <p className="text-xs vvl-text-secondary">Product/Brand Images</p>
                          <p className="text-xs text-green-400 font-medium">{currentCampaign.uploadedImages.length} files</p>
                        </div>
                      )}
                      {currentCampaign.uploadedDocuments?.length > 0 && (
                        <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-3 text-center">
                          <Hash size={16} className="text-blue-400 mx-auto mb-1" />
                          <p className="text-xs vvl-text-secondary">Documents & Specs</p>
                          <p className="text-xs text-blue-400 font-medium">{currentCampaign.uploadedDocuments.length} files</p>
                        </div>
                      )}
                      {currentCampaign.campaignAssets?.length > 0 && (
                        <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-3 text-center">
                          <Video size={16} className="text-purple-400 mx-auto mb-1" />
                          <p className="text-xs vvl-text-secondary">Campaign Assets</p>
                          <p className="text-xs text-purple-400 font-medium">{currentCampaign.campaignAssets.length} files</p>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {/* Example Content */}
                {currentCampaign.exampleContent && (
                  <div className="mb-4">
                    <h4 className="text-sm font-semibold vvl-text-primary mb-2">Example Content Reference</h4>
                    <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-3">
                      <p className="text-sm vvl-text-secondary leading-relaxed">
                        {currentCampaign.exampleContent}
                      </p>
                    </div>
                  </div>
                )}
              </div>

              {/* AI Analysis Panel */}
              <div className="lg:col-span-1">
                <div className="bg-gradient-to-br from-blue-500/10 to-purple-500/10 backdrop-blur-sm border border-blue-400/20 rounded-lg p-4">
                  <h4 className="text-sm font-semibold vvl-text-primary mb-3 flex items-center gap-2">
                    <Sparkles size={16} className="text-blue-400" />
                    AI Analysis
                    {/* Show analysis status indicator */}
                    {!currentCampaign.aiAnalysis?.businessAnalysis?.campaign_guidance && (
                      <span className="text-xs bg-orange-500/20 text-orange-400 px-2 py-1 rounded-full">
                        Incomplete
                      </span>
                    )}
                  </h4>
                  
                  {/* Analysis Status Alert */}
                  {!currentCampaign.aiAnalysis?.businessAnalysis?.campaign_guidance && (
                    <div className="bg-orange-500/10 border border-orange-400/20 rounded-lg p-3 mb-4">
                      <div className="flex items-center gap-2 mb-2">
                        <AlertTriangle size={14} className="text-orange-400" />
                        <span className="text-xs font-medium text-orange-400">Analysis Required</span>
                      </div>
                      <p className="text-xs text-orange-300 leading-relaxed">
                        Campaign analysis is incomplete. Auto-generation is disabled to prevent generic posts and token waste. 
                        Complete the analysis first for personalized, high-quality content.
                      </p>
                    </div>
                  )}
                  
                  <p className="text-sm vvl-text-secondary leading-relaxed mb-4">
                    {currentCampaign?.aiAnalysis?.summary || aiSummary || "AI-generated summary will appear here after analyzing your business URLs. Click 'Regenerate Analysis' to analyze your campaign context."}
                  </p>
                  
                  {/* Analysis Metrics */}
                  <div className="space-y-3">
                    <div className="flex justify-between items-center">
                      <span className="text-xs vvl-text-secondary">Content Relevance</span>
                      <span className="text-xs text-green-400 font-medium">High</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-xs vvl-text-secondary">Brand Alignment</span>
                      <span className="text-xs text-blue-400 font-medium">Excellent</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-xs vvl-text-secondary">Target Audience Fit</span>
                      <span className="text-xs text-purple-400 font-medium">Strong</span>
                    </div>
                  </div>

                  {/* Quick Actions */}
                  <div className="mt-4 pt-3 border-t border-white/10">
                    <button 
                      onClick={regenerateAIAnalysis}
                      disabled={isRegeneratingAnalysis}
                      className="w-full text-xs bg-blue-500/20 text-blue-400 px-3 py-2 rounded-lg hover:bg-blue-500/30 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                    >
                      <RefreshCw size={12} className={isRegeneratingAnalysis ? 'animate-spin' : ''} />
                      {isRegeneratingAnalysis ? 'Regenerating...' : 'Regenerate Analysis'}
                    </button>
                  </div>
                </div>
              </div>
            </div>

            {/* Campaign Creative Guidance Section - Now Editable */}
            <div className="bg-gradient-to-br from-purple-500/10 to-blue-500/10 border border-purple-400/20 rounded-lg p-6 mb-4">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  <Palette className="text-purple-400" size={20} />
                  <h4 className="text-lg font-semibold text-white">Campaign Creative Guidance</h4>
                  {isRegeneratingAnalysis && (
                    <div className="flex items-center gap-2 text-sm text-blue-400">
                      <div className="w-3 h-3 border border-blue-400 border-t-transparent rounded-full animate-spin"></div>
                      <span>Updating...</span>
                    </div>
                  )}
                </div>
                <div className="flex items-center gap-2">
                  {/* Show regenerate button if guidance is missing or incomplete */}
                  {(!currentCampaign?.aiAnalysis?.businessAnalysis?.campaign_guidance?.creative_direction || 
                    !currentCampaign?.aiAnalysis?.businessAnalysis?.campaign_guidance?.visual_style) && (
                    <button 
                      onClick={regenerateAIAnalysis}
                      disabled={isRegeneratingAnalysis}
                      className="flex items-center gap-2 bg-orange-500/20 text-orange-400 px-3 py-1 rounded-lg hover:bg-orange-500/30 transition-colors text-sm disabled:opacity-50"
                    >
                      <RefreshCw size={16} className={isRegeneratingAnalysis ? 'animate-spin' : ''} />
                      {isRegeneratingAnalysis ? 'Generating...' : 'Generate Guidance'}
                    </button>
                  )}
                  <button 
                    onClick={() => setShowGuidanceChat(!showGuidanceChat)}
                    className="flex items-center gap-2 bg-purple-500/20 text-purple-400 px-3 py-1 rounded-lg hover:bg-purple-500/30 transition-colors text-sm"
                  >
                    <MessageCircle size={16} />
                    Chat to Refine
                  </button>
                  <button 
                    onClick={() => setShowGuidanceEdit(!showGuidanceEdit)}
                    className="flex items-center gap-2 bg-blue-500/20 text-blue-400 px-3 py-1 rounded-lg hover:bg-blue-500/30 transition-colors text-sm"
                  >
                    <Edit size={16} />
                    Edit
                  </button>
                </div>
              </div>
              
              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <h5 className="text-sm font-semibold text-white mb-2">Creative Direction</h5>
                  <p className="text-sm text-gray-200 leading-relaxed mb-3">
                    {(() => {
                      // Debug logging for campaign guidance
                      console.log('Campaign Guidance Debug:', {
                        hasAiAnalysis: !!currentCampaign?.aiAnalysis,
                        hasCampaignGuidance: !!currentCampaign?.aiAnalysis?.campaignGuidance,
                        campaignGuidanceKeys: currentCampaign?.aiAnalysis?.campaignGuidance ? Object.keys(currentCampaign.aiAnalysis.campaignGuidance) : [],
                        creativeDirection: currentCampaign?.aiAnalysis?.campaignGuidance?.creative_direction
                      });
                      
                      // FIXED: Correct data path for campaign guidance
                      const businessAnalysis = currentCampaign?.aiAnalysis?.businessAnalysis;
                      const creativeDirection = businessAnalysis?.campaign_guidance?.creative_direction;
                      
                      if (creativeDirection && creativeDirection.trim() !== '') {
                        return creativeDirection;
                      }
                      
                      // Legacy fallback for older data structure
                      const legacyCreativeDirection = currentCampaign?.aiAnalysis?.campaignGuidance?.creative_direction;
                      if (legacyCreativeDirection && legacyCreativeDirection.trim() !== '') {
                        return legacyCreativeDirection;
                      }
                      
                      return "AI-generated creative direction will appear here after analysis. Click 'Regenerate Analysis' to generate tailored creative guidance based on your business context.";
                    })()}
                  </p>
                  
                  <h5 className="text-sm font-semibold text-white mb-2 mt-4">Visual Style</h5>
                  <div className="space-y-2">
                    {(() => {
                      // FIXED: Correct data path for visual style
                      const businessAnalysis = currentCampaign?.aiAnalysis?.businessAnalysis;
                      const visualStyle = businessAnalysis?.campaign_guidance?.visual_style;
                      
                      if (visualStyle) {
                        return (
                          <>
                            <div className="flex items-center gap-2 text-xs">
                              <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
                              <span className="text-gray-300">Photography: {visualStyle.photography_style || visualStyle.photography || "Professional lifestyle"}</span>
                            </div>
                            <div className="flex items-center gap-2 text-xs">
                              <div className="w-3 h-3 bg-purple-500 rounded-full"></div>
                              <span className="text-gray-300">Mood: {visualStyle.mood || visualStyle.brand_mood || "Professional, trustworthy"}</span>
                            </div>
                            <div className="flex items-center gap-2 text-xs">
                              <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                              <span className="text-gray-300">Lighting: {visualStyle.lighting || visualStyle.lighting_style || "Natural lighting"}</span>
                            </div>
                          </>
                        );
                      }
                      
                      return (
                        <div className="text-xs text-gray-400 italic">
                          AI-generated visual style guidelines will appear here after analysis.
                        </div>
                      );
                    })()}
                  </div>
                </div>
                
                <div>
                  <h5 className="text-sm font-semibold text-white mb-2">Content Themes</h5>
                  <p className="text-sm text-gray-200 leading-relaxed mb-3">
                    {(() => {
                      // FIXED: Correct data path for target context
                      const businessAnalysis = currentCampaign?.aiAnalysis?.businessAnalysis;
                      const targetContext = businessAnalysis?.campaign_guidance?.target_context;
                      
                      if (targetContext && targetContext.trim() !== '') {
                        return targetContext;
                      }
                      
                      // Try to build from content themes
                      const contentThemes = businessAnalysis?.campaign_guidance?.content_themes;
                      
                      if (contentThemes?.primary_themes?.length > 0) {
                        return `Focus on ${contentThemes.primary_themes.slice(0, 3).join(', ').toLowerCase()}. Use compelling calls-to-action that resonate with your target audience and drive engagement.`;
                      }
                      
                      return "AI-generated content strategy will appear here after analysis. This will include tailored messaging themes based on your business context.";
                    })()}
                  </p>
                  
                  <div className="flex flex-wrap gap-2">
                    {(() => {
                      // FIXED: Correct data path for content themes
                      const businessAnalysis = currentCampaign?.aiAnalysis?.businessAnalysis;
                      const contentThemes = businessAnalysis?.campaign_guidance?.content_themes;
                      
                      const primaryThemes = contentThemes?.primary_themes || [];
                      const productThemes = contentThemes?.product_specific_themes || [];
                      const allThemes = [...primaryThemes, ...productThemes].slice(0, 6); // Limit to 6 themes
                      
                      if (allThemes.length > 0) {
                        return allThemes.map((theme: string) => (
                          <span key={theme} className="text-xs bg-purple-500/20 text-purple-400 px-2 py-1 rounded-full">
                            {theme}
                          </span>
                        ));
                      }
                      
                      return (
                        <span className="text-xs text-gray-400 italic">
                          AI-generated content themes will appear here
                        </span>
                      );
                    })()}
                  </div>
                </div>
              </div>
              
              <div className="mt-4 pt-4 border-t border-white/10">
                <div className="grid md:grid-cols-2 gap-4 text-xs">
                  <div>
                    <span className="font-semibold text-blue-400">Image Generation:</span>
                    <span className="text-gray-300 ml-2">
                      {(() => {
                        // FIXED: Correct data path for imagen prompts
                        const businessAnalysis = currentCampaign?.aiAnalysis?.businessAnalysis;
                        const imagenPrompts = businessAnalysis?.campaign_guidance?.imagen_prompts;
                        
                        if (imagenPrompts?.technical_specs) {
                          return imagenPrompts.technical_specs;
                        }
                        
                        if (imagenPrompts?.style_guidance) {
                          return imagenPrompts.style_guidance;
                        }
                        
                        return "AI-generated image guidance will appear after analysis";
                      })()}
                    </span>
                  </div>
                  <div>
                    <span className="font-semibold text-purple-400">Video Generation:</span>
                    <span className="text-gray-300 ml-2">
                      {(() => {
                        // FIXED: Correct data path for veo prompts
                        const businessAnalysis = currentCampaign?.aiAnalysis?.businessAnalysis;
                        const veoPrompts = businessAnalysis?.campaign_guidance?.veo_prompts;
                        
                        if (veoPrompts?.duration_focus) {
                          return veoPrompts.duration_focus;
                        }
                        
                        if (veoPrompts?.style_guidance) {
                          return veoPrompts.style_guidance;
                        }
                        
                        return "AI-generated video guidance will appear after analysis";
                      })()}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* Campaign Guidance Chat Interface */}
            {showGuidanceChat && (
              <div className="mt-6">
                <div className="vvl-card p-6">
                  <h4 className="text-lg font-semibold vvl-text-primary mb-4">Campaign Guidance Chat</h4>
                  <p className="vvl-text-secondary mb-4">Chat interface for refining campaign guidance will be available here.</p>
                  <button 
                    onClick={() => setShowGuidanceChat(false)}
                    className="vvl-button-secondary"
                  >
                    Close
                  </button>
                </div>
              </div>
            )}

            {/* Campaign Guidance Edit Interface */}
            {showGuidanceEdit && (
              <div className="mt-6">
                <div className="vvl-card p-6">
                  <h4 className="text-lg font-semibold vvl-text-primary mb-4">Edit Campaign Guidance</h4>
                  <p className="vvl-text-secondary mb-4">Edit interface for campaign guidance will be available here.</p>
                  <button 
                    onClick={() => setShowGuidanceEdit(false)}
                    className="vvl-button-secondary"
                  >
                    Close
                  </button>
                </div>
              </div>
            )}

            {/* Campaign Validation Status - EVENT DRIVEN */}
            {(() => {
              // FIXED: Event-driven campaign readiness based on actual AI analysis completion
              const hasAiAnalysis = currentCampaign?.aiAnalysis?.businessAnalysis;
              const hasCampaignGuidance = currentCampaign?.aiAnalysis?.businessAnalysis?.campaign_guidance;
              const hasCreativeDirection = hasCampaignGuidance?.creative_direction;
              const hasVisualStyle = hasCampaignGuidance?.visual_style;
              const hasContentThemes = hasCampaignGuidance?.content_themes;
              const hasUrls = currentCampaign?.businessUrl || currentCampaign?.aboutPageUrl || currentCampaign?.productServiceUrl;
              
              const isFullyReady = hasAiAnalysis && hasCreativeDirection && hasVisualStyle && hasContentThemes;
              const isPartiallyReady = hasAiAnalysis && hasCampaignGuidance;
              const needsAnalysis = !hasAiAnalysis && hasUrls;
              
              if (isRegeneratingAnalysis) {
                return (
                  <div className="bg-blue-500/10 border border-blue-400/20 rounded-lg p-4">
                    <div className="flex items-center gap-3">
                      <div className="w-3 h-3 border border-blue-400 border-t-transparent rounded-full animate-spin"></div>
                      <span className="text-sm font-medium text-blue-400">Generating Campaign Guidance...</span>
                    </div>
                    <p className="text-xs vvl-text-secondary mt-1 ml-6">
                      AI is analyzing your business context and generating personalized campaign guidance.
                    </p>
                  </div>
                );
              } else if (isFullyReady) {
                return (
                  <div className="bg-green-500/10 border border-green-400/20 rounded-lg p-4">
                    <div className="flex items-center gap-3">
                      <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                      <span className="text-sm font-medium text-green-400">Campaign Ready for Content Generation</span>
                    </div>
                    <p className="text-xs vvl-text-secondary mt-1 ml-5">
                      AI analysis complete with creative guidance, visual style, and content themes. Ready to generate targeted social media content.
                    </p>
                  </div>
                );
              } else if (isPartiallyReady) {
                return (
                  <div className="bg-yellow-500/10 border border-yellow-400/20 rounded-lg p-4">
                    <div className="flex items-center gap-3">
                      <div className="w-2 h-2 bg-yellow-400 rounded-full animate-pulse"></div>
                      <span className="text-sm font-medium text-yellow-400">Campaign Guidance Incomplete</span>
                    </div>
                    <p className="text-xs vvl-text-secondary mt-1 ml-5">
                      Basic AI analysis available, but campaign guidance needs completion. Click "Generate Guidance" above to complete setup.
                    </p>
                  </div>
                );
              } else if (needsAnalysis) {
                return (
                  <div className="bg-orange-500/10 border border-orange-400/20 rounded-lg p-4">
                    <div className="flex items-center gap-3">
                      <div className="w-2 h-2 bg-orange-400 rounded-full animate-pulse"></div>
                      <span className="text-sm font-medium text-orange-400">AI Analysis Required</span>
                    </div>
                    <p className="text-xs vvl-text-secondary mt-1 ml-5">
                      Business URLs detected but analysis not started. Click "Regenerate Analysis" above to begin AI analysis.
                    </p>
                  </div>
                );
              } else {
                return (
                  <div className="bg-gray-500/10 border border-gray-400/20 rounded-lg p-4">
                    <div className="flex items-center gap-3">
                      <div className="w-2 h-2 bg-gray-400 rounded-full"></div>
                      <span className="text-sm font-medium text-gray-400">Campaign Setup Incomplete</span>
                    </div>
                    <p className="text-xs vvl-text-secondary mt-1 ml-5">
                      Please provide business URLs in the campaign setup to enable AI analysis and guidance generation.
                    </p>
                  </div>
                );
              }
            })()}
          </div>

          {/* Business Logic & Cost Control Information */}
          <div className="vvl-card p-6 mb-8">
            <div className="flex items-center gap-3 mb-4">
              <Info className="text-blue-400" size={24} />
              <h3 className="text-lg font-semibold vvl-text-primary">Content Generation Limits & Cost Control</h3>
            </div>
            
            <div className="grid md:grid-cols-3 gap-4 mb-4">
              <div className="bg-blue-500/10 border border-blue-500/20 rounded-lg p-4">
                <div className="flex items-center gap-2 mb-2">
                  <Hash className="text-blue-400" size={16} />
                  <span className="text-sm font-medium text-blue-400">Text + URL Posts</span>
                </div>
                <p className="text-lg font-bold vvl-text-primary">Up to 4 posts</p>
                <p className="text-xs vvl-text-secondary">Optimized for link sharing and traffic generation</p>
              </div>
              
              <div className="bg-green-500/10 border border-green-500/20 rounded-lg p-4">
                <div className="flex items-center gap-2 mb-2">
                  <Image className="text-green-400" size={16} />
                  <span className="text-sm font-medium text-green-400">Text + Image Posts</span>
                </div>
                <p className="text-lg font-bold vvl-text-primary">Up to 4 posts</p>
                <p className="text-xs vvl-text-secondary">Limited to control Imagen API costs</p>
              </div>
              
              <div className="bg-purple-500/10 border border-purple-500/20 rounded-lg p-4">
                <div className="flex items-center gap-2 mb-2">
                  <Video className="text-purple-400" size={16} />
                  <span className="text-sm font-medium text-purple-400">Text + Video Posts</span>
                </div>
                <p className="text-lg font-bold vvl-text-primary">Up to 4 posts</p>
                <p className="text-xs vvl-text-secondary">Limited to control Veo API costs</p>
              </div>
            </div>
            
            <div className="bg-yellow-500/10 border border-yellow-500/20 rounded-lg p-3">
              <div className="flex items-start gap-2">
                <AlertTriangle className="text-yellow-400 mt-0.5" size={16} />
                <div className="text-xs vvl-text-secondary">
                  <strong className="text-yellow-400">Cost Management:</strong> Generation limits are enforced to prevent 
                  exceeding model context limits and manage API costs. Text + URL posts have higher limits as they use only 
                  text generation, while visual content is limited due to compute-intensive image/video generation.
                </div>
              </div>
            </div>
          </div>

          {/* Theme and Tag Selection */}
          <div className="grid md:grid-cols-2 gap-6 mb-8">
            <div className="vvl-card p-6">
              <h3 className="text-lg font-semibold vvl-text-primary mb-4">Suggested Themes</h3>
              <div className="flex flex-wrap gap-2">
                {suggestedThemes.map(theme => (
                  <button
                    key={theme}
                    onClick={() => selectedThemes.includes(theme) ? unselectTheme(theme) : selectTheme(theme)}
                    className={`px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                      selectedThemes.includes(theme)
                        ? 'bg-blue-500/30 text-blue-400 border border-blue-400'
                        : 'bg-white/5 text-gray-300 border border-white/20 hover:bg-white/10'
                    }`}
                  >
                    {theme}
                  </button>
                ))}
              </div>
            </div>

            <div className="vvl-card p-6">
              <h3 className="text-lg font-semibold vvl-text-primary mb-4">Suggested Tags</h3>
              <div className="flex flex-wrap gap-2">
                {suggestedTags.map(tag => (
                  <button
                    key={tag}
                    onClick={() => selectedTags.includes(tag) ? unselectTag(tag) : selectTag(tag)}
                    className={`px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                      selectedTags.includes(tag)
                        ? 'bg-purple-500/30 text-purple-400 border border-purple-400'
                        : 'bg-white/5 text-gray-300 border border-white/20 hover:bg-white/10'
                    }`}
                  >
                    #{tag}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Campaign Media Tuning */}
          <div className="vvl-card p-6 mb-8">
            <h3 className="text-lg font-semibold vvl-text-primary mb-4">Campaign Tuning (Optional)</h3>
            <p className="text-sm vvl-text-secondary mb-3">
              Fine-tune your visual content generation by specifying design preferences, visual styles, colors, moods, or specific requirements for images and videos.
            </p>
            <Textarea
              placeholder="Example: I want vibrant, colorful t-shirt designs with creative artwork instead of generic text. Use modern, artistic styles with unique graphics that reflect creativity and personal expression..."
              value={preferredDesign}
              onChange={(e) => setPreferredDesign(e.target.value)}
              className="min-h-[100px] resize-none bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-3 text-white placeholder-gray-400 focus:border-blue-500/50 focus:ring-1 focus:ring-blue-500/25"
            />
          </div>

          {/* Suggested Marketing Post Ideas - Main Section */}
          <div className="mb-12">
            <div className="text-center mb-8">
              <h2 className="text-3xl font-bold vvl-text-primary mb-4 flex items-center justify-center gap-3">
                <Sparkles className="text-blue-400" size={32} />
                Suggested Marketing Post Ideas
              </h2>
              <p className="text-lg vvl-text-secondary">
                AI-generated social media content tailored to your campaign objectives
              </p>
            </div>

            {/* Content Grid */}
            <div className="grid lg:grid-cols-3 gap-8">
              {socialMediaColumns.map((column) => (
                <div key={column.id} className="vvl-card p-6">
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-3">
                      <div className="flex items-center gap-2">
                        {column.id === 'text-only' && <Hash className="text-blue-400" size={20} />}
                        {column.id === 'text-image' && <Image className="text-green-400" size={20} />}
                        {column.id === 'text-video' && <Video className="text-purple-400" size={20} />}
                        <h3 className="text-lg font-semibold vvl-text-primary">{column.title}</h3>
                      </div>
                      <span className={`text-xs px-2 py-1 rounded-full ${
                        column.id === 'text-only' ? 'bg-blue-500/20 text-blue-400' :
                        column.id === 'text-image' ? 'bg-green-500/20 text-green-400' :
                        'bg-purple-500/20 text-purple-400'
                      }`}>
                        {column.id === 'text-only' ? 'BASIC' : 
                         column.id === 'text-image' ? 'ENHANCED' : 'PREMIUM'}
                      </span>
                    </div>
                  </div>
                  
                  <p className="text-sm vvl-text-secondary mb-4">{column.description}</p>
                  
                  {/* Text Content Generation Button */}
                  <button
                    onClick={() => generateColumnPosts(column.id)}
                    disabled={column.isGenerating}
                    className={`w-full py-3 px-4 rounded-lg font-medium transition-all duration-200 flex items-center justify-center gap-2 ${
                      column.isGenerating
                        ? 'bg-gray-600 text-gray-400 cursor-not-allowed'
                        : column.id === 'text-only'
                        ? 'bg-blue-600 hover:bg-blue-700 text-white'
                        : column.id === 'text-image'
                        ? 'bg-green-600 hover:bg-green-700 text-white'
                        : 'bg-gradient-to-r from-purple-600 to-orange-500 hover:from-purple-700 hover:to-orange-600 text-white'
                    }`}
                  >
                    {column.isGenerating ? (
                      <>
                        {/* AI Processing Animation */}
                        <div className="flex items-center gap-2">
                          <div className="relative">
                            <div className="w-4 h-4 border-2 border-gray-400 border-t-white rounded-full animate-spin"></div>
                          </div>
                          <span className="text-sm">AI Processing...</span>
                        </div>
                      </>
                    ) : (
                      <>
                        <RefreshCw size={16} />
                        {column.posts.length > 0 ? 'Regenerate Text Content' :
                         column.id === 'text-only' ? 'Generate Text + URL Posts' :
                         column.id === 'text-image' ? 'Generate Text + Image Posts' :
                         'Generate Text + Video Posts'}
                      </>
                    )}
                  </button>


                  
                  {/* Enhanced Loading State with AI Processing Indicators */}
                  {column.isGenerating && (
                    <div className="mt-4 p-6 bg-gradient-to-br from-blue-500/10 to-purple-500/10 backdrop-blur-sm border border-blue-400/20 rounded-lg">
                      <div className="flex items-center gap-3 mb-4">
                        <div className="relative">
                          <div className="w-6 h-6 border-2 border-blue-400 border-t-transparent rounded-full animate-spin"></div>
                          <div className="absolute inset-0 w-6 h-6 border-2 border-purple-400/30 border-b-transparent rounded-full animate-spin animation-delay-300" style={{animationDirection: 'reverse'}}></div>
                        </div>
                        <div>
                          <h4 className="text-sm font-semibold text-blue-400">AI Processing in Progress</h4>
                          <p className="text-xs text-gray-400">Please wait while our AI agents work on your content...</p>
                        </div>
                      </div>
                      
                      <div className="space-y-3">
                        <div className="flex items-center gap-3 text-sm text-blue-400">
                          <div className="w-2 h-2 bg-blue-400 rounded-full animate-pulse"></div>
                          <span>🧠 Analyzing business context with Gemini AI...</span>
                        </div>
                        <div className="flex items-center gap-3 text-sm text-green-400">
                          <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" style={{animationDelay: '0.3s'}}></div>
                          <span>✨ Generating creative content variations...</span>
                        </div>
                        <div className="flex items-center gap-3 text-sm text-purple-400">
                          <div className="w-2 h-2 bg-purple-400 rounded-full animate-pulse" style={{animationDelay: '0.6s'}}></div>
                          <span>🎯 Optimizing for platform engagement...</span>
                        </div>
                        {column.id !== 'text-only' && (
                          <div className="flex items-center gap-3 text-sm text-orange-400">
                            <div className="w-2 h-2 bg-orange-400 rounded-full animate-pulse" style={{animationDelay: '0.9s'}}></div>
                            <span>
                              {column.id === 'text-image' ? '🎨 Generating images with Imagen AI...' : '🎬 Generating videos with Veo AI...'}
                            </span>
                          </div>
                        )}
                      </div>
                      
                      {/* Enhanced Progress Bar with Time Estimation */}
                      <div className="mt-6">
                        <div className="flex justify-between items-center mb-2">
                          <span className="text-xs font-medium text-gray-300">Processing Progress</span>
                          <span className="text-xs text-blue-400">
                            {column.id === 'text-only' ? '~5-8 seconds' : 
                             column.id === 'text-image' ? '~10-15 seconds' : '~15-25 seconds'}
                          </span>
                        </div>
                        <div className="w-full bg-gray-700/50 rounded-full h-2 overflow-hidden">
                          <div className="bg-gradient-to-r from-blue-500 via-purple-500 to-orange-500 h-2 rounded-full animate-pulse transition-all duration-2000 relative">
                            <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent animate-shimmer"></div>
                          </div>
                        </div>
                        <div className="flex justify-between items-center mt-2">
                          <span className="text-xs text-gray-500">
                            {column.id === 'text-only' ? 'Text Generation' : 
                             column.id === 'text-image' ? 'Text + Image Generation' : 'Text + Video Generation'}
                          </span>
                          <div className="flex items-center gap-1">
                            <div className="w-1 h-1 bg-blue-400 rounded-full animate-bounce"></div>
                            <div className="w-1 h-1 bg-purple-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                            <div className="w-1 h-1 bg-orange-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                          </div>
                        </div>
                      </div>
                      
                      {/* Important Notice */}
                      <div className="mt-4 p-3 bg-yellow-500/10 border border-yellow-400/20 rounded-lg">
                        <div className="flex items-start gap-2">
                          <div className="w-4 h-4 text-yellow-400 mt-0.5">⚠️</div>
                          <div className="text-xs text-yellow-300">
                            <strong>Please wait:</strong> AI processing is in progress. The "Regenerate" button is disabled to prevent duplicate requests and ensure optimal results.
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                  
                  {/* Posts Display */}
                  <div className="mt-6 space-y-4">
                    {column.posts.length === 0 && !column.isGenerating ? (
                      <div className="text-center py-8 text-gray-400">
                        <div className="text-4xl mb-2">🎯</div>
                        <p className="text-sm">No posts generated yet</p>
                        <p className="text-xs text-gray-500 mt-1">Click "Regenerate" to create content</p>
                      </div>
                    ) : (
                      column.posts.map((post, index) => (
                        <div key={post.id} className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-4 break-words">
                          {/* Visual Content Display */}
                          {(post.content.imageUrl || post.content.videoUrl) && (
                            <div className="mb-4">
                              {post.content.imageUrl && (
                                <div className="relative rounded-lg overflow-hidden bg-gray-800">
                                  <img 
                                    src={post.content.imageUrl} 
                                    alt="Generated marketing image"
                                    className="w-full h-48 object-cover"
                                    onLoad={() => {
                                      console.log(`✅ IMAGE_LOADED: Post ${post.id} image loaded successfully`);
                                    }}
                                    onError={(e) => {
                                      console.error(`❌ IMAGE_ERROR: Post ${post.id} image failed to load:`, e);
                                      console.log(`🔍 Image URL length: ${post.content.imageUrl?.length}`);
                                      console.log(`🔍 Image URL format: ${post.content.imageUrl?.substring(0, 50)}...`);
                                      // Fallback to placeholder if image fails to load
                                      e.currentTarget.src = 'https://picsum.photos/400/240?blur=2';
                                    }}
                                  />
                                  {/* Debug overlay */}
                                  <div className="absolute top-1 right-1 bg-black/50 text-white text-xs px-1 rounded">
                                    {post.content.imageUrl ? `${Math.round(post.content.imageUrl.length / 1024)}KB` : 'No Image'}
                                  </div>
                                </div>
                              )}
                              
                              {post.content.videoUrl && (
                                <div className="relative rounded-lg overflow-hidden bg-gray-800 group">
                                  {/* Debug Info */}
                                  <div className="absolute top-1 left-1 bg-black/70 text-white text-xs px-1 rounded z-30">
                                    {post.content.videoUrl ? `✅ ${Math.round(post.content.videoUrl.length / 1024)}KB` : '❌ No URL'}
                                  </div>
                                  
                                  {/* Simplified Video Player - YouTube Style */}
                                  <video 
                                    src={post.content.videoUrl}
                                    className="w-full h-48 object-cover"
                                    controls
                                    muted
                                    playsInline
                                    preload="metadata"
                                    onLoadStart={() => {
                                      console.log(`🎬 VIDEO_LOAD_START: ${post.id} - ${post.content.videoUrl}`);
                                    }}
                                    onLoadedData={() => {
                                      console.log(`✅ VIDEO_LOADED: ${post.id} - Video loaded successfully`);
                                    }}
                                    onCanPlay={() => {
                                      console.log(`▶️ VIDEO_CAN_PLAY: ${post.id} - Ready to play`);
                                    }}
                                    onError={(e) => {
                                      console.error(`❌ VIDEO_ERROR: ${post.id}`, {
                                        error: e,
                                        videoUrl: post.content.videoUrl,
                                        errorCode: e.currentTarget.error?.code,
                                        errorMessage: e.currentTarget.error?.message
                                      });
                                    }}
                                    style={{
                                      maxWidth: '100%',
                                      height: '192px',
                                      objectFit: 'cover'
                                    }}
                                  />
                                  
                                  {/* YouTube-Style Play Button Overlay */}
                                  <div className="absolute inset-0 flex items-center justify-center bg-black/20 hover:bg-black/40 transition-all duration-300 cursor-pointer opacity-0 group-hover:opacity-100"
                                       onClick={(e) => {
                                         const video = e.currentTarget.previousElementSibling as HTMLVideoElement;
                                         if (video && video.tagName === 'VIDEO') {
                                           if (video.paused) {
                                             video.play().catch(err => {
                                               console.log('Video autoplay prevented:', err);
                                               toast.info('Click the video controls to play');
                                             });
                                           } else {
                                             video.pause();
                                           }
                                         }
                                       }}>
                                    <div className="bg-white/20 backdrop-blur-sm rounded-full p-4 hover:bg-white/30 hover:scale-110 transition-all duration-200 border border-white/30">
                                      <svg className="w-8 h-8 text-white" fill="currentColor" viewBox="0 0 20 20">
                                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clipRule="evenodd" />
                                      </svg>
                                    </div>
                                  </div>
                                  
                                  {/* Video Status Indicators */}
                                  <div className="absolute top-2 right-2 bg-black/70 text-white text-xs px-2 py-1 rounded-full flex items-center gap-1">
                                    <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                                    <span>Local</span>
                                  </div>
                                  
                                  <div className="absolute bottom-2 left-2 bg-black/70 text-white text-xs px-2 py-1 rounded-full">
                                    🎬 AI Generated
                                  </div>
                                </div>
                              )}
                            </div>
                          )}

                          {/* Visual Content Placeholder (when not generated yet) */}
                          {(column.id === 'text-image' || column.id === 'text-video') && !post.content.imageUrl && !post.content.videoUrl && (
                            <div className="mb-4 p-6 bg-gray-800/50 border border-gray-600 rounded-lg text-center">
                              <div className="text-3xl mb-2">
                                {column.id === 'text-image' ? '🖼️' : '🎬'}
                              </div>
                              <p className="text-sm text-gray-400 mb-1">
                                {column.isGenerating ? 
                                  (column.id === 'text-image' ? 'Image generation in progress...' : 'Video generation in progress...') :
                                  (column.id === 'text-image' ? 'Image generation complete' : 'Video generation complete')
                                }
                              </p>
                              <p className="text-xs text-gray-500">
                                {column.isGenerating ? 
                                  'Visual content will appear here when generation completes' :
                                  'Use "Regenerate All" button above to refresh visuals'
                                }
                              </p>
                            </div>
                          )}

                          {/* Post Content */}
                          <div className="mb-4">
                            <p className="text-gray-300 leading-relaxed text-sm break-words whitespace-pre-wrap">
                              {post.content.text}
                            </p>
                            
                            {/* URL Display for text+url posts */}
                            {post.content.productUrl && (
                              <div className="mt-3 p-3 bg-blue-500/10 border border-blue-500/20 rounded-lg">
                                <div className="flex items-center gap-2 mb-1">
                                  <ExternalLink className="text-blue-400" size={14} />
                                  <span className="text-xs font-medium text-blue-400">See More</span>
                                </div>
                                <a 
                                  href={post.content.productUrl} 
                                  target="_blank" 
                                  rel="noopener noreferrer"
                                  className="text-blue-300 hover:text-blue-200 text-xs break-all underline"
                                >
                                  {post.content.productUrl}
                                </a>
                              </div>
                            )}
                          </div>

                          {/* Hashtags */}
                          {post.content.hashtags && post.content.hashtags.length > 0 && (
                            <div className="mb-4">
                              <div className="flex flex-wrap gap-2">
                                {post.content.hashtags.slice(0, 6).map((tag, tagIdx) => (
                                  <span
                                    key={tagIdx}
                                    className="px-2 py-1 bg-blue-500/20 text-blue-300 rounded-full text-xs break-words"
                                  >
                                    {tag}
                                  </span>
                                ))}
                                {post.content.hashtags.length > 6 && (
                                  <span className="px-2 py-1 bg-gray-500/20 text-gray-400 rounded-full text-xs">
                                    +{post.content.hashtags.length - 6} more
                                  </span>
                                )}
                              </div>
                            </div>
                          )}
                          
                          {/* Post Actions */}
                          <div className="flex items-center justify-between pt-3 border-t border-white/10">
                            <div className="flex items-center gap-2 text-xs text-gray-400">
                              <span className="capitalize">{post.type.replace('_', ' + ')}</span>
                              {post.engagement_score && (
                                <>
                                  <span>•</span>
                                  <span>Score: {post.engagement_score.toFixed(1)}</span>
                                </>
                              )}
                            </div>
                            
                            <button
                              onClick={() => togglePostSelection(post.id)}
                              className={`p-2 rounded-lg transition-all duration-200 ${
                                selectedPosts.includes(post.id)
                                  ? 'bg-blue-500/30 text-blue-400'
                                  : 'bg-white/5 text-gray-400 hover:bg-white/10'
                              }`}
                              title={selectedPosts.includes(post.id) ? 'Remove from selection' : 'Add to selection'}
                            >
                              <Heart size={16} className={selectedPosts.includes(post.id) ? 'fill-current' : ''} />
                            </button>
                          </div>
                        </div>
                      ))
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Action Bar */}
          <div className="vvl-card p-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <span className="vvl-text-primary font-medium">
                  {selectedPosts.length} posts selected
                </span>
                {selectedPosts.length > 0 && (
                  <span className="text-sm vvl-text-secondary">
                    Ready for scheduling and publishing
                  </span>
                )}
              </div>
              
              <div className="flex items-center gap-3">
                <button
                  onClick={async () => {
                    setIsLoading(true);
                    try {
                      await Promise.all([
                        generateColumnPosts('text-only'),
                        generateColumnPosts('text-image'),
                        generateColumnPosts('text-video')
                      ]);
                      toast.success('All posts regenerated successfully!');
                    } catch (error) {
                      toast.error('Failed to regenerate posts');
                    } finally {
                      setIsLoading(false);
                    }
                  }}
                  disabled={isLoading}
                  className="vvl-button-secondary flex items-center gap-2"
                >
                  <RefreshCw size={16} className={isLoading ? 'animate-spin' : ''} />
                  {isLoading ? 'Generating...' : 'Regenerate All'}
                </button>
                
                <button
                  onClick={handleProceedToScheduling}
                  disabled={selectedPosts.length === 0}
                  className="vvl-button-primary flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <ArrowRight size={16} />
                  Proceed to Scheduling ({selectedPosts.length})
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default IdeationPage;

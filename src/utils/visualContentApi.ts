/**
 * Visual Content API Integration
 * Handles real API calls for image and video generation
 */

import { debug, info, warn, error } from './logger';

interface VisualContentRequest {
  social_posts: Array<{
    id: string;
    type: string;
    platform: string;
    content: {
      text: string;
      hashtags?: string[];
      image_prompt?: string;
      video_prompt?: string;
    };
  }>;
  business_context: any;
  campaign_objective?: string;
  target_platforms?: string[];
  campaign_guidance?: any;
}

interface VisualContentResponse {
  posts_with_visuals: Array<{
    id: string;
    type: string;
    content: {
      text: string;
      hashtags?: string[];
      imageUrl?: string;
      videoUrl?: string;
      image_prompt?: string;
      video_prompt?: string;
    };
  }>;
  visual_strategy: any;
  generation_metadata: any;
}

export class VisualContentAPI {
  private static baseUrl = '/api/v1/content';

  static async generateVisualContent(request: VisualContentRequest): Promise<VisualContentResponse | null> {
    try {
      info('🎨 Starting visual content generation API call', { postsCount: request.social_posts.length });
      
      const response = await fetch(`${this.baseUrl}/generate-visuals`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        throw new Error(`Visual generation API failed: ${response.status} ${response.statusText}`);
      }

      const result = await response.json();
      
      info('✅ Visual content generation completed successfully', { 
        generatedImages: result.posts_with_visuals?.filter((p: any) => p.content.imageUrl).length || 0,
        generatedVideos: result.posts_with_visuals?.filter((p: any) => p.content.videoUrl).length || 0
      });

      return result;
      
    } catch (err: any) {
      error('❌ Visual content generation failed', { error: err.message });
      return null;
    }
  }

  static async generateVisualsForPosts(
    posts: any[],
    businessContext: any,
    campaignObjective: string = 'engagement'
  ): Promise<any[]> {
    try {
      // Transform posts to API format
      const socialPosts = posts.map(post => ({
        id: post.id,
        type: post.type,
        platform: post.platform,
        content: {
          text: post.content.text,
          hashtags: post.content.hashtags,
          image_prompt: post.content.text + " - Professional marketing image",
          video_prompt: post.content.text + " - Engaging marketing video"
        }
      }));

      const request: VisualContentRequest = {
        social_posts: socialPosts,
        business_context: businessContext,
        campaign_objective: campaignObjective,
        target_platforms: ['instagram', 'linkedin', 'twitter']
      };

      const result = await this.generateVisualContent(request);
      
      if (!result?.posts_with_visuals) {
        warn('⚠️ No visual content generated, returning original posts');
        return posts;
      }

      // Merge generated visuals back into original posts
      const updatedPosts = posts.map(post => {
        const generatedPost = result.posts_with_visuals.find(gp => gp.id === post.id);
        if (generatedPost) {
          return {
            ...post,
            content: {
              ...post.content,
              // Handle both snake_case (backend) and camelCase (frontend) formats
              imageUrl: generatedPost.content.imageUrl || 
                       generatedPost.content.image_url || 
                       (generatedPost as any).image_url || 
                       post.content.imageUrl,
              videoUrl: generatedPost.content.videoUrl || 
                       generatedPost.content.video_url || 
                       (generatedPost as any).video_url || 
                       post.content.videoUrl,
            }
          };
        }
        return post;
      });

      info('🔄 Merged visual content into posts', { 
        totalPosts: updatedPosts.length,
        postsWithImages: updatedPosts.filter(p => p.content.imageUrl).length,
        postsWithVideos: updatedPosts.filter(p => p.content.videoUrl).length
      });

      return updatedPosts;
      
    } catch (err: any) {
      error('❌ Visual content integration failed', { error: err.message });
      return posts; // Return original posts on error
    }
  }
}

export default VisualContentAPI;
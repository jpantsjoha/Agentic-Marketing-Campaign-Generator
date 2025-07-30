"""
FILENAME: __init__.py
DESCRIPTION/PURPOSE: Agents package initialization with ADK CLI compatibility
Author: JP + 2025-06-25
"""

from .business_analysis_agent import analyze_business_urls, URLAnalysisAgent
# Importing visual agents can fail in minimal test environments
try:
    from .visual_content_agent import generate_visual_content_for_posts, ImageGenerationAgent, VideoGenerationAgent, VisualContentOrchestrator
except Exception:  # pragma: no cover - optional dependency
    generate_visual_content_for_posts = None
    ImageGenerationAgent = None
    VideoGenerationAgent = None
    VisualContentOrchestrator = None
from .marketing_orchestrator import execute_campaign_workflow, create_marketing_orchestrator_agent

# ADK CLI compatibility - expose root_agent
try:
    from .agent import root_agent
    __all__ = [
        'analyze_business_urls', 
        'URLAnalysisAgent',
        'generate_visual_content_for_posts',
        'ImageGenerationAgent',
        'VideoGenerationAgent', 
        'VisualContentOrchestrator',
        'execute_campaign_workflow',
        'create_marketing_orchestrator_agent',
        'root_agent'  # ADK CLI compatibility
    ]
except ImportError as e:
    # Fallback if root_agent creation fails
    import logging
    logging.getLogger(__name__).warning(f"Could not import root_agent: {e}")
__all__ = [
    'analyze_business_urls', 
    'URLAnalysisAgent',
    'generate_visual_content_for_posts',
    'ImageGenerationAgent',
    'VideoGenerationAgent', 
    'VisualContentOrchestrator',
    'execute_campaign_workflow',
    'create_marketing_orchestrator_agent'
] 
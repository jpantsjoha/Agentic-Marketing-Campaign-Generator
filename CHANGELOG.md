# Changelog

All notable changes for the Phase 1 Enhanced Agents work compared to `main`.

## [Unreleased] - Proposed v1.1.0

- Backend
  - Added enhanced agent suite: `enhanced_marketing_orchestrator{,_v2}.py`, `enhanced_image_generation_agent.py`, `enhanced_video_generation_agent.py`, `enhanced_social_media_agent.py`, `trending_hashtag_agent.py`, and supporting services (`enhanced_memory_service.py`, messaging, models)
  - New API routes: `backend/api/routes/enhanced_campaigns.py`
  - Substantial test coverage: end-to-end, integration, regression, and validation tests
  - ADK upgrades and fixes (v1.6.1 → v1.8.0)
- Frontend
  - Major UI/UX improvements across Settings, Scheduling, Ideation pages
  - New API utilities for enhanced endpoints
  - Comprehensive UI tests and validation flows
- DevEx & Docs
  - Extensive design docs, ADRs, reference, and reports
  - Added `vercel.json` and `.env.production` (no secrets) with secure headers
  - Repository reorganization toward best practices

Notes:
- No secrets added; `.env.production` contains public `VITE_*` keys only
- Consider enabling analytics only with consent/CMP
- Recommend reviewing in logical commits/PRs if desired (backend, frontend, docs)
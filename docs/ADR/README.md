# Architecture Decision Records (ADR)

**Author: JP + 2025-06-15**
**Last Updated: 2025-01-30**

## Purpose

This folder contains Architecture Decision Records (ADRs) that document the significant architectural decisions made during the development of the AI Marketing Campaign Post Generator platform. Each ADR captures the context, decision, and consequences of important technical choices.

## ADR Format

Each ADR follows this structure:
- **Title**: Short descriptive title
- **Status**: Proposed, Accepted, Deprecated, Superseded
- **Context**: The situation that led to the decision
- **Decision**: The architectural decision made
- **Consequences**: The positive and negative outcomes

## Current ADRs Status Table

| ADR | Title | Status | Notes |
|-----|-------|--------|-------|
| [ADR-001](./ADR-001-technology-stack.md) | Technology Stack Selection | ✅ Accepted | Core tech stack |
| [ADR-002](./ADR-002-enhanced-campaign-creation.md) | Enhanced Campaign Creation Workflow | ✅ Accepted | Campaign UX |
| [ADR-003](./ADR-003-backend-adk-implementation.md) | Backend ADK Implementation Strategy | ✅ Accepted | ADK integration |
| [ADR-003B](./ADR-003-vvl-design-system-framework.md) | VVL Design System Framework | ✅ Accepted | UI framework |
| [ADR-004](./ADR-004-environment-variable-standardization.md) | Environment Variable Standardization | ✅ Accepted | Config management |
| [ADR-004B](./ADR-004-local-database-design.md) | Local Database Design for MVP | ✅ Accepted | Database schema |
| [ADR-005](./ADR-005-social-media-post-generation-enhancement.md) | Social Media Post Generation Enhancement | ✅ Accepted | Content generation |
| [ADR-009](./ADR-009-real-ai-analysis-implementation.md) | Real AI Analysis Implementation | ✅ Accepted | AI analysis |
| [ADR-010](./ADR-010-API-timeout-configuration.md) | API Timeout Configuration | ✅ Accepted | API reliability |
| [ADR-011](./ADR-011-near-live-testing-strategy.md) | Near-Live Testing Strategy | ✅ Accepted | Testing approach |
| [ADR-012](./ADR-012-campaign-content-caching-architecture.md) | Campaign Content Caching Architecture | ✅ Accepted | Performance |
| [ADR-013](./ADR-013-visual-content-file-storage.md) | Visual Content File Storage | ✅ Accepted | File management |
| [ADR-014](./ADR-014-video-content-generation-architecture.md) | Video Content Generation Architecture | ✅ Accepted | Video generation |
| [ADR-015](./ADR-015-real-video-file-storage-architecture.md) | Real Video File Storage Architecture | ✅ Accepted | Video storage |
| [ADR-016](./ADR-016-campaign-creative-guidance-validation.md) | Campaign Creative Guidance Validation | ✅ Accepted | Error handling |
| [ADR-017](./ADR-017-frontend-backend-api-data-transformation-strategy.md) | Frontend-Backend API Data Transformation | ❌ **Superseded** | **Replaced by ADR-018** |
| [ADR-018](./ADR-018-backend-camelcase-api-contract.md) | Backend CamelCase API Contract | 🟢 **Accepted** | **Current implementation** |
| [ADR-019](./ADR-019-agentic-visual-content-generation.md) | Agentic Visual Content Generation | ✅ Accepted | Multi-agent content |
| [ADR-020](./ADR-020-strict-llm-json-schema.md) | Strict LLM JSON Schema | ✅ Accepted | Data validation |
| [ADR-021](./ADR-021-async-visual-content-generation-architecture.md) | Async Visual Content Generation Architecture | ✅ Accepted | Performance optimization |
| [ADR-022](./ADR-022-event-driven-progress-updates.md) | Event-Driven Progress Updates | ✅ Accepted | Real-time UX |
| [ADR-023](./ADR-023-architectural-coherence-plan.md) | Architectural Coherence Plan | ✅ Accepted | System consistency |
| [ADR-024](./ADR-024-ai-development-commandments.md) | AI Development Commandments | ✅ Accepted | Development principles |
| [ADR-025](./ADR-025-api-structure-definition.md) | API Structure Definition | ✅ Accepted | API design standards |
| [ADR-026](./ADR-026-social-media-oauth-integration.md) | Social Media OAuth Integration | ✅ Accepted | Authentication strategy |
| [ADR-027](./ADR-027-visual-content-context-fidelity.md) | Visual Content Context Fidelity | ✅ Accepted | Content quality assurance |

## Architectural Evolution

### Data Contract Strategy Evolution
- **ADR-017** → **ADR-018**: Moved from frontend transformation to backend camelCase
- **Reason**: Frontend complexity and runtime errors with null/undefined values
- **Result**: Simpler, more robust data contract with backend responsibility

## Creating New ADRs

When making significant architectural decisions:
1. Copy the template from `ADR-template.md`
2. Number sequentially (ADR-XXX)
3. Fill in all sections thoroughly
4. Get team review before marking as "Accepted"
5. Update this README with the new ADR
6. If superseding an existing ADR, mark the old one as "Superseded" with cross-reference

## ADR Lifecycle

- **Proposed**: Initial draft, under discussion
- **Accepted**: Decision approved and implemented
- **Deprecated**: No longer recommended but still in use
- **Superseded**: Replaced by a newer ADR (cross-referenced)

## Legend

- ✅ **Accepted**: Currently implemented and active
- 🟢 **Current**: Most recent decision in this area
- ❌ **Superseded**: Replaced by newer ADR
- ⚠️ **Deprecated**: Still in use but not recommended 
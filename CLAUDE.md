# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# Overview
'video-venture-launch' is the intended solution codebase we're working with. All other folders on the same level as 'video-venture-launch' are for guidance and reference only.
The 'README.md' as located in the working folder 'video-venture-launch' is the solution we should be focusing on evolving, improving and taking into production.

'video-venture-launch' is intended to work locally (via makefiles) for local development, but in the eventual production release this should be working in a self contained container runtime. 

use Python3 and pip3 for run and install python app

ensure you're coding only in the 'video-venture-launch' - thats where all the solution code should reside. thats the github repo that houses the solution!

In production release, we would be hosting in Google Cloud Platform. Consider the appropriate and relevant GCP cloud native services to leverage for application to scale.

Ensure automation cloud infrastructure is deployed, and configured with the appropriate terraform IAC configuration, in line with best practices

We leverage 3 musketeers patterns to achieve local runtime, target configuration, testing and deploying to production cloud estate

Ensure you create and run lint and unit tests when creating or extending the functionality.

Create, Run and maintain appropriate UI tests to avoid regressing when additional functionality is implemented.

Review and update the documentation, when functionality is changed, or amended to ensure codebase is reflected with verbose documentation

Consult the User, and Business Logic, Solution Intent and HLD to ensure coherence and holistic solution architecture is implemented and extended as required, reducing silos

We are looking to build multi-agent Agentic AI solutions leveraging the latest Google ADK Framework v1.8+.

Recommend we commit, merge and release each atomic functional release along with Pull Request, so User can review and merge incremental improvements.

## Executive Leadership Intent and Strategic Direction

### CTO Vision: Technical Excellence Through Agentic AI Innovation
**Strategic Objectives:**
- **Revolutionary AI Architecture**: Build sophisticated multi-agent systems using Google ADK Framework v1.8+ that demonstrate technical leadership in agentic AI space
- **Production-Grade Quality**: Achieve enterprise-level technical maturity with 90%+ test coverage, comprehensive error handling, and scalable cloud-native architecture
- **ADK Framework Mastery**: Leverage latest ADK v1.8+ features, enhanced memory state, advanced Model Context Protocol (MCP) integration, and streaming capabilities
- **Technical Differentiation**: Create technical moat through sequential agent patterns, context-aware AI workflows, and autonomous visual content generation

### CEO Vision: Market Transformation Through AI-Powered Marketing Automation  
**Business Objectives:**
- **Democratize Professional Marketing**: Transform marketing workflow from days-to-minutes for technical teams and bootstrap organizations
- **Universal Problem Solution**: Address the "marketing bottleneck" that affects 90%+ of technical organizations globally
- **Freemium SaaS Evolution**: Build platform foundation supporting 1000+ users with 85%+ satisfaction targeting enterprise tiers and strategic partnerships
- **Market Leadership**: Establish as the definitive AI marketing automation platform for technical teams transitioning to market

### COO Vision: Operational Excellence and Scalable Growth Infrastructure
**Operational Objectives:**
- **Scalable Production Infrastructure**: Deploy Google Cloud Platform solution supporting concurrent user growth from MVP to enterprise scale
- **Quality Assurance Framework**: Implement comprehensive testing strategy (linting, unit, integration, E2E) ensuring 95%+ reliability and zero-downtime deployments
- **User Success Metrics**: Achieve <5 minute campaign creation time vs 2-5 days traditional, 60%+ campaign publishing success rate, and measurable ROI for users
- **Operational Efficiency**: Automated CI/CD pipelines, infrastructure-as-code (Terraform), and monitoring systems supporting rapid iteration and deployment

### Unified Strategic Intent: AI Marketing Revolution
**Shared Vision:**
Transform the fundamental workflow of marketing campaign creation through innovative agentic AI architecture, delivering professional-quality campaigns in minutes rather than days, while building a technically excellent, scalable platform that democratizes marketing for technical teams globally.

**Success Criteria:**
- Technical: Production-ready multi-agent system with real AI integration throughout workflow
- Business: 1000+ users with 85%+ satisfaction and clear path to enterprise monetization  
- Operational: <5 minute campaign creation with 95%+ system reliability and automated deployment

**Market Position:**
Establish as the premier AI-powered marketing automation platform for technical organizations, leveraging cutting-edge agentic AI architecture as a competitive moat while solving the universal "marketing bottleneck" problem.



## Repository Overview

This is the Google Agent Development Kit (ADK) Python samples repository containing ready-to-use sample agents built on top of the Python Agent Development Kit. 
The repository contains 15+ different agents covering various use cases from simple conversational bots to complex multi-agent workflows.

https://github.com/google/adk-python
https://github.com/google/adk-samples
https://google.github.io/adk-docs/
https://github.com/google/adk-web

## Common Development Commands

### Poetry-based Projects (Most Agents)
Most agents use Poetry for dependency management:

```bash
# Navigate to specific agent directory
cd agents/<agent-name>

# Install dependencies
poetry install

# Run agent with CLI
cd <agent_name>/  # Note: underscore in folder name
adk run .

# Run agent with Web UI
adk web .  # Run from agent root directory

# Run tests (if available)
pytest
```

### UV-based Projects (Newer Agents)
Some agents like `gemini-fullstack` and `software-bug-assistant` use UV:

```bash
# Install dependencies
uv sync

# For gemini-fullstack:
make install     # Installs both backend and frontend deps
make dev        # Runs both backend and frontend
make lint       # Runs linting tools
make playground # Runs web interface

# Backend only
make dev-backend  # uv run adk api_server app --allow_origins="*"

# Frontend only  
make dev-frontend  # npm --prefix frontend run dev
```

### Testing and Evaluation
Many agents include evaluation scripts:

```bash
# Run evaluations (from agent root)
python eval/test_eval.py

# Run unit tests
pytest tests/
```

## Architecture Patterns

### Agent Structure
All agents follow a consistent structure:
- **Single Agents**: Use `LlmAgent` or `Agent` classes directly
- **Multi-Agent Systems**: Use `SequentialAgent` for sequential workflows or `LoopAgent` for iterative processes
- **Sub-agents**: Organized in `sub_agents/` directories, each with `agent.py` and `prompt.py`

### Key Components
- **`agent.py`**: Core agent logic and configuration
- **`prompt.py`**: Agent instructions and prompts
- **`tools/`**: Custom tools for specific agent functionality
- **`shared_libraries/`**: Reusable utilities across sub-agents

### Common Patterns
- **SequentialAgent**: Linear workflow execution (e.g., llm-auditor: critic → reviser)
- **LoopAgent**: Iterative refinement (e.g., research evaluation loops)
- **AgentTool**: Calling sub-agents as tools
- **Callback Functions**: For state management and post-processing

## Environment Setup

### Required Environment Variables
Most agents require a `.env` file (copy from `.env.example`):
- `GOOGLE_CLOUD_PROJECT`: Your Google Cloud project ID
- `GOOGLE_CLOUD_LOCATION`: Typically "us-central1" 
- Model configuration variables (varies by agent)

### Google Cloud Setup
- Agents primarily use Vertex AI and Google Cloud services
- BigQuery integration common in data-focused agents
- Authentication via Google Cloud credentials

## Key Libraries and Dependencies

### Core ADK Dependencies
- **google-adk**: Core Agent Development Kit
- **google-cloud-aiplatform**: Vertex AI integration with ADK extensions
- **google-genai**: Gemini model integration

### Common Development Tools
- **Poetry**: Dependency management (most agents)
- **UV**: Modern Python dependency management (newer agents)
- **pytest**: Testing framework
- **black**: Code formatting
- **ruff**: Linting and code quality

## Testing Strategy

### Unit Tests
Located in `tests/` directory, typically test custom tools and utilities:
```bash
pytest tests/unit/
```

### Integration Tests
Some agents include integration tests for agent workflows:
```bash
pytest tests/test_agents.py
```

### Evaluation Framework
Most agents include evaluation scripts in `eval/`:
- Test data in `eval/data/` with `.test.json` files
- Evaluation scripts like `test_eval.py`
- Configuration in `test_config.json`

## Deployment

### Vertex AI Agent Engine
Many agents include deployment scripts:
```bash
cd deployment/
python deploy.py
```

### Local Development
Use ADK's built-in development tools:
- `adk run .` for CLI interaction
- `adk web .` for browser-based UI
- `adk api_server` for API server mode

## Agent-Specific Notes

### Multi-Agent Workflows
- **Data Science Agent**: Complex NL2SQL and data analysis pipeline
- **Academic Research**: Literature review and research synthesis
- **FOMC Research**: Financial analysis with multiple specialized sub-agents

### Specialized Integrations
- **Brand Search Optimization**: BigQuery integration for e-commerce data
- **Personalized Shopping**: Custom search engine and web interaction
- **Travel Concierge**: Complex multi-phase travel planning workflow

### Frontend Integration
- **Gemini Fullstack**: React frontend with FastAPI backend
- Custom UI components for agent interaction

## File Naming Conventions
- Agent directories: `kebab-case` (e.g., `llm-auditor`)
- Python packages: `snake_case` (e.g., `llm_auditor/`)
- This is due to Poetry's project structure requirements



## External MCP-Tools Used for Development and Testing

To ensure robust frontend validation, verification, and automated testing, the following external MCP-Tools are integrated into the TradingAlpha Signals Hub development workflow:

> **📋 Complete MCP Tools Documentation**: For comprehensive MCP tools configuration, including internal tools and troubleshooting, see [`mcp-tools/README.md`](./mcp-tools/README.md)

### 1. MCP-Selenium
- **Install Command:**
  ```sh
  npm install -g @angiejones/mcp-selenium
  ```
- **Purpose:** Enables advanced browser automation and UI validation using Selenium, supporting end-to-end testing and layout verification for the frontend.
- **Usage for Frontend Testing:**
  - Navigate to application pages (Home, Portfolio, Signals, etc.)
  - Validate page loading and component rendering
  - Test user interactions (clicks, form submissions, navigation)
  - Verify responsive design across different screen sizes
  - Validate trading panel functionality and mock data display
  - Test navigation between pages and component state persistence
- **Reference:** [MCP-Selenium GitHub](https://github.com/angiejones/mcp-selenium)

### 4. MCP-Playwright
- **Install Command:**
  ```sh
  npx '@playwright/mcp@latest'
  ```
- **Purpose:** Provides fast, reliable browser automation and cross-browser testing for frontend UI/UX validation, supporting both headless and headed modes.
- **Reference:** [Playwright MCP Claude Code](https://til.simonwillison.net/claude-code/playwright-mcp-claude-code)

## 🔧 ENGINEERING STANDARDS

### Test before Commiting and Pushing to Git. 
1. Selenium test validate the visual functionality by codifying the necessary test (and saving against future regression)
2. When Testing, take UI snapshots to assess visual compliance with expected UX requirement, fix or adjustment.


# Validating Successful outcomes
Be Critical. Do not assume working successful outcome unless you have concrete QA Data to provide evidence.
- Review the completed task to ensure it achieves the task towards the overarching business and technical objective. Advise if there is delta or deviation from the Business Intent or Technical Roadmap.
- Ensure you run tests via Selenium MCP, Playwright, unit tests and ESlints. Visually validate the intended behaviour as well.
- Validate the Local runtime, Then Deploy to Dev Environment for user to validate.
- Once confirmed successful, Then Commit and Push changes to remote repo and release to Production.
- Update the Completed tasks against the TODO/Roadmap activities and perform self-evaluation, self-assessment how far revised Implementation scores against Completeness and Release maturity, targetting MVP, Stage and Production Environments (out of 100 score)

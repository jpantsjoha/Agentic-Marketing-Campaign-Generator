# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# Overview
'video-venture-launch' is the intended solution codebase we're working with. All other folders on the same level as 'video-venture-launch' are forr guidance and reference only.
The 'README.md' as localed in the working folder 'video-venture-launch' is the solution we should be focusing on evolving, improving and taking into production.

'video-venture-launch' is intended to work locally (via makefiles) for local development, but in the eventual production release this should be working in a self contained container runtime. 

use Python3 and pip3 for run and install python app

ensure you're coding only in the 'video-venture-launch' - thats where all the solution code should reside. thats the github repo that houses the solution!

In production release, we would be hosting in Google Cloud Platform. Consider the approrpiate and relevant GCP cloud native services to leverage for application to scale.

Ensure automation cloud infrastructure is deployed, and configured with the appropriate terraform IAC configuration, in line with best practices

We leverage 3 musketeers patterns to achieve local runtime, target configuration, testing and deploying to produciton cloud estate

Ensure you create and run lint and unit tests when creating or extending the functionality.

Create, Run and maintain appropriate UI tests to avoid regressing when additional functionality is implemented.

Review and update the documentation, when functionality is changed, or amended to ensure codebase is reflected with verbose documentation

Consult the User, and Business Logic, Solution Intent and HLD to ensure coherence and holistic solution arhictecture is implemented and extended as required, reducing silos

We are looking to build multi-agent Agentic AI solutions leveraging the appropriate Google ADK Framework.

Recommend we commit, merge and release each atomic functional release along with Pull Request, so User can review and merge incremental improvements.



## Repository Overview

This is the Google Agent Development Kit (ADK) Python samples repository containing ready-to-use sample agents built on top of the Python Agent Development Kit. 
The repository contains 15+ different agents covering various use cases from simple conversational bots to complex multi-agent workflows.

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
# Resume Tailorator - GitHub Copilot Instructions

## Project Overview
Resume Tailorator is a multi-agent AI system that analyzes job postings and tailors resumes to match specific job requirements while maintaining authenticity and avoiding AI-generated clichés.

## Core Architecture

### Agent-Based Workflow
The system uses a sequential multi-agent pipeline:
1. **Scraper Agent** - Fetches job posting content
2. **Analyst Agent** - Extracts structured job requirements
3. **Resume Parser Agent** - Parses Markdown resumes into structured data
4. **Writer Agent** - Tailors CV to match job requirements
5. **Auditor Agent** - Validates for hallucinations and AI clichés
6. **Reviewer Agent** - Provides quality feedback and improvement suggestions
7. **Cover Letter Writer Agent** - Generates authentic cover letters

### Technology Stack
- **Framework**: `pydantic-ai` for agent orchestration
- **LLM**: OpenAI GPT-4o-mini (`MODLE_NAME = "openai:gpt-5-mini"`)
- **Models**: Pydantic v2 for structured outputs
- **Tools**: Playwright for web scraping

## Coding Guidelines

### Agent Development
- All agents must use structured `output_type` from `models.agents.output`
- Include `retries=3` for all agents
- System prompts must be explicit about avoiding AI clichés
- Always validate that agents don't hallucinate information

### Data Models
- Use Pydantic v2 models for all structured data
- Models must be defined in `models/agents/output.py`
- Key models: `JobAnalysis`, `CV`, `AuditResult`, `ReviewResult`

### Anti-Hallucination Rules
When writing or modifying agents:
- **NEVER** invent skills, experiences, or qualifications
- **ONLY** rephrase existing content from original CV
- Include explicit validation checks in auditor
- Score hallucinations: 0 = perfect, 10 = severe

### AI Cliché Blacklist
Avoid these terms in generated content:
- "orchestrated", "spearheaded", "leveraged"
- "synergy", "tapestry", "dynamic"
- "innovative", "cutting-edge", "game-changer"
- "passion for", "excited to bring"

### File Organization
- Agents: `workflows/agents.py`
- Data models: `models/agents/output.py`
- Tools: `tools/`
- Workflow orchestration: `models/workflow.py`
- Output files: `files/` directory

### Testing
- Integration tests: `test_reviewer_integration.py`
- Parsing tests: `test_resume_parsing.py`
- Use demo files from `files/` for testing

## Code Style

### Python Standards
- Use type hints for all function parameters and returns
- Follow PEP 8 naming conventions
- Use descriptive variable names (avoid abbreviations)
- Document complex logic with inline comments

### Agent System Prompts
- Start with role definition: "You are a [role]"
- List explicit rules numbered 1, 2, 3...
- Include CRITICAL/IMPORTANT sections for key requirements
- Define clear pass/fail criteria where applicable

### Error Handling
- All agents have built-in retry mechanism (retries=3)
- Handle file I/O errors explicitly
- Validate structured outputs before passing between agents

## Common Tasks

### Adding a New Agent
1. Define output model in `models/agents/output.py`
2. Create agent in `workflows/agents.py` with clear system prompt
3. Add agent to workflow in `models/workflow.py`
4. Write integration tests

### Modifying Agent Behavior
- Update system prompt rules
- Test with real job postings from `files/`
- Run auditor agent to validate output quality

### Testing Resume Parsing
- Use Markdown files from `files/` directory
- Verify structured `CV` object contains all original information
- Ensure no data loss during parsing

## Key Principles

1. **Authenticity First**: Generated content must sound human, not AI-generated
2. **No Hallucinations**: Never add information not present in original CV
3. **ATS Optimization**: Incorporate keywords naturally while maintaining readability
4. **Quality Over Quantity**: Better to highlight relevant experience than pad with fluff
5. **Validation Pipeline**: Every output passes through auditor and reviewer checks

## Dependencies
- `pydantic-ai`: Agent framework
- `pydantic`: Data validation
- `playwright`: Web scraping
- `uv`: Python packaging and environment management
- See `pyproject.toml` for full dependency list

# AI-Powered Resume Tailoring System

A multi-agent AI system that automatically analyzes job postings and tailors your resume to match specific job requirements while maintaining accuracy and avoiding AI-generated clichés.

## Overview

This project uses a pipeline of specialized AI agents to:
1. **Scrape & Analyze** job postings to extract key requirements
2. **Rewrite** your resume to target those requirements
3. **Audit** the generated resume for hallucinations and AI-speak
4. **Validate** that no false claims were added

## Features

- 🕷️ **Automated Job Scraping** - Uses Playwright to fetch job posting content
- 🧠 **Multi-Agent Architecture** - Specialized agents for analysis, writing, and auditing
- 🎯 **ATS Optimization** - Identifies and targets keywords for Applicant Tracking Systems
- ✅ **Hallucination Detection** - Ensures no fake skills or experience are added
- 🚫 **AI Cliché Filter** - Detects and removes robotic AI-generated language
- 🔄 **Automatic Retries** - Built-in retry logic for reliability
- 🔁 **Self-Correcting Loop** - Writer automatically fixes issues based on auditor feedback (up to 3 attempts)

## Architecture

The system uses 3 specialized AI agents:

1. **Analyst Agent** - Extracts structured data from job postings
2. **Writer Agent** - Tailors your resume to match job requirements
3. **Auditor Agent** - Validates accuracy and quality

## Requirements

- Python 3.8+
- Playwright (for web scraping)
- Ollama (running locally with `gpt-oss:20b` model)
- Pydantic AI

## Installation

```bash
# Install dependencies
pip install pydantic-ai playwright html2text

# Install Playwright browsers
playwright install chromium
```

## Usage

1. **Prepare your resume** as `resume.md` in Markdown format

2. **Update the job URL** in `main.py`:
   ```python
   job_url = "https://example.com/job-posting"
   ```

3. **Run the pipeline**:
   ```bash
   python main.py
   ```

4. **Review the output**:
   - Check the audit report in the console
   - If passed, find your tailored resume in `tailored_resume.md`

## Configuration

### Model Selection
Change the model by updating `MODLE_NAME`:
```python
MODLE_NAME = "ollama:gpt-oss:20b"  # Or any compatible model
```

### Retry Attempts
Adjust retry behavior:
```python
MAX_RETRIES = 3  # Number of retry attempts
```

## Output Structure

The generated resume includes:
- **Summary** - Tailored to the job description
- **Skills** - Highlighted relevant technical and soft skills
- **Experience** - Rephrased to match job keywords
- **Education** - Preserved from original resume

## Audit System

The auditor checks for:
- **Hallucinations** (Score: 0-10) - Fabricated skills or experience
- **AI Clichés** (Score: 0-10) - Robotic language patterns
- **Critical Issues** - False claims that would disqualify the resume
- **Minor Issues** - Style improvements

### Feedback Loop

If the audit fails, the system automatically:
1. Extracts all issues and suggestions from the audit report
2. Sends the feedback back to the writer agent
3. Requests a corrected version with strict instructions to fix the issues
4. Re-audits the new version
5. Repeats up to 3 times until the CV passes or max attempts reached

This ensures that common issues like:
- Adding skills not in the original CV
- Omitting important original skills
- Missing job requirements
- Using AI clichés

...are automatically corrected without manual intervention.

## Example Workflow

```
🚀 STARTING MULTI-AGENT PIPELINE

🤖 Agent 1 (Analyst): Reading job post...
   [Tool] 🕷️ Scraping https://job-boards.greenhouse.io/...
   ✅ Job Analyzed: Senior Backend Engineer at ClickHouse
   🎯 Keywords found: ['Python', 'Kubernetes', 'Docker', ...]

🤖 Agent 2 (Writer): Tailoring CV (Attempt 1/3)...
   ✅ CV Drafted. Summary: Experienced backend engineer...

🤖 Agent 3 (Auditor): Validating for hallucinations and AI-speak...
   ⚠️ Audit failed on attempt 1
   🔄 Will retry with feedback...

🤖 Agent 2 (Writer): Tailoring CV (Attempt 2/3)...
   🔄 Retrying with audit feedback...
   ✅ CV Drafted. Summary: Backend engineer with expertise...

🤖 Agent 3 (Auditor): Validating for hallucinations and AI-speak...
   ✅ Audit passed on attempt 2!

==============================
📋 FINAL AUDIT REPORT
==============================
Passed: True
Hallucination Score (0 is best): 0
AI Cliché Score (0 is best): 2
Feedback: Resume effectively targets job requirements...

✅ Audit Passed. Saving CV...
```

## Safety Features

- ✅ Never invents experience or skills
- ✅ Only rephrases existing content
- ✅ Flags AI-generated language
- ✅ Requires audit approval before saving

## Limitations

- Requires Ollama running locally
- Limited to 20,000 characters of scraped content
- May need manual review for complex job postings

## Future Improvements

- [ ] CLI argument support for job URL and resume path
- [ ] Support for multiple LLM providers
- [ ] PDF resume generation
- [ ] Batch processing for multiple jobs
- [ ] Web interface

## License

[Your License Here]

## Contributing

Contributions welcome! Please open an issue or PR.
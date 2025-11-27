import asyncio
import os
import sys
from typing import List

import html2text
from playwright.async_api import async_playwright
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext, AgentRunResult

MODLE_NAME = "ollama:gpt-oss:20b"
MAX_RETRIES = 3

# ==========================================
# 1. DATA MODELS (The "Protocol")
# ==========================================


# --- Model for the Job Analysis ---
class JobAnalysis(BaseModel):
    job_title: str
    company_name: str
    summary: str = Field(
        description="A concise summary of what the role actually entails."
    )
    hard_skills: List[str] = Field(description="Technical skills explicitly required.")
    soft_skills: List[str] = Field(
        description="Cultural or behavioral traits required."
    )
    key_responsibilities: List[str] = Field(description="The top 3-5 main duties.")
    keywords_to_target: List[str] = Field(
        description="Specific ATS keywords found in the text."
    )


# --- Model for the CV ---
class WorkExperience(BaseModel):
    company: str
    role: str
    dates: str
    highlights: List[str] = Field(description="Bullet points of achievements.")


class CV(BaseModel):
    full_name: str
    summary: str
    skills: List[str]
    experience: List[WorkExperience]
    education: List[str]


# --- Model for the Audit/Validation ---
class AuditIssue(BaseModel):
    severity: str = Field(description="'Critical' for lies, 'Minor' for style.")
    issue: str
    suggestion: str


class AuditResult(BaseModel):
    passed: bool
    hallucination_score: int = Field(description="0-10. 0 means no hallucinations.")
    ai_cliche_score: int = Field(description="0-10. 10 means it sounds very robotic.")
    issues: List[AuditIssue]
    feedback_summary: str


# ==========================================
# 2. THE PLAYWRIGHT MCP TOOL
# ==========================================


async def fetch_job_content(ctx: RunContext, url: str) -> str:
    """
    MCP Tool: Navigates to a URL and extracts the main text content as Markdown.
    """
    print(f"   [Tool] 🕷️ Scraping {url}...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        try:
            await page.goto(url, timeout=30000)
            content = await page.content()
            print(f"   [Tool] ✅ Scraped content from {url}")
            with open("./scraped_content.html", "w", encoding="utf-8") as f:
                f.write(content)

            # Convert to Markdown to strip noise
            h = html2text.HTML2Text()
            h.ignore_links = True
            h.ignore_images = True
            h.body_width = 0
            return h.handle(content)[:20000]  # Limit context
        except Exception as e:
            return f"Error scraping: {e}"
        finally:
            await browser.close()


# ==========================================
# 3. THE AGENTS
# ==========================================

# --- Agent 0: The Scraper ---
# Responsibility: Fetch the job posting content.
scraper_agent = Agent(
    MODLE_NAME,
    system_prompt="""
    You are an expert Technical Recruiter.
    Your job is to analyze a raw job posting and extract structured data.
    Identify the core requirements, not just the 'nice to haves'.
    Look for 'hidden' keywords that ATS systems might scan for.
    """,
    output_type=JobAnalysis,
    tools=[fetch_job_content],
    retries=3,
)

# --- Agent 1: The Job Analyst ---
# Responsibility: Turn raw HTML into a structured JobAnalysis object.
analyst_agent = Agent(
    MODLE_NAME,
    system_prompt="""
    You are an expert Technical Recruiter.
    Your job is to analyze a raw job posting and extract structured data.
    Identify the core requirements, not just the 'nice to haves'.
    Look for 'hidden' keywords that ATS systems might scan for.
    """,
    output_type=JobAnalysis,
    tools=[fetch_job_content],
)

# --- Agent 2: The Writer ---
# Responsibility: Rewrite the CV based on the Analysis.
writer_agent = Agent(
    MODLE_NAME,
    system_prompt="""
    You are a Senior Resume Writer.
    Input: A User's Original CV and a Job Analysis in Markdown format.
    Task: Rewrite the CV to target the Job Analysis.

    RULES:
    1. Do NOT invent experience. If the user lacks a skill, do not add it.
    2. Rephrase existing bullets to use the keywords from the Job Analysis.
    3. Use active voice.
    4. Do not use flowery AI language (e.g., 'Orchestrated', 'Tapestry').
    """,
    output_type=CV,
    retries=3,
)

# --- Agent 3: The Auditor ---
# Responsibility: Compare Original vs New to catch lies and AI-speak.
auditor_agent = Agent(
    MODLE_NAME,
    system_prompt="""
    You are a strict Compliance Auditor.
    Input: Original CV, New CV, and Job Analysis.

    Task:
    1. Check for Hallucinations: Did the New CV add skills/companies not in the Original? (CRITICAL FAIL)
    2. Check for AI Cliches: Does it sound like ChatGPT wrote it?
    3. Check for Relevance: Did the writer actually target the job?

    Return a structured Audit Result.
    """,
    output_type=AuditResult,
    retries=3,
)

# ==========================================
# 4. ORCHESTRATION LOGIC
# ==========================================


async def main():
    # --- Inputs ---
    # TODO: Pass the job URL as CLI argument.
    job_url = "https://job-boards.greenhouse.io/clickhouse/jobs/5585335004"  # Example
    resume_file_path = os.path.join(os.getcwd(), "resume.md")
    original_cv_text: str = ""

    # Reading the original CV from the file
    # ASSUME: This is markdown file.
    # TODO: Pass the file as a CLI argument.
    try:
        with open(resume_file_path, "r", encoding="utf-8") as f:
            original_cv_text = f.read()
    except FileNotFoundError:
        print(
            f"⚠️ Resume file not found at {resume_file_path}. Continuing with empty resume."
        )
        original_cv_text = ""
    except Exception as e:
        print(f"⚠️ Error reading resume file: {e}")
        original_cv_text = ""

    print("🚀 STARTING MULTI-AGENT PIPELINE\n")

    # --- STEP 1: ANALYZE JOB (Agent 1) ---
    print("🤖 Agent 1 (Analyst): Reading job post...")
    job_analysis_result: AgentRunResult[JobAnalysis] | None = None
    for attempt in range(MAX_RETRIES):
        try:
            job_analysis_result = await analyst_agent.run(
                f"Analyze the job posting at this URL: {job_url}"
            )

            print(f"   [Debug] Job Data: {job_analysis_result.output}")

            if job_analysis_result.output is None:
                raise ValueError("Job analysis data is None")

            if (
                job_analysis_result.output.job_title
                and job_analysis_result.output.company_name
            ):
                break  # Success

            print(
                f"⚠️ Attempt {attempt + 1}/{MAX_RETRIES}: Incomplete job data, retrying..."
            )

        except Exception as e:
            print(f"⚠️ Attempt {attempt + 1}/{MAX_RETRIES} failed: {e}")
            if attempt == MAX_RETRIES - 1:
                sys.exit("❌ Failed to get complete job analysis after retries.")

    print(
        f"   ✅ Job Analyzed: {job_analysis_result.output.job_title} at {job_analysis_result.output.company_name}"
    )
    print(f"   🎯 Keywords found: {job_analysis_result.output.keywords_to_target}\n")

    # Prepare a JSON/string representation of the job data for prompts
    job_data_json = JobAnalysis.model_dump(job_analysis_result.output)

    # --- STEP 2: WRITE CV (Agent 2) ---
    print("🤖 Agent 2 (Writer): Tailoring CV...")
    print("   [Debug] Original CV Text Length:", len(original_cv_text))
    writer_prompt = f"""
    Here is the Job Analysis:
    {job_data_json}

    Here is the Original CV:
    {original_cv_text}

    Rewrite the CV to match the Job Analysis.
    """
    writer_result = await writer_agent.run(writer_prompt)

    new_cv = writer_result.output or None
    if new_cv is None:
        sys.exit("❌ Failed to get new CV data from agent.")

    print(f"   ✅ CV Drafted. Summary: {new_cv.summary}...\n")

    # For auditor prompt, prepare serializations
    new_cv_json = (
        new_cv.model_dump_json() if hasattr(new_cv, "model_dump_json") else str(new_cv)
    )

    # --- STEP 3: AUDIT (Agent 3) ---
    print("🤖 Agent 3 (Auditor): Validating for hallucinations and AI-speak...")
    audit_prompt = f"""
    ORIGINAL CV:
    {original_cv_text}

    NEW GENERATED CV:
    {new_cv_json}

    JOB REQUIREMENTS:
    {job_data_json}
    """
    audit_result = await auditor_agent.run(audit_prompt)

    audit = audit_result.output or None
    if audit is None:
        audit = audit_result

    # --- REPORTING ---
    print("\n" + "=" * 30)
    print("📋 FINAL AUDIT REPORT")
    print("=" * 30)

    passed = getattr(audit, "passed", None)
    hallucination_score = getattr(audit, "hallucination_score", None)
    ai_cliche_score = getattr(audit, "ai_cliche_score", None)
    feedback_summary = getattr(audit, "feedback_summary", "")

    print(f"Passed: {passed}")
    print(f"Hallucination Score (0 is best): {hallucination_score}")
    print(f"AI Cliche Score (0 is best): {ai_cliche_score}")
    print(f"Feedback: {feedback_summary}")

    issues = getattr(audit, "issues", []) or []
    if issues:
        print("\n⚠️ Issues Found:")
        for i in issues:
            sev = getattr(i, "severity", "Unknown")
            issue_text = getattr(i, "issue", str(i))
            suggestion = getattr(i, "suggestion", "")
            print(f" - [{sev}] {issue_text} -> {suggestion}")

    # If passed, save the file
    if passed:
        print("\n✅ Audit Passed. Saving CV...")
        output_path = os.path.join(os.getcwd(), "tailored_resume.md")
        with open(output_path, "w", encoding="utf-8") as f:
            # Simple markdown serialization
            f.write(f"# {new_cv.full_name}\n\n")
            f.write(f"## Summary\n{new_cv.summary}\n\n")
            f.write("## Skills\n")
            for skill in new_cv.skills:
                f.write(f"- {skill}\n")
            f.write("\n## Experience\n")
            for exp in new_cv.experience:
                f.write(f"### {exp.role} at {exp.company} ({exp.dates})\n")
                for hl in exp.highlights:
                    f.write(f"- {hl}\n")
                f.write("\n")
            f.write("## Education\n")
            for edu in new_cv.education:
                f.write(f"- {edu}\n")
    else:
        print("\n❌ Audit Failed. Please refine inputs.")


if __name__ == "__main__":
    asyncio.run(main())

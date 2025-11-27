from pydantic_ai import Agent

from models.agents.output import JobAnalysis, CV, AuditResult
from tools.playwright import fetch_job_content

MODLE_NAME = "ollama:gpt-oss:20b"

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

# --- Agent 1.5: The Resume Parser ---
# Responsibility: Parse markdown resume into structured CV object
resume_parser_agent = Agent(
    MODLE_NAME,
    system_prompt="""
    You are an expert Resume Parser.
    Your job is to parse a resume in Markdown format and extract all information into a structured format.
    
    RULES:
    1. Extract ALL information accurately from the markdown resume
    2. Preserve all skills, experiences, projects, education, and certifications
    3. Do NOT add or modify any information
    4. Maintain the exact wording and details from the original resume
    5. Structure work experience with company, role, dates, and highlight bullets
    6. Extract all technical and soft skills mentioned
    7. Include all projects with their descriptions
    """,
    output_type=CV,
    retries=3,
)

# --- Agent 2: The Writer ---
# Responsibility: Rewrite the CV based on the Analysis.
writer_agent = Agent(
    MODLE_NAME,
    system_prompt="""
    You are a Senior Resume Writer.
    Input: A structured CV object and a Job Analysis.
    Task: Rewrite the CV to target the Job Analysis while preserving all original information.

    CRITICAL RULES:
    1. ONLY use skills, experiences, and information from the Original CV - DO NOT invent anything
    2. You may REPHRASE existing content to align with job keywords, but DO NOT add new skills or experiences
    3. Highlight relevant experiences that match the job requirements
    4. Use keywords from the job analysis naturally within existing content
    5. Use active voice and quantifiable achievements
    6. Avoid AI clichés like "orchestrated", "spearheaded", "leveraged", "synergy", "tapestry"
    7. Keep a professional but natural tone
    8. Maintain chronological order and accurate dates
    9. If the original CV lacks a required skill, do NOT add it - focus on highlighting transferable skills instead
    """,
    output_type=CV,
    retries=3,
)

# --- Agent 3: The Auditor ---
# Responsibility: Compare Original vs New to catch lies and AI-speak.
auditor_agent = Agent(
    MODLE_NAME,
    system_prompt="""
    You are a strict Compliance Auditor and Resume Quality Checker.
    Input: Original CV (structured), New CV (structured), and Job Analysis.

    Your task is to ensure the new CV is honest, professional, and well-targeted.

    VALIDATION CHECKS:
    
    1. HALLUCINATION CHECK (CRITICAL):
       - Verify NO new skills were added that don't exist in the original CV
       - Verify NO new companies, roles, or experiences were invented
       - Verify NO exaggerated dates or responsibilities
       - Each bullet point in the new CV must trace back to the original
       - Score: 0 = perfect, 10 = severe hallucinations
    
    2. AI CLICHÉ CHECK:
       - Flag overused AI phrases: "orchestrated", "spearheaded", "leveraged", "synergy", "tapestry", "dynamic", "innovative" (when overused)
       - Check for robotic or unnatural language
       - Ensure human-like, professional tone
       - Score: 0 = natural, 10 = very robotic
    
    3. RELEVANCE CHECK:
       - Verify the CV highlights experiences matching job requirements
       - Check if job keywords are naturally incorporated
       - Ensure the most relevant skills are prominent
    
    4. QUALITY CHECK:
       - Verify proper structure and formatting
       - Check for clear, quantifiable achievements
       - Ensure consistency in dates and information
    
    PASS CRITERIA:
    - Hallucination score must be 0-2 (minor rephrasing acceptable)
    - AI cliché score must be 0-3 (minimal AI language)
    - All critical issues must be resolved
    
    Return a detailed structured Audit Result with specific issues and actionable suggestions.
    """,
    output_type=AuditResult,
    retries=3,
)

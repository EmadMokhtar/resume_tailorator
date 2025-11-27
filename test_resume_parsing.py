"""
Test script to verify resume parsing improvements
"""

import asyncio
import os
from workflows.agents import resume_parser_agent


async def test_resume_parsing():
    """Test that the resume parser correctly extracts all information"""
    print("🧪 Testing Resume Parser Agent\n")

    # Read the resume
    resume_file_path = os.path.join(os.getcwd(), "resume.md")
    with open(resume_file_path, "r", encoding="utf-8") as f:
        resume_text = f.read()

    print(f"📄 Resume length: {len(resume_text)} characters\n")

    # Parse the resume
    print("🔍 Parsing resume...")
    result = await resume_parser_agent.run(
        f"Parse this resume into structured format:\n\n{resume_text}"
    )

    if result.output is None:
        print("❌ FAILED: Resume parsing returned None")
        return False

    cv = result.output

    # Validate the parsing
    print("\n✅ Resume parsed successfully!\n")
    print("=" * 50)
    print("PARSED DATA VALIDATION")
    print("=" * 50)

    print(f"\n👤 Full Name: {cv.full_name}")
    print(f"📧 Contact Info: {cv.contact_info}")
    print(f"\n📝 Summary: {cv.summary[:100]}...")

    print(f"\n🎯 Skills ({len(cv.skills)}):")
    for skill in cv.skills[:5]:
        print(f"   - {skill}")
    if len(cv.skills) > 5:
        print(f"   ... and {len(cv.skills) - 5} more")

    print(f"\n💼 Work Experience ({len(cv.experience)}):")
    for exp in cv.experience:
        print(f"   - {exp.role} at {exp.company} ({exp.dates})")
        print(f"     Highlights: {len(exp.highlights)} items")

    print(f"\n📚 Projects ({len(cv.projects)}):")
    for project in cv.projects[:2]:
        print(f"   - {project[:80]}...")

    print(f"\n🎓 Education ({len(cv.education)}):")
    for edu in cv.education:
        print(f"   - {edu}")

    print(f"\n🏆 Certifications ({len(cv.certifications)}):")
    for cert in cv.certifications[:5]:
        print(f"   - {cert}")
    if len(cv.certifications) > 5:
        print(f"   ... and {len(cv.certifications) - 5} more")

    print(f"\n📖 Publications ({len(cv.publications)}):")
    for pub in cv.publications:
        print(f"   - {pub}")

    # Validation checks
    print("\n" + "=" * 50)
    print("VALIDATION CHECKS")
    print("=" * 50)

    checks = {
        "Full name extracted": bool(cv.full_name and "Emad" in cv.full_name),
        "Contact info extracted": bool(cv.contact_info),
        "Summary extracted": bool(cv.summary and len(cv.summary) > 50),
        "Skills extracted (>10)": len(cv.skills) >= 10,
        "Experience extracted (>5)": len(cv.experience) >= 5,
        "Projects extracted": len(cv.projects) > 0,
        "Education extracted": len(cv.education) > 0,
        "Certifications extracted (>5)": len(cv.certifications) >= 5,
        "Publications extracted": len(cv.publications) > 0,
    }

    all_passed = True
    for check, passed in checks.items():
        status = "✅" if passed else "❌"
        print(f"{status} {check}")
        if not passed:
            all_passed = False

    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 ALL VALIDATION CHECKS PASSED!")
    else:
        print("⚠️ SOME VALIDATION CHECKS FAILED")
    print("=" * 50)

    return all_passed


if __name__ == "__main__":
    success = asyncio.run(test_resume_parsing())
    exit(0 if success else 1)

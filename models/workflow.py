from pydantic import BaseModel


class ResumeTailorResult(BaseModel):
    tailored_resume: str
    audit_report: dict
    passed: bool

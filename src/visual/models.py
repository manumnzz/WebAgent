from typing import Literal
from pydantic import BaseModel, Field


class BrowserFinding(BaseModel):
    code: str
    viewport: str
    detail: str
    blocking: bool = False


class Screenshot(BaseModel):
    name: str
    path: str
    width: int
    height: int


class CaptureReport(BaseModel):
    screenshots: list[Screenshot] = Field(default_factory=list)
    findings: list[BrowserFinding] = Field(default_factory=list)

    @property
    def blockers(self) -> int:
        return sum(f.blocking for f in self.findings)


class VisualIssue(BaseModel):
    severity: Literal["high", "medium", "low"]
    viewport: str
    target: str
    evidence: str
    correction: str
    acceptance: str


class VisualScores(BaseModel):
    identity: int = Field(ge=0, le=10)
    hierarchy: int = Field(ge=0, le=10)
    typography: int = Field(ge=0, le=10)
    composition: int = Field(ge=0, le=10)
    imagery: int = Field(ge=0, le=10)
    mobile: int = Field(ge=0, le=10)


class VisualReview(BaseModel):
    scores: VisualScores
    strengths: list[str]
    issues: list[VisualIssue] = Field(max_length=8)
    summary: str

    @property
    def score(self) -> float:
        values = self.scores.model_dump().values()
        return round(sum(values) / len(values) * 10, 1)

    @property
    def passed(self) -> bool:
        return min(self.scores.model_dump().values()) >= 8 and not any(
            issue.severity == "high" for issue in self.issues
        )

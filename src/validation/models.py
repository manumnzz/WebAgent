from pydantic import BaseModel

class ValidationIssue(BaseModel):
    code: str
    file: str | None = None
    message: str


class ValidationResult(BaseModel):
    is_valid: bool
    errors: list[ValidationIssue]
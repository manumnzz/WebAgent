from pydantic import BaseModel, Field

class ReviewData(BaseModel):
    author: str
    text: str
    rating: int = Field(
        ge=1,
        le=5,
    )
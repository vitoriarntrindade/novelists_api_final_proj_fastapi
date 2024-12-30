from typing import List, Optional

from pydantic import BaseModel, field_validator
from madrproject.books.models import Books

class NovelistSchema(BaseModel):
    name: str

    @field_validator('name')
    def sanitize_title(cls, v):
        return v.lower()
    books: Optional[List] = List

class NovelistPublicSchema(NovelistSchema):
    id: int

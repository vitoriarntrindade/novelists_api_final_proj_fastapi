from typing import List

from pydantic import BaseModel, field_validator


class BooksSchema(BaseModel):
    year: int
    title: str
    novelist_id: int

    @field_validator('title')
    def sanitize_title(cls, v):
        return v.lower()


class BookSchemaPublic(BooksSchema):
    id: int


class BookSchemaList(BaseModel):
    books: List[BookSchemaPublic]

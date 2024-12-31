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


class BookSchemaUpdate(BaseModel):
    year: int | None = None
    title: str | None = None
    novelist_id: int | None = None

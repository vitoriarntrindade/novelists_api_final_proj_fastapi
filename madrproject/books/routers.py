from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.future import select
from sqlalchemy.orm import Session

from madrproject.__init__ import *
from madrproject.books.schemas import BookSchemaPublic, BooksSchema
from madrproject.config.database import get_session

router = APIRouter(prefix='/books', tags=['books'])


@router.post('/', response_model=BookSchemaPublic, status_code=201)
def create_book(book: BooksSchema, session: Session = Depends(get_session)):
    stmt = select(Novelist).where(Novelist.id == book.novelist_id)
    result = session.execute(stmt).scalars().first()

    if not result:
        raise HTTPException(
            status_code=404,
            detail="Novelist ID not found."
        )

    new_book = Books(
        year=book.year,
        title=book.title,
        novelist_id=result.id
    )

    session.add(new_book)
    session.commit()
    session.refresh(new_book)

    return new_book

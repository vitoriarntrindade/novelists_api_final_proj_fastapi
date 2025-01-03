from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.future import select
from sqlalchemy.orm import Session

from madrproject.__init__ import *
from madrproject.books.schemas import (
    BookSchemaList,
    BookSchemaPublic,
    BookSchemaUpdate,
    BooksSchema,
)
from madrproject.config.database import get_session
from madrproject.config.security import get_current_account

router = APIRouter(prefix='/books', tags=['books'])


@router.post('/', response_model=BookSchemaPublic, status_code=201)
def create_book(book: BooksSchema, session: Session = Depends(get_session)):
    existing_novelist = (
        session.query(Novelist).filter(Novelist.id == book.novelist_id).first()
    )

    if not existing_novelist:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f'Novelist ID {book.novelist_id} was not found.',
        )

    existing_book = (
        session.query(Books).filter(Books.title == book.title).first()
    )

    if existing_book:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT, detail='Book already exists.'
        )

    new_book = Books(
        year=book.year, title=book.title, novelist_id=existing_novelist.id
    )

    session.add(new_book)
    session.commit()
    session.refresh(new_book)

    return new_book


@router.patch('/{book_id}', response_model=BookSchemaPublic, status_code=200)
def update_book(
    book: BookSchemaUpdate,
    book_id: int,
    session: Session = Depends(get_session),
    account: Account = Depends(get_current_account),
):
    book_db = session.query(Books).where(Books.id == book_id).first()

    if not book_db:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f'The book ID {book_id} was not found.',
        )

    for key, value in book.model_dump(exclude_unset=True).items():
        setattr(book_db, key, value)

    session.add(book_db)
    session.commit()
    session.refresh(book_db)

    return book_db


@router.get('/', response_model=BookSchemaList, status_code=HTTPStatus.OK)
def list_books(
    limit: int = 3,
    offset: int = 0,
    account: Account = Depends(get_current_account),
    session: Session = Depends(get_session),
    title: str | None = None,
    year: int | None = None,
):
    query = select(Books)

    if title:
        query.filter(Books.title.contains(title))

    if year:
        query = query.filter(Books.year == year)

    books = session.scalars(query.offset(offset).limit(limit)).all()

    return {'books': books}


@router.delete('/{book_id}', status_code=HTTPStatus.OK)
def delete_book(
    book_id: int,
    session: Session = Depends(get_session),
    account: Account = Depends(get_current_account),
):
    book_db = session.query(Books).filter(Books.id == book_id).first()

    if not book_db:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f'The book with ID {book_id} was not found.',
        )

    session.delete(book_db)
    session.commit()

    return {
        'message': 'The book was successfully deleted.',
        'book': {
            'id': book_db.id,
            'title': book_db.title,
            'year': book_db.year,
        },
    }

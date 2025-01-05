from http import HTTPStatus

from fastapi import APIRouter, HTTPException

from madrproject.books.repository import (
    BooksRepository,
)
from madrproject.books.schemas import (
    BookSchemaList,
    BookSchemaPublic,
    BookSchemaUpdate,
    BooksSchema,
)
from madrproject.config.dependencies import *

router = APIRouter(prefix='/book', tags=['book'])


@router.post(
    '/', response_model=BookSchemaPublic, status_code=HTTPStatus.CREATED
)
def create_book(
    book: BooksSchema, session: T_Session, account: T_CurrentAccount
):
    """
    Route to create a new book.

    Args:
        book (BooksSchema): Schema with book details.
        session (Session): Dependency for database session.

    Raises:
        HTTPException: If the novelist ID is not found.
        HTTPException: If a book with the same title already exists.

    Returns:
        BookSchemaPublic: The created book's details.
    """
    repository = BooksRepository(session)

    existing_novelist = repository.get_novelist_by_id(book.novelist_id)
    if not existing_novelist:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f'Novelist ID {book.novelist_id} was not found.',
        )

    existing_book = repository.get_book_by_title(book.title)
    if existing_book:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT, detail='Book already exists.'
        )

    return repository.create_book(book)


@router.patch(
    '/{book_id}', response_model=BookSchemaPublic, status_code=HTTPStatus.OK
)
def update_book(
    book: BookSchemaUpdate,
    book_id: int,
    session: T_Session,
    account: T_CurrentAccount,
):
    """
    Route to update an existing book.

    Args:
        book (BookSchemaUpdate): Schema with updated book details.
        book_id (int): ID of the book to update.
        session (Session): Dependency for database session.
        account (T_CurrentAccount): Current authenticated account.

    Raises:
        HTTPException: If the book ID is not found.

    Returns:
        BookSchemaPublic: The updated book's details.
    """
    repository = BooksRepository(session)

    book_db = repository.get_book_by_id(book_id)
    if not book_db:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f'The book ID {book_id} was not found.',
        )

    updated_book = repository.update_book(
        book_db, book.model_dump(exclude_unset=True)
    )
    return updated_book


@router.get('/', response_model=BookSchemaList, status_code=HTTPStatus.OK)
def list_books(
    session: T_Session,
    account: T_CurrentAccount,
    limit: int = 3,
    offset: int = 0,
    title: str = None,
    year: int = None,
):
    """
    Route to list books with optional filters.

    Args:
        limit (int): Maximum number of books to return. Default is 3.
        offset (int): Number of books to skip. Default is 0.
        title (str, optional): Filter by title. Default is None.
        year (int, optional): Filter by year. Default is None.
        session (Session): Dependency for database session.
        account (T_CurrentAccount): Current authenticated account.

    Returns:
        dict: A list of books.
    """
    repository = BooksRepository(session)
    books = repository.list_books(limit, offset, title, year)
    return {'books': books}


@router.delete('/{book_id}', status_code=HTTPStatus.OK)
def delete_book(book_id: int, session: T_Session, account: T_CurrentAccount):
    """
    Route to delete a book by ID.

    Args:
        book_id (int): ID of the book to delete.
        session (Session): Dependency for database session.

    Raises:
        HTTPException: If the book ID is not found.
    """
    repository = BooksRepository(session)

    book_db = repository.get_book_by_id(book_id)
    if not book_db:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f'The book ID {book_id} was not found.',
        )

    repository.delete_book(book_db)

    return {}

from typing import Sequence, Type

from sqlalchemy.future import select
from sqlalchemy.orm import Session

from madrproject.books.models import Books
from madrproject.novelists.models import Novelist


class BooksRepository:
    """
    Repository class for managing books in the database.
    """

    def __init__(self, session: Session):
        """
        Initializes the repository with a database session.

        Args:
            session (Session): SQLAlchemy session for database interaction.
        """
        self.session = session

    def create_book(self, book: Books) -> Books:
        """
        Inserts a new book into the database.

        Args:
            book (Books): Book object to be added.

        Returns:
            Books: The created book object.
        """
        new_book = Books(
            year=book.year,
            title=book.title,
            novelist_id=book.novelist_id,
        )
        self.session.add(new_book)
        self.session.commit()
        self.session.refresh(new_book)
        return new_book

    def get_novelist_by_id(self, novelist_id: int) -> Type[Novelist] | None:
        """
        Retrieves a novelist by ID from the database.

        Args:
            novelist_id (int): ID of the novelist to retrieve.

        Returns:
            Novelist: The novelist object, or None if not found.
        """
        return (
            self.session.query(Novelist)
            .filter(Novelist.id == novelist_id)
            .first()
        )

    def get_book_by_title(self, title: str) -> Type[Books] | None:
        """
        Retrieves a book by its title.

        Args:
            title (str): Title of the book to retrieve.

        Returns:
            Books: The book object, or None if not found.
        """
        return self.session.query(Books).filter(Books.title == title).first()

    def update_book(self, book_db: Books, updated_data: dict) -> Books:
        """
        Updates an existing book in the database.

        Args:
            book_db (Books): The book object to update.
            updated_data (dict): Dictionary with fields to update.

        Returns:
            Books: The updated book object.
        """
        for key, value in updated_data.items():
            setattr(book_db, key, value)

        self.session.add(book_db)
        self.session.commit()
        self.session.refresh(book_db)
        return book_db

    def get_book_by_id(self, book_id: int) -> Books:
        """
        Retrieves a book by its ID.

        Args:
            book_id (int): ID of the book to retrieve.

        Returns:
            Books: The book object, or None if not found.
        """
        return self.session.scalar(select(Books).where(Books.id == book_id))

    def list_books(
        self, limit: int, offset: int, title: str = None, year: int = None
    ) -> Sequence[Books]:
        """
        Retrieves a list of books from the database with optional filters.

        Args:
            limit (int): Maximum number of books to return.
            offset (int): Number of books to skip.
            title (str, optional): Partial match for book title.
            year (int, optional): Filter by publication year.

        Returns:
            list: List of book objects.
        """
        query = select(Books)

        if title:
            query = query.filter(Books.title.contains(title))

        if year:
            query = query.filter(Books.year == year)

        return self.session.scalars(query.offset(offset).limit(limit)).all()

    def delete_book(self, book_db: Books) -> None:
        """
        Deletes a book from the database.

        Args:
            book_db (Books): The book object to delete.
        """
        self.session.delete(book_db)
        self.session.commit()

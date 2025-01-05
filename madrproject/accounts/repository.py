from typing import List, Optional

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from madrproject.accounts.models import Account
from madrproject.config.security import get_password_hash


class AccountRepository:
    """
    Repository class for handling database operations related to accounts.
    """

    def __init__(self, session: Session):
        self.session = session

    def get_by_username_or_email(
        self, username: str, email: str
    ) -> Optional[Account]:
        """
        Retrieve an account by username or email.

        Args:
            username (str): The username to search for.
            email (str): The email to search for.

        Returns:
            Optional[Account]: The account if found, otherwise None.
        """
        return self.session.scalar(
            select(Account).where(
                or_(Account.username == username, Account.email == email)
            )
        )

    def create(self, username: str, email: str, password: str) -> Account:
        """
        Create a new account.

        Args:
            username (str): The username of the new account.
            email (str): The email of the new account.
            password (str): The plain-text password for the account.

        Returns:
            Account: The newly created account.
        """
        account = Account(
            username=username,
            email=email,
            password=get_password_hash(password),
        )
        self.session.add(account)
        self.session.commit()
        self.session.refresh(account)
        return account

    def update(self, account: Account) -> Account:
        """
        Update an existing account.

        Args:
            account (Account): The account object with updated fields.

        Returns:
            Account: The updated account.
        """
        self.session.add(account)
        self.session.commit()
        self.session.refresh(account)
        return account

    def delete(self, account: Account) -> None:
        """
        Delete an account.

        Args:
            account (Account): The account to delete.

        Returns:
            None
        """
        self.session.delete(account)
        self.session.commit()

    def list_all(self) -> List[Account]:
        """
        Retrieve all accounts.

        Returns:
            List[Account]: A list of all accounts in the database.
        """
        return self.session.scalars(select(Account)).all()

from http import HTTPStatus

from fastapi import APIRouter, HTTPException

from madrproject.accounts.repository import AccountRepository
from madrproject.accounts.schemas import (
    AccountPublicSchema,
    AccountSchema,
    ListAccountsSchema,
)
from madrproject.config.dependencies import *
from madrproject.config.security import get_password_hash

router = APIRouter(prefix='/account', tags=['account'])


@router.post(
    '/',
    status_code=HTTPStatus.CREATED,
    response_model=AccountPublicSchema,
)
def create_account(account: AccountSchema, session: T_Session):
    """
    Endpoint to create a new account.

    Args:
        account (AccountSchema): The account details.
        session (Session): The database session.

    Returns:
        AccountPublicSchema: The newly created account.
    """
    repo = AccountRepository(session)
    existing_account = repo.get_by_username_or_email(
        username=account.username, email=account.email
    )

    if existing_account:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Email or Username already exists.',
        )

    new_account = repo.create(
        username=account.username,
        email=account.email,
        password=account.password,
    )
    return new_account


@router.put(
    '/{account_id}',
    status_code=HTTPStatus.OK,
    response_model=AccountPublicSchema,
)
def update_account(
    account_id: int,
    account: AccountSchema,
    session: T_Session,
    current_account: T_CurrentAccount,
):
    """
    Endpoint to update an account.

    Args:
        account_id (int): The ID of the account to update.
        account (AccountSchema): The new account details.
        session (Session): The database session.
        current_account (Account): The currently authenticated account.

    Returns:
        AccountPublicSchema: The updated account.
    """
    if current_account.id != account_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='You do not have sufficient permissions to perform this action.',
        )

    repo = AccountRepository(session)

    if repo.is_email_or_username_taken(
        account.email, account.username, account_id
    ):
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Email or Username is already in use by another account.',
        )

    current_account.email = account.email
    current_account.password = get_password_hash(account.password)
    current_account.username = account.username
    updated_account = repo.update(current_account)

    return updated_account


@router.get(
    '/',
    status_code=HTTPStatus.OK,
    response_model=ListAccountsSchema,
)
def read_accounts(session: T_Session):
    """
    Endpoint to retrieve all accounts.

    Args:
        session (Session): The database session.

    Returns:
        ListAccountsSchema: A list of all accounts.
    """
    repo = AccountRepository(session)
    accounts = repo.list_all()
    return {'accounts': accounts}


@router.delete(
    '/{account_id}',
    status_code=HTTPStatus.OK,
)
def delete_account(
    account_id: int,
    session: T_Session,
    current_account: T_CurrentAccount,
):
    """
    Endpoint to delete an account.

    Args:
        account_id (int): The ID of the account to delete.
        session (Session): The database session.
        current_account (Account): The currently authenticated account.

    Returns:
        None
    """
    if current_account.id != account_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='You do not have sufficient permissions to perform this action.',
        )

    repo = AccountRepository(session)
    repo.delete(current_account)

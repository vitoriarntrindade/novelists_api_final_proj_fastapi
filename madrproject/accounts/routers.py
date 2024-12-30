from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from madrproject.accounts.models import Account
from madrproject.accounts.schemas import (
    AccountPublicSchema,
    AccountSchema,
    ListAccountsSchema,
)
from madrproject.config.database import get_session
from madrproject.config.security import get_current_account, get_password_hash

router = APIRouter(prefix='/account', tags=['accounts'])


@router.post(
    '/', status_code=HTTPStatus.CREATED, response_model=AccountPublicSchema
)
def create_account(
    account: AccountSchema, session: Session = Depends(get_session)
):
    account_db = session.scalar(
        select(Account).where(
            (Account.username == account.username)
            | (Account.email == account.email)
        )
    )

    if account_db:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Email or Username is alredy exists.',
        )
    account_db = Account(
        username=account.username,
        email=account.email,
        password=get_password_hash(account.password),
    )
    session.add(account_db)
    session.commit()

    return account_db


@router.put(
    '/{account_id}',
    status_code=HTTPStatus.OK,
    response_model=AccountPublicSchema,
)
def update_account(
    account_id: int,
    account: AccountSchema,
    session: Session = Depends(get_session),
    current_account: Account = Depends(get_current_account),
):
    if current_account.id != account_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail={'message': 'Not enought permission.'},
        )

    current_account.email = account.email
    current_account.password = get_password_hash(account.password)
    current_account.username = account.username

    session.add(current_account)
    session.commit()
    session.refresh(current_account)

    return current_account


@router.get('/', status_code=HTTPStatus.OK, response_model=ListAccountsSchema)
def read_accounts(session: Session = Depends(get_session)):
    accounts = session.scalars(select(Account)).all()

    return {'accounts': accounts}


@router.delete('/{account_id}', status_code=HTTPStatus.OK)
def delete(
    account_id: int,
    session: Session = Depends(get_session),
    current_account: Account = Depends(get_current_account),
):
    if current_account.id != account_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail={'message': 'Not enought permission.'},
        )

    session.delete(current_account)
    session.commit()

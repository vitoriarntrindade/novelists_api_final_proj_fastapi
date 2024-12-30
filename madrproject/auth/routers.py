from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from madrproject.accounts.models import Account
from madrproject.auth.schemas import Token
from madrproject.config.database import get_session
from madrproject.config.security import (
    create_access_token,
    get_current_account,
    verify_password,
)

router = APIRouter(prefix='/auth', tags=['auth'])


@router.post('/token/', response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):
    account: Account = session.scalar(
        select(Account).where(Account.email == form_data.username)
    )

    if not account or not verify_password(
        form_data.password, account.password
    ):
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Incorrect email or password',
        )

    access_token = create_access_token(data_payload={'sub': account.email})

    return {'access_token': access_token, 'token_type': 'Bearer'}


@router.post('/refresh_token/', response_model=Token)
def refresh_access_token(
    account: Account = Depends(get_current_account),
):
    new_access_token = create_access_token(data_payload={'sub': account.email})

    return {'access_token': new_access_token, 'token_type': 'bearer'}

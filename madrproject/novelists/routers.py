from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.future import select
from sqlalchemy.orm import Session

from madrproject import Novelist
from madrproject.accounts.models import Account
from madrproject.config.database import get_session
from madrproject.config.security import get_current_account
from madrproject.novelists.schemas import (
    NovelistPublicSchema,
    NovelistPublicSchemaList,
    NovelistSchema,
    UpdateNovelistSchema,
)

router = APIRouter(prefix='/novelist', tags=['novelist'])


@router.post('/', response_model=NovelistPublicSchema, status_code=201)
def create_new_novelist(
    novelist: NovelistSchema, session: Session = Depends(get_session)
):
    existing_novelist = (
        session.query(Novelist).filter(Novelist.name == novelist.name).first()
    )

    if existing_novelist:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT, detail='Novelist already exists.'
        )

    new_novelist = Novelist(name=novelist.name)
    session.add(new_novelist)
    session.commit()
    session.refresh(new_novelist)

    return new_novelist


@router.get(
    '/', response_model=NovelistPublicSchemaList, status_code=HTTPStatus.OK
)
def list_novelists(
    name: str | None = None,
    session: Session = Depends(get_session),
    account: Account = Depends(get_current_account),
    limit: int = 3,
    offset: int = 0,
):
    query = select(Novelist)

    if name:
        query = query.filter(Novelist.name.contains(name))

    novelists = session.scalars(query.offset(offset).limit(limit)).all()

    response_data = []
    for novelist in novelists:
        response_data.append({
            'id': novelist.id,
            'name': novelist.name,
            'books': [
                {'id': book.id, 'title': book.title, 'year': book.year}
                for book in novelist.books
            ],
        })

    return {'novelists': response_data}


@router.patch(
    '/{novelist_id}',
    response_model=NovelistPublicSchema,
    status_code=HTTPStatus.OK,
)
def update_novelist(
    novelist: UpdateNovelistSchema,
    novelist_id: int,
    session: Session = Depends(get_session),
    account: Account = Depends(get_current_account),
):
    novelist_db = session.scalar(
        select(Novelist).where(Novelist.id == novelist_id)
    )

    if not novelist_db:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f'Novelist with ID {novelist_id} was not found',
        )

    for key, value in novelist.model_dump(exclude_unset=True).items():
        setattr(novelist_db, key, value)

    session.add(novelist_db)
    session.commit()
    session.refresh(novelist_db)

    return novelist_db

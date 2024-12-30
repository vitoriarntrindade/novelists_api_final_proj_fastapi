from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from madrproject import Novelist
from madrproject.config.database import get_session
from madrproject.novelists.schemas import NovelistPublicSchema, NovelistSchema

router = APIRouter(prefix='/novelists', tags=['novelists'])


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

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, registry

from .settings import settings

mapper_registry = registry()
metadata = mapper_registry.metadata


engine = create_engine(settings.DATABASE_URL, echo=True)

mapper_registry.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session

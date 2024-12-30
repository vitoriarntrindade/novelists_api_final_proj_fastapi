from typing import List

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from madrproject.config.database import mapper_registry


@mapper_registry.mapped_as_dataclass
class Novelist:
    __tablename__ = 'novelists'
    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)

    books: Mapped[List['Books']] = relationship(
        'Books', back_populates='novelist', cascade='all, delete-orphan', default_factory=list
    )
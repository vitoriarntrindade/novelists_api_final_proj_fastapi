from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from madrproject.config.database import mapper_registry


@mapper_registry.mapped_as_dataclass
class Books:
    __tablename__ = 'books'
    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    year: Mapped[int]
    title: Mapped[str]
    novelist_id: Mapped[int] = mapped_column(ForeignKey('novelists.id'))
    novelist: Mapped['Novelist'] = relationship(
        'Novelist', back_populates='books', init=False
    )

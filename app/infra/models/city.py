from app.infra.models.base import Base
from sqlalchemy import (
    Integer,
    String,
    Float,
)
from sqlalchemy.orm import Mapped, mapped_column


class City(Base):
    __tablename__ = "cities"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )
    name: Mapped[str] = mapped_column(
        String,
        unique=False,
        index=True,
    )
    latitude: Mapped[float] = mapped_column(
        Float,
    )
    longitude: Mapped[float] = mapped_column(
        Float,
    )

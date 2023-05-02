from sqlalchemy import BigInteger, Column, ForeignKey, String, Table, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


class S3Storage(Base):
    __tablename__ = "s3storages"
    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    url: Mapped[str] = mapped_column(String(255), unique=True)
    ip_address: Mapped[str] = mapped_column(String(255), unique=True)
    size_bytes: Mapped[int] = mapped_column(BigInteger)

    def __repr__(self):
        return f"<S3Storage {self.url}>"


films_s3storages = Table(
    "films_s3storages",
    Base.metadata,
    Column("film_id", ForeignKey("films.id", ondelete="CASCADE"), primary_key=True),
    Column("s3storage_id", ForeignKey("s3storages.id", ondelete="CASCADE"), primary_key=True),
)


class Film(Base):
    __tablename__ = "films"
    id: Mapped[Uuid] = mapped_column(Uuid, primary_key=True)
    size_bytes: Mapped[int] = mapped_column(BigInteger)
    storages: Mapped[list[S3Storage]] = relationship(secondary=films_s3storages, lazy="raise")

    def __repr__(self):
        return f"<Film {self.id}>"

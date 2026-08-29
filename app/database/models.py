from datetime import date, datetime
from sqlalchemy import String, Text, Date, DateTime, ForeignKey, Table, Column, Integer,Float, Boolean
from sqlalchemy.orm import Mapped,mapped_column, relationship
from app.database.base import Base

paper_authors = Table(
    "paper_authors",
    Base.metadata,
    Column("paper_id", ForeignKey("papers.id"), primary_key=True),
    Column("author_id", ForeignKey("authors.id"), primary_key=True),
)

class AuthorORM(Base):
    __tablename__ = "authors"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique = True, index = True )
    affiliation: Mapped[str | None ] = mapped_column(String(255), nullable=True)

    papers: Mapped[list["PaperORM"]] = relationship(
        secondary = paper_authors, back_populates = "authors"
    )

class PaperORM(Base):
    __tablename__ = "papers"

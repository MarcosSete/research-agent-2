from datetime import date, datetime
from sqlalchemy import String, Text, Date, DateTime, ForeignKey, Table, Column, Integer, Float, Boolean, func
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
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(500))
    abstract: Mapped[str] = mapped_column(Text)

    source_name: Mapped[str] = mapped_column(String(50), index = True)
    source_url: Mapped[str] = mapped_column(String(500), unique=True) ## garanti que os papers tenha somente uma url fonte, assim evitando duplicação.
    published_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    conference: Mapped[str | None] = mapped_column(String(100), nullable=True)
    pdf_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    has_code: Mapped[bool] = mapped_column(Boolean, nullable=True)
    citations: Mapped[int] = mapped_column(Integer, default=0)
    has_embedding: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    authors: Mapped[list["AuthorORM"]] = relationship(
        secondary=paper_authors, back_populates="papers"
    )



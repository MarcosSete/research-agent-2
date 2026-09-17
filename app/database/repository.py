from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database.models import AuthorORM, PaperORM
from app.models.paper import Paper


class PaperRepository:
    def __init__(self, session: Session):
        self.session = session

    def save(self, paper: Paper) -> PaperORM | None:
        """Persiste um Paper e seus autores, evitando duplicidade por source_url."""
        source_url = str(paper.source.url)
        existing = (
            self.session.query(PaperORM)
            .filter_by(source_url=source_url)
            .first()
        )

        if existing:
            return None

        authors_orm = []
        for author in paper.authors:
            author_orm = (
                self.session.query(AuthorORM)
                .filter_by(name=author.name)
                .first()
            )

            if not author_orm:
                author_orm = AuthorORM(
                    name=author.name,
                    affiliation=author.affiliation,
                )
                self.session.add(author_orm)

            authors_orm.append(author_orm)

        paper_orm = PaperORM(
            title=paper.title,
            abstract=paper.abstract,
            source_name=paper.source.name.value,
            source_url=source_url,
            published_date=paper.published_date,
            conference=paper.conference,
            pdf_url=str(paper.pdf_url) if paper.pdf_url else None,
            has_code=paper.has_code,
            citations=paper.citations,
            authors=authors_orm,
        )

        try:
            self.session.add(paper_orm)
            self.session.commit()
        except IntegrityError:
            self.session.rollback()
            return None

        return paper_orm

    def exists(self, source_url: str) -> bool:
        return (
            self.session.query(PaperORM)
            .filter_by(source_url=source_url)
            .first()
            is not None
        )

    def count(self) -> int:
        return self.session.query(PaperORM).count()

    def get_without_embedding(self) -> list[PaperORM]:
        """Retorna papers que ainda não tiveram embedding gerado."""
        return (
            self.session.query(PaperORM)
            .filter_by(has_embedding=False)
            .all()
        )

    def mark_embedded(self, paper_id: int) -> None:
        """Marca um paper como já processado no Qdrant."""
        paper = (
            self.session.query(PaperORM)
            .filter_by(id=paper_id)
            .first()
        )

        if paper:
            paper.has_embedding = True
            self.session.commit()

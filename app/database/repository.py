from sqlalchemy.orm import Session
from sqlalchemy.exc import  IntegrityError
from app.database.models import PaperORM, AuthorORM
from app.models.paper import Paper


class PaperRepository:
    def __init__(self, session: Session):
        self.session = session


    def save(self, paper: Paper) -> PaperORM:
        """Salva um Paper (Pydantic) como PaperORM. Retorna None se já existir (duplicado)."""

        existing = self.session.query(PaperORM). filter_by(
            source_url=str(paper.source.url)
        ).first()

        if existing:
            return None ## Já existe, não duplica

        authors_orm = []
        for author in paper.authors:
            author_orm = self.session.query(AuthorORM).filter_by(name=author.name).first()
            if not author_orm:
                author_orm = AuthorORM(name=author.name,affiliation=author.affiliation)
                self.session.add(author_orm)
            authors_orm.append(author_orm)


        paper_orm = PaperORM(
            title=paper.title,
            abstract=paper.abstract,
            source_name=paper.source.name.value,
            source_url=str(paper.source.url),
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
            self.session.rollback()  # desfaz a transação em caso de erro
            return None

        return paper_orm


    def exists(self, source_url: str) -> bool:
        return self.session.query(PaperORM).filter_by(source_url=source_url).first() is not None
    def count(self) -> int:
        return self.session.query(PaperORM).count()
















## o que seria self de  self.session = session

## o que seria existing = self.session.query(PaperORM).filter_by(source_url=str(paper.source.url)).first() e o que faz o first()
## o que seria esse if not
## nese caso, author_orm = AuthorORM(name=author.name, affiliation=author.affiliation) e salvando em author_orm, eu estou adidiconado author na tabela?
## o que seria self.session.add(author_orm)
## o que seria self.session.commit()
## porque agente tem que retorna paper_orm se ele já foi adicionado dentro da tabela?
## O que seria o operador is not ?

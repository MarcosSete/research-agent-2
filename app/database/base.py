from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Classe base de onde todas as tabelas do projeto vão herdar."""
    pass

## Pra que serve essa classe Base? Porque todas as classes precisam herdar dela?
## O que significa esse pass?


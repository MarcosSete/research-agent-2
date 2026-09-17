"""create initial schema

Revision ID: 001_initial_schema
Revises:
Create Date: 2026-09-17
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "001_initial_schema"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "authors",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("affiliation", sa.String(length=255), nullable=True),
    )
    op.create_index("ix_authors_name", "authors", ["name"], unique=True)

    op.create_table(
        "papers",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("abstract", sa.Text(), nullable=False),
        sa.Column("source_name", sa.String(length=50), nullable=False),
        sa.Column("source_url", sa.String(length=500), nullable=False),
        sa.Column("published_date", sa.Date(), nullable=True),
        sa.Column("conference", sa.String(length=100), nullable=True),
        sa.Column("pdf_url", sa.String(length=500), nullable=True),
        sa.Column("has_code", sa.Boolean(), nullable=True),
        sa.Column("citations", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("has_embedding", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("source_url"),
    )
    op.create_index("ix_papers_source_name", "papers", ["source_name"], unique=False)

    op.create_table(
        "paper_authors",
        sa.Column("paper_id", sa.Integer(), sa.ForeignKey("papers.id"), primary_key=True),
        sa.Column("author_id", sa.Integer(), sa.ForeignKey("authors.id"), primary_key=True),
    )


def downgrade() -> None:
    op.drop_table("paper_authors")
    op.drop_index("ix_papers_source_name", table_name="papers")
    op.drop_table("papers")
    op.drop_index("ix_authors_name", table_name="authors")
    op.drop_table("authors")

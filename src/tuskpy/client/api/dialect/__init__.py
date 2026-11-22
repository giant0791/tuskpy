"""SQLAlchemy dialect for the tuskpy API."""

from sqlalchemy.dialects.postgresql.base import PGDialect


class TuskpyDialect(PGDialect):
    """SQLAlchemy dialect that connects through the tuskpy API."""

    name = "tuskpy"
    driver = "tuskpy"

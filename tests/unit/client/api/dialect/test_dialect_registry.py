from sqlalchemy.dialects import registry

from tuskpy.client.api.dialect import TuskpyDialect


def test_sqlalchemy_finds_the_tuskpy_dialect_by_name():
    assert registry.load("tuskpy") is TuskpyDialect

import sysconfig
from pathlib import Path

import pytest

TUSKPY_SERVER = str(Path(sysconfig.get_path("scripts")) / "tuskpy-server")


@pytest.mark.xfail(strict=True, reason="walking skeleton: SELECT 1 path not built")
def test_select_one_returns_one_row_with_one(start_server):
    # Arrange
    port = start_server([TUSKPY_SERVER, "--port", "0"])

    # import here, not at the top: xfail does not cover a collection error
    from tuskpy.client.api import connect  # ty: ignore[missing-module-member]

    connection = connect(host="127.0.0.1", port=port)

    try:
        cursor = connection.cursor()

        # Act
        cursor.execute("SELECT 1")
        row = cursor.fetchone()

        # Assert
        assert row == (1,)
    finally:
        connection.close()

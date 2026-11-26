import os
import sys
from pathlib import Path

import pytest


def fake_server(ready_line: str) -> list[str]:
    script = f"""
import signal
import sys
import time
signal.signal(signal.SIGTERM, lambda *_: sys.exit(0))
print({ready_line!r}, flush=True)
time.sleep(30)
"""
    return [sys.executable, "-c", script]


@pytest.mark.parametrize("port", [54321, 5433])
def test_start_server_gives_port_from_ready_line(start_server, port):
    # Arrange
    command = fake_server(f"listening on 127.0.0.1:{port}")

    # Act
    actual = start_server(command)

    # Assert
    assert actual == port


@pytest.mark.parametrize("exit_status", [1, 7])
def test_start_server_fails_test_when_server_exits_non_zero_after_sigterm(
    pytester: pytest.Pytester, exit_status
):
    # Arrange
    server_script = f"""
import signal
import sys
import time
signal.signal(signal.SIGTERM, lambda *_: sys.exit({exit_status}))
print("listening on 127.0.0.1:54321", flush=True)
time.sleep(30)
"""
    pytester.makeconftest(Path(__file__).with_name("conftest.py").read_text())
    pytester.makepyfile(
        f"""
import sys

def test_uses_server(start_server):
    start_server([sys.executable, "-c", {server_script!r}])
"""
    )

    # Act
    result = pytester.runpytest_subprocess()

    # Assert
    result.assert_outcomes(passed=1, errors=1)


def test_start_server_fails_fast_when_server_prints_no_ready_line(
    pytester: pytest.Pytester,
):
    # Arrange
    silent_server_script = """
import signal
import sys
import time
signal.signal(signal.SIGTERM, lambda *_: sys.exit(0))
time.sleep(30)
"""
    pytester.makeconftest(Path(__file__).with_name("conftest.py").read_text())
    pytester.makepyfile(
        f"""
import sys

def test_uses_server(start_server):
    start_server([sys.executable, "-c", {silent_server_script!r}])
"""
    )

    # Act
    result = pytester.runpytest_subprocess(timeout=20)

    # Assert
    result.assert_outcomes(failed=1)
    result.stdout.fnmatch_lines(["*Failed: *ready line*"])


def test_start_server_stops_server_that_ignores_sigterm(pytester: pytest.Pytester):
    # Arrange
    pid_file = pytester.path / "server.pid"
    stubborn_server_script = f"""
import os
import pathlib
import signal
import time
signal.signal(signal.SIGTERM, signal.SIG_IGN)
pathlib.Path({str(pid_file)!r}).write_text(str(os.getpid()))
print("listening on 127.0.0.1:54321", flush=True)
time.sleep(30)
"""
    pytester.makeconftest(Path(__file__).with_name("conftest.py").read_text())
    pytester.makepyfile(
        f"""
import sys

def test_uses_server(start_server):
    start_server([sys.executable, "-c", {stubborn_server_script!r}])
"""
    )

    # Act
    result = pytester.runpytest_subprocess(timeout=20)

    # Assert
    result.assert_outcomes(passed=1, errors=1)
    result.stdout.fnmatch_lines(["*Failed: *SIGTERM*"])
    server_pid = int(pid_file.read_text())
    with pytest.raises(ProcessLookupError):
        os.kill(server_pid, 0)

import re
import selectors
import subprocess
from collections.abc import Callable, Iterator

import pytest

READY_LINE = re.compile(r"listening on (?P<host>\S+):(?P<port>\d+)")
READY_TIMEOUT_SECONDS = 10
TERM_TIMEOUT_SECONDS = 5
KILL_TIMEOUT_SECONDS = 5


@pytest.fixture
def start_server() -> Iterator[Callable[[list[str]], int]]:
    processes: list[subprocess.Popen[str]] = []

    def _start(cmd: list[str]) -> int:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, text=True)

        processes.append(proc)
        assert proc.stdout is not None
        with selectors.DefaultSelector() as sel:
            sel.register(proc.stdout, selectors.EVENT_READ)
            ready = sel.select(timeout=READY_TIMEOUT_SECONDS)
        if not ready:
            pytest.fail(
                f"server printed no ready line within {READY_TIMEOUT_SECONDS} s"
            )

        line = proc.stdout.readline().rstrip("\n")
        match = READY_LINE.fullmatch(line)
        if match is None:
            pytest.fail(f"server printed no ready line, got {line!r}")
        return int(match["port"])

    yield _start

    errors: list[str] = []

    for proc in processes:
        killed = False
        proc.terminate()
        try:
            returncode = proc.wait(timeout=TERM_TIMEOUT_SECONDS)
        except subprocess.TimeoutExpired:
            # server did not terminate within grace period.
            proc.kill()
            killed = True
            returncode = proc.wait(timeout=KILL_TIMEOUT_SECONDS)

        # close before the check: a failed check must not leak the pipe
        if proc.stdout is not None:
            proc.stdout.close()

        if killed:
            errors.append(
                f"server (pid {proc.pid}) did not exit within "
                f"{TERM_TIMEOUT_SECONDS} s after SIGTERM, killed with SIGKILL"
            )
        elif returncode != 0:
            errors.append(
                f"server (pid {proc.pid}) exited with status {returncode} after SIGTERM"
            )

    if errors:
        pytest.fail("\n".join(errors))

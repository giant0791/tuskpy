# Research: GitHub Actions practice for uv-based Python projects

Ticket: #4. Date of research: 2026-11-22.

This note answers one question. What is the current recommended practice to run a uv-based Python project on GitHub Actions? It presents options and trade-offs. It does not make the final design decision. A later grilling ticket makes that decision.

## 1. Install uv: `astral-sh/setup-uv`

- The uv docs recommend the official `astral-sh/setup-uv` action. [1]
- The current major version is **v10**. The latest release is v10.4.0 (2026-11-20). [2][3]
- The uv docs page still shows v9.0.0 in its examples. The setup-uv README shows v10.4.0. Use the README as the source of truth for the action version. [1][2]
- v10.0.0 (2026-08-12) is a breaking release. With the default `enable-cache: auto`, the action now turns off the cache for `pull_request_target`, `workflow_run` and `release` events. This protects against cache poisoning. [4]
- v10 adds `version: "latest-known"`. This installs the newest uv with a checksum that the action knows. [4]
- The uv docs say: "It is considered best practice to pin to a specific uv version." The examples pin `version: "0.13.9"`. [1]
- The uv docs examples pin each action to a full commit SHA with a version comment, for example `astral-sh/setup-uv@<sha> # v10.4.0`. [1][2]
- If you do not set `version`, the action reads `required-version` from `uv.toml`, then from `pyproject.toml`. [2]

Project note: the local uv is 0.7.20. The latest uv is 0.13.9 (2026-11-17). [5] If CI pins a newer uv than the local one, the lockfile format or resolver output can differ. Align the local and CI uv versions, for example with `[tool.uv] required-version` in `pyproject.toml`.

### `python-version` input

- `python-version` sets the `UV_PYTHON` environment variable for the rest of the job. [2]
- It overrides the Python version in `pyproject.toml`, `.python-version` and `.tool-versions`. [2]
- It takes one version only. For many versions, use a job matrix. [1][2]
- `activate-environment: true` creates and activates a venv for later steps. The default is `false`. [2]

### Alternative: `actions/setup-python`

- The uv docs list `actions/setup-python` with `python-version-file: ".python-version"` or `"pyproject.toml"` as an option. [1]
- GitHub caches Python versions on the runner image, so this "can be faster". [1]
- Trade-off: one more action to pin and update. `uv python install` alone respects the project pin and needs no extra action. [1]

## 2. Dependency caching

Option A: built-in cache of setup-uv (simple).

- `enable-cache` defaults to `"auto"`. On GitHub-hosted runners the cache is on, except for release, tag push, `pull_request_target` and `workflow_run` events. On self-hosted runners it is off. [2]
- `cache-dependency-glob` defaults to `uv.lock`, `pyproject.toml`, `*.py.lock` and `requirements`/`constraints` files. A change in these files makes a new cache key. [2]
- `prune-cache` (default `false`) prunes the cache before save. `cache-suffix` adds a suffix to the key. [2]
- The uv docs show `enable-cache: true` as the simplest option. [1]

Option B: manual `actions/cache`.

- Set `UV_CACHE_DIR`, restore with `actions/cache` keyed on `hashFiles('uv.lock')`, and run `uv cache prune --ci` at the end. [1]
- `uv cache prune --ci` "is optimized for CI". Its effect depends on the packages that you install. [1]
- Trade-off: more YAML, more control. Option A gives the same result with one line.

Project note: tuskpy has few or no third-party runtime dependencies at the start. The cache gives only a small gain now. Option A costs nothing, so it is a safe default.

## 3. `uv sync --locked`

- The uv docs example installs with `uv sync --locked --all-extras --dev`, then runs `uv run pytest tests`. [1]
- By default, uv locks and syncs automatically. `uv run` updates `uv.lock` if it is stale. [6]
- `--locked`: "If the lockfile is not up-to-date, uv will raise an error instead of updating the lockfile." Use it in CI. It catches a `pyproject.toml` change without a matching `uv.lock` commit. [6]
- `--frozen`: uses the lockfile as-is and does not check it against `pyproject.toml`. It is less strict. [6]
- `uv lock --check` is a separate check step. It is equal to `--locked` on other commands. [6]
- Trade-off: `--locked` is strict and gives reproducible CI. `--frozen` is faster but hides a stale lockfile. For CI, `--locked` is the documented choice.

Note: `uv run` after `uv sync --locked` can re-lock if you do not pass `--locked` (or `--frozen`/`--no-sync`) to it as well. Set `UV_LOCKED=1` in the job `env` or pass the flag to each command. `UV_LOCKED` is "Equivalent to the `--locked` command-line argument." [12]

## 4. Python version matrix

Python release status (python.org devguide): [7]

| Version | Status | End of life |
|---|---|---|
| 3.11 | security | 2027-10 |
| 3.12 | security | 2028-10 |
| 3.13 | security | 2029-10 |
| 3.14 | bugfix | 2030-10 |
| 3.15 | bugfix (released 2026-10-09) | 2031-10 |

Facts:

- Python 3.12 is now in security-only mode. 3.14 and 3.15 are the bugfix branches. [7]
- The project pins Python 3.12.

Options:

- **M1: one version (3.12 only).** One job. Fastest feedback. It does not detect breakage on newer Pythons.
- **M2: floor and ceiling (3.12 and 3.15).** Two jobs. It tests the oldest supported and the newest version. It catches most deprecations.
- **M3: full range (3.12, 3.13, 3.14, 3.15).** Four jobs. Most coverage. Free on a public repo, but more noise and more wait time.
- **M4: optional pre-release or free-threaded job** (for example `3.15t` or a 3.16 alpha) with `continue-on-error: true`. Useful only if free-threading matters to the engine.

Trade-off: a learning project gains little from a wide matrix. A database engine uses `asyncio`, `socket` and `struct`. These modules are stable across 3.12 to 3.15. Consider raising the floor from 3.12, because 3.12 now gets only security fixes. [7]

## 5. OS coverage

Runner labels now (actions/runner-images): [8]

- `ubuntu-latest` = Ubuntu 24.04 x64. `ubuntu-24.04-arm` and `ubuntu-26.04` exist.
- `macos-latest` = macOS 26 arm64.
- `windows-latest` = Windows Server 2025 x64.

Options:

- **O1: Linux only.** Fastest and simplest. Most server software targets Linux. Enough for a learning DB engine.
- **O2: Linux plus macOS.** Useful if the developer works on macOS. Catches path and socket differences.
- **O3: Linux, macOS and Windows.** Full coverage. Windows differs in `asyncio` event loops, file locking, `fsync` and path handling. These differences matter for a storage engine and a network server. They also add work that does not teach PostgreSQL internals.

Limits on the Free plan: 20 concurrent jobs, and only 5 concurrent macOS jobs. [9] A 3-OS by 4-version matrix makes 12 jobs. It fits, but macOS jobs queue.

## 6. Concurrency cancellation

GitHub docs pattern: [10]

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

- This cancels an older run when a new push arrives on the same branch or PR. [10]
- Trade-off: on `main`, it can cancel a run that you want to finish for each commit. The docs show a conditional form, for example `cancel-in-progress: ${{ !contains(github.ref, 'release/') }}`. [10]
- A common variant is `cancel-in-progress: ${{ github.ref != 'refs/heads/main' }}`. This keeps every run on `main` and cancels stale PR runs. (This variant comes from the docs conditional pattern; the docs do not show this exact line.)

## 7. Cost on public repos

- GitHub docs: "The use of standard GitHub-hosted runners is free" in public repositories. This usage does not reduce the included minutes. [11]
- Larger runners are billed, also on public repos. [11]
- The per-minute rates apply to private repos beyond the included minutes: Linux 2-core $0.006, Windows $0.010, macOS $0.062. [11]
- Self-hosted runners are free. [11]
- Effect: on a public repo, matrix size and OS choice cost no money. They cost only wall-clock time and the concurrency limits in section 5. If the repo becomes private, macOS minutes cost about 10 times Linux minutes.

## 8. Example workflow (reference, not a decision)

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: ${{ github.ref != 'refs/heads/main' }}

permissions:
  contents: read

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        python-version: ["3.12", "3.15"]
    env:
      UV_LOCKED: "1"
    steps:
      - uses: actions/checkout@<sha> # v7.x
      - uses: astral-sh/setup-uv@<sha> # v10.4.0
        with:
          version: "0.13.9"
          python-version: ${{ matrix.python-version }}
          enable-cache: true
      - run: uv sync --locked --all-extras --dev
      - run: uv run pytest
```

## 9. Recommendation (input for the grilling ticket)

- Use `astral-sh/setup-uv@v10`, pinned by SHA, with a pinned uv `version`. Align it with the local uv through `required-version`.
- Use the built-in cache (`enable-cache: auto` or `true`). Do not add `actions/cache`.
- Use `uv sync --locked` and set `UV_LOCKED=1` so `uv run` does not re-lock.
- Start with Linux only (`ubuntu-latest`). Add macOS or Windows later if a real need appears.
- Start with a small matrix: 3.12 plus the newest stable (3.15). Decide if 3.12 stays the floor.
- Use the concurrency block that cancels stale PR runs but keeps `main` runs.
- Cost is zero on a public repo. Time and simplicity are the real constraints.

Open questions for the grilling ticket:

1. Which Python version is the floor: 3.12 (security-only) or a newer one?
2. Does the project need Windows support at all?
3. Which uv version does the project pin, given the local uv is 0.7.20?
4. Do lint and type-check (ruff, mypy or ty) run in the same workflow or in a separate job?

## Sources

1. uv docs, "Using uv in GitHub Actions": https://docs.astral.sh/uv/guides/integration/github/
2. astral-sh/setup-uv README: https://github.com/astral-sh/setup-uv
3. astral-sh/setup-uv releases: https://github.com/astral-sh/setup-uv/releases
4. setup-uv v10.0.0 release notes: https://github.com/astral-sh/setup-uv/releases/tag/v10.0.0
5. uv releases: https://github.com/astral-sh/uv/releases
6. uv docs, "Locking and syncing": https://docs.astral.sh/uv/concepts/projects/sync/
7. Python devguide, "Status of Python versions": https://devguide.python.org/versions/
8. actions/runner-images: https://github.com/actions/runner-images
9. GitHub docs, "Actions limits": https://docs.github.com/en/actions/reference/limits
10. GitHub docs, "Control the concurrency of workflows and jobs": https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/control-workflow-concurrency
11. GitHub docs, "GitHub Actions billing": https://docs.github.com/en/billing/concepts/product-billing/github-actions
12. uv docs, "Environment variables": https://docs.astral.sh/uv/reference/environment/

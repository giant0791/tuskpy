# Research: Sphinx documentation options

Ticket: [#8 Research Sphinx documentation options](https://github.com/giant0791/tuskpy/issues/8)

Date: 2026-11-22

## Question

What are the current options for a Sphinx site in a Python project?
This note compares themes, markup languages, API documentation tools, and hosting.
It also covers how to include Markdown files that live outside the Sphinx source directory.

This note gives options and trade-offs. It does not make the final design decision.
A later grilling ticket makes that decision.

## Project context

- tuskpy is a public GitHub repository.
- tuskpy uses uv 0.7.20, Python 3.12, and a src layout (`src/tuskpy`).
- The repository has no code yet.
- Agent docs live in `docs/agents/` as Markdown.
- A `CONTEXT.md` glossary and `docs/adr/*.md` ADRs are planned at the repo root. They are Markdown.

## 1. Themes

| Theme | Strengths | Weaknesses | Best fit |
|---|---|---|---|
| Furo | Light, dark, and automatic mode. Responsive. "Intentionally minimal". Many customization points (colors, fonts, logo, sidebar, announcement banner). | The theme states a bias toward smaller documentation sets, because the sidebar shows the full page hierarchy. | Small to medium project docs. |
| PyData Sphinx Theme | Bootstrap-based and responsive. Light and dark mode. Built-in version switcher dropdown. Has an accessibility section. Built by and for the PyData community. | More configuration surface. Top navigation bar suits large sites with many sections. | Large docs with many sections and versioned releases. |
| sphinx-rtd-theme | The classic Read the Docs look. Good on desktop and mobile. Works on any host. | No built-in dark mode found. Dark mode needs the third-party `sphinx-rtd-dark-mode` package (last release 1.3.0, September 2023). | Users who want the familiar Read the Docs look. |
| Sphinx Book Theme | Book-like layout. Margin content and sidenotes (Tufte style). Jupyter Notebook styling and Binder launch buttons. Default theme of Jupyter Book. Uses Bootstrap 5. | Focus on books and notebooks, not API reference. A recent release changed the HTML, so custom CSS can break. | Tutorials, books, and notebook-heavy content. |

Sources:
- Furo: https://pradyunsg.me/furo/
- PyData Sphinx Theme: https://pydata-sphinx-theme.readthedocs.io/en/stable/
- sphinx-rtd-theme: https://sphinx-rtd-theme.readthedocs.io/en/stable/
- sphinx-rtd-theme changelog (3.0.x): https://sphinx-rtd-theme.readthedocs.io/en/3.0.2/changelog.html
- sphinx-rtd-dark-mode: https://pypi.org/project/sphinx-rtd-dark-mode
- Sphinx Book Theme: https://sphinx-book-theme.readthedocs.io/en/stable/

Note: the dark mode finding for sphinx-rtd-theme comes from a web search, not from an explicit statement in the theme docs. Check the upstream changelog before you rely on it.

## 2. Markup: MyST Markdown vs reStructuredText

### reStructuredText (rST)

- rST is the native Sphinx markup. All directives and roles work with no extra layer.
- `sphinx.ext.autodoc` "is hard-coded to generate RestructureText". rST docstrings work directly.
- You must write a second markup language if the rest of the repo uses Markdown.

### MyST Markdown (myst-parser)

- MyST lets Sphinx read Markdown with Sphinx directives and roles.
- The existing and planned docs (`docs/agents/`, `CONTEXT.md`, `docs/adr/`) are already Markdown. MyST lets Sphinx use them without conversion.
- autodoc output is rST. In a MyST page, you wrap autodoc directives in an `eval-rst` block.
- MyST recommends `sphinx-autodoc2` for API docs. It does static analysis. It allows docstrings in rST or MyST.

### Mixed use

- Sphinx can read `.md` and `.rst` files in the same project.
- A common pattern: prose pages in MyST, docstrings in rST or Google/NumPy style (with napoleon).

Sources:
- MyST, code and APIs: https://myst-parser.readthedocs.io/en/latest/syntax/code_and_apis.html
- MyST FAQ: https://myst-parser.readthedocs.io/en/latest/faq/index.html

## 3. API docs: autodoc/autosummary vs sphinx-autoapi

| Tool | How it works | Strengths | Weaknesses |
|---|---|---|---|
| `sphinx.ext.autodoc` | Imports the package and reads docstrings. You write directives (`.. automodule::`) by hand. | Built into Sphinx. Full control over page layout. | Needs the package to be importable at build time. Manual pages. Output is rST only. |
| `sphinx.ext.autosummary` | Builds on autodoc. Generates stub pages. `autosummary_generate` is `True` by default since Sphinx 4.0. The `:recursive:` option (since 3.1) walks sub-packages. | Built into Sphinx. Less manual work than plain autodoc. | Same import model as autodoc (it shares `autodoc_mock_imports`). Templates need tuning for a good look. |
| `sphinx-autoapi` | Parses the source code. It does not import or run the project. Generates all API pages. Version 3.9.0 at the time of writing. | No import at build time. No mock imports. Almost zero setup. Good fit for a src layout. | Less control over page layout. Static analysis can miss dynamic behavior. |
| `sphinx-autodoc2` | Static analysis, like sphinx-autoapi. | MyST docstrings are possible. Recommended by MyST. | Smaller user base than autodoc or sphinx-autoapi. |

Sources:
- autosummary: https://www.sphinx-doc.org/en/master/usage/extensions/autosummary.html
- sphinx-autoapi: https://sphinx-autoapi.readthedocs.io/en/latest/
- MyST on autodoc and autodoc2: https://myst-parser.readthedocs.io/en/latest/syntax/code_and_apis.html

## 4. Hosting: Read the Docs vs GitHub Pages

### Read the Docs (Community plan)

- Free for open-source projects. Hosting is ad-supported. Public repositories only.
- Every plan includes pull request previews.
- PR previews are on by default for new projects. Each PR gets a build status check. With the GitHub App, Read the Docs also posts a comment with the preview link and the changed files.
- PR previews use separate domains (`*.readthedocs.build`) for security. PR builds only get environment variables marked *Public*.
- Versioned docs are built in. Each Git tag and branch can be a version. `latest` tracks the default branch. `stable` tracks the highest semantic version tag (PEP 440). A flyout menu lets readers switch versions.
- uv support is native in `.readthedocs.yaml`. If `uv.lock` exists, Read the Docs respects it:

```yaml
version: 2

build:
  os: ubuntu-26.04
  tools:
    python: "3.14"   # tuskpy would set "3.12"

python:
  install:
    - method: uv
      command: sync
      groups:
        - docs

sphinx:
  configuration: docs/conf.py
```

- Use `build.jobs` only for an advanced uv workflow.

Sources:
- uv on Read the Docs: https://docs.readthedocs.com/platform/stable/build-customization.html
- PR previews: https://docs.readthedocs.com/platform/stable/pull-requests.html
- Versions: https://docs.readthedocs.com/platform/stable/versions.html
- Pricing and plans: https://about.readthedocs.com/pricing/

### GitHub Pages (GitHub Actions)

- You write a workflow. It runs `uv sync --group docs` and `sphinx-build`, then uploads the HTML.
- The official path uses `actions/upload-pages-artifact@v4` and `actions/deploy-pages@v4`. The deploy job needs `pages: write` and `id-token: write` permissions.
- No ads. Everything stays on GitHub. You own the full build.
- PR previews are not built in. The third-party `rossjrw/pr-preview-action` deploys previews to `https://<owner>.github.io/<repo>/pr-preview/pr-<number>/`. It does not support PRs from forks yet. It deploys to a `gh-pages` branch, so the main deploy must not delete the `pr-preview/` folder (for example, set `clean-exclude: pr-preview` in `JamesIves/github-pages-deploy-action`). This model conflicts with the artifact-based `deploy-pages` path.
- Versioned docs are not built in. `sphinx-multiversion` builds one site per tag or branch. Its maintenance status is unclear (no published GitHub releases shown). You must also add a version switcher yourself (PyData Sphinx Theme has one).

Sources:
- GitHub Pages custom workflows: https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages
- pr-preview-action: https://github.com/rossjrw/pr-preview-action
- sphinx-multiversion: https://github.com/sphinx-contrib/multiversion

### Hosting trade-off summary

| Need | Read the Docs | GitHub Pages |
|---|---|---|
| Setup effort | Low. One YAML file. | Medium. A workflow file and Pages settings. |
| uv support | Native (`method: uv`). | You run uv in the workflow. |
| PR previews | Built in. | Third-party action. No fork PRs. |
| Versioned docs | Built in (`latest`, `stable`, tags). | Extra tool and manual switcher. |
| Ads | Yes, on the free plan. | No. |
| Control over build | Limited to the config schema. | Full. |

## 5. Include Markdown files outside the Sphinx source directory

Sphinx only builds documents inside its source directory. `CONTEXT.md` and `docs/adr/*.md` live at the repo root, so they need a bridge. Options:

1. **MyST `include` directive (recommended by MyST).** Make a small stub page in the source directory. The stub includes the outside file, for example `../CONTEXT.md`.
   - A plain include does not fix local links and images. The content acts as if it comes from the stub file.
   - Add `:relative-docs:` and `:relative-images:` to rewrite links and images. This feature is experimental (since myst-parser 0.12.7). It only works for Markdown-style links and images.
2. **rST include with the MyST parser.** In an `.rst` stub, use `.. include:: ../CONTEXT.md` with `:parser: myst_parser.sphinx_`. This needs `docutils>=0.17`.
3. **Put the Sphinx source directory at a higher level.** For example, set the source directory to `docs/` so `docs/adr/` is inside it. Use `exclude_patterns` to skip files that must not become pages (for example `docs/agents/`). `CONTEXT.md` at the repo root still needs a stub.
4. **Symlinks.** Link the files into the source directory. This is simple, but symlinks can fail on some platforms and hosts.

Source:
- MyST FAQ, include files from outside the docs folder: https://myst-parser.readthedocs.io/en/latest/faq/index.html

Note: option 3 and option 4 come from general Sphinx behavior. The MyST FAQ documents options 1 and 2.

## 6. Useful extensions

| Extension | What it does | How to enable |
|---|---|---|
| `sphinx.ext.napoleon` | Reads Google-style and NumPy-style docstrings. It converts them to rST before Sphinx parses them. Both styles are on by default. | Add `"sphinx.ext.napoleon"` to `extensions` in `conf.py`. |
| `sphinx.ext.intersphinx` | Links your docs to objects in other projects through their `objects.inv` file. It is a fallback when a cross-reference has no local target. The `:external:` role forces an outside lookup. | `intersphinx_mapping = {"python": ("https://docs.python.org/3", None)}` |
| `linkcheck` builder | Scans all documents for external links. Reports broken and redirected links to stdout and `output.txt`. Retries on rate limits (since 3.4). | `sphinx-build -b linkcheck docs docs/_build/linkcheck` |
| `sphinx-autobuild` | Watches the source directory. Rebuilds on change. Serves the site with live reload at `http://127.0.0.1:8000`. | `uv run sphinx-autobuild docs docs/_build/html` |

Sources:
- napoleon: https://www.sphinx-doc.org/en/master/usage/extensions/napoleon.html
- intersphinx: https://www.sphinx-doc.org/en/master/usage/extensions/intersphinx.html
- linkcheck: https://www.sphinx-doc.org/en/master/usage/builders/index.html
- sphinx-autobuild: https://github.com/sphinx-doc/sphinx-autobuild

## 7. Setup with uv

- Put the docs tools in a dependency group, for example `docs` in `[dependency-groups]` in `pyproject.toml`.
- Local build: `uv sync --group docs`, then `uv run sphinx-build docs docs/_build/html`.
- Local live preview: `uv run sphinx-autobuild docs docs/_build/html`.
- Read the Docs reads the same `docs` group through `method: uv` and `groups: [docs]`.
- GitHub Actions runs the same uv commands in the workflow.

Source for the Read the Docs side: https://docs.readthedocs.com/platform/stable/build-customization.html

## Recommendation (not a decision)

The grilling ticket makes the decision. This combination fits tuskpy best on current evidence:

- **Theme:** Furo. It is clean, has dark mode, and fits a project that starts small. Switch to PyData Sphinx Theme if the site grows large or needs a version switcher on GitHub Pages.
- **Markup:** MyST Markdown for prose. The repo already uses Markdown for agent docs, `CONTEXT.md`, and ADRs.
- **Docstrings:** Google style with `sphinx.ext.napoleon`.
- **API docs:** sphinx-autoapi. It needs no import at build time and fits a src layout with low setup. Use autodoc/autosummary if you need fine control over page layout later.
- **Hosting:** Read the Docs. It gives native uv support, PR previews, and versioned docs with one YAML file. Choose GitHub Pages if no ads and full build control matter more.
- **External Markdown:** stub pages with the MyST `include` directive and `:relative-docs:` / `:relative-images:`.
- **Extensions:** napoleon, intersphinx (Python stdlib), linkcheck in CI, sphinx-autobuild for local work.

## Open questions for the grilling ticket

- Do ads on the Read the Docs free plan matter?
- Do we need versioned docs before the first release?
- Do docstrings use Google style, NumPy style, or rST?
- Does `docs/agents/` belong in the public site, or only `CONTEXT.md` and the ADRs?
- Where does the Sphinx source directory live (`docs/` or `docs/source/`)?

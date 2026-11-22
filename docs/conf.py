"""Sphinx configuration for the tuskpy docs site (issues #9 and #10)."""

project = "tuskpy"
author = "Gianmarco Antonini"
copyright = "2026, Gianmarco Antonini"

extensions = [
    "myst_parser",
    "autoapi.extension",
    "sphinx.ext.napoleon",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
]

# docs/agents/ holds instructions for agents, not pages for readers.
exclude_patterns = ["_build", "agents"]

# Prose pages are MyST Markdown only (issue #9). sphinx-autoapi writes
# its generated API pages in reStructuredText, so .rst stays a source suffix.
source_suffix = {".rst": "restructuredtext", ".md": "markdown"}
myst_heading_anchors = 3

html_theme = "furo"
html_title = "tuskpy"

# API reference. sphinx-autoapi reads the source and does not import it.
# Private members are in, because the internals are the learning content.
# No undoc-members: Ruff D requires a docstring on each member.
autoapi_type = "python"
autoapi_dirs = ["../src/tuskpy"]
autoapi_root = "api"
autoapi_options = [
    "members",
    "private-members",
    "show-inheritance",
    "show-module-summary",
]

napoleon_google_docstring = True
napoleon_numpy_docstring = False

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}

# Known false alarms of the nitpicky build (-n). Give a reason for each one.
nitpick_ignore = [
    # The SQLAlchemy docs do not document PGDialect, so its inventory has
    # no target for the base class of TuskpyDialect.
    ("py:obj", "sqlalchemy.dialects.postgresql.base.PGDialect"),
]

# External URLs that always reject bots. Give a reason for each one.
linkcheck_ignore: list[str] = []

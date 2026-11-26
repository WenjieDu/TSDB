"""Sphinx configuration for the TSDB documentation."""

import atexit
import os
import sys
import tempfile
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tsdb.version import __version__

project = "TSDB"
author = "Wenjie Du"
copyright = f"{datetime.now().year}, {author}"
release = __version__
version = release

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.doctest",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
    "sphinxcontrib.bibtex",
]
autodoc_member_order = "bysource"
napoleon_use_param = True
bibtex_bibfiles = ["references.bib"]
bibtex_default_style = "unsrt"
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
html_theme = "furo"
html_title = "TSDB documentation"
epub_exclude_files = ["search.html", ".doctrees"]


# Autodoc/doctest can exercise data-access APIs that initialize ecosystem config.
# Keep the entire build isolated from the maintainer's real configuration/cache.
def setup(app):
    home = tempfile.TemporaryDirectory(prefix="tsdb-docs-home-")
    previous = {key: os.environ.get(key) for key in ("HOME", "USERPROFILE", "PYPOTS_HOME", "TSDB_CACHE_DIR")}
    for key in ("HOME", "USERPROFILE"):
        os.environ[key] = home.name
    for key in ("PYPOTS_HOME", "TSDB_CACHE_DIR"):
        os.environ.pop(key, None)

    def cleanup():
        for key, value in previous.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        home.cleanup()

    atexit.register(cleanup)
    return {"parallel_read_safe": False, "parallel_write_safe": False}

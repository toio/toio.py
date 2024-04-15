import os
import sys

sys.path.insert(0, os.path.abspath("../toio"))

# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "toio.py"
copyright = "2022, Sony Interactive Entertainment"
author = "Sony Interactive Entertainment"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.viewcode",
    "sphinx.ext.todo",
    "sphinx.ext.napoleon",
    "sphinx.ext.githubpages",
    "sphinx_multiversion",
]

autodoc_default_options = {
    "member-order": "bysource",
    "special-members": "__init__,__str__,__bytes__",
    "undoc-members": True,
}

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

html_sidebars = {
    "**": [
        "version.html",
    ],
}

language = "en"

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

# html_theme = "sphinx_rtd_theme"
# html_static_path = ["_static"]

html_theme = "sphinx_nefertiti"

# -- Options for todo extension ----------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/todo.html#configuration

todo_include_todos = True

autosummary_generate = True

# -- Options for multiversion ------------------------------------------------

smv_tag_whitelist = r"^\d+\.\d+\.(\d+|\d(a|b|rc)*\d+|\d+\.post\d+)$"
smv_branch_whitelist = "__DOCUMENT_FOR_BRANCH_IS_NOT_GENERATED__"


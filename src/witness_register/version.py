"""Single source of the register's own version string.

The version names this register's code and schemas, not any line's report.
``pyproject.toml``, the manuscript config, and the changelog all repeat this
value; a binding test holds them equal so the copies cannot drift apart.
"""

from __future__ import annotations

__version__ = "0.1.0"

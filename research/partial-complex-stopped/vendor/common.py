"""Exact require helper from PR104 scripts/certify.py (Apache-2.0)."""

def require(condition, message):
    if not condition:
        raise ValueError(message)

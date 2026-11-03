"""Source-bound sparse kernel products for the complete PR1668 replay.

This contribution was produced by Nick Petalas. Apache-2.0.
The retained scientific program and every mathematical result are credited
to Josie Elliston and its source notices. Only kernel_ok is replaced.
"""

import argparse
import hashlib
import types
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / "full-family-g-without-d" / "verify.py"
SOURCE_SHA256 = "2e45790da2cc2b2eea2e47900a94cadf7aa4a7d42a3d38390729cd9b409d73fb"
MAX_ROWS, MAX_COLUMNS, MAX_VECTORS = 2025, 120, 8


def require(condition, message):
    if not condition:
        raise ValueError(message)


def authenticated_source(path=SOURCE):
    with path.open("rb") as handle:
        source = handle.read(65537)
    require(len(source) <= 65536, "source exceeds byte limit")
    require(hashlib.sha256(source).hexdigest() == SOURCE_SHA256,
            "source hash mismatch")
    return source


def load_source():
    source = authenticated_source()
    module = types.ModuleType("frozen_frame_incidence")
    module.__file__ = str(SOURCE)
    # The only dynamic program is the authenticated, unchanged reference.
    # optimize=0 retains its assertions even under an optimized adapter.
    exec(compile(source, str(SOURCE), "exec", optimize=0), module.__dict__)
    return module


def kernel_ok(rows, vecs):
    """Return the same integer dot-product predicate on bounded binary rows."""
    require(len(rows) <= MAX_ROWS and len(vecs) <= MAX_VECTORS,
            "kernel collection exceeds capacity")
    width = len(rows[0]) if rows else (len(vecs[0]) if vecs else 0)
    require(width <= MAX_COLUMNS, "kernel width exceeds capacity")
    require(all(len(v) == width and all(type(x) is int for x in v)
                for v in vecs), "invalid kernel vector")
    for row in rows:
        require(len(row) == width and all(type(x) is int and x in (0, 1)
                                         for x in row), "invalid incidence row")
        support = tuple(i for i, value in enumerate(row) if value)
        for vector in vecs:
            if sum(vector[i] for i in support) != 0:
                return False
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", action="store_true")
    args = parser.parse_args()
    module = load_source()
    if not args.baseline:
        module.kernel_ok = kernel_ok
    module.main()


if __name__ == "__main__":
    main()

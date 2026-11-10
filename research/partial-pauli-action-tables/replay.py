"""Complete source-authenticated PR5342 replay with invocation-local action tables.

This contribution was produced by Nick Petalas. Apache-2.0.
Ali Romman's original verifier and every retained check remain unchanged.
"""

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path


PACKAGE = Path(__file__).resolve().parent
SOURCE = "research/partial-pauli-gaussian-minimum/verify.py"
MAX_TABLES = sum(16**j for j in range(5))


def load_source(root=None):
    """Authenticate the declared source bytes before executing its module."""
    root = PACKAGE.parents[1] if root is None else Path(root)
    path = root / SOURCE
    pins = json.loads((PACKAGE / "SOURCES.json").read_text())
    pin = next(row for row in pins["files"] if row["path"] == SOURCE)
    payload = path.read_bytes()
    if len(payload) > 65536 or hashlib.sha256(payload).hexdigest() != pin["sha256"]:
        raise ValueError("source bytes differ from the pinned PR5342 verifier")
    spec = importlib.util.spec_from_file_location("partial_pauli_retained", path)
    if spec is None or spec.loader is None:
        raise ValueError("source loader unavailable")
    module = importlib.util.module_from_spec(spec)
    # Compile authenticated bytes directly, avoiding preexisting bytecode caches.
    exec(compile(payload, str(path), "exec"), module.__dict__)
    return module


def make_action(stats):
    """Return an exact action on at most four columns of four binary bits."""
    tables = {}
    stats.update(calls=0, tables=0, entries=0, xor_updates=0)

    def action(columns, x):
        key = tuple(columns)
        table = tables.get(key)
        if table is None:
            if len(key) > 4 or any(type(v) is not int or not 0 <= v < 16 for v in key):
                raise ValueError("action columns outside the four-bit replay domain")
            if len(tables) >= MAX_TABLES:
                raise ValueError("action table capacity exhausted")
            table = [0] * (1 << len(key))
            for c in range(1, len(table)):
                bit = c & -c
                table[c] = table[c ^ bit] ^ key[bit.bit_length() - 1]
            tables[key] = table
            stats["tables"] += 1
            stats["entries"] += len(table)
            stats["xor_updates"] += len(table) - 1
        if type(x) is not int or not 0 <= x < len(table):
            raise ValueError("action mask outside the declared columns")
        stats["calls"] += 1
        return table[x]

    return action


def run(original=False):
    module = load_source()
    stats = {}
    if not original:
        module.act = make_action(stats)
    module.main()
    return stats


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--original", action="store_true")
    args = parser.parse_args()
    run(args.original)


if __name__ == "__main__":
    main()

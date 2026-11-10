"""Bounded exact containment reuse for the frozen PR6396 census.

New implementation produced by Nick Petalas. Apache-2.0.
The frozen census, oracle, mathematical claims and notices retain their authors.
"""

import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
MANIFEST_SHA256 = "3e74a49400d174b61049815a4ece5ff1ac3226d28e1eeac6f2b856b013989d47"
CAPACITY = 32768


def require(condition, message):
    if not condition:
        raise ValueError(message)


class ContainmentMemo:
    """Cache a pure Boolean function on ordered immutable space pairs."""

    def __init__(self, original, capacity=CAPACITY):
        require(type(capacity) is int and 0 <= capacity <= CAPACITY, "Cache capacity")
        require(callable(original), "Containment function required")
        self.original = original
        self.capacity = capacity
        self.memo = {}
        self.calls = self.hits = self.misses = 0

    def __call__(self, outer, inner):
        self.calls += 1
        key = (outer, inner)
        if key in self.memo:
            self.hits += 1
            return self.memo[key]
        self.misses += 1
        result = self.original(outer, inner)
        require(type(result) is bool, "Boolean containment result required")
        if len(self.memo) < self.capacity:
            self.memo[key] = result
        return result

    def statistics(self):
        require(self.calls == self.hits + self.misses, "Cache accounting")
        require(len(self.memo) <= self.capacity, "Cache bound")
        return {"calls": self.calls, "hits": self.hits, "misses": self.misses,
                "entries": len(self.memo), "capacity": self.capacity}


def authenticated_source():
    raw = (ROOT / "FROZEN.json").read_bytes()
    require(hashlib.sha256(raw).hexdigest() == MANIFEST_SHA256, "Frozen manifest digest")
    manifest = json.loads(raw)
    require(len(manifest["files"]) == 17, "Frozen file inventory")
    for row in manifest["files"]:
        payload = (ROOT / "frozen" / row["path"]).read_bytes()
        require(hashlib.sha256(payload).hexdigest() == row["sha256"],
                "Frozen sha256: " + row["path"])
        blob = hashlib.sha1(b"blob " + str(len(payload)).encode() + b"\0" + payload).hexdigest()
        require(blob == row["git_blob"], "Frozen Git blob: " + row["path"])
    path = ROOT / "frozen" / "verify_full_census.py"
    namespace = {"__name__": "authenticated_frozen_census", "__file__": str(path)}
    exec(compile(path.read_bytes(), str(path), "exec"), namespace)
    return namespace


def run(emit=False, statistics=False):
    source = authenticated_source()
    kernel = source["load_kernel"]()
    memo = ContainmentMemo(kernel["contains"])
    kernel["contains"] = memo
    result = source["Census"](kernel).run()
    canonical = source["canonical"]
    expected = kernel["decode"]((ROOT / "frozen" / "FULL-CENSUS.json").read_bytes())
    require(canonical(result) == canonical(expected), "Complete frozen census receipt mismatch")
    stats = memo.statistics()
    require(stats["hits"] > 0 and stats["misses"] > 0, "Containment reuse must execute")
    if statistics:
        print(json.dumps(stats, sort_keys=True), file=sys.stderr)
    print(canonical(result) if emit else "PASS independent complete normalized G20 census receipt")
    return result, stats


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--stats", action="store_true")
    args = parser.parse_args()
    run(args.emit, args.stats)


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, TypeError, OSError) as exc:
        print("FAIL: " + str(exc), file=sys.stderr)
        sys.exit(1)

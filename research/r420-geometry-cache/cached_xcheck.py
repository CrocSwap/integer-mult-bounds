"""Opt-in, bounded geometry reuse for the pinned PR543 exact checker.

Only Word.__init__ and labels() results are reused. full() and interface()
always run on a fresh Word instance. No persistent cache or approximate math.
Prepared for mtpsl with substantial OpenAI Codex assistance; Apache-2.0.
"""
from collections import OrderedDict
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = ROOT / "research/e8-bit-r420/code/xcheck.py"
PIN = "5737d18a7826fd51e131035f2d7bebba2e2868af91dd7672a5f11208b036d424"
if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != PIN:
    raise RuntimeError("pinned xcheck source changed; review cache dependencies before use")
spec = importlib.util.spec_from_file_location("r420_original_xcheck", SOURCE)
original = importlib.util.module_from_spec(spec)
spec.loader.exec_module(original)
Reject = original.Reject

# Complete data dependencies of the pinned Word.__init__ and labels methods.
GEOMETRY_FIELDS = ("h", "v", "R", "form", "lines", "frames")


class GeometryCache:
    def __init__(self, capacity=2):
        if type(capacity) is not int or capacity < 1:
            raise ValueError("capacity must be a positive integer")
        self.capacity = capacity
        self._entries = OrderedDict()
        self.hits = 0
        self.misses = 0

    def check(self, word):
        # The full serialization, not its hash, is the equality key. Preserve
        # array order, duplicate entries and raw numeric types. No normalization
        # of labels or frames may hide invalid input from the original checker.
        key = json.dumps({field: word[field] for field in GEOMETRY_FIELDS},
                         sort_keys=True, separators=(",", ":"), allow_nan=False)
        if key in self._entries:
            self.hits += 1
            snapshot = self._entries.pop(key)
            self._entries[key] = snapshot
        else:
            self.misses += 1
            checked = original.Word(word)
            labels = checked.labels()  # Failures never populate the cache.
            snapshot = (
                checked.v, checked.R, checked.n, tuple(checked.lines),
                tuple(checked.fdim),
                tuple(tuple(tuple(row) for row in frame) for frame in checked.fperp),
                checked.FULL, checked.ZERO, tuple(labels.items()),
            )
            self._entries[key] = snapshot
            if len(self._entries) > self.capacity:
                self._entries.popitem(last=False)

        # Never return the cached mutable Word or share mutable derived data
        # with it. In particular, caller mutation of a previous result cannot
        # poison a later geometry hit. Per-word nesting memoization starts empty.
        obj = original.Word.__new__(original.Word)
        obj.w = word
        obj.v, obj.R, obj.n = snapshot[:3]
        obj.lines = list(snapshot[3])
        obj.fdim = list(snapshot[4])
        obj.fperp = [[list(row) for row in frame] for frame in snapshot[5]]
        obj.FULL, obj.ZERO = snapshot[6:8]
        obj._nest = {}
        labels = dict(snapshot[8])
        full = obj.full()
        hypotheses, conclusion, info = obj.interface()
        return obj, labels, full, hypotheses, conclusion, info


_cache = GeometryCache()


def check(word):
    """Drop-in check/Reject API for PR543's unchanged mutants.py harness."""
    return _cache.check(word)


def cache_info():
    return {"hits": _cache.hits, "misses": _cache.misses,
            "entries": len(_cache._entries), "capacity": _cache.capacity}


if __name__ == "__main__":
    raise SystemExit("This is a check/Reject adapter, not a verifier CLI. Run the package's verify.py or pass this file to PR543 mutants.py.")

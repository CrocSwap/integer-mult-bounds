"""Equivalence, capacity and failure controls for exact containment reuse.

Produced by Nick Petalas. Apache-2.0.
"""

import contextlib
from fractions import Fraction
import hashlib
import io
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def load_replay(payload=None):
    path = ROOT / "replay.py"
    namespace = {"__name__": "cache_control", "__file__": str(path)}
    exec(compile(path.read_bytes() if payload is None else payload, str(path), "exec"), namespace)
    return namespace


def fixtures(source, memo_type):
    kernel = source["load_kernel"]()
    q = Fraction
    zero = (q(0),) * 6
    e0, e1 = (q(1), q(0)) + zero, (q(0), q(1)) + zero
    spaces = ((), (e0,), (e1,), ((q(1), q(1)) + zero,),
              ((q(2), q(1)) + zero,), (e1, e0))
    comparisons = 0
    for capacity in (0, 1, 2, 32768):
        memo = memo_type(kernel["contains"], capacity)
        for _ in range(3):
            for outer in spaces:
                for inner in spaces:
                    expected = kernel["contains"](outer, inner)
                    if memo(outer, inner) is not expected:
                        raise ValueError("Ordered positive/negative containment mismatch")
                    comparisons += 1
        stats = memo.statistics()
        if stats["calls"] != 108 or stats["entries"] > capacity:
            raise ValueError("Capacity exhaustion or accounting changed")
    return comparisons


def failure_controls(source, replay):
    rejected = 0
    for capacity in (-1, 32769, True, 1.0):
        try:
            replay["ContainmentMemo"](lambda _a, _b: True, capacity)
        except ValueError:
            rejected += 1
        else:
            raise ValueError("Invalid capacity accepted")
    raw = (ROOT / "replay.py").read_text()
    changes = (
        ("return self.memo[key]", "return True"),
        ("key = (outer, inner)", "key = tuple(sorted((outer, inner)))"),
    )
    for old, new in changes:
        if raw.count(old) != 1:
            raise ValueError("Mutation anchor changed")
        mutant = load_replay(raw.replace(old, new).encode())
        try:
            fixtures(source, mutant["ContainmentMemo"])
        except ValueError:
            rejected += 1
        else:
            raise ValueError("Wrong-result implementation mutant accepted")
    return rejected


def main():
    replay = load_replay()
    source = replay["authenticated_source"]()
    comparisons = fixtures(source, replay["ContainmentMemo"])
    rejected = failure_controls(source, replay)
    capture = io.StringIO()
    with contextlib.redirect_stdout(capture):
        result, stats = replay["run"]()
    if capture.getvalue() != "PASS independent complete normalized G20 census receipt\n":
        raise ValueError("CLI success output changed")
    receipt = {"status": "PASS_G20_MEMBER_BANK_CACHE", "comparisons": comparisons,
               "rejections": rejected, "cache": stats,
               "scientific_sha256": hashlib.sha256(source["canonical"](result).encode()).hexdigest(),
               "source_manifest_sha256": replay["MANIFEST_SHA256"]}
    files = sorted(p for p in ROOT.rglob("*") if p.is_file() and "__pycache__" not in p.parts)
    if len(files) > 64:
        raise ValueError("Package file bound")
    receipt["package_files_sha256"] = {
        str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()

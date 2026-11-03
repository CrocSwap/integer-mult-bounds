#!/usr/bin/env python3
"""Check the new reuse boundary, including every reached product and eviction.

This contribution was produced by Nick Petalas. Apache-2.0.
"""

from contextlib import redirect_stdout
from functools import lru_cache
from hashlib import sha256
from io import StringIO
from pathlib import Path
from statistics import median
from tempfile import TemporaryDirectory
import json
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cached import CAPACITY, MAX_SOURCE_BYTES, SOURCE, load_source, require


def full_conformance():
    namespace = load_source()
    original = namespace["mul"]
    reused = lru_cache(maxsize=CAPACITY)(original)
    calls, max_extent = 0, 0

    def checked_product(a, b, q):
        nonlocal calls, max_extent
        result = reused(a, b, q)
        require(result == original(a, b, q), "reached product differs")
        require(isinstance(result, tuple) and all(isinstance(r, tuple) for r in result),
                "cached output must be immutable")
        calls += 1
        max_extent = max(max_extent, len(a), len(a[0]), len(b), len(b[0]))
        require(max_extent <= 32 and calls <= 300000, "conformance capacity")
        return result

    namespace["mul"] = checked_product
    output = StringIO()
    try:
        with redirect_stdout(output):
            namespace["main"]()
        stats = reused.cache_info()
    finally:
        reused.cache_clear()
    digest = sha256(output.getvalue().encode()).hexdigest()
    require(digest == "ba358675b3031aef57895701547380f864223c83ef89a9f44f039714f1a97fa0",
            "complete scientific output differs")
    require(calls == 274422 and stats.hits == 128609 and stats.misses == 145813,
            "complete cache trace differs")
    require(stats.currsize == CAPACITY and reused.cache_info().currsize == 0,
            "capacity or cleanup")
    return {"calls": calls, "hits": stats.hits, "misses": stats.misses,
            "max_extent": max_extent, "stdout_sha256": digest}


def expect_rejection(action, label):
    try:
        action()
    except ValueError:
        return label
    raise ValueError("control failed: " + label)


def controls():
    namespace = load_source()
    original = namespace["mul"]
    product = lru_cache(maxsize=CAPACITY)(original)
    names = []
    a, b = ((1, 1), (0, 1)), ((1, 0), (1, 1))
    require(product(a, b, 2) != product(a, b, 3), "modulus omitted from key")
    names.append("modulus key")
    require(product(a, b, 3) != product(b, a, 3), "factor order omitted from key")
    names.append("ordered factors")
    require(product(a, b, 3) is product(a, b, 3), "hit must reuse immutable value")
    names.append("immutable reuse")
    for label, x, y in (("empty left", (), b), ("empty right", a, ()),
                        ("shape", ((1,),), b), ("ragged right", a, ((1,), (1, 2)))):
        names.append(expect_rejection(lambda: product(x, y, 3), label))
    product.cache_clear()
    for value in range(CAPACITY + 2):
        require(product(((value,),), ((2,),), 1031) == ((2 * value % 1031,),),
                "eviction stream result")
    before = product.cache_info()
    require(before.currsize == CAPACITY, "unbounded cache")
    require(product(((0,),), ((2,),), 1031) == ((0,),), "evicted recomputation")
    require(product.cache_info().misses == before.misses + 1, "oldest key not evicted")
    names.append("capacity and eviction")
    product.cache_clear()
    require(product.cache_info().currsize == 0, "cache retirement")
    names.append("explicit retirement")
    with TemporaryDirectory(prefix="schur-source-control-") as directory:
        path = Path(directory) / "changed.py"
        path.write_bytes(b"raise RuntimeError('must never execute')\n")
        names.append(expect_rejection(lambda: load_source(path), "changed source"))
        path.write_bytes(b" " * (MAX_SOURCE_BYTES + 1))
        names.append(expect_rejection(lambda: load_source(path), "oversized source"))
    return names


def benchmark_record():
    """Authenticate recorded observations without making CI repeat local timings."""
    package = Path(__file__).resolve().parent
    with (package / "BENCHMARK.json").open("rb") as stream:
        raw = stream.read(65537)
    require(len(raw) <= 65536, "benchmark receipt capacity")
    record = json.loads(raw)
    require(record["source_sha256"] == sha256(
        (package.parents[1] / SOURCE).read_bytes()).hexdigest(), "benchmark source")
    for field, name in (("implementation_sha256", "cached.py"),
                        ("harness_sha256", "benchmark.py")):
        require(record[field] == sha256((package / name).read_bytes()).hexdigest(),
                "benchmark executable bytes")
    rows = record["rounds"]
    require(5 <= len(rows) <= 15 and record["errors"] == 0, "benchmark workload")
    for row in rows:
        for side in ("baseline", "cached"):
            sample = row[side]
            require(sample["returncode"] == 0 and 0 < sample["seconds"] < 120,
                    "benchmark sample failure")
            require(sample["stdout_sha256"] ==
                    "ba358675b3031aef57895701547380f864223c83ef89a9f44f039714f1a97fa0",
                    "benchmark scientific output")
    for side in ("baseline", "cached"):
        times = [row[side]["seconds"] for row in rows]
        require(record["summary"][side] == {
            "median_seconds": median(times), "min_seconds": min(times),
            "max_seconds": max(times)}, "benchmark summary differs from raw samples")
    return {"rounds": len(rows), "errors": record["errors"]}


def main():
    trace = full_conformance()
    trace["controls"] = controls()
    require(len(trace["controls"]) == 11, "control inventory")
    trace["benchmark"] = benchmark_record()
    trace["files_sha256"] = {
        path.name: sha256(path.read_bytes()).hexdigest()
        for path in sorted(Path(__file__).resolve().parent.iterdir()) if path.is_file()
    }
    source_path = Path(__file__).resolve().parents[2] / SOURCE
    trace["source_sha256"] = sha256(source_path.read_bytes()).hexdigest()
    print(json.dumps(trace, sort_keys=True))
    print("PASS_SCHUR_NILPOTENT_CACHE calls=274422 hits=128609 controls=11")


if __name__ == "__main__":
    main()

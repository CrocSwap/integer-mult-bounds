"""One bounded A/B of the original mutation suite plus cache failure controls.

Prepared for mtpsl with substantial OpenAI Codex assistance; Apache-2.0.
"""
import argparse
import copy
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import platform
import subprocess
import sys
import tempfile
import time

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PACKAGE = Path("research/r420-geometry-cache")
SOURCE = Path("research/e8-bit-r420/code/xcheck.py")
HARNESS = Path("research/e8-bit-r420/code/mutants.py")
WORD = Path("research/e8-bit-r420/data/bitE8mut-r420.json.gz")


def need(condition, message):
    if not condition:
        raise RuntimeError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def sha(value):
    return hashlib.sha256(value).hexdigest()


def signature(result):
    obj, *receipts = result
    fields = ("v", "R", "n", "lines", "fdim", "fperp", "FULL", "ZERO")
    return {"geometry": {key: getattr(obj, key) for key in fields}, "receipts": receipts}


def outcome(check, word, reject):
    try:
        result = check(word)
    except reject as error:
        return {"accepted": False, "exception": str(error)}
    return {"accepted": all(result[3].values()) and all(result[4].values()),
            "signature_sha256": sha(canonical(signature(result)))}


def run(output):
    pins = json.loads((HERE / "SOURCES.json").read_text())
    for path, pin in pins["execution_inputs"].items():
        need(sha((ROOT / path).read_bytes()) == pin["sha256"], "input pin changed: " + path)

    benchmark = {}
    receipts = {}
    for name, checker in (("original", SOURCE), ("cached", PACKAGE / "cached_xcheck.py")):
        command = [sys.executable, "-I", "-B", str(ROOT / HARNESS), str(ROOT / checker),
                   str(ROOT / WORD), "--json", str(output / (name + ".json"))]
        start = time.perf_counter()
        proc = subprocess.run(command, capture_output=True, text=True)
        elapsed = time.perf_counter() - start
        (output / (name + ".log")).write_text(proc.stdout + proc.stderr)
        need(proc.returncode == 0, name + " mutation suite failed: " + proc.stderr[-500:])
        receipts[name] = json.loads((output / (name + ".json")).read_text())
        need(receipts[name]["status"] == "PASS_INTERLEAVED_INTERFACE_MUTATION_CONTROLS",
             name + " incorrect status")
        rows = receipts[name]["controls"]
        need(len(rows) == 10 and all(r["rejected"] for r in rows[:9])
             and not rows[9]["rejected"], name + " changed mutation coverage")
        benchmark[name + "_seconds"] = elapsed
    need(receipts["original"] == receipts["cached"], "original/cached mutation receipts differ")
    need((output / "original.log").read_bytes() == (output / "cached.log").read_bytes(),
         "original/cached diagnostics differ")
    benchmark["speedup"] = benchmark["original_seconds"] / benchmark["cached_seconds"]
    benchmark["method"] = "one original-then-cached pair, separate cold processes, identical harness/input; OS caches not flushed"

    spec = importlib.util.spec_from_file_location("cached_xcheck_test", HERE / "cached_xcheck.py")
    adapter = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(adapter)
    original = adapter.original
    base = json.loads(gzip.decompress((ROOT / WORD).read_bytes()))
    cache = adapter.GeometryCache()
    baseline = outcome(original.check, base, original.Reject)
    need(baseline["accepted"], "baseline rejected")
    need(outcome(cache.check, base, original.Reject) == baseline, "initial cached result differs")
    checks = []

    def compare(name, changed, geometry, accept=False):
        expected = outcome(original.check, changed, original.Reject)
        before = (cache.hits, cache.misses)
        actual = outcome(cache.check, changed, original.Reject)
        need(actual == expected, name + " differs from uncached checker")
        need(actual["accepted"] == accept, name + " unexpected acceptance")
        delta = (cache.hits - before[0], cache.misses - before[1])
        need(delta == ((0, 1) if geometry else (1, 0)), name + " wrong cache invalidation")
        checks.append({"case": name, "accepted": accept, "cache_miss": geometry,
                       "outcome": actual})

    # Every omitted-from-key field still receives its full per-word checks.
    mutations = []
    w = copy.deepcopy(base); w["start"][240] = 1; mutations.append(("start frame", w))
    w = copy.deepcopy(base); w["final"][240] = 0; mutations.append(("final frame", w))
    w = copy.deepcopy(base); w["A"].pop(0); mutations.append(("A gate", w))
    w = copy.deepcopy(base); w["B"].pop(0); mutations.append(("B gate", w))
    w = copy.deepcopy(base); w["C"].pop(0); mutations.append(("C cleanup", w))
    w = copy.deepcopy(base); w["D"][0][2].pop(); mutations.append(("D compensation", w))
    w = copy.deepcopy(base); w["ret"][0], w["ret"][1] = w["ret"][1], w["ret"][0]
    mutations.append(("retained totals", w))
    w = copy.deepcopy(base); w["scatter"][0] = []; mutations.append(("scatter", w))
    for name, w in mutations:
        compare(name, w, geometry=False)

    # Each geometry dependency independently forces validation, even when the
    # invalid word has the same gate stream as the previously accepted word.
    for field, value in (("h", 9), ("v", 119), ("R", 419), ("form", "wrong")):
        w = copy.deepcopy(base); w[field] = value
        compare("changed " + field, w, geometry=True)
    w = copy.deepcopy(base); w["lines"][0][0] = 3
    compare("changed label", w, geometry=True)
    w = copy.deepcopy(base); w["frames"][1].pop()
    compare("nonclosed full frame", w, geometry=True)
    miss = cache.misses
    need(not outcome(cache.check, w, original.Reject)["accepted"], "failed geometry accepted on repeat")
    need(cache.misses == miss + 1, "failed geometry was cached")
    checks.append({"case": "failed geometry is not cached", "accepted": False})

    # A new valid geometry must also be verified, not simply refused or aliased.
    reflected = copy.deepcopy(base)
    for row in reflected["lines"]:
        row[0] = -row[0]
    compare("valid reflected E8 labels", reflected, geometry=True, accept=True)
    need(outcome(cache.check, reflected, original.Reject)["accepted"], "valid reflected hit failed")

    # Results returned by check are mutable in the predecessor API. Corrupting
    # them must not corrupt private derived data used by another call.
    cache = adapter.GeometryCache()
    word = copy.deepcopy(base)
    obj, lab, *_ = cache.check(word)
    obj.lines[0] = (0,) * 8
    obj.fdim[1] = 0
    obj.fperp[2].append([1] * 8)
    obj._nest[(1, 0)] = True
    obj.v = 1
    lab["gram_det"] = 999
    need(outcome(cache.check, base, original.Reject) == baseline, "returned objects poisoned cache")
    checks.append({"case": "returned geometry and receipt mutation", "accepted": True})
    word["lines"][0][0] = 3
    need(not outcome(cache.check, word, original.Reject)["accepted"], "in-place input mutation bypassed key")
    need(outcome(cache.check, base, original.Reject) == baseline, "input mutation poisoned cache")
    checks.append({"case": "in-place source input mutation", "accepted": False})

    single = adapter.GeometryCache(capacity=1)
    for w in (base, reflected, base):
        need(outcome(single.check, w, original.Reject)["accepted"], "eviction replay failed")
    need(single.misses == 3 and single.hits == 0 and len(single._entries) == 1,
         "bounded eviction failed")
    checks.append({"case": "capacity-one eviction and revalidation", "accepted": True})

    # Exercise the unmodified adapter in a relocated minimal tree with a changed
    # predecessor. It must refuse to import before using any stale cached proof.
    relocated = output / "pin-control"
    dest = relocated / PACKAGE / "cached_xcheck.py"
    dest.parent.mkdir(parents=True)
    dest.write_bytes((HERE / "cached_xcheck.py").read_bytes())
    source = relocated / SOURCE
    source.parent.mkdir(parents=True)
    source.write_bytes((ROOT / SOURCE).read_bytes() + b"\n# changed source\n")
    proc = subprocess.run([sys.executable, "-I", "-B", str(dest)], capture_output=True, text=True)
    need(proc.returncode != 0 and "pinned xcheck source changed" in proc.stderr, "changed source pin accepted")
    checks.append({"case": "changed predecessor source pin", "accepted": False})

    result = {"status": "PASS_R420_GEOMETRY_CACHE", "benchmark": benchmark,
              "environment": {"python": sys.version.split()[0], "platform": platform.system(),
                              "machine": platform.machine()},
              "mutation_receipt_sha256": sha(canonical(receipts["original"])),
              "mutation_diagnostics_sha256": sha((output / "original.log").read_bytes()),
              "baseline_signature_sha256": baseline["signature_sha256"],
              "supplemental_checks": checks, "source_pins": pins["execution_inputs"]}
    (output / "RESULT.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print("PASS_R420_GEOMETRY_CACHE original_controls=10 supplemental_checks=" + str(len(checks)))
    print("same-input mutation suite: %.3fs -> %.3fs (%.2fx); timing is diagnostic, not an acceptance threshold"
          % (benchmark["original_seconds"], benchmark["cached_seconds"], benchmark["speedup"]))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="new output directory for logs, comparison and timings")
    args = parser.parse_args()
    if args.output:
        args.output.mkdir(parents=True, exist_ok=False)
        run(args.output.resolve())
    else:
        with tempfile.TemporaryDirectory(prefix="r420-geometry-cache-") as work:
            run(Path(work))

#!/usr/bin/env python3
"""Exact endpoint, full caller, source and arithmetic rejection checks."""

from fractions import Fraction as Q
from hashlib import sha1, sha256
import importlib.util
import json
from math import factorial
from pathlib import Path
import platform

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(condition, message):
    if not condition:
        raise ValueError(message)


def load(name):
    spec = importlib.util.spec_from_file_location("query_taylor_" + name, HERE / (name + ".py"))
    need(spec is not None and spec.loader is not None, "module loader")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def authenticate():
    manifest = json.loads((HERE / "SOURCES.json").read_text())
    rows = [row for row in manifest["files"] if row["usage"] == "input"]
    need(1 <= len(rows) <= 64, "input inventory capacity")
    for row in rows:
        path = ROOT / row["path"]
        need(path.is_file() and not path.is_symlink(), "regular source input")
        need(path.stat().st_size <= 32 * 1024 * 1024, "source byte capacity")
        raw = path.read_bytes()
        need(sha256(raw).hexdigest() == row["sha256"], "source SHA256: " + row["path"])
        blob = b"blob " + str(len(raw)).encode() + b"\0" + raw
        need(sha1(blob).hexdigest() == row["git_blob"], "source Git blob: " + row["path"])
    return len(rows)


def oracle(x):
    low = sum((x**j / factorial(j) for j in range(49)), Q(0))
    next_term = x**49 / factorial(49)
    return low, low + next_term / (1 - x / 50)


def conformance(kernel):
    count = 0
    for denominator in range(1, 18):
        for numerator in range(denominator):
            x = Q(numerator, denominator)
            need(kernel.exp_interval(x) == oracle(x), "literal powers/factorials")
            count += 1
    for bits in (256, 2048):
        for x in (Q(1, (1 << bits) + 1), Q((1 << bits) - 1, 1 << bits)):
            need(kernel.exp_interval(x) == oracle(x), "large exact denominator")
            count += 1
    bad = (Q(-1, 100), Q(1), Q(2), True, 0.5, "1/2", Q(1, 1 << 16384))
    for x in bad:
        try:
            kernel.exp_interval(x)
        except ValueError:
            continue
        raise ValueError("invalid exponential input accepted")
    need(kernel.exp_interval(Q(1, 1 << 16383)) == oracle(Q(1, 1 << 16383)),
         "inclusive bit capacity")
    return count + 1, len(bad)


def semantic_controls():
    rejected = []
    for kind in ("omitted_tail", "wrong_polynomial", "upper_rounded_down"):
        caller = load("caller")
        original_load = caller.load

        def altered(path, name):
            module = original_load(path, name)
            if path.name == "integer_exp.py":
                original = module.exp_interval

                def damaged(x):
                    low, high = original(x)
                    if kind == "omitted_tail":
                        return low, low
                    if kind == "wrong_polynomial":
                        return low + 1, high + 1
                    return low, high - Q(1, 10**20)

                module.exp_interval = damaged
            return module

        caller.load = altered
        try:
            payload, trace = caller.run("candidate", capture=True)
            # A tail mutant can preserve the rounded scientific display. Compare
            # every exact endpoint against the separate retained function too.
            engine = original_load(caller.ENGINE, "retained_endpoint_control")
            need(all(bounds == engine.exp_interval(x) for x, bounds in trace), "exact endpoint control")
        except (ValueError, AssertionError):
            rejected.append(kind)
            continue
        raise ValueError("arithmetic mutant accepted: " + kind)
    return rejected


def main():
    inputs = authenticate()
    cases, boundaries = conformance(load("integer_exp"))
    baseline, before = load("caller").run("baseline", capture=True)
    candidate, after = load("caller").run("candidate", capture=True)
    need(before == after, "every ordered exact exponential input/output")
    need(baseline["result"] == candidate["result"], "complete scientific result")
    need(baseline["work"] == candidate["work"], "complete exponential workload")
    need(candidate["work"] == {"exponential_calls": 98, "taylor_steps": 4704}, "observed workload")
    need(baseline["trace_sha256"] == candidate["trace_sha256"], "trace digest")
    mutations = semantic_controls()
    files = sorted(path for path in HERE.iterdir() if path.is_file())
    need(len(files) <= 16, "package inventory capacity")
    hashes = {path.name: sha256(path.read_bytes()).hexdigest() for path in files}
    scientific = json.dumps(candidate["result"], sort_keys=True, separators=(",", ":")).encode()
    print(json.dumps({"status": "PASS_QUERY_CONTROLLER_INTEGER_TAYLOR", "python": platform.python_version(),
                      "source_inputs": inputs, "oracle_cases": cases, "boundary_rejections": boundaries,
                      "semantic_rejections": mutations, "work": candidate["work"],
                      "trace_sha256": candidate["trace_sha256"], "scientific_sha256": sha256(scientific).hexdigest(),
                      "package_sha256": hashes}, sort_keys=True))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Check the new symmetric-power implementation and its complete consumer."""
import hashlib
import json
from pathlib import Path
from types import ModuleType


PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
SOURCE = ROOT / "research/alternating-plane-spectral-copy"
DIGESTS = {
    "verify.py": "c526f2198b3df8502f302b7d80c2fe546a819048ba390e0df3a5fa28e72a12b5",
    "RESULT.json": "4e05ba9431e6e698e509ecf35f9db29f4ea4cb66a45399b373ece21d4d85cad9",
    "README.md": "6c270429599180ddc3185ba3026d549ca27dfe1f8a9cd493f0d20b0dcee28ccd",
}
HEADER = (
    "# Retained primary verifier: Ali Romman, PR5624, Apache-2.0.\n"
    "# Symmetric adjacency-power evaluation: Nick Petalas.\n"
    "# See README.md for the exact source adapter and equivalence proof.\n"
)
OLD = "power = [[sum(power[k][j] for k in row) for j in range(n)] for row in neighbors]"
NEW = "power = symmetric_step(neighbors, power)"


def need(ok, message):
    if not ok:
        raise ValueError(message)


def bounded_read(path):
    need(path.is_file() and path.stat().st_size <= 1048576, "file boundary")
    return path.read_bytes()


def authenticate(files):
    need(set(files) == set(DIGESTS), "source inventory")
    for name, digest in DIGESTS.items():
        need(hashlib.sha256(files[name]).hexdigest() == digest, "source digest " + name)


def adapter(original, candidate):
    need(original.count(OLD) == 1, "unique original recurrence")
    start = candidate.index("def symmetric_step(neighbors, power):\n")
    end = candidate.index("def compute():\n", start)
    helper = candidate[start:end]
    need(candidate.count("def symmetric_step(") == 1, "unique helper")
    expected = original.replace(
        "# SPDX-License-Identifier: Apache-2.0\n",
        "# SPDX-License-Identifier: Apache-2.0\n" + HEADER,
        1,
    ).replace("def compute():\n", helper + "def compute():\n", 1)
    expected = expected.replace(OLD, NEW, 1)
    need(candidate == expected, "exact source adapter")
    return helper


def load_module(text, name, path):
    module = ModuleType(name)
    module.__file__ = str(path)
    exec(compile(text, str(path), "exec"), module.__dict__)
    return module


def literal_step(neighbors, power):
    return [
        [sum(power[k][j] for k in row) for j in range(len(neighbors))]
        for row in neighbors
    ]


def simple_graphs(n):
    edges = [(i, j) for i in range(n) for j in range(i + 1, n)]
    for mask in range(1 << len(edges)):
        rows = [[] for _ in range(n)]
        for bit, (i, j) in enumerate(edges):
            if mask >> bit & 1:
                rows[i].append(j)
                rows[j].append(i)
        yield rows


def small_graph_checks(step):
    graphs = entries = terms = 0
    for n in range(1, 6):
        for neighbors in simple_graphs(n):
            graphs += 1
            power = [[int(i == j) for j in range(n)] for i in range(n)]
            for _ in range(5):
                expected = literal_step(neighbors, power)
                result = step(neighbors, power)
                need(result == expected, "small graph power")
                need(result is not power, "fresh matrix")
                entries += n * n
                terms += sum((n - i) * len(row) for i, row in enumerate(neighbors))
                power = result
    return {"graphs": graphs, "power_entry_comparisons": entries, "terms": terms}


def complete_check(original, optimized, expected):
    baseline = original.compute()
    need(baseline == expected, "original complete result")
    step = optimized.symmetric_step
    observations = []

    def compared_step(neighbors, power):
        reference = literal_step(neighbors, power)
        before = tuple(tuple(row) for row in power)
        result = step(neighbors, power)
        need(result == reference, "reached full matrix")
        need(tuple(tuple(row) for row in power) == before, "input mutated")
        n = len(neighbors)
        old_terms = n * sum(map(len, neighbors))
        new_terms = sum((n - i) * len(row) for i, row in enumerate(neighbors))
        observations.append([n * n, old_terms, new_terms])
        return result

    optimized.symmetric_step = compared_step
    try:
        result = optimized.compute()
    finally:
        optimized.symmetric_step = step
    need(result == baseline, "complete result equivalence")
    need(len(observations) == 5, "five reached powers")
    need(all(row == [112896, 2257920, 1132320] for row in observations), "operation counts")
    return {"power_steps": len(observations), "observations": observations,
            "saved_integer_terms": sum(row[1] - row[2] for row in observations)}


def rejected(operation):
    try:
        operation()
    except (ValueError, KeyError):
        return
    raise ValueError("negative control accepted")


def controls(files, original, candidate, step):
    count = 0
    for name in DIGESTS:
        changed = dict(files)
        changed[name] += b"\n"
        rejected(lambda: authenticate(changed))
        count += 1
    rejected(lambda: authenticate({}))
    rejected(lambda: authenticate({**files, "extra": b""}))
    rejected(lambda: adapter(original.replace(OLD, "pass"), candidate))
    rejected(lambda: adapter(original, candidate.replace("prime = 65537", "prime = 65539")))
    rejected(lambda: adapter(original, candidate.replace(NEW, OLD)))
    count += 5
    # Symmetric inputs alone do not establish that their product is symmetric.
    for neighbors, power in [
        ([[1], []], [[1, 0], [0, 1]]),
        ([[1], [0]], [[1, 0], [0, 2]]),
    ]:
        rejected(lambda: need(step(neighbors, power) == literal_step(neighbors, power), "premise"))
        count += 1
    for power in ([[1, -2], [-2, 1]], [[0, 0], [0, 0]]):
        need(step([[1], [0]], power) == literal_step([[1], [0]], power), "signed commuting control")
    return {"rejection_controls": count, "signed_or_zero_commuting_controls": 2}


def timing_check(data, candidate):
    need(data["schema"] == "symmetric-spectral-benchmark/1", "benchmark schema")
    need(data["source_sha256"] == {
        "baseline": DIGESTS["verify.py"],
        "candidate": hashlib.sha256(candidate.encode()).hexdigest(),
    }, "benchmark source binding")
    need(data["result_sha256"] == DIGESTS["RESULT.json"], "benchmark result binding")
    need(len(data["pairs"]) == 5 and data["failures"] == 0, "benchmark coverage")
    output_hash = hashlib.sha256(b"PASS_ALTERNATING_PLANE_SPECTRAL_COPY\n").hexdigest()
    for pair in data["pairs"]:
        need(set(pair) == {"baseline", "candidate"}, "benchmark pair")
        for result in pair.values():
            need(type(result["elapsed_ns"]) is int and 0 < result["elapsed_ns"] < 30_000_000_000,
                 "benchmark time")
            need(result["returncode"] == 0 and result["stderr_bytes"] == 0,
                 "benchmark success")
            need(result["stdout_sha256"] == output_hash, "benchmark complete output")
    for name in ("baseline", "candidate"):
        times = sorted(pair[name]["elapsed_ns"] for pair in data["pairs"])
        need(data["summary"][name] == {
            "median_ns": times[2], "min_ns": times[0], "max_ns": times[-1],
        }, "benchmark summary")
    base = data["summary"]["baseline"]["median_ns"]
    fast = data["summary"]["candidate"]["median_ns"]
    need(data["median_time_reduction_percent"] == 100 * (base - fast) / base,
         "benchmark arithmetic")
    improves = all(p["candidate"]["elapsed_ns"] < p["baseline"]["elapsed_ns"] for p in data["pairs"])
    need(data["all_pairs_improve"] == improves, "benchmark pair comparison")
    return {"recorded_pairs": 5, "recorded_failures": 0, "timing_is_local_evidence": True}


def receipt(result):
    names = ("README.md", "TASK.json", "SOURCES.json", "VERIFY.json", "RESULT.json",
             "replay.py", "verify.py", "benchmark.py", "BENCHMARK.json")
    hashes = {name: hashlib.sha256(bounded_read(PACKAGE / name)).hexdigest() for name in names}
    return {"status": "PASS_SYMMETRIC_SPECTRAL_REPLAY", "evidence": result,
            "package_sha256": hashes, "new_kappa": False}


def main():
    files = {name: bounded_read(SOURCE / name) for name in DIGESTS}
    authenticate(files)
    original_text = files["verify.py"].decode()
    candidate = bounded_read(PACKAGE / "replay.py").decode()
    adapter(original_text, candidate)
    need(bounded_read(PACKAGE / "RESULT.json") == files["RESULT.json"], "retained result bytes")
    original = load_module(original_text, "retained_spectral", SOURCE / "verify.py")
    optimized = load_module(candidate, "symmetric_spectral", PACKAGE / "replay.py")
    result = {"complete": complete_check(original, optimized, json.loads(files["RESULT.json"])),
              "small_graphs": small_graph_checks(optimized.symmetric_step),
              "controls": controls(files, original_text, candidate, optimized.symmetric_step),
              "benchmark": timing_check(json.loads(bounded_read(PACKAGE / "BENCHMARK.json")), candidate)}
    print(json.dumps(receipt(result), sort_keys=True, indent=2))


if __name__ == "__main__":
    main()

"""Check the new transform and complete compatibility, with no runtime threshold."""
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import benchmark
import planner
import source
import workload


def require(ok, message):
    if not ok:
        raise ValueError(message)


def transform_exhaustion():
    checked = 0
    digest = hashlib.sha256()
    for costs in itertools.product((None, 0, 1, 2), repeat=4):
        for ranks in itertools.permutations(range(4)):
            for weights in ((1, 1), (2, 5)):
                result = planner.distance_transform(costs, ranks, weights)
                expected = []
                for k in range(4):
                    candidates = [(c + sum(weights[j] for j in range(2) if (h ^ k) >> j & 1),
                                   ranks[h], h) for h, c in enumerate(costs) if c is not None]
                    expected.append(min(candidates) if candidates else None)
                require(result == expected, "hypercube transform or tie rank disagrees")
                digest.update(json.dumps(result, separators=(",", ":")).encode())
                checked += 1
    return {"complete_transforms": checked, "labels": 4 * checked,
            "sha256": digest.hexdigest()}


def complete_compatibility():
    consumer = source.load_consumer()
    original = consumer.model.solve
    counts = {"successful_calls": 0, "matched_rejections": 0}

    def compare(*args, **kwargs):
        try:
            expected = original(*args, **kwargs)
        except ValueError:
            try:
                planner.solve(*args, **kwargs)
            except ValueError:
                counts["matched_rejections"] += 1
                raise
            raise RuntimeError("a predecessor rejection was lost")
        actual = planner.solve(*args, **kwargs)
        require(actual == expected, "complete returned value differs")
        counts["successful_calls"] += 1
        return actual

    consumer.model.solve = compare
    result = consumer.build()
    require(counts["matched_rejections"] == 3, "source rejection coverage changed")
    expected = json.loads((source.SOURCE / "CERTIFICATE.json").read_text())
    require(result == expected, "complete compatibility consumer changed")
    return {**counts, "complete_certificate_sha256": benchmark.digest(result),
            "source_controls_retained": len(result["controls"])}


def pipeline_compatibility():
    model = source.load_model()
    records = []
    for d, rounds in ((1, 1), (3, 2), (4, 1), (6, 2), (8, 1), (8, 4)):
        spec = workload.specification(d, rounds)
        for mixed in (False, True):
            original = workload.prepare(model, model.solve, spec, mixed)
            actual = workload.prepare(model, planner.solve, spec, mixed)
            require(actual == original, "complete preparation pipeline differs")
            records.append({"width": d, "stages": len(spec["steps"]), "mixed": mixed,
                            "cost": actual["plan"]["cost"], "sha256": benchmark.digest(actual)})
    return records


def controls():
    cases = [
        (0, [], [], None), (9, [], [1] * 9, None),
        (2, [(0, 0)] * 257, [1, 1], None),
        (2, [], [1, 0], None), (2, [], [1, -1], None),
        (2, [], [1, 1 << 256], None), (2, [(4, 0)], [1, 1], None),
        (2, [(1, 2)], [1, 1], None), (2, [(0, 1)], [1, 1], None),
        (2, [(1, 1)], [1, 1], []), (2, [(1, 1)], [1, 1], [False]),
    ]
    rejected = 0
    for args in cases:
        try:
            planner.solve(*args)
        except ValueError:
            rejected += 1
    require(rejected == len(cases), "invalid-domain control was accepted")
    tie = planner.distance_transform([0, 1, None, None], [1, 0, None, None], [1, 1])
    require(tie[3] == (2, 0, 1), "path-rank tie control failed")
    require(planner.solve(2, [], [1, 1])["path"] == [0], "empty path changed")
    require(planner.solve(2, [(0, 1)], [1, 1], [3])["cost"] == 3,
            "paid zero-reader defect changed")
    boundary = planner.solve(8, [(0, 0)] * 256, [1 << 255] * 8)
    require(boundary["cost"] == 0 and boundary["path"] == [0] * 257,
            "valid maximum-resource input changed")
    try:
        source.check_digest(b"corrupted source", "0" * 64, "control.py")
    except ValueError:
        pass
    else:
        raise ValueError("source corruption was accepted")
    return {"domain_rejections": rejected, "semantic_controls": 5}


def operation_counts():
    model = source.load_model()
    result = workload.prepare(model, planner.solve, workload.specification(), True)
    tables = result["plan"]["tables"]
    size = len(tables[0])
    baseline = sum(1 for table in tables[:-1] for _ in range(size)
                   for cost in table if cost is not None)
    transform = sum(2 for _ in tables[:-1] for j in range(8)
                    for block in range(0, size, 2 << j)
                    for _ in range(block, block + (1 << j)))
    return {"baseline_predecessor_candidates": baseline,
            "transform_directed_edge_slots": transform,
            "complete_preparation_sha256": benchmark.digest(result)}


def build():
    return {"schema_version": 1, "claim_type": "scoped algorithmic proof and finite conformance",
            "transform": transform_exhaustion(), "compatibility": complete_compatibility(),
            "pipelines": pipeline_compatibility(), "controls": controls(),
            "operations": operation_counts(), "files_sha256": benchmark.file_hashes(),
            "verifier_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    args = parser.parse_args()
    actual = build()
    if args.emit:
        print(json.dumps(actual, indent=2, sort_keys=True))
        return
    expected = json.loads((HERE / "RESULT.json").read_text())
    require(actual == expected, "committed result differs")
    measured = json.loads((HERE / "BENCHMARK.json").read_text())
    require(measured["files_sha256"] == benchmark.file_hashes(), "stale benchmark source binding")
    require(all(x["output"]["sha256"] == actual["operations"]["complete_preparation_sha256"]
                for x in measured["records"]), "benchmark used different work")
    print("PASS_OBSERVABLE_HAMMING_TRANSFORM "
          + json.dumps({"transforms": actual["transform"]["complete_transforms"],
                        **actual["compatibility"], **actual["operations"]}, sort_keys=True))


if __name__ == "__main__":
    main()

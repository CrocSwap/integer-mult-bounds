"""Read-only exact synthesis, independent frontier and dirty-map replay."""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import random

HERE = Path(__file__).resolve().parent


def need(ok, message):
    if not ok:
        raise ValueError(message)


def module(name):
    spec = importlib.util.spec_from_file_location(name, HERE / (name+".py"))
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


def pins():
    for item in json.loads((HERE / "PREDECESSORS.json").read_text())["files"]:
        data = (HERE / item["retained_path"]).read_bytes()
        need(hashlib.sha256(data).hexdigest() == item["sha256"], "predecessor SHA256 mismatch")
        blob = b"blob " + str(len(data)).encode() + b"\0" + data
        need(hashlib.sha1(blob).hexdigest() == item["git_blob"], "predecessor Git blob mismatch")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-receipt", action="store_true")
    args = parser.parse_args()
    pins()
    s, independent = module("synth"), module("independent")
    spec = importlib.util.spec_from_file_location("credited_baseline", HERE / "sources/PR2208-walk.py")
    baseline = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(baseline)
    _, baseline_counts = baseline.construct([2, 0, 1, 2, 1, 0], [1, 2, 1])
    need((baseline_counts["readout_calls"], baseline_counts["transfers"]) == (14, 10),
         "credited chosen-decomposition baseline drift")
    cases = [([2, 0, 1, 2, 1, 0], [1, 2, 1]),
             ([0, 1, 2, 0, 1, 2], [1, 2, 3]),
             ([3, 2, 0, 1, 3, 2, 1, 0], [1, 2, 1, 3]),
             ([0, 1, 2, 3, 0, 2, 3, 1], [1, 1, 2, 3])]
    records = []
    rng = random.Random(20261015)
    columns = 0
    for source, colors in cases:
        n = len(colors)
        targets = list(range(1, 1 << n))
        record = s.synthesize(source, colors, targets)
        other = independent.frontier(source, colors, targets, record["transfers"])
        for field in ("minimum_reads", "lower_frontier_counts", "lower_frontier_sha256"):
            need(record[field] == other[field], "independent complete frontier disagreement: " + field)
        record["independent"] = other
        need([op[1] for op in record["program"] if op[0] == "B"] == source, "source order changed")
        need(all(op[2] == 0 for op in record["program"] if op[0] in ("A", "B")), "nonfixed port")
        for trial in range(16):
            maps = {"B": [(rng.randrange(4), rng.randrange(4)) for _ in colors],
                    "A": {t: (rng.randrange(4), rng.randrange(4)) for t in targets}}
            columns += independent.dense(record["program"], n, targets, maps)
        records.append(record)
    need([r["transfers"] for r in records] == [6, 12, 12, 12], "optimum drift")
    controls = []
    first = records[0]
    identity = {"B": [(1, 2)] * 3, "A": {t: (1, 2) for t in range(1, 8)}}
    for name, mutate in (
        ("omit_source", lambda p: p[:next(i for i, op in enumerate(p) if op[0] == "B")] + p[next(i for i, op in enumerate(p) if op[0] == "B")+1:]),
        ("omit_transfer", lambda p: p[:next(i for i, op in enumerate(p) if op[0] == "C")] + p[next(i for i, op in enumerate(p) if op[0] == "C")+1:]),
        ("read_wrong_port", lambda p: [[*op[:2], 1] if op[0] == "A" else op for op in p])):
        try:
            independent.dense(mutate(first["program"]), 3, list(range(1, 8)), identity)
        except ValueError:
            controls.append(name)
        else:
            raise ValueError("accepted control " + name)
    for name, call in (
        ("false_shorter_optimum", lambda: independent.frontier(cases[0][0], cases[0][1], list(range(1, 8)), 5)),
        ("state_cap_is_failure", lambda: s.synthesize(cases[0][0], cases[0][1], list(range(1, 8)), state_cap=1))):
        try:
            call()
        except ValueError:
            controls.append(name)
        else:
            raise ValueError("accepted control " + name)
    receipt = {"schema_version": 1, "records": records, "dense_basis_columns": columns,
               "semantic_controls": controls}
    destination = HERE / "RESULT.json"
    if args.write_receipt:
        need(not destination.exists(), "refuse receipt overwrite")
        destination.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    else:
        need(receipt == json.loads(destination.read_text()), "receipt mismatch")
    print("PASS_JOINT_CONNECTOR_READ_SYNTHESIS cases=4 transfer_optima=6,12,12,12 controls=5 dense_columns=" + str(columns))


if __name__ == "__main__":
    main()

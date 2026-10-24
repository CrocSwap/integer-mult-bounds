"""Check that material damage to a gauge proof is rejected."""

from collections import Counter
from copy import deepcopy
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import argparse
import gzip
import json
import tempfile


def main(args):
    spec = spec_from_file_location("review", Path(__file__).with_name("review_wire_gauge.py"))
    review = module_from_spec(spec)
    spec.loader.exec_module(review)
    word, programs = review.load_source()
    certificate = json.loads(gzip.decompress(args.certificate.read_bytes()))
    native = review.rebuild_graph(word, programs[certificate["orientation"]], certificate)
    count = len(certificate["graph"]["labels"])
    entry = certificate["lines"][0]
    line = entry["line"]
    lagrangians = list(map(review.lagrangian, word["frames"]))
    changed = [review.transform(rows, line) for rows in lagrangians]
    deltas = [len(review.gf2_basis(lagrangians[b] + changed[a])) - 9 - rank
              for _, _, b, a, rank, _, _ in native]
    edges = Counter()
    for edge, delta in zip(native, deltas):
        if edge[0] != edge[1]:
            edges[tuple(sorted(edge[:2]))] += delta
    edges = {pair: weight for pair, weight in edges.items() if weight}
    original_case = next(case for case in entry["cases"] if case["flow"])
    records = []

    def rejects(name, operation, expected):
        try:
            operation()
        except ValueError as error:
            review.check(str(error) == expected, "A negative control failed at the wrong check: " + name)
            records.append(dict(control=name, rejected_by=str(error)))
        else:
            raise ValueError("A damaged certificate passed: " + name)

    changed_program = deepcopy(programs["forward"])
    gate = next(event[1] for event in reversed(changed_program)
                if event[0] == "scalar" and event[1][0] == "add")
    gate[3] += gate[4]
    rejects("Changed final scalar coefficient", lambda: review.scalar_endpoint(word, changed_program, False),
            "The original scalar endpoint is not the stated dirty shear")

    damaged = deepcopy(certificate)
    wrapper = next(i for i, edge in enumerate(damaged["graph"]["edges"]) if edge[4] == 0)
    damaged["graph"]["edges"].pop(wrapper)
    rejects("Omitted rank-zero wrapper", lambda: review.rebuild_graph(word, programs["forward"], damaged),
            "Native edge count")

    case = deepcopy(original_case)
    case["flow"][0][2] += 1000000
    rejects("Flow exceeds capacity", lambda: review.check_case(case, edges, native, deltas, count, dict(case["fixed"])),
            "Flow capacity")

    case = deepcopy(original_case)
    case["rank_delta"] += 1
    rejects("False objective", lambda: review.check_case(case, edges, native, deltas, count, dict(case["fixed"])),
            "Exact objective")

    case = deepcopy(original_case)
    node, bit = case["fixed"][0]
    if node in case["flipped_frames"]:
        case["flipped_frames"].remove(node)
    else:
        case["flipped_frames"].append(node)
    rejects("Cut violates its branch", lambda: review.check_case(case, edges, native, deltas, count, dict(case["fixed"])),
            "Cut violates a fixed bit")

    damaged = deepcopy(certificate)
    position = next(i for i, case in enumerate(damaged["lines"][0]["cases"])
                    if case["forced_centre_cross"] is not None)
    damaged["lines"][0]["cases"].pop(position)
    with tempfile.TemporaryDirectory(prefix="centre-gauge-control-") as directory:
        path = Path(directory) / "missing-case.json.gz"
        path.write_bytes(gzip.compress(json.dumps(damaged).encode(), mtime=0))
        rejects("Omitted forced-centre branch", lambda: review.run(path),
                "The exhaustive branch list is incomplete")

    output = dict(status="PASS_GAUGE_NEGATIVE_CONTROLS", controls=records)
    args.out.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
    print(output["status"] + " controls=" + str(len(records)))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--certificate", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    main(parser.parse_args())

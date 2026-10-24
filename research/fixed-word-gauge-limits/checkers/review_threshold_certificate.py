"""Check capped-rank witnesses by exact source ranks and flow/cut duality."""

from collections import Counter
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from itertools import product
from pathlib import Path
import argparse
import gzip
import json


def main(args):
    spec = spec_from_file_location("review", Path(__file__).with_name("review_wire_gauge.py"))
    review = module_from_spec(spec)
    spec.loader.exec_module(review)
    raw = args.certificate.read_bytes()
    certificate = json.loads(gzip.decompress(raw))
    source_raw = args.source_certificate.read_bytes()
    review.check(certificate["source_certificate_sha256"] == sha256(source_raw).hexdigest(), "Graph certificate pin")
    source = json.loads(gzip.decompress(source_raw))
    word, programs = review.load_source()
    review.check_orientation_duality(word, programs)
    native = review.rebuild_graph(word, programs[source["orientation"]], source)
    lagrangians = list(map(review.lagrangian, word["frames"]))
    count = len(source["graph"]["labels"])
    summary = []
    expected_lines = sorted(set.intersection(*(review.frame_span(word["frames"][i]) for i in word["center_frames"])))
    expected_lines = [line for line in expected_lines if line.bit_count() % 2]
    review.check(sorted(e["line"] for e in certificate["lines"]) == expected_lines, "Common-line coverage")
    for record in certificate["lines"]:
        line = record["line"]
        changed = [review.transform(rows, line) for rows in lagrangians]
        rank_by_pair = {}
        for _, _, before, after, old_rank, _, _ in native:
            if (before, after) not in rank_by_pair:
                old = len(review.gf2_basis(lagrangians[before] + lagrangians[after])) - 9
                new = len(review.gf2_basis(lagrangians[before] + changed[after])) - 9
                review.check(old == old_rank and 0 <= new <= 8, "Exact native rank")
                rank_by_pair[before, after] = (old, new)
        review.check(sorted(t["cap"] for t in record["thresholds"]) == list(range(1, 9)), "Threshold coverage")
        values = []
        for threshold in record["thresholds"]:
            cap = threshold["cap"]
            edges = Counter()
            for u, v, before, after, _, _, _ in native:
                old, new = rank_by_pair[before, after]
                if u != v:
                    edges[tuple(sorted((u, v)))] += min(new, cap) - min(old, cap)
            edges = {pair: weight for pair, weight in edges.items() if weight}
            cover = threshold["negative_cover"]
            review.check(len(set(cover)) == len(cover) and set(cover) <= set(range(count)), "Threshold cover vertices")
            review.check(all(set(pair) & set(cover) for pair, weight in edges.items() if weight < 0), "Threshold negative cover")
            expected = set(product((0, 1), repeat=len(cover)))
            seen = set()
            minima = []
            for case in threshold["cases"]:
                branch = tuple(case["branch"])
                review.check(branch in expected and branch not in seen, "Threshold branch coverage")
                seen.add(branch)
                value, _, _, _ = review.check_flow_cut(case, edges, count, dict(zip(cover, branch)), case["objective_delta"])
                minima.append(value)
            review.check(seen == expected, "A threshold branch was omitted")
            minimum = min(minima)
            review.check(minimum == threshold["minimum_delta"] == 0, "A capped-rank improvement exists")
            values.append(dict(cap=cap, minimum_delta=minimum, flow_cut_cases=len(minima)))
        summary.append(dict(line=line, thresholds=values))
    result = dict(status="PASS_INCREASING_CONCAVE_RANK_COST_OBSTRUCTION",
                  certificate_sha256=sha256(raw).hexdigest(),
                  source_certificate_sha256=sha256(source_raw).hexdigest(), source_base=review.BASE,
                  forward_backward_gauge_graph_isomorphism=True,
                  lines=summary, total_flow_cut_cases=sum(t["flow_cut_cases"] for e in summary for t in e["thresholds"]),
                  conclusion="Every common odd-line binary gauge has nonnegative delta for every increasing concave function f of native rank with f(0)=0.",
                  recurrence_scope="This includes sum r^(1-b) for 0<=b<1 and the count of positive-rank children at b=1. It excludes changed scalar schedules and other gauge families.")
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"])
    print("lines=" + str(len(summary)) + " threshold_flow_cut_cases=" + str(result["total_flow_cut_cases"]))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-certificate", type=Path, required=True)
    parser.add_argument("--certificate", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    main(parser.parse_args())

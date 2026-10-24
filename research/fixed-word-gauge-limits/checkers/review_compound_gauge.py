"""Independently check two compound binary gauges on the old supplier."""

from collections import Counter
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from itertools import product
from pathlib import Path
import argparse
import gzip
import json


def pairing(left, right):
    return (((left & 511) & (right >> 9)).bit_count() +
            ((left >> 9) & (right & 511)).bit_count()) % 2


def frame_transvections(frame, review):
    basis = list(frame)
    for unit in (1 << j for j in range(9)):
        if len(review.gf2_basis(basis + [unit])) > len(basis):
            basis.append(unit)
    review.check(len(basis) == 9, "A canonical basis was not completed")
    dual = [next(x for x in range(512) if all((x & u).bit_count() % 2 == (j == k)
                                            for k, u in enumerate(basis))) for j in range(9)]
    return [u | ((u ^ dual[j]) << 9) for j, u in enumerate(frame)]


def apply_transvections(value, vectors):
    for vector in vectors:
        if pairing(value, vector):
            value ^= vector
    return value


def main(args):
    spec = spec_from_file_location("review", Path(__file__).with_name("review_wire_gauge.py"))
    review = module_from_spec(spec)
    spec.loader.exec_module(review)
    raw = args.certificate.read_bytes()
    certificate = json.loads(gzip.decompress(raw))
    review.check(certificate["source_base"] == review.BASE, "Compound source base")
    word, programs = review.load_source()
    review.check_orientation_duality(word, programs)
    native = review.rebuild_graph(word, programs["forward"], certificate)
    gauge = certificate["gauge"]
    if "product_lines" in gauge:
        vectors = gauge["product_lines"]
        review.check(all(0 < a < 512 for a in vectors), "Product line range")
    else:
        frame = word["frames"][gauge["frame"]]
        review.check(frame == gauge["basis"], "Compound canonical frame pin")
        vectors = frame_transvections(frame, review)
    review.check(all(pairing(u, v) == 0 for u in vectors for v in vectors), "Commuting transvections")
    images = [apply_transvections(1 << j, vectors) for j in range(18)]
    review.check(all(apply_transvections(value, vectors) == 1 << j for j, value in enumerate(images)),
                 "Binary gauge involution")
    lagrangians = list(map(review.lagrangian, word["frames"]))
    changed = [[apply_transvections(value, vectors) for value in rows] for rows in lagrangians]
    pair_delta = {}
    for _, _, before, after, old, _, _ in native:
        if (before, after) in pair_delta:
            continue
        check_old = len(review.gf2_basis(lagrangians[before] + lagrangians[after])) - 9
        left = len(review.gf2_basis(changed[before] + lagrangians[after])) - 9
        right = len(review.gf2_basis(lagrangians[before] + changed[after])) - 9
        both = len(review.gf2_basis(changed[before] + changed[after])) - 9
        review.check(check_old == old == both and left == right, "Compound relative rank")
        pair_delta[before, after] = left - old
    deltas = [pair_delta[edge[2], edge[3]] for edge in native]
    review.check(dict(Counter(deltas)) == {int(k): v for k, v in certificate["edge_delta_counts"].items()},
                 "Compound rank inventory")
    edges = Counter()
    for edge, delta in zip(native, deltas):
        if edge[0] != edge[1]:
            edges[tuple(sorted(edge[:2]))] += delta
    edges = {pair: weight for pair, weight in edges.items() if weight}
    count = len(certificate["graph"]["labels"])
    cover = certificate["negative_cover"]
    review.check(len(set(cover)) == len(cover) and set(cover) <= set(range(count)), "Compound cover")
    review.check(all(set(pair) & set(cover) for pair, weight in edges.items() if weight < 0), "Compound negative cover")
    expected = set(product((0, 1), repeat=len(cover)))
    seen, values, rigidity = set(), [], []
    for original_case in certificate["cases"]:
        case = dict(original_case, forced_centre_cross=None)
        branch = tuple(case["branch"])
        review.check(branch in expected and branch not in seen, "Compound branch coverage")
        seen.add(branch)
        value, zero = review.check_case(case, edges, native, deltas, count, dict(zip(cover, branch)))
        values.append(value)
        if zero is not None:
            rigidity.append(zero)
    review.check(seen == expected and min(values) == certificate["certified_minimum"] == 0,
                 "Compound exact minimum")
    thresholds = []
    if "thresholds" in certificate:
        review.check([rec["cap"] for rec in certificate["thresholds"]] == list(range(1, 10)),
                     "Compound threshold coverage")
        for receipt in certificate["thresholds"]:
            cap = receipt["cap"]
            weighted = Counter()
            for edge, delta in zip(native, deltas):
                u, v, _, _, rank, _, _ = edge
                if u != v:
                    weighted[tuple(sorted((u, v)))] += min(rank + delta, cap) - min(rank, cap)
            weighted = {pair: weight for pair, weight in weighted.items() if weight}
            cover = receipt["negative_cover"]
            review.check(len(set(cover)) == len(cover) and set(cover) <= set(range(count)), "Compound threshold cover")
            review.check(all(set(pair) & set(cover) for pair, weight in weighted.items() if weight < 0),
                         "Compound threshold negative cover")
            expected = set(product((0, 1), repeat=len(cover)))
            seen, energies = set(), []
            best = None
            for case in receipt["cases"]:
                branch = tuple(case["branch"])
                review.check(branch in expected and branch not in seen, "Compound threshold branch coverage")
                seen.add(branch)
                energy, _, _, selected = review.check_flow_cut(case, weighted, count, dict(zip(cover, branch)), case["objective_delta"])
                review.check_profile(case, native, deltas, selected)
                energies.append(energy)
                if best is None or energy < best["objective_delta"]:
                    best = dict(objective_delta=energy, rank_delta=case["rank_delta"], profile=case["profile"])
            review.check(seen == expected and min(energies) == receipt["minimum"], "Compound threshold exact minimum")
            thresholds.append(dict(cap=cap, minimum=min(energies), cases=len(energies), best=best))
    result = dict(status="PASS_COMPOUND_GAUGE_RANK_AND_RIGIDITY", source_base=review.BASE,
                  certificate_sha256=sha256(raw).hexdigest(), gauge=gauge,
                  exact_native_rank_pairs=len(pair_delta), all_flow_cut_cases=len(values),
                  minimum_rank_delta=min(values), maximum_total_negative_rank_mass=sum(-d for d in deltas if d < 0),
                  zero_cut_rigidity=rigidity, forward_backward_gauge_graph_isomorphism=True,
                  backward_gauge=(gauge if "product_lines" in gauge else dict(conjugated_by_full_frame=gauge)),
                  thresholds=thresholds,
                  scope="Binary gauges I,G on actual segments, with the old scalar schedule and paired endpoints. No changed native lowering is admitted.")
    if thresholds and gauge.get("frame") == 415:
        review.check([record["minimum"] for record in thresholds] == [-1] + [0] * 8,
                     "The centre-frame threshold premise changed")
        review.check(all(delta % 2 == 0 for delta in deltas), "Even rank increments")
        review.check(49 ** 5 > 81 * 20 ** 5 and 303 ** 5 < 8 * 200 ** 5,
                     "Rational fifth-power bounds")
        result["moment_obstruction"] = dict(saving_parameter_range=["0", "2/5"],
            lower_bound_for_every_changed_native_cut="47/9800 (strict)",
            rank_zero_cuts="All native gauges are constant, so the child profile is unchanged.",
            proof="The threshold cone gives delta >= 2*(9^(1-b)-8^(1-b))-(2-2^(1-b)); the exact fifth-power bounds give >47/9800.")
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"] + " cases=" + str(len(values)))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--certificate", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    main(parser.parse_args())

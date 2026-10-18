#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Replay a mixed COPY62 support witness and its exact coefficient obstruction."""
import argparse
from fractions import Fraction
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import screen
import family


def require(condition, message):
    if not condition:
        raise ValueError(message)


def rank_low(rows):
    """Second F2 elimination, using least rather than greatest pivots."""
    pivots = {}
    for row in rows:
        while row:
            bit = row & -row
            if bit in pivots:
                row ^= pivots[bit]
            else:
                pivots[bit] = row
                break
    return len(pivots)


def decode(data, pairing, supports, witness):
    require(witness["coordinate_root"] in data["punctured_frame"], "coordinate must be punctured")
    require(len(witness["terms"]) == 9, "nine rank-six rectangles required")
    terms, invoices = [], []
    for a, b, encoded in witness["terms"]:
        require(type(a) is int and type(b) is int and 0 <= a < 240 and 0 <= b < 240, "parent tag")
        left, right = supports[a], supports[b]
        cut = int(encoded, 16)
        require(screen.engine.rank(pairing, left, right) == 7, "rank-seven parent")
        require(cut in screen.engine.column_code(pairing, left, right), "maximal slice codeword")
        left ^= cut
        ranks = (screen.engine.rank(pairing, left, right),
                 rank_low(pairing[i] & right for i in screen.engine.bits(left)))
        require(ranks == (6, 6), "independent COPY6 ranks")
        terms.append((left, right))
        invoices.append(6)
    coordinate = supports[2 * witness["coordinate_root"]]
    require(screen.engine.rank(pairing, coordinate, coordinate) == 8, "coordinate COPY8")
    require(rank_low(pairing[i] & coordinate for i in screen.engine.bits(coordinate)) == 8,
            "independent coordinate COPY8")
    terms.append((coordinate, coordinate))
    invoices.append(8)
    return terms, invoices


def check_separator(data, terms, certificate):
    """Reject malformed or unsaturated trace certificates, not just bad hashes."""
    frame = certificate["frame"]
    require(len(frame) == 8 and len(set(frame)) == 8 and set(frame) <= set(data["live"]), "separator frame")
    roots = data["lines"]
    require(all(sum(x*y for x, y in zip(roots[i], roots[j])) == 0
                for i, j in itertools.combinations(frame, 2)), "separator orthogonality")
    mask = sum(1 << i for i in frame)
    active = [k for k, (left, right) in enumerate(terms) if left & mask and right & mask]
    require(active == certificate["active_terms"] and len(active) == 8, "separator saturation")
    k = certificate["term"]
    require(k in active, "separator term is not active")
    left, right = terms[k]
    require(list(screen.engine.bits(left & mask)) == certificate["left_on_frame"], "separator left support")
    require(list(screen.engine.bits(right & mask)) == certificate["right_on_frame"], "separator right support")
    require(not left & right & mask, "separator is not an empty diagonal product")
    return True


def positive_controls(data, ip, pairing, supports, frames):
    coordinates = data["punctured_frame"]
    live = data["live"]
    columns = [[ip[root][c] for c in coordinates] for root in live]
    for i, root in enumerate(live):
        for j, other in enumerate(live):
            require(sum(x*y for x, y in zip(columns[i], columns[j])) == 2 * ip[root][other],
                    "coordinate exact identity")
    terms = [(supports[2*c], supports[2*c]) for c in coordinates]
    summary, saturated = screen.frame_screen(data, frames, terms)
    require(summary["minimum_frame_hits"] == 8 and not summary["empty_trace_constraints"],
            "true coordinate decoder falsely rejected")
    for index, active in saturated:
        for k in active:
            require(sum(ip[root][coordinates[k]] ** 2 for root in frames[index]) == 4,
                    "positive saturated trace")
    clique = screen.all_clique_screen(data, terms)
    require(not clique["failed_cliques"], "true decoder fails a principal rank cut")
    # Independently exercise square-factor duality over Q, including negative entries.
    invertible = 0
    for a, b, c, d in itertools.product((-1, 0, 1), repeat=4):
        det = a*d-b*c
        if not det:
            continue
        D = [[Fraction(a), Fraction(b)], [Fraction(c), Fraction(d)]]
        T = [[Fraction(d, det), Fraction(-c, det)], [Fraction(-b, det), Fraction(a, det)]]
        require(all(sum(D[i][k]*T[j][k] for k in range(2)) == (i == j)
                    for i in range(2) for j in range(2)), "small exact dual")
        require(all(sum(D[i][k]*T[i][k] for i in range(2)) == 1 for k in range(2)), "small term trace")
        invertible += 1
    # A genuinely complex ordinary-transpose fixture: i * (-i) = 1,
    # whereas a mistaken Hermitian product gives -1. Gaussian pairs are exact.
    def mul(x, y):
        return x[0]*y[0]-x[1]*y[1], x[0]*y[1]+x[1]*y[0]
    require(mul((0, 1), (0, -1)) == (1, 0), "complex ordinary transpose")
    require(mul((0, 1), (0, 1)) != (1, 0), "Hermitian mutation must fail")
    return dict(coordinate_identity_entries=len(live)**2,
                coordinate_trace_checks=8*len(frames), rational_square_fixtures=invertible,
                ordinary_transpose_complex_fixture=True)


def budget():
    spec = importlib.util.spec_from_file_location(
        "credited_ceiling", ROOT / "research/complex-local-word-ceiling/ceiling.py")
    ceiling = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ceiling)
    baseline = {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}
    mixed = {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 6: 9, 8: 1}
    low, high = ceiling.ceiling(baseline, 73, 896, 9, 64)
    candidate_low, candidate_high = ceiling.ceiling(mixed, 73, 896, 9, 62)
    require(candidate_low > Fraction(21, 20)*high, "optimistic five-percent screen")
    return dict(baseline_ceiling=[str(low), str(high)], mixed62_ceiling=[str(candidate_low), str(candidate_high)],
                strict_five_percent_screen=True,
                physical_extra_costs="Optimistically omitted only for screening; no realization or kappa claim.")


def compute():
    pins = json.loads((HERE / "SOURCES.json").read_text())
    for record in pins["files"]:
        if record["usage"] == "input":
            require(hashlib.sha256((ROOT / record["path"]).read_bytes()).hexdigest() == record["sha256"],
                    "source bytes: " + record["path"])
    data = screen.engine.model()
    ip, pairing, supports, frames = screen.engine.geometry(data)
    witness = json.loads((HERE / "SUPPORT.json").read_text())
    terms, invoice = decode(data, pairing, supports, witness)
    summary, _ = screen.frame_screen(data, frames, terms)
    require(summary["minimum_frame_hits"] >= 8 and not summary["uncovered_diagonals"],
            "proposal must survive old frame and diagonal conditions")
    choices, census = family.representatives(data, pairing, supports, frames, terms)
    quotient = family.quotient(data, ip, supports, choices)
    original_choices = [next(i for i, record in enumerate(group)
                             if (int(record["left"], 16), int(record["right"], 16)) == terms[k])
                        for k, group in enumerate(choices)]
    original_case = next(case for case in quotient["diagonal_survivors"]
                         if case["coordinate_root"] == witness["coordinate_root"] and case["choices"] == original_choices)
    for case in quotient["diagonal_survivors"]:
        survivor_terms, survivor_invoice = decode(data, pairing, supports, case)
        survivor_summary, _ = screen.frame_screen(data, frames, survivor_terms)
        require(sum(survivor_invoice) == 62 and survivor_summary["minimum_frame_hits"] >= 8
                and not survivor_summary["uncovered_diagonals"], "survivor must pass predecessor screens")
        family.check_rank_cut(data, survivor_terms, case["rank_cut"])
    cliques = screen.all_clique_screen(data, terms)
    require(cliques["failed_cliques"] > 0, "the complete clique scan must detect the source counterexample")
    require(summary["empty_trace_constraints"], "missing additional saturated-duality obstruction")
    f, k = summary["empty_trace_constraints"][0]
    mask = sum(1 << i for i in frames[f])
    separator = dict(frame=list(frames[f]), term=k,
                     active_terms=[j for j, (left, right) in enumerate(terms) if left & mask and right & mask],
                     left_on_frame=list(screen.engine.bits(terms[k][0] & mask)),
                     right_on_frame=list(screen.engine.bits(terms[k][1] & mask)))
    check_separator(data, terms, separator)
    controls = []
    def reject(name, function):
        try:
            function()
        except (ValueError, KeyError):
            controls.append(name)
        else:
            raise ValueError("negative control accepted: " + name)
    bad = dict(separator, active_terms=separator["active_terms"][:-1])
    reject("missing_active_term", lambda: check_separator(data, terms, bad))
    bad_term = next(j for j in separator["active_terms"] if terms[j][0] & terms[j][1] & mask)
    bad = dict(separator, term=bad_term,
               left_on_frame=list(screen.engine.bits(terms[bad_term][0] & mask)),
               right_on_frame=list(screen.engine.bits(terms[bad_term][1] & mask)))
    reject("nonempty_trace_claimed_empty", lambda: check_separator(data, terms, bad))
    bad = dict(separator, frame=separator["frame"][:-1] + [separator["frame"][0]])
    reject("duplicate_frame_root", lambda: check_separator(data, terms, bad))
    bad_witness = json.loads(json.dumps(witness))
    bad_witness["terms"][0][2] = "0"
    reject("uncut_parent_priced_six", lambda: decode(data, pairing, supports, bad_witness))
    for other in frames:
        other_mask = sum(1 << i for i in other)
        active = [j for j, (left, right) in enumerate(terms) if left & other_mask and right & other_mask]
        if len(active) > 8:
            bad = dict(separator, frame=list(other), active_terms=active)
            reject("unsaturated_frame_cannot_use_square_duality", lambda: check_separator(data, terms, bad))
            break
    else:
        raise ValueError("missing unsaturated negative fixture")
    # Enlarging the obstructed rectangle by its right support erases the
    # empty-diagonal premise. The verifier must not preserve the old rejection.
    enlarged = list(terms)
    left, right = enlarged[k]
    enlarged[k] = (left | right, right)
    bad = dict(separator, left_on_frame=list(screen.engine.bits((left | right) & mask)))
    reject("support_enlargement_invalidates_certificate", lambda: check_separator(data, enlarged, bad))
    rank_cut = original_case["rank_cut"]
    a = rank_cut["roots"][0]
    b = next(i for i in data["live"] if i != a and ip[a][i] != 0)
    bad_cut = dict(rank_cut, roots=[a, b])
    reject("nonorthogonal_pair_is_not_an_identity_minor", lambda: family.check_rank_cut(data, terms, bad_cut))
    bad_cut = dict(rank_cut, active_terms=[])
    reject("false_rank_cut_incidence", lambda: family.check_rank_cut(data, terms, bad_cut))
    cut_mask = sum(1 << i for i in rank_cut["roots"])
    enlarged = list(terms)
    inactive = next(j for j in range(10) if j not in rank_cut["active_terms"])
    left, right = enlarged[inactive]
    enlarged[inactive] = (left | cut_mask, right | cut_mask)
    active = [j for j, (left, right) in enumerate(enlarged) if left & cut_mask and right & cut_mask]
    bad_cut = dict(rank_cut, active_terms=active)
    reject("enlarged_support_can_erase_rank_cut", lambda: family.check_rank_cut(data, enlarged, bad_cut))
    positive = positive_controls(data, ip, pairing, supports, frames)
    return dict(schema_version=1, copy_profile=invoice, total_copy_rank=sum(invoice),
                support_sha256=hashlib.sha256((HERE / "SUPPORT.json").read_bytes()).hexdigest(),
                frames=summary, all_clique_rank_counts=cliques, separator=separator,
                census=census, quotient=quotient, original_choices=original_choices,
                controls=controls, positive_controls=positive, optimistic_budget=budget(),
                scope="No masked decoder in the declared nine retained-hit rank-at-most-six star-descendant family plus any one coordinate-star rectangle, over C with ordinary transpose. Other COPY62 supports remain open.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    result = json.loads(json.dumps(compute()))
    if args.write:
        (HERE / "CERTIFICATE.json").write_text(json.dumps(result, indent=2)+"\n")
    else:
        require(result == json.loads((HERE / "CERTIFICATE.json").read_text()), "complete certificate mismatch")
    print("PASS_P112_MIXED62_QUOTIENT parents=7616 slices=967232 families=4096 "
          "diagonal_survivors=3 rank2_rejections=3 controls=" + str(len(result["controls"])))


if __name__ == "__main__":
    main()

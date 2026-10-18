"""Source-bound exact checks for one mixed good/fallback descriptor interface.

Prepared for commdata2338 with substantial OpenAI Codex assistance.
Apache-2.0. No predecessor executable is imported.
"""

import argparse
from dataclasses import replace
import gzip
from hashlib import sha1, sha256
from itertools import product
import json
from math import gcd
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from descriptor import (FallbackPair, Good, Root, elimination, good_pivots,
                        identity, inverse, multiply, projector, require,
                        residual, reversed_child, weighted_residual)


def triangular_oracle(matrix, modulus):
    """Separate forward normalized Gaussian elimination, no descriptor calls.

    Record the pivot BEFORE normalization. Clearing only BELOW the pivot
    gives the same diagonal as unnormalized all-row clearing, because later
    pivot rows have zeros in earlier columns.
    """
    a = [row[:] for row in matrix]
    n = len(a)
    diagonal, itinerary = [], []
    for k in range(n):
        candidates = [i for i in range(k, n) if gcd(a[i][k], modulus) == 1]
        require(bool(candidates), "oracle unit pivot")
        p = min(candidates)
        itinerary.append(p)
        a[k], a[p] = a[p], a[k]
        d = a[k][k] % modulus
        diagonal.append(d)
        a[k] = [x * pow(d, -1, modulus) % modulus for x in a[k]]
        for i in range(k+1, n):
            c = a[i][k]
            for j in range(k, n):
                a[i][j] = (a[i][j] - c * a[k][j]) % modulus
    return tuple(diagonal), tuple(itinerary)


def reconstructed_matrix(plan):
    """Reconstruct full coefficients from D and reversed inverse row actions."""
    n, modulus = len(plan.diagonal), plan.modulus
    out = [[int(i == j) * plan.diagonal[i] for j in range(n)] for i in range(n)]
    for kind, i, k, c in reversed(plan.operations):
        if kind == "swap":
            out[i], out[k] = out[k], out[i]
        else:
            out[i] = [(x - c*y) % modulus for x, y in zip(out[i], out[k])]
    return out


def check_pins():
    data = {}
    for pin in json.loads((HERE / "SOURCES.json").read_text())["files"]:
        if pin["usage"] == "input":
            raw = (ROOT / pin["path"]).read_bytes()
            require(sha256(raw).hexdigest() == pin["sha256"], "source pin: " + pin["path"])
            data[pin["path"]] = raw
    base = "research/community-hyperplane599-audit/pr589/bit589/v9/hosted/"
    template_raw = gzip.decompress(data[base + "GLOBAL-TEMPLATE.json.gz"])
    template = json.loads(template_raw)
    expected_path = "research/e8-bit-p111-tuned/tune/EXPECTED.json"
    expected = json.loads(data[expected_path])
    assembly = json.loads(data["research/community-frontier1094-audit/ASSEMBLY.json"])
    global_receipt = json.loads(data[base + "GLOBAL.json"])
    raw = data[expected_path]
    blob = sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
    require(assembly["bit_supplier"]["pr"] == 589 and
            assembly["bit_supplier"]["git_blob_sha1"] == blob, "selected bit binding")
    require(sha256(template_raw).hexdigest() == global_receipt["template_sha256"],
            "decoded template binding")
    require(global_receipt["word_sha256"] == expected["word"]["file_sha256"],
            "selected word binding")
    require((template["m"], template["h"], template["stages"], template["replicas"])
            == (64, 8, 9, 32), "selected dimensions")
    children = [x for x in template["schedule"] if x["kind"] == "idle" and x["idx"] == 6]
    require(len(children) == 1 and children[0] == {
        "idx": 6, "kind": "idle", "pair": 0, "rank": 42,
        "source_level": 2, "target_level": 8}, "selected idle label")
    used = [slot for slot in template["hosting"]["slots"] if slot[0] == 6 and slot[1] == 213]
    require(not used and template["hosting"]["remainders"]["6"] == {"2": 213, "42": 9},
            "selected unhosted copy")
    require(expected["nine"]["profile"]["42"] == 288, "selected rank42 count")
    return {"idle_child": 6, "copy": 213, "rank": 42, "axes": list(range(22, 64)),
            "cover_bridge": "GL64 implementation domain remains conditional"}


def selected_chart(blocks):
    """h S, where S sends the selected last42 axes to the first42 axes."""
    h = identity(64)
    for i, j, a, b, c, d in blocks:
        h[i][i], h[i][j], h[j][i], h[j][j] = a, b, c, d
    order = list(range(22, 64)) + list(range(22))
    g = [[0] * 64 for _ in range(64)]
    for i in range(64):
        for j, original_column in enumerate(order):
            g[i][original_column] = h[i][j]
    return g


def fixture(q=5, width=2, root_columns=5, branching=True):
    modulus = q**width
    good_chart = selected_chart([
        (0, 43, 1, 1, q, 1+q),
        (1, 42, 1, 1, 2*q, 1+2*q),
        (25, 44, 1, 1, 3*q, 1+3*q)])
    p = projector(good_chart, range(22, 64), modulus)
    pivots = good_pivots(p, 42, modulus)
    require([pivots[k] for k in (0, 1, 25)] == [(1+t*q) % modulus for t in (1, 2, 3)],
            "good full-chart pivots")
    good = Good(Root(64*root_columns, modulus), 64, root_columns, pivots)
    blocks = [(0, 43, q, q-1, 1, 1)]
    if branching:
        blocks.append((1, 42, 1, 0, 1, 1))
    bad_chart = selected_chart(blocks)
    bad_p = projector(bad_chart, range(22, 64), modulus)
    require(bad_p[0][0] == q % modulus and gcd(bad_p[0][0], modulus) != 1,
            "nongeneric rank42 projector")
    require(multiply(bad_p, bad_p, modulus) == bad_p, "split projector")
    matrix = residual(bad_p, modulus)
    require(multiply(matrix, matrix, modulus) == identity(128), "full residual involution")
    plan = elimination(matrix, modulus)
    require(reconstructed_matrix(plan) == matrix, "full fallback reconstruction")
    oracle_d, oracle_pivots = triangular_oracle(matrix, modulus)
    require((plan.diagonal, plan.pivots) == (oracle_d, oracle_pivots), "unweighted oracle")
    return good, matrix, plan


def expected_weights_from_oracle(good, matrix, field, reverse):
    f = good.size // 64
    values = []
    for t in range(f):
        j = f-1-t if reverse else t
        a = [good.value(k*f+j) for k in range(64)]
        weighted = weighted_residual(matrix, a, good.modulus)
        d, _ = triangular_oracle(weighted, good.modulus)
        values.append(d[field])
    return values


def selected_checks():
    records = []
    columns = diagonal_entries = 0
    for q, width, f0 in [(3, 2, 2), (5, 2, 5), (5, 3, 8), (7, 1, 4)]:
        good, matrix, plan = fixture(q, width, f0)
        f, modulus = good.size // 64, good.modulus
        determinant = (-1) ** sum(op[0] == "swap" for op in plan.operations)
        for d in plan.diagonal:
            determinant = determinant*d % modulus
        require(determinant == 1, "selected even-rank residual determinant")
        # Every paired-diagonal descriptor, both physical orientations.
        for j in range(f):
            weights = [good.value(k*f+j) for k in range(64)]
            weighted = weighted_residual(matrix, weights, modulus)
            direct_d, direct_pivots = triangular_oracle(weighted, modulus)
            require(direct_pivots == plan.pivots, "weight-independent pivot itinerary")
            # Check the weighted entire ADDRESS matrix by a second reconstruction.
            weighted_plan = elimination(weighted, modulus)
            require(reconstructed_matrix(weighted_plan) == weighted, "weighted whole-operator reconstruction")
            for i in range(127):
                for reverse in (False, True):
                    child = FallbackPair(good, 64, f, plan, i, reverse)
                    t = f-1-j if reverse else j
                    require(child.value(t) == direct_d[i], "mixed descriptor vs independent elimination")
                    diagonal_entries += 1
            columns += 1
        records.append({"q": q, "width": width, "good_columns": f0,
                        "good_child_atoms": good.size, "bad_columns": f,
                        "peeled_spectators": good.size-64*f,
                        "tail126_weights": [FallbackPair(good,64,f,plan,126,True).value(t)
                                            for t in range(f)]})
    good, matrix, plan = fixture()
    head = FallbackPair(good,64,3,plan,1,False)
    tail = FallbackPair(good,64,3,plan,126,True)
    require([head.value(t) for t in range(3)] == [14,14,19], "two-index quotient witness")
    require([tail.value(t) for t in range(3)] == [11,6,6], "tail orientation witness")
    return {"fixtures": records, "weighted_columns": columns,
            "descriptor_entries": diagonal_entries,
            "quotient_witness": {"field":1, "original_row":plan.permutation[1],
                                 "weights":[14,14,19]},
            "orientation_witness": {"field":126,"original_row":plan.permutation[126],
                                     "weights":[11,6,6]}}


def small_covariance_checks():
    """Exhaust all determinant +/-1 matrices and unit diagonal weights at 3,9."""
    matrices, weighted_cases, nontrivial_swaps = 0, 0, 0
    for modulus in (3, 9):
        units = [x for x in range(modulus) if gcd(x, modulus) == 1]
        for a,b,c,d in product(range(modulus), repeat=4):
            if (a*d-b*c) % modulus not in (1, modulus-1):
                continue
            matrix = [[a,b],[c,d]]
            plan = elimination(matrix, modulus)
            require(reconstructed_matrix(plan) == matrix, "small full reconstruction")
            matrices += 1
            nontrivial_swaps += plan.permutation != (0,1)
            for weights in product(units, repeat=2):
                weighted = [[weights[i]*matrix[i][j]*pow(weights[j],-1,modulus) % modulus
                             for j in range(2)] for i in range(2)]
                diag, pivots = triangular_oracle(weighted, modulus)
                predicted = tuple(plan.diagonal[i] * weights[plan.permutation[i]] *
                                  pow(weights[i],-1,modulus) % modulus for i in range(2))
                require(diag == predicted and pivots == plan.pivots, "exhaustive covariance")
                weighted_cases += 1
    require((matrices, weighted_cases) == (1344, 46848), "small exhaustive coverage")
    return {"matrices": matrices, "weighted_cases": weighted_cases,
            "matrices_with_row_swap": nontrivial_swaps}


def ordinary_via_children(head, tail, weights, modulus):
    """R_tail F_A R_tail; each reversal is one smaller unweighted child."""
    def reverse_with_child(values):
        h = len(values)//2
        if not h:
            return list(values), 0
        left, right = reversed_child(values[:h], values[-h:], [1]*h, modulus)
        return left + list(values[h:len(values)-h]) + right, 1
    tail, before = reverse_with_child(tail)
    head, tail = reversed_child(head, tail, weights, modulus)
    tail, after = reverse_with_child(tail)
    return head, tail, 1+before+after


def child_checks():
    good, _, plan = fixture()
    child = FallbackPair(good,64,3,plan,126,True)
    weights = [child.value(t) for t in range(3)]
    modulus, f = 25, 3
    count = 0
    # Each coordinate pair exhausts its complete two-field fiber. Other
    # coordinates are arbitrary nonzero values; spectator labels stay present.
    for t in range(f):
        images = set()
        for x, y, stock in product(range(modulus), range(modulus), range(3)):
            h, d = [2,3,4], [7,8,9]
            h[t], d[t] = x, y
            before = (stock, tuple(h), ("middle",17), tuple(d), ("suffix",23))
            h1,d1,n1 = ordinary_via_children(h,d,[1]*f,modulus)
            h2,d2,n2 = ordinary_via_children(h1,d1,weights,modulus)
            after = (stock,tuple(h2),before[2],tuple(d2),before[4])
            expected_h = tuple(weights[k]*h[k]%modulus for k in range(f))
            expected_d = tuple(pow(weights[k],-1,modulus)*d[k]%modulus for k in range(f))
            require(after == (stock,expected_h,before[2],expected_d,before[4]),
                    "weighted diagonal pair with complete spectators")
            require(n1+n2 == 6, "paid same-orientation child count")
            images.add((after[0], after[1][t], after[3][t]))
            count += 1
        require(len(images) == 3*modulus**2, "complete pair fibers preserved")
    head_child = FallbackPair(good,64,3,plan,1,False)
    opposite_weights = [head_child.value(t) for t in range(3)]
    basis_count = 0
    for k in range(2*f):
        basis = [int(i==k) for i in range(2*f)]
        h,d = reversed_child(basis[:f],basis[f:],[1]*f,modulus)
        h,d = reversed_child(h,d,opposite_weights,modulus)
        require(h == [opposite_weights[t]*basis[t]%modulus for t in range(f)] and
                d == [pow(opposite_weights[f-1-t],-1,modulus)*basis[f+t]%modulus
                      for t in range(f)], "opposite-orientation diagonal pair")
        basis_count += 1
    return {"complete_pair_and_stock_cases":count,"pair_children":6,
            "pair_child_widths":[1,3,1,1,3,1],"weights":weights,
            "opposite_orientation_basis_columns":basis_count,"opposite_pair_children":2}


def mixed_chain_check():
    """A fallback child large enough to become the next selected good parent."""
    older, matrix, plan = fixture(root_columns=100)
    bad = FallbackPair(older,64,65,plan,126,True)
    reference = expected_weights_from_oracle(older,matrix,126,True)
    require([bad.value(t) for t in range(65)] == reference, "mixed ancestor vector")
    # The next good normal form is independently prepared from its full chart.
    current_chart = selected_chart([(0,43,1,1,5,6), (1,42,1,1,10,11)])
    pivots = good_pivots(projector(current_chart,range(22,64),25),42,25)
    current = Good(bad,64,1,pivots)
    actual = [current.value(t) for t in range(current.size)]
    require(actual == [reference[t]*pivots[t]%25 for t in range(42)],
            "good-after-fallback generated weights")
    require((actual[0],actual[1],actual[29],actual[30],actual[41]) == (16,21,11,6,6),
            "mixed depth-three witness")
    return {"root_atoms":6400,"first_good_atoms":4200,"fallback_columns":65,
            "first_peeled_atoms":40,"fallback_child_atoms":65,
            "current_good_columns":1,"current_peeled_atoms":1,
            "current_good_child_atoms":42,
            "current_weights":actual,"oracle_weight_entries":65}


def controls():
    names = []

    def rejects(name, action):
        try:
            action()
        except ValueError:
            names.append(name)
        else:
            raise ValueError("control did not reject: " + name)

    good, matrix, plan = fixture()
    child = FallbackPair(good,64,3,plan,126,True)
    expected = expected_weights_from_oracle(good,matrix,126,True)
    def compare(candidate, wanted=expected):
        require([candidate.value(t) for t in range(candidate.size)] == wanted, "descriptor mismatch")

    rejects("omit_physical_orientation", lambda: compare(replace(child,reverse=False)))
    pi = list(plan.permutation)
    a,b = 126,pi.index(126)
    pi[a],pi[b] = pi[b],pi[a]
    rejects("wrong_original_row", lambda: compare(replace(child,plan=replace(plan,permutation=tuple(pi)))))
    low_good = replace(good,pivots=tuple(x%5 for x in good.pivots))
    rejects("low_only_good_ancestor", lambda: compare(replace(child,parent=low_good)))
    head = FallbackPair(good,64,3,plan,1,False)
    wanted = expected_weights_from_oracle(good,matrix,1,False)
    omitted_denominator = [plan.diagonal[1] * good.value(42*3+j)%25 for j in range(3)]
    rejects("omit_denominator", lambda: require(omitted_denominator==wanted,"denominator needed"))
    wrong_flat = [plan.diagonal[126]*good.value(t)%25 for t in range(3)]
    rejects("reuse_good_only_flat_index", lambda: require(wrong_flat==expected,"fallback reindexes"))
    wrong_sign = replace(plan,diagonal=tuple((-x if i==1 else x)%25 for i,x in enumerate(plan.diagonal)))
    rejects("lost_diagonal_sign", lambda: compare(replace(head,plan=wrong_sign),wanted))
    low_matrix = [[x%5 for x in row] for row in matrix]
    low_plan = elimination(low_matrix,25)
    low_child = FallbackPair(good,64,3,low_plan,0,False)
    rejects("low_only_bad_ancestor", lambda: compare(low_child,expected_weights_from_oracle(good,matrix,0,False)))
    rejects("wrong_coarse_width", lambda: replace(child,columns=4))
    rejects("wrong_plan_modulus", lambda: replace(child,plan=replace(plan,modulus=9)))
    rejects("nonunit_root_weight", lambda: replace(good.parent,unit=5).value(0))
    rejects("nonunit_diagonal", lambda: replace(child,plan=replace(plan,diagonal=(5,)+plan.diagonal[1:])))
    rejects("out_of_range_child_index", lambda: child.value(3))
    rejects("invalid_row_permutation", lambda: replace(child,plan=replace(plan,permutation=(0,)*128)))
    weights = [child.value(t) for t in range(3)]
    h,d = [1,2,3],[4,5,6]
    # Swapping the chronological order of J_1 then J_a inverts the scaling.
    h1,d1,_ = ordinary_via_children(h,d,weights,25)
    h2,d2,_ = ordinary_via_children(h1,d1,[1]*3,25)
    rejects("reversed_diagonal_pair_order", lambda: require(
        h2==[weights[k]*h[k]%25 for k in range(3)],"pair order"))
    rejects("unpaid_tail_reversal", lambda: require(
        reversed_child(h,d,weights,25) ==
        ([weights[k]*d[k]%25 for k in range(3)],
         [pow(weights[k],-1,25)*h[k]%25 for k in range(3)]), "ordinary vs reversed swap"))
    return names


def build_result():
    return {"selected":check_pins(), "selected_checks":selected_checks(),
            "exhaustive_covariance":small_covariance_checks(), "child":child_checks(),
            "good_fallback_good":mixed_chain_check(),
            "rejected_controls":controls(),
            "fallback_child_allowance":6*128*127+3*128+6*127,
            "charged_fallback_allowance":32*64**2,
            "scope":"conditional mixed descriptor interface; no supplier or new kappa"}


def read_receipt(path):
    def unique(pairs):
        out = {}
        for key, value in pairs:
            require(key not in out, "duplicate receipt key: " + key)
            out[key] = value
        return out
    def reject_constant(value):
        raise ValueError("nonfinite receipt number: " + value)
    return json.loads(path.read_text(),object_pairs_hook=unique,parse_constant=reject_constant)


def exact_json(value):
    return json.dumps(value,sort_keys=True,separators=(",",":"),allow_nan=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-result", type=Path, help="write a new candidate receipt, exclusively")
    args = parser.parse_args()
    result = build_result()
    if args.write_result:
        with args.write_result.open("x") as handle:
            json.dump(result,handle,indent=2)
            handle.write("\n")
        print("WROTE_CANDIDATE_RESULT (not a committed-receipt comparison)")
    else:
        require(exact_json(read_receipt(HERE/"RESULT.json")) == exact_json(result),
                "committed result mismatch")
        print("PASS_SELECTED_BIT_MIXED_DESCRIPTOR covariance=46848 mixed_columns=11 controls=15 no_new_kappa")


if __name__ == "__main__":
    main()

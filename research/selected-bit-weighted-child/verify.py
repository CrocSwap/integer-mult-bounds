#!/usr/bin/env python3
"""Selected BIT generic child check. Apache-2.0; substantial OpenAI Codex assistance."""
import argparse
from copy import deepcopy
from dataclasses import replace
from hashlib import sha256, sha1
import json
from pathlib import Path
import sys

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
sys.path.insert(0, str(PACKAGE))
from child import (ChildDescriptor, compile_projector, direct_action, execute, eye,
                   multiply, require, weighted_adapters, weighted_swap, residual,
                   block_diagonal, shear)

BIT = "research/e8-bit-p111-tuned/"
ASSEMBLY = "research/community-frontier1094-audit/ASSEMBLY.json"
SELECTED = "research/community-frontier1094-audit/SELECTED-SOURCE.json"


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value):
    return sha256(canonical(value)).hexdigest()


def source_object():
    manifest = json.loads((PACKAGE / "SOURCES.json").read_text())
    blobs, hashes, sources = {}, {}, {}
    for pin in manifest["files"]:
        if pin["usage"] != "input":
            continue
        raw = (ROOT / pin["path"]).read_bytes()
        require(len(raw) <= 8 * 1024 * 1024, "bounded source size")
        hashes[pin["path"]] = sha256(raw).hexdigest()
        blobs[pin["path"]] = sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
        require((hashes[pin["path"]], blobs[pin["path"]]) == (pin["sha256"], pin["git_blob"]),
                "source binding: " + pin["path"])
        sources[pin["path"]] = raw
    assembly = json.loads(sources[ASSEMBLY])
    selected = json.loads(sources[SELECTED])["files"]
    expected = json.loads(sources[BIT + "tune/EXPECTED.json"])
    selection = json.loads(sources[BIT + "data/selection9-p111.json"])["bit"]
    require(assembly["bit_supplier"]["commit"] == "a5afc8c6169ea61ba7c51dfd3cade02cc7b13b46",
            "selected PR589 source")
    require(assembly["bit_supplier"]["git_blob_sha1"] == blobs[BIT + "tune/EXPECTED.json"],
            "selected receipt citation")
    for path in (BIT + "tune/EXPECTED.json", BIT + "data/selection9-p111.json"):
        require(selected[path] == hashes[path], "selected input manifest")
    require(expected["nine"]["bit"]["maxchild"] == 42 and
            expected["nine"]["bit"]["live"] == 28416, "selected dimensions")
    # Reconstruct the pinned geometry idle table and descending hosting pattern
    # allocation. No predecessor code is imported or executed.
    idle = []
    for pair in range(1, 4):
        idle.extend([(pair, -1, 2 * pair - 1), (pair, 2 * pair - 1, 2 * pair)])
    idle.extend((pair, 2 * pair + 2, 8) for pair in range(4))
    candidates = []
    for child, (pair, low, high) in enumerate(idle):
        axes = list(range(1 if low == -1 else 8 + 7 * low, 8 + 7 * high))
        patterns = sorted([(tuple(widths), count) for idx, widths, count in selection["patterns"]
                           if idx == child], key=lambda item: (-sum(item[0]), item[0]))
        copy = 0
        for widths, count in patterns:
            require(sum(widths) <= len(axes), "hosting fits idle projector")
            for _ in range(count):
                remaining = axes[sum(widths):]
                if len(remaining) == 42:
                    candidates.append((child, copy, pair, copy // 111, copy % 111, remaining))
                copy += 1
        while copy < 222:
            if len(axes) == 42:
                candidates.append((child, copy, pair, copy // 111, copy % 111, axes))
            copy += 1
        require(copy == 222, "physical side-port coverage")
    require(len(candidates) * 32 == expected["nine"]["profile"]["42"] == 288,
            "selected maximal children accounted")
    child, copy, pair, side, port, axes = min(candidates)
    require((child, copy, pair, side, port, axes) == (6, 213, 0, 1, 102, list(range(22, 64))),
            "specified first rank42 residual")
    p0 = [[int(i == j and i in axes) for j in range(64)] for i in range(64)]
    return p0, {"child": child, "copy": copy, "pair": pair, "side": side, "port": port,
                "replica": 0, "axes": axes, "maximal_children_all_replicas": 288,
                "projector_sha256": digest(p0)}, hashes


def scalar(i, j, seed, modulus):
    return ((i + 1) * (j + 3) * (i + 2 * j + 7) + seed * (i + j + 2)) % modulus


def chart_fixture(p0, q, width, seed=1, fresh_high=True, c_scale=None):
    """Block-shear GL64 chart; default C is divisible by q for known genericity."""
    n, r, modulus = len(p0), sum(p0[i][i] for i in range(len(p0))), q ** width
    if c_scale is None:
        c_scale = q
    lower, upper, li, ui = eye(n), eye(n), eye(n), eye(n)
    for i in range(n - r):
        for j in range(r):
            x = c_scale * scalar(i, j, seed + 11, modulus) % modulus if fresh_high else 0
            lower[r + i][j], li[r + i][j] = x, -x % modulus
    for i in range(r):
        for j in range(n - r):
            x = scalar(i, j, seed, modulus)
            upper[i][r + j], ui[i][r + j] = x, -x % modulus
    axes = [i for i in range(n) if p0[i][i]] + [i for i in range(n) if not p0[i][i]]
    permutation = [[int(j == axes[i]) for j in range(n)] for i in range(n)]
    pinverse = [list(row) for row in zip(*permutation)]
    g = multiply(multiply(lower, upper, modulus), permutation, modulus)
    gi = multiply(multiply(pinverse, ui, modulus), li, modulus)
    require(multiply(g, gi, modulus) == eye(n) and multiply(gi, g, modulus) == eye(n),
            "complete chart inverse")
    return g, multiply(multiply(g, p0, modulus), gi, modulus)


def parent_weights(q, width, f):
    modulus = q ** width
    return tuple((1 + (i * i + 3 * i + 1) % (q - 1) + q * (7 * i + 3)) % modulus
                 for i in range(64 * f))


def full_weighted_matrix_check(projector, form, weights):
    m = form.modulus
    left, li, k_matrix = weighted_adapters(form, weights)
    c = multiply(shear(k_matrix, m), block_diagonal(left, form.right_inverse), m)
    ci = multiply(block_diagonal(li, form.right), shear(k_matrix, m, -1), m)
    actual = multiply(multiply(c, residual(projector, weights, m), m), ci, m)
    require(actual == weighted_swap(64, form.pivots, weights, m), "128 weighted operator columns")
    return digest(actual)


def differential(projector, form, width, f, basis=False):
    weights, size = parent_weights(form.q, width, f), 64 * f
    inputs = [([scalar(i, 0, 19, form.modulus) for i in range(size)],
               [scalar(i, 2, 23, form.modulus) for i in range(size)])]
    if basis:
        inputs += [([int(i == j) for i in range(size)], [0] * size) for j in range(size)]
        inputs += [([0] * size, [int(i == j) for i in range(size)]) for j in range(size)]
    for head, tail in inputs:
        expected = direct_action(projector, weights, f, head, tail, form.modulus)
        actual = execute(form, weights, f, head, tail)
        require(actual == expected, "contiguous child equals direct residual")
        require(execute(form, weights, f, *actual) == (head, tail), "complete residual involution")
    return len(inputs), digest(ChildDescriptor(form.modulus, f, weights, form.pivots).values())


def expect_reject(name, call, controls):
    try:
        call()
    except (ValueError, FileNotFoundError):
        controls.append(name)
        return
    raise ValueError("control accepted: " + name)


def lucas_lehmer_89():
    require(all(89 % d for d in range(2, 10)), "Mersenne exponent prime")
    m, s = 2 ** 89 - 1, 4
    for _ in range(87):
        s = (s * s - 2) % m
    require(s == 0, "Lucas-Lehmer prime fixture")
    return m


def build_result():
    p0, selected, hashes = source_object()
    cases, counts, controls = [], 0, []
    detailed = None
    for q in (5, 7, lucas_lehmer_89()):
        for width in (1, 2, 3):
            chart, p = chart_fixture(p0, q, width)
            form = compile_projector(p, 42, q, width)
            weighted_hash = full_weighted_matrix_check(p, form, parent_weights(q, width, 1))
            checks, descriptor_hashes = 0, {}
            for f in (1, 2, 3):
                count, dhash = differential(p, form, width, f, basis=(q == 5 and width == 2))
                checks += count
                descriptor_hashes[str(f)] = dhash
            counts += checks
            cases.append({"q": str(q), "width": width, "chart_sha256": digest(chart),
                          "projector_sha256": digest(p), "pivots": [str(x) for x in form.pivots],
                          "left_sha256": digest(form.left), "right_sha256": digest(form.right),
                          "cross_shear_sha256": digest(form.cross_shear),
                          "row_additions": len(form.row_additions), "column_additions": len(form.column_additions),
                          "cross_additions": sum(x != 0 for row in form.cross_shear for x in row),
                          "adapter_additions_per_atom_column": 2 * (len(form.row_additions) + len(form.column_additions)
                              + sum(x != 0 for row in form.cross_shear for x in row)),
                          "weighted_operator_sha256": weighted_hash, "descriptor_sha256": descriptor_hashes,
                          "direct_input_cases": checks})
            if q == 5 and width == 2:
                detailed = (p, form)
    # A different low class: dense lower shear, with no q-divisibility promise.
    # Fixed deterministic candidate list, bounded at 32; acceptance stays exact.
    for seed in range(1, 33):
        chart, p = chart_fixture(p0, 101, 2, seed=seed, c_scale=1)
        try:
            extra = compile_projector(p, 42, 101, 2)
        except ValueError as error:
            require(str(error) == "nongeneric northeast pivot", "unexpected dense-class failure")
            continue
        break
    else:
        raise ValueError("no generic dense fixture in bounded list")
    dhashes, checks = {}, 0
    for f in (1, 2, 3):
        count, dhash = differential(p, extra, 2, f)
        checks += count
        dhashes[str(f)] = dhash
    counts += checks
    cases.append({"q": "101", "width": 2, "dense_low_class_seed": seed,
                  "chart_sha256": digest(chart), "projector_sha256": digest(p),
                  "pivots": [str(x) for x in extra.pivots],
                  "left_sha256": digest(extra.left), "right_sha256": digest(extra.right),
                  "cross_shear_sha256": digest(extra.cross_shear),
                  "row_additions": len(extra.row_additions), "column_additions": len(extra.column_additions),
                  "cross_additions": sum(x != 0 for row in extra.cross_shear for x in row),
                  "adapter_additions_per_atom_column": 2 * (len(extra.row_additions) + len(extra.column_additions)
                      + sum(x != 0 for row in extra.cross_shear for x in row)),
                  "weighted_operator_sha256": full_weighted_matrix_check(p, extra, parent_weights(101, 2, 1)),
                  "descriptor_sha256": dhashes, "direct_input_cases": checks})
    p, form = detailed
    q, modulus, f = 5, 25, 3
    weights = parent_weights(q, 2, f)
    head = [scalar(i, 0, 19, modulus) for i in range(64 * f)]
    tail = [scalar(i, 2, 23, modulus) for i in range(64 * f)]
    oracle = direct_action(p, weights, f, head, tail, modulus)
    for label, kwargs in (("column-major child weights", {"wrong_child_order": True}),
                          ("missing within-column tail reversal", {"omit_tail_atom_reversal": True}),
                          ("omitted inverse adapters", {"omit_restore": True})):
        expect_reject(label, lambda kwargs=kwargs: require(
            execute(form, weights, f, head, tail, **kwargs) == oracle, label), controls)
    badweights = list(weights)
    badweights[0] = q
    expect_reject("nonunit parent weight", lambda: execute(form, badweights, f, head, tail), controls)
    expect_reject("nongeneric uncharted projector", lambda: compile_projector(p0, 42, q, 2), controls)
    expect_reject("wrong residual rank", lambda: compile_projector(p, 41, q, 2), controls)
    badp = deepcopy(p)
    badp[0][0] = (badp[0][0] + 1) % modulus
    expect_reject("nonprojector input", lambda: compile_projector(badp, 42, q, 2), controls)
    badform = replace(form, right=form.right_inverse, right_inverse=form.right)
    expect_reject("right-normalizer orientation", lambda:
                  full_weighted_matrix_check(p, badform, weights[::f]), controls)
    badform = replace(form, column_additions=tuple(reversed(form.column_additions)))
    expect_reject("column-factor execution order", lambda: require(
        execute(badform, weights, f, head, tail) == oracle, "wrong factor order"), controls)
    # Equal low charts need not give equal full-width pivot weights.
    chart, _ = chart_fixture(p0, q, 2)
    lowchart, lowp = chart_fixture(p0, q, 2, fresh_high=False)
    require([[x % q for x in row] for row in chart] == [[x % q for x in row] for row in lowchart],
            "equal low chart control")
    lowform = compile_projector(lowp, 42, q, 2)
    require(form.pivots != lowform.pivots, "high parent matrix changes child pivots")
    badform = replace(form, pivots=lowform.pivots)
    expect_reject("descriptor uses only low parent chart", lambda: require(
        execute(badform, weights, f, head, tail) == oracle, "wrong high pivots"), controls)
    first_difference = next(k for k in range(42) if form.pivots[k] != lowform.pivots[k])
    # Product-extension preservation: the implementation does not mutate its
    # coefficient/argument objects, and has no access to fresh child fields.
    saved_form, saved_weights, saved_head, saved_tail = deepcopy(form), weights, head[:], tail[:]
    execute(form, weights, f, head, tail)
    require((form, weights, head, tail) == (saved_form, saved_weights, saved_head, saved_tail),
            "parent coefficients and input objects unchanged")
    reads = {"parent_weight_ancestors", "parent_current_low", "parent_current_high", "atom_index"}
    values = ChildDescriptor(modulus, f, weights, form.pivots).values()
    # A genuinely changed interface: using a fresh child bit to select a unit
    # changes the child action, even though the row coordinate is never written.
    independent_outputs = [((1 + fresh_bit) * values[0]) % modulus for fresh_bit in (0, 1)]
    require(independent_outputs[0] != independent_outputs[1], "fresh-dependent child counterexample")
    # A two-coordinate all-width illustration embedded in the selected 64D chart.
    # In canonical active-first coordinates g=[[1,1],[10,11]] at positions 0,42.
    canonical_p = [[int(i == j and i < 42) for j in range(64)] for i in range(64)]
    simple_g, simple_gi = eye(64), eye(64)
    for matrix, block in ((simple_g, ((1, 1), (10, 11))),
                          (simple_gi, ((11, -1), (-10, 1)))):
        for i, ii in enumerate((0, 42)):
            for j, jj in enumerate((0, 42)):
                matrix[ii][jj] = block[i][j] % 25
    simple_p = multiply(multiply(simple_g, canonical_p, 25), simple_gi, 25)
    simple_form = compile_projector(simple_p, 42, 5, 2)
    require(simple_form.pivots == (11,) + (1,) * 41, "explicit high-pivot example")
    return {"schema_version": 1, "status": "PASS_SELECTED_BIT_WEIGHTED_CHILD",
            "selected_object": selected, "input_sha256": hashes, "cases": cases,
            "full_operator_columns": 128 * len(cases), "direct_input_cases": counts,
            "basis_columns_at_q5_w2": 128 + 256 + 384, "single_child_atom_counts": [42, 84, 126],
            "high_field_control": {"q": 5, "width": 2, "same_low_chart": True,
                                   "first_changed_pivot": first_difference,
                                   "complete_parent_value": form.pivots[first_difference],
                                   "low_only_parent_value": lowform.pivots[first_difference],
                                   "simple_chart_block": [[1, 1], [10, 11]],
                                   "simple_projector_block": [[11, 24], [10, 15]],
                                   "simple_pivots": list(simple_form.pivots)},
            "descriptor_reads_at_parent": sorted(reads),
            "spectators": ["older_ancestors", "parent_row", "unused_child_stock", "other_role_fields"],
            "controls_rejected": controls,
            "scope": "One generic residual lowering; no bad-class, physical routing, full compiler, stock coefficient, or kappa claim."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-result", type=Path)
    args = parser.parse_args()
    if args.write_result:
        require(not args.write_result.exists(), "receipt destination already exists")
        recorded = None
    else:
        receipt = (PACKAGE / "RESULT.json").read_bytes()
        require(len(receipt) <= 1024 * 1024, "bounded receipt size")
        recorded = json.loads(receipt)
    result = build_result()
    if args.write_result:
        with args.write_result.open("x", encoding="utf-8") as output:
            json.dump(result, output, indent=2, sort_keys=True)
            output.write("\n")
    else:
        require(canonical(result) == canonical(recorded), "complete committed receipt")
    print(result["status"] + " rank=42 cases=" + str(len(result["cases"])) + " basis=768 controls=" +
          str(len(result["controls_rejected"])) + " no_new_kappa")


if __name__ == "__main__":
    main()

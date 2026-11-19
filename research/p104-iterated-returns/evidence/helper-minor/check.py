#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Replay the one-helper support obstruction on the pinned rational P104 word."""

import argparse
from collections import Counter
from dataclasses import replace
from fractions import Fraction
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parents[1]
HEAD = "172475c2ca321d3496fda7a2a71478ada5acb948"
WORD = "bd3d941f6528341a92b59fb1226e322e98ab6051d32cc0461b3e7cbcae843c22"
LAYOUT = "52c0712b829d830186f4aa811b5fc46c04f62b38005a6b17794eb2484ef12aba"
CALLER = "156fdf3a4a129b39225fd6ca51011de27974d7f104e8b04907c17ed5344bc858"
TARGET = "0.00387981257853"
CALLS = 48
TAPE_PATH = "parent/complex/independent.py"
TAPE_SHA = "0b428bc6fac4dc6ec014114bf4119782553fbb58d92b2a632b51629f4abe563b"
INTERVAL_PATH = "source/research/paired-query-only-bit/independent/interval_gate.py"
INTERVAL_SHA = "8dc2bc4c64cba3f83c664373984a075f1a14b4d53958084091345c8cab189dec"
APPLICATION_SHA = "067a46257dd8a979385943333754bc52c5820eef0abbf2ef74f2e2756477627a"
PRICE_SHA = "a8bf475880a5623aaff7277fd10255561a3bf59843177117b38402838220949b"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def pinned_bytes(path, digest):
    data = path.read_bytes()
    require(sha256(data).hexdigest() == digest, f"SHA-256 mismatch for {path}")
    return data


def load_module(alias, path, digest):
    source = pinned_bytes(path, digest)
    spec = spec_from_file_location(alias, path)
    module = module_from_spec(spec)
    sys.modules[alias] = module
    exec(compile(source, str(path), "exec", dont_inherit=True), module.__dict__)
    return module


def dot(left, right):
    return sum(q * right.get(i, 0) for i, q in left.items())


def apply(columns, vector):
    result = Counter()
    for j, q in vector.items():
        for i, coefficient in columns[j].items():
            result[i] += q * coefficient
    return {i: q for i, q in result.items() if q}


def inverse_columns(rows, columns):
    """Invert independent owner blocks with general exact Gauss–Jordan pivots."""
    inverse = [{} for _ in rows]
    inventory = Counter()
    pending = set(range(len(rows)))
    while pending:
        seed = min(pending)
        component = {seed}
        queue = [seed]
        while queue:
            i = queue.pop()
            new = (rows[i].keys() | columns[i].keys()) - component
            component.update(new)
            queue.extend(new)
        pending.difference_update(component)
        axes = sorted(component)
        width = len(axes)
        inventory[width] += 1
        matrix = [
            [Fraction(rows[i].get(j, 0)) for j in axes]
            + [Fraction(i == j) for j in axes]
            for i in axes
        ]
        for j in range(width):
            pivot = next((k for k in range(j, width) if matrix[k][j]), None)
            require(pivot is not None, "the reference owner block is singular")
            matrix[j], matrix[pivot] = matrix[pivot], matrix[j]
            divisor = matrix[j][j]
            matrix[j] = [q / divisor for q in matrix[j]]
            for k in range(width):
                if k != j and (factor := matrix[k][j]):
                    matrix[k] = [a - factor * b for a,b in zip(matrix[k], matrix[j], strict=True)]
        for i, row in zip(axes, matrix, strict=True):
            for j, coefficient in zip(axes, row[width:], strict=True):
                if coefficient:
                    inverse[j][i] = coefficient
    require(all(apply(columns, column) == {j: 1} for j, column in enumerate(inverse)),
            "complete exact inverse-column identities")
    return inverse, inventory


def outward(interval, scale, places=24):
    ticks = 10 ** places
    lo = interval[0] * ticks // scale
    hi = -((-interval[1] * ticks) // scale)
    def text(n):
        whole, part = divmod(n, ticks)
        return f"{whole}.{part:0{places}d}"
    require(lo >= 0, "expected a positive bound")
    return [text(lo), text(hi)]


def price_bounds(interval, package, paid, productive, ceiling):
    application = json.loads(pinned_bytes(package / "evidence/application.json", APPLICATION_SHA))
    price = json.loads(pinned_bytes(package / "evidence/independent-price.json", PRICE_SHA))
    caller = application["caller"]
    stream = application["caller_proof"]["readback"]["event_stream_sha256"]
    require((application["native_sha256"], application["layout_sha256"], application["target"],
             caller["calls"], stream) == (WORD, LAYOUT, TARGET, CALLS, CALLER), "published application binding")
    invoice = price["signed"]["candidate"]
    require((price["source"], price["signed"]["target_kappa"], invoice["caller_sha256"], invoice["native_calls"],
             invoice["tariff"]) == (WORD, TARGET, CALLER, CALLS, "rank^(1-kappa)"), "published price binding")
    complete_paid = Counter({int(g): n for g,n in caller["fixed_caller_paid"].items()})
    complete_targets = Counter({int(g): n for g,n in caller["fixed_root_targets"].items()})
    complete_paid.update({g: CALLS * n for g,n in paid.items()})
    complete_targets.update({g: CALLS * n for g,n in productive.items()})
    require(dict(invoice["rank_histograms"]["paid"]) == complete_paid
            and dict(invoice["rank_histograms"]["targets"]) == complete_targets, "complete literal native and fixed caller invoice")
    require(invoice["totals"] == {"paid": sum(complete_paid.values()), "targets": sum(complete_targets.values())},
            "complete invoice totals")
    target = Fraction(TARGET)
    deficit = interval.sub(interval.moment(complete_paid, target), interval.moment(complete_targets, target))
    published_lo, published_hi = map(Fraction, price["signed"]["candidate_margin"])
    computed_lo = Fraction(-deficit[1], interval.B)
    computed_hi = Fraction(-deficit[0], interval.B)
    require(max(published_lo, computed_lo) <= min(published_hi, computed_hi), "independent directed invoice bounds agree")
    differences = [interval.smul(interval.sub(interval.power(r, target), interval.power(h, target)), CALLS)
                   for r in range(2, ceiling + 1) for h in range(1, r)]
    minimum = min(v[0] for v in differences), min(v[1] for v in differences)
    require(minimum[0] > deficit[1] > 0, "the conservative positive one-grade bound clears the complete deficit")
    return {
        "paid_positions": invoice["totals"]["paid"],
        "productive_positions": invoice["totals"]["targets"],
        "shortfall": outward(deficit, interval.B),
        "grade_ceiling": ceiling,
        "minimum_positive_grade_saving": outward(minimum, interval.B),
    }


def chart_bits(vector, endpoints, mask):
    result = 0
    for i in vector:
        result |= mask.get(endpoints[i], 0)
    return result


def literal_control(tape, graph, matrix, columns, slot, owner, kernel, cokernel, paid_grade, helper_grade):
    """Check an exact nonsingular minor at equal price on a literal omission."""
    cut = replace(
        graph,
        moves={k: charts for k, charts in graph.moves.items() if k != slot},
        forms={k: tuple((j, q) for j,q in terms if j != slot)
               for k, terms in graph.forms.items() if k != slot},
        order=tuple(k for k in graph.order if k != slot),
    )
    cut.validate_causality()
    actual, _ = tape.forward(cut)
    adjoint, _ = tape.adjoint(cut)
    require(adjoint == tape.transpose(actual), "literal control adjoint equals the cut transpose")
    restricted_actual = [{j: q for j,q in row.items() if j != owner} for i,row in enumerate(actual) if i != owner]
    restricted_old = [{j: q for j,q in row.items() if j != owner} for i,row in enumerate(matrix) if i != owner]
    require(restricted_actual == restricted_old, "literal control preserves every retained public coefficient")
    ratio = kernel.get(owner, 0) * cokernel.get(owner, 0)
    require(ratio and paid_grade == helper_grade, "actual nonsingular equal-price principal minor")
    require(apply(tape.transpose(actual), kernel) == {}, "the same literal deletion is singular with all owners kept")
    require(matrix[owner] == columns[owner] == {owner: 1}, "control axis is an original independent helper")
    return {
        "paid_slot": slot,
        "helper_owner": owner,
        "helper_charts": [graph.initial[owner], graph.final[owner]],
        "paid_grade": paid_grade,
        "surrendered_grade": helper_grade,
        "principal_minor_over_original_determinant": str(ratio),
        "kept_coefficients_each_way": (graph.size - 1) ** 2,
        "same_cut_with_all_owners_is_singular": True,
        "signed_saving": "0",
    }


def evidence(cache, package=PACKAGE):
    tape = load_module("helper_minor_exact_tape", cache / TAPE_PATH, TAPE_SHA)
    interval = load_module("helper_minor_directed_tariff", cache / INTERVAL_PATH, INTERVAL_SHA)
    raw, _ = tape.read(package / "complex/WORD.json.gz", WORD)
    layout, _ = tape.read(package / "complex/LAYOUT.json.gz", LAYOUT)
    graph = tape.Graph.parse(raw)
    spans = [tape.span(frame) for frame in graph.frames]
    expected, mains = tape.public_operator(graph, layout, spans)
    matrix, forms = tape.forward(graph, graph.moves)
    columns, impulses = tape.adjoint(graph, graph.moves)
    require(matrix == expected and tape.transpose(matrix) == columns, "literal forward and adjoint equal the published operator")
    inverse, inverse_blocks = inverse_columns(matrix, columns)
    inverse_rows = tape.transpose(inverse)
    helpers = set(range(graph.size)) - mains
    require(all(matrix[i] == columns[i] == {i: 1} for i in helpers), "independent original helper identities")
    sites = set(graph.initial) | set(graph.final)
    require(len({spans[site] for site in sites}) == len(sites), "public chart labels distinguish actual physical subspaces")
    paid, productive = tape.ranks(graph, mains, spans)
    ceiling = max(map(len, graph.frames))
    tariff = price_bounds(interval, package, paid, productive, ceiling)

    grade = lambda a,b: abs(len(graph.frames[a]) - len(graph.frames[b]))
    groups = sorted({(graph.initial[i], graph.final[i]) for i in helpers})
    inlet, outlet = Counter(), Counter()
    less_than, equal_to = Counter(), Counter()
    for j, (a,b) in enumerate(groups):
        bit = 1 << j
        inlet[a] |= bit
        outlet[b] |= bit
        h = grade(a,b)
        equal_to[h] |= bit
        for r in range(h + 1, ceiling + 1):
            less_than[r] |= bit

    missing = Counter()
    singular = Counter()
    nonsingular = 0
    eligible = 0
    supported_ties = 0
    control = None
    for slot, (a,b) in graph.moves.items():
        f, v = forms[slot], impulses[slot]
        u, g = apply(inverse, v), apply(inverse_rows, f)
        contraction = dot(f, u)
        require(contraction == dot(g, v), "the two exact Schur contractions differ")
        if contraction != 1:
            nonsingular += 1
            continue
        r = grade(a,b)
        singular[r] += 1
        left = chart_bits(u, graph.initial, inlet)
        right = chart_bits(g, graph.final, outlet)
        fundable = less_than[r]
        survivor = fundable & left & right
        require(not survivor, f"a lower-grade chart pair passes both exact support tests for paid slot {slot}")
        missing["both"] += (fundable & ~(left | right)).bit_count()
        missing["input_kernel_only"] += (fundable & ~left & right).bit_count()
        missing["output_cokernel_only"] += (fundable & left & ~right).bit_count()
        eligible += fundable.bit_count()
        supported_ties += (equal_to[r] & left & right).bit_count()
        if slot == 0:
            owner = 1260
            require(owner in helpers, "literal control surrenders a named helper")
            control = literal_control(tape, graph, matrix, columns, slot, owner, u, g, r,
                                      grade(graph.initial[owner], graph.final[owner]))
    require(eligible == sum(missing.values()) and control and supported_ties, "nonempty controls and full support coverage")
    return {
        "schema": "p104-helper-minor-support/v1",
        "published_head": HEAD,
        "word_sha256": WORD,
        "layout_sha256": LAYOUT,
        "caller_sha256": CALLER,
        "target": TARGET,
        "native_calls": CALLS,
        "operator_coefficients_each_way": graph.size ** 2,
        "main_owners": len(mains),
        "helper_owners": len(helpers),
        "helper_chart_pairs": len(groups),
        "inverse_owner_blocks": dict(sorted(inverse_blocks.items())),
        "singular_paid_by_grade": dict(sorted(singular.items())),
        "nonsingular_paid_slots": nonsingular,
        "lower_grade_slot_chart_pairs": eligible,
        "excluded_by_missing_support": dict(missing),
        "equal_grade_pairs_with_both_supports": supported_ties,
        "control": control,
        "price": tariff,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache", required=True, type=Path, help="public source cache verified by prepare_sources.py")
    parser.add_argument("--checkpoint", type=Path, help="checkout root at the immutable bd3d checkpoint")
    parser.add_argument("--out", type=Path, help="optional path for the reproduced JSON receipt")
    args = parser.parse_args()
    package = args.checkpoint / "research/p104-iterated-returns" if args.checkpoint else PACKAGE
    report = evidence(args.cache, package)
    result = json.dumps(report, indent=2, sort_keys=True) + "\n"
    require(json.loads(result) == json.loads((HERE / "EXPECTED.json").read_bytes()), "reproduced evidence differs from EXPECTED.json")
    if args.out:
        args.out.write_text(result)
    count = report["lower_grade_slot_chart_pairs"]
    print(f"PASS: all {count:,} lower-grade slot/chart pairs excluded. Literal equal-price control passed.")


if __name__ == "__main__":
    main()

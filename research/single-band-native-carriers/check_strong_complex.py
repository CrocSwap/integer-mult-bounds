"""Check the changed Gaussian raw word, all its charts, and the executed exact grid."""

from argparse import ArgumentParser
from collections import Counter
from fractions import Fraction
from hashlib import sha256
from math import gcd, prod
from pathlib import Path
import json
import sys

from strong_complex import (
    ADDITIONAL,
    DYADIC,
    GRID,
    ODD,
    artifacts,
    digest,
    load_changed,
    packed,
    required_pairs,
    word,
)


def check(cond, why):
    if not cond:
        raise ValueError(why)


def atlas(grade, graph, layout, data):
    from charts import native_catalogue
    from check_complex import all_images
    from contacts import contact_receipt

    prior = packed(grade / "complex-atlas.json.gz")
    extra = packed(data / "new-charts.json.gz")
    check(digest(extra) == ADDITIONAL, "supplemental Clifford factors")
    need = required_pairs(graph, layout)
    old = {(a, b): r for a, b, r in prior["pairs"]}
    add = {(a, b): r for a, b, r in extra}
    check(
        need - old.keys() == add.keys() and len(add) == len(extra), "all supplementary directions"
    )
    factors = old | add
    catalogue = {"pairs": [[a, b, factors[a, b]] for a, b in sorted(need)], "ports": prior["ports"]}
    checked = native_catalogue(graph, layout, catalogue)
    contact = contact_receipt(
        layout, json.loads((grade / "retained/data/CALLER-PHASE-BASES.json").read_bytes())["by_q"]
    )
    return dict(
        pairs=len(need),
        new=len(extra),
        ports=len(catalogue["ports"]),
        atlas_sha256=digest(checked),
        images=all_images(checked),
        contact=contact,
    )


def literal_grid(graph, layout):
    from spool import short_divisors

    size = len(graph["initial"])
    stocks = {~i: {i: GRID} for i in range(size)}
    moves = {k for k, _, _ in graph["moves"]}
    rows = {k: [(s, Fraction(q)) for s, q in row] for k, row in graph["forms"]}
    masses = {~i: Fraction(1) for i in range(size)}
    expected = [{i: GRID} for i in range(size)]
    hosted = layout["hosted"]
    for i, x in enumerate(layout["live"]):
        y = x + 112
        if i in hosted["Dports"]:
            expected[y][x] = GRID
        else:
            expected[x][y] = -GRID
            expected[y] = {x: GRID // 2, y: GRID // 2}
    for x, y in zip(hosted["X2"], hosted["Y2"], strict=True):
        expected[x][y] = -GRID
    peak = Fraction(1)
    largest_limb = maximum_literal = products = nontrivial = 0
    common = GRID
    literals = set()
    for node in graph["schedule"]:
        values, mass = {}, Fraction(0)
        for src, coeff in rows[node]:
            a, b = coeff.numerator, coeff.denominator
            literals.add(coeff)
            mass += abs(coeff) * masses[src]
            for i, old in stocks[src].items():
                q, rem = divmod(old, b)
                check(rem == 0, "inexact term before multiplication")
                term = a * q
                if common != 1:
                    common = gcd(common, term)
                values[i] = values.get(i, 0) + term
            products += len(stocks[src])
            nontrivial += (b != 1) * len(stocks[src])
        peak = max(peak, mass)
        result = {i: v for i, v in values.items() if v}
        if node in moves:
            stocks[node] = result
            masses[node] = mass
        else:
            check(
                result == expected[node - graph["first_output"]],
                "wrong whole inverse odd or endpoint",
            )
    for coeff in literals | {Fraction(1, ODD), Fraction(ODD)}:
        factors = short_divisors(coeff.denominator)
        check(
            prod(factors) == coeff.denominator and all(1 < v < 2**24 for v in factors),
            "unrepresentable fixed coefficient denominator",
        )
        maximum_literal = max(
            maximum_literal, coeff.numerator.bit_length(), coeff.denominator.bit_length()
        )
        largest_limb = max(largest_limb, *factors, 0)
    check(common == 1 and (ODD << DYADIC) == GRID and ODD % 2 == 1, "minimal grid")
    check((products, nontrivial) == (25146238, 17231591), "all signed basis products")
    check(
        peak
        == Fraction(
            205356183613728386434052488657699504746980105023, 1621896683681232672237748224000
        ),
        "source mass",
    )
    return dict(
        products=products,
        nontrivial=nontrivial,
        peak=str(peak),
        odd=ODD,
        literal_width_with_odd=maximum_literal,
        distinct_literals=len(literals),
        largest_divisor=largest_limb,
    )


def caller(grade, graph, layout, data, mass):
    from mixed_grid import exact, envelope
    from graph_identity import graph_identity
    from raw48 import ComplexRaw

    a = artifacts(grade, data)
    w = word(graph, layout)
    heights, entrance = [], []
    masses, entrance_mass = [], []
    template = {}
    for name, (events, diagonal) in a.words.items():
        receipt = exact(events, diagonal, 2025 << 9)
        check(exact(events, diagonal, receipt["minimum_grid"]) == receipt, "signed complete caller")
        e = envelope(events, len(diagonal))
        heights.append(e["height"])
        entrance.append(e["entrance_height"])
        masses.append(Fraction(e["mass"]))
        entrance_mass.append(Fraction(e["entrance_mass"]))
        template[name] = receipt
    denominator = max(max(heights), max(entrance) + DYADIC)
    scaled_mass = max(max(masses) * 2025, max(entrance_mass) * 2025 * ODD * mass)
    mass_bits = (scaled_mass.numerator - 1) // scaled_mass.denominator
    mass_bits = mass_bits.bit_length()
    scheduled, source = [], []
    degrees = Counter()
    for (kind, root), _ in a.roots.items():
        for i, (sign, terms) in enumerate(a.words[kind][1]):
            tag = ("root", kind, root, a.offsets[kind, root] + i, sign)
            source.append((tag, 1 + 8 * len(terms)))
    source_events = sha256()
    for clock, row in enumerate(a.instructions()):
        source_events.update(json.dumps(row, separators=(",", ":")).encode())
        op = row[0]
        degrees[op] += 1
        if op == "NATIVE":
            call = row[1]
            for i, (b, e) in enumerate(zip(graph["initial"], graph["final"], strict=True)):
                if i not in a.main:
                    tag = "helper", clock, call, layout["source_labels"][i]
                    r = a.factors[b, e][0]
                    check(
                        r == len(graph["frames"][e]) - len(graph["frames"][b]) > 0,
                        "funded native helper",
                    )
                    source.append((tag, r))
            scheduled.extend(
                (("return", clock, call, k), a.factors[a.moves[k]][0])
                for k in graph["schedule"]
                if k in a.moves
            )
        elif op == "QUERY" or op.startswith("IDLE_"):
            r = 1 if op == "QUERY" else 8 * len(row[2]) + (op == "IDLE_ODD")
            scheduled.append(((op, clock, row[1]), r))
    check(source == [(x.tag, x.rank) for x in w.targets], "complete physical productive stream")
    check(scheduled == [(x.tag, x.rank) for x in w.paid], "complete physical paid stream")
    check(
        source_events.hexdigest()
        == json.loads((grade / "retained/grade14-audit.json").read_bytes())["signed"][
            "caller_sha256"
        ],
        "chronological native caller",
    )
    check(
        degrees["NATIVE"] == 48
        and len({x[0] for x in source}) == len(source)
        and len({x[0] for x in scheduled}) == len(scheduled),
        "independent owners and chronological tags",
    )
    check(
        ComplexRaw.axis_list(3, (0, 9, 17))[:3] == (0, 1, 2)
        and (("root", "rotated", 191, 9825, 1), 129) in source,
        "materialized exposed witness",
    )
    return dict(
        targets=len(source),
        paid=len(scheduled),
        target_hist=dict(sorted(Counter(r for _, r in source).items())),
        paid_hist=dict(sorted(Counter(r for _, r in scheduled).items())),
        stages=degrees,
        graph=graph_identity(graph, layout),
        binding=a.binding_receipt,
        caller=template,
        per_context_dyadic=denominator,
        per_context_mass=mass_bits,
        context_guard=2 * max(denominator, mass_bits),
        caller_sha=source_events.hexdigest(),
    )


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)
    for arg in ("grade", "engine", "native", "bounded", "data"):
        parser.add_argument(arg, type=Path)
    parser.add_argument("mode", choices=("atlas", "grid", "caller"))
    args = parser.parse_args()
    for path in (
        args.grade.resolve(),
        args.grade.resolve() / "retained",
        args.engine.resolve(),
        args.native.resolve(),
        args.bounded.resolve(),
    ):
        sys.path.append(str(path))
    g, l = load_changed(args.data)
    proven_mass = Fraction(
        205356183613728386434052488657699504746980105023, 1621896683681232672237748224000
    )
    if args.mode == "atlas":
        answer = atlas(args.grade, g, l, args.data)
    elif args.mode == "grid":
        answer = literal_grid(g, l)
    else:
        answer = caller(args.grade, g, l, args.data, proven_mass)
    print(json.dumps(answer, sort_keys=True))

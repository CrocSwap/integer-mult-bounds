"""Check the minimal odd-scale substitution on the fixed composed graph.

The grid and basis-witness methods adapt PR7680, with its PR866 credit.
The physical engines and interface reader retain their PR7717 bytes.
See CREDITS.md. Ali Romman, with OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction as F
from hashlib import sha1, sha256
from math import gcd
from pathlib import Path
import json
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "source"))
from common import inputs, need, physical, read as source_read
from caller16 import signed_caller

sys.path.insert(0, str(HERE.parents[1] / "research/shared-wire-split-composition/frozen"))
import native_verify as native

ODD, HEIGHT = 11025, 20


def odd(value):
    need(value > 0, "positive denominator")
    return value >> ((value & -value).bit_length() - 1)


def valuation(value, prime):
    exponent = 0
    while value % prime == 0:
        value //= prime
        exponent += 1
    return exponent


def provenance():
    pins = json.loads((HERE / "SOURCE-PINS.json").read_text())
    for pin in pins:
        raw = (HERE / pin["path"]).read_bytes()
        need(sha256(raw).hexdigest() == pin["sha256"]
             and sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest() == pin["git_blob"],
             "retained source identity: " + pin["path"])
    for pin in json.loads((HERE / "SOURCES.json").read_text())["files"]:
        if pin["usage"] == "input":
            need(sha256((HERE.parents[1] / pin["path"]).read_bytes()).hexdigest() == pin["sha256"],
                 "external interpreter identity")
    return len(pins)


def coefficient_certificate(graph, moves, forms, grid):
    values = {~r: {r: grid} for r in range(len(graph["initial"]))}
    common, products, witnesses = grid, 0, {}
    for node in graph["schedule"]:
        row = {}
        for donor, factor in forms[node]:
            for owner, value in values[donor].items():
                term, remainder = divmod(factor.numerator * value, factor.denominator)
                need(remainder == 0, "sufficient source grid")
                new = gcd(common, term)
                if new != common:
                    for prime in (3, 5, 7):
                        if valuation(new, prime) < valuation(common, prime):
                            coefficient = F(term, grid)
                            witnesses[str(prime)] = dict(node=node, donor=donor, input=owner,
                                factor=str(factor), coefficient=str(coefficient),
                                odd_denominator=odd(coefficient.denominator),
                                chart=moves[node][0] if node in moves else graph["final"][node-graph["first_output"]])
                    common = new
                total = row.get(owner, 0) + term
                if total:
                    row[owner] = total
                else:
                    row.pop(owner, None)
                products += 1
        values[node] = row
    minimum = grid // common
    need(odd(minimum) == ODD and minimum == 90316800 and set(witnesses) == {"3", "5", "7"},
         "complete odd denominator certificate")
    return dict(odd=ODD, binary_height=valuation(minimum, 2), products=products, witnesses=witnesses)


def rational_witness(graph, forms, witness):
    values = {~r: F(int(r == witness["input"])) for r in range(len(graph["initial"]))}
    observed = False
    for node in graph["schedule"]:
        row = F(0)
        for donor, factor in forms[node]:
            term = factor * values[donor]
            if node == witness["node"] and donor == witness["donor"]:
                need(str(term) == witness["coefficient"] and str(factor) == witness["factor"],
                     "independent Fraction product witness")
                observed = True
            row += term
        values[node] = row
    need(observed, "witness site reached")


def first_fault(graph, forms, owner, grid):
    values = {~r: grid * int(r == owner) for r in range(len(graph["initial"]))}
    for node in graph["schedule"]:
        row = 0
        for donor, factor in forms[node]:
            numerator = factor.numerator * values[donor]
            term, remainder = divmod(numerator, factor.denominator)
            if remainder:
                return dict(node=node, donor=donor, input=owner, grid=grid,
                            numerator=numerator, divisor=factor.denominator, remainder=remainder)
            row += term
        values[node] = row
    raise ValueError("insufficient odd scale completed")


def physical_witness(graph, prime, witness):
    first, last = graph["initial"][witness["input"]], witness["chart"]
    x, xbits = native.state(native.frame(graph["frames"][first], 9))
    y, ybits = native.state(native.frame(graph["frames"][last], 9))
    need(x == {0: (1, 0)} and xbits == 0, "literal physical unit input")
    coefficient = F(witness["coefficient"])
    full, under = ODD * coefficient, (ODD // prime) * coefficient
    need(all(odd((full * F(v, 2**ybits)).denominator) == 1 for pair in y.values() for v in pair),
         "all chart components clear on the smaller scale")
    bad = next((address, part, F(v, 2**ybits)) for address, pair in sorted(y.items())
               for part, v in zip(("real", "imaginary"), pair, strict=True)
               if (under * F(v, 2**ybits)).denominator % prime == 0)
    return dict(prime=prime, input_role=witness["input"], input_chart=first, input_basis=0,
                input_dyadic_bits=xbits, input_column_sha256=sha256(physical.encoded([x, xbits])).hexdigest(),
                product_chart=last, address=bad[0], component=bad[1], chart_amplitude=str(bad[2]),
                normalized_product=str(coefficient), scaled_product=str(full * bad[2]),
                under_scaled_product=str(under * bad[2]))


def contract_controls():
    need(odd((F(1, 3) * 3).denominator) == 1, "nonunit map hides an odd denominator")
    need(F(1, 3) - F(1, 3) == 0, "correlated inputs hide an odd denominator")
    phase = (F(3, 5), F(4, 5))
    need(sum(x*x for x in phase) == 1 and all(odd(x.denominator) == 5 for x in phase),
         "arbitrary unitary global phase can add an odd denominator")
    return dict(nonunit_chart_counterexample_checked=True, correlated_input_counterexample_checked=True,
                unrestricted_global_phase_counterexample_checked=True)


def verify():
    pins = provenance()
    graph, layout, moves, forms, interface = inputs()
    published = source_read("results/application.json")
    bound = physical.graph_bounds(graph, moves, forms, interface[0])
    for key, value in bound.items():
        need(json.loads(json.dumps(value)) == published["physical"]["native"][key], "source bound identity")
    certificate = coefficient_certificate(graph, moves, forms, bound["path_grid"])
    physical_columns = []
    for prime, witness in certificate["witnesses"].items():
        rational_witness(graph, forms, witness)
        witness["first_under_scaled_fault"] = first_fault(graph, forms, witness["input"], (ODD // int(prime)) << HEIGHT)
        physical_columns.append(physical_witness(graph, int(prime), witness))
    grid = ODD << HEIGHT
    expected = physical.expected_rows(layout["public"], layout, interface, grid)
    exact = physical.exact_basis_grid(graph, moves, forms, grid, expected)
    addressed = physical.held_schedule(graph, moves, forms, grid, expected, control=True)
    need(addressed["live_sender_alias_control_rejected"] and addressed["retired_and_guards_restored"],
         "complete addressed storage controls")
    caller = source_read("data/CALLER.json.gz")
    signed = signed_caller(caller, layout, 2025, 9)
    need(json.loads(json.dumps(signed)) == published["caller"], "same complete signed caller")
    scalars = physical.scalar_cases([forms], caller, (2025, ODD))
    budget = physical.ordinary_budget(bound | exact | addressed, signed, 3536, scalars["coefficient_bits"])
    old = published["physical"]["ordinary"]
    need(all(value == old[key] for key, value in budget.items() if key != "scalar_step_rate"),
         "all ordinary counts and layout charges retained")
    need(scalars["coefficient_bits"] == 14 and budget["scalar_step_rate"] == 2**22
         and old["scalar_step_rate"] == 128 * budget["scalar_step_rate"], "exact finite scalar-rate reduction")
    need(ODD < bound["path_grid_odd"] and HEIGHT == bound["path_grid_height"], "old root envelope dominates")
    guard = physical.check_depth_guard(published["physical"]["common_root"], int(published["compiler"]["H"]))
    need(guard == published["physical"]["depth_guard"], "retained depth guard")
    return dict(status="PASS_MINIMAL_ODD_PHYSICAL_SUBSTITUTION", graph_sha256=published["graph_sha256"],
                source_pins=pins, coefficient_certificate=certificate, physical_columns=physical_columns,
                implementation_odd=ODD, implementation_binary_height=HEIGHT, implementation_grid=grid,
                exact=exact, addressed=addressed, scalars=scalars, ordinary=budget,
                conservative_source_path_bounds=bound, retained_root_envelope=published["physical"]["common_root"],
                retained_compiler_H=published["compiler"]["H"], retained_depth_guard=guard,
                conditional_interfaces=published["conditional_interfaces"],
                scalar_rate_reduction=128, contract_controls=contract_controls(),
                partial_clear_control=physical.partial_clear_control())


if __name__ == "__main__":
    result = verify()
    need(json.loads(json.dumps(result)) == json.loads((HERE / "RESULT.json").read_text()), "receipt mismatch")
    print(result["status"], result["implementation_odd"], result["scalar_rate_reduction"])

"""Check the physical bill and complete conditional compiler application.

The calculation uses the retained engines from PR7704 and PR7713.
See CREDITS.md for source authors and the exact source files.
"""
from collections import Counter
from copy import deepcopy
from fractions import Fraction as F
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import HERE, digest, inputs, jobs, need, owner_stages, physical, provenance, read, receipt
from caller16 import signed_caller
from interval_gate_signed import gate

sys.path.insert(0, str(HERE.parents[1] / "scripts"))
from compare_recursive_invoices import compare_invoices
from evaluate_recursive_power import evaluate

price = read("PRICE.json")
CLAIM, PROBE = price["claim"], price["probe"]
LOWER, UPPER = price["bracket"]
PREVIOUS_UPPER = "0.00376313686062"
PREVIOUS_GAIN = "0.00002115478655"
BIT = "0.00385248"


def selected_interfaces():
    claim = read("vendor/selected-claim.json")
    bit, = [r for r in claim["uniform_templates"] if r["family"] == "BIT before cover"]
    validation, repair = read("vendor/selected-validation.json"), read("vendor/selected-bit-ambient.json")
    need(bit["ambient"] == 134 and bit["rank_encoding"] == "2^296630000000000"
         and F(bit["saving"]) > F(BIT), "selected BIT bound")
    need(validation["status"] == "admitted_conditional" and validation["registered_replays_complete"]
         and repair["exit_code"] == 0 and repair["source_unchanged"], "selected conditional record")
    assumptions = [r["id"] for r in claim["assumptions"]]
    need(assumptions == ["native_all_columns", "owned_erasure", "compiler", "precision_tape",
                         "analytic_recovery"], "five inherited interfaces")
    return assumptions


def invoice(native, helpers, signed, contract):
    def total(local, fixed):
        count = Counter({r: signed["calls"] * n for r, n in local.items()})
        count.update(fixed)
        return {str(r): n for r, n in sorted(count.items())}
    return dict(schema="integer-mult-recursive-invoice/v1", contract=contract,
                paid=total(native, signed["fixed_caller_paid"]),
                targets=total(helpers, signed["fixed_root_targets"]))


def prices(old, new):
    order = compare_invoices(old, new)
    empty = dict(new, paid={}, targets={})
    points = []
    for hist, at, sign in ((old, PREVIOUS_UPPER, "higher"), (new, PREVIOUS_UPPER, "lower"),
                           (new, CLAIM, "lower"), (new, PROBE, "lower"),
                           (new, LOWER, "lower"), (new, UPPER, "higher")):
        result = evaluate(empty, hist, 1 - F(at), 256)
        need(result["classification"] == "new_cost_" + sign, "directed power at " + at)
        points.append(dict(graph="parent" if hist is old else "candidate", kappa=at,
                           paid_minus_productive=result["new_minus_old"]))
    weights = {name: {int(r): n for r, n in new[key].items()}
               for name, key in (("P", "paid"), ("T", "targets"))}
    compiler = gate(weights, CLAIM, PROBE, LOWER, UPPER, BIT)
    need(F(CLAIM) - F(PREVIOUS_UPPER) > F(PREVIOUS_GAIN), "separated complete lower point")
    return order, points, compiler


def verify():
    source_files = provenance()
    assumptions = selected_interfaces()
    graph, layout, moves, rows, interface = inputs()
    caller = read("data/CALLER.json.gz")
    signed = signed_caller(caller, layout, 2025, 9)
    stages = owner_stages(layout, interface[0], caller)
    alias = deepcopy(caller)
    joint = next(e for e in alias["events"] if e[0] == "J")
    joint[2][1] = joint[2][0]
    try:
        owner_stages(layout, interface[0], alias)
    except ValueError as error:
        need(str(error) == "signed main owners", "owner alias rejection reason")
    else:
        raise ValueError("aliased caller owners accepted")
    native_jobs, helpers, _ = jobs(graph, interface[0], moves)
    parent = read("data/COMPARATOR-APPLICATION.json")
    need(parent["bracket"][1] == PREVIOUS_UPPER, "parent crossing pin")
    new = invoice(native_jobs, helpers, signed, parent["invoice"]["contract"])
    order, powers, compiler = prices(parent["invoice"], new)
    native = physical.graph_bounds(graph, moves, rows, interface[0])
    grid = native["path_grid"]
    expected = physical.expected_rows(layout["public"], layout, interface, grid)
    native.update(physical.exact_basis_grid(graph, moves, rows, grid, expected))
    native.update(physical.held_schedule(graph, moves, rows, grid, expected, control=True))
    need(native["live_sender_alias_control_rejected"]
         and set(native["missing_odd_factor_controls"]) == {3, 5}, "inherited grid and sender controls")
    missing_primes = []
    for prime in (7, 17):
        reduced = grid
        while reduced % prime == 0:
            reduced //= prime
        if reduced == grid:
            continue
        try:
            physical.exact_basis_grid(graph, moves, rows, reduced,
                                      physical.expected_rows(layout["public"], layout, interface, reduced))
        except ValueError as error:
            need(str(error) == "nonintegral scalar pre-product", "missing prime rejection")
        else:
            raise ValueError("inexact product accepted")
        missing_primes.append(prime)
    envelope = physical.caller_envelope(caller)
    need(envelope["uses"] == signed["uses"], "independent caller count")
    root = physical.root_envelope({"candidate": native}, envelope)
    guard = physical.check_depth_guard(root, int(compiler["H"]))
    scalars = physical.scalar_cases([rows], caller, (signed["odd_scale"], native["path_grid_odd"]))
    shifts = sum(len(t["ports"]) * sum(row[0] < 0 for row in t["diagonal"]) for t in caller["types"].values())
    need(shifts == 3536, "all negative-q translations")
    ordinary = physical.ordinary_budget(native, signed, shifts, scalars["coefficient_bits"])
    paid, productive = sum(new["paid"].values()), sum(new["targets"].values())
    need((paid, productive) == (ordinary["raw_paid_positions"], ordinary["raw_productive_targets"]), "complete physical and recursive denominators")
    need(productive == signed["root_owners"] + sum(stage[2] for stage in stages), "complete productive owners")
    return dict(claim=CLAIM, probe=PROBE, bracket=[LOWER, UPPER], previous_upper=PREVIOUS_UPPER,
                authenticated_package_sources=source_files,
                gain_over_previous_upper=str(F(CLAIM) - F(PREVIOUS_UPPER)), graph_sha256=digest(graph),
                stages=stages, owner_alias_rejected=True, caller=signed, paid=paid, productive=productive, invoice=new,
                comparison=order, powers=powers, compiler=compiler, conditional_interfaces=assumptions,
                physical=dict(native=native, caller_envelope=envelope, common_root=root, depth_guard=guard,
                              ordinary=ordinary, scalars=scalars, extra_prime_rejections=missing_primes,
                              partial_clear_control=physical.partial_clear_control()))


if __name__ == "__main__":
    need(sys.flags.optimize == 0, "outer gate assertions enabled")
    result = verify()
    receipt("application", result)
    print("PASS_INTERLEAVED_APPLICATION", CLAIM, result["paid"], result["productive"])

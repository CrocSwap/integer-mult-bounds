"""Price the complete application and check its compact physical schedule."""
from collections import Counter
from fractions import Fraction
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from quotient import HERE, construct_candidate, digest, main_roles, need, parent, read, receipt, recoding
from catalogue import jobs
from caller16 import signed_caller
from interval_gate import gate
from vendor import physical

sys.path.insert(0, str(HERE.parents[1] / "scripts"))
from compare_recursive_invoices import compare_invoices
from evaluate_recursive_power import evaluate

CLAIM, PROBE = "0.00376154487703", "0.00376154487710"
LOWER, UPPER = "0.00376154487711", "0.00376154487712"
PREVIOUS_UPPER, PREVIOUS_GAIN = "0.00374039009048", "0.00001034832006"
BIT = "0.00376669"


def selected_interfaces():
    vendor = HERE / "vendor"
    claim = read(vendor / "selected-claim.json")
    bit, = [row for row in claim["uniform_templates"] if row["family"] == "BIT before cover"]
    validation = read(vendor / "selected-validation.json")
    repair = read(vendor / "selected-bit-ambient.json")
    need(bit["ambient"] == 134 and bit["rank_encoding"] == "2^296630000000000" and
         Fraction(bit["saving"]) > Fraction(".00385248") > Fraction(BIT), "selected BIT pin")
    need(validation["status"] == "admitted_conditional" and validation["registered_replays_complete"]
         and repair["exit_code"] == 0 and repair["source_unchanged"], "selected conditional record")
    assumptions = [item["id"] for item in claim["assumptions"]]
    need(assumptions == ["native_all_columns", "owned_erasure", "compiler", "precision_tape",
                         "analytic_recovery"], "selected interfaces")
    return assumptions


def owners(word, source, layout, net, keep, caller):
    original_mains, hosted, _ = physical.public_interface(
        dict(initial=source.initial, final=source.final, frames=word["frames"]), word)
    mains = main_roles(layout)
    need(len(mains) == 400 and {keep[r] for r in mains} == original_mains, "all original main owners")
    need(all((a, b) == (source.initial[old], source.final[old])
             for old, a, b in zip(keep, net.initial, net.final, strict=True)), "surviving owner charts")
    h = layout["hosted"]
    planes = list(zip(h["X2"], h["Y2"], strict=True))
    second = dict(zip(h["Dports"], planes, strict=True))
    need(all(net.initial[a] == net.initial[b] and net.final[a] == net.final[b]
             for i, pair in second.items()
             for a, b in zip((layout["live"][i], layout["live"][i] + 112), pair, strict=True)),
         "hosted second-plane charts")
    helpers = set(range(layout["public"])) - mains
    seen = set()
    stages = []
    for event in caller["events"]:
        if event[0] != "J":
            continue
        _, stage, group_a, group_b = event
        bound = {}
        for i, x in enumerate(layout["live"]):
            slots = (x, x + 112) + second.get(i, ())
            roles = group_a if i in second else group_b[:2]
            for slot, role in zip(slots, roles, strict=True):
                need(slot not in bound, "main owner alias")
                bound[slot] = (i, role)
        need(bound.keys() == mains and len(set(bound.values())) == 400, "signed stage owners")
        fresh = {(stage, keep[r]) for r in helpers}
        need(fresh.isdisjoint(seen), "repeated productive helper")
        seen.update(fresh)
        stages.append([stage, len(bound), len(fresh)])
    need([s[0] for s in stages] == list(range(1, 17)), "complete signed stages")
    return (mains, hosted, planes), stages


def invoice(net, layout, signed, contract):
    native, helpers, _ = jobs(net, layout)
    calls = signed["calls"]
    paid = Counter({r: calls * n for r, n in native.items()})
    paid.update(signed["fixed_caller_paid"])
    targets = Counter({r: calls * n for r, n in helpers.items()})
    targets.update(signed["fixed_root_targets"])
    def formatted(histogram):
        return {str(r): n for r, n in sorted(histogram.items())}
    return dict(schema="integer-mult-recursive-invoice/v1", contract=contract,
                paid=formatted(paid), targets=formatted(targets))


def reconcile_debits(word, source, new, old, calls):
    dims = [len(b) for b in word["frames"]]
    removed = {"paid": Counter(), "targets": Counter()}
    paid_keys, roles = set(), set()
    for edit in read(HERE / "QUOTIENTS.json"):
        role = edit["role"]
        need(role not in roles, "duplicate helper debit")
        roles.add(role)
        rank = abs(dims[source.final[role]] - dims[source.initial[role]])
        removed["targets"][str(rank)] += calls
        for bank in edit["banks"]:
            key = bank["remove"]
            need(key not in paid_keys, "duplicate paid credit")
            paid_keys.add(key)
            a, b = source.moves[key]
            removed["paid"][str(abs(dims[b] - dims[a]))] += calls
    for field, changes in removed.items():
        count = Counter(old[field])
        count.subtract(changes)
        need(+count == Counter(new[field]) and all(n >= 0 for n in count.values()),
             "parent less the certificate entries must equal the observed " + field)
    return {field: dict(values) for field, values in removed.items()}


def prices(old, new):
    empty = dict(new, paid={}, targets={})
    points = []
    tests = [(old, PREVIOUS_UPPER, "higher"), (new, PREVIOUS_UPPER, "lower"), (new, CLAIM, "lower"),
             (new, PROBE, "lower"), (new, LOWER, "lower"), (new, UPPER, "higher")]
    for hist, at, sign in tests:
        result = evaluate(empty, hist, 1 - Fraction(at), 256)
        need(result["classification"] == "new_cost_" + sign, "directed power check at " + at)
        points.append(dict(graph="parent" if hist is old else "candidate", kappa=at,
                           paid_minus_productive=result["new_minus_old"]))
    weights = {name: {int(r): n for r, n in new[key].items()} for name, key in (("P", "paid"), ("T", "targets"))}
    compiler = gate(weights, CLAIM, PROBE, LOWER, UPPER, BIT)
    need(Fraction(CLAIM) - Fraction(PREVIOUS_UPPER) > 2 * Fraction(PREVIOUS_GAIN), "larger certified gain")
    return points, compiler


def machine(net, layout, interface, caller, signed, graph, h):
    moves = net.moves
    rows = {k: sorted(v.items()) for k, v in net.forms.items()}
    audit = physical.graph_bounds(graph, moves, rows, interface[0])
    grid = audit["path_grid"]
    expected = physical.expected_rows(layout["public"], layout, interface, grid)
    audit.update(physical.exact_basis_grid(graph, moves, rows, grid, expected))
    audit.update(physical.held_schedule(graph, moves, rows, grid, expected, control=True))
    need(audit["live_sender_alias_control_rejected"] and set(audit["missing_odd_factor_controls"]) == {3, 5},
         "physical controls")
    envelope = physical.caller_envelope(caller)
    need(envelope["uses"] == signed["uses"], "independent caller count")
    root = physical.root_envelope({"candidate": audit}, envelope)
    guard = physical.check_depth_guard(root, h)
    scalars = physical.scalar_cases([rows], caller, (signed["odd_scale"], audit["path_grid_odd"]))
    shifts = sum(len(t["ports"]) * sum(row[0] < 0 for row in t["diagonal"]) for t in caller["types"].values())
    ordinary = physical.ordinary_budget(audit, signed, shifts, scalars["coefficient_bits"])
    return dict(native=audit, caller_envelope=envelope, common_root=root, depth_guard=guard,
                ordinary=ordinary, scalars=scalars, partial_clear_control=physical.partial_clear_control())


def verify():
    assumptions = selected_interfaces()
    word, source = parent()
    net, layout, keep = construct_candidate(word, source)
    caller = read(HERE / "data/CALLER.json.gz")
    signed = signed_caller(caller, layout, 2025, 9)
    interface, stages = owners(word, source, layout, net, keep, caller)
    published = read(HERE / "data/PARENT-APPLICATION.json")
    old = invoice(source, word, signed, published["invoice"]["contract"])
    new = invoice(net, layout, signed, old["contract"])
    need(old == published["invoice"] and published["bracket"][1] == PREVIOUS_UPPER,
         "independent parent price")
    debits = reconcile_debits(word, source, new, old, signed["calls"])
    order = compare_invoices(old, new)
    need(order["classification"] == "uniformly_better", "concave signed comparison")
    points, compiler = prices(old, new)
    graph = recoding.layout(layout, net)
    proof = machine(net, layout, interface, caller, signed, graph, int(compiler["H"]))
    paid, productive = sum(new["paid"].values()), sum(new["targets"].values())
    need((paid, productive) == (proof["ordinary"]["raw_paid_positions"], proof["ordinary"]["raw_productive_targets"]),
         "physical and recursive denominators")
    need(productive == signed["root_owners"] + sum(stage[2] for stage in stages), "complete owner debit")
    return dict(claim=CLAIM, probe=PROBE, bracket=[LOWER, UPPER], previous_upper=PREVIOUS_UPPER,
                graph_sha256=digest(graph), retained_labels_sha256=digest(keep), paid=paid,
                productive=productive, caller=signed, stages=stages, invoice=new, removed=debits, comparison=order,
                powers=points, compiler=compiler, physical=proof, conditional_interfaces=assumptions)


if __name__ == "__main__":
    need(sys.flags.optimize == 0, "outer gate assertions enabled")
    result = verify()
    receipt("application", result)
    print("PASS_HELPER_QUOTIENT_APPLICATION", result["claim"], result["paid"], result["productive"])

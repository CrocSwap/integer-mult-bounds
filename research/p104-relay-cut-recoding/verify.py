"""Bind the recoded DAG to the signed application, physical schedule and price."""
from collections import Counter
from fractions import Fraction
from graphlib import CycleError
from hashlib import sha256
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from recoding import HERE, Network, apply, encoded, layout, need, read, receipt, sources
from caller16 import signed_caller
from catalogue import rank_data
from interval_gate import gate
from network import main_roles
from vendor import physical

sys.path.insert(0, str(HERE.parents[1] / "scripts"))
from compare_recursive_invoices import compare_invoices
from evaluate_recursive_power import evaluate

CLAIM, PROBE = "0.00374039009039", "0.00374039009046"
LOWER, UPPER = "0.00374039009047", "0.00374039009048"
PARENT_LOWER, PARENT_UPPER = "0.00373004177032", "0.00373004177033"
BIT = "0.00376669"


def selected_bit():
    vendor = HERE / "vendor"
    claim = read(vendor / "selected-claim.json")
    bit = next(row for row in claim["uniform_templates"] if row["family"] == "BIT before cover")
    validation = read(vendor / "selected-validation.json")
    repair = read(vendor / "selected-bit-ambient.json")
    assumptions = [a["id"] for a in claim["assumptions"]]
    need(bit["ambient"] == 134 and bit["rank_encoding"] == "2^296630000000000"
         and Fraction(bit["saving"]) > Fraction("0.00385248") > Fraction(BIT)
         and repair["exit_code"] == 0 and repair["source_unchanged"]
         and validation["status"] == "admitted_conditional" and validation["registered_replays_complete"],
         "selected BIT and ambient repair")
    need(assumptions == ["native_all_columns", "owned_erasure", "compiler", "precision_tape",
                         "analytic_recovery"], "inherited scientific interfaces")
    return assumptions


def stage_owners(word, caller):
    h = word["hosted"]
    second = dict(zip(h["Dports"], zip(h["X2"], h["Y2"], strict=True), strict=True))
    mains = main_roles(word)
    helpers = sorted(set(range(word["public"])) - mains)
    seen = set()
    stages = []
    for event in caller["events"]:
        if event[0] != "J":
            continue
        _, stage, type_a, type_b = event
        owners = {}
        for port, x in enumerate(word["live"]):
            slots = (x, x + 112)
            if port in second:
                slots += second[port]
            roles = type_a if port in second else type_b[:2]
            owners.update(zip(slots, [(port, role) for role in roles], strict=True))
        need(set(owners) == mains and len(set(owners.values())) == 400, "injective main assignment")
        fresh = {("helper", stage, r) for r in helpers}
        need(len(fresh) == 1101 and fresh.isdisjoint(seen), "fresh productive owners")
        seen.update(fresh)
        stages.append([stage, len(owners), len(fresh)])
    need(len(stages) == 16, "actual joint stages")
    return stages


def bill(word, net, signed, contract):
    native, helper, _ = rank_data(word, net)
    calls = signed["calls"]
    paid = Counter({r: n*calls for r,n in native.items()})
    paid.update(signed["fixed_caller_paid"])
    targets = Counter({r: n*calls for r,n in helper.items()})
    targets.update(signed["fixed_root_targets"])
    return dict(schema="integer-mult-recursive-invoice/v1", contract=contract,
                paid={str(r): n for r,n in sorted(paid.items())},
                targets={str(r): n for r,n in sorted(targets.items())})


def price(parent, child):
    empty = dict(child, paid={}, targets={})
    checks = []
    for name, data, at, sign in (
            ("parent", parent, PARENT_LOWER, "lower"), ("parent", parent, PARENT_UPPER, "higher"),
            ("parent", parent, CLAIM, "higher"), ("candidate", child, CLAIM, "lower"),
            ("candidate", child, PROBE, "lower"), ("candidate", child, LOWER, "lower"),
            ("candidate", child, UPPER, "higher")):
        result = evaluate(empty, data, 1-Fraction(at), 256)
        need(result["classification"] == "new_cost_" + sign, "independent signed moment")
        checks.append([name, at, sign, result["new_minus_old"]])
    paid = {int(r): n for r,n in child["paid"].items()}
    target = {int(r): n for r,n in child["targets"].items()}
    compiler = gate({"P": paid, "T": target}, CLAIM, PROBE, LOWER, UPPER, BIT)
    return checks, compiler


def physical_application(graph, word, caller, signed, h):
    interface = physical.public_interface(graph, word)
    moves, rows = physical.graph_inputs(graph)
    audit = physical.graph_bounds(graph, moves, rows, interface[0])
    grid = audit["path_grid"]
    expected = physical.expected_rows(audit["public"], word, interface, grid)
    audit.update(physical.exact_basis_grid(graph, moves, rows, grid, expected))
    audit.update(physical.held_schedule(graph, moves, rows, grid, expected, control=True))
    need(audit["live_sender_alias_control_rejected"] and set(audit["missing_odd_factor_controls"]) == {3, 5},
         "parked sender and odd-grid controls")
    envelope = physical.caller_envelope(caller)
    need(envelope["uses"] == signed["uses"], "weighted signed caller counts")
    root = physical.root_envelope({"candidate": audit}, envelope)
    guard = physical.check_depth_guard(root, h)
    scalars = physical.scalar_cases([rows], caller, (signed["odd_scale"], audit["path_grid_odd"]))
    translations = sum(len(kind["ports"])*sum(row[0] < 0 for row in kind["diagonal"])
                       for kind in caller["types"].values())
    ordinary = physical.ordinary_budget(audit, signed, translations, scalars["coefficient_bits"])
    return dict(native=audit, caller_envelope=envelope, common_root=root, depth_guard=guard,
                ordinary=ordinary, scalars=scalars, partial_clear_control=physical.partial_clear_control())


def schedule_controls(net):
    moves = net.moves.copy()
    key = next(iter(moves))
    _, dst = moves[key]
    moves[key] = (dst, dst)
    forms = net.forms.copy()
    forms[key] = {key: Fraction(1)}
    try:
        Network(net.first_output, net.initial, net.final, moves, forms).schedule()
    except CycleError:
        pass
    else:
        raise ValueError("cycle control")
    try:
        Network(net.first_output, net.initial, net.final, moves, net.forms).schedule()
    except ValueError as exc:
        need(str(exc) == "nonlocal scalar", "wrong-chart rejection reason")
    else:
        raise ValueError("nonlocal read control")


def application():
    assumptions = selected_bit()
    word, source, edits = sources()
    net = apply(source, edits, word["frames"])
    schedule_controls(net)
    caller = read(HERE / "data/CALLER.json.gz")
    signed = signed_caller(caller, word, 2025, 9)
    stages = stage_owners(word, caller)
    published = read(HERE / "data/PARENT-PRICE.json")["invoices"]["candidate"]
    parent = bill(word, source, signed, published["contract"])
    child = bill(word, net, signed, published["contract"])
    need(parent == published and parent["targets"] == child["targets"], "matched parent boundary")
    preflight = compare_invoices(parent, child)
    need(preflight["classification"] == "uniformly_better", "concave tariff comparison")
    signs, compiler = price(parent, child)
    graph = layout(word, net)
    machine = physical_application(graph, word, caller, signed, int(compiler["H"]))
    costs = machine["ordinary"]
    paid, target = sum(child["paid"].values()), sum(child["targets"].values())
    surplus = sum(int(r)*n for r,n in child["targets"].items()) - sum(int(r)*n for r,n in child["paid"].items())
    need((paid, target, surplus) == (costs["raw_paid_positions"], costs["raw_productive_targets"], 1328),
         "match positive physical and recursive counts")
    delta = {r: child["paid"].get(r, 0) - parent["paid"].get(r, 0)
             for r in child["paid"].keys() | parent["paid"].keys()}
    return dict(claim=CLAIM, probe=PROBE, bracket=[LOWER, UPPER], parent_bracket=[PARENT_LOWER, PARENT_UPPER],
                graph_sha256=sha256(encoded(graph)).hexdigest(), cut_counts=dict(Counter(e["kind"] for e in edits)),
                invoice=child, paid_delta={r: n for r,n in delta.items() if n}, paid=paid,
                productive=target, signed_rank_surplus=surplus, caller=signed, stages=stages,
                preflight=preflight, powers=signs, compiler=compiler, physical=machine,
                conditional_interfaces=assumptions)


if __name__ == "__main__":
    need(sys.flags.optimize == 0, "compiler assertions enabled")
    result = application()
    receipt("application", result)
    print("PASS_RELAY_CUT_APPLICATION", result["claim"], result["paid"], result["productive"])

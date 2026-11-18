"""Check both full prices, compiler funding, precision, and fresh physical costs."""
from collections import Counter
from fractions import Fraction
from hashlib import sha1, sha256
from pathlib import Path
import json
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path[:0] = [str(HERE), str(HERE / "source"), str(ROOT / "scripts")]
from banks import verify as verify_banks
from caller import caller_replay
from native import span, run as verify_native
from word import main_roles, need, words
from interval_gate import gate
from evaluate_recursive_power import evaluate

CLAIM = "0.0037194530062"
PROBE = "0.00371945300627"
LOWER = "0.00371945300635"
UPPER = "0.00371945300636"
BIT = "0.00376669"


def verify_inputs():
    for pin in json.loads((HERE / "SOURCE-PINS.json").read_bytes()):
        raw = (HERE / pin["copy"]).read_bytes()
        need(sha256(raw).hexdigest() == pin["sha256"], "source digest")
        need(sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest() == pin["git_blob"], "source Git blob")


def complete(word, audited):
    paid = Counter(audited["paid"])
    targets = Counter(audited["targets"])
    calls = audited["calls"]
    basis = word["frames"]
    for e in word["program"]:
        if e[0] == "MOVE":
            paid[abs(len(basis[e[3]]) - len(basis[e[2]]))] += calls
    mains = main_roles(word)
    for r, (a, b) in enumerate(zip(word["initial"], word["final"], strict=True)):
        if r not in mains:
            targets[len(basis[b]) - len(basis[a])] += calls
    return paid, targets


def delta(new, old):
    return {r: new[r] - old[r] for r in sorted(new.keys() | old.keys()) if new[r] != old[r]}


def invoice(paid, targets):
    return {"schema": "integer-mult-recursive-invoice/v1",
            "contract": {"model": "mixed-target-unnormalized-power-v1", "ambient_rank": 145,
                         "rank_semantics": "One positive rank-r child costs r^(1-C).",
                         "boundary": "All 17 signed native calls and all caller operations."},
            "paid": {str(r): n for r, n in sorted(paid.items())}, "targets": {str(r): n for r, n in sorted(targets.items())}}


def owner_geometry(word, caller):
    h = word["hosted"]
    all_ports = set(range(len(word["ports"])))
    hosted = dict(zip(h["Dports"], zip(h["X2"], h["Y2"], strict=True), strict=True))
    need(len(hosted) == 96 and len(all_ports) == 104, "signed port count")
    masks = [span(f) for f in word["frames"]]
    records = []
    for e in caller["events"]:
        if e[0] != "J":
            continue
        owner = {}
        for j, (x, q) in enumerate(zip(word["live"], word["ports"], strict=True)):
            y = x + 112
            need(masks[word["initial"][x]] == {0, q} and len(masks[word["final"][x]]) == 512, "first main boundary")
            need(masks[word["initial"][y]] == {0} and masks[word["final"][y]] == {b for b in range(512) if (b & q).bit_count() % 2 == 0}, "second main boundary")
            slots = (x, y)
            roles = e[3][:2]
            if j in hosted:
                u, v = hosted[j]
                need(all(word[k][a] == word[k][b] for k in ("initial", "final") for a, b in ((x, u), (y, v))), "second-plane charts")
                slots += (u, v)
                roles = e[2]
            for slot, role in zip(slots, roles, strict=True):
                need(slot not in owner, "native slot alias")
                owner[slot] = (j, role)
        need(set(owner) == main_roles(word) and len(set(owner.values())) == len(owner), "stage owner bijection")
        records.append(len(owner))
    return records


def bound_bits(q):
    q = Fraction(q)
    return max(0, ((q.numerator + q.denominator - 1) // q.denominator).bit_length())


def run(native):
    verify_inputs()
    parent, candidate = words()
    caller = json.loads((HERE / "data/caller.json").read_bytes())
    audited = caller_replay(caller, candidate)
    old_p, old_t = complete(parent, audited)
    paid, targets = complete(candidate, audited)
    need(sum(old_p.values()) == 108581 and sum(targets.values()) == 22461, "parent and output census")
    signed = gate({"P": paid, "T": targets}, CLAIM, PROBE, LOWER, UPPER, BIT)
    reference = invoice({}, {})
    old = invoice(old_p, old_t)
    cur = invoice(paid, targets)
    signs = []
    for word, at, sign in ((old, "0.0037170835568", "lower"), (old, "0.0037170835569", "higher"),
                           (old, CLAIM, "higher"), (cur, CLAIM, "lower"), (cur, PROBE, "lower"),
                           (cur, LOWER, "lower"), (cur, UPPER, "higher")):
        check = evaluate(reference, word, 1 - Fraction(at), 256)
        need(check["classification"] == "new_cost_" + sign, "independent signed price")
        signs.append([at, sign, check["new_minus_old"]])
    census = verify_banks(candidate, caller, audited["calls"])
    owners = owner_geometry(candidate, caller)
    bad_events = caller["events"].copy()
    j = next(i for i, e in enumerate(bad_events) if e[0] == "J")
    op, stage, ar, br = bad_events[j]
    bad_events[j] = [op, stage, [ar[0], ar[0], *ar[2:]], br]
    try:
        owner_geometry(candidate, dict(caller, events=bad_events))
    except ValueError as exc:
        need(str(exc) == "stage owner bijection", "alias rejection reason")
    else:
        raise ValueError("caller-owner mutation escaped")
    uses = audited["uses"]
    nscalar = sum(e[0] != "MOVE" for e in candidate["program"])
    conversions = 2 * (audited["root_owners"] + audited["calls"] * candidate["public"])
    scalar_services = 32 * (audited["calls"] * nscalar + sum(uses.values()) + conversions)
    slots = (2 * sum(paid.values()) + 2 * sum(targets.values()) + 2 * sum(owners)
             + 2 * (uses["IDLE_ONE"] + uses["IDLE_ODD"]) + 3 * uses["QUERY"]
             + uses["LAMBDA"] + uses["IDLE_ODD"])
    # Use the compiler cap for each elementary map, including the ordinary wrappers.
    map_records = slots * 4 * (153 + 1)**2
    height = audited["dyadic_height"] + native["grid"][1]
    mass = Fraction(audited["peak_scaled_mass"]) * Fraction(native["peak_scaled_mass"])
    mass_bits = bound_bits(mass)
    c = 2 * max(height, mass_bits)
    H = int(signed["H"])
    K = 1920 * 153**1920 * (H + 1)**2
    need((c * K).bit_length() < H, "common root guard")
    need(census["numerator_bits"] + 2 <= 26, "temporary signed product")
    physical = dict(context_height=height, context_mass_upper=str(mass), context_mass_bits=mass_bits,
                    context_c=c, depth_times_c_bits=(c * K).bit_length(), H=H,
                    conversions=conversions, scalar_services=scalar_services,
                    scalar_bit_step_coefficient=scalar_services * 2**20,
                    native_contact_boundaries=2 * sum(owners), monomial_maps=slots,
                    elementary_records=map_records, fresh_private=census)
    return dict(caller=audited, main_owners_by_stage=owners, invoice=cur,
                paid_delta=delta(paid, old_p), target_delta=delta(targets, old_t),
                paid_count=sum(paid.values()), productive_count=sum(targets.values()),
                surplus=sum(r * (targets[r] - paid[r]) for r in paid.keys() | targets.keys()),
                gate=signed, directed_checks=signs, physical=physical)


if __name__ == "__main__":
    expected = json.loads((HERE / "RESULT.json").read_bytes())
    current = json.loads(json.dumps(run(verify_native())))
    need(current == expected["application"], "application receipt")
    print("PASS_JOINT_APPLICATION", CLAIM, current["paid_count"], current["productive_count"])

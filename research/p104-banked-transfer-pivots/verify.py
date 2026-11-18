"""Verify the complete application and compare it with the published parent."""
from collections import Counter
from fractions import Fraction
from graphlib import CycleError
from pathlib import Path
import json
import sys

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE / "source"), str(HERE.parents[1] / "scripts")]
from caller import caller_replay
from catalogue import rank_data
from evaluate_recursive_power import evaluate
from interval_gate import gate
from native import check_endpoints
from network import Network, need, networks, read, source_word
from physical import budget

CLAIM = "0.0037260455556"
PROBE = "0.00372604555567"
LOWER = "0.00372604555571"
UPPER = "0.00372604555572"
BIT = "0.00376669"


def complete(word, net, audited):
    native, helper, _ = rank_data(word, net)
    calls = audited["calls"]
    paid = Counter({r: calls * count for r, count in native.items()})
    target = Counter({r: calls * count for r, count in helper.items()})
    paid.update(audited["paid"])
    target.update(audited["targets"])
    return paid, target


def histogram(counter):
    return {str(i): n for i, n in sorted(counter.items())}


def ownership(word, caller):
    h = word["hosted"]
    hosted = dict(zip(h["Dports"], zip(h["X2"], h["Y2"], strict=True), strict=True))
    geom = []
    for e in caller["events"]:
        if e[0] != "J":
            continue
        pairs = []
        for j, x in enumerate(word["live"]):
            y = x + 112
            if j in hosted:
                u, v = hosted[j]
                for side in ("initial", "final"):
                    need(word[side][u] == word[side][x] and word[side][v] == word[side][y], "second-plane chart")
                pairs.extend(zip((x, y, u, v), ((j, r) for r in e[2]), strict=True))
            else:
                pairs.extend(zip((x, y), ((j, r) for r in e[3][:2]), strict=True))
        need(len(pairs) == len(dict(pairs)) == len({who for _, who in pairs}) == 400, "stage owners")
        geom.append(len(pairs))
    need(len(geom) == caller["stages"], "stage bindings")
    return geom


def controls(net):
    # A self-dependency and a wrong coframe must both fail before execution.
    node = next(iter(net.moves))
    move = net.moves[node]
    moves = net.moves.copy()
    moves[node] = (move[1], move[1])
    cyclic = Network(net.first_output, net.initial, net.final, moves, dict(net.forms))
    cyclic.forms[node] = {node: 1}
    try:
        cyclic.schedule()
    except CycleError:
        pass
    else:
        raise ValueError("causal cycle accepted")
    moves = net.moves.copy()
    moves[node] = (move[1], move[1])
    try:
        Network(net.first_output, net.initial, net.final, moves, net.forms).schedule()
    except ValueError as exc:
        need(str(exc) == "nonlocal scalar", "coframe control reason")
    else:
        raise ValueError("incorrect sender chart accepted")


def application():
    word = source_word()
    parent, net, edits = networks(word)
    controls(net)
    caller = read(HERE / "source/caller.json.gz")
    audited = caller_replay(caller, word)
    owners = ownership(word, caller)
    origin = read(HERE / "source/parent-invoice.json")
    old_paid, old_targets = complete(word, parent, audited)
    need(histogram(old_paid) == origin["paid"] and histogram(old_targets) == origin["targets"], "published parent invoice")
    paid, targets = complete(word, net, audited)
    need(targets == old_targets, "productive boundary")
    cur = dict(origin, paid=histogram(paid), targets=histogram(targets))
    empty = dict(origin, paid={}, targets={})
    signed = gate({"P": paid, "T": targets}, CLAIM, PROBE, LOWER, UPPER, BIT)
    signs = []
    for data, at, sign in ((origin, "0.0037218793483", "lower"), (origin, "0.0037218793484", "higher"),
                           (origin, CLAIM, "higher"), (cur, CLAIM, "lower"), (cur, PROBE, "lower"),
                           (cur, LOWER, "lower"), (cur, UPPER, "higher")):
        result = evaluate(empty, data, 1 - Fraction(at), 256)
        need(result["classification"] == "new_cost_" + sign, "independent price")
        signs.append([at, sign, result["new_minus_old"]])
    norm = check_endpoints(net, word)
    physical = budget(net, caller, norm, audited, paid, targets, signed)
    delta = {str(i): paid[i] - old_paid[i] for i in sorted(paid.keys() | old_paid.keys()) if paid[i] != old_paid[i]}
    return dict(native=norm, pivot_checks=len(edits),
                application=dict(claim=CLAIM, parent_upper="0.0037218793484", invoice=cur, paid_change=delta,
                                 parent_paid=sum(old_paid.values()), paid=sum(paid.values()), targets=sum(targets.values()),
                                 signed_surplus=sum(r * (targets[r] - paid[r]) for r in paid.keys() | targets.keys()),
                                 caller=audited, stage_owners=owners, pivots=edits, powers=signs, compiler=signed,
                                 physical=physical))


if __name__ == "__main__":
    need(sys.flags.optimize == 0, "directed gate requires assertions")
    result = application()
    stored = read(HERE / "RESULT.json")
    # JSON object keys are strings in the published receipt.
    need(json.loads(json.dumps(result)) == {k: stored[k] for k in result}, "application receipt")
    a = result["application"]
    print("PASS_BANKED_APPLICATION", a["claim"], a["paid"], a["targets"])

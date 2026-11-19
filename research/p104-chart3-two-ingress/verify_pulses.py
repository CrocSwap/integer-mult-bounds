#!/usr/bin/env python3
"""Replay two source-pinned adjoint pulse certificates using the Python standard library."""

from argparse import ArgumentParser
from collections import defaultdict
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import gzip
import json

HERE = Path(__file__).resolve().parent
HEAD = "89a67c404226d51028e135de2b9169e9020d57af"
WORD = "c447b6d5ba956fbe40834fe3c1bc69af2f225736f1b97ecd84b57bab9dd283cb"
LAYOUT = "f7de788c4a559282d35a9fce42f841a0e8de5a4015db871e718f9245569b0aa7"
E, F, P = 97760, 95681, 99128
SENDER, RELAY, RECEIVER = 768, 508, 3
RESTORATION = ((100967, Q(1)), (100945, Q(-1, 2)))


def need(condition, reason):
    if not condition:
        raise SystemExit(reason)


def content_hash(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def read(path):
    data = path.read_bytes()
    return json.loads(gzip.decompress(data) if data.startswith(b"\x1f\x8b") else data)


def adjoint(word):
    """Reverse the scalar incidences and swap the public input/output charts."""
    first = word["first_output"]
    size = len(word["initial"])
    moves = {k: (b, a) for k, a, b in word["moves"]}
    forms = {k: [] for k in (*moves, *range(first, first + size))}
    for reader, row in word["forms"]:
        donor = reader if reader in moves else ~(reader - first)
        for old_donor, coefficient in row:
            node = old_donor if old_donor >= 0 else (first + ~old_donor)
            forms[node].append((donor, Q(coefficient)))
    order = [k for k in reversed(word["schedule"]) if k in moves]
    order.extend(range(first, first + size))
    return moves, forms, order


def chart_banks_and_dependencies(word, moves, forms, order):
    """Check every old local read and retain its exact paid ancestor set."""
    first = word["first_output"]
    charts = {~i: c for i, c in enumerate(word["final"])}
    banks = defaultdict(list)
    for key, chart in charts.items():
        banks[chart].append(key)
    ids = {k: 1 << i for i, k in enumerate(moves)}
    ancestors = {k: 0 for k in charts}
    for k in order:
        source = moves[k][0] if k in moves else word["initial"][k - first]
        mask = ids.get(k, 0)
        for donor, _ in forms[k]:
            need(charts.get(donor) == source, f"invalid local read at {k} from {donor}")
            mask |= ancestors[donor]
        ancestors[k] = mask
        if k in moves:
            dest = moves[k][1]
            banks[dest].append(k)
            charts[k] = dest
    return banks, ids, ancestors


def propagate(forms, order, size, pulse, suppressed=()):
    node = {~i: Q(pulse.get(i, 0)) for i in range(size)}
    for k in order:
        node[k] = (Q(0) if k in suppressed
                   else sum((q * node[d] for d, q in forms[k] if node[d]), Q(0)))
    return node


def validate_pulse(data, support, forms, order, size, first):
    pairs = data["coordinates"]
    pulse = dict(pairs)
    need(len(pairs) == len(pulse) == support and all(0 <= i < size and type(q) is int and q for i, q in pairs),
         "sparse exact integer input")
    observed = propagate(forms, order, size, pulse)
    retired = propagate(forms, order, size, pulse, (E, F))
    impacted = [(i, observed[first + i] - retired[first + i])
                for i in range(size) if observed[first + i] != retired[first + i]]
    need(observed[F] == data["old_payload"] == -960, "exact required paid payload")
    need(len(impacted) == data["affected_terminals"] == 165 and
         impacted[0] == tuple(data["first_terminal"]) == (3, Q(60)), "protected terminal control")
    return observed


def certify_identity(forms, order):
    """Expand the restoration difference as an exact linear form on every input."""
    remaining = defaultdict(Q, RESTORATION)
    remaining[P] -= 1
    for k in reversed(order):
        weight = remaining.pop(k, 0)
        if weight:
            for donor, coefficient in forms[k]:
                remaining[donor] += weight * coefficient
    need(not any(remaining.values()), "exact H6 restoration of 99128 on the whole arbitrary input space")


def report(args):
    word, layout, data = read(args.word), read(args.layout), read(args.witnesses)
    size, first = len(word["initial"]), word["first_output"]
    need(content_hash(word) == WORD and content_hash(layout) == LAYOUT, "exact #7786 source and layout hashes")
    need(data["schema_version"] == 1 and data["source_head"] == HEAD, "source-bound witness data")
    need(word["frames"] == layout["frames"] and size == len(word["final"]) == layout["public"] == 1289,
         "all original arbitrary owner addresses")
    moves, forms, order = adjoint(word)
    need(moves[E] == (SENDER, RELAY) and moves[F] == moves[P] == (RELAY, RECEIVER), "exact original paid geometry")
    need([k for k in forms if any(donor == E for donor, _ in forms[k])] == [F], "old first leg exclusively feeds 95681")
    banks, ids, ancestors = chart_banks_and_dependencies(word, moves, forms, order)
    ban = ids[E] | ids[F]
    receiver = [k for k in banks[RECEIVER] if not ancestors[k] & ban]
    sender = [k for k in banks[SENDER] if not ancestors[k] & ban]
    producer = [k for k in banks[RELAY] if not ancestors[k] & ban]
    need(len(receiver) == len(banks[RECEIVER]) - 1 == 907 and P in receiver, "complete 907 receiver rows")
    need(set(sender) == set(banks[SENDER]) == {98835, 100945, 100947, 100967}, "complete four shortcut source rows")
    need(set(producer) == {89158, 91022, 98212, 99131, 99134} and set(banks[RELAY]) - set(producer) == {E},
         "complete five recoded ingress producer rows")
    need(set((k for k in receiver if moves[k][0] == RELAY)) == {P} and
         all(moves[k][0] != SENDER for k in receiver), "actual paid receiver source routes")

    q1 = validate_pulse(data["r14_pulse"], 167, forms, order, size, first)
    need(all(not q1[k] for k in receiver + sender) and q1[91022] == q1[98212] == 960,
         "first pulse's exact bank and producer values")
    certify_identity(forms, order)
    q2 = validate_pulse(data["r15_pulse"], 165, forms, order, size, first)
    need(all(not q2[k] for k in receiver + producer) and
         not sum((q2[k]*coefficient for k, coefficient in RESTORATION), Q(0)), "second pulse's full causal obstruction")

    roster = []
    for k in sorted(receiver):
        origin = moves[k][0]
        if origin == RELAY:
            continue
        mask = ban | ids[k]
        visible = {str(d): str(q1[d]) for d in banks[origin] if not ancestors[d] & mask and q1[d]}
        if visible:
            roster.append(dict(ingress=k, producer=origin, grade=abs(len(word["frames"][origin])-len(word["frames"][RECEIVER])),
                               causal_producer_nonzero_readers=visible))
    shortlist = data["saved_first_pulse_roster"]
    need([r["ingress"] for r in roster] == shortlist["paid_slots"] and len(roster) == 126
         and content_hash(roster) == shortlist["canonical_sha256"], "saved first-pulse roster identity")
    print(f"source {HEAD}")
    print(f"word {WORD}")
    print(f"layout {LAYOUT}")
    print("first pulse support 167 required 95681=-960 zero 907 receiver + 4 shortcut stock rows")
    print("first pulse retirement changes 165 terminals first 3=+60")
    print("99128 = 100967 - 100945/2 exactly on all 1289 arbitrary inputs")
    print("second pulse support 165 required 95681=-960 zero 907 receiver + 5 chart-508 stocks and restored 99128")
    print("second pulse retirement changes 165 terminals first 3=+60")
    print(f"saved first-pulse shortlist 126 sha256 {content_hash(roster)}")
    print("PASS pinned pulse and saved roster replay")


def main():
    args = ArgumentParser(description=__doc__)
    args.add_argument("--word", type=Path, default=HERE/"source"/"WORD.json.gz")
    args.add_argument("--layout", type=Path, default=HERE/"source"/"LAYOUT.json.gz")
    args.add_argument("--witnesses", type=Path, default=HERE/"WITNESSES.json")
    report(args.parse_args())


if __name__ == "__main__":
    main()

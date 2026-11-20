#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Replay the one-funded-payload cut for the saved S8 chart-266 paths."""

from collections import Counter, defaultdict
from fractions import Fraction
from functools import reduce
import gzip
from hashlib import sha256
import json
from operator import xor
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
INPUTS = HERE / "inputs"
PINS = {
    "WORD.json.gz": "d28f0d28d9d87d5fe57b8ef19e12faf98014f0bbef781987ce22daaa82f21cb9",
    "EFREE-CALLER.json.gz": "757b3523798f840bdb02028b23708c3416627a99ea09e7a3c4bcdc5cd0c7ce4b",
    "PHYSICAL.json": "fc59fbff30fc2ca1fb28a90b2cc8f9eb5f6c03b6ca4bcf677cb757d8e2aec612",
    "dual-price.json": "62e3d4e643e2be518c2b0a09bf73cc594c1be46bb6ae3aa6420a20156bc2f9b9",
    "literal.py": "4021766d87fa791a43a78a6665c9260b7ba3772d8b2db6e9c84b6a3d51a1305c",
    "price.py": "d720df6f3f7a22554e83d0c29243af3ee04fa036073404926bab7bc2f2687e1b",
}
WORD = "d3aa4426fa8fe7dc167270d01f2515184f2bff6a82744a14e941c5dd3afca27d"
LAYOUT = "a0ffffd99fb9b91f0013695877480766319ac51b926ed00dd5f7ec32f2d1e1a6"
HEAD = "14c74c6a67108f675ac1196a5f2415ead0920e71"
CAUSAL = "79e6a07f2e577b87051a57e6660c9eff9756306c59190c6f55db6b47323d4cf0"
ALTERNATE_HEAD = "cd282ce24fb3eea707f4342cecd1935ed367a1a3"
TARGET = "0.003889928046155"
RECEIVER = 266
HELD = {740, 753}
BIT = 252
BRIDGE = 3553


def load(name):
    data = (INPUTS / name).read_bytes()
    return json.loads(gzip.decompress(data) if name.endswith(".gz") else data)


def support(row):
    result = []
    while row:
        low = row & -row
        result.append(low.bit_length() - 1)
        row ^= low
    return result


def make_basis(rows):
    vectors = {}
    for row in rows:
        for pivot in sorted(vectors, reverse=True):
            if row >> pivot & 1:
                row ^= vectors[pivot]
        if row:
            vectors[row.bit_length() - 1] = row
    return vectors


def quotient(basis, row):
    for pivot in sorted(basis, reverse=True):
        if row >> pivot & 1:
            row ^= basis[pivot]
    return row


def extract_forward(word):
    """Track exact arbitrary input rows and chart-local provenance independently."""
    public = word["public"]
    state = [1 << i for i in range(public)] + [0] * word["owned_fields"]
    provenance = state.copy()
    routes, stock, readers = {}, defaultdict(dict), defaultdict(dict)
    for i, label in enumerate(word["start"]):
        stock[label][i] = state[i]
    for clock, (op, bank, *args) in enumerate(word["program"]):
        if op == "ADD":
            donor = args[0]
            state[bank] ^= state[donor]
            provenance[bank] ^= provenance[donor]
        elif op == "SWAP":
            peer = args[0]
            state[bank], state[peer] = state[peer], state[bank]
            provenance[bank], provenance[peer] = provenance[peer], provenance[bank]
        elif op in ("INIT", "CLEAR"):
            state[bank] = provenance[bank] = 0
        else:
            assert op == "MOVE"
            sender, receiver = args
            label = public + len(routes)
            routes[label] = (sender, receiver, clock)
            stock[receiver][label] = state[bank]
            readers[sender][label] = (state[bank], provenance[bank])
            provenance[bank] = 1 << label
    for i, chart in enumerate(word["final"]):
        readers[chart][~i] = (state[i], provenance[i])
    for chart, demands in readers.items():
        for row, operands in demands.values():
            assert row == reduce(xor, (stock[chart][k] for k in support(operands)), 0)
    return state[:public], routes, stock, readers


def price_invoice(word, charts, caller, old_tape, receipt, enrolled, lit, price):
    native_paid = old_tape["paid"]
    native_targets = Counter(charts.leg(a, b) for a, b in zip(word["start"][222:], word["final"][222:]))
    events = Counter(event[0] for event in caller["events"])
    calls = events["LOCAL"]
    paid, targets = lit.paired_invoice(caller, native_paid, native_targets, events)
    assert calls == enrolled["native_calls"] == 36
    assert paid == lit.histogram(enrolled["paid"]) == lit.histogram(receipt["paid"])
    assert targets == lit.histogram(enrolled["targets"]) == lit.histogram(receipt["targets"])
    assert native_paid == lit.histogram(receipt["native_paid"])
    assert native_targets == lit.histogram(receipt["native_targets"])
    ordinary = lit.ordinary(word, caller, events, paid, targets)
    assert ordinary == receipt["ordinary"]
    target = Fraction(TARGET)

    def priced(paid_delta, target_delta):
        paid_after = Counter(paid)
        paid_after.update(paid_delta)
        target_after = Counter(targets)
        target_after.update(target_delta)
        assert all(v > 0 for v in paid_after.values()) and all(v > 0 for v in target_after.values())
        return dict(
            paid_delta=paid_delta, target_delta=target_delta,
            paid=paid_after, targets=target_after,
            signed_margin=price.decimal_interval(
                price.moment(price.signed_profile(target_after, paid_after), target), 45),
        )

    baseline = priced({}, {})
    assert all(
        Fraction(a) <= Fraction(b)
        for a, b in zip(
            (enrolled["signed_margin"]["lower"], baseline["signed_margin"][1]),
            (baseline["signed_margin"][0], enrolled["signed_margin"]["upper"]),
        )
    )
    replacement = priced({2: calls, 3: -calls}, {})
    credit = price.decimal_interval(price.moment({3: calls, 2: -calls}, target), 45)
    extra = priced({1: calls, 2: calls, 3: -calls}, {})
    lost = priced({2: calls, 3: -calls}, {1: -calls})
    assert Fraction(replacement["signed_margin"][0]) > 0
    assert Fraction(extra["signed_margin"][1]) < 0 and lost["signed_margin"] == extra["signed_margin"]
    return dict(
        trial=TARGET, model="mixed-target-unnormalized-power-v1", native_calls=calls,
        native_paid=native_paid, native_targets=native_targets, pinned_baseline_ordinary=ordinary,
        baseline=baseline, hypothetical_fixed_grade_recode=replacement, directed_credit=credit,
        hypothetical_one_extra_grade_one_per_call=extra,
        hypothetical_one_grade_one_target_lost_per_call=lost,
    )


def cut_source_check(banks, incoming, stock, routes, bit):
    """The crossing pipes cannot import this coefficient under a one-payload edit."""
    external = [k for k in incoming if k in routes and routes[k][0] not in banks]
    fixed_nonzero = [k for k in external if stock[routes[k][1]][k] >> bit & 1]
    recode_nonzero = {
        k: [i for i, row in stock[routes[k][0]].items() if row >> bit & 1]
        for k in external
    }
    return external, fixed_nonzero, {k: v for k, v in recode_nonzero.items() if v}


def main():
    for name, digest in PINS.items():
        assert sha256((INPUTS / name).read_bytes()).hexdigest() == digest, name
    assert sha256(gzip.decompress((INPUTS / "CAUSAL-forward.json.gz").read_bytes())).hexdigest() == CAUSAL
    sys.path.insert(0, str(INPUTS))
    import literal as lit
    import price

    word, caller = load("WORD.json.gz"), load("EFREE-CALLER.json.gz")
    enrolled = load("dual-price.json")
    assert enrolled["target"] == TARGET and enrolled["head"] == HEAD
    assert enrolled["sides"]["binary"]["native_word"] == lit.canonical(word) == WORD
    assert enrolled["sides"]["binary"]["caller"] == PINS["EFREE-CALLER.json.gz"]
    assert lit.canonical({k: word[k] for k in ("frames", "start", "final")}) == LAYOUT
    charts = lit.Charts(word["frames"])
    assert charts.main_contacts(word["start"], word["final"]) == 111
    forward, tape, _ = lit.tape(word, charts)
    adjoint, adjoint_tape, _ = lit.tape(word, charts, adjoint=True)
    for reverse, rows, stat in ((False, forward, tape), (True, adjoint, adjoint_tape)):
        assert rows == lit.expected_rows(word["public"], reverse)
        assert stat["erase_dirty"] == word["owned_fields"]
    invoice = price_invoice(word, charts, caller, tape, load("PHYSICAL.json")["native"],
                            enrolled["sides"]["binary"], lit, price)

    end, routes, stock, readers = extract_forward(word)
    assert end == forward
    assert Counter(charts.leg(a, b) for a, b, _ in routes.values()) == tape["paid"]
    assert routes[BRIDGE] == (509, 1, 31290)
    assert word["start"][411] == 509 and word["final"][411] == 1
    assert readers[509][BRIDGE] == (1 << 411, 1 << 411)
    assert readers[1][~411] == (1 << 411, 1 << BRIDGE)

    def packet(label):
        a, b, clock = routes[label]
        row, coeff = readers[a][label]
        return dict(label=label, source=a, target=b, clock=clock, grade=charts.leg(a, b),
                    input_coefficients=support(row), stock_coefficients=support(coeff))

    def immediate_readers(label):
        target = routes[label][1]
        return {
            "chart": target,
            "paid_packets": [k for k, (_, operands) in readers[target].items()
                             if k >= 0 and operands >> label & 1],
            "public_outputs": [~k for k, (_, operands) in readers[target].items()
                               if k < 0 and operands >> label & 1],
        }

    staged, = [case for case in load("CAUSAL-forward.json.gz")["staged_hits"]
               if case["receiver"] == RECEIVER and set(case["held"]) == HELD]
    line, grade, first, first_donors, saved_peers = next(
        trial for trial in staged["first_safe_with_optimistic_second"] if trial[2] == 11
    )
    assert (line, grade, first, first_donors) == (1, 3, 11, [9, 737])
    assert routes[740] == (first, RECEIVER, 213) and routes[753] == (13, RECEIVER, 260)
    assert charts.leg(first, RECEIVER) == charts.leg(13, RECEIVER) == 3

    old_c = stock[RECEIVER]
    retained = [k for k in old_c if k not in HELD]
    assert retained == [1632, 1704, 1776, 1848]
    first_row = reduce(xor, (stock[first][k] for k in first_donors), 0)
    assert all(k not in routes or routes[k][2] < routes[740][2] for k in first_donors)
    assert first_row == old_c[740] and support(first_row) == [9, 247]
    basis = make_basis(old_c[k] for k in retained)
    r1, r2 = (quotient(basis, old_c[k]) for k in sorted(HELD))
    lines = [r1, r2, r1 ^ r2]
    assert [support(r) for r in lines[:2]] == staged["demand_basis"] == [[9, 247], [11, 252]]
    assert [r >> BIT & 1 for r in lines] == [0, 1, 1]
    assert not any(old_c[k] >> BIT & 1 for k in retained)

    demanded = [k for k, (r, _) in readers[RECEIVER].items() if r >> BIT & 1]
    assert demanded == [1919, 1921, 1922, 1923, 1924]

    cases = []
    for which_line, grade, peer, donors in saved_peers:
        banks = {RECEIVER, peer}
        assert charts.leg(peer, RECEIVER) == grade == 2
        wanted = reduce(xor, (stock[peer][k] for k in donors), 0)
        assert quotient(basis, wanted) == lines[which_line - 1] and wanted >> BIT & 1
        assert all(k in routes for k in stock[peer])  # There is no initial input at either bank.
        assert all(k in routes for k in old_c)
        incoming = retained + list(stock[peer])
        crossing, fixed_nonzero, recode_nonzero = cut_source_check(banks, incoming, stock, routes, BIT)
        assert not fixed_nonzero and not recode_nonzero
        external_demands = [k for k in demanded if routes[k][1] not in banks]
        # Even removing one such demand (the altered packet) leaves three external violations.
        assert len(external_demands) == 4
        peer_outputs = []
        for k in readers[peer]:
            assert k in routes
            peer_outputs.append(packet(k) | {"immediate_readers": immediate_readers(k)})
        cases.append(dict(
            banks=sorted(banks), candidate_route=[peer, RECEIVER, grade],
            saved_optimistic_line=which_line, saved_donors=donors,
            donor_rows=[packet(k) for k in donors],
            all_original_peer_ingresses=[packet(k) for k in stock[peer]],
            outside_edges_into_cut=[packet(k) for k in crossing],
            original_stocks_of_outside_producers=[
                dict(chart=c, stock_labels=list(stock[c]), nonzero_at_252=[])
                for c in sorted({routes[k][0] for k in crossing})
            ],
            external_demands_at_252=external_demands,
            surviving_external_demands_minimum=len(external_demands)-1,
            original_peer_outputs=peer_outputs,
        ))
    assert [case["candidate_route"][0] for case in cases] == [326, 439, 457, 475, 493]

    # The packet from 507 is funded, but admits e11 and still lacks e252.
    banks = {RECEIVER, 326}
    incoming = retained + list(stock[326])
    _, _, weaker_separation = cut_source_check(banks, incoming, stock, routes, 11)
    assert 1366 in weaker_separation[2292]
    perturbed = stock.copy()
    perturbed[507] = stock[507] | {1366: stock[507][1366] ^ (1 << BIT)}
    _, _, recode_control = cut_source_check(banks, incoming, perturbed, routes, BIT)
    assert recode_control == {2292: [1366]}
    _, old_ingress_breaks, _ = cut_source_check(banks, incoming + [753], stock, routes, BIT)
    assert old_ingress_breaks == [753]
    assert all(not (row & (1 << BIT)) for row in old_c.values() if row != old_c[753])

    output = dict(
        schema="s11-binary-coupled-banks/v1", status="excluded_on_saved_paths",
        source=dict(repository="CrocSwap/integer-mult-bounds", pr=7830, head=HEAD, word=WORD,
                    layout=LAYOUT, predecessor_step="s8-bit-basis-cost", predecessor_causal=CAUSAL,
                    overlap_pr_7793_head=ALTERNATE_HEAD, input_sha256=PINS),
        goal="goal-c9b923e487624c27b9078b5182fc7dee",
        step="s11-binary-coupled-banks",
        worker_binding="progress.goal-c9b923e487624c27b9078b5182fc7dee.00000163",
        scope=("Forward chart 266, fixed first line from chart 11 and one of five saved S8 "
               "grade-two return senders. Allow one funded packet to change its scalar payload at "
               "its existing endpoints. All other old payloads outside the held routes and all "
               "old terminal rows are fixed. Arbitrary retiming and unlimited chart-local stock granted."),
        invoice=invoice,
        source_replay=dict(native_scalar_coefficients_each_orientation=word["public"]**2,
                           native_paid_packets=len(routes), archived_program_clocks=len(word["program"]),
                           dirty_CLEARs_each_orientation=word["owned_fields"],
                           checked_unchanged_polynomial_diagonal_in_both_orientations=True),
        cut=dict(
            separating_input_coordinate=BIT,
            held=[packet(k) for k in sorted(HELD)],
            first=packet(740), quotient_line_supports=[support(r) for r in lines],
            receiver_retained=[packet(k) for k in retained],
            receiver_original_readers=[packet(k) | {"immediate_readers": immediate_readers(k)}
                                       for k in readers[RECEIVER]],
            required_receiver_packets_with_nonzero_projection=demanded,
            cases=cases,
        ),
        protected_bridge=packet(BRIDGE) | {"fixed_output_owner": 411},
        perturbations=dict(
            using_e11_instead_of_e252_gives_a_nonzero_outside_producer=weaker_separation,
            grant_e252_at_chart507_and_cut_rejects=recode_control,
            restore_old_grade_three_753_and_cut_rejects=old_ingress_breaks,
        ),
    )
    print(json.dumps(output, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()

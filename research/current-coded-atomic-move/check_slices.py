"""Bounded complete-field traces at genuine returned factor boundaries.

Each factor processes all4096 records. Reconstructed interfaces are compared
byte for byte, not inferred only from hashes. This is sliced execution; no
claim of a completed uninterrupted Python process is made.
Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from argparse import ArgumentParser
from hashlib import sha256
import json

from check_move import (S, active_positions, body, encode, fixture, gauss_mul,
                        hardware, header_bits, put, replace_column, rotate,
                        source_boundary, source_matrix)
from move_sources import need


def decode(bits, width):
    symbols = [sum(bits[j+k] << (2-k) for k in range(3)) for j in range(0, len(bits), 3)]
    step = width+1
    need(len(symbols) % (2*step) == 0, "whole fixed-width complex packet")
    values = []
    for j in range(0, len(symbols), 2*step):
        pair = []
        for offset in (0, step):
            component = symbols[j+offset:j+offset+width]
            need(symbols[j+offset+width] == 2 and all(x in (0, 1) for x in component),
                 "literal signed field and delimiter")
            value = sum(x << bit for bit, x in enumerate(component))
            if component[-1]:
                value -= 1 << width
            pair.append(value)
        values.append(tuple(pair))
    return values


def monomial(values, header, recipe):
    positions = active_positions(header)
    result = [None]*len(values)
    for address, value in enumerate(values):
        column = sum(((address >> bit) & 1) << j for j, bit in enumerate(positions))
        phase = recipe["phase"] + sum(recipe["linear_Z4"][j] for j in range(9) if column >> j & 1)
        phase += 2*sum(1 for j in range(9) for k in range(j+1, 9)
                       if column >> j & 1 and column >> k & 1 and recipe["quadratic_rows"][j] >> k & 1)
        image = recipe["offset"] ^ sum(((row & column).bit_count() % 2) << j
                                       for j, row in enumerate(recipe["matrix_rows"]))
        target = replace_column(address, image, positions)
        need(result[target] is None, "complete bijective right/left reference")
        result[target] = rotate(value, phase)
    return result


def positive(values, header, axis=0, sign=1):
    bit = 1 << active_positions(header)[axis]
    result = []
    for address, value in enumerate(values):
        one = gauss_mul((1, sign), value)
        two = gauss_mul((1, -sign), values[address ^ bit])
        a, b = one[0]+two[0], one[1]+two[1]
        need(a % 2 == b % 2 == 0, "complete pair exact at the common quantum")
        result.append((a//2, b//2))
    return result


def corpus(bad=False):
    columns, matrix = source_matrix()
    header, initial, expected, bad_index = fixture(columns, bad=bad)
    record = source_boundary()[1]
    right = encode(monomial(decode(initial, 2), header, record["right"]), 2)
    if bad:
        values = decode(right, 2)
        need(values[-1] == (0, 0) and sum(value == (0, 0) for value in values) == 1,
             "unique zero at the actual last C-pair position")
        try:
            positive(values, header)
        except ValueError:
            pass
        else:
            raise ValueError("late-child parity countercontrol became exact")
        return header, (initial, right), matrix, bad_index
    middle = encode(positive(decode(right, 2), header), 2)
    final = encode(monomial(decode(middle, 2), header, record["left"]), 2)
    need(final == expected, "complete three-factor reference agrees with original source matrix")
    return header, (initial, right, middle, final), matrix, None


def reference_controls():
    """Discriminate four faults at the new complete composition interface."""
    header, packets, matrix, _bad = corpus()
    record = source_boundary()[1]
    wrong_right = dict(record["right"], phase=(record["right"]["phase"]+1) % 4)
    right_values = decode(packets[1], 2)
    changed_phase = monomial(decode(packets[0], 2), header, wrong_right)
    faults = {
        "wrong_absolute_entrance_phase": encode(monomial(positive(changed_phase, header), header, record["left"]), 2),
        "wrong_middle_direction": encode(monomial(positive(right_values, header, sign=-1), header, record["left"]), 2),
        "wrong_middle_vector": encode(monomial(positive(right_values, header, axis=1), header, record["left"]), 2),
        "omitted_exit": packets[2],
    }
    differences = {name: sum(a != b for a, b in zip(value, packets[3])) for name, value in faults.items()}
    need(all(len(value) == len(packets[3]) and value != packets[3] for value in faults.values()),
         "complete original-circuit oracle rejects each numerical join fault")
    return dict(records=4096, packet_hashes=[sha256(bytes(x)).hexdigest() for x in packets],
                exact_reference_bytes_checked=True, rejected_join_faults=differences,
                physical_execution_claim=False)


def run(which):
    bad = which == "reject"
    header, packets, matrix, bad_index = corpus(bad)
    engine, work, field, context = hardware()
    stage = work[0]
    put(field, packets[0]); put(context, header_bits(header))
    provider = {"entry": engine.entry, "leaf": engine.leaf, "exit": engine.exit, "reject": engine.leaf}[which]
    input_index = {"entry": 0, "leaf": 1, "exit": 2, "reject": 1}[which]
    if which != "entry":
        put(stage, packets[input_index])
    all_tapes = (*work, field, context)
    ancestors = [bytes(t.cells[:t.origin]) for t in all_tapes]
    before = sum(t.actions() for t in all_tapes)
    prefix_cost = 0
    if which == "entry":
        S.abi.transfer(field, stage)
        prefix_cost = sum(t.actions() for t in all_tapes)-before
        need(prefix_cost == 8*len(packets[0])+14, "actual source transfer invoice")
    factor_before = sum(t.actions() for t in all_tapes)
    error = None
    try:
        provider.run(engine.stage, engine.context)
    except S.leaf.linear.CoefficientDomainError as caught:
        error = str(caught)
    factor_actions = sum(t.actions() for t in all_tapes)-factor_before
    need(error == ("inexact Gaussian halving" if bad else None), "exact returned factor outcome")
    expected = packets[input_index] if bad else packets[input_index+1]
    need(body(stage) == expected, "exact complete bytes at the factor return boundary")
    need(body(context) == header_bits(header), "all context bytes preserved")
    need(body(field) == packets[0], "original public word remains protected before commit")
    need(all(t.head == t.origin for t in all_tapes), "all returned local heads")
    need(all(all(x == 6 for x in t.cells[t.origin:]) for t in work[1:]),
         "every complete numerical cohort physically retired")
    need(not provider.pool.live and provider.engine.closed and not provider.engine.pool.live,
         "closed returned numerical provider")
    if which in ("entry", "exit"):
        need(provider.engine.compact.closed, "closed returned Compact provider")
    need(all(bytes(t.cells[:t.origin]) == old for t, old in zip(all_tapes, ancestors)),
         "protected ancestor and origin bytes")
    returned_bytes = bytes(body(stage))
    postfix_before = sum(t.actions() for t in all_tapes)
    if which == "exit":
        engine.commit(); S.abi.retire(stage)
        need(body(field) == packets[3], "actual complete commit to the original-source answer")
    elif bad:
        S.abi.retire(stage)
        need(body(field) == packets[0], "actual stage retirement leaves original failure input intact")
    postfix_cost = sum(t.actions() for t in all_tapes)-postfix_before
    need(postfix_cost == (14*len(packets[0])+21 if which == "exit"
                          else 5*len(packets[0])+7 if bad else 0), "actual final administrative bill")
    if which in ("exit", "reject"):
        need(all(all(x == 6 for x in t.cells[t.origin:]) for t in work), "complete final private erasure")
    return dict(slice=which, records=4096, physical_bits=len(packets[0]),
                input_packet_sha256=sha256(bytes(packets[input_index])).hexdigest(),
                returned_packet_sha256=sha256(returned_bytes).hexdigest(),
                corpus_sha256=[sha256(bytes(bits)).hexdigest() for bits in packets],
                factor_actions=factor_actions, prefix_actions=prefix_cost, postfix_actions=postfix_cost,
                total_actions=sum(t.actions() for t in all_tapes)-before,
                private_role_extents=[len(t.cells)-t.origin for t in work],
                fixed_private_ports=len(work), header_sha256=sha256(bytes(header_bits(header))).hexdigest(),
                bad_initial_index=bad_index, rejection=error, matrix=matrix,
                exact_byte_boundary_checked=True, uninterrupted_run_claim=False)


if __name__ == "__main__":
    ap = ArgumentParser()
    ap.add_argument("slice", choices=("entry", "leaf", "exit", "reject"))
    args = ap.parse_args()
    print(json.dumps(run(args.slice), sort_keys=True))

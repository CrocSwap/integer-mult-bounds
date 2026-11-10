"""Full nine-coordinate packet through an actual selected positive-rank leaf.

Expected values use normalized C eigencharacters, independently of the
retained arithmetic engine. Prepared for @CubeJerry with substantial OpenAI
assistance. Apache-2.0.
"""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from argparse import ArgumentParser
from hashlib import sha256
import json
from all_leaf_sources import HERE, activate, load, need
from check_view import encode as encode_header
from selected_leaf import PaidService
from source_catalog import catalog

S = activate()
HARDWARE = load("ranked_child_physical_hardware", HERE/"vendor/atomic/physical_hardware.py")


def rotate(phase):
    return ((1, 0), (0, 1), (-1, 0), (0, -1))[phase % 4]


def encoded(values):
    bits = []
    for pair in values:
        for value in pair:
            need(-2 <= value <= 1, "reference signed two-bit range")
            for symbol in ((value & 1), ((value >> 1) & 1), 2):
                bits += [(symbol >> shift) & 1 for shift in (2, 1, 0)]
    return bits


def fixture(mode, rank=2):
    need(mode != "cutoff" or rank > 1, "unscaled-width cutoff control needs rank above one")
    header = dict(outer=1, rows=1, stock=1, row_bits=4096*18,
                  within_bits=12, record_bits=18, p=9, d=9, K=1, G=1,
                  H=1, q0=3, qF=0, qB=0, D=9, f=1, rho=0,
                  active_start=2, back_start=11, selected_axes=9,
                  entry_start=2, remainder=0, cutoff=1 if mode == "cutoff" else 9)
    positions = [9-j for j in range(rank)]
    initial, expected, too_short = [], [], []
    for address in range(4096):
        spectator = ((address & 3) | (((address >> 10) & 3) << 2))
        weights = ([((spectator & (j+1)).bit_count() % 2) for j in range(rank)]
                   if rank <= 2 else
                   [int(j == spectator) if spectator < 8 else ((spectator-8) >> (j % 3)) & 1
                    for j in range(rank)])
        sign = sum(weight*((address >> bit) & 1) for weight, bit in zip(weights, positions))
        phase = spectator+2*sign
        initial.append(rotate(phase))
        expected.append(rotate(phase+sum(weights)))
        too_short.append(rotate(phase+weights[0]))
    need(initial != expected and (rank == 1 or expected != too_short),
         "nontrivial full rank child and unscaled-width discriminator")
    if mode == "parity":
        initial[-1] = (0, 0)
    return header, encoded(initial), encoded(expected)


def put(tape, bits):
    tape.cells[tape.origin:] = bytearray(bits)
    tape.head, tape.high = tape.origin, tape.origin+len(bits)


def body(tape):
    values = tape.cells[tape.origin:]
    stop = values.index(6) if 6 in values else len(values)
    need(all(x == 6 for x in values[stop:]), "no hidden nonblank tail")
    return bytes(values[:stop])


def hardware(rank):
    entries = catalog()[1]
    pc = next(pc for pc, triple in entries.items() if triple[1].rank == rank)
    service = PaidService(entries[pc][1])
    work = [HARDWARE.Tape(3+j % 5) for j in range(service.port_count)]
    field, context = HARDWARE.Tape(9), HARDWARE.Tape(11)
    for tape in (*work, field, context):
        for j in range(tape.origin-1):
            tape.cells[j] = j % 2
    service.bind(work, {service.owner:S.common.abi.CodedPort(field)}, S.common.abi.BinaryContextPort(context))
    return service, work, field, context, pc


def run(mode, rank=2):
    service, work, field, context, pc = hardware(rank)
    header, initial, expected = fixture(mode, rank)
    bits = encode_header(header)
    put(field, initial); put(context, bits)
    tapes = (*work, field, context)
    ancestors = [bytes(t.cells[:t.origin]) for t in tapes]
    before = sum(t.actions() for t in tapes)
    error = None
    try:
        service.run()
    except ValueError as caught:
        error = str(caught)
    expected_error = {"success":None, "cutoff":"elementary PAID branch f <= cutoff",
                      "parity":"inexact Gaussian halving"}[mode]
    need(error == expected_error, "actual source child result or precise rejection")
    need(body(field) == bytes(expected if mode == "success" else initial), "complete independent child answer or preserved rejection input")
    need(body(context) == bytes(bits), "complete parent header preserved")
    need(all(t.head == t.origin for t in tapes), "all returned local heads")
    need(all(all(x == 6 for x in t.cells[t.origin:]) for t in work), "all header and leaf work physically retired")
    need(all(bytes(t.cells[:t.origin]) == old for t, old in zip(tapes, ancestors)), "all caller ancestors preserved")
    need(not service.provider.view.active and not service.provider.native.pool.live
         and not service.provider.native.engine.pool.live, "closed child/header scopes")
    return dict(mode=mode, source_event=pc, owner=service.owner, rank=service.rank,
                parent_f=1, child_f=rank, original_cutoff=header["cutoff"],
                records=4096, physical_bits=len(initial), header_bits=len(bits),
                private_ports=len(work), physical_actions=sum(t.actions() for t in tapes)-before,
                endpoint_sha256=sha256(body(field)).hexdigest(), rejection=error,
                private_materialized_extents=[len(t.cells)-t.origin for t in work],
                complete_selected_move_claim=False, ordinary_invocations=0)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("mode", choices=("success", "cutoff", "parity"))
    parser.add_argument("--rank", type=int, choices=range(1, 9), default=2)
    args = parser.parse_args()
    print(json.dumps(run(args.mode, args.rank), sort_keys=True))

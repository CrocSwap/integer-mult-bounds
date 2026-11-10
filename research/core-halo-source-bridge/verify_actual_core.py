"""A complete real small Core call through the exact format/normalizer bridge.

This is the packed two-record boundary, not an execution of the full first-face
geometry. The larger global splice is a separately scoped composition theorem.
"""
import argparse
from fractions import Fraction as Q
import json
from pathlib import Path
import sys
import time
from types import SimpleNamespace
from unittest.mock import patch

from boundary_codec import Codec, Format, BoundCore
from bridge_sources import HERE, core_source, transport_source, load, authenticate


def need(ok, message):
    if not ok:
        raise ValueError(message)


def sigmag(n, bits):
    return str(int(n < 0)) + format(abs(n), f'0{bits-1}b')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    started = time.monotonic()
    source = core_source()
    B = transport_source()
    with source.numerical() as runtime:
        from admitted_context import AdmittedPartition
        from prepared_join import build_numeric, prepare_banks
        reference = runtime.reference.Reference(runtime.raw, 7, 1, 2, 1, 3, 64)
        partition = AdmittedPartition(runtime, reference, 'narrow', 2, 2, 1, ((1,),))
        family = [[partition]]
        # Component radius R=1 on T=2 records has global Euclidean radius <2.
        programs, windows, actions, blocks, plan = build_numeric(
            runtime, family, target=4, initial_radius_bits=1, incoming=12)
        matrix = windows[0][0].H
        need(any(matrix[i][j] for i in range(2) for j in range(2) if i != j),
             'genuine source coupling')
        types = (runtime.global_compiler.Hadamard, runtime.global_compiler.Diagonal)
        print('PREFLIGHT ' + json.dumps(plan, sort_keys=True), flush=True)
    with source.physical() as state:
        from records import Tape
        from cardinal_counts import Count
        from physical_controls import PreparedFull
        from physical_join import CompleteCore
        from check_support import no_decode
        from session import initialize_marker, erase_marker
        from words import BLANK
        import check_composed
        all_tapes = []
        original_init = Tape.__init__
        def tracked(self, *a, **k):
            original_init(self, *a, **k); all_tapes.append(self)
        def meter():
            return tuple(sum(getattr(t.meter, k) for t in all_tapes)
                         for k in ('reads', 'writes', 'moves'))
        with patch.object(Tape, '__init__', tracked):
            prepared = [PreparedFull(program, Tape, Count, types) for program in programs]
            ibank, fbank, keys = prepare_banks(family, windows, actions, blocks, plan)
            print('ALL_ACTUAL_CORE_SOURCE_PORTS_PREPARED', flush=True)
            root, visits = check_composed.fixture('standard', False)
            owner = CompleteCore(root, dense_leaf_bits=64)
            up = tuple(Count.literal(x) for x in (1, 2, 1, 1, plan['width'], plan['P']))
            fmt = Format(14, 12, plan['width'], plan['P'], 1)
            codec = Codec(B, Tape, BLANK, initialize_marker, erase_marker, fmt)
            values = ((513, -257), (-123, 63))
            contents = ''.join(''.join(sigmag(x, fmt.external_bits) for x in row) + '#'
                               for row in values)
            holder = SimpleNamespace(source=B.Tape('isolated admitted packed source', contents), phase='saved')
            bound = BoundCore(codec, owner, (prepared[0].code, prepared[1].code,
                ibank, fbank, keys, prepared[0].parameters, prepared[1].parameters, up))
            from fixture_tools import snapshot
            ports = (prepared[0].code, prepared[1].code, ibank, fbank, keys,
                     *(x.tape for x in (*prepared[0].parameters, *prepared[1].parameters, *up)))
            saved = snapshot(ports)
            folded = load('bridge_actual_certified_floors', source.COHORT / 'fixture_tools.py')
            bases = {1, *(p.data_width for p in programs),
                     *(p.data_width + 1 for p in programs), *(p.data_width + 2 for p in programs)}
            before = meter()
            with folded.certified_floors(bases) as (table, calls, misses):
                with no_decode():
                    bound.run(holder)
                need(not misses, 'declared finite metadata specialization')
            used = tuple(a-b for a,b in zip(meter(), before))
            need(snapshot(ports) == saved, 'borrowed actual source/control ports restored')
            need(holder.phase == 'core' and not owner.pending and not codec.pending,
                 'complete protected source return and bridge commit')
            output = []
            for row in holder.source.inspect().split('#')[:-1]:
                pair = []
                for part in (row[:fmt.external_bits], row[fmt.external_bits:]):
                    mag = int(part[1:], 2)
                    need(part[0] == '0' or mag != 0, 'canonical output zero')
                    pair.append(-mag if part[0] == '1' else mag)
                output.append(pair)
            # Original rational 2x2 inverse, independent of every Schur builder,
            # source interpreter and rounded numerical implementation.
            a,b = matrix[0]; c,d = matrix[1]; determinant = a*d-b*c
            inverse = ((d/determinant, -b/determinant), (-c/determinant, a/determinant))
            exact = [[sum(inverse[i][j] * Q(values[j][part], 1 << 12) for j in range(2))/2
                      for part in range(2)] for i in range(2)]
            error = max(sum(abs(Q(output[i][part], 1 << 12)-exact[i][part]) for part in range(2))
                        for i in range(2))
            allowance = Q(1, 1 << 5) + Q(1, 1 << 11)
            need(error <= allowance, 'actual Core normalized source endpoint')
            need(all(t.inspect() == '' for t in codec.work) and all(x == BLANK for x in codec.input.cells),
                 'all bridge-owned payload backing blank')
            owner.idle()
            receipt = {'status': 'PASS_ACTUAL_CORE_SOURCE_BRIDGE',
                'scope': 'actual packed K1 g1 L2 Core and physical code/grid/normalizer bridge; not full first-face geometry',
                'complete_native_calls': 3, 'complete_dense_events': 2*programs[0].stages+programs[1].stages,
                'complete_sparse_calls': [owner.inverse.child.calls, owner.forward.child.calls],
                'source': {'spec': list(reference.spec.__dict__.values()), 'origin': 2,
                           'reference_sha256': reference.description_hash, 'matrix': [[str(x) for x in row] for row in matrix]},
                'format': fmt.__dict__, 'core_plan': plan, 'input': values, 'output': output,
                'exact_component_error': str(error), 'proved_bridge_allowance': str(allowance),
                'native_online_reads_writes_moves': used,
                'native_constructed_retained_cells': sum(len(t.cells) for t in all_tapes),
                'bridge_external_primitive_actions': sum(sum(t.actions[k] for k in ('read','write','move'))
                    for t in (*codec.templates,*codec.work)),
                'bridge_external_retained_cells': sum(t.bill()['retained_cells'] for t in (*codec.templates,*codec.work)),
                'same_source_ports_restored': True, 'bridge_owned_payload_blank': True,
                'native_fixture': 'retained q2 root with certified finite floor metadata specialization',
                'seconds': time.monotonic()-started, 'no_new_kappa': True,
                'publication': 'frozen public Core source bytes authenticated; source admissions remain conditional',
                'public_core_commit': authenticate()['core_public_commit']}
            Path(args.output).write_text(json.dumps(receipt, sort_keys=True, indent=2)+'\n')
            print('PASS_ACTUAL_CORE_SOURCE_BRIDGE', flush=True)
            print(json.dumps(receipt, sort_keys=True), flush=True)
            for p in prepared: p.close()
            for x in up: x.close()
            for t in (ibank,fbank,keys):t.clear();erase_marker(t)


if __name__ == '__main__':
    main()

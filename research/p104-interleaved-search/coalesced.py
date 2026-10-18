#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact recharting of the finite 31-helper fanout word.

The scalar operations and all public boundary frames are fixed. A sparse list
changes common scalar charts; eight private COPY paths keep their original Hb
sources and La seed frames. Every public transport is derived afresh from the
resulting chronological word. No optimizer or numerical solver is trusted.
This finite forward certificate alone is not a multiplication supplier or an
exponent improvement; native lowering and complete hosting are separate bills.
"""
from collections import Counter
from fractions import Fraction as Q
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location('p104_fanout', HERE / 'fanout.py')
F = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(F)
D, QC, S = F.D, F.QC, F.S
FRAMES_SHA256 = '5e3d129ec88b23173f75c3d7187c78e96676f43ef1606166f4eadf888adb7a69'


def construct(fault=None, baseline=None):
    """Replay the unchanged scalar word with the proposed exact common charts."""
    base = F.construct() if baseline is None else baseline
    raw = (HERE / 'COALESCED-FRAMES.json').read_bytes()
    D.require(hashlib.sha256(raw).hexdigest() == FRAMES_SHA256, 'coalesced frame input pin')
    data = json.loads(raw)
    original = base['scalar_operations']
    D.require(F.digest(original) == data['source_scalar_operations_sha256'], 'source scalar word pin')
    assignments = {}
    for entry in data['changes']:
        k, vectors = entry['event'], entry['frame']
        D.require(type(k) is int and 0 <= k < len(original), 'changed event index')
        D.require(k not in assignments, 'duplicate changed event')
        e = original[k]
        D.require(e['kind'] in ('add', 'scale', 'private_copy'), 'changed nonscalar event')
        frame = QC.span(vectors)
        D.require(F.basis(frame) == vectors, 'noncanonical changed frame')
        D.require(frame != QC.span(e['frame']), 'redundant unchanged frame')
        assignments[k] = frame
    word = QC.load_inputs()['word']
    n = base['report']['public_registers']
    oldn = 2 * word['v'] + word['R']
    live = [i for i in range(word['v']) if i not in QC.REMOVED]
    initial = [QC.span(word['frames'][i]) for i in word['start']] + [F.ZERO] * (n-oldn)
    for r in QC.REMOVED:
        initial[r] = F.ZERO
    current, rows = list(initial), QC.identity(n)
    private_frames, private_rows = {}, {}
    old_edges = {e['occurrence']:e for e in base['transport_edges']}
    paid, copy_paid, edges, operations, paths = Counter(), Counter(), [], [], []
    active_path = None
    peak, created = 0, 0
    mutated_frame = mutated_coefficient = False

    def transport(r, target, phase, private=False):
        old = private_frames[r] if private else current[r]
        D.require(target <= old if private else old <= target, 'nonmonotone recharted transport')
        rank = abs(D.dimension(target)-D.dimension(old))
        if rank:
            edge = dict(occurrence=len(edges), register=r, source_frame=F.basis(old),
                        target_frame=F.basis(target), rank=rank, private=private, phase=phase)
            edges.append(edge)
            operations.append(dict(kind='transport', occurrence=edge['occurrence'], phase=phase))
            (copy_paid if private else paid)[rank] += 1
            if private:
                D.require(active_path is not None, 'private transport outside lifetime')
                active_path.append(edge)
        if private:
            private_frames[r] = target
        else:
            current[r] = target

    for k, old_event in enumerate(original):
        e = dict(old_event)
        kind, phase = e['kind'], e['phase']
        if kind == 'transport':
            old = old_edges[e['occurrence']]
            if old['private']:
                r = old['register']
                D.require(private_frames.get(r) == QC.span(old['source_frame']), 'private source frame changed')
                transport(r, QC.span(old['target_frame']), phase, True)
            continue
        if kind == 'private_init':
            r = e['register']
            D.require(r >= n and r not in private_frames, 'private lifetime initialization')
            private_frames[r], private_rows[r] = QC.span(e['frame']), {}
            created += 1
            peak = max(peak, len(private_frames))
            D.require(active_path is None, 'overlapping private paths')
            active_path = []
        elif kind == 'private_discard':
            r = e['register']
            D.require(private_frames.get(r) == QC.span(e['frame']), 'private discard frame changed')
            paths.append(active_path)
            active_path = None
            del private_frames[r], private_rows[r]
        elif kind in ('add', 'scale', 'private_copy'):
            rr = e['registers']
            frame = assignments.get(k, QC.span(e['frame']))
            if fault == 'seed_frame' and phase == 'fanout helper seed' and not mutated_frame:
                frame, mutated_frame = F.FULL, True
            if fault == 'contact_coefficient' and phase == 'fanout contact' and not mutated_coefficient:
                e['coefficient'] = str(Q(e['coefficient']) + 1)
                mutated_coefficient = True
            for r in rr:
                if r < n:
                    transport(r, frame, phase)
                else:
                    D.require(private_frames.get(r) == frame, 'private source or seed common chart changed')
            D.require(all((current[r] if r < n else private_frames[r]) == frame for r in rr),
                      'scalar operands have different charts')
            e['frame'] = F.basis(frame)
            coefficient = Q(e['coefficient'])
            target = rows[rr[0]] if rr[0] < n else private_rows[rr[0]]
            if kind == 'scale':
                D.require(bool(coefficient), 'singular scalar scale')
                scaled = {i:coefficient*x for i,x in target.items()}
                if rr[0] < n:
                    rows[rr[0]] = scaled
                else:
                    private_rows[rr[0]] = scaled
            else:
                source = rows[rr[1]] if rr[1] < n else private_rows[rr[1]]
                if kind == 'private_copy':
                    D.require(rr[0] >= n and not target, 'COPY destination is not cleared private state')
                    private_rows[rr[0]] = {i:coefficient*x for i,x in source.items()}
                else:
                    S.add_row(target, source, coefficient)
        else:
            raise D.VerificationError('unknown scalar event: '+kind)
        operations.append(e)
    for r, target in enumerate(base['final']):
        transport(r, target, 'final public boundary')
    D.require(not private_frames and not private_rows and active_path is None, 'private lifetime remains live')
    D.require(not S.endpoint_failures(rows, word['v'], live), 'full 735-column endpoint identity failed')
    D.require(created == 8 and peak == 1 and copy_paid == Counter({7:8}), 'private copy contract changed')
    D.require(current == base['final'], 'public endpoint frames changed')
    D.require(sum(k*v for k,v in paid.items()) == base['report']['public_rank_mass'], 'public boundary mass changed')
    D.require(D.profile(paid) == data['expected_public_profile'], 'recorded coalesced profile changed')
    D.require(Counter(e['rank'] for e in edges if not e['private']) == paid, 'transport occurrence recount')
    report = dict(schema='p104-coalesced-forward-report-v1',
                  scope='Finite exact 735-column forward word; complete native, hosting and exponent admission are separate.',
                  source_scalar_operations_sha256=data['source_scalar_operations_sha256'],
                  frame_changes_sha256=FRAMES_SHA256, changed_scalar_frames=len(assignments),
                  scalar_coefficients_and_order_unchanged=True, public_boundary_frames_unchanged=True,
                  candidate_public_profile=D.profile(paid), private_COPY_profile=D.profile(copy_paid),
                  public_rank_mass=sum(k*v for k,v in paid.items()),
                  ordinary_fanout_helpers=n-oldn, public_registers=n, live_ports=len(live),
                  private_copies_created=created, peak_private_copies=peak,
                  full_735_column_identity_verified=True, all_public_scalar_adds_common_chart=True,
                  actual_query_Hb_frames_verified=True, helper_La_seed_frames_verified=True,
                  complete_public_widths=base['report']['complete_public_widths'],
                  native_phase_compilation_verified=False, global_hosting_verified=False,
                  completed_full_multiplication_supplier=False, kappa_improvement_claimed=False,
                  scalar_operation_word_sha256=F.digest(operations), transport_occurrences_sha256=F.digest(edges))
    return dict(report=report, scalar_operations=operations, transport_edges=edges,
                private_paths=paths, final=current, initial=initial, ports=base['ports'])


def native_witness(built=None):
    built = construct() if built is None else built
    edges = [dict(register=str(e['register']), old=e['source_frame'], new=e['target_frame'],
                  occurrence=e['occurrence'], private=e['private'], rank=e['rank']) for e in built['transport_edges']]
    lookup = {e['occurrence']:e for e in edges}
    return dict(transports=edges,
                private_paths=[[lookup[e['occurrence']] for e in path] for path in built['private_paths']],
                scalar_operations=built['scalar_operations'], ports=built['ports'],
                scalar_operation_word_sha256=built['report']['scalar_operation_word_sha256'],
                transport_occurrences_sha256=built['report']['transport_occurrences_sha256'],
                public_profile=built['report']['candidate_public_profile'], private_profile=built['report']['private_COPY_profile'])


def verify():
    baseline = F.construct()
    built = construct(baseline=baseline)
    controls = {}
    for fault in ('seed_frame', 'contact_coefficient'):
        try:
            construct(fault=fault, baseline=baseline)
        except ValueError as error:
            controls[fault] = str(error)
        else:
            raise D.VerificationError('coalesced negative control accepted: '+fault)
    built['report']['negative_controls'] = controls
    return built['report']


if __name__ == '__main__':
    print(json.dumps(verify(), indent=2, sort_keys=True))

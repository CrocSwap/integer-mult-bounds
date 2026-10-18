#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Compose credited private descent reuse with the actual coalesced scalar word.

The exact replayer follows David Arias's PR2152 coalesced.py. The helper-7
reuse mechanism is Cinna Davis's PR2219. This adapter consumes the already
coalesced events, keeps their explicit source indices, and retains every public
boundary by charging the now-unused helper's ZERO -> FULL rank-nine transport.
"""
from collections import Counter
from fractions import Fraction as Q

HELPER, OWNED, SOURCE = 711, 738, 133
TARGETS = (159, 203, 148)


def construct(C, baseline=None, fault=None):
    F, D, QC, S = C.F, C.D, C.QC, C.S
    require = D.require
    base = C.construct() if baseline is None else baseline
    original = base['scalar_operations']
    word = QC.load_inputs()['word']
    n = base['report']['public_registers']
    require(n == 735, 'expected 735 independent public inputs')
    require(F.digest(original) == base['report']['scalar_operation_word_sha256'],
            'coalesced source event binding')
    removed = {k: e for k, e in enumerate(original)
               if HELPER in e.get('registers', [])}
    require(Counter(e['phase'] for e in removed.values()) ==
            Counter({'entry compensation': 7, 'fanout helper seed': 1,
                     'fanout contact': 3, 'helper restoration': 1}),
            'helper event inventory changed')
    seed = next(e for e in removed.values() if e['phase'] == 'fanout helper seed')
    require(seed['registers'] == [HELPER, OWNED] and seed['coefficient'] == '1',
            'helper seed does not use the selected owned query')
    contacts = {e['registers'][0]: (k, e) for k, e in removed.items()
                if e['phase'] == 'fanout contact'}
    require(set(contacts) == set(TARGETS), 'three reused targets')
    copy = [e for e in original if e['kind'] == 'private_copy'
            and e['registers'][0] == OWNED]
    scale = [e for e in original if e['kind'] == 'scale'
             and e['registers'][0] == OWNED]
    require(len(copy) == len(scale) == 1 and copy[0]['registers'] == [OWNED, SOURCE]
            and copy[0]['coefficient'] == '1' and scale[0]['coefficient'] == '-1/2',
            'actual source133 query and scaling')
    chain = [QC.span(copy[0]['frame'])] + [QC.span(contacts[r][1]['frame']) for r in TARGETS]
    chain.append(QC.span(seed['frame']))
    require([D.dimension(f) for f in chain] == [8, 7, 6, 3, 1]
            and all(b < a for a, b in zip(chain, chain[1:])),
            'actual coalesced contact frames do not form the required descent')

    initial = list(base['initial'])
    current, rows = list(initial), QC.identity(n)
    private_frames, private_rows = {}, {}
    old_edges = {e['occurrence']: e for e in base['transport_edges']}
    paid, copy_paid = Counter(), Counter()
    edges, operations, paths, origins = [], [], [], []
    active_path = None
    peak = created = replaced = 0
    retained_dirty = False

    def transport(r, target, phase, private=False):
        old = private_frames[r] if private else current[r]
        require(target <= old if private else old <= target,
                'nonmonotone composed transport')
        rank = abs(D.dimension(target) - D.dimension(old))
        if rank:
            edge = dict(occurrence=len(edges), register=r, source_frame=F.basis(old),
                        target_frame=F.basis(target), rank=rank, private=private, phase=phase)
            edges.append(edge)
            operations.append(dict(kind='transport', occurrence=edge['occurrence'], phase=phase))
            origins.append(None)
            (copy_paid if private else paid)[rank] += 1
            if private:
                require(active_path is not None, 'private transport outside lifetime')
                active_path.append(edge)
        if private:
            private_frames[r] = target
        else:
            current[r] = target

    def scalar(e, origin):
        rr, frame = e['registers'], QC.span(e['frame'])
        for r in rr:
            if r < n:
                transport(r, frame, e['phase'])
            else:
                require(private_frames.get(r) == frame, 'private scalar common chart')
        require(all((current[r] if r < n else private_frames[r]) == frame for r in rr),
                'scalar common chart')
        coefficient = Q(e['coefficient'])
        target = rows[rr[0]] if rr[0] < n else private_rows[rr[0]]
        if e['kind'] == 'scale':
            require(bool(coefficient), 'singular scalar scale')
            scaled = {i: coefficient * x for i, x in target.items()}
            if rr[0] < n:
                rows[rr[0]] = scaled
            else:
                private_rows[rr[0]] = scaled
        else:
            source = rows[rr[1]] if rr[1] < n else private_rows[rr[1]]
            if e['kind'] == 'private_copy':
                require(rr[0] >= n and not target, 'COPY destination is not cleared')
                private_rows[rr[0]] = {i: coefficient * x for i, x in source.items()}
            else:
                require(e['kind'] == 'add', 'unknown scalar operation')
                S.add_row(target, source, coefficient)
        operations.append(e)
        origins.append(origin)

    for k, old_event in enumerate(original):
        e = dict(old_event)
        kind, phase = e['kind'], e['phase']
        if k in removed:
            if fault == 'retain_dirty_compensation' and phase == 'entry compensation' and not retained_dirty:
                retained_dirty = True
            else:
                continue
        if kind == 'transport':
            old = old_edges[e['occurrence']]
            if not old['private']:
                continue
            r = old['register']
            require(private_frames.get(r) == QC.span(old['source_frame']), 'private source changed')
            if r == OWNED:
                replaced += 1
                for target in TARGETS:
                    source_index, contact = contacts[target]
                    frame = QC.span(contact['frame'])
                    if fault == 'ascending_private_contact' and target == TARGETS[0]:
                        frame = F.FULL
                    transport(r, frame, 'owned query to reused contact', True)
                    event = dict(kind='add', registers=[target, r],
                                 coefficient=contact['coefficient'], frame=F.basis(frame),
                                 phase='private query replaces helper contact')
                    if fault == 'wrong_contact_coefficient' and target == TARGETS[0]:
                        event['coefficient'] = str(Q(event['coefficient']) + 1)
                    if fault != 'missing_reused_contact' or target != TARGETS[0]:
                        scalar(event, {'replacement_for': source_index})
                transport(r, QC.span(old['target_frame']), 'owned query to La after contacts', True)
            else:
                transport(r, QC.span(old['target_frame']), phase, True)
            continue
        if kind == 'private_init':
            r = e['register']
            require(r >= n and r not in private_frames and active_path is None,
                    'overlapping or invalid private initialization')
            private_frames[r], private_rows[r] = QC.span(e['frame']), {}
            created += 1
            peak = max(peak, len(private_frames))
            active_path = []
        elif kind == 'private_discard':
            r = e['register']
            require(private_frames.get(r) == QC.span(e['frame']), 'private discard frame')
            paths.append(active_path)
            active_path = None
            del private_frames[r], private_rows[r]
        elif kind in ('add', 'scale', 'private_copy'):
            scalar(e, k)
            continue
        else:
            raise ValueError('unknown source event: ' + kind)
        operations.append(e)
        origins.append(k)
    # Unlike PR2219's retired-helper contract, retain every public boundary.
    for r, target in enumerate(base['final']):
        transport(r, target, 'final public boundary')
    require(not private_frames and not private_rows and active_path is None, 'private state remains')
    live = [i for i in range(word['v']) if i not in QC.REMOVED]
    require(not S.endpoint_failures(rows, word['v'], live), 'full 735-column endpoint identity failed')
    require(replaced == 1 and created == 8 and peak == 1, 'owned lifetime inventory')
    require(current == base['final'], 'public boundary frames changed')
    expected_private = Counter({1: 2, 2: 1, 3: 1, 7: 7})
    require(copy_paid == expected_private, 'private path invoice')
    widths = [D.dimension(b) - D.dimension(a) for a, b in zip(initial, current)]
    require(widths == base['report']['complete_public_widths'], 'public lifetime widths changed')
    require(sum(widths) == sum(r*c for r, c in paid.items()) == 5838, 'public mass')
    baseline_paid = Counter({int(k): v for k, v in base['report']['candidate_public_profile'].items()})
    expected_public = baseline_paid.copy()
    expected_public.update({1: -2, 2: -2, 3: -1, 9: 1})
    require(paid == expected_public, 'unexpected extra public transport charge')
    require(len(operations) == len(origins), 'source index map length')
    retained = [origin for origin in origins if type(origin) is int]
    wanted = [k for k, e in enumerate(original) if k not in removed and e['kind'] != 'transport']
    require(retained == wanted, 'retained coalesced scalar order changed')
    for e, origin in zip(operations, origins):
        if type(origin) is int:
            require(e == original[origin], 'retained scalar event changed')
    adds = Counter(e['phase'] for e in operations if e['kind'] == 'add')
    old_adds = sum(e['kind'] == 'add' for e in original)
    require(old_adds - sum(adds.values()) == 9, 'scalar ADD reduction')
    endpoint = [[[i, str(x)] for i, x in sorted(row.items())] for row in rows]
    report = dict(schema='p104-coalesced-private-reuse-v1',
                  full_735_column_identity_verified=True,
                  all_retained_scalar_events_and_charts_source_bound=True,
                  source_scalar_operations_sha256=F.digest(original),
                  original_fanout_operations_sha256=base['report']['source_scalar_operations_sha256'],
                  frame_changes_sha256=base['report']['frame_changes_sha256'],
                  public_boundary_frames_unchanged=True, complete_public_widths=widths,
                  public_registers=n, ordinary_fanout_helpers=31, live_ports=len(live),
                  candidate_public_profile=D.profile(paid), private_COPY_profile=D.profile(copy_paid),
                  combined_profile=D.profile(paid + copy_paid), public_rank_mass=5838,
                  private_rank_mass=sum(r*c for r, c in copy_paid.items()),
                  private_copies_created=created, peak_private_copies=peak,
                  private_path_ranks=[[e['rank'] for e in path] for path in paths],
                  unused_helper_boundary_transport=[e for e in edges if e['register'] == HELPER],
                  scalar_adds_by_phase=dict(sorted(adds.items())), scalar_add_count=sum(adds.values()),
                  baseline_scalar_add_count=old_adds, removed_source_events=list(removed),
                  replacements=[dict(source_event=contacts[r][0], target=r,
                                     frame=contacts[r][1]['frame'], coefficient=contacts[r][1]['coefficient'])
                                for r in TARGETS],
                  scalar_origin_map_sha256=F.digest(origins), endpoint_rows_sha256=F.digest(endpoint),
                  scalar_operation_word_sha256=F.digest(operations), transport_occurrences_sha256=F.digest(edges),
                  completed_full_multiplication_supplier=False, kappa_improvement_claimed=False)
    return dict(report=report, scalar_operations=operations, transport_edges=edges,
                private_paths=paths, initial=initial, final=current, ports=base['ports'], origins=origins)

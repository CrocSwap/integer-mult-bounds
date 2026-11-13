#!/usr/bin/env python3
"""Independent exact replay of the #7481 earlier-destination history filter.

Unlike worker-b/history-cache/filter.py, this verifier directly replays every
latent row and uses its own canonical GF(2) frame quotient and low-pivot exact
Q echelon. Historical generators are only public entrances and MOVE arrivals;
all scalar contacts and exact row updates are replayed, with history-span
preservation for coframed ADD/COPY/SCALE proved by linearity.
"""
from collections import Counter
from fractions import Fraction
from pathlib import Path
import gzip
import hashlib
import json
import time

ROOT = Path(__file__).resolve().parent
HERE = ROOT
WORD = ROOT / 'inputs/WORD.json.gz'
WORD_SHA256 = 'acee323696b18914bd863d55341f92112b48d3d1dc1443c276efb6c396fcc0a9'


def require(condition, label):
    if not condition:
        raise AssertionError(label)


def frame_key(vectors):
    """Canonical RREF key for the span of integer bit-vectors over GF(2)."""
    basis = {}
    for raw in vectors:
        v = raw
        for p in sorted(basis, reverse=True):
            if (v >> p) & 1:
                v ^= basis[p]
        if v:
            p = v.bit_length() - 1
            for q in list(basis):
                if (basis[q] >> p) & 1:
                    basis[q] ^= v
            basis[p] = v
    return tuple((p, basis[p]) for p in sorted(basis, reverse=True))


def row_add(dst, src, q):
    require(dst is not src, 'aliasing row update')
    for i, x in src.items():
        y = dst.get(i, Fraction(0)) + q * x
        if y:
            dst[i] = y
        else:
            dst.pop(i, None)


def row_scale(row, q):
    if not q:
        row.clear()
    elif q != 1:
        for i in list(row):
            row[i] *= q
            if not row[i]:
                del row[i]


def reduced(row, basis):
    value = row.copy()
    while value:
        p = min(value)
        b = basis.get(p)
        if b is None:
            return value
        row_add(value, b, -value[p])
    return value


def insert(basis, row):
    value = reduced(row, basis)
    if not value:
        return False
    p = min(value)
    scale = 1 / value[p]
    row_scale(value, scale)
    basis[p] = value
    return True


def member(basis, row):
    return not reduced(row, basis)


def run(source=WORD, kr=None):
    started = time.monotonic()
    src = source.read_bytes()
    require(hashlib.sha256(src).hexdigest() == WORD_SHA256, 'native word hash')
    w = json.loads(gzip.decompress(src))
    require(kr is not None, 'in-memory exact source census supplied')
    require(kr['source_sha256'] == WORD_SHA256, 'candidate source binding')
    require(kr['status'] == 'COMPLETE_EXACT_GLOBAL_KERNEL_RELOCATION_CENSUS',
            'complete source-span census')

    frames = [frame_key(f) for f in w['frames']]
    candidate = {r['event']: r for r in kr['records'] if r['source']['inside']}
    require(len(kr['records']) == 6279, 'all MOVE cuts in source census')
    source_counts = Counter((bool(r['owned']), bool(r['source']['inside']))
                            for r in kr['records'])
    require(source_counts == Counter({(False, False): 6214,
                                      (False, True): 18,
                                      (True, False): 16,
                                      (True, True): 31}),
            'complete public/owned source-bank split')
    require(len(candidate) == 49, 'all source-span survivors')
    require(Counter(bool(r['owned']) for r in candidate.values()) ==
            Counter({False: 18, True: 31}), 'public/owned candidate split')
    require(Counter(r['rank'] for r in candidate.values()) ==
            Counter({1: 21, 2: 12, 3: 5, 4: 9, 5: 2}), 'candidate ranks')
    stable_candidates = [dict(event=r['event'], owner=r['owner'], owned=r['owned'],
                              rank=r['rank'], witness=r['source']['witness'])
                         for r in kr['records'] if r['source']['inside']]
    census_sha = hashlib.sha256(json.dumps(stable_candidates, sort_keys=True,
                                            separators=(',', ':')).encode()).hexdigest()

    targets = {frames[w['program'][i][3]] for i in candidate}
    histories = {f: {} for f in targets}
    hist_rank_total = 0
    initial_added = 0
    arrivals = Counter()
    event_counts = Counter()
    scalar_preservation_cases = Counter()
    leave_checks = 0
    positive_controls = set()
    records = []
    rows = [{i: Fraction(1)} for i in range(w['public'])]
    rows.extend({} for _ in range(w['owned_fields']))
    charts = w['initial'] + [None] * w['owned_fields']

    # History starts with every public row initially present at a target chart.
    for owner, frame in enumerate(w['initial']):
        key = frames[frame]
        if key in histories:
            initial_added += insert(histories[key], rows[owner])

    for event, e in enumerate(w['program']):
        op, a = e[:2]
        event_counts[op] += 1
        if op == 'MOVE':
            old, new = e[2], e[3]
            require(charts[a] == old, f'MOVE source chart at {event}')
            old_key, new_key = frames[old], frames[new]
            # Before moving away, the value belongs to the full earlier history
            # of its current target chart.  The incoming row at the destination
            # is deliberately not admitted until after a candidate check.
            if event in candidate and old_key in histories and rows[a]:
                require(member(histories[old_key], rows[a]),
                        f'candidate pre-MOVE history inclusion at {event}')
                leave_checks += 1
            if event in candidate:
                rec = candidate[event]
                require(len(e) == 5 and bool(e[4]) == bool(rec['owned']),
                        f'candidate operation / ownership at {event}')
                # Independently reconstruct source-span membership from the
                # recorded exact coefficients and the directly replayed rows.
                witness = {}
                for field, coeff in rec['source']['witness'].items():
                    row_add(witness, rows[int(field)], Fraction(coeff))
                require(witness == rows[a], f'exact source witness at {event}')
                dst_key = frames[new]
                hist = histories[dst_key]
                pre_rank = len(hist)
                hit = member(hist, rows[a])
                # Failure control: in a clone, inserting the alleged missing
                # target must create a member; already-historical basis rows
                # must also be recognized as members.
                if dst_key not in positive_controls:
                    require(member(hist, {}) and
                            (not hist or member(hist, hist[min(hist)])),
                            f'positive membership control at {event}')
                    positive_controls.add(dst_key)
                if not hit:
                    trial = {p: r.copy() for p, r in hist.items()}
                    require(insert(trial, rows[a]), f'negative control rank at {event}')
                    require(member(trial, rows[a]), f'negative control hit at {event}')
                records.append(dict(event=event, owner=a, owned=bool(e[4]),
                                    rank=rec['rank'], destination=new,
                                    destination_history_rank=pre_rank,
                                    member_before_arrival=hit))
            charts[a] = new
            if new_key in histories and rows[a]:
                arrivals[new_key] += 1
                if insert(histories[new_key], rows[a]):
                    hist_rank_total += 1
        elif op == 'INIT':
            require(charts[a] is None and not rows[a], f'INIT zero/fresh at {event}')
            charts[a] = e[2]
        elif op == 'CLEAR':
            require(charts[a] == e[2], f'CLEAR chart at {event}')
            charts[a] = None
            rows[a] = {}
        elif op == 'SCALE':
            require(charts[a] == e[-1], f'SCALE chart at {event}')
            q = Fraction(e[2])
            require(q != 0, f'nonzero SCALE at {event}')
            row_scale(rows[a], q)
            key = frames[charts[a]]
            if key in histories:
                scalar_preservation_cases['SCALE'] += 1
        elif op in ('ADD', 'COPY'):
            b = e[2]
            require(charts[a] == charts[b] == e[-1], f'{op} coframe at {event}')
            if op == 'COPY':
                require(not rows[a], f'COPY zero destination at {event}')
            key = frames[charts[a]]
            row_add(rows[a], rows[b], Fraction(e[3]))
            if key in histories:
                scalar_preservation_cases[op] += 1
        else:
            raise AssertionError(f'unknown instruction {op}')

    require(len(records) == 49, 'all candidate checks reached')
    require(not any(r['member_before_arrival'] for r in records),
            'no destination-history membership hits')
    require(charts == w['final'] + [None] * w['owned_fields'],
            'all final charts and owned lifetimes')
    require(sum(len(b) for b in histories.values()) ==
            initial_added + hist_rank_total, 'history rank accounting')
    expected_history_rank = 1465
    observed_rank = sum(map(len, histories.values()))
    require(observed_rank == expected_history_rank,
            'independent exact cumulative generator count')
    require(len(histories) == 40, '40 destination subspaces')
    require(sum(arrivals.values()) > 0 and leave_checks > 0,
            'chronological arrival and departure coverage')

    result = dict(
        status='INDEPENDENT_EXACT_EARLIER_DESTINATION_HISTORY_REPLAY',
        source_sha256=WORD_SHA256,
        source_census_sha256=census_sha,
        native_events=len(w['program']),
        native_MOVE_events=event_counts['MOVE'],
        source_span_survivors=len(candidate),
        public_candidates=18,
        owned_candidates=31,
        source_prefilter_counts=dict(public_misses=source_counts[(False, False)],
                                     public_survivors=source_counts[(False, True)],
                                     owned_misses=source_counts[(True, False)],
                                     owned_survivors=source_counts[(True, True)]),
        candidate_rank_histogram={str(k): v for k, v in sorted(Counter(r['rank'] for r in candidate.values()).items())},
        coframed_destination_subspaces=len(histories),
        duplicate_frame_ids=len(w['frames']) - len(set(frames)),
        initial_public_rows_inserted=initial_added,
        nonzero_MOVE_arrivals_to_target_subspaces=sum(arrivals.values()),
        independent_history_generators=observed_rank,
        coframed_scalar_events_using_target_history=dict(scalar_preservation_cases),
        MOVE_outgoing_live_row_history_checks=leave_checks,
        candidate_history_hits=sum(r['member_before_arrival'] for r in records),
        all_49_exact_source_witnesses_reconstructed=True,
        failure_control='For every nonmember candidate, adding its target to a cloned history basis raises rank and makes it a member; existing basis rows test positive membership.',
        records=records,
        seconds=round(time.monotonic() - started, 3),
        scope='Fixed #7481 source and unchanged complete scalar history at the destination coframe. Does not cover imported stock, modified prior histories, changed later repair, or a physical multi-chart cache.',
    )
    return result

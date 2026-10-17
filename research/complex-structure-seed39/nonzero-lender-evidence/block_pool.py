#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Tekalign (@tekuuu), with substantial OpenAI Codex assistance.
"""Bound the unused nonzero-entrance lender pool for four blocked low blocks.

Checks four handoff times in each of four baselines, including the optimistic
deletion of all16 low prefixes. This is a pool bound for a fixed mechanism,
not an impossibility claim for other circuits or restoration geometries.
"""
import argparse
import hashlib
import json
from pathlib import Path
import census as c

HERE = Path(__file__).resolve().parent
BASES = [632, 640, 648, 656]
LOWS = [b + j for b in BASES for j in [0, 1, 2, 4]]
EXPECTED = [33, 49, 55, 68, 74, 80, 83, 85, 88, 98, 101]
ORIENTED_PAIRS = [(33, 49), (55, 101), (74, 83), (88, 80), (85, 98)]


def run_case(name, tag, baseline):
    w = c.read(c.VENDOR / 'inputs' / f'{name}.canonical.json.gz')
    blocks = c.read(c.VENDOR / 'inputs/blocks.json')['sources'][0]['blocks']
    full = c.read(c.VENDOR / 'witness' / f'witness_80_{tag}.json')
    inv = c.subset_witness(full, set() if baseline == 'high48' else
                           {p['register'] for p in full['pairs'] if p['low']})
    deferred, skip = c.deferred_sets(w, blocks)
    additions, first_frames = [], {}
    for L in LOWS:
        block = next(b for b in blocks if L in b['helpers'])
        plan, error = c.prefix_plan(w, block, L, skip)
        assert plan is not None, error
        additions.append(dict(register=L, low=True, **plan))
        _, f = c.first_frame(w, block['first_input'], L, deferred, skip,
                             set(plan['deleted_prefix_indices']),
                             {int(i): g for i, g in plan['early_prefix_rewrites'].items()})
        assert len(w['frames'][f]) in (4, 5)
        first_frames[str(L)] = w['frames'][f]
    optimistic = dict(inv, pairs=inv['pairs'] + additions)
    schedules = {'baseline': list(c.actual_events(w, blocks, inv)),
                 'all16_prefixes_deleted': list(c.actual_events(w, blocks, optimistic))}
    used = {p['register'] for p in inv['pairs']} | {p['borrow_from'] for p in inv['pairs']} | set(LOWS)
    deadlines = {base: next(b['first_input'] for b in blocks if base in b['helpers']) for base in BASES}
    probes = {i: None for i in deadlines.values()}
    c.replay(w, blocks, inv, probe=probes)
    observations = []
    for base, deadline in deadlines.items():
        snap = probes[deadline]
        rows = c.handoff_rows(w, blocks, inv, deadline)
        by_schedule = {}
        for label, events in schedules.items():
            touches = {}
            for i, phase, gate in events:
                for r in c.incident(gate):
                    touches.setdefault(r, []).append((i, phase))
            eligible = [r for r in sorted(rows) if r not in used and not w['v'] <= r < 2 * w['v']
                        and w['frames'][w['start'][r]] and len(snap['cur'][r]) <= 4
                        and all(i < deadline or (i == deadline and phase == 'early_tail') for i, phase in touches.get(r, []))]
            assert eligible == EXPECTED
            by_schedule[label] = dict(eligible=eligible,
                                      last_touches={str(r): list(touches[r][-1]) for r in eligible})
        U = c.span(snap['cur'][68])
        generous_pool = [r for r in rows if not w['v'] <= r < 2 * w['v'] and c.span(snap['cur'][r]) <= U]
        functional = {(68, ()): c.Q(1), (4, ()): c.Q(-1)}
        dot = lambda row: sum(q * functional.get(k, c.Q(0)) for k, q in row.items())
        assert dot({(68, ()): c.Q(1)}) == 1
        separated = all(dot(rows[r]) == 0 for r in generous_pool)
        simultaneous = {r: dict(row) for r, row in rows.items()}
        gates = []
        for r, s in ORIENTED_PAIRS:
            assert c.span(snap['cur'][r]) == c.span(snap['cur'][s])
            c.sparse_add(simultaneous[r], simultaneous[s], c.Q(1, 2))
            c.sparse_add(simultaneous[s], simultaneous[r], c.Q(-1))
            assert simultaneous[r] == {(r, ()): c.Q(1)}
            assert simultaneous[s] == {(s, ()): c.Q(1)}
            gates += [dict(target=r, source=s, coefficient='1/2', basis=snap['cur'][r]),
                      dict(target=s, source=r, coefficient='-1', basis=snap['cur'][s])]
        observations.append(dict(block=base, handoff_B=deadline, schedules=by_schedule,
                                 current_bases={str(r): snap['cur'][r] for r in EXPECTED},
                                 entrance_bases={str(r): w['frames'][w['start'][r]] for r in EXPECTED},
                                 simultaneous_restoration_gates=gates,
                                 source_rows={str(r): c.encode_row(rows[r]) for r in EXPECTED},
                                 lender68_functional_diagnostic=dict(frame_pool=generous_pool,
                                      frame_pool_rows={str(r): c.encode_row(rows[r]) for r in generous_pool},
                                      functional=c.encode_row(functional), separates=separated,
                                      nonzero_pool_values={str(r): str(dot(rows[r])) for r in generous_pool if dot(rows[r])},
                                      functional_on_initial68='1')))
    return dict(provider=name, baseline=baseline, first_helper_frames=first_frames, observations=observations,
                unused_retired_dimension_at_most4_pool=EXPECTED,
                simultaneously_restored_lenders=10,
                distinct_lenders_required_for_all16=16)


def main():
    if not __debug__:
        raise RuntimeError('assertions must remain enabled')
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', type=Path, default=HERE / 'BLOCK-POOL.json')
    args = ap.parse_args()
    c.check_sources()
    cases = []
    for name, tag in [('gauge44', 'base'), ('extra', 'extra')]:
        for baseline in ['high48', 'full80']:
            cases.append(run_case(name, tag, baseline))
            print('PASS_BLOCK_POOL', name, baseline, flush=True)
    out = dict(status='PASS_SCOPED_FOUR_BLOCK_POOL_BOUND', cases=cases,
               domain=dict(low_helpers=LOWS, providers=2, baselines_per_provider=2,
                           handoff_snapshots=16, scalar_schedules_per_snapshot=2),
               conclusion='Every snapshot has exactly11 unused retired nonzero-entrance fields of dimension at most4, with the same union. Five same-frame paired updates restore10 fields simultaneously. Blocks632,640,656 contain12 dimension4 first-use slots sharing only11 dimension-compatible lenders, a finite Hall obstruction for the frozen one-use mechanism regardless of restoration. Block648 has4 dimension5 slots; its larger lender pool is deliberately not searched. Even granting those4 arbitrary distinct lenders and restoration of all11 small-frame fields, this one-use mechanism supplies at most15 of16 slots.',
               scope='The initial dimension4 screen does not describe every candidate for dimension5 block648. This does not exclude lender recycling, zero-entrance lenders, other handoff times, paid restoration, changed circuits, or alternative mechanisms. Ten restored fields are a source-availability certificate, not10 complete compensated aliases.',
               source_head='bf1742aee4d855efb8bbd44a8419eddb33a679e5',
               source_sha256={str(p.relative_to(HERE.parent)): hashlib.sha256(p.read_bytes()).hexdigest() for p in [HERE / 'census.py', Path(__file__).resolve()]},
               attribution='Tekalign (@tekuuu), with substantial OpenAI Codex assistance; PR2226/PR2269/PR2339 predecessor constructions. Apache-2.0.')
    args.out.write_text(json.dumps(out, indent=2, sort_keys=True) + '\n')
    print(out['status'])


if __name__ == '__main__':
    main()

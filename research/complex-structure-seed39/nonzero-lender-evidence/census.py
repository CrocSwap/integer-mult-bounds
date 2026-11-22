#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Tekalign (@tekuuu), with substantial OpenAI Codex assistance.
"""Census unused nonzero-entrance lenders for PR2339 low helper 644.

The pinned replay is unchanged, including its zero-entrance assertion for
initial corrections. New pairs are diagnosed with their correction OMITTED;
their nonzero residual is an obligation, not an admitted construction.
"""
import argparse
from collections import defaultdict
from fractions import Fraction as Q
import hashlib
import inspect
import json
from pathlib import Path
import sys
import time

HERE = Path(__file__).resolve().parent
STAGE = HERE.parent / 'anticipatory-stage-evidence'
VENDOR = STAGE / 'vendor/pr2339'
sys.path.insert(0, str(STAGE))
sys.path.insert(0, str(VENDOR))
from selective_alias_marginals import read, check_sources, subset_witness, inventory
from replay_core import replay, span, frame_basis, incident
from build_ext import deferred_sets, prefix_plan, first_frame


def handoff_rows(w, blocks, inv, deadline):
    """Observe pinned replay locals without changing its code or assertions."""
    lines, first = inspect.getsourcelines(replay)
    line = first + next(j for j, s in enumerate(lines) if s.strip() == 'if i in starts:')
    captured = {}

    def observe(frame, event, arg):
        if event == 'line' and frame.f_lineno == line and frame.f_locals['i'] == deadline:
            captured.update({r: dict(row) for r, row in frame.f_locals['val'].items()})
            sys.settrace(None)
        return observe

    def trace(frame, event, arg):
        return observe if frame.f_code is replay.__code__ else None

    try:
        sys.settrace(trace)
        replay(w, blocks, inv)
    finally:
        sys.settrace(None)
    assert captured
    return captured


def replay_with_restoration(w, blocks, inv, deadline, gates, **kwargs):
    """Call original scalar evaluator at one observed boundary; never patch it.

    It updates the original profile and inverse-cleanup stack as normal.
    The witness extension is experimental and not a native compiler input.
    """
    lines, first = inspect.getsourcelines(replay)
    line = first + next(j for j, s in enumerate(lines) if s.strip() == 'if i in starts:')
    inserted = []

    def observe(frame, event, arg):
        if event == 'line' and frame.f_lineno == line and frame.f_locals['i'] == deadline:
            sys.settrace(None)
            for gate in gates:
                frame.f_locals['scalar'](gate)
                inserted.append(gate)
        return observe

    def trace(frame, event, arg):
        return observe if frame.f_code is replay.__code__ else None

    try:
        sys.settrace(trace)
        result = replay(w, blocks, inv, **kwargs)
    finally:
        sys.settrace(None)
    assert inserted == gates
    return result


def sparse_add(a, b, scale):
    for key, value in b.items():
        q = a.get(key, Q(0)) + scale * value
        if q:
            a[key] = q
        else:
            a.pop(key, None)


def combination(rows, pool, goal):
    """Exact rational Gaussian elimination, with original-register coefficients."""
    pivots = {}
    for r in pool:
        row, coeff = dict(rows[r]), {r: Q(1)}
        while row:
            key = min(row)
            if key not in pivots:
                q = row[key]
                pivots[key] = ({k: v / q for k, v in row.items()},
                               {k: v / q for k, v in coeff.items()})
                break
            base, code = pivots[key]
            q = -row[key]
            sparse_add(row, base, q)
            sparse_add(coeff, code, q)
    row, coeff = dict(goal), {}
    while row:
        key = min(row)
        if key not in pivots:
            return None, row
        base, code = pivots[key]
        q = row[key]
        sparse_add(row, base, -q)
        sparse_add(coeff, code, q)
    return coeff, {}


def encode_row(row):
    return [{'source': source, 'operator_word': list(word), 'coefficient': str(c)}
            for (source, word), c in sorted(row.items())]


def restoration_scan(w, inv, snap, rows, lenders):
    out = []
    for lender in lenders:
        if not (lender['retired'] and lender['first_use_dim_allows_rankzero'] and not lender['pristine']):
            continue
        r = lender['register']
        U = span(lender['current_basis'])
        pool = [s for s in rows if not w['v'] <= s < 2 * w['v'] and span(snap['cur'][s]) <= U]
        assert r in pool
        goal = {(r, ()): Q(1)}
        solution, remainder = combination(rows, pool, goal)
        record = dict(register=r, current_basis=lender['current_basis'], pool=pool,
                      current_row=encode_row(rows[r]),
                      exact_span_contains_initial=solution is not None)
        if solution is None:
            record['elimination_remainder'] = encode_row(remainder)
            record['status'] = 'NO_EXACT_LINEAR_RESTORATION_FROM_THIS_FRAME_POOL'
            if r == 68:
                functional = {(68, ()): Q(1), (4, ()): Q(-1)}
                dot = lambda row: sum(c * functional.get(k, Q(0)) for k, c in row.items())
                assert all(dot(rows[s]) == 0 for s in pool)
                assert dot(goal) == 1
                record['separating_functional'] = encode_row(functional)
                record['functional_on_pool'] = {str(s): str(dot(rows[s])) for s in pool}
                record['functional_on_goal'] = '1'
                record['pool_rows'] = {str(s): encode_row(rows[s]) for s in pool}
        else:
            # Prefer a triangular update that keeps coefficient1 on the lender.
            difference = dict(goal)
            sparse_add(difference, rows[r], Q(-1))
            triangular, _ = combination(rows, [s for s in pool if s != r], difference)
            if triangular is not None:
                triangular[r] = Q(1)
                solution = triangular
            dyadic = all(c.denominator & (c.denominator - 1) == 0 for c in solution.values())
            factor = solution.get(r, Q(0))
            unit = factor and abs(factor.numerator) & (abs(factor.numerator) - 1) == 0 and factor.denominator & (factor.denominator - 1) == 0
            reconstructed = {}
            for s, c in solution.items():
                sparse_add(reconstructed, rows[s], c)
            assert reconstructed == goal
            record.update(solution={str(s): str(c) for s, c in sorted(solution.items())},
                          dyadic=dyadic, lender_factor_is_dyadic_unit=bool(unit),
                          scalar_additions=len(solution) - (r in solution),
                          scalar_scale=int(factor != 1))
            same_frame = all(span(snap['cur'][s]) == U for s in solution)
            record['all_solution_sources_already_in_same_frame'] = same_frame
            record['solution_source_bases'] = {str(s): snap['cur'][s] for s in sorted(solution)}
            record['solution_source_rows'] = {str(s): encode_row(rows[s]) for s in sorted(solution)}
            record['status'] = 'REVERSIBLE_ZERO_RANK_RESTORATION' if dyadic and unit and same_frame else 'RATIONAL_SOLUTION_NOT_CERTIFIED_ZERO_RANK_REVERSIBLE'
        print('restoration', r, record['status'], flush=True)
        out.append(record)
    return out


def actual_events(w, blocks, inv):
    """Exact B/deferred/early-tail scalar schedule before proposed new pair."""
    deferred, skip = deferred_sets(w, blocks)
    deleted = {i for p in inv['pairs'] if p['low']
               for i in p.get('deleted_prefix_indices', p['deleted_echo_indices'])}
    rewrites = {int(i): gates for p in inv['pairs'] if p['low']
                for i, gates in p.get('early_prefix_rewrites', {}).items()}
    early = defaultdict(list)
    for x in inv['early_tail_events']:
        early[x['before_B']].append(x['gate'])
    for i in range(len(w['B']) + 1):
        for e in early[i]:
            yield i, 'early_tail', e
        for e in deferred.get(i, []):
            yield i, 'B', e
        for e in rewrites.get(i, []):
            yield i, 'B', e
        if i < len(w['B']) and i not in skip and i not in deleted:
            yield i, 'B', w['B'][i]


def gf_rank(xs):
    b = {}
    for x in xs:
        while x:
            j = x.bit_length()
            if j not in b:
                b[j] = x
                break
            x ^= b[j]
    return len(b)


def gf_extend(xs, h):
    out = list(xs)
    for j in range(h):
        if gf_rank(out + [1 << j]) > len(out):
            out.append(1 << j)
    assert len(out) == h
    return out


def gf_linear(cols, x):
    out = 0
    for j, c in enumerate(cols):
        if x >> j & 1:
            out ^= c
    return out


def gf_change(source, target, h):
    a, b = gf_extend(source, h), gf_extend(target, h)
    back = {gf_linear(a, x): x for x in range(1 << h)}
    assert len(back) == 1 << h
    return [gf_linear(b, back[1 << j]) for j in range(h)]


def one_case(name, tag, baseline, L=644):
    w = read(VENDOR / 'inputs' / f'{name}.canonical.json.gz')
    blocks = read(VENDOR / 'inputs/blocks.json')['sources'][0]['blocks']
    full = read(VENDOR / 'witness' / f'witness_80_{tag}.json')
    inv = subset_witness(full, set() if baseline == 'high48' else
                         {p['register'] for p in full['pairs'] if p['low']})
    block = next(b for b in blocks if L in b['helpers'])
    deadline = block['first_input']
    probe = {deadline: None}
    complete = replay(w, blocks, inv, probe=probe)
    snap = probe[deadline]
    rows = handoff_rows(w, blocks, inv, deadline)
    assert {r for r, row in rows.items() if row == {(r, ()): Q(1)}} == snap['pristine']
    deferred, skip = deferred_sets(w, blocks)
    plan, obstruction = prefix_plan(w, block, L, skip)
    assert plan is not None, obstruction
    j, frame = first_frame(w, deadline, L, deferred, skip,
                           set(plan['deleted_prefix_indices']),
                           {int(i): g for i, g in plan['early_prefix_rewrites'].items()})
    first_basis = frame_basis(span(w['frames'][frame]))
    used = {p['register'] for p in inv['pairs']} | {p['borrow_from'] for p in inv['pairs']}
    events = list(actual_events(w, blocks, inv))
    touches = defaultdict(list)
    for i, phase, e in events:
        for r in incident(e):
            touches[r].append((i, phase))
    restored = {x['register']: x['frame'] for x in complete['exact_cold_restoration']}
    frames_index = {span(f): i for i, f in reversed(list(enumerate(w['frames'])))}
    all_lenders = []
    candidates = []
    for r in range(2 * w['v'] + w['R']):
        entrance = w['frames'][w['start'][r]]
        if r == L or r in used or w['v'] <= r < 2 * w['v'] or not entrance:
            continue
        retired = all(i < deadline or (i == deadline and phase == 'early_tail')
                      for i, phase in touches[r])
        current = snap['cur'].get(r)
        record = dict(register=r, entrance_basis=entrance,
                      current_basis=current, canonical_final_basis=w['frames'][w['final'][r]],
                      baseline_restored_basis=w['frames'][restored[r]] if r in restored else list(1 << j for j in range(w['h'])),
                      entrance_dim=len(entrance), current_dim=None if current is None else len(current),
                      canonical_final_dim=len(w['frames'][w['final'][r]]),
                      baseline_final_dim=len(w['frames'][restored[r]]) if r in restored else w['h'],
                      cold_restored=r in restored, retired=retired,
                      pristine=r in snap['pristine'],
                      last_scalar_touch=list(touches[r][-1]) if touches[r] else None,
                      active=current is not None,
                      first_use_dim_allows_rankzero=current is not None and len(current) <= len(first_basis))
        all_lenders.append(record)
        if not (retired and record['pristine'] and record['first_use_dim_allows_rankzero']):
            continue
        U = current
        E = first_basis[:len(U)]
        last = max([i if phase == 'B' else i - 1 for i, phase in touches[r]], default=-1)
        pair = dict(register=L, base=block['base'], common_basis=frame_basis(span(block['common_frame'])),
                    dimension=len(frame_basis(span(block['common_frame']))), deadline=deadline,
                    deleted_echo_indices=plan['deleted_echo_indices'], low=True, borrow_from=r,
                    retirement_B_event=last, retirement_frame=frames_index[span(U)],
                    retirement_dimension=len(U), old_final_dimension=len(w['frames'][w['final'][r]]),
                    handoff_B=deadline, handoff_basis=E, handoff_paid_rank=0, anticipate=True,
                    retirement_basis=U, first_use_B=j,
                    deleted_prefix_indices=plan['deleted_prefix_indices'],
                    early_prefix_rewrites=plan['early_prefix_rewrites'])
        proposed = dict(inv, pairs=inv['pairs'] + [pair])
        diag = replay(w, blocks, proposed, diagnose=True)
        assert all(ok for _, _, ok in diag['lender_check'])
        residual = [{'target': t, 'terms': [{'source': source, 'operator_word': list(word), 'coefficient': str(c)}
                     for (source, word), c in sorted(row.items())]}
                    for t, row in sorted(diag['residual'].items())]
        candidate = dict(record, pair=pair, G_columns=gf_change(w['frames'][pair['retirement_frame']], E, w['h']),
                         operator=len(proposed['pairs']), residual=residual,
                         diagnostic_profile=diag['profile'],
                         diagnostic_final_basis=frame_basis(diag['cur'][r]))
        candidates.append(candidate)
        print(name, baseline, 'CANDIDATE', r, 'start/current/final', len(entrance), len(U),
              record['baseline_final_dim'], 'targets', [x['target'] for x in residual], flush=True)
    repairs = restoration_scan(w, inv, snap, rows, all_lenders)
    # One explicit repaired representative. Other restoration solutions are
    # exact scalar identities, not automatically admitted borrowing witnesses.
    repaired_candidates = []
    repair = next(x for x in repairs if x['register'] == 33)
    if repair['status'] == 'REVERSIBLE_ZERO_RANK_RESTORATION':
        r = repair['register']
        fact = next(x for x in all_lenders if x['register'] == r)
        U = fact['current_basis']
        E = first_basis[:len(U)]
        f = frames_index[span(U)]
        factor = Q(repair['solution'][str(r)])
        gates = []
        if factor != 1:
            gates.append(['scale', r, factor.numerator, factor.denominator, f])
        for s, q in repair['solution'].items():
            if int(s) != r:
                c = Q(q)
                gates.append(['add', r, int(s), c.numerator, c.denominator, f])
        pair = dict(register=L, base=block['base'], common_basis=frame_basis(span(block['common_frame'])),
                    dimension=len(frame_basis(span(block['common_frame']))), deadline=deadline,
                    deleted_echo_indices=plan['deleted_echo_indices'], low=True, borrow_from=r,
                    retirement_B_event=max([i if phase == 'B' else i - 1 for i, phase in touches[r]], default=-1), retirement_frame=f,
                    retirement_dimension=len(U), old_final_dimension=len(w['frames'][w['final'][r]]),
                    handoff_B=deadline, handoff_basis=E, handoff_paid_rank=0, anticipate=True,
                    retirement_basis=U, first_use_B=j,
                    deleted_prefix_indices=plan['deleted_prefix_indices'],
                    early_prefix_rewrites=plan['early_prefix_rewrites'])
        proposed = dict(inv, pairs=inv['pairs'] + [pair])
        diag = replay_with_restoration(w, blocks, proposed, deadline, gates, diagnose=True)
        assert all(ok for _, _, ok in diag['lender_check'])
        residual = [{'target': t, 'terms': encode_row(row)} for t, row in sorted(diag['residual'].items())]
        no_repair = replay(w, blocks, proposed, diagnose=True)
        assert not next(ok for op, _, ok in no_repair['lender_check'] if op == len(proposed['pairs']))
        bad_gates = [list(e) for e in gates]
        bad_gates[0][3] *= -1
        bad = replay_with_restoration(w, blocks, proposed, deadline, bad_gates, diagnose=True)
        assert not next(ok for op, _, ok in bad['lender_check'] if op == len(proposed['pairs']))
        assertion_rejected = False
        bad_initial = dict(proposed, initial_corrections=proposed['initial_corrections'] +
                           [dict(target=112, source=r, operator_word=[len(proposed['pairs'])], coefficient='1')])
        try:
            replay(w, blocks, bad_initial, diagnose=True)
        except AssertionError:
            assertion_rejected = True
        assert assertion_rejected
        repaired_candidates.append(dict(register=r, pair=pair, restoration_gates=gates,
                                        restoration_phase='Immediately before B1109 handoffs, after baseline early-tail gates; integer retirement metadata refers to original scalar schedule.',
                                        operator_source_basis=w['frames'][f],
                                        G_columns=gf_change(w['frames'][f], E, w['h']),
                                        operator=len(proposed['pairs']), residual=residual,
                                        diagnostic_profile=diag['profile'],
                                        target_bases_before_handoff={str(t): snap['cur'][t] for t in range(w['v'], 2*w['v'])},
                                        controls=dict(omitted_restoration_rejected=True, wrong_restoration_sign_rejected=True,
                                                      nonzero_entrance_initial_compensation_rejected=assertion_rejected),
                                        status='PRISTINE_AFTER_REVERSIBLE_RESTORATION_BUT_COMPENSATION_UNIMPLEMENTED'))
    return dict(provider=name, baseline=baseline, helper=L, handoff_B=deadline,
                first_use_B=j, first_use_frame=frame, first_use_basis=first_basis,
                baseline_profile=complete['local_profile'], baseline_mass=complete['local_mass'],
                baseline_widths=inventory(w, inv, complete),
                baseline_helpers=w['R'] - len(inv['pairs']),
                unused_nonzero_lenders=all_lenders, candidates=candidates,
                frame_local_restoration=repairs, repaired_candidates=repaired_candidates)


def main():
    if not __debug__:
        raise RuntimeError('assertions must remain enabled')
    check_sources()
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', type=Path, default=HERE / 'CENSUS.json')
    args = ap.parse_args()
    receipt = read(STAGE / 'PR2339-SOURCE-RECEIPT.json')
    ext_pin = next(x for x in receipt['files'] if x['vendor_path'] == 'vendor/pr2339/build_ext.py')
    assert hashlib.sha256((VENDOR / 'build_ext.py').read_bytes()).hexdigest() == ext_pin['sha256']
    source_paths = [VENDOR / 'replay_core.py', VENDOR / 'build_ext.py', VENDOR / 'inputs/blocks.json',
                    STAGE / 'selective_alias_marginals.py', Path(__file__).resolve()]
    for name, tag in [('gauge44', 'base'), ('extra', 'extra')]:
        source_paths += [VENDOR / 'inputs' / f'{name}.canonical.json.gz',
                         VENDOR / 'witness' / f'witness_80_{tag}.json']
    started = time.monotonic()
    result = dict(status='SCOPED_CENSUS_NONZERO_ENTRANCE_644', assignment_seed=39,
                  base_commit='7ee02b7c96d85f22b38d28bd7ed49bb8c1aeb261',
                  source_head='bf1742aee4d855efb8bbd44a8419eddb33a679e5',
                  source_sha256={str(p.relative_to(HERE.parent)): hashlib.sha256(p.read_bytes()).hexdigest() for p in source_paths},
                  attribution='Tekalign (@tekuuu), with substantial OpenAI Codex assistance. Builds on PR2339 (Sagar Thakrar), PR2226 (Cinna Davis), and PR2269 (Jeremy Kothe). Apache-2.0.',
                  scope='Four baselines; unused active non-target lenders with nonzero entrance, exact pristine handoff, actual scalar retirement, and rank-zero handoff dimension. All11 retired dimension4 lenders are then tested for exact frame-local restoration. Only repaired33 is diagnosed as an alias. Diagnostic residual is not paid or admitted.', cases=[])
    for name, tag in [('gauge44', 'base'), ('extra', 'extra')]:
        for baseline in ['high48', 'full80']:
            result['cases'].append(one_case(name, tag, baseline))
    result['coverage'] = dict(baselines=4, unused_nonzero_lenders=sum(len(c['unused_nonzero_lenders']) for c in result['cases']),
                              direct_candidates=sum(len(c['candidates']) for c in result['cases']),
                              restoration_checks=sum(len(c['frame_local_restoration']) for c in result['cases']),
                              successful_restorations=sum(x['status']=='REVERSIBLE_ZERO_RANK_RESTORATION' for c in result['cases'] for x in c['frame_local_restoration']),
                              repaired_pair_diagnostics=sum(len(c['repaired_candidates']) for c in result['cases']),
                              negative_controls=12)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(result['status'], json.dumps(result['coverage'], sort_keys=True), 'seconds', round(time.monotonic()-started, 3), flush=True)


if __name__ == '__main__':
    main()

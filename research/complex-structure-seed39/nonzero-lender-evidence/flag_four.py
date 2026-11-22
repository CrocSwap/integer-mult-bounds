#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Tekalign (@tekuuu), with substantial OpenAI Codex assistance.
"""Four simultaneous scalar-repaired flag borrowers in block640.

Emits uncompensated formal residuals and exact physical Gaussian certificates.
It does not admit the early target-lift chronology or complete hosted bound.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import numpy as np
import census as c

HERE = Path(__file__).resolve().parent
ASSIGNMENT = [(640, 33, 49), (641, 55, 101), (642, 74, 83), (644, 85, 98)]


def build_case(name, tag, baseline, ops):
    w = c.read(c.VENDOR / 'inputs' / f'{name}.canonical.json.gz')
    blocks = c.read(c.VENDOR / 'inputs/blocks.json')['sources'][0]['blocks']
    full = c.read(c.VENDOR / 'witness' / f'witness_80_{tag}.json')
    inv = c.subset_witness(full, set() if baseline == 'high48' else
                           {p['register'] for p in full['pairs'] if p['low']})
    deadline = 1109
    probe = {deadline: None}
    c.replay(w, blocks, inv, probe=probe)
    snap = probe[deadline]
    rows = c.handoff_rows(w, blocks, inv, deadline)
    used = {p['register'] for p in inv['pairs']} | {p['borrow_from'] for p in inv['pairs']}
    assert not used.intersection({r for _, r, _ in ASSIGNMENT} | {s for _, _, s in ASSIGNMENT})
    deferred, skip = c.deferred_sets(w, blocks)
    frame_ids = {c.span(f): i for i, f in reversed(list(enumerate(w['frames'])))}
    events = list(c.actual_events(w, blocks, inv))
    touches = {}
    for i, phase, e in events:
        for r in c.incident(e):
            touches.setdefault(r, []).append((i, phase))
    pairs, gates, records = [], [], []
    h = w['h']
    identity = lambda: (np.eye(1 << h, dtype=np.int64), np.zeros((1 << h, 1 << h), dtype=np.int64), 0)
    for L, r, partner in ASSIGNMENT:
        block = next(b for b in blocks if L in b['helpers'])
        assert block['first_input'] == deadline
        assert all(i < deadline or (i == deadline and phase == 'early_tail')
                   for s in [r, partner] for i, phase in touches[s])
        U = snap['cur'][r]
        assert c.span(U) == c.span(snap['cur'][partner])
        restored = dict(rows[r])
        c.sparse_add(restored, rows[partner], c.Q(1, 2))
        assert restored == {(r, ()): c.Q(1)}
        f = frame_ids[c.span(U)]
        gate = ['add', r, partner, 1, 2, f]
        gates.append(gate)
        plan, failure = c.prefix_plan(w, block, L, skip)
        assert plan is not None, failure
        j, first = c.first_frame(w, deadline, L, deferred, skip,
                                set(plan['deleted_prefix_indices']),
                                {int(i): g for i, g in plan['early_prefix_rewrites'].items()})
        F = c.frame_basis(c.span(w['frames'][first]))
        S = w['frames'][w['start'][r]]
        T = [30]
        assert len(S) == 1 and c.span(T) <= c.span(F)
        a, b = list(S), list(T)
        for x in c.frame_basis(c.span(U)):
            if c.gf_rank(a + [x]) > len(a):
                a.append(x)
        for x in F:
            if c.gf_rank(b + [x]) > len(b):
                b.append(x)
        G = ops.change(a, b, h)
        Uoriginal = w['frames'][f]
        E = [ops.linear(G, x) for x in Uoriginal]
        assert c.span(E) == c.span(F) and ops.change(Uoriginal, E, h) == G
        assert ops.linear(G, S[0]) == 30
        pair = dict(register=L, base=block['base'], common_basis=c.frame_basis(c.span(block['common_frame'])),
                    dimension=len(c.frame_basis(c.span(block['common_frame']))), deadline=deadline,
                    deleted_echo_indices=plan['deleted_echo_indices'], low=True, borrow_from=r,
                    retirement_B_event=max(i if phase == 'B' else i - 1 for i, phase in touches[r]),
                    retirement_frame=f, retirement_dimension=len(U), old_final_dimension=len(w['frames'][w['final'][r]]),
                    handoff_B=deadline, handoff_basis=E, handoff_paid_rank=0, anticipate=True,
                    retirement_basis=U, first_use_B=j,
                    deleted_prefix_indices=plan['deleted_prefix_indices'],
                    early_prefix_rewrites=plan['early_prefix_rewrites'])
        pairs.append(pair)
        checks = []
        K = ops.monomial(G, h)
        for label, source, target, sign in [
            ('entrance_line', S, T, 1), ('handoff', Uoriginal, E, 1),
            ('full_inverse_cleanup', [1 << k for k in range(h)], [1 << k for k in range(h)], -1),
        ]:
            z = ops.frame(identity(), source, h, -1)
            z = ops.apply_mono(z, K, sign)
            z = ops.frame(z, target, h, 1)
            checks.append(dict(label=label, gaussian_monomial_sha256=ops.check(z), columns=1 << h))
        records.append(dict(register=L, lender=r, partner=partner, entrance_basis=S,
                            retirement_basis=Uoriginal, handoff_basis=E, G_columns=G,
                            restoration_gate=gate, restoration_source_rows={str(s): c.encode_row(rows[s]) for s in [r, partner]},
                            gaussian_checks=checks, operator=len(inv['pairs']) + len(pairs)))
    proposed = dict(inv, pairs=inv['pairs'] + pairs)
    diagnostic = c.replay_with_restoration(w, blocks, proposed, deadline, gates, diagnose=True)
    assert all(ok for _, _, ok in diagnostic['lender_check'])
    target_residual = [{'target': t, 'terms': c.encode_row(row)} for t, row in sorted(diagnostic['residual'].items())]
    abstract_initial = [dict(target=t, source=s, operator_word=list(word), coefficient=str(-q))
                        for t, row in sorted(diagnostic['residual'].items()) for (s, word), q in sorted(row.items())]
    assert all(len(x['operator_word']) == 1 and x['operator_word'][0] > len(inv['pairs']) for x in abstract_initial)
    bad = c.replay_with_restoration(w, blocks, proposed, deadline, gates[:-1], diagnose=True)
    assert not next(ok for op, _, ok in bad['lender_check'] if op == len(proposed['pairs']))
    return dict(provider=name, baseline=baseline, pairs=pairs, records=records,
                restoration_gates=gates, final_uncompensated_residual=target_residual,
                abstract_initial_corrections=abstract_initial, diagnostic_profile=diagnostic['profile'],
                controls=dict(omitted_last_restoration_fails_pristine_check=True),
                status='FOUR_PRISTINE_HANDOFFS_AND_EXACT_GAUSSIAN_FLAGS_COMPENSATION_UNIMPLEMENTED')


def main():
    if not __debug__:
        raise RuntimeError('assertions must remain enabled')
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', type=Path, default=HERE / 'FLAG-FOUR.json')
    args = ap.parse_args()
    c.check_sources()
    path = c.VENDOR / 'vendor/pr2226/operators.py'
    receipt = c.read(c.STAGE / 'PR2339-SOURCE-RECEIPT.json')
    pin = next(x for x in receipt['files'] if x['vendor_path'] == 'vendor/pr2339/vendor/pr2226/operators.py')
    assert hashlib.sha256(path.read_bytes()).hexdigest() == pin['sha256']
    spec = importlib.util.spec_from_file_location('pr2226_operators', path)
    ops = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ops)
    cases = []
    for name, tag in [('gauge44', 'base'), ('extra', 'extra')]:
        for baseline in ['high48', 'full80']:
            cases.append(build_case(name, tag, baseline, ops))
            print('PASS_FOUR_FLAGS', name, baseline, flush=True)
    out = dict(status='PASS_SCOPED_FOUR_REPAIRED_FLAG_HANDOFFS', cases=cases,
               assignment=ASSIGNMENT, source_head='bf1742aee4d855efb8bbd44a8419eddb33a679e5',
               source_sha256={str(p.relative_to(HERE.parent)): hashlib.sha256(p.read_bytes()).hexdigest() for p in [path, HERE / 'census.py', Path(__file__).resolve()]},
               scope='Four cases, four exact repaired handoffs per case and three512-column rank-zero Gaussian products per handoff. Abstract initial corrections violate the pinned zero-entrance rule and are recorded only for target transport by a separate extension. No full profile, native word, owner assignment, or new kappa is certified.',
               attribution='Tekalign (@tekuuu), with substantial OpenAI Codex assistance. PR2226 Gaussian operators and PR2269/PR2339 provider construction. Apache-2.0.')
    args.out.write_text(json.dumps(out, indent=2, sort_keys=True) + '\n')
    print(out['status'])


if __name__ == '__main__':
    main()

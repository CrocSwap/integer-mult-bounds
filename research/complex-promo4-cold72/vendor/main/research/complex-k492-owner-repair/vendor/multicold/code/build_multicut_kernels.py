"""Frozen multi-cut cold-kernel constructor; Apache-2.0.

Generalises PR564's build_cold_kernel.py: a cold pivot (untouched before its
first new gate) may receive its donor gates  donor += -q*pivot @E  at several
cuts.  The pivot holds only its initial dirt until its first original touch, so
the new gates kill its complete dirty response iff the exact suffix relation
sum_g q_g * col_{cut_g}[donor_g] = col[pivot] holds.  This script inserts the
recipe gates kernel by kernel (positions refer to the word before that kernel),
then checks: donors are not targets/pivot/centres, dyadic coefficients, the
pivot's first touch is a new gate, the exact complete dirty response of the
pivot is zero (forward replay), frame legality and the exact profile delta via
gk_word.profile, and the pinned output content hash.  Native all-column,
phase, owner, invoice and assembly checks remain separate.
"""
import argparse, copy, gzip, hashlib, json, sys
from fractions import Fraction as Q
from pathlib import Path
if not __debug__: raise SystemExit('Assertions required.')
ap = argparse.ArgumentParser()
for k in ('input', 'recipe', 'gk-dir', 'out'): ap.add_argument('--' + k, type=Path, required=True)
a = ap.parse_args()
sys.path.insert(0, str(a.gk_dir.resolve())); import gk_word as g, gk_common as co
g.V = co.V = 112; g.DATA = co.DATA = 7168
V = 112; N = 728
raw = gzip.decompress(a.input.read_bytes()); recipe = json.loads(a.recipe.read_text())
assert hashlib.sha256(raw).hexdigest() == recipe['input_content_sha256']
w = json.loads(raw)
regs = lambda e: e[1:3] if e[0] == 'add' else e[1:2]


def dirty_response(word, pivot):
    rows = {}
    def get(r): return rows.setdefault(r, {r: Q(1)})
    for e in word['A'] + word['cut'] + word['B']:
        if e[0] == 'scale':
            q = Q(e[2], e[3]); rows[e[1]] = {j: q * x for j, x in get(e[1]).items()}
        else:
            t, s = e[1], e[2]; q = Q(e[3], e[4]); src = get(s); tgt = get(t)
            for j, x in list(src.items()):
                z = tgt.get(j, Q(0)) + q * x
                if z: tgt[j] = z
                else: tgt.pop(j, None)
    return {r: rows[r][pivot] for r in range(V, 2 * V) if r in rows and rows[r].get(pivot)}


receipts = []
for K in recipe['kernels']:
    P0 = g.profile(w)
    pivot = K['pivot']; E = co.basis(K['frame'])
    assert 2 * V <= pivot < N and str(pivot) not in w['start_extra']
    before = dirty_response(w, pivot); assert before, 'pivot already has zero response'
    ins = {'A': {}, 'B': {}}
    for gt in K['gates']:
        d = gt['donor']; q = Q(gt['coefficient'])
        assert d != pivot and d not in w['centers']
        if V <= d < 2 * V:
            # gauge-type (target) donor: only after the centre scatter, like the post-centre gauge compensation
            assert gt['part'] == 'B' and gt.get('target_donor') is True
        assert q and q.denominator & (q.denominator - 1) == 0
        assert gt['part'] in ('A', 'B') and 0 <= gt['index'] <= len(w[gt['part']])
        ins[gt['part']].setdefault(gt['index'], []).append(['add', d, pivot, -q.numerator, q.denominator, list(E)])
    assert all(pivot not in regs(e) for e in w['cut'] if e[0] == 'add')
    new_ids = {id(e) for part in ins for lst in ins[part].values() for e in lst}
    for part in ('B', 'A'):
        for i in sorted(ins[part], reverse=True):
            w[part][i:i] = ins[part][i]
    allg = w['A'] + w['B']
    first_old = next(k for k, e in enumerate(allg) if pivot in regs(e) and id(e) not in new_ids)
    assert all(id(e) in new_ids or pivot not in regs(e) for e in allg[:first_old])
    assert sum(id(e) in new_ids for e in allg[:first_old]) == len(K['gates']), 'every new gate must precede the first original pivot touch'
    w['start_extra'][str(pivot)] = list(E)
    w['cleanup'] = [g.inverse(e, g.FULL) for e in reversed(w['A'] + w['B']) if not V <= e[1] < 2 * V]
    after = dirty_response(w, pivot)
    assert not after, ('exact multi-cut relation failed', pivot, after)
    PP = g.profile(w)
    delta = {r: PP[r] - P0[r] for r in set(P0) | set(PP) if PP[r] != P0[r]}
    assert delta == {int(r): n for r, n in K['profile_delta'].items()}, (pivot, delta)
    assert sum(r * n for r, n in delta.items()) == -len(E)
    receipts.append(dict(pivot=pivot, changed_helper=pivot - 2 * V, entrance_frame=list(E), inserted_gates=len(K['gates']),
                         cuts=sorted({(gt['part'], gt['index']) for gt in K['gates']}), profile_delta=delta,
                         prior_dirty_targets=len(before), exact_zero_response=True, helper_width_before=9,
                         helper_width_after=9 - len(E)))
w['report']['local_profile'] = {str(k): n for k, n in sorted(g.profile(w).items())}
w['report']['entering_helpers'] = sum(1 for x in g.widths_of(w) if x < 9)
w['report']['entrance_rank'] = sum(9 - x for x in g.widths_of(w))
encoded = g.dump(w)
assert hashlib.sha256(gzip.decompress(encoded)).hexdigest() == recipe['output_content_sha256'], hashlib.sha256(gzip.decompress(encoded)).hexdigest()
a.out.mkdir(parents=True, exist_ok=False); (a.out / 'FULL-WORD.json.gz').write_bytes(encoded)
r = dict(status='PASS_FROZEN_MULTICUT_COLD_KERNEL_CONSTRUCTION', input_content_sha256=recipe['input_content_sha256'],
         output_content_sha256=recipe['output_content_sha256'], kernels=receipts,
         local_profile=w['report']['local_profile'], entering_helpers=w['report']['entering_helpers'],
         entrance_rank=w['report']['entrance_rank'],
         scope='Literal multi-cut donor gates, exact complete dirty-response cancellation, exact frame chains and regenerated cleanup. Native all-column, phase, owner, invoice and assembly checks remain separate.')
(a.out / 'KERNEL-CONSTRUCTION.json').write_text(json.dumps(r, indent=2) + '\n'); print(json.dumps(r, indent=2))

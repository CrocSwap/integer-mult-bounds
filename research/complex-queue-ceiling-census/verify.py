#!/usr/bin/env python3
"""Packing ceilings of the local words behind the open complex kappa claims (SNAPSHOT.json).

For every pinned claim: check the coverage law mass = 72*live + 64*calls, split its profile into
local word + idle remainder, certify the word's packing ceiling with ../complex-local-word-ceiling,
and check the claim's own endpoint lies below it. Writes or checks RESULT.json.

usage: verify.py [--write]
Douglas Colkitt, with Claude (Anthropic) assistance. Apache-2.0.
"""
import json, sys
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE.parent / 'complex-local-word-ceiling'))
import ceiling as C  # noqa: E402

M, CENTRE = 73, 64
SELECTED = json.loads((ROOT / 'certificates/selected-result.json').read_text())
SELECTED_WORD = {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}    # research/complex-local-word-ceiling


def dec(x, digits=17):
    return f'{float(x):.{digits}g}'


def split(c):
    P = {int(r): n for r, n in c['profile'].items()}
    I = {int(r): n for r, n in c['idle'].items()}
    W, N = c['live'], c['calls']
    C.require(sum(r * n for r, n in P.items()) == (M - 1) * W + CENTRE * N, f"#{c['pr']} coverage law")
    C.require(all(I[r] <= P.get(r, 0) for r in I) and max(I) <= C.max_idle_rank(M), f"#{c['pr']} idle split")
    return {r: Q(P[r] - I.get(r, 0), N) for r in P if P[r] - I.get(r, 0)}, W, N


def main():
    snap = json.loads((HERE / 'SNAPSHOT.json').read_text())
    words, rows = {}, []
    for c in snap['claims']:
        local, W, N = split(c)
        C.require(Q(W, N) == Q(896, 9), f"#{c['pr']} families per call differ from 896/9")
        key = json.dumps(sorted((r, str(v)) for r, v in local.items()))
        if key not in words:
            lo, hi = C.ceiling(local, M, W, N, CENTRE)
            words[key] = dict(id=f'W{len(words) + 1}', local=local, a_lo=lo, a_hi=hi, claims=[])
        w = words[key]
        b, k = Q(c['complex_lower']), Q(c['kappa'])
        C.require(b < w['a_lo'], f"#{c['pr']} endpoint not below its word's relaxation")
        cap = w['a_hi'] / (1 + w['a_hi'])
        C.require(k < cap, f"#{c['pr']} kappa above its ceiling")
        w['claims'].append(c['pr'])
        rows.append(dict(pr=c['pr'], head=c['head'], word=w['id'], kappa=c['kappa'], kappa_decimal=dec(k),
                         kappa_cap=dec(cap), remaining_packing_headroom_percent=dec(100 * (cap / k - 1), 4),
                         live=W, calls=N))
    sel_key = json.dumps(sorted((r, str(Q(v))) for r, v in SELECTED_WORD.items()))
    C.require(sel_key in words, 'selected local word not among the claims')
    sel = words[sel_key]
    out_words = []
    for w in sorted(words.values(), key=lambda w: -w['a_hi']):
        cap = w['a_hi'] / (1 + w['a_hi'])
        out_words.append(dict(id=w['id'], selected_word=(w is sel),
                              local_profile_per_call={str(r): str(v) for r, v in sorted(w['local'].items())},
                              local_mass_per_call=str(sum(r * v for r, v in w['local'].items())),
                              a_ceiling=str(w['a_hi']), kappa_cap=dec(cap),
                              cap_vs_selected_word_percent=dec(100 * (cap / (sel['a_hi'] / (1 + sel['a_hi'])) - 1), 4),
                              claims=sorted(w['claims'])))
    best = max(words.values(), key=lambda w: w['a_hi'])
    out = dict(status='PASS_COMPLEX_QUEUE_CEILING_CENSUS', base_commit=snap['base_commit'],
               claims_covered=len(rows), claims_not_covered=[d['pr'] for d in snap['not_covered']],
               distinct_local_words=len(words),
               max_kappa_cap_over_covered_words=dec(best['a_hi'] / (1 + best['a_hi'])),
               selected_kappa=SELECTED['decimal'], words=out_words, claims=sorted(rows, key=lambda r: r['pr']),
               scope='Each cap bounds hosting, owner and idle repacking of that claim\'s own local word under the '
                     'coverage law, 896/9 live families per call and the halving guard. It does not bound changed '
                     'words, templates or outer recipes, and does not review or accept any claim.')
    text = json.dumps(out, indent=1, sort_keys=True) + '\n'
    if sys.argv[1:] == ['--write']:
        (HERE / 'RESULT.json').write_text(text)
    else:
        C.require((HERE / 'RESULT.json').read_text() == text, 'RESULT.json differs')
    print(out['status'], f"claims={len(rows)} words={len(words)} max_cap={out['max_kappa_cap_over_covered_words']}")


if __name__ == '__main__':
    try:
        main()
    except ValueError as e:
        print('FAIL:', e); sys.exit(1)

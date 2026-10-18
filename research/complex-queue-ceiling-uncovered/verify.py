#!/usr/bin/env python3
"""Packing ceilings for the sixteen queue claims the census listed as not covered (SNAPSHOT.json).

For every recorded claim: check the coverage law mass = 72*live + 64*calls, split its global
profile into local word + idle remainder with the documented field aliases, certify the word's
packing ceiling with ../complex-local-word-ceiling (#1240), and check the claim's own recorded
endpoint lies below it. Writes or checks RESULT.json. Five mutation controls run at the end.

usage: verify.py [--write]
Aaron Wang / navinor, with help from opencode. Apache-2.0.
"""
import json
import sys
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE.parent / 'complex-local-word-ceiling'))
import ceiling as C  # noqa: E402

M, CENTRE = 73, 64
SELECTED_WORD = {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}    # research/complex-local-word-ceiling
TITLE_MISMATCH = {1175: ('0.001675338871723469', '0.001674083482880778')}


def dec(x, digits=17):
    return f'{float(x):.{digits}g}'


def split(profile, idle, W, N, tag):
    P = {int(r): int(n) for r, n in profile.items()}
    I = {int(r): int(n) for r, n in idle.items()}
    C.require(sum(r * n for r, n in P.items()) == (M - 1) * W + CENTRE * N, f'{tag} coverage law')
    C.require(all(I[r] <= P.get(r, 0) for r in I) and max(I) <= C.max_idle_rank(M), f'{tag} idle split')
    C.require(Q(W, N) == Q(896, 9), f'{tag} families per call differ from 896/9')
    local = {r: Q(P[r] - I.get(r, 0), N) for r in P if P[r] - I.get(r, 0)}
    C.require(all(v >= 0 for v in local.values()), f'{tag} idle exceeds profile')
    return local


def local_key(local):
    return json.dumps(sorted((r, str(v)) for r, v in local.items()))


def compute(snap, census):
    words, rows = {}, []
    census_words = {}
    for c in census['claims']:
        local = split(c['profile'], c['idle'], c['live'], c['calls'], f"census #{c['pr']}")
        census_words.setdefault(local_key(local), []).append(c['pr'])
    known = {}
    result = json.loads((HERE.parent / 'complex-queue-ceiling-census' / 'RESULT.json').read_text())
    for w in result['words']:
        local = {int(r): Q(v) for r, v in w['local_profile_per_call'].items()}
        known[local_key(local)] = w['id']
    for c in snap['claims']:
        tag = f"#{c['pr']}"
        local = split(c['profile'], c['idle'], c['live'], c['calls'], tag)
        k = local_key(local)
        if k not in words:
            lo, hi = C.ceiling(local, M, c['live'], c['calls'], CENTRE)
            words[k] = dict(id=f'N{len(words) + 1}', local=local, a_lo=lo, a_hi=hi, claims=[])
        w = words[k]
        endpoint = Q(c['complex_lower'])
        C.require(endpoint < w['a_lo'], f'{tag} endpoint not below its word\'s relaxation')
        cap = w['a_hi'] / (1 + w['a_hi'])
        kap = Q(c['kappa_decimal'])
        C.require(kap < cap, f'{tag} kappa above its ceiling')
        if c['pr'] in TITLE_MISMATCH:
            want = TITLE_MISMATCH[c['pr']]
            C.require((c['title_kappa'], c['kappa_decimal']) == want, f'{tag} recorded title mismatch changed')
        else:
            C.require(Q(c['kappa_decimal']) == Q(c['title_kappa']), f'{tag} recorded kappa differs from title kappa')
        w['claims'].append(c['pr'])
        rows.append(dict(pr=c['pr'], head=c['head'], census_head=c['census_head'],
                         head_moved_since_census=c['head_moved_since_census'],
                         word=w['id'], title_kappa=c['title_kappa'], kappa=c['kappa_decimal'],
                         complex_lower=c['complex_lower'], live=c['live'], calls=c['calls'],
                         kappa_cap=dec(cap), remaining_packing_headroom_percent=dec(100 * (cap / kap - 1), 4),
                         title_record_mismatch=(c['pr'] in TITLE_MISMATCH),
                         extraction=c.get('extraction', 'JSON fields (see SNAPSHOT.json paths)'),
                         profile_file=c['profile_file'], idle_file=c['idle_file']))
    sel_key = local_key({r: Q(v) for r, v in SELECTED_WORD.items()})
    sel_cap = None
    for k, w in words.items():
        w['kappa_cap'] = w['a_hi'] / (1 + w['a_hi'])
        w['selected_word'] = (k == sel_key)
        if w['selected_word']:
            sel_cap = w['kappa_cap']
    C.require(sel_cap is not None, 'selected local word not among the screened words')
    out_words = []
    for w in sorted(words.values(), key=lambda w: -w['a_hi']):
        out_words.append(dict(id=w['id'], selected_word=w['selected_word'],
                              known_census_word=known.get(local_key(w['local'])),
                              local_profile_per_call={str(r): str(v) for r, v in sorted(w['local'].items())},
                              local_mass_per_call=str(sum(r * v for r, v in w['local'].items())),
                              a_ceiling=str(w['a_hi']), kappa_cap=dec(w['kappa_cap']),
                              cap_vs_selected_word_percent=dec(100 * (w['kappa_cap'] / sel_cap - 1), 4),
                              claims=sorted(w['claims'])))
    best = max(words.values(), key=lambda w: w['a_hi'])
    out = dict(status='PASS_COMPLEX_QUEUE_CEILING_UNCOVERED',
               base_commit=snap['base_commit'],
               claims_screened=len(rows),
               claims_screened_prs=sorted(r['pr'] for r in rows),
               distinct_local_words=len(words),
               new_words_vs_census=sum(1 for w in out_words if not w['known_census_word']),
               max_kappa_cap=dec(best['a_hi'] / (1 + best['a_hi'])),
               max_kappa_cap_word=best['id'],
               selected_kappa=json.loads((ROOT / 'certificates/selected-result.json').read_text())['decimal'],
               title_record_mismatches=[dict(pr=pr, title_kappa=v[0], recorded_kappa=v[1]) for pr, v in sorted(TITLE_MISMATCH.items())],
               words=out_words, claims=sorted(rows, key=lambda r: r['pr']),
               scope="Each cap bounds hosting, owner and idle repacking of that claim's own recorded local word under "
                     "the coverage law, 896/9 live families per call and the halving guard. It does not bound changed "
                     "words, templates or outer recipes, does not re-derive any claim's profile from its circuit, and "
                     "does not review or accept any claim.")
    return out, words, rows


def controls(snap):
    import copy
    census = json.loads((HERE.parent / 'complex-queue-ceiling-census' / 'SNAPSHOT.json').read_text())
    n = 0
    for mutate, why in [
        (lambda c: c['profile'].__setitem__('1', c['profile']['1'] + 1), 'coverage law'),
        (lambda c: c['idle'].__setitem__('1', c['profile']['1'] + 1), 'idle split'),
        (lambda c: c.update(live=c['live'] + 896), 'families per call'),
    ]:
        s = copy.deepcopy(snap)
        mutate(s['claims'][0])
        try:
            compute(s, census)
        except ValueError:
            n += 1
        else:
            raise ValueError('control not rejected: ' + why)
    for mutate, why in [
        (lambda c: c.update(complex_lower='2'), 'endpoint above relaxation'),
        (lambda c: c.update(title_kappa='0.5'), 'title mismatch'),
    ]:
        s = copy.deepcopy(snap)
        row = next(c for c in s['claims'] if c['pr'] != 1175)
        mutate(row)
        try:
            compute(s, census)
        except ValueError:
            n += 1
        else:
            raise ValueError('control not rejected: ' + why)
    return n


def main():
    snap = json.loads((HERE / 'SNAPSHOT.json').read_text())
    census = json.loads((HERE.parent / 'complex-queue-ceiling-census' / 'SNAPSHOT.json').read_text())
    out, words, rows = compute(snap, census)
    text = json.dumps(out, indent=1, sort_keys=True) + '\n'
    if sys.argv[1:] == ['--write']:
        (HERE / 'RESULT.json').write_text(text)
    else:
        C.require((HERE / 'RESULT.json').read_text() == text, 'RESULT.json differs')
    n = controls(snap)
    C.require(n == 5, 'control count')
    print(out['status'], f"claims={len(rows)} words={len(words)} new={out['new_words_vs_census']} "
                         f"max_cap={out['max_kappa_cap']} controls={n}")


if __name__ == '__main__':
    try:
        main()
    except ValueError as e:
        print('FAIL:', e)
        sys.exit(1)

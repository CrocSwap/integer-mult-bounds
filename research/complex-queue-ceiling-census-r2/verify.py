#!/usr/bin/env python3
"""Census round 2: screen the 16 claims the first complex-queue ceiling census could not.

For every claim pinned in SNAPSHOT2.json: re-check the coverage identity mass = 72*live + 64*calls,
the idle split, recompute the per-call local word, certify it with merged #1240's exact relaxation,
require the claim's complex_lower endpoint below the ceiling's a_lo and its title kappa below the
implied cap, and cross-control against the first census (same word -> same cap, from that census's
own pinned inputs). Three claims remain unscreened and are pinned with the exact fields they lack.
Writes or checks RESULT.json.

usage: verify.py [--write]
Abhinav Ramachandran (geckods), with substantial GLM (Z.ai) assistance via Hermes. Apache-2.0.
"""
import json, sys
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'research/complex-local-word-ceiling'))
import ceiling as C  # noqa: E402

M, CENTRE = 73, 64
CENSUS = ROOT / 'research/complex-queue-ceiling-census'
SELECTED = json.loads((ROOT / 'certificates/selected-result.json').read_text())


def dec(x, digits=17):
    return f'{float(x):.{digits}g}'


def dec17(q):
    return dec(Q(q))


def split_and_check(c, tag):
    P = {int(r): n for r, n in c['profile'].items()}
    I = {int(r): n for r, n in c['idle'].items()}
    W, N = c['live'], c['calls']
    C.require(sum(r * n for r, n in P.items()) == (M - 1) * W + CENTRE * N, f"#{c['pr']} coverage law ({tag})")
    C.require(all(I[r] <= P.get(r, 0) for r in I) and max(I) <= C.max_idle_rank(M), f"#{c['pr']} idle split ({tag})")
    C.require(Q(W, N) == Q(896, 9), f"#{c['pr']} families per call ({tag})")
    return {r: Q(P[r] - I.get(r, 0), N) for r in P if P[r] - I.get(r, 0)}


def main():
    snap = json.loads((HERE / 'SNAPSHOT2.json').read_text())
    words, rows = {}, []
    for c in snap['claims']:
        if not c['screened']:
            continue
        local = split_and_check(c, 'snapshot')
        C.require(Q(c['kappa']) == Q(c['title_kappa']), f"#{c['pr']} kappa is not the title kappa")
        lo, hi = C.ceiling(local, M, c['live'], c['calls'], CENTRE)
        lo, hi = Q(lo), Q(hi)
        C.require(lo == Q(c['a_lo']) and hi == Q(c['a_hi']), f"#{c['pr']} ceiling not reproduced")
        b, k = Q(c['complex_lower']), Q(c['kappa'])
        cap = hi / (1 + hi)
        C.require(b < lo, f"#{c['pr']} endpoint not below its word's relaxation")
        C.require(k < cap, f"#{c['pr']} kappa above its ceiling")
        key = json.dumps(sorted((r, str(v)) for r, v in local.items()))
        if key not in words:
            words[key] = dict(id=f'V{len(words) + 1}', local=local, a_lo=lo, a_hi=hi, claims=[])
        w = words[key]
        C.require(w['a_hi'] == hi, f"#{c['pr']} shared-word cap mismatch")
        w['claims'].append(c['pr'])
        rows.append(dict(pr=c['pr'], head=c['head'][:12], word=w['id'], state_note=('merged' if c['pr'] == 1111 else 'open'),
                         kappa=c['kappa'], kappa_decimal=dec17(k), kappa_cap=dec17(cap),
                         remaining_packing_headroom_percent=dec(100 * (cap / k - 1), 4),
                         live=c['live'], calls=c['calls'],
                         profile_file=c['profile_file'], prof_key=c['prof_key']))
    # ---- cross-controls against the first census (from its own pinned inputs) ----
    first = json.loads((CENSUS / 'SNAPSHOT.json').read_text())
    fresult = json.loads((CENSUS / 'RESULT.json').read_text())
    by_prof = {x['id']: x for x in fresult['words']}
    n_cross = 0
    for fw_id, src_pr in (('W4', 1152), ('W3', 1148)):
        fw = by_prof[fw_id]
        src = [x for x in first['claims'] if x['pr'] == src_pr]
        if not src:
            continue
        s = src[0]
        P = {int(r): n for r, n in s['profile'].items()}
        I = {int(r): n for r, n in s['idle'].items()}
        local = {r: Q(P[r] - I.get(r, 0), s['calls']) for r in P if P[r] - I.get(r, 0)}
        C.require({str(r): str(v) for r, v in sorted(local.items())} == fw['local_profile_per_call'],
                  f'{fw_id} word drift vs first census')
        lo, hi = C.ceiling(local, M, s['live'], s['calls'], CENTRE)
        C.require(dec17(Q(hi) / (1 + Q(hi))) == fw['kappa_cap'], f'{fw_id} cap drift vs first census')
        n_cross += 1
    C.require(n_cross == 2, 'first-census cross-controls not both run')
    # my W4-type group must equal the census W4 word exactly
    w4 = by_prof['W4']['local_profile_per_call']
    mine = [w for w in words.values() if {str(r): str(v) for r, v in sorted(w['local'].items())} == w4]
    C.require(len(mine) == 1 and len(mine[0]['claims']) == 6, 'expected six claims on the census W4 word')
    max_first = Q(fresult['max_kappa_cap_over_covered_words'])
    best = max((Q(w['a_hi']) / (1 + Q(w['a_hi'])) for w in words.values()), default=None)
    C.require(best is not None and best < max_first + Q(1, 10 ** 12),
              'round-2 cap exceeds all first-census words (unexpected: round 2 shares the 0.87% band)')
    # ---- negative controls ----
    c = next(x for x in snap['claims'] if x['screened'])
    P = {int(r): n for r, n in c['profile'].items()}
    I = {int(r): n for r, n in c['idle'].items()}
    bad = dict(c, profile={str(r): n for r, n in {**P, '1': P.get(1, 0) - 1}.items()})
    try:
        split_and_check(bad, 'negative')
        raise SystemExit('FAIL: negative identity control did not reject')
    except ValueError:
        pass
    idle_bad = dict(c, idle={str(r): n for r, n in {**I, '1': I.get('1', 0) + P.get(1, 0) + 1}.items()})
    try:
        split_and_check(idle_bad, 'negative')
        raise SystemExit('FAIL: negative idle control did not reject')
    except ValueError:
        pass
    unscreened = [x for x in snap['claims'] if not x['screened']]
    C.require(sorted(x['pr'] for x in unscreened) == [1154, 1175, 1176],
              'unexpected unscreened set')
    for x in unscreened:
        C.require(set(x['observed_keysets']), f"#{x['pr']} no observed keysets recorded")
    # ---- result ----
    out_words = []
    for w in sorted(words.values(), key=lambda w: -w['a_hi']):
        cap = w['a_hi'] / (1 + w['a_hi'])
        out_words.append(dict(id=w['id'],
                              local_profile_per_call={str(r): str(v) for r, v in sorted(w['local'].items())},
                              local_mass_per_call=str(sum(r * v for r, v in w['local'].items())),
                              kappa_cap=dec17(cap), a_ceiling=str(w['a_hi']),
                              claims=sorted(w['claims'])))
    out = dict(status='PASS_COMPLEX_QUEUE_CEILING_CENSUS_R2', base_commit=snap['snapshot_utc'],
               claims_screened=len(rows), screened_prs=[r['pr'] for r in rows],
               distinct_local_words=len(words),
               screened_prs_uncovered_by_first_census=len(rows),
               unscreened=[dict(pr=x['pr'], head=x['head'][:12],
                                reason='no record in the claim package at its head carries a kappa '
                                       'equal to the title kappa together with a paid profile and an '
                                       'idle histogram; only vendored predecessor and variant-lineage '
                                       'records appear (kappa of other PRs, or no exact kappa at all)',
                                must_record=['global_profile (paid per-replica profile) in the same '
                                             'record as an exact kappa equal to the title kappa',
                                             'idle_remainder_profile in the same record',
                                             'live (with calls derivable: live*9 == 896*calls)'],
                                observed_keysets=x['observed_keysets'])
                           for x in unscreened],
               words=out_words, claims=sorted(rows, key=lambda r: r['pr']),
               selected_kappa=SELECTED['decimal'],
               scope='Round 2 of the queue ceiling census. Each cap bounds hosting, owner and idle '
                     'repacking of that claim\'s own local word under the coverage law, 896/9 live '
                     'families per call and the halving guard, exactly as the first census for its 14 '
                     'covered claims. It does not bound changed words, templates or outer recipes, '
                     'and does not review or accept any claim.')
    text = json.dumps(out, indent=1, sort_keys=True) + '\n'
    if sys.argv[1:] == ['--write']:
        (HERE / 'RESULT.json').write_text(text)
    else:
        C.require((HERE / 'RESULT.json').read_text() == text, 'RESULT.json differs')
    print(out['status'], f"screened={len(rows)} words={len(words)} unscreened={len(unscreened)}")


if __name__ == '__main__':
    try:
        main()
    except ValueError as e:
        print('FAIL:', e)
        sys.exit(1)

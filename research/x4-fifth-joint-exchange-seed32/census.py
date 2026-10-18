#!/usr/bin/env python3
"""Complete census of a fifth joint read-set exchange on the selected X4 word.

python3 -I -B census.py --root REPO [--mode core|full] --out RESULTS.json

Domain (defined from code, see README): every unordered pair {p1, p2} of BRoute sw4 copy pairs
with movable reads, neither among X4's eight, whose movable-read target sets intersect; every
(S1, S2) of nonempty movable-read subsets; frame policy per moved read either K (keep the stored
frame, monotone repair: span(stored + operand frames), X4's rule) or J (plain join, BRoute's rule).
mode core: policies all-K and all-J on every (S1, S2); plus every per-read K/J mask on the 28 full
exchanges. mode full: every per-read K/J mask on every (S1, S2).
A per-read K on a read that already has an explicit frame is rejected as a duplicate frame,
as build_jx does. Each candidate is applied jointly with X4's recipe edits on the SW4 word, keeping PR741's eight
explicit frames, and checked for B-segment exactness (Fraction replay), target caps, tails and ends.
Seed 32 only selects the oracle cross-check sample (build_jx.build on recipe-expressible candidates).
Apache-2.0.
"""
import argparse
import gzip
import hashlib
import io
import json
import random
import sys
import tarfile
import tempfile
import time
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import jx5  # noqa: E402

SEED = 32
FILE_PINS = {
    'build_jx': '3cc7550b0c24bb54e245c6f7f16de489fd7844721fbb64aac628f38f43887916',
    'recipe_x4': '9d42c6b38e8124f5ffe15da56c260a7fba7260626bf3c5f8cbd93aa4a71ceadd',
    'price_profile': None,  # pinned in SOURCES.json; price_profile pins its engines itself
}


def fsha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def load_word_file(p, pin):
    raw = gzip.decompress(Path(p).read_bytes())
    assert hashlib.sha256(raw).hexdigest() == pin, ('input pin', str(p))
    return json.loads(raw)


def load_x4_from_tar(p):
    with tarfile.open(p, 'r:gz') as t:
        m = t.getmember(jx5.REL['x4_member'])
        assert m.isfile() and m.size < 10 ** 7
        raw = gzip.decompress(t.extractfile(m).read())
    assert hashlib.sha256(raw).hexdigest() == jx5.PINS['x4_content'], 'X4 replay member pin'
    return json.loads(raw)


def outcome(fn):
    try:
        prof, _ = fn()
        return ('ok', prof)
    except jx5.Reject as r:
        return ('reject', r.args[0][0])


def run(root, mode, out):
    t0 = time.monotonic(); root = Path(root).resolve()
    for k in ('build_jx', 'recipe_x4'):
        assert fsha(root / jx5.REL[k]) == FILE_PINS[k], ('file pin', k)
    sw4 = load_word_file(root / jx5.REL['sw4_word'], jx5.PINS['sw4_content'])
    f741 = load_word_file(root / jx5.REL['f741_word'], jx5.PINS['f741_content'])
    x4 = load_x4_from_tar(root / jx5.REL['replay_tar'])
    rc = json.loads((root / jx5.REL['recipe_x4']).read_text())
    assert rc['input_content_sha256'] == jx5.PINS['sw4_content']
    oracle = jx5.load_build_jx(root)
    B = jx5.Builder(sw4)
    ex_all = jx5.explicit_of(rc)
    ex741 = {int(i): f for i, f in rc['frames_741']}
    ex_keys = frozenset(ex_all)
    x4moved = frozenset(x['i'] for x in rc['edits']['replace'])
    X4E = rc['edits']
    PX4 = x4['report']['local_profile']; P741 = f741['report']['local_profile']
    tmp = Path(tempfile.mkdtemp(prefix='x5price-'))
    res = dict(seed=SEED, mode=mode, controls={}, positive={}, negative={})

    # ---------------- positive controls
    prof, w = B.build(X4E, ex_all, want_word=True)
    pos = res['positive']
    pos['P1_x4_rebuilt_from_sw4'] = jx5.csha(w) == jx5.PINS['x4_content'] == jx5.csha(x4) and prof == PX4
    pos['P2_oracle_build_jx_x4'] = jx5.csha(oracle.build(sw4, rc)) == jx5.PINS['x4_content']
    pos['P3_uniform_keep_policy_equals_x4'] = B.build(X4E, ex741, keep=x4moved)[0] == PX4
    p741, w741 = B.build(jx5.merge(), ex741, want_word=True)
    pos['P4_741_rebuilt'] = jx5.csha(w741) == jx5.PINS['f741_content'] and p741 == P741
    k741 = jx5.price(root, P741, tmp, '741'); kx4 = jx5.price(root, PX4, tmp, 'x4')
    pos['P5_price_mapping_741'] = k741['kappa'] == '1661202643272239/1000000000000000000'
    pos['P6_price_mapping_x4'] = kx4['kappa'] == '1661634653669567/1000000000000000000'
    # one X4 instance re-derived from its sw4-rule definition, alone on PR741's word
    P, T, pp, allpp = jx5.domain(sw4)
    byh = {p['h']: p for p in P}
    one = jx5.merge(*[jx5.pair_edits(sw4, byh[h], byh[h]['movable'])[0] for h in (448, 472)])
    sig = lambda E: sorted(json.dumps(x, sort_keys=True) for k in E for x in [{kk: vv for kk, vv in y.items() if kk != 'why'} for y in E[k]])
    x4one = {k: [x for x in X4E[k] if x['h'] in (448, 472)] for k in X4E}
    pos['P7_instance_448_472_edits_equal_recipe'] = sig(one) == sig(x4one)
    pinst = B.build(one, ex741, keep=frozenset(x['i'] for x in one['replace']))[0]
    kinst = jx5.price(root, pinst, tmp, 'inst448')
    from fractions import Fraction as Q
    d_b = Q(kinst['complex_b']) - Q(k741['complex_b'])
    d_k = Q(kinst['kappa']) - Q(k741['kappa'])
    pos['P8_instance_profile_delta'] = {k: pinst.get(k, 0) - P741.get(k, 0) for k in sorted(set(pinst) | set(P741)) if pinst.get(k, 0) != P741.get(k, 0)} == {'1': -2, '2': 1}
    # PROOF-NOTE-FRAMES-X4 quotes the per-instance gain in kappa
    pos['P9_instance_kappa_gain_1.0798e-7'] = abs(float(d_k) - 1.0798e-7) < 5e-12
    res['instance_448_472'] = dict(profile=pinst, complex_b_gain=str(d_b), complex_b_gain_float=float(d_b), kappa_gain=str(d_k), kappa_gain_float=float(d_k))
    # domain bookkeeping agrees with the PR799 / BRoute reports
    combos = lambda L: sum((2 ** len(byh[a]['movable']) - 1) * (2 ** len(byh[b]['movable']) - 1) for a, b in L)
    nb = len(jx5.copy_pairs(sw4))
    pos['P10_domain_counts_match_reports'] = (nb, len(P), len(allpp), combos(allpp)) == (107, 54, 40, 5880)
    res['domain'] = dict(copy_pairs=nb, pairs_with_movable_reads=len(P), target_sharing_pair_pairs_total=len(allpp),
                         subset_combinations_total=combos(allpp),
                         pair_pairs_with_an_x4_pair=len(allpp) - len(pp),
                         pair_pairs_after_x4=len(pp), subset_combinations_after_x4=combos([(a['h'], b['h']) for a, b in pp]),
                         pair_pairs=[[a['h'], a['r'], b['h'], b['r'], sorted(T[a['h']] & T[b['h']])] for a, b in pp])

    # ---------------- negative controls (on the first domain pair-pair, full exchange)
    a0, b0 = pp[0]
    e0 = jx5.merge(jx5.pair_edits(sw4, a0, a0['movable'])[0], jx5.pair_edits(sw4, b0, b0['movable'])[0])
    neg = res['negative']
    def mut(E, f):
        E = json.loads(json.dumps(E)); f(E); return E
    drop_ins = mut(e0, lambda E: E['insert'].pop(0))
    flip = mut(e0, lambda E: E['insert'][0]['gate'].__setitem__(3, -E['insert'][0]['gate'][3]))
    drop_del = mut(e0, lambda E: E['delete'].pop(0))
    neg['N1_dropped_preread_rejected'] = bool(B.exact(jx5.merge(X4E, drop_ins)))
    neg['N2_wrong_sign_preread_rejected'] = bool(B.exact(jx5.merge(X4E, flip)))
    neg['N3_kept_h_preread_rejected'] = bool(B.exact(jx5.merge(X4E, drop_del)))
    neg['N4_x4_recipe_N1_pinned_rows'] = B.exact(jx5.merge({**X4E, 'insert': X4E['insert'][1:]})) == [132, 135]
    neg['N5_x4_recipe_N4_cap_pinned'] = outcome(lambda: B.build(X4E, {**ex_all, 855: [280, 128, 64, 40, 4, 2, 1]})) == ('reject', 'cap')
    bad = json.loads(json.dumps(X4E)); bad['replace'][0]['old'][3] = 1
    neg['N6_stale_old_gate_rejected'] = outcome(lambda: B.build(bad, ex_all)) == ('reject', 'replace old mismatch')
    tw = json.loads(json.dumps(sw4)); tw['B'][0][3] = 3
    neg['N7_tampered_input_pin_rejected'] = jx5.csha(tw) != jx5.PINS['sw4_content']
    neg['N8_frame_tamper_profile_changes'] = B.build(X4E, ex741)[0] != PX4   # plain join refit (X4's N3) differs

    # ---------------- census
    rows = []; ex_fail = 0; t1 = time.monotonic(); nb_build = 0
    rng = random.Random(SEED)
    for a, b in pp:
        for S1 in jx5.subsets(a['movable']):
            for S2 in jx5.subsets(b['movable']):
                e1, p1 = jx5.pair_edits(sw4, a, S1); e2, p2 = jx5.pair_edits(sw4, b, S2)
                key = [a['h'], b['h'], S1, S2]
                if p1 or p2:
                    rows.append(dict(c=key, x='rule', why=list(p1 or p2))); continue
                E = jx5.merge(X4E, e1, e2)
                idx = [x['i'] for k in ('replace', 'delete') for x in E[k]]
                assert len(idx) == len(set(idx)), 'edit overlap with X4'
                badrows = B.exact(E)
                moved = sorted(x['i'] for x in e1['replace'] + e2['replace'])
                full = len(S1) == len(a['movable']) and len(S2) == len(b['movable'])
                if mode == 'full' or full:
                    masks = range(1 << len(moved))
                else:
                    masks = [(1 << len(moved)) - 1, 0]
                for m in masks:
                    keep = frozenset(moved[j] for j in range(len(moved)) if m >> j & 1)
                    relaxed = False
                    if keep & ex_keys:
                        # a kept read that already carries an explicit frame is the same build as the
                        # unkept one; build_jx rejects the recipe as a duplicate frame
                        o = ('reject', 'duplicate frame')
                    elif badrows:
                        o = ('reject', 'exactness rows'); ex_fail += 1
                    else:
                        # X4 exactly as its recipe (PR741 frames and X4 raises explicit, equality required)
                        o = outcome(lambda: B.build(E, ex_all, keep=keep, check_exact=False)); nb_build += 1
                        if o == ('reject', 'explicit frame below join'):
                            # relaxed: every explicit frame and every X4 moved read retained with monotone repair
                            o = outcome(lambda: B.build(E, {}, keep=keep | x4moved, soft=ex_all, check_exact=False))
                            relaxed = True; nb_build += 1
                    rows.append(dict(c=key, full=full, mask=m, n=len(moved), o=o[0], v=o[1], relaxed=relaxed))
        print('pair-pair', a['h'], b['h'], 'rows', len(rows), 'elapsed %.0fs' % (time.monotonic() - t1), file=sys.stderr, flush=True)
    res['census_seconds'] = round(time.monotonic() - t1, 1)

    # ---------------- aggregate and price
    legal = [r for r in rows if r.get('o') == 'ok']
    rej = Counter(r['v'] if r.get('o') == 'reject' else r.get('x') for r in rows if r.get('o') != 'ok')
    profs = sorted({json.dumps(r['v'], sort_keys=True) for r in legal})
    priced = {}
    for i, ps in enumerate(profs):
        priced[ps] = jx5.price(root, json.loads(ps), tmp, 'c%d' % i)
    KX4 = Q(kx4['kappa'])
    better = [r for r in legal if Q(priced[json.dumps(r['v'], sort_keys=True)]['kappa']) > KX4]
    neutral = [r for r in legal if r['v'] == PX4]
    eqk = [r for r in legal if Q(priced[json.dumps(r['v'], sort_keys=True)]['kappa']) == KX4]
    res['census'] = dict(rows=len(rows), frame_policy_builds=nb_build, exactness_rejections=ex_fail,
                         legal=len(legal), legal_relaxed=sum(1 for r in legal if r['relaxed']), rejections=dict(sorted(rej.items())),
                         legal_full_exchanges=sum(1 for r in legal if r['full']),
                         distinct_legal_profiles=len(profs),
                         kappa_improving=len(better), profile_neutral=len(neutral), kappa_equal=len(eqk),
                         legal_by_pair_pair=dict(sorted(Counter('%d-%d' % (r['c'][0], r['c'][1]) for r in legal).items())))
    res['profiles'] = [dict(profile=json.loads(ps), count=sum(1 for r in legal if json.dumps(r['v'], sort_keys=True) == ps),
                            kappa=priced[ps]['kappa'], kappa_decimal=priced[ps]['kappa_decimal'],
                            delta_vs_x4=str(Q(priced[ps]['kappa']) - KX4), sign=(Q(priced[ps]['kappa']) > KX4) - (Q(priced[ps]['kappa']) < KX4))
                       for ps in profs]
    res['legal_candidates'] = [dict(c=r['c'], mask=r['mask'], full=r['full'], relaxed=r['relaxed'], profile=r['v']) for r in legal]
    res['best_legal'] = max(res['profiles'], key=lambda d: Q(d['kappa'])) if profs else None

    # ---------------- pairs of neutral-or-better candidates (bounded)
    pool = [r for r in legal if Q(priced[json.dumps(r['v'], sort_keys=True)]['kappa']) >= KX4]
    combos2 = []
    for i in range(len(pool)):
        for j in range(i + 1, len(pool)):
            r1, r2 = pool[i], pool[j]
            if {r1['c'][0], r1['c'][1]} & {r2['c'][0], r2['c'][1]}: continue
            combos2.append((r1, r2))
    CAP = 20000
    if len(combos2) > CAP: combos2 = rng.sample(combos2, CAP)
    c2 = Counter(); c2best = None
    for r1, r2 in combos2:
        es, keep = [X4E], set(x4moved)
        for r in (r1, r2):
            a, b = byh[r['c'][0]], byh[r['c'][1]]
            e1 = jx5.pair_edits(sw4, a, r['c'][2])[0]; e2 = jx5.pair_edits(sw4, b, r['c'][3])[0]
            mv = sorted(x['i'] for x in e1['replace'] + e2['replace'])
            keep |= {mv[j] for j in range(len(mv)) if r['mask'] >> j & 1}; es += [e1, e2]
        E = jx5.merge(*es)
        keep -= x4moved
        o = ('reject', 'exactness rows') if B.exact(E) else outcome(lambda: B.build(E, ex_all, keep=frozenset(keep), check_exact=False))
        if o == ('reject', 'explicit frame below join'):
            o = outcome(lambda: B.build(E, {}, keep=frozenset(keep) | x4moved, soft=ex_all, check_exact=False))
        c2[o[0] if o[0] == 'reject' else ('better' if o[1] != PX4 and Q(jx5.price(root, o[1], tmp, 'pair')['kappa']) > KX4 else 'not_better')] += 1
    res['pairs_of_candidates'] = dict(pool=len(pool), evaluated=len(combos2), cap=CAP, outcomes=dict(c2))

    # ---------------- oracle cross-check (seeded sample, build_jx.build on expressible candidates)
    sample = rng.sample(rows, min(48, len(rows))); agree = 0; expressible = 0; disagree = []
    for r in sample:
        if 'mask' not in r or r['relaxed']: continue
        a, b = byh[r['c'][0]], byh[r['c'][1]]
        e1 = jx5.pair_edits(sw4, a, r['c'][2])[0]; e2 = jx5.pair_edits(sw4, b, r['c'][3])[0]
        rc2 = json.loads(json.dumps(rc)); rc2['edits'] = jx5.merge(X4E, e1, e2)
        mv = sorted(x['i'] for x in e1['replace'] + e2['replace'])
        # every kept read becomes a raise, so build_jx sees the same duplicate frames the census rejects
        rc2['raises'] = rc['raises'] + [[mv[j], list(sw4['B'][mv[j]][-1])] for j in range(len(mv)) if r['mask'] >> j & 1]
        try:
            o = ('ok', oracle.build(sw4, rc2)['report']['local_profile'])
        except oracle.Reject as e:
            o = ('reject', e.args[0][0])
        if o == ('reject', 'explicit frame below join') and r['o'] == 'ok': continue
        # the two builders test rejection causes in different orders; compare verdict and profile only
        expressible += 1
        same = o[0] == r['o'] and (o[0] == 'reject' or o[1] == r['v'])
        agree += same
        if not same: disagree.append(dict(c=r['c'], mask=r['mask'], census=[r['o'], r['v']], oracle=list(o)))
    res['oracle'] = dict(sample=len(sample), expressible=expressible, agree=agree, disagree=disagree)
    pos['P11_oracle_agrees'] = expressible > 0 and agree == expressible
    res['seconds'] = round(time.monotonic() - t0, 1)
    res['x4'] = dict(profile=PX4, kappa=kx4['kappa']); res['f741'] = dict(profile=P741, kappa=k741['kappa'])
    ok = all(pos.values()) and all(neg.values())
    res['status'] = ('PASS_X4_FIFTH_JOINT_EXCHANGE_CENSUS' if ok else 'FAIL')
    if out:
        Path(out).write_text(json.dumps(res, indent=1, sort_keys=True) + '\n')
    return res


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root', default=str(HERE.parent.parent))
    ap.add_argument('--mode', choices=('core', 'full'), default='core')
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    r = run(a.root, a.mode, a.out)
    c = r['census']
    print(r['status'], 'mode=%s' % r['mode'], 'rows=%d' % c['rows'], 'legal=%d' % c['legal'],
          'improving=%d' % c['kappa_improving'], 'seconds=%.0f' % r['seconds'])


if __name__ == '__main__':
    main()

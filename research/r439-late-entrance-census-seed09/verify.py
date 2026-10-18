#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Scoped census: late-compensated helper entrances on the R439 bit word (no new kappa).

Usage: python3 -I -B research/r439-late-entrance-census-seed09/verify.py [--write]

The inherited H2/K implication says every helper starts at frame 0 so that a frame-0 prefix D can supply all dirt
compensation. #1128 (PROOF section 4) leaves 'compensation moved after A' open and #1179 states that K e_J = 0 is not
about arbitrary later compensation. This script asks, for every support J of a common-frame entrance (#1253's 366
classes, 4,954 supports) on the selected PR589 word and the four merged star words, whether the entrance can be
compensated after the scatter instead:

  B  byte binding of the five words, #1253's certificate and the replay library (sha256 pins);
  E1 Engine 1 (census.py): raw replay and K, first contacts, the closure L and I(V), and per target t the dirt-only
     space W_t in three classes: LC-fav (the necessary test, PROOF.md theorem), the scout prototype's strict class,
     and A6 (fixed raw paths, inserted target reads with a carrier check, read-only relays); the parity census of
     every support, the sound linear relaxation per class, and source-donor entrances;
  E2 Engine 2 (engine2.py, no shared code): set-valued replay and K, rational-annihilator geometry, the closure
     (also equal to #1253's certificate), W_t for LC-fav (kernel method) and A6 (per-pair change points); exact
     agreement of every W_t and every verdict;
  R  A6R (A6 plus frame-tagged storage relays, restoration ignored) for the only late LC-fav survivor;
  C  controls: a synthetic word whose built late witness replays (and fails without its late reads), K / frame
     mutations that flip verdicts, frame closure, a flipped byte; plus sanity checks of the census (pre-A window,
     the #1179 kernel pair, a cleared K column) and of the relaxation (a superset of every admission).

Expected last line: PASS_R439_LATE_ENTRANCE_CENSUS
"""
import argparse
import copy
import gzip
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import census as E  # noqa: E402
import engine2 as F  # noqa: E402

WORDS = {
    'PR589': ('research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz',
              'e3e301e62bc2b41dbf1ceac0acf3d35824ebeab1848c5a2142d4577b109da52f'),
    'PR1062': ('research/r439-bsection-stars-seed01/candidate.json.gz',
               'b452d2c2b0b2a546d1105b1da9769aa78e5c54d6f00e97b30c77e3f54ce445ee'),
    'PR1122': ('research/r439-abc-semantic-bridge/inputs/candidate.json.gz',
               '2b09a7a3851cdf2a7f19350d1555cf75788d001c9507a37e459cd931881ee066'),
    'PR1188': ('research/r439-gl5-shortest/candidate.json.gz',
               '4e7904d01ebdbfc60a26472b4e0d2e813c19c2fe1a4bb8ab390c12746a1da359'),
    'PR1208': ('research/r439-abc-zrewrite-seed16/CANDIDATE-WORD.json',
               '66b34404f39f5f612c2aaadd53ae33eb9f5993ec2065c82e23d7467cce03a226'),
}
CERT_1253 = ('research/r439-kernel-entrance-closure/CERTIFICATE.json',
             'f08b9de12089687fe6c0c6b2eb985d0e6a883b72fa4f08ded11d34d875f48909')
WLIB = ('research/e8-bit-p111-tuned/tune/wlib.py', 'a37fdf3cdf5f62945c2a90193401c0e9edc9dd3cda8d8cb36a3b9c329ebe4dbc')
SYN_SHA = 'a33bf677cb43b26f27e18bf29b5618ded5a17d04987ddb71d8ce4f2de4401ea1'
WITNESS_SHA = 'cf7aa7a94141fd18623e0ce489f67d86c725f17ec0856bbc23b4700d66c5d00a'
KERNEL_PAIR = (444, 470)
TRIPLE = (444, 470, 578)


class Reject(Exception):
    """A check failed; the argument is the label of the check."""


def need(ok, label):
    if not ok:
        raise Reject(label)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def canonical_sha(w):
    return sha(json.dumps(w, sort_keys=True, separators=(',', ':')).encode())


def load_word(path, digest, raw=None):
    raw = (ROOT / path).read_bytes() if raw is None else raw
    need(sha(raw) == digest, 'B word digest: ' + path)
    try:
        data = gzip.decompress(raw) if raw[:2] == b'\x1f\x8b' else raw
    except OSError:
        raise Reject('B word does not decompress: ' + path)
    try:
        w = json.loads(data)
    except ValueError:
        raise Reject('B word is not JSON: ' + path)
    need(w.get('format') == 'bitE8/1+mut' and w.get('h') == 8 and w.get('form') == '<x,y>/2', 'B word header: ' + path)
    return w


def load_wlib():
    path, digest = WLIB
    need(sha((ROOT / path).read_bytes()) == digest, 'B replay library digest')
    sys.path.insert(0, str((ROOT / path).parent))
    import wlib
    return wlib


def regs(c):
    return [list(x) for x in c]


# ------------------------------------------------------------------------------------------------ one word
def analyse(name, w, cert_classes, run_a6r=True):
    W = E.Word(w)
    st = W.raw()
    K = st['K']
    first = W.first_contact()
    cl = E.closure(W, first)
    sup = E.supports(cl['elig'])
    full = next(i for i, f in enumerate(w['frames']) if len(f) == W.v)
    # A6 inserts reads anywhere in B ++ C; the sweeps stop at the end of B. C is entirely at FULL and touches no target,
    # and no target ends at FULL, so a read during C sees the end-of-B value and the same legality as at tau = |B|.
    need(all(g[0] == full for g in w['C']) and not any(W.v <= r < 2 * W.v for g in w['C'] for r in (g[1], *g[2]))
         and all(w['final'][W.v + t] != full for t in range(W.v)), 'E1 reads during C reduce to the end of B')
    Wf, Wfs = E.W_fav(W, st), E.W_sweep(W, st, 'fav')
    Wstrict, Wa = E.W_sweep(W, st, 'strict'), E.W_sweep(W, st, 'A6')
    need(all(E.canonical(a) == E.canonical(b) for a, b in zip(Wf, Wfs)), 'E1 LC-fav at sigma = union over the sweep')
    need(all(E.canonical(a) == E.canonical(b) for a, b in zip(Wf, E.W_fav(W, st, y_free=False))), 'E1 y-free = y-zero')
    # the classes are nested: A6 inside LC-fav
    need(all(F.same_span(list(a) + list(b), list(b)) for a, b in zip(Wa, Wf)), 'E1 A6 spans inside LC-fav spans')
    res = {}
    for cls, X in (('LC_fav', Wf), ('strict_proto', Wstrict), ('A6', Wa)):
        adm = E.census(W, K, X, sup)
        coord = all(all(bin(u).count('1') == 1 for u in E.canonical(x)) for x in X)
        res[cls] = dict(admitted=[[list(s), nT] for s, nT in adm], covered_K_incidences=E.coverage(W, K, X), dim_W=E.dims(X),
                        coordinate_subspaces=coord)
    for cls, X in (('LC_fav', Wf), ('A6', Wa)):
        rel = E.relax(W, K, X, cl['elig'])
        res[cls]['relax366'] = [dict(dim_V=len(V), kernel=regs(d['kernel']), rows_kept=d['rows_kept']) for V, d in
                                sorted(rel.items(), key=lambda kv: (len(kv[0]), kv[0]))]
        # the relaxation is a superset: every admitted support lies in the relaxed kernel of some class containing it
        for S, _ in E.census(W, K, X, sup):
            cmS = sum(1 << (r - 2 * W.v) for r in S)
            ok = False
            for V, I in cl['elig'].items():
                if set(S) <= set(I) and V in rel:
                    span = E.Span()
                    for kv in rel[V]['kernel']:
                        span.add(sum(1 << (r - 2 * W.v) for r in kv))
                    ok = ok or not span.add(cmS)
            need(ok, 'E1 relaxation contains every admitted support: ' + cls)
        don = E.donors(W, K, X, cl['elig'])
        res[cls]['source_donors'] = dict(enumerated=don['checked'], placeable=don['placeable'], kernel=len(don['kernel']),
                                         late=len(don['late']))
    # Engine 2
    rep = F.replay_sets(w)
    geo = F.Geometry(w)
    need(rep['K'] == K, 'E2 K agrees')
    need(F.first_contact(w) == first, 'E2 first contacts agree')
    classes = F.closure_classes(w, first)
    need(sorted(map(tuple, classes.values())) == sorted(map(tuple, cl['elig'].values())), 'E2 closure agrees')
    need(sorted(map(tuple, classes.values())) == cert_classes, 'E2 closure = #1253 certificate')
    Wf2, Wa2 = F.W_fav(w, rep, geo), F.W_A6(w, rep, geo)
    need(all(F.same_span(a, b) for a, b in zip(Wf, Wf2)), 'E2 LC-fav spans agree')
    need(all(F.same_span(a, b) for a, b in zip(Wa, Wa2)), 'E2 A6 spans agree')
    for cls, X in (('LC_fav', Wf2), ('A6', Wa2)):
        adm2, nsup = F.admitted(K, X, classes, w['v'])
        need(nsup == len(sup) and [[list(s), nT] for s, nT in adm2] == res[cls]['admitted'], 'E2 verdicts agree: ' + cls)
    need(all(geo.closed(f, w['v']) == w['frames'][f] for f in range(len(w['frames']))), 'E2 every frame is closed')
    # A6R for the late LC-fav survivors
    late = [tuple(s) for s, nT in res['LC_fav']['admitted'] if nT > 0]
    survivors = {}
    for J in late:
        cm = sum(1 << (r - 2 * W.v) for r in J)
        T = [W.v + t for t in E.response(K, cm)]
        entry = dict(T=T)
        if run_a6r:
            full = set(E.a6r_coverable(W, st, J))
            tonly = set(E.a6r_coverable(W, st, J, only_targets=set(T)))
            plain = set(E.a6r_coverable(W, st, J, relays=False))
            entry.update(A6_covered=sorted(set(T) & plain), A6R_covered=sorted(set(T) & full),
                         A6R_T_only_covered=sorted(set(T) & tonly))
        survivors[','.join(map(str, J))] = entry
    dv = [1 << r for r in range(W.n)]
    for f, d, ss in w['D']:
        a = 0
        for s in ss:
            a ^= dv[s]
        dv[d] ^= a
    N = [(dv[W.v + t] >> (2 * W.v)) & ((1 << W.R) - 1) for t in range(W.v)]
    colw = [sum((K[t] >> j) & 1 for t in range(W.v)) for j in range(W.R)]
    return dict(gates={k: len(w[k]) for k in 'DABC'}, K_nonzeros=sum(colw), K_column_weights=[min(colw), max(colw)],
                N_equals_K=N == K, closure=dict(size=len(cl['L']), plane_pairs=cl['plane_pairs'], meeting_pairs=cl['meets'],
                                                supports=len(sup)),
                classes=res, late_survivors=survivors,
                engines_agree=True), (W, st, K, cl, sup, Wf, Wa)


# ------------------------------------------------------------------------------------------------ controls
def synthetic(P):
    """W_syn: three inserted target reads make the {444,470} entrance late-compensable at target 150; the witness
    realises it (start[444] = 79, shear at the head of A, its inverse at the end of C, D without 444)."""
    S = copy.deepcopy(P)
    S['B'] = [[0, 150, [149]]] + P['B'][:37] + [[323, 150, [149]], [323, 150, [470]]] + P['B'][37:]
    S['D'] = [[f, d, [s for s in ss if not (d == 150 and s == 470)]] for f, d, ss in P['D']]
    Wt = copy.deepcopy(S)
    Wt['start'][444] = 79
    Wt['A'] = [[79, 470, [444]]] + S['A']
    Wt['B'] = [[0, 150, [149]]] + S['B'][:38] + [[323, 150, [149]], [323, 150, [470]]] + S['B'][38:]
    Wt['C'] = S['C'] + [[1, 470, [444]]]
    Wt['D'] = [[f, d, [s for s in ss if s != 444]] for f, d, ss in P['D']]
    return S, Wt


def controls(P, ctx, wlib):
    W, st, K, cl, sup, Wf, Wa = ctx
    v = W.v
    out = {}
    # (a) pre-A window: every helper readable at frame 0 before A -> every support admitted
    allj = [1 << j for j in range(W.R)]
    pre = [list(x) + allj for x in Wf]
    n_pre = len(E.census(W, K, pre, sup))
    need(n_pre == len(sup), 'C pre-A window admits every support')
    out['sanity_pre_A_window'] = 'with every unit vector added to every W_t, %d/%d supports are admitted' % (n_pre, len(sup))
    # (b) the #1179 kernel pair: T empty, admitted by every class
    cm = sum(1 << (r - 2 * v) for r in KERNEL_PAIR)
    need(not E.response(K, cm), 'C kernel pair has T empty')
    out['sanity_kernel_pair'] = '444+470: K e_J = 0 (the #1179 entrance), so admitted in every class'
    # (c) synthetic word with a built witness
    S, Wt = synthetic(P)
    need(canonical_sha(S) == SYN_SHA and canonical_sha(Wt) == WITNESS_SHA, 'C synthetic words reproduce their digests')
    wlib.replay(S)
    wlib.replay(Wt)
    late_only = copy.deepcopy(Wt)
    late_only['B'] = S['B']                          # the witness without its three post-scatter reads
    try:
        wlib.replay(late_only)
        need(False, 'C witness without its late reads must fail replay')
    except AssertionError as exc:
        need(exc.args and exc.args[0] == 150, 'C witness without its late reads fails at register 150')
    Sneg = copy.deepcopy(S)
    Sneg['D'] = P['D']
    try:
        wlib.replay(Sneg)
        need(False, 'C synthetic negative must fail replay')
    except AssertionError as exc:
        need(exc.args and exc.args[0] == 150, 'C synthetic negative fails at register 150')
    SW = E.Word(S)
    sst = SW.raw()
    sK = sst['K']
    sfirst = SW.first_contact()
    ssup = E.supports(E.closure(SW, sfirst)['elig'])
    syn_fav = E.census(SW, sK, E.W_fav(SW, sst), ssup)
    syn_a6 = E.census(SW, sK, E.W_sweep(SW, sst, 'A6'), ssup)
    T_syn = [v + t for t in E.response(sK, cm)]
    need(T_syn == [150] and (KERNEL_PAIR, 1) in syn_fav and (KERNEL_PAIR, 1) in syn_a6, 'C synthetic: 444+470 late at 150, admitted')
    out['synthetic'] = dict(word_sha256=SYN_SHA, witness_sha256=WITNESS_SHA, kernel_pair_T=T_syn,
                            admitted_LC_fav=[[list(s), nT] for s, nT in syn_fav], admitted_A6=[[list(s), nT] for s, nT in syn_a6],
                            witness_replay='PASS', witness_paid=wlib.paid(Wt), synthetic_paid=wlib.paid(S),
                            witness_without_late_reads='fails replay at register 150',
                            negative='W_syn with the unedited D fails replay at register 150',
                            note='the late reads undo W_syn\'s own moved compensation, so after B the witness carries the same '
                                 'values as #1179\'s prefix entrance on PR589: a realisable late entrance, not a new construction')
    # (d) mutations flip verdicts
    Kf = list(K)
    Kf[1] ^= 1 << (470 - 2 * v)
    need(not any(s == KERNEL_PAIR for s, _ in E.census(W, Kf, Wf, [frozenset(KERNEL_PAIR)])), 'C flipped K bit rejects 444+470')
    K0 = [x & ~(1 << (578 - 2 * v)) for x in K]
    need(((578,), 0) in E.census(W, K0, Wf, [frozenset((578,))]), 'C zero K column admits 578 (sanity: T empty)')
    full = next(i for i, f in enumerate(P['frames']) if len(f) == v)
    Wrel = E.W_sweep(W, st, 'A6', next_override={77: full})
    trip = E.census(W, K, Wrel, [frozenset(TRIPLE)])
    need(trip == [(TRIPLE, 8)], 'C relaxing next_77 to FULL admits the triple in A6')
    out['mutations'] = dict(flip_K_bit='444+470 rejected after flipping K[target 112, helper 470]',
                            sanity_zero_K_column='578 admitted (T empty) after clearing column 578',
                            relax_next_77='444+470+578 admitted by A6 when register 77 may be read at FULL')
    # (e) closure: dropping a label from a closed frame breaks closure
    bad = copy.deepcopy(P)
    f = next(i for i, fr in enumerate(bad['frames']) if len(fr) >= 3)
    bad['frames'][f] = bad['frames'][f][1:]
    need(F.Geometry(bad).closed(f, v) != bad['frames'][f], 'C a frame with a dropped label is not closed')
    out['frame_closure'] = 'all frames closed (label inclusion = rational containment); a dropped label is detected'
    path, digest = WORDS['PR589']
    raw = bytearray((ROOT / path).read_bytes())
    raw[100] ^= 1
    try:
        load_word(path, digest, bytes(raw))
        need(False, 'C a flipped word byte must be rejected')
    except Reject as exc:
        need(str(exc).startswith('B word digest'), 'C a flipped word byte is rejected by its digest')
    out['flipped_byte'] = 'rejected by the word digest'
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    ap.add_argument('--write', action='store_true')
    ap.add_argument('--no-a6r', action='store_true', help='skip the slow A6R runs (partial)')
    a = ap.parse_args()
    cert_raw = (ROOT / CERT_1253[0]).read_bytes()
    need(sha(cert_raw) == CERT_1253[1], 'B #1253 certificate digest')
    cert = sorted(tuple(c['eligible_helpers']) for c in json.loads(cert_raw)['classification']['classes'])
    wlib = load_wlib()
    words = {name: load_word(*pin) for name, pin in WORDS.items()}
    results, ctx = {}, None
    for name, w in words.items():
        results[name], c = analyse(name, w, cert, run_a6r=not a.no_a6r)
        print('%-7s LC-fav %s  A6 %s' % (name, results[name]['classes']['LC_fav']['admitted'], results[name]['classes']['A6']['admitted']))
        if name == 'PR589':
            ctx = c
    first = json.dumps(results['PR589']['classes'], sort_keys=True)
    same = {name: json.dumps(r['classes'], sort_keys=True) == first and r['late_survivors'] == results['PR589']['late_survivors']
            for name, r in results.items()}
    need(all(same.values()), 'all five words give the same census')
    ctrl = controls(words['PR589'], ctx, wlib)
    lc = results['PR589']['classes']
    a6r = results['PR589']['late_survivors'].get(','.join(map(str, TRIPLE)), {})
    need(a.no_a6r or {'A6_covered', 'A6R_covered', 'A6R_T_only_covered'} <= set(a6r), 'R A6R computed for the triple')
    summary = dict(
        supports=results['PR589']['closure']['supports'],
        singles_admitted=sum(1 for s, _ in lc['LC_fav']['admitted'] if len(s) == 1),
        new_pairs_admitted=sum(1 for s, nT in lc['LC_fav']['admitted'] if len(s) == 2 and nT > 0),
        LC_fav_late=[s for s, nT in lc['LC_fav']['admitted'] if nT > 0],
        A6_late=[s for s, nT in lc['A6']['admitted'] if nT > 0],
        source_donors_late=lc['LC_fav']['source_donors']['late'],
        triple_status=('NOT_COMPUTED' if 'A6R_covered' not in a6r else
                       'OPEN' if a6r['A6R_covered'] == a6r['T'] else 'EXCLUDED_IN_A6R'))
    result = dict(status='PASS_R439_LATE_ENTRANCE_CENSUS', summary=summary, words=results, controls=ctrl,
                  inputs={k: dict(path=p, sha256=d) for k, (p, d) in WORDS.items()},
                  certificate_1253=dict(path=CERT_1253[0], sha256=CERT_1253[1]),
                  scope='Scoped census: late (post-scatter) compensation of single common-frame entrances on fixed A/scatter; '
                        'no change to A or the scatter, no pre-scatter wires, one entrance at a time; no construction and no new kappa')
    text = json.dumps(result, indent=1, sort_keys=True) + '\n'
    target = HERE / 'RESULT.json'
    if a.no_a6r:
        print('PARTIAL (no A6R)')
        return
    if a.write:
        target.write_text(text)
    else:
        need(target.read_text() == text, 'RESULT.json reproduced byte for byte')
    print('summary', json.dumps(summary, sort_keys=True))
    print('PASS_R439_LATE_ENTRANCE_CENSUS')


if __name__ == '__main__':
    try:
        main()
    except Reject as exc:
        raise SystemExit('FAIL ' + str(exc))

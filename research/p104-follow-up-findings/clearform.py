#!/usr/bin/env python3
"""CLEARFORM checker: every owned CLEAR of an endpoint-exact word is lossless (Rank lemma), with exact certificates.

Own code (DreamingOfClouds with Claude Opus 5.5), standard library only. Data only is read from other authors:
  data/base-7605-word.json.gz  aliromman's #7605 word (bytes vendored by #7608, sha256 pinned below)
  data/edits-7608.json         our #7608 edit list (main 902 skips chart 595)
  research/p104-6372-clear-form-gap/inputs/candidate-WORD.json.gz  pinned candidate of the clear-form-gap package (data only)

Checks
  1. #7608 word = #7605 + edit list (every deleted event matches).  Exact Fraction replay of both words.
  2. CLEAR #44 (owned 1557, chart 595): the #7608 row {451:-1, 1495:1} and the #7605 row {451:-1, 902:-3/2, 985:-3/2, 1495:1}
     are exact Q-combinations of the other live rows (21 and 23 terms); the two certificates differ by exactly -3/2(x902 + x985).
  3. All 74 owned CLEARs (73 dirty) of both words are lossless: the final public rows have rank 1501 = n_pub, and by the
     Rank lemma (PROOF 1.1) the live rank never rises, so no CLEAR lowered it.  73 of the 74 erased rows are identical in
     the two words; only CLEAR #44 differs.
  4. Swarm question Q1 (clear-form-gap): CLEARs 17755 and 17756 of the pinned candidate are lossless (other live rank 770 = n_pub),
     with exact certificates.
  Controls: a 3-register toy whose CLEAR is lossy is detected; a prepended COPY/zero/CLEAR of token 0 through owned 1557 makes a real-word CLEAR lossy
  (other live rank 1500, endpoint rank 1500) and is detected; a corrupted certificate coefficient is rejected.
Prints PASS_CLEARFORM.
"""
import gzip, hashlib, json, os, sys
from fractions import Fraction as Q

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
P = (1 << 61) - 1
PINS = {
    'data/base-7605-word.json.gz': '37358c493d18ebc6be386aebb4c17529b38883674731f7009ef4e96a5313467d',
    'data/edits-7608.json': '21516f556cfc8dca1e9a6938aca6a6e9453f7c7b8691324efdb634636343ff0a',
}
GAP = 'research/p104-6372-clear-form-gap/inputs/candidate-WORD.json.gz'
GAP_SHA = None  # filled from SOURCES.json at run time


def fail(msg):
    print('FAIL:', msg); sys.exit(1)


def expect(name, got, want):
    ok = got == want
    print(('ok   ' if ok else 'FAIL ') + name + ': ' + str(got))
    if not ok:
        fail('%s: got %r want %r' % (name, got, want))


def raw(path, sha):
    b = open(path, 'rb').read()
    h = hashlib.sha256(b).hexdigest()
    if sha is not None and h != sha:
        fail('sha256 mismatch for %s: %s' % (path, h))
    return b


def load_gz(b): return json.loads(gzip.decompress(b))


def apply_edits(program, E):
    if len(program) != E['base_events']: fail('edit list base length')
    dele = {}
    for i, ev in E['delete']:
        if program[i] != ev: fail('deleted event %d does not match' % i)
        dele[i] = ev
    ins = {}
    for i, evs in E['insert_before']: ins.setdefault(i, []).extend(evs)
    out = []
    for i, ev in enumerate(program):
        out.extend(ins.get(i, []))
        if i not in dele: out.append(ev)
    out.extend(ins.get(len(program), []))
    return out + E['append']


def replay(W, program=None, want=()):
    """Exact replay of the scalar projection. Returns (final rows, clears=[(event, field, erased row, others-snapshot)]).
    The snapshot of the other live rows is taken only for CLEAR events listed in `want` (else None)."""
    prog = W['program'] if program is None else program
    n = W['public']
    rows = [{r: Q(1)} if r < n else {} for r in range(n + W['owned_fields'])]
    live = set(range(n)); clears = []
    for i, e in enumerate(prog):
        op, r = e[0], e[1]
        if op == 'INIT':
            if rows[r] or r in live: fail('INIT on live field')
            live.add(r)
        elif op == 'CLEAR':
            snap = {k: dict(rows[k]) for k in live if k != r} if i in want else None
            clears.append((i, r, dict(rows[r]), snap))
            rows[r] = {}; live.discard(r)
        elif op == 'SCALE':
            c = Q(e[2])
            if c == 0: fail('zero SCALE')
            rows[r] = {k: v * c for k, v in rows[r].items()}
        elif op in ('ADD', 'COPY'):
            if op == 'COPY' and rows[r]: fail('COPY into nonzero field')
            c = Q(e[3]); R = rows[r]
            for k, v in list(rows[e[2]].items()):
                nv = R.get(k, 0) + c * v
                if nv: R[k] = nv
                else: R.pop(k, None)
        elif op != 'MOVE':
            fail('unknown op ' + str(op))
    return rows, clears


def modp(x): return x.numerator % P * pow(x.denominator % P, P - 2, P) % P


def echelon(vecs):
    """mod-p echelon with combination tracking; returns pivots {col: (row, combo)}."""
    piv = {}
    for idx, v in enumerate(vecs):
        w = {k: modp(c) for k, c in v.items()}; w = {k: a for k, a in w.items() if a}; combo = {idx: 1}
        while w:
            c = min(w)
            if c not in piv: break
            pr, pc = piv[c]; f = w[c]
            for k, a in pr.items():
                t = (w.get(k, 0) - f * a) % P
                if t: w[k] = t
                else: w.pop(k, None)
            for k, a in pc.items():
                t = (combo.get(k, 0) - f * a) % P
                if t: combo[k] = t
                else: combo.pop(k, None)
        if w:
            c = min(w); inv = pow(w[c], P - 2, P)
            piv[c] = ({k: a * inv % P for k, a in w.items()}, {k: a * inv % P for k, a in combo.items()})
    return piv


def member(piv, target):
    w = {k: modp(c) for k, c in target.items()}; w = {k: a for k, a in w.items() if a}; combo = {}
    while w:
        c = min(w)
        if c not in piv: return None
        pr, pc = piv[c]; f = w[c]
        for k, a in pr.items():
            t = (w.get(k, 0) - f * a) % P
            if t: w[k] = t
            else: w.pop(k, None)
        for k, a in pc.items():
            combo[k] = (combo.get(k, 0) + f * a) % P
    return {k: a for k, a in combo.items() if a}


def ratrec(a):
    r0, r1, s0, s1 = P, a, 0, 1
    B = int((P // 2) ** 0.5)
    while r1 > B:
        q = r0 // r1; r0, r1, s0, s1 = r1, r0 - q * r1, s1, s0 - q * s1
    return Q(r1, s1) if s1 else None


def certificate(snap, target):
    """Exact certificate: dict field -> Fraction with sum c_k row_k == target, or None. Also the rank of the snapshot."""
    keys = sorted(snap); piv = echelon([snap[k] for k in keys])
    combo = member(piv, target)
    if combo is None: return len(piv), None
    cert = {keys[i]: ratrec(a) for i, a in combo.items()}
    if any(v is None for v in cert.values()): return len(piv), None
    return len(piv), cert


def verify_cert(snap, cert, target):
    s = {}
    for k, c in cert.items():
        for t, v in snap[k].items(): s[t] = s.get(t, 0) + c * v
    return {t: v for t, v in s.items() if v} == {t: v for t, v in target.items() if v}


def toy_controls():
    # 2 public tokens, 1 owned field 2.  Lossy: copy x0 into owned, zero public 0 using it, CLEAR owned.
    W = {'public': 2, 'owned_fields': 1, 'program': [['INIT', 2], ['COPY', 2, 0, '1'], ['ADD', 0, 2, '-1'], ['CLEAR', 2]]}
    _, cl = replay(W, None, {3}); i, r, t, snap = cl[0]
    rk, cert = certificate(snap, t)
    expect('toy control (lossy CLEAR): rank of other live rows / certificate exists', (rk, cert is not None), (1, False))
    W['program'] = [['INIT', 2], ['COPY', 2, 0, '1'], ['ADD', 1, 2, '1'], ['CLEAR', 2]]
    _, cl = replay(W, None, {3}); i, r, t, snap = cl[0]
    rk, cert = certificate(snap, t)
    expect('toy control (lossless CLEAR): rank / certificate verified', (rk, cert is not None and verify_cert(snap, cert, t)), (2, True))


def main():
    global GAP_SHA
    src = json.load(open(os.path.join(HERE, 'SOURCES.json')))
    for f in src['files']:
        if f['path'] == GAP: GAP_SHA = f['sha256']
    if GAP_SHA is None: fail('gap candidate not pinned in SOURCES.json')
    toy_controls()
    base = load_gz(raw(os.path.join(HERE, 'data/base-7605-word.json.gz'), PINS['data/base-7605-word.json.gz']))
    E = json.loads(raw(os.path.join(HERE, 'data/edits-7608.json'), PINS['data/edits-7608.json']))
    newprog = apply_edits(base['program'], E)
    expect('edit list applies to #7605 (events before / after)', (len(base['program']), len(newprog)), (76636, 76631))
    n = base['public']
    rows_o, cl_o = replay(base, None, {42713})
    rows_n, cl_n = replay(base, newprog, {42708})
    expect('final public rows identical in #7605 and #7608', all(rows_o[r] == rows_n[r] for r in range(n)), True)
    expect('owned fields all empty at the end (both words)',
           (all(not rows_o[r] for r in range(n, len(rows_o))), all(not rows_n[r] for r in range(n, len(rows_n)))), (True, True))
    expect('CLEAR counts (#7605, #7608) and dirty counts', (len(cl_o), len(cl_n), sum(bool(c[2]) for c in cl_o),
                                                             sum(bool(c[2]) for c in cl_n)), (74, 74, 73, 73))
    diffs = [j for j in range(74) if cl_o[j][1] != cl_n[j][1] or cl_o[j][2] != cl_n[j][2]]
    expect('CLEARs whose (field, erased row) differ between the words (0-based CLEAR index)', diffs, [44])
    j = 44
    io, fo, to, so = cl_o[j]; inn, fn, tn, sn = cl_n[j]
    expect('CLEAR #44: field, #7605 event, #7608 event', (fo, fn, io, inn), (1557, 1557, 42713, 42708))
    expect('#7608 erased row', {k: str(v) for k, v in sorted(tn.items())}, {451: '-1', 1495: '1'})
    expect('#7605 erased row', {k: str(v) for k, v in sorted(to.items())}, {451: '-1', 902: '-3/2', 985: '-3/2', 1495: '1'})
    rkn, cn = certificate(sn, tn); rko, co = certificate(so, to)
    expect('#7608 CLEAR #44: other live rows, rank, certificate verified over Q, terms',
           (len(sn), rkn, cn is not None and verify_cert(sn, cn, tn), len(cn or {})), (1525, 1501, True, 21))
    expect('#7605 CLEAR #44: other live rows, rank, certificate verified over Q, terms',
           (len(so), rko, co is not None and verify_cert(so, co, to), len(co or {})), (1525, 1501, True, 23))
    d = {k: co.get(k, 0) - cn.get(k, 0) for k in set(co) | set(cn)}
    d = {k: str(v) for k, v in sorted(d.items()) if v}
    expect('certificate difference (#7605 - #7608)', d, {902: '-3/2', 985: '-3/2'})
    bad = dict(cn); k0 = min(bad); bad[k0] += 1
    expect('negative control: corrupted certificate coefficient rejected', verify_cert(sn, bad, tn), False)
    print('     #7608 certificate:', {k: str(v) for k, v in sorted(cn.items())})
    # all CLEARs, both words: by the Rank lemma (PROOF 1.1) the live rank never rises, so rank n_pub of the final public
    # rows proves that no CLEAR lowered it, i.e. all 74 CLEARs are lossless.  Checked mod p (prime 2^61-1).
    for name, rows in (('#7605', rows_o), ('#7608', rows_n)):
        expect(name + ': rank of the 1501 final public rows (=> every CLEAR lossless)', len(echelon(rows[:n])), n)
    # real-word negative control (scalar model): prepend INIT 1557, COPY 1557 <- register 0, ADD 0 += -1557, CLEAR 1557.
    # The CLEAR erases the only copy of token 0, so it is lossy and the endpoint becomes singular.
    mut = [['INIT', 1557], ['COPY', 1557, 0, '1', 3], ['ADD', 0, 1557, '-1', 3], ['CLEAR', 1557]] + newprog
    rows_m, clm = replay(base, mut, {3})
    i2, f2, t2, s2 = clm[0]
    rk2 = len(echelon(list(s2.values())))
    _, c2 = certificate(s2, t2)
    expect('negative control: prepended lossy CLEAR -> event, other live rank, certificate, final public rank',
           (i2, rk2, c2 is not None, len(echelon(rows_m[:n]))), (3, 1500, False, 1500))
    # swarm Q1
    g = load_gz(raw(os.path.join(ROOT, GAP), GAP_SHA))
    _, clg = replay(g, None, {17755, 17756})
    for ev in (17755, 17756):
        hit = [c for c in clg if c[0] == ev]
        i, r, t, snap = hit[0]
        rk, cert = certificate(snap, t)
        expect('clear-form-gap candidate CLEAR %d (field %d): nonzero row, other live rank (n_pub %d), certificate verified, terms'
               % (ev, r, g['public']), (bool(t), rk, cert is not None and verify_cert(snap, cert, t), len(cert or {})),
               (True, g['public'], True, 97))
    print('PASS_CLEARFORM')


if __name__ == '__main__':
    main()

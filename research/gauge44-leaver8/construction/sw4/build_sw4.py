#!/usr/bin/env python3
"""build_sw4.py INPUT_WORD OUT_DIR [RECIPE] : deterministic, standard-library-only rebuild of the BRoute SW4 word.

SW4 exchanges the B-phase target read sets of four entering packet copies h and their face registers r
(h = E_h + r after h's copy gate; E_h = h's entering content):
  h2r: a post-copy read add(t,h,c) becomes add(t,r,c), and t's entrance pre-read add(t,h,-c) (taken while h = E_h) is deleted;
  r2h: a read add(t,r,c) becomes add(t,h,c), and a pre-read add(t,h,-c) is inserted before index insert_preread_before
       (right after h's last existing pre-read, still before h's copy gate).
Every register holds the same value at the end of B (checked mod p). Frames: a moved or inserted gate gets the plain join of
its operands' current frames; every other B gate and every early-cleanup tail keeps span(old frame + current operand frames).
Targets must stay inside u_t^perp, and tails and ends must contain the current frame.

Controls (run on every build; the count is pinned to 4 and all must hold, else exit 1):
  C0 the identity recipe (no moves) reproduces the input B and early_cleanup byte for byte;
  N1 h2r without deleting the pre-read is rejected by exactness;
  N2 a partial exchange (one read only) is rejected by the frame cap;
  N3 an inserted pre-read with the wrong sign is rejected by exactness.
Rejection sites are pinned: the recipe's 'rejection_expected' gives, for N1/N3, the exact set of target rows whose B-end
state changes (the mutated target plus its butterfly partner(s)) and, for N2, the first cap violation (kind, B index,
register) and the violation count. Each control must reproduce its pinned site exactly. BUILD.json records the observed
sites under 'rejection'.
Writes OUT_DIR/FULL-WORD.json.gz (sha checked against the recipe) and OUT_DIR/BUILD.json."""
import sys, json, gzip, hashlib, os
from collections import Counter, defaultdict

PR = 2147483629
HERE = os.path.dirname(os.path.abspath(__file__))
V, HH = 112, 9


def basis(vs):
    piv = {}
    for a in vs:
        while a:
            bit = a.bit_length() - 1
            if bit in piv: a ^= piv[bit]
            else:
                piv[bit] = a; break
    for k in sorted(piv):
        for j in piv:
            if j > k and piv[j] >> k & 1: piv[j] ^= piv[k]
    return tuple(piv[k] for k in sorted(piv, reverse=True))


def contained(a, b): return basis(list(a) + list(b)) == tuple(b)
def registers(e): return e[1:3] if e[0] == 'add' else e[1:2]
def hyper(p): return basis([x for x in range(1, 1 << HH) if (x & p).bit_count() % 2 == 0])
FULL = basis([1 << i for i in range(HH)])


def coef(e):
    a, b = (e[3], e[4]) if e[0] == 'add' else (e[2], e[3])
    return a % PR * pow(b % PR, PR - 2, PR) % PR


def bend_state(w):
    """sparse rows mod p of every register after A + cut + B (identity start)."""
    n = 2 * V + w['report']['R']; rows = [{i: 1} for i in range(n)]
    for e in w['A'] + w['cut'] + w['B']:
        q = coef(e); t = e[1]
        if e[0] == 'scale': rows[t] = {k: x * q % PR for k, x in rows[t].items()}
        else:
            d = rows[t]
            for k, x in rows[e[2]].items():
                y = (d.get(k, 0) + q * x) % PR
                if y: d[k] = y
                else: d.pop(k, None)
    return rows


def apply_recipe(w, moves, drop_delete=False, wrong_sign=False):
    B = [list(e[:-1]) + [list(e[-1]) if e[-1] is not None else None] for e in w['B']]
    tag = {}; dele = set(); ins = defaultdict(list)
    for m in moves:
        i = m['read_index']; e = B[i]; t = m['target']; a, b = m['coef']
        assert e[0] == 'add' and e[1] == t and [e[3], e[4]] == [a, b], ('recipe/word mismatch', m)
        if m['kind'] == 'h2r':
            assert e[2] == m['h']
            pi = m['delete_preread_index']; g = B[pi]
            assert g[:5] == ['add', t, m['h'], -a, b], ('pre-read mismatch', m)
            B[i] = ['add', t, m['r'], a, b, e[-1]]
            if not drop_delete: dele.add(pi)
        else:
            assert e[2] == m['r']
            B[i] = ['add', t, m['h'], a, b, e[-1]]
            g = list(m['preread'])
            if wrong_sign: g[3] = -g[3]
            ins[m['insert_preread_before']].append(g + [None])
        tag[i] = 1
    NB, nt = [], []
    for i, e in enumerate(B):
        for g in ins.get(i, []): NB.append(g); nt.append(1)
        if i in dele: continue
        NB.append(e); nt.append(tag.get(i, 0))
    w2 = dict(w); w2['B'] = NB; w2['early_cleanup'] = [list(x) for x in w.get('early_cleanup', [])]
    return w2, nt


def refit(w, nt):
    n = 2 * V + w['report']['R']
    cur = [(p,) for p in w['ports']] + [()] * (n - V)
    for q, U in w['start_extra'].items(): cur[int(q)] = basis(U)
    for e in w['A']:
        for q in registers(e): cur[q] = basis(e[-1])
    prob = []
    for i, e in enumerate(w['B']):
        rs = registers(e)
        base = [] if nt[i] or e[-1] is None else list(e[-1])
        F = basis(base + [x for q in rs for x in cur[q]])
        for q in rs:
            if V <= q < 2 * V and not contained(F, hyper(w['ports'][q - V])): prob.append(('cap', i, q))
        e[-1] = list(F)
        for q in rs: cur[q] = F
    ne = []
    for i, U in w.get('early_cleanup', []):
        rs = registers(w['cleanup'][i]); F = basis(list(U) + [x for q in rs for x in cur[q]])
        for q in rs:
            fin = w['helper_final'].get(str(q))
            if fin is not None and not contained(F, basis(fin)): prob.append(('tail', i, q))
        ne.append([i, list(F)])
        for q in rs: cur[q] = F
    w['early_cleanup'] = ne
    for q in range(2 * V, n):
        fin = w['helper_final'].get(str(q))
        if fin is not None and not contained(cur[q], basis(fin)): prob.append(('end', q))
    return prob


def profile(w):
    n = 2 * V + w['report']['R']
    tail = [w['cleanup'][i][:-1] + [U] for i, U in w.get('early_cleanup', [])]
    end = [FULL] * V + [hyper(p) for p in w['ports']] + [FULL] * (n - 2 * V)
    for q, U in w['helper_final'].items(): end[int(q)] = basis(U)
    start = [(p,) for p in w['ports']] + [()] * (n - V)
    for q, U in w['start_extra'].items(): start[int(q)] = basis(U)
    cur = list(start); paid = Counter()
    def climb(q, U):
        U = basis(U); assert contained(cur[q], U), ('monotone', q)
        d = len(U) - len(cur[q])
        if d: paid[d] += 1
        cur[q] = U
    for sec in ('A', 'B'):
        if sec == 'B':
            lev = {int(t): basis(U) for t, U in w.get('target_levels', {}).items()}
            for q, U in zip(w['centers'], w['center_frames']):
                U = basis(U); served = {lev.get(e[1] - V, ()) for e in w['cut'] if e[2] == q}
                for T in sorted(served, key=lambda x: -len(x)):
                    if T != U: paid[len(U) - len(T)] += 1
                    U = T
        for e in w[sec]:
            for q in registers(e): climb(q, e[-1])
    for e in tail:
        for q in registers(e): climb(q, e[-1])
    for q, U in enumerate(end): climb(q, U)
    widths = Counter(len(end[q]) - len(start[q]) for q in range(2 * V, n))
    return paid, widths


def enc(w): return json.dumps(w, sort_keys=True, separators=(',', ':')).encode()


def main():
    src, out = sys.argv[1], sys.argv[2]
    rec = json.load(open(sys.argv[3] if len(sys.argv) > 3 else os.path.join(HERE, 'SW4-RECIPE.json')))
    raw = gzip.decompress(open(src, 'rb').read())
    assert hashlib.sha256(raw).hexdigest() == rec['input_sha256'], 'input sha mismatch'
    w = json.loads(raw); S0 = bend_state(w); moves = rec['moves']
    h0 = moves[0]['h']; one = [m for m in moves if m['h'] == h0]
    ctl = {}; why = {}; EXP = rec.get('rejection_expected', {})
    if os.environ.get('SW4_PIN') != '1' and set(EXP) != {'N1', 'N2', 'N3'}: raise SystemExit('recipe rejection_expected must pin exactly N1, N2, N3 (set SW4_PIN=1 to record)')
    def diff(S):
        d = [q for q in range(len(S0)) if S[q] != S0[q]]
        return dict(changed_registers=d[:8], n=len(d))
    w0, nt0 = apply_recipe(w, []); p0 = refit(w0, nt0)
    ctl['C0_identity'] = not p0 and w0['B'] == w['B'] and w0['early_cleanup'] == w['early_cleanup']
    m1 = [m for m in one if m['kind'] == 'h2r'][:1]
    w1, nt1 = apply_recipe(w, m1, drop_delete=True); d1 = diff(bend_state(w1))
    ctl['N1_keep_preread_rejected'] = d1['n'] > 0 and d1 == EXP.get('N1', d1); why['N1'] = d1
    w2, nt2 = apply_recipe(w, m1); p2 = refit(w2, nt2)
    why['N2'] = dict(first=list(p2[0]) if p2 else None, n=len(p2)); ctl['N2_partial_rejected'] = bool(p2) and p2[0][0] == 'cap' and why['N2'] == EXP.get('N2', why['N2'])
    w3, nt3 = apply_recipe(w, one, wrong_sign=True); d3 = diff(bend_state(w3))
    ctl['N3_wrong_sign_rejected'] = d3['n'] > 0 and d3 == EXP.get('N3', d3); why['N3'] = d3
    assert len(ctl) == 4
    wn, nt = apply_recipe(w, moves); pr = refit(wn, nt)
    assert not pr, ('illegal', pr[:5])
    assert bend_state(wn) == S0, 'B-end state changed'
    paid, widths = profile(wn)
    wn['report'] = dict(wn['report'], local_profile={str(k): v for k, v in sorted(paid.items())},
                        local_rank_mass=sum(k * v for k, v in paid.items()))
    data = enc(wn); sha = hashlib.sha256(data).hexdigest()
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, 'FULL-WORD.json.gz'), 'wb') as f: f.write(gzip.compress(data, mtime=0))
    rep = dict(recipe=rec['name'], input_sha256=rec['input_sha256'], output_sha256=sha, expected_output_sha256=rec['output_sha256'],
               moves=len(moves), controls=ctl, rejection=why, profile=wn['report']['local_profile'],
               widths={str(k): v for k, v in sorted(widths.items()) if k}, W=sum(k * v for k, v in widths.items()))
    with open(os.path.join(out, 'BUILD.json'), 'w', newline='\n') as f: f.write(json.dumps(rep, indent=1) + '\n')
    print(json.dumps(rep, indent=1))
    ok = all(ctl.values()) and sha == rec['output_sha256'] and rep['profile'] == rec['profile_out'] and rep['W'] == rec['W']
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()

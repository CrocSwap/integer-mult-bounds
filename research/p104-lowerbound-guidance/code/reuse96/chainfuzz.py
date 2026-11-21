"""REUSE96 chainfuzz.py: exact sanity check of the CHAIN LAW on random multi-epoch runs (own code).
Model (eng.py): publics X_t (chart <q_t>, never lifted), Y_s (ascend inside q_s^perp); owned O_k: free INIT anywhere, nested
moves, descents free, R = sum of ascents. Intakes O += lam*Y_s (needs chart(O) <= chart(Y_s): automatically cold), outputs
X_t += lam*O (needs q_t in chart(O)).  Epoch = maximal block of intakes followed by outputs.
Checks per run: (i) Rec[t][s] (y_s coef of X_t) == sum_j w_j[t] * cum_c_j[s]  (all cells);
(ii) per epoch ascent >= dim B_j - dim(B_j cap A_j) >= rank_F2 Q[D(w_j), S(c_j)];  (iii) R >= sum_j rank_F2 Q[D(w_j),S(c_j)].
Fields: GF(2) and Q (Fraction scalars)."""
import random, sys
from fractions import Fraction as Fr
sys.path.insert(0, '.')
from eng import span, fdim, perp, dot

def rankF2(rows):
    rows = [r for r in rows if r]; rk = 0
    basis = []
    for r in rows:
        for b in basis: r = min(r, r ^ b)
        if r: basis.append(r); rk += 1
    return rk

def pairing_rank(P, D, S):
    return rankF2([sum(1 << j for j, s in enumerate(S) if dot(P[t], P[s])) for t in D])

def meet(A, B): return frozenset(A & B)
def join(A, B): return span(list(A) + list(B))

def one(n, P, field, rng, no=2, steps=40):
    T = len(P); F = (lambda x: x % 2) if field == 2 else (lambda x: Fr(x))
    scal = [1] if field == 2 else [1, -1, Fr(1, 2), 2, Fr(-3, 2)]
    Ych = [frozenset([0]) for _ in range(T)]
    X = [dict() for _ in range(T)]          # y-part of X_t
    allsub = None
    O = {}; R = 0
    life = {}   # k -> list of epochs: dict(asc, A, B, c (dict), w (dict), state)
    def newlife(k, C):
        O[k] = [C, {}]; life.setdefault(k, []).append([])
        life[k][-1].append(dict(asc=0, A=None, B=frozenset([0]), c={}, w={}, phase='in'))
    def ep(k): return life[k][-1][-1]
    full = frozenset(range(1 << n))
    for k in range(no):
        v = [rng.randrange(1, 1 << n) for _ in range(rng.randrange(0, 3))]
        newlife(k, span(v))
    for _ in range(steps):
        k = rng.randrange(no); C, cont = O[k]; e = ep(k)
        op = rng.random()
        if op < 0.3:  # move: up by adding a vector, or down to a subspace
            if rng.random() < 0.55:
                v = rng.randrange(1, 1 << n); D = join(C, [v]); a = fdim(D) - fdim(C); R += a; e['asc'] += a
            else:
                if fdim(C) == 0: continue
                # random hyperplane-ish descent: keep vectors orthogonal to random u
                u = rng.randrange(1, 1 << n); D = frozenset(x for x in C if not dot(x, u))
                if D == C: continue
            O[k][0] = D
        elif op < 0.65:  # intake from Y_s
            s = rng.randrange(T)
            if any(dot(x, P[s]) for x in C): continue
            Ych[s] = join(Ych[s], C)
            if e['phase'] == 'out':
                life[k][-1].append(dict(asc=0, A=None, B=frozenset([0]), c={}, w={}, phase='in')); e = ep(k)
            lam = F(rng.choice(scal))
            cont[s] = cont.get(s, F(0)) + lam
            e['c'][s] = e['c'].get(s, F(0)) + lam
            e['A'] = C if e['A'] is None else meet(e['A'], C)
        elif op < 0.95:  # output into X_t
            ts = [t for t in range(T) if P[t] in C]
            if not ts or not cont: continue
            t = rng.choice(ts); lam = F(rng.choice(scal))
            for s, v in cont.items(): X[t][s] = X[t].get(s, F(0)) + lam * v
            e['phase'] = 'out'; e['w'][t] = e['w'].get(t, F(0)) + lam; e['B'] = join(e['B'], C)
        else:  # clear + re-init anywhere
            v = [rng.randrange(1, 1 << n) for _ in range(rng.randrange(0, 3))]
            newlife(k, span(v))
    # checks
    pred = [[F(0)] * T for _ in range(T)]
    tot_price = 0; bad = []; rowprice = 0
    for k, lts in life.items():
        for lt in lts:
            for i in range(len(lt)):   # Abel rows (W_i, c_i), W_i = sum_{j>=i} w_j
                W = {}
                for e in lt[i:]:
                    for t, v in e['w'].items(): W[t] = W.get(t, F(0)) + v
                D = [t for t, v in W.items() if v != 0]; S = [s for s, v in lt[i]['c'].items() if v != 0]
                if D and S: rowprice += pairing_rank(P, D, S)
            cum = {}
            for e in lt:
                for s, v in e['c'].items(): cum[s] = cum.get(s, F(0)) + v
                for t, wv in e['w'].items():
                    for s, v in cum.items(): pred[t][s] += wv * v
                D = [t for t, v in e['w'].items() if v != 0]; S = [s for s, v in e['c'].items() if v != 0]
                if D and S:
                    pr = pairing_rank(P, D, S)
                    A = e['A'] if e['A'] is not None else full
                    gb = fdim(e['B']) - fdim(meet(e['B'], A))
                    if not (e['asc'] >= gb >= pr): bad.append(('epoch', e['asc'], gb, pr))
                    tot_price += pr
    for t in range(T):
        for s in range(T):
            if pred[t][s] != X[t].get(s, F(0)): bad.append(('rec', t, s))
    if R < tot_price: bad.append(('R', R, tot_price))
    nep = sum(len(lt) for lts in life.values() for lt in lts)
    multi = sum(1 for lts in life.values() for lt in lts if len(lt) > 1)
    return bad, R, tot_price, multi, rowprice

if __name__ == '__main__':
    rng = random.Random(int(sys.argv[1]) if len(sys.argv) > 1 else 1)
    N = int(sys.argv[2]) if len(sys.argv) > 2 else 4000
    cases = [(3, [1, 2, 4, 7]), (4, [1, 2, 7, 11, 13]), (4, [1, 2, 4, 8, 7, 11, 13, 14])]
    nb = 0; nm = 0; tight = 0; npos = 0; teeth = 0
    for i in range(N):
        n, P = cases[i % 3]; field = 2 if i % 2 else 0
        bad, R, tp, multi, rp = one(n, P, field, rng)
        npos += tp > 0; teeth += rp > R
        nm += multi > 0; tight += (R == tp and tp > 0)
        if bad: nb += 1; print('BAD', i, n, P, field, bad[:3])
    print(f'runs {N} bad {nb} with-multi-epoch {nm} chainprice>0 {npos} tight {tight} abel-rowprice>R (teeth) {teeth}')

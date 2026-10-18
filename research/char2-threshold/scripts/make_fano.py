"""Authors' script (NOT run by verify.sh; sympy, and the C program c/kgap.c compiled to c/kgap_tmp): realises the Levi graph of the Fano plane over Q.  Seven points
P_i in Z^T (random), seven lines Q_L in Z^T orthogonal to the three points of the Fano line L = (i, i+1, i+3) (a null vector), and a perfect matching sigma
with P_t . Q_sigma(t) != 0 that makes the seven (point, line) pairs the 'lines' t of a configuration with decoder pairing M_ts = P_t . Q_sigma(s).
Keeps, for T = 4 and T = 5, the realisation of least exact F2 cost over 100 random draws; writes data/fano_T4.json and data/fano_T5.json."""
import sys, os, json, random, itertools, subprocess
from math import lcm, gcd
import sympy
H = os.path.dirname(os.path.abspath(__file__)); fl = [(i, (i + 1) % 7, (i + 3) % 7) for i in range(7)]
def realize(T, rng, m=3):
    while True:
        P = [[rng.randint(-m, m) for _ in range(T)] for _ in range(7)]; Q = []; ok = True
        for L in fl:
            ns = sympy.Matrix([P[i] for i in L]).nullspace()
            if len(ns) != T - 3: ok = False; break
            n = ns[0]
            for extra in ns[1:]: n = n + rng.randint(-2, 2) * extra   # generic null vector (all T coordinates can be used)
            l = 1
            for x in n: l = lcm(l, int(sympy.Rational(x).q))
            q = [int(x * l) for x in n]; g = 0
            for x in q: g = gcd(g, abs(x))
            Q.append([x // g for x in q])
        if ok and sympy.Matrix(P).rank() == T and all(any(P[t][j] for t in range(7)) and any(q[j] for q in Q) for j in range(T)): return P, Q
def kg_cost(P, Q):
    T = len(P[0]); inp = "%d 7\n" % T + "\n".join(" ".join(map(str, P[t] + Q[t])) for t in range(7)) + "\n"
    out = subprocess.run([os.path.join(H, '..', 'c', 'kgap_tmp'), 'ex'], input=inp, capture_output=True, text=True).stdout.split('\n')
    return int([l for l in out if l.startswith('best')][0].split()[1])
rng = random.Random(1)
for T in (4, 5):
    best = None
    for tr in range(100):
        P, Q = realize(T, rng)
        for sg in itertools.permutations(range(7)):
            if all(sum(a * b for a, b in zip(P[t], Q[sg[t]])) != 0 for t in range(7)):
                Qp = [Q[sg[t]] for t in range(7)]
                if sympy.Matrix(P).T.shape and sympy.Matrix(P) * sympy.Matrix(Qp).T == sympy.zeros(7, 7): continue
                if (sympy.Matrix(P) * sympy.Matrix(Qp).T).rank() != T: continue
                c = kg_cost(P, Qp)
                if best is None or c < best[0]: best = (c, P, Qp)
                break
    print(T, best[0]); json.dump({'T': T, 'P': best[1], 'Q': best[2], 'cost_found': best[0]}, open(os.path.join(H, '..', 'data', 'fano_T%d.json' % T), 'w'))

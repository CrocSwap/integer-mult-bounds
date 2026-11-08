"""Exact tile caps over ALL subspaces of F2^9 for the port set (120 lines minus the 16 pair lines). Stdlib only.
For A of dimension a and B = A + <w> (dimension a+1): area(A,B) = #{ports with label in A} * #{ports orthogonal to B}.
Prints the maximum over all pairs; recursion over reduced row-echelon bases (exhaustive, no sampling)."""
import os, sys, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import e8lib as E
HERE = os.path.dirname(os.path.abspath(__file__))
pairs = json.load(open(os.path.join(os.path.dirname(HERE), 'data', 'p104_pairs.json')))
D = set(pairs['ys']) | set(pairs['zs'])
PORTS = [E.LABEL[i] for i in range(E.n) if i not in D]
assert len(PORTS) == 104
isp = [0] * 512
for x in PORTS: isp[x] += 1
assert max(isp) == 1
# linear map G with form(x, y) = parity(G(x) & y)
G = [sum(E.form(1 << i, 1 << j) << j for j in range(9)) for i in range(9)]
def Gx(x):
    r = 0
    for i in range(9):
        if (x >> i) & 1: r ^= G[i]
    return r
def par(x): return bin(x).count('1') & 1
orth = [0] * 512      # bitmask over port indices: ports orthogonal to v
GP = [Gx(x) for x in PORTS]
for v in range(512):
    m = 0
    for k, g in enumerate(GP):
        if par(g & v) == 0: m |= 1 << k
    orth[v] = m
ALL = (1 << 104) - 1
pc = int.bit_count
results = {}
def run(a):
    best = [0, 0, 0]; cnt = [0]
    def leaf(basis):
        cnt[0] += 1
        el = [0]
        o = ALL
        for b in basis:
            el += [x ^ b for x in el]; o &= orth[b]
        po = sum(isp[x] for x in el)
        if not po: return
        c0 = pc(o)
        if po * c0 <= best[0]: return
        inA = set(el)
        for w in range(1, 512):
            if w in inA: continue
            c = pc(o & orth[w])
            if po * c > best[0]: best[0] = po * c; best[1] = po; best[2] = c
    basis = [0] * a
    def rec(i, start):
        if i == a:
            leaf(basis); return
        for p in range(start, a - i - 2, -1):
            for fr in range(1 << p):
                v = (1 << p) | fr
                if any((basis[k] >> p) & 1 for k in range(i)):
                    break
                basis[i] = v
                rec(i + 1, p - 1)
    rec(0, 8)
    return best, cnt[0]
if __name__ == '__main__':
    fails = []
    want = {2: 32, 3: 32, 4: 36}
    for a in (2, 3, 4):
        t = time.time()
        best, cnt = run(a)
        gauss = 1
        for i in range(a): gauss = gauss * (2 ** (9 - i) - 1) // (2 ** (i + 1) - 1)
        ok = cnt == gauss and best[0] == want[a]
        print(('ok   ' if ok else 'FAIL ') + f'dim A = {a}: {cnt} subspaces (Gaussian binomial {gauss}), maximum area {best[0]} = {best[1]} x {best[2]}  [{time.time()-t:.0f}s]', flush=True)
        if not ok: fails.append(a)
    print('PASS_CAPS' if not fails else 'FAILED_CAPS')
    sys.exit(1 if fails else 0)

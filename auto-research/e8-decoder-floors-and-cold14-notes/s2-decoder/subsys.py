import itertools
from bitp import *
def diagram(name):
    """edges of a Dynkin diagram (disjoint union), returns (n, edges)"""
    parts = name.split('+'); n = 0; E = []
    for part in parts:
        mult = 1
        if '*' in part: mult, part = int(part.split('*')[0]), part.split('*')[1]
        for _ in range(mult):
            t, r = part[0], int(part[1:])
            if t == 'A': e = [(i, i + 1) for i in range(r - 1)]
            elif t == 'D': e = [(i, i + 1) for i in range(r - 2)] + [(r - 3, r - 1)]
            elif t == 'E': e = [(0, 2), (2, 3), (3, 4), (1, 3)] + [(i, i + 1) for i in range(4, r - 1)]
            E += [(a + n, b + n) for a, b in e]; n += r
    return n, E
def embed(name, start=0):
    n, E = diagram(name)
    adj = {i: set() for i in range(n)}
    for a, b in E: adj[a].add(b); adj[b].add(a)
    sol = []
    def rec(k):
        if k == n: return True
        for c in range(NL):
            if c in sol: continue
            ok = all((abs(G[c, sol[j]]) == 1) == (j in adj[k]) for j in range(k))
            if ok:
                sol.append(c)
                if rec(k + 1): return True
                sol.pop()
        return False
    assert rec(0)
    return sol
def closure(S):
    S = set(S)
    while True:
        new = set()
        for a in S:
            for b in S:
                new.add(REFL[a][b])
        if new <= S: return sorted(S)
        S |= new
def report(name):
    X = closure(embed(name))
    P = set(range(NL)) - set(X)
    live = sorted(X)
    h = rankQ_lines(live)
    s = s_all(P); ch, c = greedy_basis(s)
    return len(X), h, c, ch
if __name__ == '__main__':
    import sys
    for nm in sys.argv[1:]:
        print(nm, report(nm), flush=True)

"""Theorems I and R: the subspace frames are the geodesic interval, and rho(L) = L_{pi_1(L)} is a 1-Lipschitz retraction. Exhaustive for h <= 4. Stdlib only."""
import itertools, sys
fails = []
def ck(cond, msg):
    print(('ok   ' if cond else 'FAIL ') + msg, flush=True)
    if not cond: fails.append(msg)
def par(x): return bin(x).count('1') & 1
def sp(h, u, v):
    m = (1 << h) - 1
    return par((u >> h) & (v & m)) ^ par((u & m) & (v >> h))
def span(gens):
    S = {0}
    for g in gens:
        if g not in S: S |= {s ^ g for s in S}
    return frozenset(S)
def dimof(S): return len(S).bit_length() - 1
def subspaces(h):
    seen = {frozenset({0})}; fr = list(seen)
    while fr:
        nxt = []
        for U in fr:
            for v in range(1, 1 << h):
                if v not in U:
                    W = frozenset(U | {u ^ v for u in U})
                    if W not in seen: seen.add(W); nxt.append(W)
        fr = nxt
    return list(seen)
def perp(h, U): return frozenset(v for v in range(1 << h) if all(par(v & u) == 0 for u in U))
def LU(h, U):   # {(u, u+v) : u in U, v in U^perp}, vector = (x << h) | z
    return frozenset((u << h) | (u ^ v) for u in U for v in perp(h, U))
def lagrangians(h):
    L0 = frozenset(range(1 << h))      # {(0, z)} is x = 0: with (x<<h)|z this is range(1<<h)
    seen = {L0}; fr = [L0]
    while fr:
        nxt = []
        for L in fr:
            for w in range(1, 1 << (2 * h)):
                M = frozenset(x ^ w if sp(h, x, w) else x for x in L)
                if M not in seen: seen.add(M); nxt.append(M)
        fr = nxt
    return list(seen)
def dist(h, L, M): return h - dimof(L & M)
def proj1(h, L): return frozenset(x >> h for x in L)
for h in (1, 2, 3, 4):
    Ls = lagrangians(h)
    expect = 1
    for i in range(1, h + 1): expect *= (2 ** i + 1)
    ck(len(Ls) == expect and all(len(L) == 2 ** h and all(sp(h, a, b) == 0 for a in list(L)[:8] for b in L) for L in Ls[:200]), f'h={h}: {len(Ls)} Lagrangians = prod (2^i + 1), isotropic of size 2^h')
    Us = subspaces(h)
    FU = {U: LU(h, U) for U in Us}
    ck(len(set(FU.values())) == len(Us) and all(L in set(Ls) for L in FU.values()), f'h={h}: U -> L_U is injective into the Lagrangians ({len(Us)} subspaces)')
    L0 = LU(h, frozenset({0})); LF = LU(h, frozenset(range(1 << h)))
    interval = {L for L in Ls if dist(h, L0, L) + dist(h, L, LF) == h}
    ck(interval == set(FU.values()), f'h={h} Theorem I: the Lagrangians on a geodesic from L_0 to L_F are exactly the L_U')
    ok = all(dist(h, FU[U], FU[V]) == dimof(U) + dimof(V) - 2 * dimof(U & V) for U, V in itertools.combinations(Us, 2))
    ck(ok, f'h={h}: d(L_U, L_V) = dim U + dim V - 2 dim(U cap V)')
    # adjacency by hyperplanes
    byhyp = {}
    for idx, L in enumerate(Ls):
        els = sorted(L)
        basis = []
        for v in els:
            if v not in span(basis): basis.append(v)
        # direct: a hyperplane is the span of L minus a coset; enumerate via functionals on coordinates of the basis
        coords = {}
        for c in range(1 << h):
            vec = 0
            for i in range(h):
                if (c >> i) & 1: vec ^= basis[i]
            coords[vec] = c
        for f in range(1, 1 << h):
            H = frozenset(v for v, c in coords.items() if par(c & f) == 0)
            byhyp.setdefault(H, []).append(idx)
    adj = [set() for _ in Ls]
    for H, lst in byhyp.items():
        for a in lst:
            for b in lst:
                if a != b: adj[a].add(b)
    ck(all(dist(h, Ls[a], Ls[b]) == 1 for a in range(len(Ls)) for b in adj[a]) and all(len(adj[a]) == 2 * (2 ** h - 1) for a in range(len(Ls))), f'h={h}: adjacency (meeting in a hyperplane) has valency 2(2^h - 1)')
    # d is the graph distance (all sources for h <= 3, two sources for h = 4)
    srcs = range(len(Ls)) if h <= 3 else [0, len(Ls) // 2]
    okd = True
    for s in srcs:
        D = {s: 0}; fr = [s]
        while fr:
            nxt = []
            for a in fr:
                for b in adj[a]:
                    if b not in D: D[b] = D[a] + 1; nxt.append(b)
            fr = nxt
        okd &= all(D[b] == dist(h, Ls[s], Ls[b]) for b in range(len(Ls)))
    ck(okd, f'h={h}: d(L, L\') = h - dim(L cap L\') equals the graph distance ({"all" if h <= 3 else "two"} sources)')
    # Theorem R
    rho = {}; allproj = True
    for L in Ls:
        U = proj1(h, L)
        Z = frozenset(z for (x, z) in ((v >> h, v & ((1 << h) - 1)) for v in L) if x == 0)
        okproj = all(par(u & z) == 0 for u in U for z in Z) and len(U) * len(Z) == 2 ** h
        rho[L] = LU(h, U)
        allproj &= okproj
    idx = {L: i for i, L in enumerate(Ls)}
    ck(all(rho[L] == L for L in FU.values()) and allproj, f'h={h} Theorem R: rho fixes every L_U, and pi_1(L) is the orthogonal complement of L cap L_0 (sizes multiply to 2^h)')
    bad = sum(1 for a in range(len(Ls)) for b in adj[a] if dist(h, rho[Ls[a]], rho[Ls[b]]) > 1)
    ck(bad == 0, f'h={h} Theorem R: d(rho L, rho L\') <= 1 for all {sum(len(x) for x in adj)} ordered adjacent pairs (violations {bad})')
    nonfam = sum(1 for L in Ls if L not in set(FU.values()))
    ck(h < 2 or nonfam > 0, f'h={h}: {nonfam} Lagrangians are not subspace frames (the retraction moves them)')
print('PASS_LAGR' if not fails else 'FAILED_LAGR')
sys.exit(1 if fails else 0)

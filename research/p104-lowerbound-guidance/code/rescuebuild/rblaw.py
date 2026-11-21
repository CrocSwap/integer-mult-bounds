"""rblaw: direct evaluation of the mask-level laws (RB.md section 1) on ONE design (no CP-SAT). Returns list of violations.
Design = list of (mask frozenset, idle pieces list); mains = mask - union(pieces).  Stages are call positions."""
import itertools
def runs(seq, lab): return sum(1 for i, x in enumerate(seq) if x == lab and (i == 0 or seq[i-1] != lab))
def setparts(s):
    s = list(s)
    if not s: yield []; return
    a = s[0]
    for p in setparts(s[1:]):
        for i in range(len(p)): yield p[:i] + [p[i] | {a}] + p[i+1:]
        yield p + [frozenset({a})]
def violations(k, R, full=True):
    n = len(R); V = []
    pieces = [(r, p) for r, (M, P) in enumerate(R) for p in P]
    mains = [M - (frozenset().union(*P) if P else frozenset()) for M, P in R]
    E = lambda X: [r for r, (M, P) in enumerate(R) if M >= X]
    pi = lambda X: sum(1 for r, p in pieces if p >= X)
    if n != 2*k-2: V.append('n')
    for t in range(k):
        if sum(1 for m in mains if t in m) != 2: V.append(('mains', t))
    for M, P in R:
        if len(M) < 2: V.append('D1')
    # PC3 (contains CROSS and SEPARATION)
    for lab in itertools.product('XY.', repeat=k):
        X = frozenset(i for i in range(k) if lab[i] == 'X'); Y = frozenset(i for i in range(k) if lab[i] == 'Y')
        if not X or not Y: continue
        sq = [x for x in lab if x != '.']; need = 2*min(runs(sq, 'X'), runs(sq, 'Y'))
        RXY = sum(1 for M, P in R if M & X and M & Y)
        bad = sum(1 for r, p in pieces if p >= X and all(M & Y for M, P in R if M >= p))
        if RXY - bad < need: V.append(('PC3', ''.join(lab)))
    allS = [frozenset(x) for j in range(1, k+1) for x in itertools.combinations(range(k), j)]
    # LOCAL-PIECEFIX
    for X in allS:
        if len(X) == k: continue
        comp = [t for t in range(k) if t not in X]
        for j in range(len(comp)+1):
            for T in itertools.combinations(comp, j):
                T = frozenset(T)
                cnt = sum(1 for r, p in pieces if p >= X and (frozenset().union(*[R[o][0] for o in E(p)]) - p) <= T)
                cnt += sum(1 for M, P in R if T and M <= T)
                if cnt > max(0, 2*len(T)-2): V.append(('LOCAL', tuple(sorted(X)), tuple(sorted(T))))
    # RESCUE
    for r, (M, P) in enumerate(R):
        un = [t for t in mains[r] if not any(t in p and p <= M for o, p in pieces)]
        if len(un) > 1: V.append(('RESCUE', r))
    # ADJ (linear consecutive)
    for a in range(k-1):
        ab = frozenset({a, a+1})
        if any(M <= ab for M, P in R) and not any(M >= ab and len(M) >= 3 for M, P in R): V.append(('ADJ', a))
    # e-row
    if sum(len(P) + len(m) - 1 for (M, P), m in zip(R, mains)) < 2*k-2: V.append('e')
    # SPAN on set partitions
    for part in setparts(range(k)):
        if len(part) == k: continue
        tot = sum(min(2*len(X), sum(1 for M, P in R if M & X) - pi(frozenset(X))) for X in part)
        if tot < n: V.append(('SPAN', tuple(tuple(sorted(X)) for X in part)))
    # CELL-RANK (all collections of disjoint cells = set partitions of k+1 points, extra point = unused)
    if full:
        for part in setparts(range(k+1)):
            fam = [frozenset(X) for X in part if k not in X]
            if not fam or max(len(X) for X in fam) < 2: continue
            U = frozenset().union(*fam)
            S = sum(1 for M, P in R if M <= U and all((not (M & X)) or X <= M for X in fam))
            rhs = sum(len(E(X)) - pi(X) for X in fam)
            if S > rhs: V.append(('CELLRANK', tuple(tuple(sorted(X)) for X in fam)))
    # PURE-CELL and SATURATED-CELL v2
    for X in allS:
        if not (2 <= len(X) <= k-1): continue
        dbar = len(E(X)) - pi(X); pX = sum(1 for M, P in R if M == X)
        if pX >= dbar:
            s1 = sum(1 for M, P in R if M >= X and len(M - X) == 1)
            out = sum(1 for M, P in R if (M & X) and not M >= X)
            if pX + s1 > dbar: V.append(('PURECELL', tuple(sorted(X))))
            if out < 2: V.append(('PURECELL-out', tuple(sorted(X))))
            for r, q in pieces:
                if len(q) < 2 or not (q & X) or q <= X: continue
                I = [o for o in E(q) if not R[o][0] >= X]
                outside = frozenset().union(*[R[o][0] for o in I]) - q if I else frozenset()
                if len(outside) < 2: V.append(('SATCELL', tuple(sorted(X)), tuple(sorted(q))))
    return V

def star_zero(k, R):
    """STAR-3 + zero-sum kill (RB.md). Returns list of kills."""
    from fractions import Fraction as Fr
    pieces = [(r, p) for r, (M, P) in enumerate(R) for p in P]
    Eset = lambda q: frozenset(r for r, (M, P) in enumerate(R) if M >= q)
    kills = []
    for C in itertools.combinations(range(len(R)), 2):
        C = frozenset(C)
        # star pieces: E(q) = C + {o}, o not in C
        star = [(r, q) for r, q in pieces if len(q) >= 2 and len(Eset(q)) == 3 and C < Eset(q)
                and len(R[next(iter(Eset(q) - C))][0] - q) <= 1]      # relay partner o: |M_o - q| <= 1 (else it may be inert)
        if len(star) < 3: continue
        # stages with >= 3 star pieces; union-find over pieces sharing such a stage
        par = {i: i for i in range(len(star))}
        def f(i):
            while par[i] != i: i = par[i]
            return i
        active = set()
        for t in range(k):
            idx = [i for i, (r, q) in enumerate(star) if t in q]
            os_ = [next(iter(Eset(star[i][1]) - C)) for i in idx]
            idx = [i for i, o in zip(idx, os_) if os_.count(o) == 1]   # distinct partners -> pairwise E-intersections = C
            if len(idx) >= 3:
                active |= set(idx)
                for i in idx[1:]: par[f(i)] = f(idx[0])
        # closure [P]: a star piece sharing a stage with a class member (distinct partners, so E-intersection = C) has
        # b_member . a_q = 0 with b_member a nonzero vector on l^perp, hence a_q on l: it joins the class (and classes merge).
        part = lambda i: next(iter(Eset(star[i][1]) - C))
        changed = True
        while changed and active:
            changed = False
            for i in range(len(star)):
                for j in list(active):
                    if i == j or f(i) == f(j) and i in active: continue
                    if (star[i][1] & star[j][1]) and part(i) != part(j):
                        if i not in active: active.add(i); par[f(i)] = f(j); changed = True
                        elif f(i) != f(j): par[f(i)] = f(j); changed = True
        # TRIANGLE seed [P]: STAR-3 only needs b_i.a_j = 0 for i != j, i.e. the three pieces PAIRWISE share a stage
        # (distinct partners), not one common stage.
        adj = lambda i, j: bool(star[i][1] & star[j][1]) and part(i) != part(j)
        for i, j, l in itertools.combinations(range(len(star)), 3):
            if adj(i, j) and adj(j, l) and adj(i, l):
                for x in (i, j, l): active.add(x)
                par[f(j)] = f(i); par[f(l)] = f(i)
        changed = True
        while changed and active:
            changed = False
            for i in range(len(star)):
                for j in list(active):
                    if i != j and adj(i, j) and (i not in active or f(i) != f(j)):
                        active.add(i); par[f(i)] = f(j); changed = True
        classes = {}
        for i in active: classes.setdefault(f(i), []).append(i)
        supp = frozenset().union(*[R[c][0] for c in C])
        for cl in classes.values():
            rows = []
            mem = []      # (piece set, E, partner)
            for i in cl:
                r, q = star[i]; o = next(iter(Eset(q) - C)); mem.append((q, Eset(q), o))
                if R[o][0] == q: rows.append(q)       # o's row = c * h|q  -> zero block sum on q
            # STAR-EXT [P]: a piece q (E(q) >= C) sharing a stage with a member p, E(p) n E(q) = C, has a_q on l, b_q on l^perp;
            # then for members p' at a shared stage with E(p') n E(q) = C u {o_p'}: x_q[o_p'] = y_q[o_p'] = 0 (partner coeff != 0).
            # If one role o remains outside C with M_o = q, o's row = c h|q (c != 0): q joins (zero-sum row, propagates).
            grow = True
            while grow:
                grow = False
                for r, q in pieces:
                    if len(q) < 2 or any(q == mq for mq, _, _ in mem): continue
                    Eq = Eset(q)
                    if not C <= Eq: continue
                    if not any((q & mq) and (Eq & mE) == C for mq, mE, mo in mem): continue
                    rem = {mo for mq, mE, mo in mem if (q & mq) and (Eq & mE) == C | {mo}}
                    rest = Eq - C - rem
                    if len(rest) == 1:
                        o = next(iter(rest))
                        if R[o][0] == q:
                            mem.append((q, Eq, o)); rows.append(q); grow = True
            if not rows: continue
            # linear system over scalar h_s: sum_{s in q} h_s = 0 (q in rows), sum_s h_s = 0, h_s = 0 off supp
            var = sorted(supp); idx = {s: j for j, s in enumerate(var)}
            A = [[Fr(1 if s in q else 0) for s in var] for q in rows] + [[Fr(1)]*len(var)]
            # nullspace basis by exact Gaussian elimination
            m = [row[:] for row in A]; piv = []; rk = 0
            for c in range(len(var)):
                p = next((i for i in range(rk, len(m)) if m[i][c] != 0), None)
                if p is None: continue
                m[rk], m[p] = m[p], m[rk]
                for i in range(len(m)):
                    if i != rk and m[i][c] != 0:
                        fct = m[i][c]/m[rk][c]; m[i] = [a - fct*b for a, b in zip(m[i], m[rk])]
                piv.append(c); rk += 1
            free = [c for c in range(len(var)) if c not in piv]
            # a stage s is forced zero iff every nullspace basis vector vanishes there
            basis = []
            for fc in free:
                v = [Fr(0)]*len(var); v[fc] = Fr(1)
                for i, pc in enumerate(piv): v[pc] = -m[i][fc]/m[i][pc]
                basis.append(v)
            for q in rows:
                if all(all(b[idx[s]] == 0 for s in q) for b in basis):
                    kills.append(('STARZERO', tuple(sorted(C)), tuple(sorted(q)))); break
    return kills

"""CHAINBOUND chain.py (own code).  Chain-cover bounds on #7615's helper-layer D0 given per-frame needs B_G (needs.pkl).
Helper cost (PRICEKIT native rule, monotone climb a=p0<p1<..<pk<p_{k+1}=b):  D(h) = f(b-a) - sum f(p_{i+1}-p_i), f(r)=r ln r.
(1) free endpoints: exhaustive check that D(h) >= k*f(2) for k interior stops (all chains in dims 0..9), so splitting into
    singletons is never worse: min chain cover = f(2)*sum B_G (Dilworth adds nothing).
(2) conditional C2: the multiset of helper (start dim, end dim) pairs is #7615's (1,101 helpers), frames free.
    Telescoping with fixed a: D(h) = sum_i g_a(p_i,p_{i+1}),  g_a(p,q) = f(q-a)-f(p-a)-f(q-p) >= 0.
    LP: one flow commodity per (a,b) class of value N_ab through need frames (a<dim<b) along strict inclusions;
    coverage sum_classes inflow(G) >= B_G.  Stops at non-need frames are dropped (removing a stop never raises D).
    Integer chain covers are feasible LP points, so LP opt is a lower bound; certified via the dual (Lagrangian bound).
(3) reference C1: every helper {0}->V, count free (single commodity, a=0,b=9)."""
import pickle, math, itertools, collections, sys
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix
f = lambda r: r * math.log(r) if r > 0 else 0.0
D = pickle.load(open('needs.pkl', 'rb')); out = D['out']; keys = D['keys']; dimk = D['dimk']
# ---- (1) exhaustive per-stop check
worst = 1e9
for a in range(10):
    for b in range(a + 2, 10):
        mids = range(a + 1, b)
        for k in range(1, b - a):
            for S in itertools.combinations(mids, k):
                p = [a, *S, b]
                d = f(b - a) - sum(f(p[i + 1] - p[i]) for i in range(len(p) - 1))
                worst = min(worst, d - k * f(2))
print('(1) min over all chains of D - k*f(2) = %.12f (>=0 required)' % worst)
sumB = sum(o['B'] for o in out.values())
print('(1) free-endpoint chain-cover bound = f(2)*%d = %.4f' % (sumB, f(2) * sumB))
# ---- need frames and strict inclusions
need = sorted(G for G, o in out.items() if o['B'] > 0)
mask = {G: sum(1 << x for x in keys[G]) for G in need}   # span as bitset over 512 vectors
dim = {G: dimk[G] for G in need}
inc = [(G, H) for G in need for H in need if dim[G] < dim[H] and mask[G] & ~mask[H] == 0]
print('need frames', len(need), 'strict inclusions', len(inc))
def solve(classes, label):
    """classes: {(a,b): N}.  Returns certified lower bound."""
    var = []; cost = []; ub = []
    for (a, b), N in classes.items():
        g = lambda p, q: f(q - a) - f(p - a) - f(q - p)
        nodes = [G for G in need if a < dim[G] < b]; ns = set(nodes)
        var.append(((a, b), 's', 't')); cost.append(0.0); ub.append(N)
        for G in nodes:
            var.append(((a, b), 's', G)); cost.append(g(a, dim[G])); ub.append(N)
            var.append(((a, b), G, 't')); cost.append(g(dim[G], b)); ub.append(N)
        for G, H in inc:
            if G in ns and H in ns:
                var.append(((a, b), G, H)); cost.append(g(dim[G], dim[H])); ub.append(N)
    nv = len(var); print(label, 'vars', nv)
    eq_rows = {}; er = []; ec = []; ev = []; beq = []
    def eqrow(k, rhs):
        if k not in eq_rows: eq_rows[k] = len(beq); beq.append(rhs)
        return eq_rows[k]
    ur = []; uc = []; uv = []; bub = []; urow = {}
    for G in need:
        urow[G] = len(bub); bub.append(-out[G]['B'])
    for j, (c, u, v) in enumerate(var):
        if u == 's': r = eqrow((c, 's'), classes[c]); er.append(r); ec.append(j); ev.append(1.0)
        else: r = eqrow((c, u), 0.0); er.append(r); ec.append(j); ev.append(-1.0)   # out of u
        if v != 't':
            r = eqrow((c, v), 0.0); er.append(r); ec.append(j); ev.append(1.0)          # into v
            ur.append(urow[v]); uc.append(j); uv.append(-1.0)
    Aeq = coo_matrix((ev, (er, ec)), shape=(len(beq), nv)).tocsr()
    Aub = coo_matrix((uv, (ur, uc)), shape=(len(bub), nv)).tocsr()
    c = np.array(cost); beq = np.array(beq); bub = np.array(bub); U = np.array(ub, float)
    res = linprog(c, A_ub=Aub, b_ub=bub, A_eq=Aeq, b_eq=beq, bounds=list(zip([0] * nv, ub)), method='highs')
    print(label, res.status, res.message[:60], 'opt %.4f' % res.fun)
    y = res.eqlin.marginals; z = np.minimum(res.ineqlin.marginals, 0)
    red = c - Aeq.T @ y - Aub.T @ z
    LB = beq @ y + bub @ z + np.sum(np.minimum(red, 0) * U)
    print(label, 'certified Lagrangian LB %.4f' % LB)
    return res, LB, var
ends = D['ends']; cls = collections.Counter(ends.values())
print('#7615 helper (start,end) dim census', sorted(cls.items()))
res2, LB2, var2 = solve(dict(cls), 'C2')
res1, LB1, var1 = solve({(0, 9): len(ends)}, 'C1(ref)')
# #7615's own value under each model: its chains restricted to need frames (a feasible point of C2)
ns = set(need); own = 0.0; full = 0.0
for h, ch in D['chain'].items():
    a, b = ends[h]; p = [a] + [dimk[x] for x in ch[1:-1] if x in ns] + [b]
    own += f(b - a) - sum(f(p[i + 1] - p[i]) for i in range(len(p) - 1))
    q = [dimk[x] for x in ch]; full += f(q[-1] - q[0]) - sum(f(q[i + 1] - q[i]) for i in range(len(q) - 1))
print('#7615 helper D0 %.4f ; same chains with non-need stops dropped %.4f' % (full, own))
# stop usage in C2 optimum
x = res2.x; byd = collections.Counter()
for j, (c, u, v) in enumerate(var2):
    if v != 't' and x[j] > 1e-9: byd[c] += x[j]
print('C2 optimum: stops per class', {k: round(v, 2) for k, v in sorted(byd.items())})
pickle.dump(dict(LB1=LB1, LB2=LB2, opt1=res1.fun, opt2=res2.fun, own=own, full=full, sumB=sumB), open('chain.pkl', 'wb'))

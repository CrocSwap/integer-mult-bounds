"""model: the gauge44-lineage frame model with every constraint of independent/audit_local.py:
monotone chains, fixed starts/ends, target hyperplane caps, cut equality (center frames, target levels),
tails inside helper_final, and the final helper row/column cones as end-of-B caps.  Cones depend only on the
prefix scalar map, which read-set exchanges preserve, so caps are computed once per base word."""
import importlib.util, gzip, json, sys, time
import frames as F
from word import inline
V = 112
from paths import AUDIT_LOCAL as AUD
sp = importlib.util.spec_from_file_location("g44_audit", AUD); aud = importlib.util.module_from_spec(sp); sp.loader.exec_module(aud)
FULL = tuple(1 << i for i in range(9))
def meet(a, b):
    """intersection of two subspaces (as bases)."""
    pa = set(F.span(tuple(a))); return F.basis(tuple(x for x in F.span(tuple(b)) if x in pa))
def cone_caps(w):
    Fr = aud.F; R = w['report']['R']; n = 2 * V + R; ident = lambda: [{k: Fr(1)} for k in range(n)]
    main = w['A'] + w['cut'] + w['B']; raw = ident()
    for e in main: aud.apply(e, raw)
    dirt = [{} for _ in range(n)]
    for y in range(V, 2 * V): dirt[y] = {k: a for k, a in raw[y].items() if k >= 2 * V}
    for e in w['precondition']: aud.apply(e, dirt)
    compensation = [['add', y, k, -a.numerator, a.denominator, []] for y in range(V, 2 * V) for k, a in sorted(dirt[y].items())]
    prefix = w['precondition'] + compensation + main
    p = ident(); pinv = ident()
    for e in prefix: aud.apply(e, p)
    for e in reversed(prefix): aud.apply(aud.invert(e), pinv)
    end = [FULL] * V + [tuple(F.G.perp(pp)) for pp in w['ports']] + [FULL] * R
    for q, U in w.get('helper_final', {}).items(): end[int(q)] = F.basis(tuple(U))
    caps = {}
    for q in map(int, w.get('helper_final', {})):
        U = end[q]
        for k in set(pinv[q]) | {k for k in range(n) if p[k].get(q)}:
            if k != q: caps[k] = meet(caps.get(k, FULL), U)
    return {k: c for k, c in caps.items() if c != FULL}, compensation
def model(word, caps, check_literal=True, tail_mutable=True):
    return F.Graph(inline(word, True), check_literal=check_literal, tail_mutable=tail_mutable, caps=caps, cut_equality=True)
if __name__ == "__main__":
    # usage: python -B model.py FULL-WORD.json.gz [ENDPOINT_B]   (cone caps + exact frame optimum under every audit constraint)
    from harness import DEFAULT_B
    word = json.load(gzip.open(sys.argv[1])); b = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_B
    t0 = time.time(); caps, comp = cone_caps(word)
    print(f"cone caps computed in {time.time()-t0:.1f}s: {len(caps)} capped registers; cap dims {sorted(__import__('collections').Counter(len(c) for c in caps.values()).items())}; compensation gates {len(comp)}")
    costs = F.Costs(b); t0 = time.time(); g = model(word, caps)
    r = F.optimal_frames(inline(word, True), costs, check_literal=True, graph=g)
    print(f"full-constraint model: vars {len(g.var)} comps {len(g.components)} | literal {r['literal_cost']} optimal {r['cost']} gain {r['gain']} certified {r['certified']} | profile {dict(sorted(r['profile'].items()))} | {time.time()-t0:.1f}s")

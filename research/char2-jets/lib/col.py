import itertools
def rk(rows):
    piv=[]
    for x in rows:
        for p in piv: x=min(x,x^p)
        if x: piv.append(x); piv.sort(reverse=True)
    return len(piv)
def col_split(B, D):
    """principal split: colouring c(t) in D(t) with every B[L_c,L_c] nonsingular over F2. Returns colouring or None."""
    v=len(B)
    for ch in itertools.product(*[sorted(D[t]) for t in range(v)]):
        ok=True
        for c in range(3):
            L=[t for t in range(v) if ch[t]==c]
            if rk([sum(B[t][s]<<i for i,s in enumerate(L)) for t in L])<len(L): ok=False; break
        if ok: return ch
    return None

"""Root lines of the units A_n, D_n, E6, E7, E8 in pure Python (integer coordinates scaled by 2, so the half-integer E8 roots are integral).
A 'line' is a root up to sign; lines are returned with first nonzero coordinate positive, in a fixed generation order."""
import itertools
def canon(r):
    f = next(x for x in r if x)
    return tuple(r) if f > 0 else tuple(-x for x in r)
def lines(R):
    seen = set(); out = []
    for r in R:
        c = canon(r)
        if c not in seen: seen.add(c); out.append(c)
    return out
def A(n):
    R = []
    for i in range(n + 1):
        for j in range(i + 1, n + 1):
            v = [0] * (n + 1); v[i] = 2; v[j] = -2; R.append(v)
    return lines(R)
def D(n):
    R = []
    for i in range(n):
        for j in range(i + 1, n):
            for s in (2, -2):
                v = [0] * n; v[i] = 2; v[j] = s; R.append(v)
    return lines(R)
def E8():
    R = [list(r) for r in D(8)]
    for sg in itertools.product((1, -1), repeat=8):
        if sg.count(-1) % 2 == 0: R.append(list(sg))
    return lines(R)
def dot(a, b): return sum(x * y for x, y in zip(a, b))
def E7():
    return [r for r in E8() if sum(r) == 0]          # orthogonal to s = (1,...,1)/2
def E6():
    r1 = [2, -2, 0, 0, 0, 0, 0, 0]; r2 = [0, 2, -2, 0, 0, 0, 0, 0]   # <r1,r2> = -1 in the root normalisation: an A2
    return [r for r in E8() if dot(r, r1) == 0 and dot(r, r2) == 0]
def unit(name):
    return {'D4': lambda: D(4), 'D5': lambda: D(5), 'D6': lambda: D(6), 'A4': lambda: A(4), 'A5': lambda: A(5), 'A6': lambda: A(6),
            'E6': E6, 'E7': E7, 'E8': E8}[name]()

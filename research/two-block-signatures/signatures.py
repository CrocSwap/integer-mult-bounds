"""Construct two-block support signatures. SHIN09-git with OpenAI Codex assistance, Apache-2.0."""
from dataclasses import dataclass
from math import comb

# A=1, B=2, M=3. Each nibble is 4*source+reader, as in PR3997.
AA, AM, MA, BB, BM, MB, MM = 5, 7, 13, 10, 11, 14, 15
TYPES = (AA, AM, MA, BB, BM, MB, MM)


@dataclass(frozen=True)
class Profile:
    aa: int
    am: int
    ma: int
    bb: int
    bm: int
    mb: int
    mm: int

    def symbols(self):
        counts = (self.aa, self.am, self.ma, self.bb, self.bm, self.mb, self.mm)
        return tuple(s for s, count in zip(TYPES, counts, strict=True) for _ in range(count))

    def free(self, p, q):
        return p-self.aa-self.am-self.ma, q-self.bb-self.bm-self.mb


def profiles(n, prefix=()):
    if len(prefix) == 6:
        yield Profile(*prefix, n)
        return
    for k in range(n+1):
        yield from profiles(n-k, prefix+(k,))


def multiplicity(symbols):
    total, ways = len(symbols), 1
    for s in TYPES:
        count = symbols.count(s)
        ways *= comb(total, count)
        total -= count
    return ways


def verdict(p, q, v, binary=False):
    """Assumes the seven valid symbol types, nonnegative counts and total p+q."""
    u, w = v.free(p, q)
    if u < 0 or w < 0:
        return "capacity"
    if (p-v.aa-v.ma == 0) != (q-v.bb-v.bm == 0):
        return "A saturation"
    if (q-v.bb-v.mb == 0) != (p-v.aa-v.am == 0):
        return "B saturation"
    if not binary or u*w % 2 == 0 or min(u,w) > 1:
        return "ok"
    if u == w == 1:
        return "ok" if (v.am and v.mb) or (v.ma and v.bm) else "binary 1x1"
    if u == 1:
        return "ok" if v.am or v.ma else "binary one A"
    return "ok" if v.mb or v.bm else "binary one B"


def describe(p, q, symbols):
    if type(p) is not int or type(q) is not int or min(p,q) < 1 or len(symbols) != p+q:
        raise ValueError("two positive block sizes must sum to signature length")
    if any(type(s) is not int or s not in TYPES for s in symbols):
        raise ValueError("forbidden source-reader type")
    return Profile(*(symbols.count(s) for s in TYPES))


def witness(p, q, symbols, field="Q"):
    """Rows are A pivots followed by B pivots. Columns keep the supplied labels."""
    v = describe(p, q, symbols)
    if field not in ("Q", "F2", "F3", "F4"):
        raise ValueError("unsupported witness field")
    why = verdict(p, q, v, binary=field == "F2")
    if why != "ok":
        raise ValueError(why)
    u, w = v.free(p, q)
    free = [j for j, s in enumerate(symbols) if s == MM]
    left = [j for j, s in enumerate(symbols) if s in (AA, AM, MA)] + free[:u]
    right = [j for j, s in enumerate(symbols) if s in (BB, BM, MB)] + free[u:]
    n = p+q
    rows = [[int(j == i) for j in range(n)] for i in left+right]
    scalar = {"Q": -1, "F2": 1, "F3": 2 if u*w%3 == 1 else 1,
              "F4": 2 if u*w%2 else 1}[field]
    for i, ix in enumerate(left):
        for j, jx in enumerate(right):
            rows[i][jx] = int(symbols[ix] % 4 != 1 and symbols[jx] // 4 != 2)
            rows[p+j][ix] = scalar*int(symbols[jx] % 4 != 2 and symbols[ix] // 4 != 1)
    if field == "F2" and u*w % 2:
        ix, jx = free[0], free[u]
        remove_x = ((u > 1 and w > 1) or (u == 1 and w > 1 and v.am > 0)
                    or (w == 1 and u > 1 and v.mb > 0) or (u == w == 1 and v.am*v.mb > 0))
        if remove_x:
            rows[left.index(ix)][jx] = 0
        else:
            rows[p+right.index(jx)][ix] = 0
    return tuple(tuple(row) for row in rows)


def code(symbols):
    return sum(s << (4*j) for j,s in enumerate(symbols))

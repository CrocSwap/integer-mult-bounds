"""Exact rank-drop depth of one-parameter elementary shears.

Polynomials are tuples of integers, lowest degree first. The numeric depth
oracle factors the gap with integer row operations. The symbolic walk uses
fraction-free elimination over Z[c].
"""
from fractions import Fraction
from math import gcd

"""Fraction-free Bareiss elimination over Z[c], tuples of ints."""
from fractions import Fraction

def trim(a):
    a=list(a)
    while len(a)>1 and a[-1]==0:
        a.pop()
    return tuple(a)

def add(a,b):
    n=max(len(a),len(b))
    o=[0]*n
    for i,x in enumerate(a): o[i]+=x
    for i,x in enumerate(b): o[i]+=x
    return trim(o)

def sub(a,b):
    return add(a, tuple(-x for x in b))

def mul(a,b):
    if a==(0,) or b==(0,):
        return (0,)
    o=[0]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        if not x: continue
        for j,y in enumerate(b):
            if y: o[i+j]+=x*y
    return trim(o)

def scale(a,k):
    if k==0 or a==(0,):
        return (0,)
    if k==1:
        return a
    return trim(tuple(x*k for x in a))

def eq(a,b):
    return trim(a)==trim(b)

def is_zero(a):
    return a==(0,) or a==() 

def exact_quo(a,b):
    """Exact quotient in Z[c]. b divides a."""
    a=list(trim(a)); b=list(trim(b))
    if b==[0]:
        raise ZeroDivisionError
    if a==[0]:
        return (0,)
    if len(a)<len(b):
        raise ValueError("not divisible deg")
    out=[0]*(len(a)-len(b)+1)
    lead=b[-1]
    for k in range(len(out)-1,-1,-1):
        coef=a[k+len(b)-1]
        if coef % lead != 0:
            raise ValueError("not divisible lead %s / %s"%(coef,lead))
        q=coef//lead
        out[k]=q
        if q:
            for i,bv in enumerate(b):
                a[k+i]-=q*bv
    if any(a):
        raise ValueError("remainder")
    return trim(out)

def const(k):
    return (int(k),)

ZERO=(0,)
ONE=(1,)


def rank_of(matrix):
    work = [row[:] for row in matrix]
    height = len(work)
    width = len(work[0])
    rank = 0
    column = 0
    while rank < height and column < width:
        pivot = next((row for row in range(rank, height) if work[row][column] != 0), None)
        if pivot is None:
            column += 1
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        pivot_value = work[rank][column]
        for row in range(height):
            if row == rank or work[row][column] == 0:
                continue
            factor = work[row][column] / pivot_value
            for index in range(column, width):
                work[row][index] -= factor * work[rank][index]
        rank += 1
        column += 1
    return rank

def apply_shear(matrix, target, source, coefficient):
    out = [row[:] for row in matrix]
    for column in range(len(matrix)):
        out[target][column] += coefficient * out[source][column]
    return out

def left_peel(matrix, target, source, coefficient):
    return apply_shear(matrix, target, source, -coefficient)

def eye(size):
    return [[Fraction(int(i == j)) for j in range(size)] for i in range(size)]


def content(poly):
    g = 0
    for coef in poly:
        g = gcd(g, coef)
    return g or 1

def divc(poly):
    poly = trim(poly)
    g = content(poly)
    if g == 1:
        return poly
    return tuple(coef // g for coef in poly)

def neg(poly):
    return trim(tuple(-coef for coef in poly))

def ev(poly, value):
    acc = Fraction(0)
    power = Fraction(1)
    for coef in poly:
        if coef:
            acc += coef * power
        power *= value
    return acc

def prem(a, b):
    A = [Fraction(x) for x in trim(a)]
    B = [Fraction(x) for x in trim(b)]
    if is_zero(tuple(int(x) for x in B) if False else b):
        raise ZeroDivisionError
    while len(A) >= len(B):
        if not A or A[-1] == 0:
            if A:
                A.pop()
            else:
                break
            continue
        factor = A[-1] / B[-1]
        shift = len(A) - len(B)
        for i, bv in enumerate(B):
            A[i + shift] -= factor * bv
        while A and A[-1] == 0:
            A.pop()
        if not A:
            A = [Fraction(0)]
    den = 1
    for x in A:
        den = den * x.denominator // gcd(den, x.denominator)
    return divc(trim(tuple(int(x * den) for x in A)))

def pgcd(a, b):
    a, b = divc(trim(a)), divc(trim(b))
    if is_zero(a):
        return b if not is_zero(b) else (1,)
    if is_zero(b):
        return a
    while not is_zero(b):
        a, b = b, divc(prem(a, b))
        if len(a) > 40:
            raise RuntimeError("gcd degree %s" % len(a))
    if a[-1] < 0:
        a = neg(a)
    return a

def cancel(n, d):
    g = pgcd(n, d)
    if len(g) == 1 and abs(g[0]) == 1:
        return n, d
    return exact_quo(n, g), exact_quo(d, g)

class RF:
    __slots__ = ("n", "d")
    def __init__(self, n, d=None):
        n = trim(n)
        d = ONE if d is None else trim(d)
        if is_zero(d):
            raise ZeroDivisionError("zero den")
        if d[-1] < 0:
            n, d = neg(n), neg(d)
        g = gcd(content(n), content(d))
        if g > 1:
            n = tuple(x // g for x in n)
            d = tuple(x // g for x in d)
        n, d = cancel(n, d)
        self.n = n
        self.d = d
    def __add__(self, other):
        return RF(add(mul(self.n, other.d), mul(other.n, self.d)), mul(self.d, other.d))
    def __sub__(self, other):
        return RF(sub(mul(self.n, other.d), mul(other.n, self.d)), mul(self.d, other.d))
    def __mul__(self, other):
        return RF(mul(self.n, other.n), mul(self.d, other.d))
    def __truediv__(self, other):
        if is_zero(other.n):
            raise ZeroDivisionError("div0")
        return RF(mul(self.n, other.d), mul(self.d, other.n))
    def ev(self, value):
        return ev(self.n, value) / ev(self.d, value)
    def is_zero(self):
        return is_zero(self.n)

def eliminate(rows, rhs_columns):
    """rhs_columns: list of columns, each a list of n polys (row-major per column)."""
    n = len(rows)
    k = len(rhs_columns)
    A = [[rows[i][j] for j in range(n)] + [rhs_columns[c][i] for c in range(k)] for i in range(n)]
    prev = ONE
    rank = 0
    pivot_of_row = {}
    witnesses = []
    col = 0
    while rank < n and col < n:
        piv = next((i for i in range(rank, n) if not is_zero(A[i][col])), None)
        if piv is None:
            col += 1
            continue
        if piv != rank:
            A[rank], A[piv] = A[piv], A[rank]
        pivval = A[rank][col]
        witnesses.append(trim(pivval))
        for i in range(rank + 1, n):
            factor = A[i][col]
            nrow = [ZERO] * col
            for j in range(col, n + k):
                num = sub(mul(pivval, A[i][j]), mul(factor, A[rank][j]))
                nrow.append(exact_quo(num, prev))
            A[i] = nrow
        prev = pivval
        pivot_of_row[rank] = col
        rank += 1
        col += 1
    return A, rank, pivot_of_row, witnesses

def backsolve(A, rank, pivot_of_row, rhs_index, n):
    xs = [RF(ZERO) for _ in range(n)]
    col_rhs = n + rhs_index
    for r in range(rank - 1, -1, -1):
        col = pivot_of_row[r]
        acc = RF(A[r][col_rhs])
        for j in range(col + 1, n):
            if not is_zero(A[r][j]):
                acc = acc - RF(A[r][j]) * xs[j]
        xs[col] = acc / RF(A[r][col])
    return xs

_ROOTS = {}

def rat_roots(poly):
    """Every rational root. Degree 1 is the slope ratio. Degree 2 uses the
    discriminant: an integer quadratic has a rational root exactly when its
    discriminant is a perfect square. Higher degree uses the rational-root
    theorem with a complete factorization of coefficients below 2^64.
    """
    poly = divc(trim(poly))
    STATS["maxrootdeg"] = max(STATS.get("maxrootdeg", 0), max(0, len(poly) - 1))
    cached = _ROOTS.get(poly)
    if cached is not None:
        return cached
    found = _rat_roots_body(poly)
    _ROOTS[poly] = found
    return found

def _rat_roots_body(poly):
    if len(poly) > 3:
        for coef in poly:
            if abs(coef).bit_length() > 64:
                raise RuntimeError(
                    "degree %s coefficient has %s bits; factorization is not certified"
                    % (len(poly) - 1, abs(coef).bit_length()))
    if is_zero(poly) or len(poly) == 1:
        return []
    if len(poly) == 2:
        return [Fraction(-poly[0], poly[1])]
    if len(poly) == 3:
        # Coefficients are lowest degree first: constant, linear, leading.
        constant, linear, leading = poly
        disc = linear * linear - 4 * leading * constant
        if disc < 0:
            return []
        root = _isqrt(disc)
        if root * root != disc:
            return []
        found = [Fraction(-linear + root, 2 * leading), Fraction(-linear - root, 2 * leading)]
        for cand in found:
            if ev(poly, cand) != 0:
                raise RuntimeError("quadratic formula missed %s" % cand)
        return _uniq(found)
    g = content(poly)
    poly = tuple(c // g for c in poly)
    if poly[0] == 0:
        return _uniq([Fraction(0)] + rat_roots(poly[1:]))
    ps = divisors(abs(poly[0]))
    qs = divisors(abs(poly[-1]))
    roots = []
    for p in ps:
        for q in qs:
            for sign in (1, -1):
                cand = Fraction(sign * p, q)
                if ev(poly, cand) == 0:
                    roots.append(cand)
    return _uniq(roots)

def _isqrt(n):
    if n < 0:
        raise ValueError("negative")
    x = int(n ** 0.5) if n.bit_length() < 1000 else 1 << ((n.bit_length() + 1) // 2)
    while True:
        y = (x + n // x) // 2 if x else n
        if y >= x:
            return x
        x = y

def _uniq(vals):
    out, seen = [], set()
    for v in vals:
        if v not in seen:
            seen.add(v)
            out.append(v)
    return out

_div_cache = {}

def divisors(n):
    n = abs(int(n))
    if n in _div_cache:
        return _div_cache[n]
    factors = factorize(n)
    divs = [1]
    i = 0
    while i < len(factors):
        p = factors[i]
        e = 0
        while i < len(factors) and factors[i] == p:
            e += 1
            i += 1
        power = 1
        extra = []
        for _ in range(e):
            power *= p
            extra.extend(d * power for d in divs)
        divs.extend(extra)
    _div_cache[n] = divs
    return divs

def factorize(n):
    n = abs(int(n))
    factors = []
    for p in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47):
        while n % p == 0:
            factors.append(p)
            n //= p
    if n > 1:
        factors.extend(_split(n))
    factors.sort()
    return factors

def _split(n):
    if n == 1:
        return []
    if _prime(n):
        return [n]
    d = _rho(n)
    if d is None or d == n:
        raise RuntimeError("failed to factor %s bits" % n.bit_length())
    return _split(d) + _split(n // d)

def _rho(n):
    if n % 2 == 0:
        return 2
    for c in (1, 3, 5, 7, 11, 13):
        x = y = 2
        d = 1
        while d == 1:
            x = (x * x + c) % n
            y = (y * y + c) % n
            y = (y * y + c) % n
            d = gcd(abs(x - y), n)
        if 1 < d < n:
            return d
    return None

def _prime(n):
    """Deterministic Miller-Rabin for n < 2^64. Larger integers are refused."""
    if n < 2:
        return False
    if n >= 1 << 64:
        raise RuntimeError("primality above 2^64 is not certified here")
    small = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)
    for p in small:
        if n == p:
            return True
        if n % p == 0:
            return False
    # Jim Sinclair's base set decides every integer below 2^64.
    d = n - 1
    s = 0
    while d % 2 == 0:
        s += 1
        d //= 2
    for a in (2, 3, 5, 7, 11, 13, 23, 29, 31, 37):
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(s - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True

def _solve_scaled(matrix, rhs_scale):
    """Solve matrix x = rhs_scale e_k over Q for each k. matrix has integer entries."""
    width = len(matrix)
    work = [matrix[i][:] + [rhs_scale if i == k else 0 for k in range(width)] for i in range(width)]
    span = 2 * width
    pivot_of = {}
    row = 0
    col = 0
    while row < width and col < width:
        piv = None
        for i in range(row, width):
            if work[i][col] != 0:
                piv = i
                break
        if piv is None:
            col += 1
            continue
        if piv != row:
            work[row], work[piv] = work[piv], work[row]
        pivot_value = work[row][col]
        for i in range(width):
            if i == row:
                continue
            factor = work[i][col]
            if factor == 0:
                continue
            g = gcd(factor, pivot_value)
            mul_row = pivot_value // g
            mul_piv = factor // g
            pivot_row = work[row]
            # Scale the whole row. Entries left of the pivot are not zero on
            # earlier pivot rows, and mul_row need not be 1.
            updated = [mul_row * work[i][j] - mul_piv * pivot_row[j] for j in range(span)]
            g2 = 0
            for value in updated:
                g2 = gcd(g2, value)
            if g2 > 1:
                updated = [value // g2 for value in updated]
            work[i] = updated
        pivot_of[col] = row
        row += 1
        col += 1
    sols = []
    for k in range(width):
        inconsistent = False
        for i in range(width):
            if work[i][width + k] == 0:
                continue
            if all(work[i][j] == 0 for j in range(width)):
                inconsistent = True
                break
        if inconsistent:
            sols.append(None)
            continue
        solution = [Fraction(0) for _ in range(width)]
        # Other pivot columns were cleared, and free variables stay 0, so each
        # pivot row contributes exactly rhs / pivot.
        for column, index in pivot_of.items():
            solution[column] = Fraction(work[index][width + k], work[index][column])
        sols.append(solution)
    return sols


def batch_edges(matrix):
    """Every left rank-drop step, from one integer factorization of the gap and one of its transpose."""
    n = len(matrix)
    den = 1
    for row in matrix:
        for entry in row:
            den = den * entry.denominator // gcd(den, entry.denominator)
    # G = N / den, so G x = e_k iff N x = den e_k. Rank and images agree.
    numeric = [[int((matrix[i][j] - (1 if i == j else 0)) * den) for j in range(n)] for i in range(n)]
    columns = _solve_scaled(numeric, den)
    transposed = [[numeric[r][c] for r in range(n)] for c in range(n)]
    rows = _solve_scaled(transposed, den)
    edges = []
    for target in range(n):
        if columns[target] is None:
            continue
        for source in range(n):
            if target == source or rows[source] is None:
                continue
            pairing = rows[source][target]
            if pairing == 0:
                continue
            edges.append((target, source, 1 / pairing))
    return edges


def depth_matrix(matrix, memo):
    key = tuple(tuple(row) for row in matrix)
    hit = memo.get(key)
    if hit is not None:
        return hit
    steps = batch_edges(matrix)
    if not steps:
        memo[key] = 0
        return 0
    best = 0
    for target, source, coefficient in steps:
        child = left_peel(matrix, target, source, coefficient)
        best = max(best, 1 + depth_matrix(child, memo))
    memo[key] = best
    return best

def matrix_from_gap(gap):
    size = len(gap)
    return [[gap[i][j] + (1 if i == j else 0) for j in range(size)] for i in range(size)]

STATS = {"nodes": 0, "maxdeg": 0, "maxbits": 0, "roots": 0, "maxrootdeg": 0}
MEMO = {}

def pencil_rows(matrix, target, source):
    size = len(matrix)
    clear = 1
    for row in matrix:
        for entry in row:
            clear = clear * entry.denominator // gcd(clear, entry.denominator)
    rows = []
    for i in range(size):
        row = []
        for j in range(size):
            base = matrix[i][j] - (1 if i == j else 0)
            if i != target:
                row.append(const(int(base * clear)))
            else:
                row.append(trim((int(base * clear), int(-matrix[source][j] * clear))))
        rows.append(row)
    return rows, const(clear), size

def depth_at_rows(rows, den, size, value, memo):
    den_v = ev(den, value)
    if den_v == 0:
        raise RuntimeError("denominator vanished")
    gap = [[ev(rows[i][j], value) / den_v for j in range(size)] for i in range(size)]
    return depth_matrix(matrix_from_gap(gap), memo), rank_of(gap)

def _lower_rank_hits(rows, den, size, witnesses, rank_target):
    """Generic rank is above the stall rank, so only top-pivot roots can preserve it."""
    roots = []
    for poly in witnesses:
        roots.extend(rat_roots(poly))
    roots = [root for root in _uniq(roots) if root != 0]
    best = -1
    where = None
    for root in roots:
        depth, rank = depth_at_rows(rows, den, size, root, MEMO)
        if rank == rank_target and depth > best:
            best = depth
            where = (root, rank)
    return best, where, 0, len(roots), STATS

def certified_max_depth(matrix, target, source, rank_target=None):
    """Max of δ((I - c E_{target,source}) matrix) over c in Q, and the argmax.

    If rank_target is set, only c that keep rank(gap) == rank_target matter.
    A specialization cannot raise rank above the generic rank, so a pencil whose
    generic rank is below the target contributes nothing, and one whose generic
    rank is above the target can hit the target only at roots of the top pivots.
    """
    rows, den, size = pencil_rows(matrix, target, source)
    if rank_target is not None:
        _A, rank, _piv, witnesses = eliminate(rows, [])
        if rank < rank_target:
            return -1, None, 0, 0, STATS
        if rank > rank_target:
            return _lower_rank_hits(rows, den, size, witnesses, rank_target)
    polys = []
    generic = walk(rows, den, polys, size, 0)
    roots = []
    for poly in polys:
        roots.extend(rat_roots(poly))
    roots = [r for r in _uniq(roots) if r != 0]
    memo = MEMO
    def depth_at(value):
        gap = []
        den_v = ev(den, value)
        for i in range(size):
            gap.append([ev(rows[i][j], value) / den_v for j in range(size)])
        # rows/den is the TRUE gap only at the top call, where den is the
        # constant clear and rows are clear * gap. Yes.
        return depth_matrix(matrix_from_gap(gap), memo), rank_of_local(gap)
    # The top `rows/den` equals the true gap. Children are not evaluated here.
    best = -1
    where = None
    # generic sample
    sample = Fraction(1)
    banned = set(roots)
    k = 1
    while sample in banned or sample == 0:
        k += 1
        sample = Fraction(k)
    d_sample, r_sample = depth_at(sample)
    if d_sample != generic:
        raise RuntimeError("generic depth %s != sample %s at %s" % (generic, d_sample, sample))
    if rank_target is not None and r_sample != rank_target:
        raise RuntimeError("sample rank %s != target %s" % (r_sample, rank_target))
    best = d_sample if rank_target is None or r_sample == rank_target else -1
    where = (sample, r_sample)
    for root in roots:
        # Rank is cheap. A root whose rank leaves the stall target cannot be the
        # zero-step of a length-9 word, so its depth is not required.
        den_v = ev(den, root)
        gap = [[ev(rows[i][j], root) / den_v for j in range(size)] for i in range(size)]
        r_root = rank_of(gap)
        if rank_target is not None and r_root != rank_target:
            continue
        d_root = depth_matrix(matrix_from_gap(gap), memo)
        if d_root > best:
            best = d_root
            where = (root, r_root)
    return best, where, generic, len(roots), STATS

def rank_of_local(gap):
    return rank_of(gap)

def walk(rows, den, polys, size, depth_so_far):
    STATS["nodes"] += 1
    if depth_so_far > size:
        raise RuntimeError("depth overflow")
    for row in rows:
        for entry in row:
            STATS["maxdeg"] = max(STATS["maxdeg"], len(entry) - 1)
            if entry:
                STATS["maxbits"] = max(STATS["maxbits"], max(abs(c).bit_length() for c in entry))
    # Column membership and rank witnesses, plus row solves.
    eye_cols = [[const(1 if i == k else 0) for i in range(size)] for k in range(size)]
    A, rank, piv, witnesses = eliminate(rows, eye_cols)
    for w in witnesses:
        if len(w) > 1:
            polys.append(w)
            STATS["roots"] += 1
    col_in = []
    for k in range(size):
        nums = [trim(A[r][size + k]) for r in range(rank, size)]
        generically_in = all(is_zero(num) for num in nums)
        col_in.append(generically_in)
        if not generically_in:
            for num in nums:
                if not is_zero(num) and len(num) > 1:
                    polys.append(num)
    # Transpose for row membership and pairings. true = rows/den,
    # so solving rows^T y = e gives y_poly with y_true = den * y_poly.
    transposed = [[rows[r][c] for r in range(size)] for c in range(size)]
    AT, rank_t, piv_t, wit_t = eliminate(transposed, eye_cols)
    if rank_t != rank:
        raise RuntimeError("transpose rank")
    for w in wit_t:
        if len(w) > 1:
            polys.append(w)
    row_in = []
    solutions = []
    for k in range(size):
        nums = [trim(AT[r][size + k]) for r in range(rank_t, size)]
        generically_in = all(is_zero(num) for num in nums)
        row_in.append(generically_in)
        if not generically_in:
            for num in nums:
                if not is_zero(num) and len(num) > 1:
                    polys.append(num)
            solutions.append(None)
        else:
            solutions.append(backsolve(AT, rank_t, piv_t, k, size))
    den_rf = RF(den)
    best_child = -1
    n_edges = 0
    for tgt in range(size):
        if not col_in[tgt]:
            continue
        for src in range(size):
            if tgt == src or not row_in[src]:
                continue
            pairing = solutions[src][tgt] * den_rf
            if pairing.is_zero():
                continue
            # gamma = 1/pairing
            gamma = RF(ONE) / pairing
            n_edges += 1
            if len(gamma.d) > 1:
                polys.append(gamma.d)
            child_rows, child_den = child_gap(rows, den, tgt, src, gamma, size)
            child_depth = walk(child_rows, child_den, polys, size, depth_so_far + 1)
            if child_depth > best_child:
                best_child = child_depth
    if n_edges == 0:
        return 0
    return 1 + best_child

def child_gap(rows, den, tgt, src, gamma, size):
    gden = gamma.d
    gnum = gamma.n
    new_den = mul(den, gden)
    out = []
    unit = [const(1 if j == src else 0) for j in range(size)]
    for i in range(size):
        if i != tgt:
            out.append([mul(gden, entry) for entry in rows[i]])
            continue
        row = []
        for j in range(size):
            term = sub(mul(gden, rows[i][j]), mul(gnum, rows[src][j]))
            # subtract gamma * e_src, i.e. gnum*den on column src
            if j == src:
                term = sub(term, mul(gnum, den))
            row.append(trim(term))
        out.append(row)
    return out, new_den

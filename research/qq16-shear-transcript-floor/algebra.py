"""Exact ordered QQ16 shear fixtures; standard library, no producer imports.

These small rational models test the general ordered theorem, not the
actual-source rank premise. Apache-2.0. Prepared for @jgilfoil with
substantial OpenAI Codex assistance.
"""

from fractions import Fraction as F


def need(condition, message):
    if not condition:
        raise ValueError(message)


def eye(n):
    return [[F(i == j) for j in range(n)] for i in range(n)]


def zeros(n, m):
    return [[F(0) for _ in range(m)] for _ in range(n)]


def add(a, b):
    need(len(a) == len(b), "vector dimensions")
    return [x + y for x, y in zip(a, b)]


def scale(c, a):
    return [c * x for x in a]


def mv(a, x):
    need(all(len(row) == len(x) for row in a), "matrix/vector dimensions")
    return [sum((c * v for c, v in zip(row, x)), F(0)) for row in a]


def mm(a, b):
    need(bool(b) and all(len(row) == len(b) for row in a), "matrix dimensions")
    return [[sum((row[k] * b[k][j] for k in range(len(b))), F(0))
             for j in range(len(b[0]))] for row in a]


def ma(a, b):
    return [add(x, y) for x, y in zip(a, b)]


def ms(c, a):
    return [scale(c, row) for row in a]


def rref(matrix, columns=None):
    a = [[F(x) for x in row] for row in matrix]
    n = len(a[0]) if a else (columns or 0)
    need(all(len(row) == n for row in a), "rectangular matrix")
    pivots = []
    for col in range(n):
        pivot = next((i for i in range(len(pivots), len(a)) if a[i][col]), None)
        if pivot is None:
            continue
        row = len(pivots)
        a[row], a[pivot] = a[pivot], a[row]
        a[row] = scale(1 / a[row][col], a[row])
        for i in range(len(a)):
            if i != row and a[i][col]:
                a[i] = add(a[i], scale(-a[i][col], a[row]))
        pivots.append(col)
    return a, pivots


def rank(a, columns=None):
    return len(rref(a, columns)[1])


def kernel(a, columns=None):
    reduced, pivots = rref(a, columns)
    n = len(a[0]) if a else columns
    basis = []
    for free in range(n):
        if free in pivots:
            continue
        v = [F(0)] * n
        v[free] = F(1)
        for i, pivot in enumerate(pivots):
            v[pivot] = -reduced[i][free]
        need(not any(mv(a, v)), "constructed nullspace")
        basis.append(v)
    return basis


def inverse(a):
    n = len(a)
    reduced, pivots = rref([row + unit for row, unit in zip(a, eye(n))])
    need(pivots == list(range(n)), "invertible matrix")
    result = [row[n:] for row in reduced]
    need(mm(a, result) == eye(n) and mm(result, a) == eye(n), "two-sided inverse")
    return result


def columns_to_rows(columns, nrows=None):
    if not columns:
        return [[] for _ in range(nrows or 0)]
    return [list(row) for row in zip(*columns)]


class Model:
    """Literal conserved maps, independent of the witness construction."""

    def __init__(self, q):
        need(q in (2, 3), "fixture centre dimension")
        self.q, self.m = q, 3 * q
        upper, lower = eye(q), eye(q)
        upper[0][1] = F(1)
        lower[1][0] = F(1)
        if q == 3:
            upper[1][2] = F(1)
            lower[2][1] = F(1)
        self.A = [upper, ma(upper, ms(F(1), ma(upper, ms(-1, eye(q))))), mm(upper, lower)]
        self.T = [lower, lower, mm(lower, upper)]
        self.PA = [inverse(a) for a in self.A]
        self.PT = [inverse(t) for t in self.T]
        self.Q, self.Qinv = upper, inverse(upper)
        self.B, self.K = [], []
        for stage in range(3):
            b, k = zeros(q, self.m), zeros(self.m, q)
            for i in range(q):
                b[i][stage * q + i] = F(1)
                k[stage * q + i][i] = F(12)
            self.B.append(b)
            self.K.append(k)
            need(mm(b, k) == ms(12, eye(q)), "ordinary response identity")
        need(mm(self.Qinv, self.PT[1]) != mm(self.PT[1], self.Qinv),
             "fixture must detect operator order")
        self.tap = mm(lower, upper)

    def split(self, x):
        need(len(x) == self.m + 2 * self.q, "field dimension")
        return x[:self.m], x[self.m:self.m+self.q], x[self.m+self.q:]

    def query(self, s, x):
        u, a, t = self.split(x)
        return add(add(mv(self.B[s], u), mv(self.A[s], a)), mv(self.T[s], t))

    def forward(self, x, y):
        xu, xa, xt = self.split(x)
        yu, ya, yt = self.split(y)
        f = self.query(0, x)
        w = add(xu, scale(-1, mv(self.K[0], f)))
        new_a = mv(self.PA[0], mv(self.T[0], xt))
        new_t = mv(self.PT[0], f)
        return (w + new_a + new_t,
                add(yu, w) + add(add(xa, ya), scale(-1, new_a))
                + add(add(xt, yt), scale(-1, new_t)), f)

    def boundary(self, x, y, read, shear_sign=1):
        xu, xa, xt = self.split(x)
        yu, ya, yt = self.split(y)
        record = mv(read, xu)
        # The retained record also drives an in-place opposite-sign T tap.
        tap = mv(self.tap, record) if len(record) == self.q else [F(0)] * self.q
        delta = add(scale(shear_sign, mv(self.Q, xa)), tap)
        return (xu + xa + add(xt, delta), yu + ya + add(yt, scale(-1, delta)), record)

    def backward(self, x, y):
        xu, xa, xt = self.split(x)
        yu, ya, yt = self.split(y)
        future = self.query(2, y)
        ua = mv(self.PA[2], future)
        driver = mv(self.T[1], xt)
        current = self.query(1, yu + ua + yt)
        new_xt = mv(self.PT[1], add(current, scale(12, driver)))
        new_yt = add(yt, scale(-1, mv(self.PT[1], add(current, scale(11, driver)))))
        return (add(xu, scale(-1, yu)) + add(add(xa, ya), scale(-1, ua)) + new_xt,
                add(yu, mv(self.K[1], driver)) + ua + new_yt)

    def replay(self, x, y, read, shear_sign=1):
        x, y, f = self.forward(x, y)
        x, y, record = self.boundary(x, y, read, shear_sign)
        x, y = self.backward(x, y)
        return x, y, f, record

    def observation(self, x, y, read, shear_sign=1):
        x, y, f, record = self.replay(x, y, read, shear_sign)
        # Grant the entire post-B1 completed X bank as well as selected Y.
        return x + y[self.m:] + f + record


def family(model, h, order_mutation=False, denominator=11):
    left = (mm(model.PT[1], model.Qinv) if order_mutation
            else mm(model.Qinv, model.PT[1]))
    k = scale(-F(1, denominator), mv(left, mv(model.B[1], h)))
    xa = add(scale(-1, mv(model.PA[0], mv(model.B[0], h))), scale(-1, k))
    xt = mv(model.PT[0], mv(model.A[0], k))
    return h + xa + xt, [F(0)] * model.m + scale(-1, xa) + scale(-1, xt)


def check_model(q):
    model = Model(q)
    ordinary = model.m
    gmap = ma(ms(11, model.B[2]), mm(
        mm(ma(mm(model.A[2], model.Qinv), model.T[2]), model.PT[1]), model.B[1]))
    transcript = model.B[0]
    h_basis = kernel(gmap + transcript)
    need(len(h_basis) == q, "dense read residual dimension")
    selected_family, first_pair_census = [], []
    for h in h_basis:
        x, y = family(model, h)
        after_x, after_y, f, record = model.replay(x, y, transcript)
        expected_g = add(h, scale(-F(1, 11), mv(model.K[1], mv(model.B[1], h))))
        need(not any(after_x + after_y[ordinary:] + f + record), "ordered invisible family")
        need(after_y[:ordinary] == expected_g, "ordinary residue")
        need(any(x[ordinary:]), "nonzero required selected input")
        selected_family.append(x[ordinary:])
        first_pair_census.append(sum(bool(v) for v in expected_g))
    need(rank(columns_to_rows(selected_family)) == q, "independent lost selected values")

    # Build the complete input/output matrices from basis evaluations of
    # the literal maps, without using K, G, or the family parameterization.
    fields = ordinary + 2 * q
    observations, selected = [], []
    for j in range(2 * fields):
        full = [F(i == j) for i in range(2 * fields)]
        x, y = full[:fields], full[fields:]
        observations.append(model.observation(x, y, transcript))
        selected.append(x[ordinary:])
    obs = columns_to_rows(observations)
    desired = columns_to_rows(selected)
    source_rank = rank(model.B[0] + model.B[1] + model.B[2])
    full_defect = rank(obs + desired) - rank(obs)
    need(source_rank == 3 * q, "full triple-query rank fixture")
    need(full_defect == source_rank - q - rank(transcript) == q,
         "full arbitrary-input defect equals rank prediction")
    full_kernel = kernel(obs)
    need(len(full_kernel) == q, "full input kernel dimension")
    for v in full_kernel:
        need(not any(model.observation(v[:fields], v[fields:], transcript)),
             "independent full-kernel replay")
    need(rank(columns_to_rows([mv(desired, v) for v in full_kernel])) == q,
         "full-kernel selected-image rank")

    controls = []
    need(any(any(model.observation(*family(model, h), transcript, shear_sign=-1))
             for h in h_basis), "wrong shear sign must be detected")
    controls.append("wrong shear sign")
    need(any(any(model.observation(*family(model, h, order_mutation=True), transcript))
             for h in h_basis), "wrong noncommuting order must be detected")
    controls.append("wrong noncommuting order")
    need(any(any(model.observation(*family(model, h, denominator=12), transcript))
             for h in h_basis), "wrong eleven coefficient must be detected")
    controls.append("eleven replaced by twelve")
    no_read_basis = kernel(gmap)
    need(len(no_read_basis) == 2 * q, "unobserved family dimension")
    detected = next((h for h in no_read_basis if any(mv(transcript, h))), None)
    need(detected is not None, "record removes a real kernel direction")
    x, y = family(model, detected)
    need(not any(model.observation(x, y, [])), "omitted-record candidate")
    need(any(model.observation(x, y, transcript)), "retained record must detect candidate")
    controls.append("omitted retained record")
    # A real first-pair transient is not among the free observations.
    h = h_basis[0]
    x, y = family(model, h)
    fx, _, _ = model.forward(x, y)
    need(any(fx[ordinary:ordinary+q]), "a free transient A cut changes the contract")
    controls.append("free transient F0 A record")
    return {"centre_dimension": q, "ordinary_dimension": ordinary,
            "triple_query_rank": source_rank, "transcript_rank": rank(transcript),
            "full_input_dimension": 2 * fields, "observation_rank": rank(obs),
            "full_input_kernel_dimension": len(full_kernel),
            "lost_selected_dimension": full_defect,
            "family_basis_vectors": len(h_basis), "residue_nonzero_entries": first_pair_census,
            "rejecting_controls": controls}


def verify():
    """Return deterministic JSON-compatible exact-check evidence."""
    return {"status": "PASS_ORDERED_SHEAR_ALGEBRA", "models": [check_model(2), check_model(3)]}


if __name__ == "__main__":
    import json
    print(json.dumps(verify(), sort_keys=True, indent=2))

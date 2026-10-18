"""Check exact regressions for the ordered joint-query theorem.

Adapted from the cover-algebra proof checker. Finite regressions support
but do not replace the ring proof. New code is Apache-2.0. Research and
verification used Codex assistance.
"""

from fractions import Fraction as F


A = [0, 7, 20, 27, 36, 46, 57, 111]
T = [21, 37, 47, 76, 81, 87, 92, 110]


def need(condition, text):
    if not condition:
        raise ValueError(text)


def eye(n):
    return [[F(i == j) for j in range(n)] for i in range(n)]


def tr(a):
    return [list(row) for row in zip(*a)]


def plus(a, b, scale=1):
    return [[x + scale*y for x, y in zip(ar, br)] for ar, br in zip(a, b)]


def apply(a, x):
    result = []
    width = len(x[0])
    for row in a:
        out = [F(0)] * width
        for c, source in zip(row, x):
            if c:
                for j, value in enumerate(source):
                    if value:
                        out[j] += c*value
        result.append(out)
    return result


def restrict_rows(a, ports):
    ports = set(ports)
    return [row[:] if i in ports else [F(0)]*len(row)
            for i, row in enumerate(a)]


def check(r, k, rt_inverse, aports, tports, future_n):
    n, rdim = len(k), len(r)
    uports = [p for p in range(n) if p not in aports+tports]
    rt = [[row[p] for p in tports] for row in r]
    p = restrict_rows(k, tports)
    ka, ku = restrict_rows(k, aports), restrict_rows(k, uports)
    l = [[v if i in tports else F(0) for i, v in enumerate(row)] for row in r]
    m = apply(r, ku)
    z = plus(ku, apply(p, m), -1)
    j = plus(eye(n), apply(k, r), -1)
    h, hinv = plus(eye(n), apply(z, r)), plus(eye(n), apply(z, r), -1)
    e, einv = plus(eye(n), future_n), plus(eye(n), future_n, -1)
    need(apply(r, p) == apply(l, p) == eye(rdim), "The current T section is a unit.")
    need(apply(rt, rt_inverse) == apply(rt_inverse, rt) == eye(rdim), "Both selected inverse orders hold.")
    need(apply(r, z) == [[F(0)]*rdim for _ in range(rdim)], "The source response has zero query.")
    need(apply(h, hinv) == apply(hinv, h) == eye(n), "Both transvection inverse orders hold.")
    need(apply(e, einv) == apply(einv, e) == eye(n), "Both future logger inverse orders hold.")
    correction = plus(ka, apply(p, plus(eye(rdim), m)))
    need(apply(j, h) == plus(eye(n), apply(correction, r), -1), "The target error has selected support.")

    def pair(x, y, conserved):
        u = apply(e, y)
        a, b = apply(l, x), apply(r, u)
        v = plus(u, apply(p, plus(a, b, -1)))
        yy = apply(h, v)
        xx = plus(x, y, -1)
        if conserved:
            for i in aports+tports:
                xx[i] = [xi+yi-oi for xi, yi, oi in zip(x[i], y[i], yy[i])]
        else:
            pb = apply(p, b)
            for i in tports:
                xx[i] = pb[i]
        need(apply(r, yy) == a, "The output source query is the old selected target.")
        wanted = plus(b, apply(m, a)) if conserved else b
        need(apply(l, xx) == wanted, "The selected target has its stated query.")
        return xx, yy

    def inverse(xx, yy, conserved):
        a = apply(r, yy)
        b = apply(l, xx)
        if conserved:
            b = plus(b, apply(m, a), -1)
        v = apply(hinv, yy)
        u = plus(v, apply(p, plus(b, a, -1)))
        y = apply(einv, u)
        x = plus(xx, y)
        if conserved:
            for i in aports:
                x[i] = [oi+si-yi for oi, si, yi in zip(xx[i], yy[i], y[i])]
        pa = apply(p, a)
        for i in tports:
            x[i] = pa[i]
        return x, y

    roff = [[v if i not in tports else F(0) for i, v in enumerate(row)] for row in r]
    bmat, dmat = apply(rt_inverse, roff), apply(ku, rt)
    mhat = apply(apply(rt_inverse, m), rt)
    need(apply(bmat, dmat) == mhat, "The short source word has the correct ordered product.")

    def short_word(x, y, conserved, omit_swap=False):
        xx, yy = [row[:] for row in x], apply(e, y)
        old_t = [x[i][:] for i in tports]
        a = apply(rt, old_t)
        ca = apply(ka, a)
        na = apply(future_n, yy)
        for i in aports:
            source = y[i] if conserved else na[i]
            xx[i] = [v+u-c for v, u, c in zip(xx[i], source, ca[i])]
        yy = plus(yy, apply(dmat, old_t))
        if not omit_swap:
            for i in tports:
                xx[i], yy[i] = yy[i], xx[i]
        if not conserved:
            delta = apply(mhat, [yy[i] for i in tports])
            for i, row in zip(tports, delta):
                xx[i] = [v-d for v, d in zip(xx[i], row)]
        query = apply(bmat, yy)
        for i, row in zip(tports, query):
            yy[i] = [v-q for v, q in zip(yy[i], row)]
        return plus(xx, apply(j, yy), -1), yy

    basis = eye(2*n)
    x, y = basis[:n], basis[n:]
    records = {}
    for conserved in (False, True):
        output = pair(x, y, conserved)
        need(inverse(*output, conserved) == (x, y), "The left full pair inverse restores all inputs.")
        need(pair(*inverse(x, y, conserved), conserved) == (x, y), "The right full pair inverse restores all inputs.")
        need(short_word(x, y, conserved) == output, "The short source and precompensation word matches every column.")
        need(short_word(x, y, conserved, True) != output, "Omitting the selected exchange must fail.")
        if conserved:
            for i in aports+tports:
                need(plus([output[0][i]], [output[1][i]]) == plus([x[i]], [y[i]]), "Each selected pair sum is unchanged.")
        records["conserved_pair_sums" if conserved else "clean_current_query"] = {
            "all_input_columns": 2*n,
            "both_inverse_orders": True,
            "short_word": True,
            "omitted_exchange_control": "REJECTED"
        }
    la = [[v if i in aports else F(0) for i, v in enumerate(row)] for row in r]
    ru = [[v if i in uports else F(0) for i, v in enumerate(row)] for row in r]
    need(apply(r, ka) == eye(rdim), "The forward companion has a unit A section.")

    def forward(x, y):
        f, c = apply(r, x), apply(l, x)
        xx = plus(x, apply(ku, f), -1)
        ac, tf = apply(ka, c), apply(p, f)
        for i in aports:
            xx[i] = ac[i]
        for i in tports:
            xx[i] = tf[i]
        yy = plus(y, xx)
        for i in aports+tports:
            yy[i] = [v+u-w for v, u, w in zip(x[i], y[i], xx[i])]
        return xx, yy

    def forward_inverse(xx, yy):
        f, c = apply(l, xx), apply(la, xx)
        x = plus(xx, apply(ku, f))
        a = plus(plus(f, apply(m, f), -1), apply(ru, xx), -1)
        a = plus(a, c, -1)
        aa, tc = apply(ka, a), apply(p, c)
        for i in aports:
            x[i] = aa[i]
        for i in tports:
            x[i] = tc[i]
        y = plus(yy, xx, -1)
        for i in aports+tports:
            y[i] = [v+u-w for v, u, w in zip(xx[i], yy[i], x[i])]
        return x, y

    output = forward(x, y)
    need(forward_inverse(*output) == (x,y), "The forward left inverse restores every input.")
    need(forward(*forward_inverse(x,y)) == (x,y), "The forward right inverse restores every input.")
    for i in aports+tports:
        need(plus([output[0][i]], [output[1][i]]) == plus([x[i]], [y[i]]), "The forward selected sums are unchanged.")
    source = plus(x, apply(p, plus(apply(ru, x), apply(la, x))))
    source = plus(source, apply(ku, apply(l, source)), -1)
    anew = plus(plus(apply(plus(eye(rdim), m, -1), apply(l, source)), apply(ru, source), -1), apply(la, source), -1)
    row_a = apply(ka, anew)
    for i in aports:
        source[i] = row_a[i]
    need(source == output[0], "The full-frame forward scalar word is exact.")
    raw_target = plus(y, apply(j, x))
    fixed_target = plus(raw_target, apply(ka, plus(apply(l, source), apply(la, source), -1)))
    need(fixed_target == output[1], "Exactly the A forward targets need correction.")
    records["forward_conserved_pair_sums"] = {
        "all_input_columns": 2*n,
        "both_inverse_orders": True,
        "in_place_source_word": True,
        "A_only_target_correction": True
    }
    return records, m


def verify(source_r):
    r = [[row.get(p, F(0)) for p in range(112)] for row in source_r]
    k = [[v/4 for v in row] for row in tr(r)]
    rt = [[row[p] for p in T] for row in r]
    rti = [[v/4 for v in row] for row in tr(rt)]
    pa = restrict_rows(k, A)
    la = [[v if i in A else F(0) for i, v in enumerate(row)] for row in r]
    future_n = apply(pa, plus(r, la, -1))
    actual, m = check(r, k, rti, A, T, future_n)
    need(m == [[12*v for v in row] for row in eye(8)], "The actual ordinary Gram is 12I.")

    # The second example tests the ordered extension with a noncentral M.
    r2 = [[F(v) for v in row] for row in [[1,0,1,0,1,1],[0,1,0,1,0,1]]]
    k2 = [[F(v) for v in row] for row in [[1,0],[0,1],[1,0],[0,1],[1,2],[0,1]]]
    n2 = [[F(0)]*6 for _ in range(6)]
    n2[0][3], n2[1][2], n2[1][5] = F(1), F(-1), F(2)
    general, m2 = check(r2, k2, eye(2), [0,1], [2,3], n2)
    swap = [[F(0),F(1)],[F(1),F(0)]]
    need(apply(m2, swap) != apply(swap, m2), "The regression uses a noncentral M.")
    singular_k = [row[:] for row in k2]
    singular_k[4:] = [[F(0), F(0)], [F(0), F(0)]]
    singular, zero_m = check(r2, singular_k, eye(2), [0,1], [2,3], n2)
    need(zero_m == [[F(0), F(0)], [F(0), F(0)]], "A singular M is allowed")
    return {
        "status": "PASS_ORDERED_JOINT_QUERY_REGRESSIONS",
        "actual_R_checks": actual,
        "noncentral_M_checks": general,
        "noncentral_M": [[str(v) for v in row] for row in m2],
        "singular_M_checks": singular,
        "scope": "Exact finite checks of both data inverse orders, the short source words, selected sums, and a noncentral and singular M. The general associative-ring result is proved in the source note; it is not inferred from these tests."
    }

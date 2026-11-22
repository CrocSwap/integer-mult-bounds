"""Factor the native frames from signed Pauli tableaus and exact path sums.

The symplectic reduction and the frame convention are those of clifford_exact.
The phase producer computes one constrained binary quadratic sum per child.
"""

from functools import cache
from fractions import Fraction
from gauss_phase import matrix_element


def coefficient_rows(rows):
    """Store one exact rational for every distinct source coefficient string."""
    rational = cache(Fraction)
    return {k: tuple((j, rational(text)) for j, text in row) for k, row in rows}


def monomial_phase(op):
    import clifford_exact as c

    n, table = op.n, op.tab
    if any(x or p % 2 for x, z, p in table[n:]):
        raise ValueError("The operation has a nonmonomial signed tableau")
    G = c.transpose([x for x, z, p in table[:n]], n)
    b = c.mv(G, sum((p // 2) << i for i, (x, z, p) in enumerate(table[n:])))
    GT = c.transpose(G, n)
    Q = c.transpose([c.mv(GT, z) for x, z, p in table[:n]], n)
    alpha = [(p - 2 * c.parity(b & z)) % 4 for x, z, p in table[:n]]
    entry = matrix_element(op.circuit, n, 0, b)
    if entry is None or entry[0] != 0 or entry[1] % 2:
        raise ArithmeticError("The monomial is missing its unit Gaussian phase")
    phase = entry[1] // 2
    record = dict(
        matrix_rows=G, offset=b, quadratic_rows=Q, linear_Z4=alpha, phase=phase
    )
    built = c.diag(n, Q, alpha).then(c.perm(n, G)).then(c.xgate(n, b))
    if built.tab != table:
        raise ArithmeticError("The monomial changes a signed Pauli generator")
    return c.Op(n, built.tab, built.circuit + [("phase", phase)]), record


def catalogue(graph, layout):
    import clifford_exact as c

    frames = graph["frames"]
    if frames != layout["frames"]:
        raise ValueError("Frame inputs differ")
    n = 9

    @cache
    def frame(i):
        return c.canonical_frame(n, tuple(frames[i]))

    @cache
    def back(i):
        return frame(i).adjoint()

    @cache
    def standard(r):
        axes = range(r)
        diag = c.diag(n, tuple(1 << i if i < r else 0 for i in range(n)))
        reverse = c.xgate(n, (1 << r) - 1)
        return c.hadamard(n, axes), diag.adjoint(), reverse, c.fourier(n, axes)

    def lower(op):
        tab = op.tab
        Bcols = [x for x, z, p in tab[n:]]
        r = c.rank(Bcols)
        if not r:
            return dict(rank=0, left=monomial_phase(op)[1], right=None)
        G = c.transpose(c.basis_extend(Bcols, n), n)
        pa = c.perm(n, c.inv(G, n))
        part = op.then(pa)
        cols = [x for x, z, p in part.tab[n:]]
        zcols = [z for x, z, p in part.tab[n:]]
        picks = []
        selected = []
        for j, x in enumerate(cols):
            if c.rank(selected + [x]) > len(selected):
                picks.append(j)
                selected.append(x)
        if len(picks) != r or any(x >> r for x in cols):
            raise ArithmeticError("The frame does not cover the paid grade")
        Bi = c.inv(c.transpose(selected, r), r)
        Dr = c.transpose([zcols[j] & ((1 << r) - 1) for j in picks], r)
        Q = tuple(
            sum(c.parity(row & col) << j for j, col in enumerate(c.transpose(Bi, r)))
            for row in Dr
        )
        dq = c.diag(n, Q + (0,) * (n - r))
        h, sd, x, fourier = standard(r)
        v = part.then(dq).then(h)
        witness, _ = monomial_phase(v)
        lmon, left = monomial_phase(sd.then(dq.adjoint()).then(pa.adjoint()))
        rmon, right = monomial_phase(witness.then(sd).then(x))
        built = rmon.then(fourier).then(lmon)
        if built.tab != tab or matrix_element(
            op.circuit + built.adjoint().circuit, n, 0, 0
        ) != (0, 0):
            raise ArithmeticError(
                "The child differs on a signed Pauli or on absolute phase"
            )
        return dict(rank=r, left=left, right=right)

    xports = layout["live"]
    host = layout["hosted"]
    shadow = dict(
        zip(host["Dports"], zip(host["X2"], host["Y2"], strict=True), strict=True)
    )
    mains = set(xports) | {x + 112 for x in xports} | set(host["X2"]) | set(host["Y2"])
    if len(mains) != 400 or len(shadow) != 96:
        raise ValueError("Invalid primary and hosted owners")
    starts, ends = graph["initial"], graph["final"]
    pairs = {(a, b) for _, a, b in graph["moves"]}
    pairs.update(
        (a, b)
        for i, (a, b) in enumerate(zip(starts, ends, strict=True))
        if i not in mains
    )
    attached = []
    for a, b in sorted(pairs):
        rec = lower(back(a).then(frame(b)))
        if not rec["rank"] == abs(len(frames[a]) - len(frames[b])) > 0:
            raise ValueError("Invalid paid grade")
        attached.append([a, b, rec])
    full = c.fourier(n)
    ports = []
    for i, (x, q) in enumerate(zip(xports, layout["ports"], strict=True)):
        y = x + 112
        if frames[starts[y]] or len(frames[ends[x]]) != n:
            raise ValueError("The original main endpoints have changed")
        if i in shadow:
            u, v = shadow[i]
            if any(tags[x] != tags[u] or tags[y] != tags[v] for tags in (starts, ends)):
                raise ValueError("The second port has different frame endpoints")
        contact = c.cgate(n, q, -1)
        left = lower(contact.then(frame(starts[x])))
        right = lower(back(ends[y]).then(contact).then(full))
        if left["rank"] or right["rank"]:
            raise ValueError("An external port needs a paid grade")
        ports.append([q, left["left"], right["left"]])
    return dict(pairs=attached, ports=ports)

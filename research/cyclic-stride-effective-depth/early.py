"""Optional exact-zero truncation of PR846; extra scans and head returns charged."""
from common import original as st


def solve(x, b, w, bits, tape, trace=None, level=0):
    """Return the rounded solution. trace collects per-level (L, w, data,
    coefficients) for invariant checks. Values may be None in count-only
    mode (structure and traffic only)."""
    L = len(x)
    st.need(L >= 1 and len(b) == L, 'shape')
    w %= L
    if 2 * w > L:  # reverse orientation: stride L-w <= L/2
        tape.records += 2 * L  # read backwards, write forwards
        y = solve(x[::-1], b[::-1], L - w, bits, tape, trace, level)
        tape.records += 2 * L
        return y[::-1]
    tape.levels.append((L, w))
    if trace is not None:
        trace.append(dict(level=level, length=L, stride=w, x=x, b=b))
    count_only = x[0] is None
    # Experimental coefficient scan and return to its initial head position.
    tape.records += 2 * L
    if not count_only and all(bi == st.ZERO for bi in b):
        tape.records += 2 * L
        return [st.rounded(xi, bits) for xi in x]
    if w == 0:  # every point is its own cycle
        tape.records += 2 * L
        if count_only:
            return [None] * L
        return [st.rounded(st.div(xi, st.sub(st.ONE, bi)), bits) for xi, bi in zip(x, b)]
    # Pass A: zero-seed chains along +w, with rounded chain products.
    fifo = st.Fifo(tape, [None] * w)
    z = [None] * L
    p = [None] * L
    for i in range(L):
        tape.records += 2  # read x_i, b_i
        prev = fifo.pop()
        if count_only:
            fifo.push(None)
            continue
        if prev is None:
            z[i], p[i] = x[i], b[i]
        else:
            z[i] = st.rounded(st.add(x[i], st.mul(b[i], prev[0])), bits)
            p[i] = st.rounded(st.mul(b[i], prev[1]), bits)
        fifo.push((z[i], p[i]))
    # Closure system on the w chain ends: Y_k = c_k + a_k Y_((k+L) mod w).
    c, a = z[L - w:], p[L - w:]
    tape.records += 2 * w  # the ends are the tail of the pass-A output
    Y = solve(c, a, (-L) % w, bits, tape, trace, level + 1)
    # Pass C: reseed chain starts from the closure values (Y_k feeds start k).
    fifo = st.Fifo(tape, Y)
    y = [None] * L
    for i in range(L):
        tape.records += 3  # read x_i, b_i; write y_i
        prev = fifo.pop()
        if not count_only:
            y[i] = st.rounded(st.add(x[i], st.mul(b[i], prev)), bits)
        fifo.push(y[i])
    return y

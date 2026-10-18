"""Evaluate exact Clifford states on their nonzero support.

Gate tables are from Charles Bethin's PR662. The support update is new.
Prepared for Ali Romman with substantial OpenAI Codex assistance.
Apache-2.0.
"""


def zero_state(op, tables, basis=0):
    """Return every Gaussian numerator and the power-of-two denominator."""
    size = 1 << op.n
    if not 0 <= basis < size:
        raise IndexError(basis)
    state = {basis: (1, 0)}
    den = 0
    for gate in op.circuit:
        kind = gate[0]
        if kind == 'P':
            mapping = tables.permutation_table(op.n, tuple(gate[1]))
            state = {mapping[x]: value for x, value in state.items()}
        elif kind == 'X':
            state = {x ^ gate[1]: value for x, value in state.items()}
        elif kind in ('D', 'phase'):
            phases = (tables.phase_table(op.n, tuple(gate[1]), tuple(gate[2]))
                      if kind == 'D' else None)
            out = {}
            for x, (a, b) in state.items():
                phase = phases[x] if phases is not None else gate[1] % 4
                if phase == 0:
                    out[x] = (a, b)
                elif phase == 1:
                    out[x] = (-b, a)
                elif phase == 2:
                    out[x] = (-a, -b)
                else:
                    out[x] = (b, -a)
            state = out
        elif kind == 'C':
            q, sign = gate[1:]
            out = {}
            for x, (a, b) in state.items():
                y = x ^ q
                if y < x and y in state:
                    continue
                c, d = state.get(y, (0, 0))
                first = (a - sign*b + c + sign*d,
                         b + sign*a + d - sign*c)
                second = (c - sign*d + a + sign*b,
                          d + sign*c + b - sign*a)
                if first != (0, 0):
                    out[x] = first
                if second != (0, 0):
                    out[y] = second
            state = out
            den += 1
            while den and all((a & 1) == (b & 1) == 0
                              for a, b in state.values()):
                state = {x: (a // 2, b // 2) for x, (a, b) in state.items()}
                den -= 1
        else:
            raise AssertionError(gate)
    vec = [(0, 0)] * size
    for x, value in state.items():
        vec[x] = value
    return vec, den

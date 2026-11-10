"""Independent audit of the chain-nested root and of the literal caller against it.

DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code. Apache-2.0.
Imports nothing from the primary constructor, replay or pricing.  Three separate checks:
(1) the formula root with symbolic stage variables, multiplied as polynomial matrices;
(2) the literal word evaluated at the two real central characters with all D=1;
(3) at every IDLE_ONE the literal register's line and dual functional, read from the word
itself, equal the family formula, and every later covered native call misses that line.
"""
from fractions import Fraction as F


def require(ok, why):
    if not ok:
        raise ValueError(why)


def root(gl, gr):
    """Return (n, sites); a site is (x, y, support or None), written from the formula."""
    fL = [1+i for i in range(gl)]
    fR = [1+gl+i for i in range(gr)]
    n = 1+gl+gr
    empty = None
    if n % 2:
        empty, n = n, n+1
    require(gl % 2 == 1 and gr % 2 == 1, 'this audit covers the odd/odd family')
    sites = []
    for i in range(gl):
        x, y = {0: 1, fL[i]: 1}, {0: 1, fL[i]: -1}
        for j in fL[:i]:
            x[j] = 2
        sites.append((x, y, frozenset([0]+fL[:i+1])))
    # Thin queries, written out for odd/odd; the empty coordinate couples them.
    alternating = {f: (-1)**i for i, f in enumerate(fL)}
    reverse = {f: (-1)**i for i, f in enumerate(reversed(fR))}
    for a, u, p, q in ((0, 1, 0, 1), (-1, 2, 1, 0), (-1, 3, 1, -1)):
        x, y = {0: a}, {0: u}
        for f in fL:
            x[f], y[f] = a+1, (1-u)*alternating[f]
        for f in fR:
            x[f], y[f] = 1-a, (u-1)*reverse[f]
        x[empty], y[empty] = q, p
        sites.append((x, y, None))
    for m in range(gr):
        x, y = {0: -1, fR[m]: 1}, {0: 1, fR[m]: 1}
        for l in fR[m+1:]:
            x[l] = 2
        sites.append((x, y, frozenset([0]+fR[m:])))
    return n, sites


def polynomial_product(n, sites):
    """Prod Delta_k (I-2R_k), entries sparse polynomials in the D_k, keyed by stage bitmask."""
    rows = [{i: {0: 1}} for i in range(n)]
    stage = 0
    for x, y, support in sites:
        # Left multiply by I-2 x y^T: row r gains -2 x_r (y^T rows).
        dual = {}
        for f, c in y.items():
            if c:
                for col, poly in rows[f].items():
                    entry = dual.setdefault(col, {})
                    for mono, v in poly.items():
                        entry[mono] = entry.get(mono, 0)+c*v
        for r, c in x.items():
            if c:
                for col, poly in dual.items():
                    entry = rows[r].setdefault(col, {})
                    for mono, v in poly.items():
                        value = entry.get(mono, 0)-2*c*v
                        if value:
                            entry[mono] = value
                        else:
                            entry.pop(mono, None)
                    if not entry:
                        rows[r].pop(col)
        if support is not None:
            bit = 1 << stage
            stage += 1
            for r in support:
                rows[r] = {col: {m | bit: v for m, v in poly.items() if not require(not m & bit, 'multilinear stage')}
                           for col, poly in rows[r].items()}
    return rows


def shadow(word, sign):
    """Literal word at D=1 and Q=sign in {1,-1}: integer register matrix, with idle reads."""
    n = word['roles']
    c = [[F(int(i == j)) for j in range(n)] for i in range(n)]
    reads = []
    for event in word['events']:
        op = event[0]
        if op == 'ADD':
            value = F(event[3])
            c[event[1]] = [a+value*b for a, b in zip(c[event[1]], c[event[2]])]
        elif op == 'SCALE':
            c[event[1]] = [F(event[2])*a for a in c[event[1]]]
        elif op == 'SWAP':
            c[event[1]], c[event[2]] = c[event[2]], c[event[1]]
        elif op == 'LOCAL':
            c[event[3]] = [a+sign*b for a, b in zip(c[event[3]], c[event[2]])]
            reads.append(('LOCAL', event[1], [c[event[2]][:], c[event[3]][:]]))
        elif op == 'QUERY':
            power = F(sign)**event[3]
            c[event[1]] = [a+power*b for a, b in zip(c[event[1]], c[event[2]])]
        elif op == 'IDLE_ONE':
            reads.append(('IDLE_ONE', event[2], event[1], [r[:] for r in c]))
        elif op == 'IDLE':
            raise ValueError('the audited all-ones word has no binary node')
        else:
            require(op == 'LAMBDA', 'known ordinary opcode')   # lambda(+-1)=1
    return c, reads


def solve_column(c, r):
    """Column r of the inverse of c, by exact elimination."""
    n = len(c)
    a = [row[:]+[F(int(i == r))] for i, row in enumerate(c)]
    for j in range(n):
        k = next(k for k in range(j, n) if a[k][j])
        a[j], a[k] = a[k], a[j]
        a[j] = [v/a[j][j] for v in a[j]]
        for k in range(n):
            if k != j and a[k][j]:
                a[k] = [u-a[k][j]*v for u, v in zip(a[k], a[j])]
    return [a[i][n] for i in range(n)]


def family(word):
    n, gl, gr = word['n'], len(word['sL']), len(word['sR'])
    require(word['sL'] == [1]*gl and word['sR'] == [1]*gr and word['roles'] == n, 'audited all-ones shape, no node roles')
    m, sites = root(gl, gr)
    require(m == n and len(sites) == n+1, 'shortest root')
    stages = [frozenset(i for i in range(gl+gr) if word['diagonal'][r][2+i]) for r in range(n)]
    # (1) symbolic root endpoint at the -1 central character.
    rows = polynomial_product(n, sites)
    for r in range(n):
        mono = sum(1 << i for i in stages[r])
        require(rows[r] == {r: {mono: -1}}, 'symbolic -diag endpoint and literal output target')
    # Literal target exponents are the formula's.
    require(stages[0] == frozenset(range(gl+gr)), 'A target')
    for i in range(gl):
        require(stages[1+i] == frozenset(range(i, gl)), 'left field target')
    for j in range(gr):
        require(stages[1+gl+j] == frozenset(range(gl, gl+j+1)), 'right field target')
    # (2) literal word at both real central characters.
    plus, reads = shadow(word, 1)
    minus, _ = shadow(word, -1)
    identity = [[F(int(i == j)) for j in range(n)] for i in range(n)]
    require(plus == identity, 'literal shadow +I at Q=1')
    require(minus == [[-v for v in row] for row in identity], 'literal shadow -I at Q=-1')
    # (3) idle lines from the literal word.
    lines = 0
    for pos, read in enumerate(reads):
        if read[0] != 'IDLE_ONE':
            continue
        _, selected, register, c = read
        gamma, phi = c[register], solve_column(c, register)
        sel = sorted(selected)
        require(sel == list(range(sel[0], sel[-1]+1)), 'contiguous stage set')
        if sel[-1] == gl:                                  # left chain ends at stage gl
            field = 1+(sel[0]-1)-1                         # f_{j-1} for first stage j+1
            wanted_gamma = {field: 1, 0: -2}
        else:
            require(sel[0] == gl+1, 'right chain starts at first right stage')
            field = 1+gl+len(sel)                          # h_{j+1} for j+1 stages
            wanted_gamma = {field: 1, 0: 2}
        require(phi == [F(int(i == field)) for i in range(n)], 'literal idle line phi')
        require(gamma == [F(wanted_gamma.get(i, 0)) for i in range(n)], 'literal idle dual gamma')
        # Every native call in the covered stages, at or after this cut or before it, misses the line.
        for other in reads:
            if other[0] == 'LOCAL' and other[1] in selected:
                for row in other[2]:
                    require(sum(u*v for u, v in zip(row, phi)) == 0, 'covered native call misses the line')
        lines += 1
    require(lines == gl+gr-2, 'one idle per inner field')
    return dict(fields=n, symbolic_entries=n*n, idle_lines_read_from_word=lines, shadows=['Q=1:+I', 'Q=-1:-I'],
                scope='All-ones odd/odd shape; symbolic in every stage variable at the -1 central character; the +1 character is the diagonal product.')

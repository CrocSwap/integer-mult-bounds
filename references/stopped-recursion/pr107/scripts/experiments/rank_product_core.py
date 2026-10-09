"""Extract the two-field core of the existing three-stage bit construction.

The explicit compiler is intended for small exact controls. A positive core
can have a huge compiled network; counts do not mean that network was expanded.
"""
from fractions import Fraction as Q
from itertools import product as cartesian

from audit_joint_frames import eye, zero, matrix, add, sub, scale, rank, product, row_basis
from rational_tensor import kron
from certify import require


def binary_factor(rows, n):
    """Return C=UV over F2, with exactly rank(C) intermediate coordinates.

    V is a row-echelon basis (packed rows), U consists of coefficient masks.
    """
    require(len(rows) == n and all(type(x) is int and 0 <= x < 1 << n for x in rows),
            'Invalid square binary matrix')
    basis = {}
    for row in rows:
        x = row
        for p, b in sorted(basis.items()):
            if x >> p & 1:
                x ^= b
        if x:
            basis[(x & -x).bit_length()-1] = x
    V = [b for p, b in sorted(basis.items())]
    U = []
    for row in rows:
        x = row; coefficients = 0
        for i, b in enumerate(V):
            p = (b & -b).bit_length()-1
            if x >> p & 1:
                x ^= b; coefficients |= 1 << i
        require(x == 0, 'Binary factorization failed')
        U.append(coefficients)
    return U, V


def check_core(rows, vectors, form):
    n = len(rows); d = len(form)
    require(n >= 2 and d >= 2, 'Use at least two labels and two ambient dimensions')
    require(all(type(x) is int or isinstance(x, (Q, str))
                for a in (vectors, form) for row in a for x in row),
            'Use exact rational entries, not floating point')
    U, V = binary_factor(rows, n)
    require(all(row >> i & 1 for i, row in enumerate(rows)), 'Central diagonal must be one')
    H = matrix(form)
    require(all(len(row) == d for row in H) and H == matrix(zip(*H)), 'Form must be square symmetric')
    require(rank(H) == d, 'Ambient rational form is degenerate')
    require(len(vectors) == n and all(len(v) == d for v in vectors), 'Wrong vector dimensions')
    vectors = matrix(vectors)
    Gram = product(product(vectors, H), matrix(zip(*vectors)))
    require(all(Gram[i][i] for i in range(n)), 'Every label line must be nondegenerate')
    edges = [(i, j) for i, row in enumerate(rows) for j in range(n) if i != j and row >> j & 1]
    require(all(Gram[i][j] == 0 for i, j in edges), 'A side connection is not orthogonal')
    projections = []
    for i, v in enumerate(vectors):
        functional = product((v,), H)[0]
        P = matrix([[x*y/Gram[i][i] for y in functional] for x in v])
        require(product(P, P) == P, 'Invalid rational line projection')
        projections.append(P)
    core = check_projector_core(rows, projections)
    core['gram'] = Gram
    return core


def check_projector_core(rows, projections):
    """Rank-one idempotents with mutual annihilation; no common form required."""
    n = len(rows)
    require(len(projections) == n and n >= 2, 'One projector per label is required')
    d = len(projections[0])
    require(d >= 2, 'Use at least two ambient dimensions')
    U, V = binary_factor(rows, n)
    require(all(row >> i & 1 for i, row in enumerate(rows)), 'Central diagonal must be one')
    matrices = []
    for P in projections:
        require(len(P) == d and all(len(row) == d for row in P), 'Wrong projector dimensions')
        require(all(type(x) is int or isinstance(x, (Q, str)) for row in P for x in row),
                'Use exact rational entries, not floating point')
        M = matrix(P)
        require(rank(M) == 1 and product(M, M) == M, 'Need rank-one rational idempotents')
        matrices.append(M)
    edges = [(i, j) for i, row in enumerate(rows) for j in range(n) if i != j and row >> j & 1]
    Z = zero(d)
    require(all(product(matrices[i], matrices[j]) == Z and
                product(matrices[j], matrices[i]) == Z for i, j in edges),
            'Side edges require mutual, not one-sided, annihilation')
    return dict(n=n, r=len(V), d=d, U=U, V=V, side_edges=edges,
                projections=matrices, density=Q(n, len(V)*d))


def check_fitting_pair(rows, fitting):
    """C over F2 and a possibly nonsymmetric rational fitting matrix F.

    F_ii must be nonzero. A one in C_ij, i!=j, requires BOTH F_ij=F_ji=0.
    Factor F=BA, and set P_i=A[:,i] B[i,:]/F_ii. Then rank(P_i)=1,
    P_i^2=P_i, and required pairs mutually annihilate.
    """
    n = len(rows)
    require(len(fitting) == n and all(len(row) == n for row in fitting), 'Wrong fitting dimensions')
    require(all(type(x) is int or isinstance(x, (Q, str)) for row in fitting for x in row),
            'Use exact rational entries, not floating point')
    F = matrix(fitting)
    require(all(F[i][i] for i in range(n)), 'Fitting diagonal must be nonzero')
    A = row_basis(F); d = len(A); B = []
    for row in F:
        residual = list(row); coefficients = []
        for basis in A:
            pivot = next(i for i, x in enumerate(basis) if x)
            c = residual[pivot]
            coefficients.append(c)
            residual = [x-c*y for x, y in zip(residual, basis)]
        require(not any(residual), 'Rational factorization failed')
        B.append(coefficients)
    require(product(B, A) == F, 'Rational product is not the fitting matrix')
    P = [matrix([[A[x][i]*B[i][y]/F[i][i] for y in range(d)] for x in range(d)])
         for i in range(n)]
    core = check_projector_core(rows, P)
    core['fitting_matrix'] = F
    return core


def counts(n, r, d, side_roles):
    require(min(n, r, d) >= 1 and side_roles >= 0, 'Invalid dimensions or role count')
    N = n**3; m = d**3
    W = 2*N+3*n*n*(side_roles+r)
    L = 3*n*n*r*d
    delta = N-2*L
    return dict(n=n, r=r, d=d, side_roles_per_invocation=side_roles,
                N=N, m=m, W=W, L=L, deficit=delta, s=W*m-delta,
                density=Q(n, r*d), relative_deficit=Q(delta, W*m),
                positive=delta > 0)


def tensor(matrices):
    result = ((Q(1),),)
    for M in matrices:
        result = kron(result, M)
    return result


def compile_core(rows, vectors, form, maximum_roles=1000):
    """Complete unshared, edge-explicit three-stage network with rational frames.

    Non-symmetric binary central maps are permitted. Stage two reverses the
    actual scalar gates, so its physical side connections reverse as well.
    """
    return _compile(check_core(rows, vectors, form), maximum_roles)


def compile_projector_core(rows, projections, maximum_roles=1000):
    """The same complete compiler for possibly non-self-adjoint projections."""
    return _compile(check_projector_core(rows, projections), maximum_roles)


def compile_fitting_pair(rows, fitting, maximum_roles=1000):
    return _compile(check_fitting_pair(rows, fitting), maximum_roles)


def _compile(core, maximum_roles):
    n, r, d = core['n'], core['r'], core['d']
    side = core['side_edges']; P = core['projections']
    accounting = counts(n, r, d, len(side))
    W, m, N = accounting['W'], accounting['m'], accounting['N']
    require(W <= maximum_roles, 'Explicit expansion exceeds the role budget')
    coords = list(cartesian(range(n), repeat=3))
    index = {a: i for i, a in enumerate(coords)}
    I, Z = eye(m), zero(m)
    lines = [tensor(P[t] for t in a) for a in coords]
    sources = [scale(M, -1) for M in lines]+[Z]*(W-N)
    sinks = [I]*N+[sub(I, M) for M in lines]+[I]*(W-2*N)
    gates = []; next_role = 2*N
    for stage in range(3):
        for fixed in cartesian(range(n), repeat=2):
            a = list(fixed); a.insert(stage, 0)
            X = []; Y = []
            for t in range(n):
                a[stage] = t
                X.append(index[tuple(a)]); Y.append(N+index[tuple(a)])
            side_role = {pair: next_role+i for i, pair in enumerate(side)}
            next_role += len(side)
            centers = list(range(next_role, next_role+r)); next_role += r
            logical_x, logical_y = (X, Y) if stage != 1 else (Y, X)
            groups = []
            for op in ('J', 'R', 'V', 'G', 'R', 'J', 'G', 'V'):
                group = []
                if op in ('J', 'V'):
                    for t in range(n):
                        aux = [slot for (s, u), slot in side_role.items()
                               if (s == t if op == 'J' else u == t)]
                        data = logical_y[t] if op == 'J' else logical_x[t]
                        xors = [[data, slot] if op == 'J' else [slot, data] for slot in aux]
                        group.append((t, [data]+aux, xors))
                elif op == 'G':
                    xors = [[centers[k], logical_x[t]] for k, mask in enumerate(core['V'])
                            for t in range(n) if mask >> t & 1]
                    group.append((None, logical_x+centers, xors))
                else:
                    xors = [[logical_y[t], centers[k]] for t, mask in enumerate(core['U'])
                            for k in range(r) if mask >> k & 1]
                    group.append((None, logical_y+centers, xors))
                groups.append(group)
            if stage == 1:
                groups = [[(t, ports, list(reversed(xors))) for t, ports, xors in reversed(group)]
                          for group in reversed(groups)]
            A = eye(d**stage)
            prior = tensor(P[a[j]] for j in range(stage))
            B = sub(A, prior)
            future = tensor(P[a[j]] for j in range(stage+1, 3))
            low, high = kron(B, eye(d)), kron(A, eye(d))
            for time, group in enumerate(groups):
                for t, ports, xors in group:
                    if time == 0:
                        local = kron(B, P[t])
                    elif time in (1, 4):
                        local = low
                    elif time == 2:
                        local = add(low, kron(prior, P[t]))
                    elif time == 5:
                        local = add(low, kron(prior, sub(eye(d), P[t])))
                    else:
                        local = high
                    gates.append(dict(roles=ports, xors=xors, frame=kron(local, future)))
    require(next_role == W, 'Wrong compiled role count')
    rho = list(range(N, 2*N))+list(range(N))+list(range(2*N, W))
    return dict(W=W, m=m, rho=rho, gates=gates, source_frames=sources, sink_frames=sinks), accounting

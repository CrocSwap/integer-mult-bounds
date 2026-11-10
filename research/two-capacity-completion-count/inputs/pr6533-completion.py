"""Exact joint capacity rank counts over small prime fields.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
The kernel-subspace inversion is classical.
"""
from itertools import combinations, product
from functools import lru_cache


def require(ok, message):
    if not ok:
        raise ValueError(message)


def reduce_system(width, equations, p):
    rows = [list(row) for row in equations]
    pivots = []
    r = 0
    for j in range(width):
        k = next((k for k in range(r, len(rows)) if rows[k][j] % p), None)
        if k is None:
            continue
        rows[k], rows[r] = rows[r], rows[k]
        scale = pow(rows[r][j] % p, -1, p)
        rows[r] = [x*scale % p for x in rows[r]]
        for k in range(len(rows)):
            if k != r and rows[k][j] % p:
                c = rows[k][j] % p
                rows[k] = [(x-c*y) % p for x, y in zip(rows[k], rows[r])]
        pivots.append(j)
        r += 1
    if any(not any(row[:width]) and row[width] % p for row in rows):
        return None
    return tuple(tuple(row) for row in rows[:r]), tuple(pivots)


def rank(rows, p, width=None):
    if width is None:
        width = len(rows[0]) if rows else 0
    return len(reduce_system(width, [tuple(row)+(0,) for row in rows], p)[0])


@lru_cache(maxsize=15)
def subspaces(n, p):
    spaces = []
    for k in range(n+1):
        for pivots in combinations(range(n), k):
            free = [(i,j) for i in range(k) for j in range(pivots[i]+1,n) if j not in pivots]
            for values in product(range(p), repeat=len(free)):
                rows = [[int(j == pivots[i]) for j in range(n)] for i in range(k)]
                for (i,j), x in zip(free, values):
                    rows[i][j] = x
                spaces.append(tuple(tuple(row) for row in rows))
    return tuple(spaces)


@lru_cache(maxsize=None)
def gaussian(n, j, p):
    if j < 0 or j > n:
        return 0
    if j in (0,n):
        return 1
    return gaussian(n-1,j-1,p)+p**j*gaussian(n-1,j,p)


def validate(n, p, equations):
    require(type(n) is int and 0 <= n <= 4, 'dimension outside bounded API')
    require(type(p) is int and p in (2,3,5), 'unsupported prime field')
    require(type(equations) is tuple and all(type(row) is tuple and len(row) == n*n+1
            and all(type(x) is int and 0 <= x < p for x in row) for row in equations),
            'invalid affine equations')


def block_counts(rows, m, p, equations):
    """Count the rank of the last m rows of a rows-by-m affine matrix."""
    width = rows*m
    base = reduce_system(width,equations,p)
    if base is None:
        return {'rank_counts':[0]*(m+1),'kernel_incidence':[0]*(m+1)}
    base = base[0]
    incidence = [0]*(m+1)
    for space in subspaces(m,p):
        extra = []
        for vector in space:
            for i in range(rows-m,rows):
                row = [0]*(width+1)
                row[i*m:(i+1)*m] = vector
                extra.append(tuple(row))
        reduced = reduce_system(width,base+tuple(extra),p)
        if reduced is not None:
            incidence[len(space)] += p**(width-len(reduced[0]))
    nullities = [0]*(m+1)
    for j in range(m,-1,-1):
        nullities[j] = incidence[j]-sum(gaussian(t,j,p)*nullities[t] for t in range(j+1,m+1))
        require(nullities[j] >= 0, 'negative rank count')
    require(sum(nullities) == p**(width-len(base)), 'rank partition fails')
    return {'rank_counts':list(reversed(nullities)), 'kernel_incidence':incidence}


def rank_counts(n, p, equations):
    validate(n,p,equations)
    return block_counts(n,n,p,equations)


def annihilator(n, vectors, p):
    rows, pivots = reduce_system(n,[tuple(v)+(0,) for v in vectors],p)
    free = [j for j in range(n) if j not in pivots]
    basis = []
    for j in free:
        v = [0]*n
        v[j] = 1
        for row, pivot in zip(rows,pivots):
            v[pivot] = -row[j] % p
        basis.append(tuple(v))
    return tuple(basis)


def capacity_equations(n,p,fixed=(),capacities=()):
    validate(n,p,())
    def vector(v):
        require(type(v) is tuple and len(v) == n and all(type(x) is int and 0 <= x < p for x in v),
                'invalid vector')
    require(type(fixed) is tuple and type(capacities) is tuple,'immutable contract required')
    equations = []
    for pair in fixed:
        require(type(pair) is tuple and len(pair) == 2,'invalid fixed pair')
        source, target = pair
        vector(source); vector(target)
        for i in range(n):
            row = [0]*(n*n)+[target[i]]
            row[i*n:(i+1)*n] = source
            equations.append(tuple(row))
    for pair in capacities:
        require(type(pair) is tuple and len(pair) == 2,'invalid capacity pair')
        sources, targets = pair
        require(type(sources) is tuple and type(targets) is tuple,'immutable subspaces required')
        for v in sources+targets:
            vector(v)
        for a in sources:
            for b in annihilator(n,targets,p):
                equations.append(tuple(b[i]*a[j] % p for i in range(n) for j in range(n))+(0,))
    return tuple(equations)


def construct_block(rows,m,p,equations,target_rank=None):
    counts = block_counts(rows,m,p,equations)['rank_counts']
    if target_rank is not None:
        require(type(target_rank) is int and 0 <= target_rank <= m,'invalid target rank')
    if not any(counts):
        return None
    if target_rank is None:
        target_rank = max(i for i,c in enumerate(counts) if c)
    if counts[target_rank] == 0:
        return None
    current = equations
    entries = []
    for j in range(rows*m):
        for value in range(p):
            row = tuple(int(i == j) for i in range(rows*m))+(value,)
            candidate = current+(row,)
            if block_counts(rows,m,p,candidate)['rank_counts'][target_rank]:
                current = candidate
                entries.append(value)
                break
        else:
            raise ValueError('positive fiber has no next entry')
    matrix = tuple(tuple(entries[i*m:(i+1)*m]) for i in range(rows))
    require(rank(matrix[rows-m:],p,m) == target_rank,'constructor rank mismatch')
    require(all((sum(x*y for x,y in zip(row[:-1],entries))-row[-1]) % p == 0
                for row in equations),'constructor violates affine equations')
    return matrix


def construct(n,p,equations,target_rank=None):
    validate(n,p,equations)
    return construct_block(n,n,p,equations,target_rank)


def apply(matrix,vector,p):
    return tuple(sum(x*y for x,y in zip(row,vector)) % p for row in matrix)


def inverse(matrix,p):
    n=len(matrix)
    columns=[]
    for j in range(n):
        result=reduce_system(n,[tuple(row)+(int(i==j),) for i,row in enumerate(matrix)],p)
        require(result is not None and len(result[0])==n,'singular chart')
        columns.append(tuple(row[-1] for row in result[0]))
    return tuple(tuple(columns[j][i] for j in range(n)) for i in range(n))


def prepare_fixed(n,p,fixed,capacities):
    require(type(n) is int and 0 <= n <= 12,'ambient dimension outside bounded API')
    require(type(p) is int and p in (2,3,5),'unsupported prime field')
    require(type(fixed) is tuple and type(capacities) is tuple,'immutable contract required')
    def vector(v):
        require(type(v) is tuple and len(v)==n and all(type(x) is int and 0 <= x < p for x in v),'invalid vector')
    for pair in fixed:
        require(type(pair) is tuple and len(pair)==2,'invalid fixed pair')
        vector(pair[0]);vector(pair[1])
    source=tuple(pair[0] for pair in fixed);target=tuple(pair[1] for pair in fixed)
    u=len(fixed);m=n-u
    require(rank(source,p,n)==u and rank(target,p,n)==u,'fixed data must be an injection on a basis')
    require(0 <= m <= 4,'unfixed dimension exceeds four')
    def extend(basis):
        basis=list(basis)
        for j in range(n):
            e=tuple(int(i==j) for i in range(n))
            if rank(basis+[e],p,n)>len(basis):basis.append(e)
        return tuple(tuple(basis[j][i] for j in range(n)) for i in range(n))
    P,Q=extend(source),extend(target);Pi=inverse(P,p)
    equations=[]
    for pair in capacities:
        require(type(pair) is tuple and len(pair)==2,'invalid capacity pair')
        A,B=pair
        require(type(A) is tuple and type(B) is tuple,'immutable subspaces required')
        for v in A+B:vector(v)
        for a in A:
            x=apply(Pi,a,p)
            for b in annihilator(n,B,p):
                y=tuple(sum(b[i]*Q[i][j] for i in range(n))%p for j in range(n))
                rhs=-sum(y[i]*x[i] for i in range(u))%p
                equations.append(tuple(y[i]*x[u+j]%p for i in range(n) for j in range(m))+(rhs,))
    return u,m,Q,Pi,tuple(equations)


def fixed_rank_counts(n,p,fixed,capacities=()):
    u,m,_,_,eq=prepare_fixed(n,p,fixed,capacities)
    result=block_counts(n,m,p,eq)
    return {'rank_counts':[0]*u+result['rank_counts'], 'fixed_dimension':u,
            'quotient_dimension':m, 'kernel_incidence':result['kernel_incidence']}


def fixed_construct(n,p,fixed,capacities=(),target_rank=None):
    u,m,Q,Pi,eq=prepare_fixed(n,p,fixed,capacities)
    if target_rank is not None:
        require(type(target_rank) is int and 0 <= target_rank <= n,'invalid target rank')
        if target_rank<u:return None
    Y=construct_block(n,m,p,eq,None if target_rank is None else target_rank-u)
    if Y is None:return None
    T=tuple(tuple(int(i==j) for j in range(u))+Y[i] for i in range(n))
    TP=tuple(tuple(sum(T[i][k]*Pi[k][j] for k in range(n))%p for j in range(n)) for i in range(n))
    matrix=tuple(tuple(sum(Q[i][k]*TP[k][j] for k in range(n))%p for j in range(n)) for i in range(n))
    require(all(apply(matrix,a,p)==b for a,b in fixed),'fixed chart reconstruction fails')
    return matrix

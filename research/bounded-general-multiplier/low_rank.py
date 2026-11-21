"""Number exactly the invertible ternary matrices with consecutive ordinals."""


def group_sizes(n):
    if n < 0:
        raise ValueError("A matrix dimension must be nonnegative")
    sizes = [1]
    power = 1
    for _ in range(n):
        sizes.append(sizes[-1] * (3*power-1) * power)
        power *= 3
    return sizes


def encode_trits(values):
    i = 0
    for x in values:
        i = 3*i+x
    return i


def decode_trits(index, width):
    values = [0]*width
    for j in reversed(range(width)):
        index, values[j] = divmod(index,3)
    if index:
        raise ValueError("Ordinal outside its ternary field")
    return values


def rank_matrix(flat, n):
    if len(flat) != n*n or any(x not in (0,1,2) for x in flat):
        raise ValueError("Expected a square matrix of ternary residues")
    rows = [list(flat[i*n:(i+1)*n]) for i in range(n)]
    ordinal = 0
    for k in reversed(range(1,n+1)):
        col = [row[0] for row in rows]
        v = encode_trits(col)
        if v == 0:
            raise ValueError("Singular low matrix")
        pivot = next(i for i in range(k) if col[i])
        rows[0], rows[pivot] = rows[pivot], rows[0]
        # Every nonzero ternary residue is its own inverse.
        top = [x * col[pivot] % 3 for x in rows[0][1:]]
        count = 3**(k-1)
        digit = (v-1)*count + encode_trits(top)
        ordinal = ordinal*((3*count-1)*count) + digit
        rows = [[(x - row[0]*y) % 3 for x,y in zip(row[1:],top,strict=True)]
                for row in rows[1:]]
    return ordinal


def unrank_matrix(index, n):
    sizes = group_sizes(n)
    if not 0 <= index < sizes[-1]:
        raise ValueError("Low ordinal outside the invertible group")
    factors = []
    for k in reversed(range(1,n+1)):
        digit,index = divmod(index,sizes[k-1])
        v,t = divmod(digit,3**(k-1))
        factors.append((decode_trits(v+1,k),decode_trits(t,k-1)))
    rows = []
    for col,top in reversed(factors):
        pivot = next(i for i,x in enumerate(col) if x)
        col[0],col[pivot] = col[pivot],col[0]
        first = [col[0],*(col[0]*v % 3 for v in top)]
        rows = [first,*([a,*((x+a*y) % 3 for x,y in zip(row,top,strict=True))]
                        for a,row in zip(col[1:],rows,strict=True))]
        rows[0],rows[pivot] = rows[pivot],rows[0]
    return tuple(v for row in rows for v in row)

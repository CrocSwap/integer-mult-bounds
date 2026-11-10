"""Independent exact observer for the nilpotent banded-forward wrapper.

Prepared for @CubeJerry with separate source-aware OpenAI AI verification.
Rational elimination and page arithmetic reuse the A8 independent observer;
no author forward producer/consumer is imported. Apache-2.0.
"""
from fractions import Fraction as Q

def need(condition, message):
    if not condition:
        raise ValueError(message)

def identity(n):
    return tuple(tuple(Q(i == j) for j in range(n)) for i in range(n))

def product_matrix(a, b):
    need(bool(b) and all(len(row) == len(b) for row in a), "observer matrix dimensions")
    return tuple(tuple(sum((a[i][k]*b[k][j] for k in range(len(b))), Q())
                       for j in range(len(b[0]))) for i in range(len(a)))

def inverse(a):
    """Pivoted triangular elimination plus back-substitution, not producer GJ."""
    n = len(a)
    need(n > 0 and all(len(row) == n for row in a), "observer square inverse")
    upper = [list(map(Q, row)) for row in a]
    right = [list(row) for row in identity(n)]
    for k in range(n):
        pivot = next((i for i in range(k, n) if upper[i][k]), None)
        need(pivot is not None, "observer nonsingular original matrix")
        upper[k], upper[pivot] = upper[pivot], upper[k]
        right[k], right[pivot] = right[pivot], right[k]
        for i in range(k+1, n):
            ratio = upper[i][k]/upper[k][k]
            upper[i][k] = Q()
            for j in range(k+1, n):
                upper[i][j] -= ratio*upper[k][j]
            for j in range(n):
                right[i][j] -= ratio*right[k][j]
    answer = [[Q()]*n for _ in range(n)]
    for i in reversed(range(n)):
        for j in range(n):
            answer[i][j] = (right[i][j]-sum((upper[i][k]*answer[k][j]
                                            for k in range(i+1, n)), Q()))/upper[i][i]
    answer = tuple(map(tuple, answer))
    need(product_matrix(a, answer) == identity(n)
         and product_matrix(answer, a) == identity(n), "both original inverse identities")
    return answer

def sub(a, rows, columns):
    return tuple(tuple(a[i][j] for j in columns) for i in rows)

def toward_zero_integer(numerator, denominator):
    need(denominator > 0, "positive rounding denominator")
    return (1 if numerator >= 0 else -1)*(abs(numerator)//denominator)

def grid_integer(value, p):
    value = Q(value)
    return toward_zero_integer(value.numerator << p, value.denominator)

def padded(a, block):
    n = len(a)
    size = ((n+block-1)//block)*block
    return tuple(tuple(a[i][j] if i < n and j < n else Q(i == j)
                       for j in range(size)) for i in range(size))

def page_words(lower, upper, block, precision):
    """Derive all four page banks independently, including padded reversal."""
    banks = []
    for direction, raw in enumerate((lower, upper)):
        a = padded(raw, block)
        if direction:
            a = tuple(tuple(a[-i-1][-j-1] for j in range(len(a))) for i in range(len(a)))
        diagonals, couplings = [], []
        for start in range(0, len(a), block):
            rows = tuple(range(start, start+block))
            diagonal = inverse(sub(a, rows, rows))
            diagonals.extend(grid_integer(x, precision) for row in diagonal for x in row)
            if start:
                couplings.extend(grid_integer(a[i][j], precision)
                                 for i in rows for j in range(start-block, start))
        banks.extend((tuple(diagonals), tuple(couplings)))
    return tuple(banks)

def solve_pages(banks, rhs, block, p):
    """Pure integer completed-dot recurrence, returning original row order."""
    rows = len(rhs)
    need(rows > 0 and bool(rhs[0]), "nonempty oracle RHS")
    columns, scale = len(rhs[0]), 1 << p
    size = ((rows+block-1)//block)*block
    current = [list(row) for row in rhs]+[[0]*columns for _ in range(size-rows)]
    need(all(len(row) == columns for row in current), "rectangular oracle RHS")
    for direction in range(2):
        if direction:
            current = current[::-1]
        diagonal_bank, coupling_bank = banks[2*direction:2*direction+2]
        need(len(diagonal_bank) == size*block and len(coupling_bank) == (size-block)*block,
             "oracle complete page extents")
        output = []
        for start in range(0, size, block):
            residual = [list(row) for row in current[start:start+block]]
            if start:
                at = (start-block)*block
                for i in range(block):
                    for c in range(columns):
                        dot = sum(coupling_bank[at+i*block+j]*output[start-block+j][c]
                                  for j in range(block))
                        residual[i][c] = toward_zero_integer(scale*residual[i][c]-dot, scale)
            at = start*block
            for i in range(block):
                output.append([toward_zero_integer(sum(diagonal_bank[at+i*block+j]*residual[j][c]
                                                       for j in range(block)), scale)
                               for c in range(columns)])
        current = output
    return tuple(tuple(row) for row in current[::-1][:rows])


def lifted_factors(matrix, block, precision=None):
    n = len(matrix)
    need(n > 0 and all(len(row) == n for row in matrix), 'square forward source')
    need(block > 0 and block & (block-1) == 0, 'dyadic forward block')
    data = tuple(tuple(Q(x) if precision is None else Q(grid_integer(x,precision),1 << precision)
                       for x in row) for row in matrix)
    lift = tuple(tuple(-data[i//2][j//2] if i%2 == 0 and j%2 == 1 else Q()
                       for j in range(2*n)) for i in range(2*n))
    need(all(not value or abs(i-j) <= block for i,row in enumerate(lift)
             for j,value in enumerate(row)), 'admitted interleaved scalar band')
    lower = tuple(tuple(Q(i == j)+(lift[i][j] if i//block > j//block else 0)
                        for j in range(2*n)) for i in range(2*n))
    upper = tuple(tuple(Q(i == j)+(lift[i][j] if i//block <= j//block else 0)
                        for j in range(2*n)) for i in range(2*n))
    return lower, upper, lift


def check_pages(matrix, block, precision):
    exact = lifted_factors(matrix,block)
    pre = lifted_factors(matrix,block,precision)
    n = 2*len(matrix)
    need(product_matrix(exact[2],exact[2]) == tuple(tuple(Q() for _ in range(n)) for _ in range(n)),
         'interleaved lift is square zero')
    need(product_matrix(exact[0],exact[1]) == tuple(tuple(Q(i == j)+exact[2][i][j]
         for j in range(n)) for i in range(n)), 'exact interleaved factor product')
    exact_pages = page_words(*exact[:2],block,precision)
    short_pages = page_words(*pre[:2],block,precision)
    need(exact_pages == short_pages, 'prerounded and exact-source physical page words coincide')
    return exact_pages


def action(matrix, rhs, block, precision):
    """Direct three disjoint dot sums; no inverse/block-solver recurrence."""
    n = len(matrix)
    need(len(rhs) == n and bool(rhs[0]), 'nonempty forward observer RHS')
    columns = len(rhs[0]);scale = 1 << precision
    need(all(len(row) == columns for row in rhs), 'rectangular forward RHS')
    lifted_factors(matrix,block)  # independently enforce the stated band domain
    integers = tuple(tuple(grid_integer(value,precision) for value in row) for row in matrix)
    result = []
    for i in range(n):
        target_block = (2*i)//block
        parts = (tuple(j for j in range(n) if (2*j+1)//block < target_block),
                 tuple(j for j in range(n) if (2*j+1)//block > target_block),
                 tuple(j for j in range(n) if (2*j+1)//block == target_block))
        row = []
        for column in range(columns):
            current = 0
            for part in parts:
                dot = sum(integers[i][j]*rhs[j][column] for j in part)
                current = toward_zero_integer(current*scale+dot,scale)
            row.append(current)
        result.append(tuple(row))
    return tuple(result)


def check_action(matrix, rhs, block, precision, radius):
    radius = Q(radius); scale = 1 << precision
    n, columns = len(matrix), len(rhs[0])
    observed_radius = max(sum((abs(Q(rhs[i][j],scale)) for j in range(c,min(c+2,columns))),Q())
                          for i in range(n) for c in range(0,columns,2))
    need(observed_radius <= radius, 'actual incoming complex radius')
    words = action(matrix,rhs,block,precision)
    exact = product_matrix(matrix,tuple(tuple(Q(v,scale) for v in row) for row in rhs))
    short = tuple(tuple(Q(grid_integer(v,precision),scale) for v in row) for row in matrix)
    quantized = product_matrix(short,tuple(tuple(Q(v,scale) for v in row) for row in rhs))
    total_error = Q(); rounding_error = Q()
    for i in range(n):
        sparse = sum(value != 0 for value in matrix[i])
        for c in range(0,columns,2):
            error = sum((abs(Q(words[i][j],scale)-exact[i][j]) for j in range(c,min(c+2,columns))),Q())
            rounding = sum((abs(Q(words[i][j],scale)-quantized[i][j]) for j in range(c,min(c+2,columns))),Q())
            need(error <= (sparse*radius+6)/scale, 'original forward no-feedback error')
            need(rounding <= Q(6,scale), 'six-ulp complex completed-rounding error')
            total_error = max(total_error,error);rounding_error = max(rounding_error,rounding)
    banks = check_pages(matrix,block,precision)
    lifted_rhs = tuple(row for source in rhs for row in (tuple(0 for _ in source),tuple(source)))
    lifted_result = solve_pages(banks,lifted_rhs,block,precision)
    need(lifted_result[::2] == words and lifted_result[1::2] == tuple(map(tuple,rhs)),
         'direct three-sum oracle agrees with all lifted pages and source preservation')
    return dict(words=words, complex_error=total_error, rounding_error=rounding_error,
                row_sparsity=max(sum(value != 0 for value in row) for row in matrix),
                incoming_radius=observed_radius, page_words=banks)


def original_schur(reference, origin, length, boundary, kind='broad'):
    original = tuple(tuple(Q(reference.entry(kind,origin+i,origin+j).value)
                           for j in range(length)) for i in range(length))
    complete_inverse = inverse(original)
    return inverse(sub(complete_inverse,boundary,boundary))


def check_source(reference, matrix):
    expected = original_schur(reference,16,4,(0,3),'broad')
    need(tuple(map(tuple,matrix)) == expected, 'actual broad original-matrix Schur identity')
    narrow = original_schur(reference,16,4,(0,3),'narrow')
    need(expected != narrow, 'broad source is distinguished from the narrow matrix')
    return dict(kind='broad', original_inverse_identity_entries=32,
                schur_inverse_identity_entries=8, narrow_substitution_distinguished=True,
                reference_sha256=reference.description_hash)


def packed_bits(values, block, width):
    n, columns = len(values), len(values[0])
    rows = ((n+block-1)//block)*block
    result = []
    for first in range(0,columns,block):
        for i in range(rows):
            for c in range(first,first+block):
                value = values[i][c] if i < n and c < columns else 0
                need(-(1 << (width-1)) <= value < 1 << (width-1), 'forward observer carrier')
                result.extend((value >> bit)&1 for bit in range(width))
    return tuple(result)


def check_return(matrix, rhs, returned_bits, block, precision, width, radius):
    receipt = check_action(matrix,rhs,block,precision,radius)
    need(tuple(returned_bits) == packed_bits(receipt['words'],block,width),
         'complete projected forward output and zero padding')
    n, columns = len(matrix), len(rhs[0])
    k = (2*n+block-1)//block;j = (columns+block-1)//block
    receipt['matrix_calls'] = 2*(2*k-1)*j
    receipt['scalar_products'] = receipt['matrix_calls']*7**(block.bit_length()-1)
    return receipt

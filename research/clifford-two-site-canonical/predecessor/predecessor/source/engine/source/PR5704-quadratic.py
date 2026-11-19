"""Exact affine-support states for the retained Gaussian-dyadic gate grammar.

The method is classical stabilizer simulation. This implementation keeps the
absolute Gaussian-integer scalar. Ali Romman with substantial OpenAI Codex
assistance. Apache-2.0.
"""


def need(condition, message):
    if not condition:
        raise ValueError(message)


def bits(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask ^= bit


def term(poly, mask, value):
    value = (poly.get(mask, 0) + value) % 4
    if value:
        poly[mask] = value
    else:
        poly.pop(mask, None)


def affine(poly, form, coefficient):
    """Add a coefficient times an affine Boolean form, modulo four."""
    coefficient %= 4
    if not coefficient:
        return
    constant = form & 1
    term(poly, 0, coefficient * constant)
    signed = coefficient * (1 - 2 * constant)
    indices = list(bits(form >> 1))
    for i in indices:
        term(poly, 1 << i, signed)
    if coefficient & 1:
        for k, i in enumerate(indices):
            for j in indices[k + 1:]:
                term(poly, (1 << i) | (1 << j), 2)


def product(poly, left, right):
    """Add twice the product of two affine Boolean forms."""
    a, b = left & 1, right & 1
    u, v = list(bits(left >> 1)), list(bits(right >> 1))
    term(poly, 0, 2 * a * b)
    if b:
        for i in u:
            term(poly, 1 << i, 2)
    if a:
        for j in v:
            term(poly, 1 << j, 2)
    for i in u:
        for j in v:
            term(poly, (1 << i) | (1 << j), 2)


def substitute(poly, forms):
    result = {}
    for mask, coefficient in poly.items():
        if not mask:
            term(result, 0, coefficient)
        elif mask.bit_count() == 1:
            affine(result, forms[mask.bit_length() - 1], coefficient)
        else:
            need(mask.bit_count() == 2 and coefficient == 2,
                 'A phase must have only even quadratic terms')
            i, j = bits(mask)
            product(result, forms[i], forms[j])
    return result


def value(poly, argument):
    return sum(c for mask, c in poly.items() if argument & mask == mask) % 4


def basis(columns):
    """Return reduced binary columns with their original coordinates."""
    rows = {}
    for j, column in enumerate(columns):
        vector, coordinates = column, 1 << j
        while vector:
            pivot = vector.bit_length() - 1
            if pivot not in rows:
                rows[pivot] = (vector, coordinates)
                break
            other, witness = rows[pivot]
            vector ^= other
            coordinates ^= witness
        need(vector != 0, 'Support columns must be independent')
    for pivot in sorted(rows):
        vector, witness = rows[pivot]
        for other in sorted(rows):
            if other > pivot and rows[other][0] >> pivot & 1:
                x, y = rows[other]
                rows[other] = (x ^ vector, y ^ witness)
    return rows


def coordinates(rows, vector):
    result = 0
    for pivot in sorted(rows, reverse=True):
        if vector >> pivot & 1:
            column, witness = rows[pivot]
            vector ^= column
            result ^= witness
    return None if vector else result


def multiply_i(pair, power):
    a, b = pair
    return ((a, b), (-b, a), (-a, -b), (b, -a))[power % 4]


def multiply(left, right):
    a, b = left
    c, d = right
    return a * c - b * d, a * d + b * c


def normalize(pair, denominator):
    need(pair != (0, 0), 'A unitary state cannot be zero')
    while denominator and not ((pair[0] | pair[1]) & 1):
        pair = (pair[0] // 2, pair[1] // 2)
        denominator -= 1
    return pair, denominator


def matrix_vector(rows, vector):
    return sum(((row & vector).bit_count() & 1) << j for j, row in enumerate(rows))


def validate_integer(value_, limit, message):
    need(type(value_) is int and 0 <= value_ < limit, message)


def signature(n, circuit, initial=0, counters=None):
    """Return a canonical exact state without an exponential vector.

    A state is scalar times i^q(z) at offset xor columns*z. The columns
    remain independent. The returned tuple describes every amplitude.
    """
    need(type(n) is int and n >= 0, 'The width must be a nonnegative integer')
    validate_integer(initial, 1 << n, 'Initial basis index')
    columns, offset, poly = [], initial, {}
    scalar, denominator = (1, 0), 0
    counts = counters if counters is not None else {}

    def count(key):
        counts[key] = counts.get(key, 0) + 1

    for gate in circuit:
        need(isinstance(gate, (tuple, list)) and gate, 'Nonempty gate record')
        kind = gate[0]
        r = len(columns)
        if kind == 'P':
            need(len(gate) == 2 and len(gate[1]) == n, 'Permutation dimensions')
            rows = gate[1]
            for row in rows:
                validate_integer(row, 1 << n, 'Binary permutation row')
            basis(rows)
            offset = matrix_vector(rows, offset)
            columns = [matrix_vector(rows, x) for x in columns]
        elif kind == 'X':
            need(len(gate) == 2, 'Translation record')
            validate_integer(gate[1], 1 << n, 'Translation mask')
            offset ^= gate[1]
        elif kind == 'phase':
            need(len(gate) == 2 and type(gate[1]) is int, 'Global phase record')
            term(poly, 0, gate[1])
        elif kind == 'D':
            need(len(gate) == 3 and len(gate[1]) == len(gate[2]) == n,
                 'Diagonal dimensions')
            rows, linear = gate[1], gate[2]
            for i in range(n):
                validate_integer(rows[i], 1 << n, 'Binary diagonal row')
                need(type(linear[i]) is int and linear[i] % 2 == (rows[i] >> i & 1),
                     'Diagonal parity lift')
                for j in range(i):
                    need((rows[i] >> j & 1) == (rows[j] >> i & 1),
                         'Symmetric diagonal matrix')
            forms = [(offset >> i & 1) |
                     sum((column >> i & 1) << (j + 1) for j, column in enumerate(columns))
                     for i in range(n)]
            for i, coefficient in enumerate(linear):
                affine(poly, forms[i], coefficient)
                for j in bits(rows[i] >> (i + 1)):
                    product(poly, forms[i], forms[i + 1 + j])
        elif kind == 'C':
            need(len(gate) == 3 and type(gate[2]) is int and gate[2] in (-1, 1),
                 'Translation-root record and sign')
            q, sign = gate[1:]
            validate_integer(q, 1 << n, 'Translation-root mask')
            witness = coordinates(basis(columns), q)
            scalar = multiply(scalar, (1, sign))
            denominator += 1
            term(poly, 1 << r, -sign)
            if witness is None:
                columns.append(q)
                count('independent_root')
            else:
                # The last variable has zero output after this substitution.
                forms = [(1 << (i + 1)) | (((witness >> i) & 1) << (r + 1))
                         for i in range(r)] + [1 << (r + 1)]
                poly = substitute(poly, forms)
                last = 1 << r
                coefficient = poly.pop(last, 0)
                neighbours = 0
                for mask in list(poly):
                    if mask & last:
                        need(mask.bit_count() == 2 and poly[mask] == 2,
                             'Dependent-root quadratic term')
                        neighbours ^= mask ^ last
                        del poly[mask]
                if coefficient & 1:
                    scalar = multiply(scalar, (1, 1 if coefficient == 1 else -1))
                    affine(poly, neighbours << 1, -coefficient)
                    count('odd_elimination')
                else:
                    scalar = (2 * scalar[0], 2 * scalar[1])
                    constant = coefficient // 2
                    if neighbours:
                        pivot = (neighbours & -neighbours).bit_length() - 1
                        free = [i for i in range(r) if i != pivot]
                        forms = [0] * r
                        for j, i in enumerate(free):
                            forms[i] = 1 << (j + 1)
                        forms[pivot] = constant | sum(
                            1 << (j + 1) for j, i in enumerate(free) if neighbours >> i & 1)
                        poly = substitute(poly, forms)
                        if constant:
                            offset ^= columns[pivot]
                        columns = [columns[i] ^ (columns[pivot] if neighbours >> i & 1 else 0)
                                   for i in free]
                        count('even_restriction')
                    else:
                        need(constant == 0, 'A unitary root cannot annihilate the state')
                        count('even_free')
            scalar, denominator = normalize(scalar, denominator)
        else:
            raise ValueError('Unknown gate: ' + str(kind))
        need(len(columns) <= n, 'Support dimension cannot exceed width')
        counts['peak_support_rank'] = max(counts.get('peak_support_rank', 0), len(columns))

    rows = basis(columns)
    reduced_offset, shift = offset, 0
    for pivot in sorted(rows, reverse=True):
        if reduced_offset >> pivot & 1:
            column, witness = rows[pivot]
            reduced_offset ^= column
            shift ^= witness
    ordered = [rows[p] for p in sorted(rows)]
    forms = [(shift >> i & 1) | sum(((witness >> i) & 1) << (j + 1)
             for j, (_, witness) in enumerate(ordered)) for i in range(len(columns))]
    poly = substitute(poly, forms)
    scalar = multiply_i(scalar, poly.pop(0, 0))
    scalar, denominator = normalize(scalar, denominator)
    return (n, reduced_offset, tuple(x for x, _ in ordered), tuple(sorted(poly.items())),
            scalar[0], scalar[1], denominator)


def amplitude(state, index):
    n, offset, columns, terms, real, imag, denominator = state
    validate_integer(index, 1 << n, 'Amplitude index')
    argument = coordinates(basis(columns), index ^ offset)
    if argument is None:
        return (0, 0), 0
    pair = multiply_i((real, imag), value(dict(terms), argument))
    return pair, denominator


def equal_operators(left, right):
    """Compare valid retained Clifford objects, including absolute phase.

    Their tableaus must be derived from their circuits by the retained exact
    constructors. An arbitrary supplied tableau is not a valid input contract.
    """
    return (left.n == right.n and left.tab == right.tab and
            signature(left.n, left.circuit) == signature(right.n, right.circuit))

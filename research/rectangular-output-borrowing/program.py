"""Literal full-row shears; Apache-2.0, substantial OpenAI Codex assistance."""
from collections import Counter


def inverse(word):
    return [(-sgn, f, src, dst) for sgn, f, src, dst in reversed(word)]


def schedules(m, k):
    if m < 1 or k < 2:
        raise ValueError('requires m >= 1 and k >= 2')
    ys = list(range(m, m + k))

    def borrowed(js):
        q, r = ys[-1], ys[0]
        before = [(-1, f'A{i}', q, t) for i, t in enumerate(ys) if t != q]
        load = [(1, f'B{j}', j, q) for j in js]
        word = before + load + inverse(before) + inverse(load)
        before = [(-1, f'A{k-1}', r, q)]
        load = [(1, f'B{j}', j, r) for j in js]
        return word + before + load + inverse(before) + inverse(load)

    separate_outputs = []
    for i, t in enumerate(ys):
        z = ys[(i + 1) % k]
        before = [(-1, f'A{i}', z, t)]
        load = [(1, f'B{j}', j, z) for j in range(m)]
        separate_outputs += before + load + inverse(before) + inverse(load)
    z = m + k
    load = [(1, f'B{j}', j, z) for j in range(m)]
    reads = [(1, f'A{i}', z, t) for i, t in enumerate(ys)]
    return {
        'borrowed': borrowed(range(m)),
        'separate_sources': [op for j in range(m) for op in borrowed([j])],
        'separate_outputs': separate_outputs,
        'dedicated': load + reads + inverse(load) + inverse(reads),
    }


def scratch(n):
    if n < 1:
        raise ValueError('empty products are outside the interface')
    return (n - 1).bit_length()


def leaf_count(n):
    if n == 1:
        return 1
    return 2 * leaf_count(n // 2) + 2 * leaf_count(n - n // 2)


def product(factors, source, target, pool):
    """Factors are in application order. Every recursion port is reserved."""
    if source == target or source in pool or target in pool or len(set(pool)) != len(pool):
        raise ValueError('aliased child ports/scratch')
    if len(pool) < scratch(len(factors)):
        raise ValueError('insufficient private child scratch')
    if len(factors) == 1:
        return [(1, factors[0], source, target)]
    cut = len(factors) // 2
    z = pool[0]
    right = product(factors[:cut], source, z, pool[1:])
    left = product(factors[cut:], z, target, pool[1:])
    return inverse(left) + right + left + inverse(right)


def expand(queries, factors, pool):
    word, boundaries = [], []
    for sign, label, source, target in queries:
        block = product(factors[label], source, target, pool)
        if sign < 0:
            block = inverse(block)
        start = len(word)
        word.extend(block)
        boundaries.append((start, len(word), sign, label, source, target))
    return word, boundaries


def multiplicities(word):
    return dict(sorted(Counter(op[1] for op in word).items()))


def invoice(word, rows, factor_names, length):
    """Charge the explicit coefficient/source/target/home data-tape trace."""
    factor_index = {f: i for i, f in enumerate(sorted(factor_names))}
    travel = 0
    for sign, f, src, dst in word:
        cursor = 0
        for i in range(length):
            for j in range(length):
                for address in (rows * length + factor_index[f] * length**2 + i * length + j,
                                src * length + j):
                    travel += abs(address - cursor)
                    cursor = address
            address = dst * length + i
            travel += abs(address - cursor)
            cursor = address
        travel += cursor
    n = len(word)
    return {
        'leaves': n, 'data_rows': rows, 'data_words': rows * length,
        'coefficient_words': len(factor_names) * length**2,
        'coefficient_reads': n * length**2, 'source_reads': n * length**2,
        'target_reads': n * length, 'target_writes': n * length,
        'multiplications': n * length**2, 'additions': n * length * (length + 1),
        'sign_negations': sum(op[0] < 0 for op in word) * length,
        'accumulator_zero_assignments': n * length,
        'head_travel_word_slots': travel, 'instruction_records': n,
    }

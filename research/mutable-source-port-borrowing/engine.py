"""Fixed-cap additive echoes. Hanson Sun / Codex; Apache-2.0.

The echo and port-borrowing mechanisms are credited in README.md. The new
choice is to lend the external source as well, with an endpoint contract.
"""
from itertools import combinations


def require(condition, message):
    if not condition:
        raise ValueError(message)


def compositions(n, k):
    for cuts in combinations(range(1, n), k - 1):
        points = (0,) + cuts + (n,)
        yield tuple(points[i + 1] - points[i] for i in range(k))


def weights(k):
    require(type(k) is int and 2 <= k <= 4, "arity must be 2, 3 or 4")
    return (2,) + (4,) * (k - 2) + (2,)


def plan(limit):
    """Exact unit-price minima in three explicitly different template classes.

    T: no protected source available, at most three children;
    R: protected row zero is the source, first child R and other children T;
    M: all five rows mutable, at most four children everywhere.
    """
    require(type(limit) is int and 1 <= limit <= 128, "limit outside [1,128]")
    bills = {key: [0, 1] for key in "TRM"}
    splits = {key: [None, None] for key in "TRM"}
    candidates = {key: 0 for key in "TRM"}
    for n in range(2, limit + 1):
        best = {key: None for key in "TRM"}
        for k in range(2, min(4, n) + 1):
            for sizes in compositions(n, k):
                for key in "TRM":
                    if key == "T" and k == 4:
                        continue
                    types = ("R",) + ("T",) * (k - 1) if key == "R" else (key,) * k
                    cost = sum(w * bills[t][s] for w, t, s in zip(weights(k), types, sizes))
                    candidate = (cost, k, sizes)
                    candidates[key] += 1
                    if best[key] is None or candidate < best[key]:
                        best[key] = candidate
        for key in "TRM":
            bills[key].append(best[key][0])
            splits[key].append(best[key][2])

    def build(n, key, start=0):
        if n == 1:
            return start
        sizes = splits[key][n]
        children = []
        for i, size in enumerate(sizes):
            kind = "T" if key == "R" and i else key
            children.append(build(size, kind, start))
            start += size
        return tuple(children)

    return bills, {key: build(limit, key) for key in "TRM"}, candidates


def leaf_ids(tree):
    if type(tree) is int:
        require(tree >= 0, "negative factor index")
        return [tree]
    require(isinstance(tree, (tuple, list)) and 2 <= len(tree) <= 4, "invalid tree")
    return [i for child in tree for i in leaf_ids(child)]


def validate(tree):
    ids = leaf_ids(tree)
    require(ids == list(range(len(ids))), "factors must be consecutive and ordered")
    return len(ids)


def inverse(word):
    return [(s, t, f, -q) for s, t, f, q in reversed(word)]


def chain_word(k):
    weights(k)
    prefix = [(i, 1) for i in range(k - 1)]
    middle = prefix[1:]
    inv = lambda xs: [(i, -q) for i, q in reversed(xs)]
    return prefix + [(k - 1, 1)] + inv(prefix) + middle + [(k - 1, -1)] + inv(middle)


def emit(tree, mutable_source=True, sign=1, src=0, dst=1):
    """Materialize only after validating the tree and all port allocations."""
    validate(tree)
    require(type(mutable_source) is bool, "mutable_source must be bool")
    require(type(sign) is int and sign in (-1, 1), "invalid sign")
    require(type(src) is int and type(dst) is int and 0 <= src < 5 and 0 <= dst < 5 and src != dst,
            "invalid root ports")
    require(mutable_source or dst != 0, "protected row zero cannot be a target")
    # Both comparators have exactly five physical rows. Row zero is lent only
    # by M; the fixed order makes every inverse and invoice reproducible.
    pool = (2, 3, 4, 0, 1) if mutable_source else (2, 3, 4, 1)

    def lower(node, src, dst):
        if type(node) is int:
            return [(src, dst, node, 1)]
        spare = [r for r in pool if r not in (src, dst)][:len(node) - 1]
        require(len(spare) == len(node) - 1, "insufficient unprotected ports")
        ports = [src] + spare + [dst]
        children = [lower(c, ports[i], ports[i + 1]) for i, c in enumerate(node)]
        out = []
        for i, direction in chain_word(len(node)):
            out.extend(children[i] if direction > 0 else inverse(children[i]))
        return out

    result = lower(tree, src, dst)
    return result if sign > 0 else inverse(result)


def word_cost(tree):
    if type(tree) is int:
        return 1
    return sum(w * word_cost(c) for w, c in zip(weights(len(tree)), tree))


def validate_word(word, n):
    for instruction in word:
        require(len(instruction) == 4 and all(type(v) is int for v in instruction), "invalid instruction")
        src, dst, factor, sign = instruction
        require(0 <= src < 5 and 0 <= dst < 5 and src != dst, "aliased or invalid port")
        require(0 <= factor < n and sign in (-1, 1), "invalid factor or direction")


def matmul(a, b):
    return [[sum(a[i][k] * b[k][j] for k in range(len(b))) for j in range(len(b[0]))]
            for i in range(len(a))]


def factor_bank(n, dimension=2):
    """Seed 51 fixes both the main size and this small noncommuting alphabet."""
    import random
    rng = random.Random(51 + dimension)
    bank = []
    for _ in range(n):
        a = [[int(i == j) for j in range(dimension)] for i in range(dimension)]
        if dimension == 1:
            a[0][0] = rng.choice((-2, -1, 1, 2))
        else:
            i, j = rng.sample(range(dimension), 2)
            a[i][j] = rng.choice((-1, 1))
        bank.append(a)
    return bank


def final_product(bank):
    d = len(bank[0])
    out = [[int(i == j) for j in range(d)] for i in range(d)]
    for factor in bank:
        out = matmul(factor, out)
    return out


def endpoint_width(bank, bound=7):
    # No uncharged product computation: the cheap norm-product bound is used
    # for admission. Matrix products below are verification only.
    product_norm = 1
    for a in bank:
        product_norm *= max(sum(abs(x) for x in row) for row in a)
    radius = bound * (1 + product_norm)
    return max(bound, radius).bit_length() + 1


def dense_execute(word, bank, initial, width):
    """Literal modular scalar/access backend, including owned-work cleanup.

    Counters are macro operations, not constant-time bit or physical-runtime
    claims. Each data/coefficient access and head return is explicit.
    """
    n, length = len(bank), len(bank[0])
    validate_word(word, n)
    require(type(width) is int and width >= 1, "positive width required")
    modulus = 1 << width
    require(len(initial) == 5 and all(len(r) == length for r in initial), "invalid data shape")
    require(all(type(x) is int and 0 <= x < modulus for row in initial for x in row), "noncanonical input")
    require(all(len(a) == length and all(len(r) == length for r in a) for a in bank), "invalid matrix shape")
    data = [row[:] for row in initial]
    coefficients = [[[x % modulus for x in row] for row in a] for a in bank]
    stats = dict(multiply=0, add=0, reduce=0, zero=4, read=0, write=0,
                 intercell_steps=0, source_writes=0, leaf_calls=len(word))
    position = 0

    def access(address, mode):
        nonlocal position
        stats[mode] += 1
        stats["intercell_steps"] += abs(address - position)
        position = address

    source_changed = False
    max_product = max_accumulator = max_target_abs = 0
    for src, dst, factor, sign in word:
        for i in range(length):
            acc = 0
            stats["zero"] += 1
            for j in range(length):
                access(src * length + j, "read")
                value = data[src][j]
                access(5 * length + (factor * length + i) * length + j, "read")
                coefficient = coefficients[factor][i][j]
                product = value * coefficient
                stats["multiply"] += 1
                max_product = max(max_product, product)
                require(0 <= product < (1 << (2 * width)), "product overflow")
                product %= modulus
                stats["reduce"] += 1
                acc += product
                stats["add"] += 1
                max_accumulator = max(max_accumulator, acc)
                require(0 <= acc < (1 << (width + 1)), "accumulator overflow")
                acc %= modulus
                stats["reduce"] += 1
            access(dst * length + i, "read")
            value = data[dst][i] + sign * acc
            stats["add"] += 1
            max_target_abs = max(max_target_abs, abs(value))
            require(-(1 << (width + 1)) <= value < (1 << (width + 1)), "target overflow")
            value %= modulus
            stats["reduce"] += 1
            access(dst * length + i, "write")
            data[dst][i] = value
            if dst == 0:
                stats["source_writes"] += 1
        acc = value = coefficient = product = 0
        stats["zero"] += 4
        require((acc, value, coefficient, product) == (0, 0, 0, 0), "private work not cleared")
        stats["intercell_steps"] += position
        position = 0
        source_changed |= data[0] != initial[0]
    accesses = stats["read"] + stats["write"]
    record_bits = max(1, (n - 1).bit_length()) + 7
    stats.update(
        commands=sum(stats[k] for k in ("multiply", "add", "reduce", "zero", "read", "write")),
        data_bits=5 * length * width, coefficient_bits=n * length * length * width,
        private_bits=5 * width + 3, data_bit_actions=width * accesses,
        data_head_steps=width * stats["intercell_steps"] + 2 * (width - 1) * accesses,
        program_bits=len(word) * record_bits, program_head_steps=2 * len(word) * record_bits,
        dispatches=len(word), address_events=accesses,
        address_bits=max(1, (5 * length + n * length * length - 1).bit_length()),
        setup_reductions=n * length * length + 2 * length,
        source_changed=source_changed, max_product=max_product,
        max_accumulator=max_accumulator, max_target_abs=max_target_abs,
    )
    return data, stats

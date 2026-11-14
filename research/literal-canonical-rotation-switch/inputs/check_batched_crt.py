"""Exact finite controls for the draft; not a machine-cost certificate."""
import itertools
import json
import math


def need(condition, message):
    if not condition:
        raise ValueError(message)


def benes(permutation):
    """Return (bit, switch table) layers on precisely len(permutation) wires."""
    size = len(permutation)
    need(size >= 2 and size & (size - 1) == 0, "dyadic network size")
    need(sorted(permutation) == list(range(size)), "permutation")
    if size == 2:
        return [(0, (permutation[0],) * 2)]
    inverse = [0] * size
    for x, y in enumerate(permutation):
        inverse[y] = x
    color = [-1] * size
    for initial in range(size):
        if color[initial] >= 0:
            continue
        color[initial] = 0
        stack = [initial]
        while stack:
            x = stack.pop()
            for other in (x ^ 1, inverse[permutation[x] ^ 1]):
                if color[other] < 0:
                    color[other] = color[x] ^ 1
                    stack.append(other)
                need(color[other] == color[x] ^ 1, "even cycle coloring")
    first = tuple(color[x] ^ (x & 1) for x in range(size))
    last = tuple(color[inverse[y]] ^ (y & 1) for y in range(size))
    children = []
    for c in (0, 1):
        child = [None] * (size // 2)
        for x in range(size):
            if color[x] == c:
                child[x // 2] = permutation[x] // 2
        children.append(benes(child))
    result = [(0, first)]
    for left, right in zip(*children):
        need(left[0] == right[0], "common network schedule")
        table = tuple((left, right)[x & 1][1][x // 2] for x in range(size))
        result.append((left[0] + 1, table))
    result.append((0, last))
    return result


def run_network(layers, value):
    for bit, table in layers:
        value ^= table[value] << bit
    return value


def rotation(size, modulus, offset):
    return tuple((x + offset) % modulus if x < modulus else x for x in range(size))


def decode_group(values, moduli):
    """Recover the integer from locally scaled CRT residues."""
    product = math.prod(moduli)
    answer = 0
    prefix = 1
    for value, modulus in zip(values, moduli):
        complement = product // modulus
        residue = value * prefix % modulus
        answer += residue * complement * pow(complement, -1, modulus)
        prefix *= modulus
    return answer % product


def balanced(values, moduli, reverse=False, compiled=False):
    count = len(moduli)
    need(count > 0 and count & (count - 1) == 0, "power-of-two axis count")
    state = list(values)
    levels = list(range(1, count.bit_length()))
    for level in reversed(levels) if reverse else levels:
        width = 1 << level
        half = width // 2
        for start in range(0, count, width):
            middle = start + half
            valid = all(state[i] < moduli[i] for i in range(start, middle))
            lower = decode_group(state[start:middle], moduli[start:middle]) if valid else 0
            prefix = math.prod(moduli[start:middle])
            for i in range(middle, start + width):
                offset = lower * pow(prefix, -1, moduli[i]) % moduli[i]
                if reverse:
                    offset = -offset % moduli[i]
                if compiled:
                    size = 1 << (moduli[i] - 1).bit_length()
                    state[i] = run_network(benes(rotation(size, moduli[i], offset)), state[i])
                elif state[i] < moduli[i]:
                    state[i] = (state[i] + offset) % moduli[i]
                prefix *= moduli[i]
    return tuple(state)


def direct(values, moduli):
    prefix = 1
    integer = 0
    prefixes = []
    for value, modulus in zip(values, moduli):
        prefixes.append(prefix)
        integer += value * prefix
        prefix *= modulus
    return tuple(integer * pow(prefix, -1, modulus) % modulus
                 for prefix, modulus in zip(prefixes, moduli))


def primitive_f(u, t, y, bits, positions, ybits, control_bits):
    radix = 1 << bits
    control_mask = (1 << control_bits) - 1
    ymask = (1 << ybits) - 1
    z = [(u >> (bits * i)) & 1 for i in range(len(positions))]
    digits = [(t >> (bits * i)) & (radix - 1) for i in range(len(positions))]
    y = (y + sum(2 * bit * digit * (1 << pos)
                 for bit, digit, pos in zip(z, digits, positions))) & ymask
    t = (t + sum(((y >> pos) & 1) << (bits * i)
                 for i, pos in enumerate(positions))) & control_mask
    digits = [(t >> (bits * i)) & (radix - 1) for i in range(len(positions))]
    y = (y + sum(bit * (1 - 2 * digit) * (1 << pos)
                 for bit, digit, pos in zip(z, digits, positions))) & ymask
    t = (t - sum((((y >> pos) & 1) ^ z[i]) << (bits * i)
                 for i, pos in enumerate(positions))) & control_mask
    return u, t, y


def compact(u, t, y, source, bits=2, positions=(0,), ybits=6, control_bits=2):
    need(control_bits >= bits * len(positions), "control field capacity")
    mask = (1 << control_bits) - 1
    u, t, y = primitive_f(u, t, y, bits, positions, ybits, control_bits)
    u = (u + sum(value << (bits * i) for i, value in enumerate(source(y)))) & mask
    u, t, y = primitive_f(u, t, y, bits, positions, ybits, control_bits)
    u = (u - sum(value << (bits * i) for i, value in enumerate(source(y)))) & mask
    return u, t, y


def good(u, t, y, bits=2, positions=(0,), guard=6):
    radix = 1 << bits
    return all(((u >> (bits * i)) & (radix - 1)) != radix - 1
               and ((t >> (bits * i)) & (radix - 1)) != radix - 1
               and 2 * radix <= ((y >> (pos + 1)) & ((1 << (guard - 1)) - 1))
               < (1 << (guard - 1)) - 2 * radix
               for i, pos in enumerate(positions))


def linear_guard(u, t, y, bits=2, positions=(0,), guard=6,
                 control_bits=2, ybits=6):
    """Bit-by-bit guard predicate; source functions are never evaluated."""
    steps = 0
    accepted = True
    for word in (u, t):
        for digit in range(len(positions)):
            all_ones = True
            for bit in range(bits):
                all_ones = all_ones and bool((word >> (digit * bits + bit)) & 1)
                steps += 1
            accepted = accepted and not all_ones
    for pos in positions:
        lower = 2 * (1 << bits)
        upper = (1 << (guard - 1)) - lower
        comparison = [0, 0]
        for bit in range(guard - 2, -1, -1):
            value = (y >> (pos + 1 + bit)) & 1
            for index, bound in enumerate((lower, upper)):
                if comparison[index] == 0:
                    comparison[index] = value - ((bound >> bit) & 1)
            steps += 2
        accepted = accepted and comparison[0] >= 0 and comparison[1] < 0
    need(steps <= 2 * control_bits + 2 * ybits, "linear tested-bit budget")
    return accepted


def check():
    network_count = address_count = 0
    for bits in range(1, 7):
        size = 1 << bits
        for modulus in range(max(2, size // 2), size):
            for offset in range(modulus):
                permutation = rotation(size, modulus, offset)
                layers = benes(permutation)
                need(len(layers) == 2 * bits - 1, "network depth")
                for bit, table in layers:
                    need(all(table[x] == table[x ^ (1 << bit)] for x in range(size)),
                         "switch control omits its target bit")
                need(tuple(run_network(layers, x) for x in range(size)) == permutation,
                     "all-column modular rotation")
                network_count += 1
                address_count += size
    crt_addresses = valid_addresses = 0
    for moduli in ((3,), (3, 5), (3, 5, 7, 11)):
        sizes = [1 << (s - 1).bit_length() for s in moduli]
        seen = set()
        for source in itertools.product(*(range(size) for size in sizes)):
            target = balanced(source, moduli)
            need(target not in seen, "padded CRT injection")
            seen.add(target)
            need(balanced(target, moduli, reverse=True) == source, "padded CRT inverse")
            valid = all(x < s for x, s in zip(source, moduli))
            need(valid == all(x < s for x, s in zip(target, moduli)), "padding invariance")
            if valid:
                need(target == direct(source, moduli), "scaled CRT endpoint")
                valid_addresses += 1
            need(balanced(source, moduli, compiled=True) == target, "compiled CRT endpoint")
            crt_addresses += 1
    compact_cases = good_cases = repair_cases = 0
    functions = [lambda y: (0,), lambda y: (1,), lambda y: ((y >> 2) & 1,),
                 lambda y: ((y >> 1).bit_count() & 1,),
                 lambda y: ((((y >> 1) & 1) & ((y >> 4) & 1)),)]
    for source_function, control_bits in itertools.product(functions, (2, 4)):
        actual = {}
        ideal = {}
        for u, t, y in itertools.product(range(1 << control_bits),
                                         range(1 << control_bits), range(64)):
            start = (u, t, y)
            end = compact(*start, source_function, control_bits=control_bits)
            wanted = (u, t, y ^ source_function(y)[0])
            need(end not in actual, "actual gadget bijection")
            need(wanted not in ideal, "ideal switch bijection")
            actual[end] = start
            ideal[wanted] = start
            is_good = good(*start)
            need(linear_guard(*start, control_bits=control_bits) == is_good,
                 "linear guard agrees with interval predicate")
            need(good(*end) == is_good and good(*wanted) == is_good, "good/bad invariance")
            if is_good:
                need(end == wanted, "compact endpoint on good addresses")
                good_cases += 1
            compact_cases += 1
        # Each arbitrary dirty input column follows S, then T S^-1 on bad holes.
        for end, start in actual.items():
            u, t, y = start
            repaired = (u, t, y ^ source_function(y)[0]) if not good(*end) else end
            need(ideal[repaired] == start, "sparse correction column")
            repair_cases += not good(*end)
    multi_cases = 0
    def source_pair(y):
        return (y >> 3) & 1, (y & ~65).bit_count() & 1
    for u, t in ((0, 0), (0, 15), (5, 5), (10, 10), (15, 0), (15, 15)):
        for y in range(1 << 12):
            start = (u, t, y)
            end = compact(*start, source_pair, positions=(0, 6), ybits=12, control_bits=4)
            f0, f1 = source_pair(y)
            wanted = (u, t, y ^ f0 ^ (f1 << 6))
            is_good = good(*start, positions=(0, 6))
            need(linear_guard(*start, positions=(0, 6), control_bits=4, ybits=12) == is_good,
                 "two-target linear guard")
            need(good(*end, positions=(0, 6)) == is_good, "two-target guard invariance")
            if is_good:
                need(end == wanted, "two-target compact endpoint")
            multi_cases += 1
    return dict(status="PASS_FINITE_BATCHED_CRT_CONTROLS", network_count=network_count,
                network_addresses=address_count, crt_addresses=crt_addresses,
                valid_crt_addresses=valid_addresses, compact_addresses=compact_cases,
                good_addresses=good_cases, repaired_bad_addresses=repair_cases,
                two_target_addresses=multi_cases, linear_guard_verified=True,
                machine_cost_verified=False, multiplication_kappa_claimed=False)


if __name__ == "__main__":
    print(json.dumps(check(), sort_keys=True, indent=2))

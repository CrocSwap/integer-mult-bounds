"""Exact, read-only corroboration of the mixed-lane theorem. Standard library."""

import hashlib
import json
from math import comb
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def classification(width, forward, inverse):
    """Return (child width, spectator multiplicity, phase exponent), or None."""
    require(all(type(x) is int for x in (width, forward, inverse)), "integers required")
    require(width > 0 and width % 4 == 2, "width must be 2 modulo 4")
    require(min(forward, inverse) >= 0 and forward + inverse > 0, "invalid lanes")
    total, imbalance = forward + inverse, forward - inverse
    for step in range(total.bit_length()):
        scale = 1 << step
        if abs(imbalance) * scale == total and total % (scale * scale) == 0:
            phase = ((0 if imbalance > 0 else 2) - step) % 4
            return width + 2 * step, total // (scale * scale), phase
    return None


def spectrum(width):
    return tuple(sum(comb(width, k) for k in range(r, width + 1, 4)) for r in range(4))


def spectral_sweep():
    """Compare the theorem with literal binomial eigenspace capacities."""
    spectra = [spectrum(w) for w in range(37)]
    recurrence = (1, 0, 0, 0)
    for width in range(37):
        require(spectra[width] == recurrence, "independent spectrum recurrence")
        recurrence = tuple(recurrence[r] + recurrence[(r - 1) % 4] for r in range(4))
    targets = candidates = matches = upgrades = 0
    for width in range(2, 31, 4):
        base = spectra[width]
        for total in range(1, 65):
            dimension = total << width
            for forward in range(total + 1):
                inverse = total - forward
                target = tuple(forward * base[r] + inverse * base[-r % 4] for r in range(4))
                actual = []
                for child in range(1, width + total.bit_length()):
                    if dimension % (1 << child):
                        continue
                    spectator = dimension >> child
                    for phase in range(4):
                        candidates += 1
                        trial = tuple(spectator * spectra[child][(r - phase) % 4] for r in range(4))
                        if target == trial:
                            actual.append((child, spectator, phase))
                predicted = classification(width, forward, inverse)
                require(actual == ([] if predicted is None else [predicted]), "classification mismatch")
                targets += 1
                matches += len(actual)
                upgrades += int(predicted is not None and predicted[0] > width)
    return {"targets": targets, "phase_candidates": candidates, "matches": matches,
            "proper_width_upgrades": upgrades}


def gaussian_product(left, right):
    a, b = left
    c, d = right
    return a * c - b * d, a * d + b * c


def gaussian_power(value, exponent):
    result = (1, 0)
    for _ in range(exponent):
        result = gaussian_product(result, value)
    return result


def kernel_numerator(width, inverse=False):
    """Tensor coefficients, with common denominator 2**width."""
    values = []
    for distance in range(width + 1):
        value = gaussian_product(gaussian_power((1, 1), width - distance),
                                 gaussian_power((1, -1), distance))
        values.append((value[0], -value[1]) if inverse else value)
    return values


def integer_product(left, right):
    columns = tuple(zip(*right))
    return [[sum(a * b for a, b in zip(row, col)) for col in columns] for row in left]


def complex_left(left, right):
    columns = tuple(zip(*right))
    return [[(sum(a[0] * b for a, b in zip(row, col)),
              sum(a[1] * b for a, b in zip(row, col))) for col in columns] for row in left]


def complex_right(left, right):
    columns = tuple(zip(*right))
    return [[(sum(a * b[0] for a, b in zip(row, col)),
              sum(a * b[1] for a, b in zip(row, col))) for col in columns] for row in left]


def fixture(width, forward, inverse, padding):
    choice = classification(width, forward, inverse)
    require(choice is not None, "fixture has no solution")
    child, spectator, phase = choice
    lane_size, total = 1 << width, forward + inverse
    active = lane_size * total
    require(active <= 64 and 0 <= padding <= 3, "dense fixture capacity")
    size = active + padding
    target_eigen = [(lane, a, ((1 if lane < forward else -1) * a.bit_count()) % 4)
                    for lane in range(total) for a in range(lane_size)]
    buckets = [[(a, s) for a in range(1 << child) for s in range(spectator)
                if (phase + a.bit_count()) % 4 == r] for r in range(4)]
    used = [0] * 4
    matched = []
    for _, _, eigen in target_eigen:
        require(used[eigen] < len(buckets[eigen]), "eigenspace exhausted")
        matched.append(buckets[eigen][used[eigen]])
        used[eigen] += 1
    require(used == list(map(len, buckets)), "unmatched eigenspace")
    u = [[int(x // lane_size == lane) * (-1 if (x % lane_size & a).bit_count() % 2 else 1)
          for lane, a, _ in target_eigen] for x in range(active)]
    v = [[int(x % spectator == s) * (-1 if (x // spectator & a).bit_count() % 2 else 1)
          for a, s in matched] for x in range(active)]
    encoding = integer_product(v, list(zip(*u)))
    decoding = integer_product(u, list(zip(*v)))
    for matrix, denominator in ((encoding, 1 << width), (decoding, 1 << child)):
        for row in matrix:
            row.extend([0] * padding)
        matrix.extend([[denominator * int(x == y) for y in range(size)]
                       for x in range(active, size)])
    return choice, encoding, decoding


def operators(width, forward, inverse, padding, choice):
    child, spectator, phase = choice
    lane_size = 1 << width
    active = (forward + inverse) * lane_size
    size = active + padding
    kernels = (kernel_numerator(width), kernel_numerator(width, True))
    child_kernel = kernel_numerator(child)
    unit = ((1, 0), (0, 1), (-1, 0), (0, -1))[phase]
    target = [[(0, 0) for _ in range(size)] for _ in range(size)]
    host = [[(0, 0) for _ in range(size)] for _ in range(size)]
    for x in range(active):
        for y in range(active):
            if x // lane_size == y // lane_size:
                target[x][y] = kernels[int(x // lane_size >= forward)][((x ^ y) % lane_size).bit_count()]
            if x % spectator == y % spectator:
                host[x][y] = gaussian_product(unit, child_kernel[((x // spectator) ^ (y // spectator)).bit_count()])
    for x in range(active, size):
        target[x][x], host[x][x] = (1 << width, 0), (1 << child, 0)
    return target, host


def intertwines(width, child, encoding, target, host):
    size = len(encoding)
    require(size > 0 and all(len(matrix) == size and all(len(row) == size for row in matrix)
                            for matrix in (encoding, target, host)), "square operator dimensions")
    left = complex_left(host, encoding)
    right = complex_right(encoding, target)
    return all(a * (1 << width) == b * (1 << child)
               for row_l, row_r in zip(left, right)
               for pair_l, pair_r in zip(row_l, row_r) for a, b in zip(pair_l, pair_r))


def dense_checks():
    results = []
    first = None
    for width, forward, inverse, padding in ((2, 3, 1, 3), (2, 1, 3, 2), (2, 6, 2, 1), (2, 10, 6, 0)):
        choice, encoding, decoding = fixture(width, forward, inverse, padding)
        child, _, _ = choice
        size = len(encoding)
        target, host = operators(width, forward, inverse, padding, choice)
        expected = [[(1 << (width + child)) * int(x == y) for y in range(size)] for x in range(size)]
        require(integer_product(encoding, decoding) == expected, "right inverse")
        require(integer_product(decoding, encoding) == expected, "left inverse")
        require(intertwines(width, child, encoding, target, host), "full operator identity")
        digest = hashlib.sha256(json.dumps([encoding, decoding], separators=(",", ":")).encode()).hexdigest()
        results.append({"width": width, "forward": forward, "inverse": inverse, "padding": padding,
                        "child": list(choice), "matrix_entries": size * size, "basis_sha256": digest})
        if first is None:
            first = encoding, target, host, choice
    require(first is not None, "missing control fixture")
    return results, first


def controls(first):
    encoding, target, host, choice = first
    child, spectator, phase = choice
    wrong_phase = (child, spectator, (phase + 1) % 4)
    _, bad_host = operators(2, 3, 1, 3, wrong_phase)
    require(not intertwines(2, child, encoding, target, bad_host), "phase control")
    wrong_target, _ = operators(2, 4, 0, 3, choice)
    require(not intertwines(2, child, encoding, wrong_target, host), "direction control")
    broken = [row[:] for row in encoding]
    broken[0][0] += 1
    require(not intertwines(2, child, broken, target, host), "encoder control")
    dirty_target = [row[:] for row in target]
    dirty_target[-1][-1] = (0, 0)
    require(not intertwines(2, child, encoding, dirty_target, host), "dirty restoration control")
    require(classification(2, 1, 1) is None, "balanced control")
    require(classification(2, 4, 2) is None, "nondyadic imbalance control")
    require(classification(2, 3, 1) == (4, 1, 3), "first positive")
    require(classification(2, 9, 7) is None, "spectator integrality control")
    for args in ((True, 3, 1), (2, -1, 2), (2, 0, 0), (4, 3, 1)):
        try:
            classification(*args)
        except ValueError:
            continue
        raise ValueError("invalid domain accepted")
    return ["phase", "direction", "encoder", "dirty restoration", "balanced",
            "nondyadic imbalance", "spectator integrality", "four invalid-domain cases"]


def main():
    sweep = spectral_sweep()
    dense, first = dense_checks()
    rejected = controls(first)
    package = Path(__file__).resolve().parent
    files = sorted(p for p in package.iterdir() if p.is_file())
    receipt = {"status": "PASS_MIXED_CLIFFORD_IMBALANCE", "claim_type": "scoped proof",
               "spectral_sweep": sweep, "dense_fixtures": dense, "controls": rejected,
               "sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in files}}
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

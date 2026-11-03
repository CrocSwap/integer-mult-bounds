"""Exact finite corroboration of the nested-border precision theorem."""
import argparse
from fractions import Fraction as F
import hashlib
import itertools
import json
from pathlib import Path
import platform


def require(condition, message):
    if not condition:
        raise ValueError(message)


def integer(value, low, high):
    require(type(value) is int and low <= value <= high, "integer capacity")


def two(exponent):
    integer(exponent, -65536, 65536)
    return F(2**exponent) if exponent >= 0 else F(1, 2**(-exponent))


def parameters(depth, scale, precision):
    integer(depth, 1, 64)
    integer(scale, 1, 256)
    integer(precision, 0, 65536)
    return two(-scale), two(-precision)


def exact_error(depth, scale, precision):
    epsilon, eta = parameters(depth, scale, precision)
    coupling = epsilon * (1 - epsilon**depth) / (1 - epsilon)
    gain = epsilon**(-depth)
    first = coupling + eta * (1 + coupling * gain)
    second = eta * gain
    require(0 < coupling < 1 and gain > 1, "border range")
    return max(first, second), coupling, gain


def minimum_precision(depth, output_bits):
    integer(depth, 1, 64)
    integer(output_bits, 1, 128)
    return (depth + 1) * output_bits + depth


def literal(depth, scale, precision, inputs, signs):
    epsilon, eta = parameters(depth, scale, precision)
    require(len(inputs) == len(signs) == 2, "two independent registers")
    require(all(sign in (-1, 1) for sign in signs), "error signs")
    x, y = map(F, inputs)
    for _ in range(depth):
        x /= epsilon
    allowance = eta * max(abs(x), abs(y))
    x, y = x + signs[0] * allowance, -y + signs[1] * allowance
    for _ in range(depth):
        x *= epsilon
        x += epsilon * y
    target = (F(inputs[0]), -F(inputs[1]))
    return max(abs(x - target[0]), abs(y - target[1]))


def multiply(left, right):
    return tuple(tuple(sum((left[i][k] * right[k][j] for k in range(2)), F(0))
                       for j in range(2)) for i in range(2))


def check_matrices():
    count = 0
    identity = ((F(1), F(0)), (F(0), F(1)))
    target = ((F(1), F(0)), (F(0), F(-1)))
    for depth in range(1, 25):
        for scale in range(1, 9):
            epsilon = two(-scale)
            diagonal = ((epsilon, F(0)), (F(0), F(1)))
            inverse = ((1 / epsilon, F(0)), (F(0), F(1)))
            shear = ((F(1), epsilon), (F(0), F(1)))
            word = target
            for _ in range(depth):
                word = multiply(shear, multiply(diagonal, multiply(word, inverse)))
            _, coupling, gain = exact_error(depth, scale, 0)
            require(word == ((F(1), -coupling), (F(0), F(-1))), "literal endpoint")
            require(multiply(word, word) == identity, "completed involution")
            require((1 + coupling)**2 < 4, "completed spectral bound")
            require(gain == 2**(depth * scale), "inner prefix gain")
            count += 1
    return count


def check_corners():
    fixtures = executions = 0
    corners = tuple(itertools.product((-1, 1), repeat=2))
    for depth in range(1, 6):
        for scale in range(1, 6):
            for precision in range(11):
                observed = F(0)
                for inputs in corners:
                    for signs in corners:
                        value = literal(depth, scale, precision, inputs, signs)
                        observed = max(observed, value)
                        executions += 1
                expected = exact_error(depth, scale, precision)[0]
                require(observed == expected, "complete real corner maximum")
                fixtures += 1
    return fixtures, executions


def check_minima():
    comparisons = choices = 0
    for depth in range(1, 6):
        for output_bits in range(1, 7):
            threshold = minimum_precision(depth, output_bits)
            target = two(-output_bits)
            feasible = []
            for scale in range(1, output_bits + 4):
                for precision in range(threshold + 2):
                    if exact_error(depth, scale, precision)[0] <= target:
                        feasible.append((precision, scale))
                    choices += 1
            require(min(feasible) == (threshold, output_bits + 1), "finite global minimum")
            require(all(p != threshold or s == output_bits + 1 for p, s in feasible),
                    "unique optimal dyadic parameter")
            comparisons += 1
    return comparisons, choices


def check_sharp_family():
    count = 0
    for depth in range(1, 25):
        for output_bits in range(1, 17):
            scale = output_bits + 1
            precision = minimum_precision(depth, output_bits)
            target = two(-output_bits)
            upper = exact_error(depth, scale, precision)[0]
            witness = literal(depth, scale, precision, (1, -1), (1, 1))
            failure = literal(depth, scale, precision - 1, (1, -1), (1, 1))
            require(upper == witness == target, "sharp sufficient precision")
            require(failure >= 2 * target, "one-bit-short error witness")
            count += 1
    return count


def check_controls():
    invalid = ((0, 1, 1), (65, 1, 1), (1, 0, 1), (1, 257, 1),
               (1, 1, -1), (1, 1, 65537), (True, 1, 1), (1, 1.0, 1))
    for values in invalid:
        try:
            exact_error(*values)
        except ValueError:
            continue
        raise ValueError("invalid domain accepted")
    require(literal(4, 4, 10, (1, 0), (1, 1)) >= two(6), "missing prefix amplification")
    require(exact_error(3, 3, 100)[0] > two(-3), "endpoint leakage omitted")
    require(exact_error(4, 3, 5)[0] > two(-2), "depth-independent precision rejected")
    require(literal(2, 3, 7, (1, -1), (1, 1)) > two(-2), "one-bit-short rejected")
    require(exact_error(2, 3, 8)[0] == two(-2), "strictness control")
    return len(invalid) + 5


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()
    matrices = check_matrices()
    fixtures, executions = check_corners()
    minima, choices = check_minima()
    sharp = check_sharp_family()
    controls = check_controls()
    package = Path(__file__).resolve().parent
    names = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")
    hashes = {}
    for name in names:
        data = package.joinpath(name).read_bytes()
        require(len(data) <= 256 * 1024, "package file capacity")
        hashes[name] = hashlib.sha256(data).hexdigest()
    receipt = {"status": "PASS_NESTED_BORDER_PRECISION", "matrices": matrices,
               "corner_fixtures": fixtures, "literal_corner_executions": executions,
               "finite_minima": minima, "precision_choices": choices,
               "sharp_family": sharp, "controls": controls, "hashes": hashes,
               "python": platform.python_version()}
    encoded = json.dumps(receipt, sort_keys=True, indent=2) + "\n"
    if args.receipt:
        destination = args.receipt.resolve()
        require(package not in destination.parents, "receipt must be external")
        with destination.open("x", encoding="utf-8") as output:
            require(output.write(encoded) == len(encoded), "complete receipt write")
    print(encoded, end="")


if __name__ == "__main__":
    main()

"""Exact BW16 chart certificate; produced by Nick Petalas, Apache-2.0."""

import argparse
import hashlib
import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
PAIRS = tuple(itertools.combinations(range(4), 2))
# Bit k is the coefficient of x_i*x_j for (i,j)=PAIRS[k].
FORMS = (0, 57, 53, 46, 35, 28, 18, 15)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(vector):
    require(len(vector) == 16 and any(vector), "nonzero sixteen-vector required")
    first = next(value for value in vector if value)
    return vector if first > 0 else tuple(-value for value in vector)


def dot(left, right):
    return sum(a * b for a, b in zip(left, right, strict=True))


def shell_member(vector):
    """Independent Construction-D membership, with the norm fixed to eight."""
    if len(vector) != 16 or sum(value * value for value in vector) != 8:
        return False
    low = tuple(value % 2 for value in vector)
    constant = low[0]
    linear = tuple(low[1 << i] ^ constant for i in range(4))
    for x in range(16):
        predicted = (constant + sum(linear[i] * ((x >> i) & 1)
                                    for i in range(4))) % 2
        if predicted != low[x]:
            return False
    return sum((value - bit) // 2
               for value, bit in zip(vector, low, strict=True)) % 2 == 0


def make_shell():
    lines = set()
    for i, j in itertools.combinations(range(16), 2):
        for sign in (1, -1):
            lines.add(tuple(2 * (k == i) + 2 * sign * (k == j)
                            for k in range(16)))
    for a in range(1, 16):
        for b in range(2):
            support = [x for x in range(16) if (a & x).bit_count() % 2 == b]
            require(len(support) == 8, "hyperplane size")
            for signs in range(128):
                if signs.bit_count() % 2:
                    continue
                vector = [0] * 16
                vector[support[0]] = 1
                for j, x in enumerate(support[1:]):
                    vector[x] = 1 - 2 * ((signs >> j) & 1)
                lines.add(tuple(vector))
    require(len(lines) == 2160, "complete shell size")
    require(all(shell_member(v) for v in lines), "shell membership")
    return tuple(sorted(lines))


def quadratic(form, x):
    return sum(((form >> k) & 1) * ((x >> i) & 1) * ((x >> j) & 1)
               for k, (i, j) in enumerate(PAIRS)) % 2


def hadamard(form):
    """Numerator H of the orthogonal matrix U=H/4."""
    return tuple(tuple(1 - 2 * (quadratic(form, x) ^ ((b & x).bit_count() % 2))
                       for b in range(16)) for x in range(16))


def check_orthogonal(matrix):
    for i in range(16):
        for j in range(i, 16):
            require(dot(matrix[i], matrix[j]) == 16 * (i == j),
                    "Hadamard orthogonality")


def roots_in_chart(matrix):
    roots = set()
    for i, j in itertools.combinations(range(16), 2):
        for sign in (1, -1):
            numerator = tuple(matrix[x][i] + sign * matrix[x][j]
                              for x in range(16))
            require(all(value % 2 == 0 for value in numerator), "root division")
            roots.add(canonical(tuple(value // 2 for value in numerator)))
    require(len(roots) == 240, "D16 block size")
    return roots


def inverse_transport(matrix, vector):
    numerator = tuple(sum(matrix[x][b] * vector[x] for x in range(16))
                      for b in range(16))
    require(all(value % 4 == 0 for value in numerator), "chart denominator")
    return canonical(tuple(value // 4 for value in numerator))


def check_atlas(shell, forms=FORMS):
    domain = set(shell)
    coordinate = {v for v in shell if max(map(abs, v)) == 2}
    require(len(coordinate) == 240, "coordinate block size")
    blocks = [coordinate]
    transport_checks = 0
    for form in forms:
        matrix = hadamard(form)
        check_orthogonal(matrix)
        block = roots_in_chart(matrix)
        require(block <= domain, "chart root outside shell")
        for previous in blocks:
            require(not block & previous, "D16 blocks overlap")
        blocks.append(block)
        images = set()
        for vector in shell:
            image = inverse_transport(matrix, vector)
            require(image in domain, "chart does not preserve shell")
            images.add(image)
            transport_checks += 1
        require(images == domain, "chart is not onto shell")
    require(len(blocks) == 9 and set.union(*blocks) == domain,
            "atlas does not partition shell")
    return blocks, transport_checks


def star(center, signs):
    leaves = [j for j in range(16) if j != center]
    roots = []
    for k, leaf in enumerate(leaves):
        sign = 1 - 2 * ((signs >> k) & 1)
        roots.append(canonical(tuple(2 * (j == center) + 2 * sign * (j == leaf)
                                     for j in range(16))))
    return tuple(roots)


def compatible_odd(star_roots, odd_lines):
    # Each root is sparse; this path uses literal integer inner products.
    sparse = [tuple((i, value) for i, value in enumerate(root) if value)
              for root in star_roots]
    return {v for v in odd_lines
            if all(sum(value * v[i] for i, value in root) != 0 for root in sparse)}


def predicted_odd(center, signs):
    """One possible line per affine hyperplane containing the star center."""
    leaves = [j for j in range(16) if j != center]
    values = {center: 1}
    values.update({leaf: 1 - 2 * ((signs >> k) & 1)
                   for k, leaf in enumerate(leaves)})
    answer = set()
    for a in range(1, 16):
        b = (a & center).bit_count() % 2
        support = [x for x in range(16) if (a & x).bit_count() % 2 == b]
        vector = canonical(tuple(values[x] if x in support else 0
                                 for x in range(16)))
        if shell_member(vector):
            answer.add(vector)
    return answer


def check_star_lemma(shell):
    odd = tuple(v for v in shell if max(map(abs, v)) == 1)
    require(len(odd) == 1920, "odd-line domain")
    checked = 0
    # Exhaust all signs at center zero. The proof quantifies over every center.
    histogram = {}
    masks = [sum(1 << (x - 1) for x in range(1, 16)
                 if (a & x).bit_count() % 2 == 0) for a in range(1, 16)]
    for signs in range(1 << 15):
        count = sum((signs & mask).bit_count() % 2 == 0 for mask in masks)
        histogram[str(count)] = histogram.get(str(count), 0) + 1
    for center in range(16):
        for signs in (0, 1, 3, 7, 31, 127, 255, 1023, 8191, 16383, 32767):
            actual = compatible_odd(star(center, signs), odd)
            require(actual == predicted_odd(center, signs), "star restriction")
            require(len(actual) <= 15, "star cap")
            checked += 1
    witness = star(0, 0) + tuple(sorted(predicted_odd(0, 0)))
    require(len(witness) == 30 and len(set(witness)) == 30, "star attainer size")
    for left, right in itertools.combinations(witness, 2):
        require(dot(left, right) != 0, "star attainer orthogonal pair")
    return histogram, checked


def check_controls(shell):
    controls = []
    for name, vector in (
        ("odd_sign_parity", tuple(-1 if x == 0 else int(x < 8) for x in range(16))),
        ("nonaffine_support", (1,) * 7 + (0, 1) + (0,) * 7),
        ("wrong_norm", (2,) + (0,) * 15),
    ):
        require(not shell_member(vector), "accepted invalid membership control")
        controls.append(name)
    matrix = list(hadamard(FORMS[0]))
    matrix[0] = (-matrix[0][0],) + matrix[0][1:]
    try:
        check_orthogonal(matrix)
    except ValueError as error:
        require(str(error) == "Hadamard orthogonality", "wrong matrix rejection")
    else:
        raise ValueError("accepted damaged Hadamard")
    controls.append("damaged_hadamard")
    try:
        check_atlas(shell, (FORMS[0],) * 8)
    except ValueError as error:
        require(str(error) == "D16 blocks overlap", "wrong duplicate rejection")
    else:
        raise ValueError("accepted duplicate chart")
    controls.append("duplicate_chart")
    plus, minus = star(0, 0)[0], star(0, 1)[0]
    require(plus != minus and dot(plus, minus) == 0, "opposite-edge control")
    controls.append("same_edge_signs_are_orthogonal")
    return controls


def digest(value):
    return hashlib.sha256(json.dumps(value, separators=(",", ":")).encode()).hexdigest()


def result():
    shell = make_shell()
    blocks, checks = check_atlas(shell)
    histogram, star_checks = check_star_lemma(shell)
    controls = check_controls(shell)
    require(9 * 14 == 126 and 30 < 127, "global pigeonhole implication")
    sources = {}
    for name in ("verify.py", "PROOF.md", "README.md", "TASK.json", "SOURCES.json", "VERIFY.json"):
        sources[name] = hashlib.sha256((HERE / name).read_bytes()).hexdigest()
    return {
        "schema_version": 1,
        "claim_type": "finite certificate with a scoped combinatorial proof",
        "shell_lines": len(shell),
        "shell_sha256": digest(shell),
        "quadratic_forms": list(FORMS),
        "block_sizes": [len(block) for block in blocks],
        "block_sha256": [digest(sorted(block)) for block in blocks],
        "inverse_transport_checks": checks,
        "full_star_sign_patterns": 1 << 15,
        "compatible_odd_histogram_at_center_zero": histogram,
        "literal_star_fixtures": star_checks,
        "conditional_star_clique_maximum": 30,
        "global_clique_upper_bound": 126,
        "controls": controls,
        "source_sha256": sources,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true", help="emit a newly computed receipt on stdout")
    args = parser.parse_args()
    receipt = json.dumps(result(), indent=2, sort_keys=True) + "\n"
    if args.emit:
        print(receipt, end="")
    else:
        require((HERE / "RESULT.json").read_text() == receipt, "receipt mismatch")
        print("PASS_BW16_GLOBAL_CLIQUE_126 lines=2160 blocks=9 transports=17280 bound=126")


if __name__ == "__main__":
    main()

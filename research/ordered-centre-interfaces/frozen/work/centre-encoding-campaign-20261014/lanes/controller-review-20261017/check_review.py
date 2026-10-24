"""Check the ordered controller maps by reverse output propagation."""

from collections import Counter
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
LANES = HERE.parent
ONE = {(): 1}


def require(test, label):
    if not test:
        raise ValueError(label)


def add(*terms):
    result = Counter()
    for term in terms:
        result.update(term)
    return {word: value for word, value in result.items() if value}


def neg(value):
    return {word: -coefficient for word, coefficient in value.items()}


def symbol(name):
    return {(name,): 1}


def reduce_word(word):
    stack = []
    for letter in word:
        previous = stack[-1] if stack else ""
        cancel = (previous, letter) in (("Q", "q"), ("q", "Q"))
        if previous[:1] in ("H", "K") and letter[:1] in ("H", "K"):
            cancel |= previous[0] != letter[0] and previous[1:] == letter[1:]
        if cancel:
            stack.pop()
        else:
            stack.append(letter)
    return tuple(stack)


def multiply(left, right):
    result = Counter()
    for a, x in left.items():
        for b, y in right.items():
            result[reduce_word(a + b)] += x * y
    return {word: value for word, value in result.items() if value}


def apply(names, value):
    return multiply({tuple(names.split()): 1}, value)


def input_value(index):
    return symbol(f"@{index}")


class Tape:
    def __init__(self, size):
        self.size = size
        self.events = []
        self.cuts = []

    def plus(self, target, source, names="", sign=1):
        self.events.append(("add", target, source, {tuple(names.split()): sign}))

    def scale(self, target, name):
        self.events.append(("scale", target, symbol(name)))

    def swap(self, left, right):
        self.events.append(("swap", left, right))

    def exchange(self, selected_x, selected_y):
        self.swap(selected_x, selected_y)
        self.scale(selected_x, "q")
        self.scale(selected_y, "Q")

    def rows(self, outputs=None, stop=None):
        outputs = range(self.size) if outputs is None else outputs
        result = []
        for output in outputs:
            covector = [{} for _ in range(self.size)]
            covector[output] = ONE
            for event in reversed(self.events[:stop]):
                kind, target = event[:2]
                if kind == "add":
                    _, _, source, operator = event
                    covector[source] = add(covector[source], multiply(covector[target], operator))
                elif kind == "scale":
                    covector[target] = multiply(covector[target], event[2])
                else:
                    source = event[2]
                    covector[target], covector[source] = covector[source], covector[target]
            expression = {}
            for source, coefficient in enumerate(covector):
                expression = add(expression, multiply(coefficient, input_value(source)))
            result.append(expression)
        return result


def make_tape(m, family, option, mutation=None):
    tape = Tape(4 * m)
    for i in range(m - 2, -1, -1):
        tape.plus(4*i + 1, 4*i + 5, sign=-1)
    if mutation != "omit_initial_selected":
        tape.plus(2, 0)
    if mutation != "omit_initial_ordinary":
        tape.plus(3, 1)
    for i in range(m):
        a, u, b, v = range(4*i, 4*i + 4)
        s, t = 2*i + 1, 2*i + 2
        tape.exchange(a, b)
        if family == "raw":
            tape.plus(a, v, f"B{s}")
            tape.plus(u, b, f"D{s}")
            tape.plus(u, v, sign=-1)
            tape.plus(u, v, f"D{s} B{s}")
            tape.plus(u, a, f"D{s}", -1)
        else:
            tape.plus(a, b, f"R{s}", -1)
            tape.plus(a, v, f"L{s}", -1)
            tape.plus(u, b, f"C{s}", -1)
            tape.plus(u, v, f"H{s}", -1)
            tape.scale(u, f"K{s}")
            if option:
                tape.plus(a, u, f"L{s}", -1)
        if i + 1 < m:
            if family == "weighted":
                tape.scale(u + 4, f"K{s}")
            tape.plus(u, u + 4)
            tape.plus(v + 4, v, sign=-1)
        tape.cuts.append((len(tape.events), (u, v)))
        if family == "raw" and option:
            tape.plus(v, b, f"D{t} q")
        if family == "weighted":
            tape.scale(v, f"H{t}")
        tape.exchange(a, b)
        if family == "raw":
            if mutation != "omit_selected_query":
                tape.plus(b, u, f"B{t}", -1)
            tape.plus(v, a, f"D{t}", -1)
            tape.plus(v, u)
            tape.plus(v, u, f"D{t} B{t}", -1)
        else:
            if mutation != "omit_selected_self":
                tape.plus(b, a, f"R{t}")
            tape.plus(b, u, f"L{t}")
            tape.plus(v, a, f"C{t}")
            tape.plus(v, u, f"H{t}")
        tape.exchange(a, b)
        if i + 1 < m:
            if family == "weighted" and mutation == "early_idle_reset":
                tape.scale(u + 4, f"H{s}")
            tape.plus(u, u + 4, sign=-1)
            tape.plus(v + 4, v, sign=-1 if mutation == "wrong_plus_y" else 1)
            if family == "weighted" and mutation != "early_idle_reset":
                tape.scale(u + 4, f"H{s}")
    order = range(1, m) if mutation == "ascending_tail" else range(m - 1, 0, -1)
    for i in order:
        tape.plus(4*i + 1, 4*i - 3)
    return tape


def endpoint_formula(m, family, option):
    initial = [input_value(j) for j in range(4*m)]
    suffix = [{} for _ in range(m + 1)]
    for i in range(m - 1, -1, -1):
        suffix[i] = add(initial[4*i + 1], neg(suffix[i + 1]))
    incoming = add(initial[3], suffix[0])
    endpoint, cuts, before_tail = [], [], []
    previous_response, previous_correction, previous_retirement = {}, {}, {}
    for i in range(m):
        a, x, b, y = initial[4*i:4*i + 4]
        if i == 0:
            b = add(b, a)
        s, t = 2*i + 1, 2*i + 2
        if family == "raw":
            correction = add(apply("Q", a), neg(apply("q", b)))
            w = add(suffix[i], neg(incoming), apply(f"D{s}", correction))
            k = add(w, suffix[i + 1])
            selected = add(apply(f"B{s}", incoming), apply("q", b), neg(apply(f"q B{t}", k)))
            response = apply(f"B{t}", k)
            if not option:
                response = add(response, a)
            retired = add(incoming, k, neg(apply(f"D{t}", response)))
            ordinary = add(neg(y), apply(f"D{s}", correction))
            if i:
                ordinary = add(ordinary, apply(f"D{s-1}", previous_response))
            previous_response = response
        else:
            correction = neg(apply(f"K{s} C{s} Q", a))
            w = add(apply(f"K{s}", suffix[i]), neg(incoming), correction)
            k = add(w, apply(f"K{s}", suffix[i + 1]))
            retired = add(apply(f"H{t} K{s}", x), apply(f"H{t}", correction), apply(f"C{t}", a))
            selected = add(apply("q", b), neg(apply(f"R{s} Q", a)), apply(f"q R{t}", a), apply(f"q L{t}", k))
            if option:
                selected = add(selected, neg(apply(f"L{s} K{s}", suffix[i])), neg(apply(f"L{s}", correction)))
            else:
                selected = add(selected, neg(apply(f"L{s}", incoming)))
            ordinary = add(neg(y), apply(f"K{s}", suffix[i]), correction)
            if i:
                ordinary = add(ordinary, apply(f"K{s-2}", suffix[i - 1]), neg(previous_retirement), previous_correction)
            else:
                ordinary = add(ordinary, neg(suffix[0]))
            previous_correction = correction
        endpoint.extend((selected, ordinary, apply("Q", a), retired))
        cuts.extend((k, incoming))
        before_tail.append(w)
        previous_retirement = retired
        if i + 1 < m:
            incoming = add(initial[4*i + 7], neg(incoming), retired)
    return endpoint, cuts, before_tail, suffix


def restrict_to_y(value):
    return {word: c for word, c in value.items() if int(word[-1][1:]) % 4 >= 2}


def normal_forms(m, family, option, endpoint, suffix):
    w = [endpoint[4*i + 1] for i in range(m)]
    for i in range(1, m):
        w[i] = add(w[i], neg(w[i - 1]))
    if family == "raw":
        w = list(map(restrict_to_y, w))
        h = [add(restrict_to_y(endpoint[4*i]), apply(f"q B{2*i+2}", w[i])) for i in range(m)]
        for i in range(m):
            s = 2*i + 1
            correction = add(w[i-1], neg(apply(f"D{s-1} B{s-1}", w[i-1]))) if i else {}
            left = add(h[i], neg(apply(f"B{s}", correction)))
            lower = add(w[i], correction)
            require(left == add(apply("q", input_value(4*i+2)), apply(f"B{s}", input_value(4*i+3))), "Raw selected diagonal block")
            require(lower == add(neg(apply(f"D{s} q", input_value(4*i+2))), neg(input_value(4*i+3))), "Raw ordinary diagonal block")
    elif option:
        for i in range(m):
            s, t = 2*i + 1, 2*i + 2
            a, b = input_value(4*i), input_value(4*i + 2)
            if not i:
                b = add(b, a)
            actual = add(apply("Q", endpoint[4*i]), neg(apply(f"L{t}", w[i])))
            expected = add(b, neg(apply(f"Q L{s} K{s}", suffix[i])), neg(apply(f"Q R{s} Q", a)), apply(f"Q L{s} K{s} C{s} Q", a), apply(f"R{t}", a), apply(f"L{t} K{s}", suffix[i + 1]))
            require(actual == expected, "Weighted selected normalization")
            require(restrict_to_y(actual) == input_value(4*i + 2), "Weighted selected borrowed unit")
        restricted = list(map(restrict_to_y, w))
        for i, value in enumerate(restricted):
            lower = add(value, restricted[i-1]) if i else value
            require(lower == neg(input_value(4*i + 3)), "Weighted ordinary borrowed unit")


def matrix_multiply(a, b):
    return [[sum(x*y for x, y in zip(row, col)) for col in zip(*b)] for row in a]


def eye(n):
    return [[int(i == j) for j in range(n)] for i in range(n)]


def inverse(a):
    n = len(a)
    rows = [[Fraction(x) for x in row] + [Fraction(i == j) for j in range(n)] for i, row in enumerate(a)]
    for c in range(n):
        p = next(i for i in range(c, n) if rows[i][c])
        rows[c], rows[p] = rows[p], rows[c]
        divisor = rows[c][c]
        rows[c] = [x/divisor for x in rows[c]]
        for i in range(n):
            if i != c:
                coefficient = rows[i][c]
                rows[i] = [x-coefficient*y for x, y in zip(rows[i], rows[c])]
    return [row[n:] for row in rows]


def bareiss(a):
    a = [row[:] for row in a]
    previous, sign = 1, 1
    for c in range(len(a)-1):
        if not a[c][c]:
            p = next((i for i in range(c+1, len(a)) if a[i][c]), None)
            if p is None:
                return 0
            a[c], a[p] = a[p], a[c]
            sign *= -1
        pivot = a[c][c]
        for i in range(c+1, len(a)):
            for j in range(c+1, len(a)):
                numerator = a[i][j]*pivot-a[i][c]*a[c][j]
                require(numerator % previous == 0, "Exact determinant division")
                a[i][j] = numerator//previous
            a[i][c] = 0
        previous = pivot
    return sign*a[-1][-1]


def rank_mod(a, prime):
    rows = [[x % prime for x in row] for row in a]
    pivot = 0
    for c in range(len(rows[0])):
        p = next((i for i in range(pivot, len(rows)) if rows[i][c]), None)
        if p is None:
            continue
        rows[pivot], rows[p] = rows[p], rows[pivot]
        scale = pow(rows[pivot][c], -1, prime)
        rows[pivot] = [x*scale % prime for x in rows[pivot]]
        for i in range(pivot+1, len(rows)):
            scale = rows[i][c]
            rows[i] = [(x-scale*y) % prime for x, y in zip(rows[i], rows[pivot])]
        pivot += 1
    return pivot


def numeric_raw_checks():
    results = []
    for seed in (1, 2, 3):
        qmat = [[1, seed], [1, seed+1]]
        operators = {"Q": qmat, "q": inverse(qmat)}
        for stage in range(1, 9):
            p = eye(3)
            for step in range(5):
                target, source = (stage+step) % 3, (stage+step+1) % 3
                p[target] = [x+(seed+step+1)*y for x, y in zip(p[target], p[source])]
            operators[f"D{stage}"] = [row[:2] for row in p]
            operators[f"B{stage}"] = [[13*x for x in row] for row in inverse(p)[:2]]
            require(matrix_multiply(operators[f"B{stage}"], operators[f"D{stage}"]) == [[13, 0], [0, 13]], "Rectangular BD relation")
        cross = matrix_multiply(operators["B1"], operators["D2"])
        require(matrix_multiply(qmat, cross) != matrix_multiply(cross, qmat), "Noncommuting selected operators")
        for corrected in (False, True):
            for m in (1, 2, 4):
                expressions = make_tape(m, "raw", corrected).rows()
                dimensions = [2, 3, 2, 3]*m
                outputs = [j for j in range(4*m) if j % 4 < 2]
                inputs = [j for j in range(4*m) if j % 4 >= 2]
                offsets, offset = {}, 0
                for j in inputs:
                    offsets[j], offset = offset, offset + dimensions[j]
                matrix = []
                for output in outputs:
                    block = [[0]*offset for _ in range(dimensions[output])]
                    for word, coefficient in expressions[output].items():
                        source = int(word[-1][1:])
                        if source not in offsets:
                            continue
                        value = eye(dimensions[source])
                        for name in reversed(word[:-1]):
                            value = matrix_multiply(operators[name], value)
                        for i, row in enumerate(value):
                            for j, x in enumerate(row):
                                block[i][offsets[source]+j] += coefficient*x
                    require(all(Fraction(x).denominator == 1 for row in block for x in row), "Integer specialization")
                    matrix.extend([[int(x) for x in row] for row in block])
                determinant = bareiss(matrix)
                nullity = len(matrix)-rank_mod(matrix, 3)
                require(abs(determinant) == 12**(2*m), "Exact determinant factor")
                require(nullity == 2*m, "Exact characteristic-three nullity")
                results.append({"seed": seed, "pairs": m, "corrected": corrected, "determinant": str(determinant), "nullity_mod_3": nullity})
    require(bareiss([[3, 0], [0, 3]]) == bareiss([[3, 1], [0, 3]]) == 9, "Equal determinant witness")
    require(rank_mod([[3, 0], [0, 3]], 3) == 0 and rank_mod([[3, 1], [0, 3]], 3) == 1, "Different nullity witness")
    return results


def main():
    inputs = json.loads((HERE/"INPUTS.json").read_text())
    for name, digest in inputs.items():
        require(sha256((LANES/name).read_bytes()).hexdigest() == digest, f"Frozen source: {name}")
    for name in list(inputs)[:6]:
        require((HERE/"reviewed-inputs"/Path(name).name).read_bytes() == (LANES/name).read_bytes(), "Retained source snapshot")
    cases, controls = [], []
    for family in ("raw", "weighted"):
        for option in (False, True):
            for m in range(1, 9):
                tape = make_tape(m, family, option)
                actual = tape.rows()
                expected, cut_expected, _, suffix = endpoint_formula(m, family, option)
                require(actual == expected, "Complete ordered endpoint")
                cuts = []
                for stop, outputs in tape.cuts:
                    cuts.extend(tape.rows(outputs, stop))
                require(cuts == cut_expected, "Active cut rows")
                normal_forms(m, family, option, actual, suffix)
                cases.append({"family": family, "option": option, "pairs": m, "operator_blocks": (4*m)**2, "cut_blocks": 8*m*m, "events": len(tape.events)})
            for mutation in ("omit_initial_selected", "omit_initial_ordinary", "ascending_tail", "wrong_plus_y", "omit_selected_query" if family == "raw" else "omit_selected_self"):
                require(make_tape(4, family, option, mutation).rows() != endpoint_formula(4, family, option)[0], mutation)
                controls.append([family, option, mutation])
            if family == "weighted":
                require(make_tape(4, family, option, "early_idle_reset").rows() != endpoint_formula(4, family, option)[0], "early_idle_reset")
                controls.append([family, option, "early_idle_reset"])
    result = {
        "status": "PASS_INDEPENDENT_RAW_AND_WEIGHTED_CONTROLLERS",
        "checker_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
        "source_sha256": inputs,
        "input_manifest_sha256": sha256((HERE/"INPUTS.json").read_bytes()).hexdigest(),
        "method": "Reverse output propagation through independently assembled swaps, clean-core block shears, local factors, and controller events. No producer imports or execution.",
        "formal_relations": ["Q q = q Q = I", "H_j K_j = K_j H_j = I"],
        "cases": cases,
        "operator_blocks_checked": sum(case["operator_blocks"] for case in cases),
        "cut_blocks_checked": sum(case["cut_blocks"] for case in cases),
        "controls": controls,
        "exact_integer_specializations": numeric_raw_checks(),
        "all_m_proof": "REVIEW.md gives the induction and the block-diagonal reduction for every positive m.",
        "scope": "Ordered content algebra. Local native reviews are dependencies. No new local native replay, inter-call access, idle owner schedule, finite-grid implementation, or complete kappa claim.",
    }
    (HERE/"REVIEW.json").write_text(json.dumps(result, indent=2) + "\n")
    print(result["status"])
    print(f"formal cases={len(cases)} blocks={result['operator_blocks_checked']} controls={len(controls)}")


if __name__ == "__main__":
    main()

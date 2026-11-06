"""Exact finite corroboration of approximate channels. Apache-2.0."""

from fractions import Fraction as Q
from hashlib import sha256
from itertools import product
from pathlib import Path
import json
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from channels import (channel_word, coefficient_word, execute, identity,
                      multiply, need, normalize, round_dyadic)


def expected_state(cut, rounded, state):
    r, n = len(cut), len(cut[0])
    response = multiply(cut, rounded)
    answer = list(map(Q, state))
    for i in range(r):
        answer[r + n + i] += sum(response[i][j] * state[j] for j in range(r))
    return answer


def check_module(cut, epsilon):
    result = normalize(cut, epsilon)
    word = channel_word(result["cut"], result["rounded"])
    r, n = len(cut), len(cut[0])
    size = 2 * r + n
    states = identity(size)
    states += [[Q((-1) ** i * (i + 1), 4) for i in range(size)],
               [Q(2 * i - 3) for i in range(size)]]
    for state in states:
        need(execute(word, state) == expected_state(cut, result["rounded"], state),
             "complete literal endpoint")
    for dirt in (-(10 ** 60), -7, 0, 11, 10 ** 60):
        state = [Q((-1) ** i, 2) for i in range(r)]
        state += [Q(dirt + i) for i in range(n)] + [Q(9)] * r
        output = execute(word, state)
        need(output == expected_state(cut, result["rounded"], state), "dirty endpoint")
        errors = [abs(output[r + n + i] - state[r + n + i] - state[i])
                  for i in range(r)]
        need(max(errors) <= epsilon / 2, "source-only absolute error")
    return len(states), len(word)


def check_matrices():
    full_rank = singular = columns = steps = 0
    for entries in product(range(-2, 3), repeat=4):
        a, b, c, d = entries
        cut = [[Q(a), Q(b)], [Q(c), Q(d)]]
        if a * d == b * c:
            try:
                normalize(cut, Q(1, 8))
            except ValueError as error:
                need(str(error) == "cut lacks full rational row rank", "rank rejection")
                singular += 1
            else:
                raise ValueError("singular cut accepted")
        else:
            count, length = check_module(cut, Q(1, 8))
            full_rank += 1
            columns += count
            steps += length
    fixtures = [[[3]], [[3, 6]], [[3, 0], [0, 3]],
                [[Q(3, 8), Q(1, 2), 0], [0, Q(5, 4), 1]],
                [[3, 0, 1, 0], [0, 5, 0, 1], [0, 0, 7, 0]],
                [[3 if i == j else 0 for j in range(4)] for i in range(4)]]
    for cut in fixtures:
        count, length = check_module(cut, Q(1, 1 << 16))
        columns += count
        steps += length
    return {"full_rank_2x2": full_rank, "singular_2x2_rejects": singular,
            "additional_cuts": len(fixtures), "basis_and_dirty_vectors": columns,
            "sum_word_lengths": steps, "large_dirt_cases": 5 * (full_rank + len(fixtures))}


def check_scalar_precision():
    cases = candidates = 0
    for q in range(3, 32, 2):
        for bits in range(13):
            scale = 1 << bits
            actual = min(abs(q * a - scale) for a in range(scale + 1))
            residue = scale % q
            need(actual == min(residue, q - residue), "sharp odd scalar residual")
            rounded = round_dyadic(Q(1, q), bits)
            need(abs(q * rounded - 1) == Q(actual, scale), "nearest scalar coefficient")
            candidates += scale + 1
            cases += 1
    for bits in range(65):
        coefficient = round_dyadic(Q(1, 3), bits)
        need(abs(3 * coefficient - 1) == Q(1, 1 << bits), "sharp factor-three law")
    return {"odd_scalar_cases": cases, "integer_candidates": candidates,
            "factor_three_depths": 65}


def check_lowering():
    coefficients = states = 0
    for numerator in range(-15, 16):
        for bits in range(7):
            coefficient = Q(numerator, 1 << bits)
            word = coefficient_word(0, 1, coefficient)
            for z, u in product(range(-2, 3), repeat=2):
                initial = [Q(z, 4), Q(u, 4)]
                need(execute(word, initial) == [initial[0] + coefficient * initial[1],
                                               initial[1]], "unit gate lowering")
                states += 1
            coefficients += 1
    return {"coefficient_presentations": coefficients, "literal_two_role_states": states}


def check_controls():
    bad = [([[Q(1, 3)]], Q(1, 8), "dyadic cut coefficient"),
           ([[True]], Q(1, 8), "exact cut coefficient"),
           ([[1.0]], Q(1, 8), "exact cut coefficient"),
           ([[1], [2]], Q(1, 8), "cut column limit"),
           ([[1, 0], [0]], Q(1, 8), "rectangular cut"),
           ([[8192]], Q(1, 8), "cut coefficient limit"),
           ([[3]], Q(0), "error tolerance limit"),
           ([[3]], Q(3, 4), "error tolerance limit"),
           ([[3]], 0.125, "exact error tolerance")]
    for cut, error_bound, message in bad:
        try:
            normalize(cut, error_bound)
        except ValueError as error:
            need(str(error) == message, "exact boundary rejection")
        else:
            raise ValueError("invalid boundary accepted")
    cut, rounded = [[Q(3)]], [[Q(5, 16)]]
    word = channel_word(cut, rounded)
    state = [Q(2), Q(7), Q(-3)]
    expected = expected_state(cut, rounded, state)
    need(execute(word[:-1], state) != expected, "missing inverse discriminator")
    need(execute(list(reversed(word)), state) != expected, "order discriminator")
    wrong = channel_word(cut, [[Q(1)]])
    need(execute(wrong, state) != expected, "wrong normalizer discriminator")
    need(abs(3 * Q(1, 4) - 1) > Q(1, 16), "false precision discriminator")
    need(execute(word, state)[1] == state[1], "restoration positive control")
    return {"exact_reason_rejections": len(bad), "semantic_controls": 4}


def main():
    result = {}
    result.update(check_matrices())
    result.update(check_scalar_precision())
    result.update(check_lowering())
    result.update(check_controls())
    here = Path(__file__).resolve().parent
    result["file_sha256"] = {p.name: sha256(p.read_bytes()).hexdigest()
                             for p in sorted(here.iterdir()) if p.is_file()}
    result["python"] = sys.version.split()[0]
    print(json.dumps(result, sort_keys=True))
    print("PASS_APPROXIMATE_DYADIC_DIRTY_CHANNELS")


if __name__ == "__main__":
    main()

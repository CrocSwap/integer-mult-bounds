#!/usr/bin/env python3
"""Code-disjoint forward impulse controls. Adam Gall + Codex; Apache-2.0."""
from fractions import Fraction as Q
import importlib.util
from itertools import product
import json
from pathlib import Path
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("endpoint_audit", HERE / "verify.py")
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)


def forward_impulses(word, dimension):
    # Every newly created variable is a distinct leaf defect, not a factor.
    rows = [{} for _ in range(dimension)]
    for index, (source, target, factor, sign) in enumerate(word):
        for (monomial, error), coefficient in rows[source].items():
            key = ((factor,) + monomial, error)
            value = rows[target].get(key, 0) + sign*coefficient
            if value:
                rows[target][key] = value
            else:
                rows[target].pop(key, None)
        rows[target][((), index)] = 1
    return [tuple({monomial: coefficient for (monomial, error), coefficient in row.items() if error == index}
                  for row in rows) for index in range(len(word))]


def mm(a, b):
    return tuple(tuple(sum(a[i][k]*b[k][j] for k in range(2)) for j in range(2)) for i in range(2))


def mv(a, x):
    return tuple(sum(a[i][j]*x[j] for j in range(2)) for i in range(2))


def evaluate(polynomial, matrices, backwards=False):
    out = [[Q(0), Q(0)] for _ in range(2)]
    for monomial, coefficient in polynomial.items():
        term = ((Q(1), Q(0)), (Q(0), Q(1)))
        for j in (reversed(monomial) if backwards else monomial):
            term = mm(term, matrices[j])
        for i in range(2):
            for j in range(2):
                out[i][j] += coefficient*term[i][j]
    return tuple(map(tuple, out))


class EndpointControls(unittest.TestCase):
    def test_independent_forward_error_symbols(self):
        checked = 0
        for n in range(1, 9):
            for sign in (1, -1):
                word = v.source_events(n, sign)
                dimension = (n-1).bit_length()+2
                forward = forward_impulses(word, dimension)
                backward, _ = v.formal_responses(word, dimension)
                self.assertEqual(forward, backward)
                checked += len(word)
        print("FORWARD_FREE_IMPULSES", checked)

    def test_noncommuting_matrix_order(self):
        matrices = (((Q(0), Q(1)), (Q(1), Q(0))),
                    ((Q(1), Q(0)), (Q(0), Q(-1))),
                    ((Q(1), Q(0)), (Q(0), Q(0))),
                    ((Q(1, 2), Q(1, 2)), (Q(0), Q(1))))
        self.assertTrue(all(max(sum(map(abs, row)) for row in a) <= 1 for a in matrices))
        wrong_order = 0
        for sign in (1, -1):
            word = v.source_events(4, sign)
            response, _ = v.formal_responses(word, 4)
            for index in range(len(word)):
                for coordinate in range(2):
                    state = [(Q(0), Q(0)) for _ in range(4)]
                    state[word[index][1]] = tuple(Q(int(j == coordinate)) for j in range(2))
                    for source, target, factor, s in word[index+1:]:
                        update = mv(matrices[factor], state[source])
                        state[target] = tuple(a+s*b for a, b in zip(state[target], update))
                    for row in range(4):
                        expected = evaluate(response[index][row], matrices)
                        self.assertEqual(state[row], tuple(expected[j][coordinate] for j in range(2)))
                        wrong = evaluate(response[index][row], matrices, backwards=True)
                        wrong_order += wrong != expected
        self.assertGreater(wrong_order, 0, "factor-order mutation must be observable")
        print("NONCOMMUTING_REVERSED_ORDER_REJECTIONS", wrong_order)

    def test_semantic_word_mutations(self):
        word = v.emit(4)
        exact, endpoint = v.formal_responses(word, 4)
        _, inverse = v.formal_responses(v.reverse(word), 4)
        mutants = ((word[:-1], endpoint),
                   (tuple((x, y, j, -s) for x, y, j, s in word), inverse))
        for mutant, expected in mutants:
            try:
                _, changed = v.formal_responses(mutant, 4)
            except ValueError:
                continue
            self.assertNotEqual(changed, expected, "missing restore or sign-only inverse accepted")
        source_wrong = [sum(bool(col[0]) for col in exact)]
        self.assertEqual(source_wrong, [0])
        # A defect on the untouched source is not a destination-supported fixture.
        state = v.scalar_execute(word[1:], [1]*4, [1, 0, 0, 0], [0]*(len(word)-1))
        self.assertNotEqual(state[0], v.counts(4)[0])
        aliased = [0]
        with self.assertRaisesRegex(ValueError, "all ancestor arrays distinct"):
            v.source_compose(lambda *args: None)(aliased, [0], [0, 1], [aliased], [1], Q(1, 2), 32, 1)

    def test_sharpness_and_all_register_boundary(self):
        word = v.emit(8)
        responses, _ = v.formal_responses(word, 5)
        target_errors = [sum(column[1].values()) for column in responses]
        target = v.scalar_execute(word, [1]*8, [0]*5, target_errors)
        self.assertEqual(target[1], 27)
        self.assertGreater(target[1], 26, "understated target budget accepted")
        scratch_errors = [sum(column[4].values()) for column in responses]
        scratch = v.scalar_execute(word, [1]*8, [0]*5, scratch_errors)
        self.assertEqual(scratch[4], 32)
        self.assertGreater(scratch[4], 27, "target count silently used for all registers")

    def test_endpoint_not_interior_or_noncontractive(self):
        word = v.emit(4)
        witness = None
        for factors in product((-1, 1), repeat=4):
            for start in range(1, len(word)+1):
                state = [0]*4
                state[word[start-1][1]] = 1
                for end in range(start, len(word)):
                    x, y, j, sign = word[end]
                    state[y] += sign*factors[j]*state[x]
                    if max(map(abs, state)) > 1:
                        witness = {"factors": factors, "cuts": [start, end+1], "state": state[:]}
                        break
                if witness:
                    break
            if witness:
                break
        self.assertIsNotNone(witness, "early-cut mutation must violate endpoint single-error bound")
        print("INTERIOR_BOUNDARY", json.dumps(witness, sort_keys=True))
        # n=2: an error after the inverse-left leaf is scaled by the right factor.
        two = v.emit(2)
        state = v.scalar_execute(two, [1, 2], [0, 0, 0], [0, 0, 1, 0])
        self.assertEqual(abs(state[1]), 2)
        self.assertGreater(abs(state[1]), 1, "G=1 incorrectly used for noncontractive factors")

    def test_feedback_cannot_be_inferred_from_endpoint(self):
        n = 2**10
        terms = v.budget_terms(v.leaf_count(n), v.counts(n)[1], 0, 4, 8, 0, 0, 0)
        self.assertEqual(terms["feedback"], 29)
        self.assertEqual(terms["target_accuracy"], 23)
        self.assertEqual(max(terms.values()), 29)
        unsafe_width = terms["target_accuracy"]
        feedback = Q(v.leaf_count(n)*2**8, 2**unsafe_width)
        self.assertGreater(feedback, Q(1, 2))
        self.assertGreaterEqual(max(v.budget_terms(4, 3, 0, 2, 4, 0, 1, 0, input_grid=100).values()), 100)
        with self.assertRaises(ValueError):
            v.budget_terms(4, 5, 0, 0, 0, 0, 0, 0)

    def test_source_pin_corruption(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for path in v.INPUTS:
                target = root/path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes((v.ROOT/path).read_bytes())
            v.bindings(root)
            source = root/v.SOURCE
            source.write_bytes(source.read_bytes()+b"\n# damaged source fixture\n")
            with self.assertRaisesRegex(ValueError, "source drift"):
                v.bindings(root)


if __name__ == "__main__":
    unittest.main(verbosity=2)

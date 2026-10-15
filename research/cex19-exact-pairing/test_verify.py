"""Behavioral and independent-oracle checks for the certificate. Apache-2.0."""
import itertools
import json
from pathlib import Path
import random
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from encoding import Formula, PIVOTS, Reject, build, dot
from rup import RupChecker, check_refutation, parse_proof
import verify


def literal_value(literal, model):
    if type(literal) is bool:
        return literal
    return model[abs(literal)] == (literal > 0)


def evaluate(formula, inputs):
    model = {}
    for variable in range(1, formula.variables+1):
        if variable in formula.inputs:
            model[variable] = inputs[formula.inputs[variable]]
        else:
            kind, left, right = formula.gates[variable]
            a, b = literal_value(left, model), literal_value(right, model)
            model[variable] = a and b if kind == "and" else a != b
    return model


def numeric_residual(config, rows, j):
    """Separate dense integer elimination, without the CNF gate builder."""
    pivots = list(PIVOTS[j])
    r = pivots + [t for t in range(19) if config[t][0][j] and t not in pivots]
    c = pivots + [s for s in range(19) if config[s][1][j] and s not in pivots]
    a = [[rows[t] >> s & 1 for s in c] for t in r]
    for k in range(len(pivots)):
        for t in range(k+1, len(r)):
            if a[t][k]:
                a[t] = [x ^ y for x, y in zip(a[t], a[k])]
    return [row[len(pivots):] for row in a[len(pivots):]]


def row_factor(matrix):
    """Return original independent rows and coefficients for every input row."""
    basis = {}
    chosen = []
    coefficients = []
    for row in matrix:
        value = sum(bit << s for s, bit in enumerate(row))
        combination = 0
        for bit in sorted(basis, reverse=True):
            if value >> bit & 1:
                vector, code = basis[bit]
                value ^= vector
                combination ^= code
        if value:
            code = 1 << len(chosen)
            chosen.append(row)
            basis[value.bit_length()-1] = value, combination ^ code
            coefficients.append(code)
        else:
            coefficients.append(combination)
    return chosen, coefficients


def witness_inputs(config, rows, capacity):
    inputs = {("B", t, s): bool(rows[t] >> s & 1) for t in range(19)
              for s in range(19) if t != s and dot(config[t][0], config[s][1]) == 0}
    for j in range(3):
        residual = numeric_residual(config, rows, j)
        basis, codes = row_factor(residual)
        if len(basis) > capacity:
            raise ValueError("fixture factor capacity")
        for k in range(capacity):
            inputs["e", j, k] = k < len(basis)
            for t, code in enumerate(codes):
                inputs["X", j, t, k] = bool(code >> k & 1)
            for s in range(len(residual[0])):
                inputs["Y", j, k, s] = bool(basis[k][s]) if k < len(basis) else False
    return inputs


def slow_rup(clauses, clause):
    """Naive repeated full scans, independent of watched-literal propagation."""
    assigned = set(-literal for literal in clause)
    variables = {abs(z) for c in clauses + [clause] for z in c}
    for _ in range(len(variables)+1):
        if any(-z in assigned for z in assigned):
            return True
        changed = False
        for c in clauses:
            if any(z in assigned for z in c):
                continue
            remaining = [z for z in c if -z not in assigned]
            if not remaining:
                return True
            if len(remaining) == 1 and remaining[0] not in assigned:
                assigned.add(remaining[0])
                changed = True
        if not changed:
            return False
    raise ValueError("oracle iteration bound")


def scan_refutation(formula, raw):
    """Second full-proof check using bit masks and repeated whole-clause scans."""
    def masks(clause):
        positive = sum(1 << (z-1) for z in set(clause) if z > 0)
        negative = sum(1 << (-z-1) for z in set(clause) if z < 0)
        return positive, negative

    clauses = [masks(c) for c in formula.clauses]
    proof = parse_proof(raw, formula.variables)
    for clause in proof:
        positive, negative = masks(clause)
        true, false = negative, positive
        conflict = False
        for _ in range(formula.variables+1):
            if true & false:
                conflict = True
                break
            previous = true | false
            for a, b in clauses:
                if a & b or a & true or b & false:
                    continue
                remaining = (a | b) & ~(true | false)
                if not remaining:
                    conflict = True
                    break
                if remaining & (remaining-1) == 0:
                    if remaining & a:
                        true |= remaining
                    else:
                        false |= remaining
            if true & false:
                conflict = True
            if conflict or previous == true | false:
                break
        if not conflict:
            raise ValueError("scan oracle rejected proof")
        clauses.append((positive, negative))
    return len(proof)


class CertificateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config, _ = verify.configuration(HERE)
        cls.expected = verify.load_json(HERE / "RESULT.json")
        cls.rows = cls.expected["upper"]["rows"]
        cls.proof = (HERE / "lower.rup").read_bytes()

    def test_real_cli_and_optimized_relocation(self):
        for optimized in (False, True):
            with tempfile.TemporaryDirectory() as tmp:
                target = Path(tmp) / "package"
                shutil.copytree(HERE, target, ignore=shutil.ignore_patterns("__pycache__"))
                command = [sys.executable, "-I", "-Werror", "-B"]
                if optimized:
                    command.append("-O")
                process = subprocess.run(command + [str(target / "verify.py")],
                                         capture_output=True, text=True, timeout=30)
                self.assertEqual(process.returncode, 0, process.stderr)
                self.assertEqual(process.stdout.strip(),
                                 "PASS_CEX19_EXACT_PAIRING minimum=21 ranks=7,6,8 RUP=1301 no_new_kappa")

    def test_upper_and_independent_column_rank(self):
        self.assertEqual(verify.witness_ranks(self.config, self.rows), [7, 6, 8])
        for j, expected in enumerate((7, 6, 8)):
            columns = []
            for s in range(19):
                if self.config[s][1][j]:
                    columns.append([row >> s & 1 for t, row in enumerate(self.rows)
                                    if self.config[t][0][j]])
            self.assertEqual(len(row_factor(columns)[0]), expected)
        for bad in (self.rows[:-1], [True] + self.rows[1:],
                    [self.rows[0] ^ 1] + self.rows[1:],
                    [self.rows[0] | 2] + self.rows[1:]):
            with self.assertRaises(Reject):
                verify.witness_ranks(self.config, bad)

    def test_schur_identity_on_64_admissible_pairings(self):
        rng = random.Random(2329)
        for _ in range(64):
            rows = [sum(int(t == s or (dot(self.config[t][0], self.config[s][1]) == 0
                                       and rng.randrange(2))) << s for s in range(19))
                    for t in range(19)]
            ranks = verify.witness_ranks(self.config, rows)
            for j in range(3):
                a = numeric_residual(self.config, rows, j)
                self.assertEqual(ranks[j], len(PIVOTS[j]) + len(row_factor(a)[0]))

    def test_satisfiable_cost_21_boundary_and_missing_budget(self):
        for capacity in (4, 5):
            formula, residuals, start = build(self.config, capacity)
            inputs = witness_inputs(self.config, self.rows, capacity)
            model = evaluate(formula, inputs)
            self.assertTrue(all(any(literal_value(z, model) for z in c)
                                for c in formula.clauses[:start]))
            self.assertEqual(all(any(literal_value(z, model) for z in c)
                                 for c in formula.clauses[start:]), capacity == 5)
            for j, a in enumerate(residuals):
                actual = [[int(literal_value(z, model)) for z in row] for row in a]
                self.assertEqual(actual, numeric_residual(self.config, self.rows, j))
            if capacity == 4:
                formula.clauses = formula.clauses[:start]
                with self.assertRaisesRegex(Reject, "non-RUP"):
                    check_refutation(formula, self.proof)

    def test_all_gate_truth_tables(self):
        for kind in ("and", "xor"):
            for a, b in itertools.product((False, True), repeat=2):
                f = Formula()
                x, y = f.fresh(("x",)), f.fresh(("y",))
                z = f.gate(kind, x, y)
                model = evaluate(f, {("x",): a, ("y",): b})
                self.assertEqual(literal_value(z, model), a and b if kind == "and" else a != b)
                self.assertTrue(all(any(literal_value(lit, model) for lit in c) for c in f.clauses))
                for wrong in (False, True):
                    mutated = dict(model)
                    mutated[z] = wrong
                    self.assertEqual(all(any(literal_value(lit, mutated) for lit in c)
                                         for c in f.clauses), wrong == model[z])

    def test_watched_propagation_against_scan_oracle(self):
        rng = random.Random(21)
        for _ in range(80):
            clauses = []
            for _ in range(12):
                variables = rng.sample(range(1, 6), rng.randrange(1, 4))
                clauses.append([z if rng.randrange(2) else -z for z in variables])
            checker = RupChecker(clauses, 5)
            for _ in range(12):
                clause = rng.sample(range(1, 6), rng.randrange(4))
                clause = [z if rng.randrange(2) else -z for z in clause]
                self.assertEqual(checker.is_rup(clause), slow_rup(clauses, clause))

    def test_refutation_and_proof_failure_controls(self):
        formula, _, _ = build(self.config)
        self.assertEqual(check_refutation(formula, self.proof), 1301)
        for raw in (b"0\n", self.proof.rsplit(b"\n", 2)[0] + b"\n",
                    b"10001 0\n0\n", b"d 1 0\n0\n", b"0\n0\n"):
            with self.assertRaises((Reject, ValueError)):
                check_refutation(formula, raw)
        self.assertEqual(parse_proof(b"1 0\n0\n", 1), [[1], []])

    def test_complete_proof_by_independent_scan_oracle(self):
        formula, _, _ = build(self.config)
        self.assertEqual(scan_refutation(formula, self.proof), 1301)

    def test_capacity_and_literal_failure_controls(self):
        self.assertFalse(RupChecker([], 10000).is_rup([10000]))
        for clauses, variables in (([], 0), ([], 10001), ([[]]*20001, 1)):
            with self.assertRaises(Reject):
                RupChecker(clauses, variables)
        for raw in (b"x"*1000001, b"1 0\n"*5000 + b"0\n",
                    b"1 "*129 + b"0\n", b"0 0\n", b"-2 0\n0\n"):
            with self.assertRaises(Reject):
                parse_proof(raw, 1)
        checker = RupChecker([[1, -1]], 2)
        self.assertFalse(checker.is_rup([]))
        formula, _, _ = build(self.config)
        with self.assertRaisesRegex(Reject, "non-RUP"):
            check_refutation(formula, b"2224 0\n0\n")

    def test_source_receipt_and_missing_file_controls(self):
        for mutation in ("source", "receipt", "missing", "duplicate"):
            with tempfile.TemporaryDirectory() as tmp:
                target = Path(tmp) / "package"
                shutil.copytree(HERE, target, ignore=shutil.ignore_patterns("__pycache__"))
                path = target / "RESULT.json"
                if mutation == "source":
                    (target / "configuration.json").write_text("[]")
                elif mutation == "receipt":
                    receipt = json.loads(path.read_text())
                    receipt["minimum"] = 20
                    path.write_text(json.dumps(receipt))
                elif mutation == "missing":
                    path.unlink()
                else:
                    path.write_text('{"minimum":21,"minimum":20}')
                with self.assertRaises((Reject, FileNotFoundError)):
                    verify.verify(target)


if __name__ == "__main__":
    unittest.main()

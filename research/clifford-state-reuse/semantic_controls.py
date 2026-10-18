#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent finite Gaussian-rational oracle for the pinned reuse change.

The inherited Clifford compiler is credited in the package notice. This
oracle does not call its rank, matrix/vector, phase or state evaluators.
No native inventory, timing claim or multiplication theorem is checked here.
"""
import argparse
import hashlib
import importlib.util
import json
import random
import subprocess
import sys
import tempfile
from collections import Counter
from fractions import Fraction
from pathlib import Path


BASELINE_SHA256 = "2982ead07721e83358dc67c6f49c2b4c16a236a6bebdfd72f58221be1f5d0962"
CANDIDATE_SHA256 = "6fac2848d3a0c0dfa92f83c8636beb903083cce1b01bda8ef582514071429221"
ASSERTION_GUARD = "FAIL_SEMANTIC_CONTROLS_ASSERTIONS_DISABLED"
ZERO = (Fraction(0), Fraction(0))
ONE = (Fraction(1), Fraction(0))
I_POWERS = (ONE, (Fraction(0), Fraction(1)),
            (Fraction(-1), Fraction(0)), (Fraction(0), Fraction(-1)))


def require(condition, message):
    if not condition:
        raise ValueError("FAIL_SEMANTIC_CONTROLS " + message)


def multiply(a, b):
    return (a[0] * b[0] - a[1] * b[1],
            a[0] * b[1] + a[1] * b[0])


def add(a, b):
    return a[0] + b[0], a[1] + b[1]


def circuit_matrix(n, circuit):
    """Literal dense action on every basis input, using rational coefficients."""
    require(0 <= n <= 3, "oracle dimension outside finite domain")
    size = 2 ** n
    columns = []
    for basis in range(size):
        state = [ZERO] * size
        state[basis] = ONE
        for gate in circuit:
            kind = gate[0]
            if kind == "P":
                rows = gate[1]
                require(len(rows) == n, "permutation row count")
                next_state = [ZERO] * size
                seen = set()
                for x in range(size):
                    image = 0
                    for i, row in enumerate(rows):
                        parity_sum = sum(((row >> j) & 1) * ((x >> j) & 1)
                                         for j in range(n))
                        image += (parity_sum % 2) * (2 ** i)
                    require(image not in seen, "noninvertible permutation")
                    seen.add(image)
                    next_state[image] = state[x]
                state = next_state
            elif kind == "X":
                offset = gate[1]
                require(0 <= offset < size, "X offset")
                state = [state[x ^ offset] for x in range(size)]
            elif kind == "D":
                rows, linear = gate[1:]
                require(len(rows) == len(linear) == n, "diagonal dimensions")
                next_state = []
                for x in range(size):
                    bits = [(x >> i) & 1 for i in range(n)]
                    exponent = sum(linear[i] * bits[i] for i in range(n))
                    exponent += 2 * sum(((rows[i] >> j) & 1) * bits[i] * bits[j]
                                        for i in range(n) for j in range(i + 1, n))
                    next_state.append(multiply(I_POWERS[exponent % 4], state[x]))
                state = next_state
            elif kind == "phase":
                state = [multiply(I_POWERS[gate[1] % 4], value) for value in state]
            elif kind == "C":
                direction, sign = gate[1:]
                require(0 < direction < size and sign in (-1, 1), "C parameters")
                stay = (Fraction(1, 2), Fraction(sign, 2))
                flip = (Fraction(1, 2), Fraction(-sign, 2))
                state = [add(multiply(stay, state[x]),
                             multiply(flip, state[x ^ direction]))
                         for x in range(size)]
            else:
                raise ValueError("FAIL_SEMANTIC_CONTROLS unknown oracle gate " + repr(kind))
        columns.append(tuple(state))
    return tuple(tuple(columns[j][i] for j in range(size)) for i in range(size))


def matrix_digest(matrix):
    payload = [[[str(real), str(imag)] for real, imag in row] for row in matrix]
    return hashlib.sha256(json.dumps(payload, separators=(",", ":")).encode()).hexdigest()


def fixtures():
    result = []

    def put(n, name, word, expected_rank=None):
        result.append((n, name, tuple(word), expected_rank))

    rng = random.Random(88)
    for n in range(4):
        for phase in range(4):
            put(n, "global-phase-" + str(phase), [] if phase == 0 else [("phase", phase)], 0)
        if not n:
            continue
        identity_rows = tuple(2 ** i for i in range(n))
        permutations = [identity_rows]
        if n >= 2:
            swap = (2, 1) + identity_rows[2:]
            shear = (3, 2) + identity_rows[2:]
            permutations += [swap, shear]
            put(n, "swap", [("P", swap)], 0)
            put(n, "shear-permutation", [("P", shear)], 0)
        if n == 3:
            cycle = (2, 4, 1)
            permutations.append(cycle)
            put(n, "cycle-permutation", [("P", cycle)], 0)
        for phase in (1, 3):
            put(n, "diagonal-" + str(phase), [("D", identity_rows, (phase,) * n)], 0)
        put(n, "linear-character", [("D", (0,) * n, (2,) + (0,) * (n - 1))], 0)
        if n >= 2:
            put(n, "quadratic-cross", [("D", (2, 1) + (0,) * (n - 2), (0,) * n)], 0)
        for offset in range(1, 2 ** n):
            put(n, "translation-" + str(offset), [("X", offset)], 0)
            for sign in (-1, 1):
                put(n, "C-" + str(offset) + "-" + str(sign), [("C", offset, sign)], 1)
        for sign in (-1, 1):
            put(n, "full-rank-" + str(sign), [("C", 2 ** i, sign) for i in range(n)], n)
        for trial in range(12):
            word = []
            for _ in range(5):
                kind = rng.choice(("P", "D", "X", "C", "phase"))
                if kind == "P":
                    word.append((kind, rng.choice(permutations)))
                elif kind == "D":
                    rows = [0] * n
                    for i in range(n):
                        rows[i] |= rng.randrange(2) * (2 ** i)
                        for j in range(i + 1, n):
                            bit = rng.randrange(2)
                            rows[i] |= bit * (2 ** j)
                            rows[j] |= bit * (2 ** i)
                    linear = tuple(((rows[i] >> i) & 1) + 2 * rng.randrange(2) for i in range(n))
                    word.append((kind, tuple(rows), linear))
                elif kind == "X":
                    word.append((kind, rng.randrange(2 ** n)))
                elif kind == "C":
                    word.append((kind, rng.randrange(1, 2 ** n), rng.choice((-1, 1))))
                else:
                    word.append((kind, rng.randrange(4)))
            put(n, "seed88-composition-" + str(trial), word)
    return result


def build_op(module, n, word):
    op = module.ident(n)
    for gate in word:
        if gate[0] == "P":
            child = module.perm(n, gate[1])
        elif gate[0] == "D":
            child = module.diag(n, gate[1], gate[2])
        elif gate[0] == "X":
            child = module.xgate(n, gate[1])
        elif gate[0] == "C":
            child = module.cgate(n, gate[1], gate[2])
        else:
            child = module.Op(n, module.identity(n), [gate])
        op = op.then(child)
    require(tuple(op.circuit) == word, "input constructors differ from declared literal word")
    return op


def bound_bytes(path, expected, label):
    raw = path.read_bytes()
    actual = hashlib.sha256(raw).hexdigest()
    if actual != expected:
        raise ValueError("FAIL_SOURCE_BINDING " + label + " expected=" + expected + " actual=" + actual)
    return raw


def load_bound(path, raw, name):
    require(name not in sys.modules, "module name already registered")
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None, "module spec")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module  # dataclass resolves the defining module here.
    try:
        # Execute the hash-checked bytes; the loader must not reread a changed file.
        exec(compile(raw, str(path), "exec"), module.__dict__)
    except BaseException:
        sys.modules.pop(name, None)
        raise
    return module


def monomial_control(module, mode):
    """Instrument actual retained guards without changing their source code."""
    word = (("X", 1),) if mode == "support-negative" else (("phase", 3),)
    op = module.Op(1, module.identity(1), list(word))
    original_state, original_then = module.Op.zero_state, module.Op.then
    source_states, output_states = [], []
    phase_outputs = []
    unchanged_phase_tableau = []

    def state_call(self, basis=0):
        value = original_state(self, basis)
        if self is op:
            if mode == "denominator-negative":
                vec, den = value
                value = ([(2 * real, 2 * imag) for real, imag in vec], den + 1)
            source_states.append(value)
        if any(self is output for output in phase_outputs):
            output_states.append(value)
        return value

    def then_call(self, other):
        output = original_then(self, other)
        if len(other.circuit) == 1 and other.circuit[0][0] == "phase":
            if mode == "phase-negative":
                changed = list(output.circuit)
                changed[-1] = ("phase", (changed[-1][1] + 1) % 4)
                mutant = module.Op(output.n, output.tab, changed)
                unchanged_phase_tableau.append(mutant.tab == output.tab)
                output = mutant
            phase_outputs.append(output)
        return output

    module.Op.zero_state, module.Op.then = state_call, then_call
    error = None
    compiled = None
    try:
        compiled, _ = module.monomial(op)
    except AssertionError as caught:
        error = caught
    finally:
        module.Op.zero_state, module.Op.then = original_state, original_then
    require(source_states, mode + " did not evaluate actual input state")
    vec, den = source_states[0]
    support_ok = all(value == (0, 0) for i, value in enumerate(vec) if i != 0)
    expected_column = tuple(row[0] for row in circuit_matrix(1, word))
    require(tuple((Fraction(a, 2 ** den), Fraction(b, 2 ** den)) for a, b in vec)
            == expected_column, mode + " observed input state differs from independent oracle")
    negative = mode.endswith("negative")
    if negative:
        require(error is not None, mode + " was accepted")
        trace = error.__traceback__
        while trace.tb_next is not None:
            trace = trace.tb_next
        require(trace.tb_frame.f_code.co_name == "monomial", mode + " failed outside monomial")
        if mode == "phase-negative":
            require(den == 0 and support_ok and phase_outputs and output_states,
                    "phase fault failed before final output-state equality")
            require(unchanged_phase_tableau == [True], "phase fault changed tableau")
            require(output_states[0] != source_states[0], "phase mutant state unchanged")
        elif mode == "support-negative":
            require(den == 0 and not support_ok and not phase_outputs and not output_states,
                    "support fault did not reach the isolated support guard")
        else:
            require(den == 1 and support_ok and not phase_outputs and not output_states,
                    "denominator fault did not reach the isolated normalization guard")
    else:
        require(error is None and den == 0 and support_ok and phase_outputs and output_states,
                mode + " positive guard reachability")
        require(circuit_matrix(1, compiled.circuit) == circuit_matrix(1, word),
                mode + " positive compiled matrix")
    return {"mode": mode, "rejected": negative, "input_state_evaluations": len(source_states),
            "final_output_state_evaluations": len(output_states), "first_denominator": den,
            "first_support_ok": support_ok, "phase_tableau_preserved": unchanged_phase_tableau}


def cli_guard_controls(baseline, candidate, baseline_raw, candidate_raw):
    """Separate actual CLI rejections; children stop before compiler imports."""
    results = []
    with tempfile.TemporaryDirectory(prefix="clifford-semantic-guards-") as work:
        work = Path(work)
        for label in ("assertions", "baseline", "candidate"):
            base_path, candidate_path = baseline, candidate
            if label != "assertions":
                bad_path = work / (label + "-mutated.py")
                bad_path.write_bytes((baseline_raw if label == "baseline" else candidate_raw)
                                     + b"\n# exact source guard mutation\n")
                if label == "baseline":
                    base_path = bad_path
                else:
                    candidate_path = bad_path
            out = work / (label + "-receipt.json")
            command = [sys.executable, "-I", "-B"]
            if label == "assertions":
                command.append("-O")
            command += [str(Path(__file__).resolve()), "--baseline", str(base_path),
                        "--candidate", str(candidate_path), "--out", str(out)]
            completed = subprocess.run(command, capture_output=True, text=True, timeout=10)
            message = ASSERTION_GUARD if label == "assertions" else "FAIL_SOURCE_BINDING " + label
            require(completed.returncode != 0 and message in completed.stderr and not out.exists(),
                    "CLI guard failed: " + label)
            results.append({"guard": label, "rejected": True, "receipt_created": False,
                            "returncode": completed.returncode, "required_error": message})
    return results


def run_checks(baseline, candidate):
    if sys.flags.optimize or not __debug__:
        raise SystemExit(ASSERTION_GUARD)
    # Check both sources before importing either one.
    baseline_raw = bound_bytes(baseline, BASELINE_SHA256, "baseline")
    candidate_raw = bound_bytes(candidate, CANDIDATE_SHA256, "candidate")
    names = ("_state_reuse_semantic_baseline", "_state_reuse_semantic_candidate")
    modules = []
    cases = []
    counts = Counter()
    ranks = Counter()
    controls = []
    try:
        for path, raw, name in zip((baseline, candidate), (baseline_raw, candidate_raw), names):
            modules.append(load_bound(path, raw, name))
        for n, name, word, expected_rank in fixtures():
            expected = circuit_matrix(n, word)
            compiled_results = []
            for module in modules:
                op = build_op(module, n, word)
                original = (op.n, op.tab, tuple(op.circuit))
                require(circuit_matrix(n, op.circuit) == expected, name + " input matrix")
                recipe, compiled = module.lower_child(op)
                require((op.n, op.tab, tuple(op.circuit)) == original, name + " input mutated")
                require(circuit_matrix(n, compiled.circuit) == expected, name + " compiled matrix")
                if expected_rank is not None:
                    require(recipe["rank"] == expected_rank, name + " expected rank")
                compiled_results.append((recipe, compiled.tab, tuple(compiled.circuit)))
            require(compiled_results[0] == compiled_results[1], name + " exact compiler outputs differ")
            rank = compiled_results[0][0]["rank"]
            ranks[(n, rank)] += 1
            counts["basis_columns_per_input"] += 2 ** n
            counts["matrix_entries_compared"] += 4 * (2 ** n) ** 2
            cases.append({"n": n, "name": name, "rank": rank, "all_basis_columns": 2 ** n,
                          "matrix_sha256": matrix_digest(expected)})
        require(len(cases) == 107 and counts["basis_columns_per_input"] == 552,
                "finite fixture coverage drift")
        for label, module in zip(("baseline", "candidate"), modules):
            for kind in ("phase", "support", "denominator"):
                for outcome in ("positive", "negative"):
                    control = monomial_control(module, kind + "-" + outcome)
                    controls.append({"engine": label, **control})
    finally:
        for name in names:
            sys.modules.pop(name, None)
    guard_controls = cli_guard_controls(baseline, candidate, baseline_raw, candidate_raw)
    return {
        "status": "PASS_INDEPENDENT_CLIFFORD_STATE_REUSE_CONTROLS",
        "baseline_sha256": BASELINE_SHA256, "candidate_sha256": CANDIDATE_SHA256,
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "fixture_seed": 88, "dimensions": [0, 1, 2, 3], "fixture_cases": len(cases),
        "seeded_compositions": 36, "seeded_word_length": 5,
        "basis_columns_per_input": counts["basis_columns_per_input"],
        "input_matrices_checked": 2 * len(cases), "compiled_matrices_checked": 2 * len(cases),
        "matrix_entries_compared": counts["matrix_entries_compared"],
        "exact_recipe_tableau_circuit_pairs": len(cases), "input_immutability_checks": 2 * len(cases),
        "ranks": [{"n": n, "rank": rank, "cases": count}
                  for (n, rank), count in sorted(ranks.items())],
        "cases": cases, "monomial_guard_controls": controls, "separate_cli_guards": guard_controls,
        "limitations": [
            "Finite n<=3 circuits and every basis input, not the complete U8 native inventory.",
            "The oracle interprets literal circuit semantics independently; it does not prove all Clifford algebra.",
            "Denominator fault is a controlled noncanonical evaluator result with unchanged rational amplitudes.",
            "No performance, supplier hosting, changed-word transport, kappa or full multiplication theorem claim.",
        ],
    }


def main():
    if sys.flags.optimize or not __debug__:
        raise SystemExit(ASSERTION_GUARD)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    require(not args.out.exists() and not args.out.is_symlink(), "receipt path must be fresh")
    receipt = run_checks(args.baseline.resolve(), args.candidate.resolve())
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(receipt, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print("PASS_INDEPENDENT_CLIFFORD_STATE_REUSE_CONTROLS cases=107 basis_columns=552 "
          "math_rejections=6 positive_guard_reachability=6 source_guards=2 assertion_off=1")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, subprocess.TimeoutExpired) as error:
        raise SystemExit(str(error))

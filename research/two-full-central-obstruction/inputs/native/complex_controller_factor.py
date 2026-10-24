#!/usr/bin/env python3
"""Exact complex controller factorizations over an integral Laurent ring.

The native local operator is an EXPLICIT INPUT CONTRACT supplied by the
complex reconstruction: F_s=D_s S_y(Q^-1), B_s=D_s S_x(-Q).
No order-two relation, numerical Fourier characters, phase erasure, or
F2-to-complex lift is used in the acceptance check.  All Laurent
coefficients are reconstructed and multiplied over Q.  Binary candidates
are only a finite discovery filter, not an exhaustive rational census.
Apache-2.0; substantial OpenAI assistance.
"""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import argparse
import json
import time

import mixed_productive_bit as B

HERE = Path(__file__).resolve().parent


def plus(a, b, coefficient=1):
    result = dict(a)
    for term, value in b.items():
        result[term] = result.get(term, 0)+coefficient*value
        if not result[term]:
            del result[term]
    return result


def monomial_times(polynomial, exponents, coefficient=1):
    return {tuple(a+b for a, b in zip(term, exponents)):coefficient*value
            for term, value in polynomial.items()}


def controller(p, keep, wrong_reverse_sign=False):
    n, stages = 2*p, 2*p+1
    zero = (0,)*(stages+1)
    matrix = [[{zero:1} if i == j else {} for j in range(n)] for i in range(n)]
    events, idle = [], []
    def term(q, selected):
        return (q,)+tuple(int(s in selected) for s in range(stages))
    def idle_call(pair, selected, kind):
        index = len(idle)
        retained = bool(keep >> index & 1)
        idle.append(dict(index=index, kind=kind, pair=pair, stages=list(selected),
                         rank=8*len(selected), retained=retained))
        if retained:
            for role in (2*pair, 2*pair+1):
                matrix[role] = [monomial_times(x, term(0, selected)) for x in matrix[role]]
            events.append(["IDLE", pair, list(selected)])
    def local(stage, pair, reverse):
        x, y = 2*pair, 2*pair+1
        if reverse:
            x, y = y, x
        sign = -1 if reverse and not wrong_reverse_sign else 1
        exponent = 1 if reverse else -1
        matrix[y] = [plus(a, monomial_times(b, term(exponent, []), sign))
                     for a, b in zip(matrix[y], matrix[x])]
        for role in (x, y):
            matrix[role] = [monomial_times(x, term(0, [stage])) for x in matrix[role]]
        events.append(["LOCAL", stage, pair, reverse])
        if stage % 2 and stage <= 2*p-3:
            idle_call((stage+1)//2, list(range(stage+1)), "initial")
        elif stage % 2 == 0 and 2 <= stage <= 2*p-2:
            idle_call(stage//2, [stage], "middle")
        elif stage == 2*p:
            for j in range(p-1):
                idle_call(j, list(range(2*j+3, 2*p+1)), "terminal")
    def bridge(dst, src, coefficient):
        for d, s, c in ((2*dst, 2*src, coefficient), (2*src+1, 2*dst+1, -coefficient)):
            matrix[d] = [plus(a, b, c) for a, b in zip(matrix[d], matrix[s])]
            events.append(["ADD", d, s, c])
    local(0, 0, False)
    for j in range(p):
        local(2*j+1, j, True)
        if j < p-1:
            bridge(j, j+1, 1)
        local(2*j+2, j, False)
        if j < p-1:
            bridge(j, j+1, -1)
    for j in reversed(range(p-1)):
        bridge(j+1, j, 1)
    for j in range(p):
        matrix[2*j], matrix[2*j+1] = matrix[2*j+1], [monomial_times(x, zero, -1) for x in matrix[2*j]]
        events.append(["SIGNED_SWAP", 2*j, 2*j+1])
    coefficients = {}
    for i, row in enumerate(matrix):
        for j, polynomial in enumerate(row):
            for key, value in polynomial.items():
                coefficients.setdefault(key, [[Q(0)]*n for _ in range(n)])[i][j] += value
    coefficients = {key:matrix for key, matrix in coefficients.items() if any(any(row) for row in matrix)}
    return coefficients, events, idle


def matrix_rank(rows):
    basis = {}
    for row in rows:
        row = list(map(Q, row))
        for j in sorted(basis):
            if row[j]:
                scale = row[j]
                row = [a-scale*b for a, b in zip(row, basis[j])]
        pivot = next((j for j, x in enumerate(row) if x), None)
        if pivot is not None:
            scale = row[pivot]
            basis[pivot] = [x/scale for x in row]
    return len(basis)


def scalar_program(matrix):
    n = len(matrix)
    work = [row[:] for row in matrix]
    elimination = []
    for j in range(n):
        pivot = next(i for i in range(j, n) if work[i][j])
        if pivot != j:
            work[j], work[pivot] = work[pivot], work[j]
            elimination.append(["SWAP", j, pivot])
        if work[j][j] != 1:
            scale = 1/work[j][j]
            work[j] = [scale*x for x in work[j]]
            elimination.append(["SCALE", j, str(scale)])
        for i in range(n):
            if i != j and work[i][j]:
                scale = -work[i][j]
                work[i] = [a+scale*b for a, b in zip(work[i], work[j])]
                elimination.append(["ADD", i, j, str(scale)])
    program = []
    for op in reversed(elimination):
        if op[0] == "SWAP":
            program.append(op)
        elif op[0] == "SCALE":
            program.append(["SCALE", op[1], str(1/Q(op[2]))])
        else:
            program.append(["ADD", op[1], op[2], str(-Q(op[3]))])
    replay = [[Q(i == j) for j in range(n)] for i in range(n)]
    for op in program:
        if op[0] == "SWAP":
            replay[op[1]], replay[op[2]] = replay[op[2]], replay[op[1]]
        elif op[0] == "SCALE":
            replay[op[1]] = [Q(op[2])*x for x in replay[op[1]]]
        else:
            replay[op[1]] = [a+Q(op[3])*b for a, b in zip(replay[op[1]], replay[op[2]])]
    B.need(replay == matrix, "Exact signed scalar boundary program")
    coefficients = [Q(x) for row in matrix for x in row]
    B.need(all(q.denominator & (q.denominator-1) == 0 for q in coefficients), "Dyadic boundary coefficients")
    return program


def factor(coefficients):
    n = len(next(iter(coefficients.values())))
    total = [[sum(matrix[i][j] for matrix in coefficients.values()) for j in range(n)] for i in range(n)]
    inverse = B.rational_inverse(total)
    projectors = {key:B.matrix_multiply(inverse, matrix) for key, matrix in coefficients.items()}
    for key, matrix in projectors.items():
        if B.matrix_multiply(matrix, matrix) != matrix:
            return None
        for other, second in projectors.items():
            if key != other and any(any(row) for row in B.matrix_multiply(matrix, second)):
                return None
    columns, diagonal = [], []
    for key, matrix in sorted(projectors.items()):
        for column in zip(*matrix):
            if matrix_rank(columns+[column]) > len(columns):
                columns.append(list(column))
                diagonal.append(key)
    B.need(len(columns) == n, "All rational projector images")
    right = [list(row) for row in zip(*columns)]
    left = B.matrix_multiply(B.rational_inverse(right), inverse)
    transformed = {key:B.matrix_multiply(B.matrix_multiply(left, matrix), right)
                   for key, matrix in coefficients.items()}
    expected = {key:[[Q(i == j and diagonal[i] == key) for j in range(n)] for i in range(n)]
                for key in set(diagonal)}
    B.need(transformed == expected, "Every Laurent coefficient equals the advertised diagonal")
    return dict(left=left, right=right, diagonal=diagonal,
                left_program=scalar_program(left), right_program=scalar_program(right))


def serialize_matrix(matrix):
    return [[str(x) for x in row] for row in matrix]


def serialize_case(p, keep, coefficients, events, idle, result):
    # Rank normalization is an input contract of the complex native source:
    # D0=F9 Q^-1; Ds for s>0 transform fresh eight-axis blocks; Q^2 and
    # Ds^2 are explicitly free Pauli/translation operators. The EXACT
    # Laurent monomials remain in this receipt for a separate phase audit.
    jobs = Counter()
    for term in result["diagonal"]:
        B.need(term[0] in (-1, 1), "Only stated central-Q endpoint normalization")
        B.need(all(x in (0, 1) for x in term[1:]), "No hidden squared stage transforms")
        jobs[1+8*sum(term[1:])] += 112
    scalar_coefficients = [x for matrix in (result["left"], result["right"]) for row in matrix for x in row]
    return dict(pairs=p, stages=2*p+1, keep_idle_mask=keep,
                coefficient_variables=["Q"]+[f"D{s}" for s in range(2*p+1)],
                coefficient_matrices=[dict(exponents=list(key), matrix=serialize_matrix(matrix))
                                      for key, matrix in sorted(coefficients.items())],
                left=serialize_matrix(result["left"]), right=serialize_matrix(result["right"]),
                left_program=result["left_program"], right_program=result["right_program"],
                exact_diagonal_monomials=[list(term) for term in result["diagonal"]],
                all_boundary_entries_integral=all(x.denominator == 1 for x in scalar_coefficients),
                maximum_boundary_absolute_coefficient=str(max(map(abs, scalar_coefficients))),
                endpoint_after_stated_free_Pauli_normalization=dict(sorted(jobs.items())),
                retained_idle_windows=[row for row in idle if row["retained"]],
                omitted_idle_windows=[row for row in idle if not row["retained"]],
                physical_events=events,
                full_Laurent_identity=True, native_operator_contract_independently_replayed=False)


def run(max_p):
    start = time.monotonic()
    cases, census = [], {}
    for p in range(1, max_p+1):
        binary_candidates = []
        for keep in range(1 << (3*(p-1))):
            binary_coefficients, _, _ = B.physical_controller(p, keep)
            if B.simultaneous_monomial_factor(binary_coefficients) is not None:
                binary_candidates.append(keep)
        passed = 0
        for keep in binary_candidates:
            coefficients, events, idle = controller(p, keep)
            result = factor(coefficients)
            if result is not None:
                cases.append(serialize_case(p, keep, coefficients, events, idle, result))
                passed += 1
        census[p] = dict(binary_discovery_trials=1 << (3*(p-1)),
                         binary_candidates=len(binary_candidates), exact_Laurent_factorizations=passed)
        print(json.dumps(dict(pairs=p, **census[p])), flush=True)
    chosen = next(row for row in cases if row["pairs"] == 3 and row["keep_idle_mask"] == 43)
    left = [[Q(x) for x in row] for row in chosen["left"]]
    right = [[Q(x) for x in row] for row in chosen["right"]]
    wrong, _, _ = controller(3, 43, True)
    transformed = {key:B.matrix_multiply(B.matrix_multiply(left, matrix), right)
                   for key, matrix in wrong.items()}
    expected = {tuple(key):[[Q(i == j and tuple(chosen["exact_diagonal_monomials"][i]) == tuple(key))
                            for j in range(6)] for i in range(6)]
                for key in chosen["exact_diagonal_monomials"]}
    B.need(transformed != expected, "Incorrect backward sign rejected over Q")
    return dict(schema="complex-controller-integral-Laurent-factorization/1",
                status="PASS_EXACT_LAURENT_IDENTITIES_CONDITIONAL_ON_NATIVE_LOCAL_CONTRACT",
                local_contract=dict(forward="D_s * [[1,0],[Q^-1,1]]",
                                    backward="D_s * [[1,-Q],[0,1]]",
                                    commutation="Q,D0,...,D(2p) commute; no finite-order relation used"),
                census=census, cases=cases,
                selected_p3_keep43=chosen,
                controls=dict(wrong_backward_sign_rejected=True),
                source_sha256={Path(__file__).name:sha256(Path(__file__).read_bytes()).hexdigest(),
                               "mixed_productive_bit.py":sha256((HERE/"mixed_productive_bit.py").read_bytes()).hexdigest()},
                runtime_seconds=time.monotonic()-start,
                scope="Exact formal operator identity and emitted constant dyadic adapters. Native source binding, free-phase normalization, helper ownership, complete tariffs and all-size transfer belong to separate certificates.",
                new_kappa=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-p", type=int, default=5)
    parser.add_argument("--output", type=Path, default=HERE/"COMPLEX-CONTROLLER-FACTOR.json")
    args = parser.parse_args()
    B.need(3 <= args.max_p <= 6, "Bounded candidate menu")
    data = run(args.max_p)
    args.output.write_text(json.dumps(data, indent=2, sort_keys=True)+"\n")
    print(json.dumps(dict(status=data["status"], seconds=data["runtime_seconds"], cases=len(data["cases"]))))


if __name__ == "__main__":
    main()

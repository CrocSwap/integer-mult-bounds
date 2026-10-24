"""Check the finite scalar completion with separate field arithmetic."""

import hashlib
import json
from collections import defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "dirty-word.json"


def add(left, right):
    lb, la = divmod(left, 3)
    rb, ra = divmod(right, 3)
    return (la + ra) % 3 + 3 * ((lb + rb) % 3)


def product(left, right):
    lb, la = divmod(left, 3)
    rb, ra = divmod(right, 3)
    polynomial = [la * ra, la * rb + lb * ra, lb * rb]
    return (polynomial[0] - polynomial[2]) % 3 + 3 * (polynomial[1] % 3)


def negative(value):
    return product(2, value)


def power(value, exponent):
    result = 1
    while exponent:
        if exponent & 1:
            result = product(result, value)
        value = product(value, value)
        exponent >>= 1
    return result


def inverse_element(value):
    assert value != 0
    result = power(value, 7)
    assert product(value, result) == 1
    return result


def combination(coefficients, vectors):
    assert len(coefficients) == len(vectors)
    result = [0] * len(vectors[0])
    for coefficient, vector in zip(coefficients, vectors):
        if coefficient:
            result = [add(current, product(coefficient, entry))
                      for current, entry in zip(result, vector)]
    return result


def matrix_product(left, right):
    assert len(left[0]) == len(right)
    return [combination(row, right) for row in left]


def identity(size):
    return [[int(i == j) for j in range(size)] for i in range(size)]


def reduced(matrix):
    rows = [list(row) for row in matrix]
    pivots = []
    for j in range(len(rows[0])):
        pivot = next((i for i in range(len(pivots), len(rows)) if rows[i][j]), None)
        if pivot is None:
            continue
        r = len(pivots)
        rows[r], rows[pivot] = rows[pivot], rows[r]
        scale = inverse_element(rows[r][j])
        rows[r] = [product(scale, entry) for entry in rows[r]]
        for i in range(len(rows)):
            if i != r and rows[i][j]:
                coefficient = negative(rows[i][j])
                rows[i] = [add(entry, product(coefficient, base))
                           for entry, base in zip(rows[i], rows[r])]
        pivots.append(j)
    return rows, pivots


def matrix_inverse(matrix):
    n = len(matrix)
    assert all(len(row) == n for row in matrix)
    rows, pivots = reduced([row + unit for row, unit in zip(matrix, identity(n))])
    assert pivots[:n] == list(range(n))
    assert [row[:n] for row in rows] == identity(n)
    result = [row[n:] for row in rows]
    assert matrix_product(matrix, result) == matrix_product(result, matrix) == identity(n)
    return result


for a in range(1, 9):
    assert power(a, 8) == 1
assert product(3, 3) == 2
raw = SOURCE.read_bytes()
assert hashlib.sha256(raw).hexdigest() == "112532d00d991979ce21b2f74b48cd5bffdb1420abea44f2571f667a628a261f"
word = json.loads(raw)
assert len(word["inputs"]) == len(word["outputs"]) == 175
assert len(word["local_words"]) == 182
units = identity(175)
inputs = {tuple(stub): units[i] for i, stub in enumerate(word["inputs"])}
outputs = {}
output_keys = {tuple(stub) for stub in word["outputs"]}
packets = {}
physical = 0
for local in word["local_words"]:
    vertex = local["vertex"]
    assert len(local["known_edges"]) == len(local["unknown_edges"]) == 5
    assert len(local["matrix"]) == 5
    matrix_inverse(local["matrix"])
    known = [inputs[vertex, edge] if (vertex, edge) in inputs else packets[edge]
             for edge in local["known_edges"]]
    unknown = matrix_product(local["matrix"], known)
    for edge, vector in zip(local["unknown_edges"], unknown):
        if (vertex, edge) in output_keys:
            assert (vertex, edge) not in outputs
            outputs[vertex, edge] = vector
        else:
            assert edge not in packets
            packets[edge] = vector
            physical += 1
transfer = [outputs[tuple(stub)] for stub in word["outputs"]]
assert transfer == word["transfer"]
assert physical == 735
assert [row[:157] for row in transfer[:157]] == identity(157)

input_edges = defaultdict(list)
output_edges = defaultdict(list)
for i, (_, edge) in enumerate(word["inputs"][157:]):
    input_edges[edge].append(i)
for i, (_, edge) in enumerate(word["outputs"][157:]):
    output_edges[edge].append(i)
assert len(input_edges) == len(output_edges) == 9
assert all(len(indices) == 2 for indices in (*input_edges.values(), *output_edges.values()))
input_pairs = list(input_edges.values())
output_pairs = list(output_edges.values())
quotient_rows = [row[:157] + [add(row[157 + a], row[157 + b]) for a, b in input_pairs]
                 for row in transfer]
assert quotient_rows[:157] == [row + [0] * 9 for row in identity(157)]
assert all(quotient_rows[157 + a] == quotient_rows[157 + b] for a, b in output_pairs)
junk_rows = [quotient_rows[157 + a] for a, b in output_pairs]
b9 = [row[:157] for row in junk_rows]
d9 = [row[157:] for row in junk_rows]
inverse_d9 = matrix_inverse(d9)
correction = matrix_product(inverse_d9, b9)
normalized = matrix_product(inverse_d9, junk_rows)
completed = [[add(entry, negative(error)) for entry, error in zip(row, corr + [0] * 9)]
             for row, corr in zip(normalized, correction)]
assert completed == [[0] * 157 + row for row in identity(9)]
full_completion = quotient_rows[:157] + completed
assert full_completion == identity(166)
correction_rank = len(reduced(correction)[1])
assert correction_rank == 9

a18 = [row[157:] for row in transfer[:157]]
b18 = [row[:157] for row in transfer[157:]]
d18 = [row[157:] for row in transfer[157:]]
ba = matrix_product(b18, a18)
s18 = [[add(entry, negative(error)) for entry, error in zip(row, other)]
       for row, other in zip(d18, ba)]
inverse_s18 = matrix_inverse(s18)
factors_path = HERE / "PG29-FACTORS.json"
factors = json.loads(factors_path.read_text())
independent_factors = dict(B9=b9, D9=d9, inverse_D9=inverse_d9,
                           correction=correction, S18=s18, inverse_S18=inverse_s18)
assert factors == independent_factors
producer = json.loads((HERE / "PG29-COMPLETION.json").read_text())
assert producer["source_word_sha256"] == hashlib.sha256(raw).hexdigest()
assert producer["matched_C_edges"] == list(input_edges)
assert producer["matched_J_edges"] == list(output_edges)
assert producer["D9_nonzeros"] == sum(bool(value) for row in d9 for value in row) == 74
assert producer["correction_nonzeros"] == sum(bool(value) for row in correction for value in row) == 1243


receipt = dict(status="PASS_PG29_MATCHED_DIRTY_COMPLETION", source_word_sha256=hashlib.sha256(raw).hexdigest(),
    field="F3[t]/(t^2+1), encoded by a+3b", independent_field_operations=True,
    local_maps=182, physical_transmissions=physical, independent_input_stubs=175,
    matched_input_pairs=9, matched_output_pairs=9, quotient_dimension=166,
    correction_rank=correction_rank, all_formal_columns_restored=True,
    generic_schur_dimension=18, generic_schur_invertible=True,
    D9_nonzeros=74, correction_nonzeros=1243,
    physical_frames=False, paid_supplier=False, new_kappa=False)
(HERE/"COMPLETION-RESULT.json").write_text(json.dumps(receipt,indent=2)+"\n")
print(json.dumps(receipt,indent=2))

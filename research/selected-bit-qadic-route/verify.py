#!/usr/bin/env python3
"""Source-bound selected-route receipt. No predecessor Python is executed."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import route as R

WORD = "research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz"
ROOTS = "research/e8-bit-carrier-skeleton/data/bit/bitE8-r865.json.gz"
EXPECTED = "research/e8-bit-p111-tuned/tune/EXPECTED.json"
ASSEMBLY = "research/community-frontier1094-audit/ASSEMBLY.json"


def authenticated_inputs(root=ROOT):
    manifest = json.loads((HERE / "SOURCES.json").read_text())
    R.require(len(manifest["files"]) <= 16, "source count")
    result = {}
    for item in manifest["files"]:
        if item["usage"] != "input":
            continue
        path = root / item["path"]
        R.require(path.stat().st_size <= 8 * 1024**2, "source byte capacity")
        data = path.read_bytes()
        R.require(hashlib.sha256(data).hexdigest() == item["sha256"], "source hash: " + item["path"])
        result[item["path"]] = data
    return result


def decoded_word(data):
    # The authenticated inputs are immutable; also cap decompression before JSON.
    import io
    with gzip.GzipFile(fileobj=io.BytesIO(data)) as stream:
        payload = stream.read(8 * 1024**2 + 1)
    R.require(len(payload) <= 8 * 1024**2, "word byte capacity")
    return json.loads(payload)


def selected_route(data):
    assembly = json.loads(data[ASSEMBLY])
    expected = json.loads(data[EXPECTED])
    citation = assembly["bit_supplier"]
    blob = hashlib.sha1(b"blob " + str(len(data[EXPECTED])).encode() + b"\0" + data[EXPECTED]).hexdigest()
    R.require(citation["pr"] == 589 and citation["path"] == EXPECTED, "BIT producer")
    R.require(citation["git_blob_sha1"] == blob, "BIT citation blob")
    word = decoded_word(data[WORD])
    old = decoded_word(data[ROOTS])
    R.require((word["h"], word["v"], word["R"]) == (8, 111, 439), "word parameters")
    R.require(expected["word"]["file_sha256"] == hashlib.sha256(data[WORD]).hexdigest(), "word binding")
    R.require(len(old["lines"]) == 120 and len(word["ports_geom"]) == 111, "port inventory")
    port = 8
    original = word["ports_geom"][port]
    R.require(original == 8 and word["lines"][port] == old["lines"][original], "selected port")
    matrix = R.selected_reflection(old["lines"], original)
    R.require(R.multiply(matrix, matrix) == R.identity(15), "reflection involution")
    R.require(matrix == [list(r) for r in zip(*matrix)], "reflection symmetry")
    R.require(any(x.denominator > 1 for row in matrix for x in row), "nontrivial rational route")
    program = R.column_program(matrix)
    return matrix, program


def modular_matrix(matrix, modulus):
    return [[x.numerator * pow(x.denominator, -1, modulus) % modulus for x in row]
            for row in matrix]


def dense_oracle(values, matrix, axes, modulus):
    """Direct modular right product, independent of elementary carry updates."""
    local = modular_matrix(matrix, modulus)
    result = [r[:] for r in values]
    for row in range(64):
        for j, dest in enumerate(axes):
            result[row][dest] = sum(values[row][src] * local[i][j]
                                    for i, src in enumerate(axes)) % modulus
    return result


def fixture(q, width):
    """An invertible dense matrix L U with arbitrary high digits, no GL enumeration."""
    modulus = q**width
    values = [[int(i == j) for j in range(64)] for i in range(64)]
    for i in range(1, 64):
        values[i][0] = (q * (i * i + 7) + i + 1) % modulus
    for j in range(1, 64):
        c = (q * (3 * j + 1) - j - 2) % modulus
        for i in range(64):
            values[i][j] = (values[i][j] + c * values[i][0]) % modulus
    return values


def split_fields(values, q):
    return {"ancestors": (19, (4, 7), "arbitrary dirty prefix"),
            "role_type": 28424, "unused_child_stock": (23, 0, 8191),
            "head_data": (3, 11, 5), "spectators": (29, 31),
            "current_low": [[x % q for x in row] for row in values],
            "current_high": [[x // q for x in row] for row in values]}


def join_fields(fields, q):
    return [[low + q * high for low, high in zip(a, b)]
            for a, b in zip(fields["current_low"], fields["current_high"])]


def check_case(matrix, program, q, width, axes):
    values = fixture(q, width)
    fields = split_fields(values, q)
    original = json.loads(json.dumps(fields))
    routed = R.route_fields(fields, program, axes, q, width)
    expected = dense_oracle(values, matrix, axes, q**width)
    R.require(join_fields(routed, q) == expected, "dense route mismatch")
    R.require(json.loads(json.dumps(fields)) == original, "input mutated")
    for name in fields.keys() - {"current_low", "current_high"}:
        R.require(routed[name] == fields[name], "spectator changed: " + name)
    restored = R.route_fields(routed, R.inverse_program(program), axes, q, width)
    R.require(restored == fields, "inverse restoration")
    # Transpose/order mistakes can survive a symmetric route. Literal factor
    # replay is checked separately against the full noncommuting program below.
    return hashlib.sha256(json.dumps(expected, separators=(",", ":")).encode()).hexdigest()


def program_matrix(program):
    z = R.identity(15)
    for kind, i, j, c in program:
        for row in range(15):
            if kind == "swap":
                z[row][i], z[row][j] = z[row][j], z[row][i]
            elif kind == "scale":
                z[row][i] *= c
            else:
                z[row][i] += c * z[row][j]
    return z


def carry_omission_control(matrix):
    """A wrong router can preserve all low classes and pass an inverse test."""
    q, width = 5, 2
    axes = list(range(8)) + list(range(57, 64))
    original = fixture(q, width)
    value = original
    first = None
    for step in range(2):
        low = dense_oracle([[x % q for x in r] for r in value], matrix, axes, q)
        high = dense_oracle([[x // q for x in r] for r in value], matrix, axes, q)
        value = [[a + q * b for a, b in zip(x, y)] for x, y in zip(low, high)]
        if step == 0:
            first = value
    expected = dense_oracle(original, matrix, axes, q**width)
    R.require(value == original, "uncarried mutant restoration")
    R.require(all(first[i][j] % q == expected[i][j] % q
                  for i in range(64) for j in range(64)), "uncarried low route")
    R.require((first[0][6], expected[0][6]) == (19, 14), "carry omission witness")
    return {"q": q, "width": width, "stage": 8, "row": 0, "column": 6,
            "uncarried_entry": 19, "correct_entry": 14,
            "active_input_row": [original[0][k] for k in axes],
            "low_residues_correct": True, "two_applications_restore": True,
            "full_right_product_correct": False}


def receipt(data):
    matrix, program = selected_route(data)
    R.require(program_matrix(program) == matrix, "factor product")
    omitted = 0
    for i in range(len(program)):
        R.require(program_matrix(program[:i] + program[i + 1:]) != matrix, "ineffective factor")
        omitted += 1
    cases = []
    # Small odd radices test carries; 2^89-1 is a known Mersenne prime >2^80.
    # No primality inference or selected-prime eligibility follows from fixtures.
    for q in (5, 7, 2**89 - 1):
        for width in (1, 2, 3, 8):
            for stage in (1, 8):
                axes = list(range(8)) + list(range(8 + 7 * (stage - 1), 8 + 7 * stage))
                digest = check_case(matrix, program, q, width, axes)
                cases.append({"q": str(q), "width": width, "stage": stage, "dense_sha256": digest})
    return {"status": "PASS_SELECTED_BIT_QADIC_ROUTE", "selected_port": 8, "original_port": 8,
            "ambient_dimension": 64, "local_dimension": 15,
            "root": [0, 1, 1, 0, 1, 0, 0, 1],
            "matrix": [[str(x) for x in row] for row in matrix],
            "column_program": [[kind, i, j, str(c)] for kind, i, j, c in program],
            "field_contract": {"reads": ["current_low", "current_high"],
                               "writes": ["current_low", "current_high"],
                               "preserves": ["ancestors", "role_type", "unused_child_stock", "head_data", "spectators"]},
            "elementary_column_factors": len(program), "row_field_steps_per_route": 64 * len(program),
            "omitted_factor_controls": omitted, "cases": cases,
            "carry_omission_counterexample": carry_omission_control(matrix),
            "scope": "One selected route's exact row-index lowering; no physical compiler, supplier or new kappa."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-result", type=Path)
    args = parser.parse_args()
    result = receipt(authenticated_inputs())
    if args.write_result:
        with args.write_result.open("x") as out:
            out.write(json.dumps(result, indent=2) + "\n")
    else:
        expected = json.loads((HERE / "RESULT.json").read_text())
        R.require(result == expected, "required result mismatch")
    print(result["status"], "factors=" + str(result["elementary_column_factors"]),
          "cases=" + str(len(result["cases"])), "no_new_kappa")


if __name__ == "__main__":
    main()

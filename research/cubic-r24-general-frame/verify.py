"""Exact symbolic replay of the r=24 general-frame repair.

apoursh, with substantial OpenAI Codex assistance. Apache-2.0.
Standard library only; explicit checks remain active under Python -O.
"""
from copy import deepcopy
from fractions import Fraction as F
from hashlib import sha256
import json
from math import isqrt
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent


def require(ok, message):
    if not ok:
        raise ValueError(message)


def dyadic(q):
    return q.denominator & (q.denominator - 1) == 0


def cube(row):
    a, b = row
    return [a**3, 3*a*a*b, 3*a*b*b, b**3]


def solve_weights(forms, target):
    """Exact elimination; no predecessor weight formula is used."""
    columns = [cube([F(x) for x in row]) for row in forms]
    matrix = [[columns[j][i] for j in range(3)] + [F(target[i])]
              for i in range(3)]
    for j in range(3):
        pivot = next(i for i in range(j, 3) if matrix[i][j])
        matrix[j], matrix[pivot] = matrix[pivot], matrix[j]
        scale = matrix[j][j]
        matrix[j] = [x / scale for x in matrix[j]]
        for i in range(3):
            if i != j:
                scale = matrix[i][j]
                matrix[i] = [x - scale*y for x, y in zip(matrix[i], matrix[j])]
    weights = [row[-1] for row in matrix]
    require(sum(weights[j]*columns[j][3] for j in range(3)) == target[3],
            "unmatched B^3 coefficient")
    return weights


def replay(r, program):
    """Exact polynomial output increment and source matrix after every event."""
    rows = [[F(1), F(0)], [F(0), F(1)]]
    output = [F(0)] * 4
    for _ in range(r):
        output = [x+y for x, y in zip(output, cube(rows[0]))]
        rows[0] = [x+y for x, y in zip(rows[0], rows[1])]
    trace, queries, shears = [], [], []
    for op, source, raw in program:
        require(source in ("a", "b"), "unknown source")
        i = 0 if source == "a" else 1
        k = F(raw)
        require(k != 0 and dyadic(k), "nonzero dyadic event required")
        if op == "shear":
            rows[i] = [x+k*y for x, y in zip(rows[i], rows[1-i])]
            shears.append((source, k))
        elif op == "query":
            output = [x+k*y for x, y in zip(output, cube(rows[i]))]
            queries.append((source, k, rows[i][:]))
        else:
            raise ValueError("unknown operation")
        require(rows[0][0]*rows[1][1]-rows[0][1]*rows[1][0] == 1,
                "source frame is not determinant one")
        require(all(dyadic(x) for row in rows for x in row), "illegal source row")
        trace.append(deepcopy(rows))
    return output, rows, trace, queries, shears


def endpoint_ok(r, program):
    output, rows, *_ = replay(r, program)
    return output == [r, 0, 0, 0] and rows == [[1, 0], [0, 1]]


def source_inputs_ok(blobs):
    pins = json.loads((HERE / "SOURCES.json").read_text())["files"]
    return all(sha256(blobs[row["path"]]).hexdigest() == row["sha256"]
               for row in pins if row["usage"] == "input")


def main():
    pins = json.loads((HERE / "SOURCES.json").read_text())["files"]
    blobs = {row["path"]: (ROOT / row["path"]).read_bytes()
             for row in pins if row["usage"] == "input"}
    require(source_inputs_ok(blobs), "live source bytes differ from pins")
    for path in blobs:
        changed = dict(blobs); changed[path] += b"\n"
        require(not source_inputs_ok(changed), "source mutation accepted")
    old = json.loads(blobs["research/cubic-three-query-arities/CERTIFICATES.json"])
    require(24 in old["no_certificate_in_box"], "source does not leave r24 open")
    require(all(c["r"] != 24 for c in old["certificates"]), "source already has r24")
    cert = json.loads((HERE / "CERTIFICATE.json").read_text())
    r = cert["arity"]
    require(r == 24, "this certificate is scoped to arity 24")
    target = [sum(cube((1, i))[j] for i in range(r)) for j in range(4)]
    target[0] -= r
    require(target == [0, 828, 12972, 76176], "defect anchor")
    weights = solve_weights(cert["forms"], target)
    require(weights == [F(x) for x in cert["defect_weights"]], "wrong weights")
    require(all(w and dyadic(w) for w in weights), "illegal defect coefficient")
    alpha, beta = cert["forms"][0]
    require(F(beta, alpha) == F(19, 11) and not dyadic(F(beta, alpha)),
            "nonmonic direction distinction")
    # Reconstruct node 3 from discovery seeds via PR6653's node equation.
    x, y, m, s1 = F(19, 11), F(9), F(47, 3), F(276)
    require((m*(x+y)-s1-x*y)/(x+y-m) == 25, "third-node derivation")
    program = cert["repair"]
    output, rows, trace, queries, shears = replay(r, program)
    require(output == [24, 0, 0, 0] and rows == [[1, 0], [0, 1]],
            "symbolic arbitrary-input endpoint")
    require(len(queries) == 3 and len(shears) == 5, "event inventory")
    require(trace[4] == [[1, 25], [0, 1]], "dirty b restoration before reuse")
    require(queries == [("a", F(-3749, 1024), [1, 25]),
                        ("b", F(-376832), [F(-11, 256), F(-19, 256)]),
                        ("a", F(-1679, 64), [1, 9])], "named-source query bill")
    require(shears == [("a", F(1)), ("b", F(-11, 256)),
                      ("b", F(11, 256)), ("a", F(-16)), ("a", F(-9))],
            "complete shear bill")
    delta = 4*F(276)-3*F(47, 3)**2
    require(delta == F(1103, 3), "two-query invariant")
    require(isqrt(delta.denominator)**2 != delta.denominator, "square denominator")
    mutants = {}
    p = deepcopy(program); p[3][2] = "376832"; mutants["middle sign"] = p
    p = deepcopy(program); p[1][2] = "-3748/1024"; mutants["wrong weight"] = p
    p = deepcopy(program); del p[4]; mutants["lost dirty b"] = p
    p = deepcopy(program); del p[-1]; mutants["unrestored a"] = p
    p = deepcopy(program); p[2], p[3] = p[3], p[2]; mutants["premature query"] = p
    p = deepcopy(program); p[3][1] = "a"; mutants["wrong named source"] = p
    p = deepcopy(program); del p[6]; mutants["omitted query"] = p
    p = deepcopy(program); p[2][2] = "-11/128"; mutants["wrong frame"] = p
    for name, mutant in mutants.items():
        require(not endpoint_ok(r, mutant), "accepted mutation: " + name)
    require(not endpoint_ok(23, program), "wrong arity accepted")
    bad = deepcopy(program); bad[2][2] = "-11/255"
    try:
        replay(r, bad)
    except ValueError:
        pass
    else:
        raise ValueError("non-dyadic event accepted")
    print("PASS source pins and 3 source mutations; exact coefficient elimination")
    print("PASS symbolic dirty endpoint, 3 queries / 5 shears, rational lower-bound invariant")
    print("PASS 10 program/domain rejection controls")
    print("PASS_CUBIC_R24_GENERAL_FRAME")


if __name__ == "__main__":
    main()

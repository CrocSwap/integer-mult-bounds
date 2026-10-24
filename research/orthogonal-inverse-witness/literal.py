"""Execute the complete program with rational Cayley matrices and true inverses.

Prepared by Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""

from fractions import Fraction
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent / "vendor"))
from syntax import validate


def parameters(program, word, parameter):
    if validate(program).characteristic:
        raise ValueError("the orthogonal construction requires Q")
    if any(a not in program["operators"] for a in word):
        raise ValueError("unknown path label")
    if not 0 < parameter <= Fraction(1, 4):
        raise ValueError("parameter must be in (0, 1/4]")
    bands = {}
    for a in program["operators"]:
        off = [parameter / 2 if b == a else Fraction(0) for b in word]
        pivots = [Fraction(1)] * (len(word) + 1)
        for j in range(1, len(pivots)):
            pivots[j] += off[j - 1] ** 2 / pivots[j - 1]
        bands[a] = off, pivots
    return bands


def action(band, vector, direction):
    if direction not in (-1, 1):
        raise ValueError("direction must be +1 or -1")
    off, pivots = band
    n = len(vector)
    result = vector[:]
    # Form (I + direction*t*K/2) v from the old vector.
    for j, edge in enumerate(off):
        result[j] += direction * edge * vector[j + 1]
        result[j + 1] -= direction * edge * vector[j]
    # Solve (I - direction*t*K/2) x = result.
    for j in range(1, n):
        result[j] -= direction * off[j - 1] * result[j - 1] / pivots[j - 1]
    result[-1] /= pivots[-1]
    for j in range(n - 2, -1, -1):
        result[j] = (result[j] + direction * off[j] * result[j + 1]) / pivots[j]
    return result


def replay(program, word, parameter, input_index):
    bands = parameters(program, word, parameter)
    roles, n = program["roles"], len(word) + 1
    if type(input_index) is not int or not 0 <= input_index < len(roles):
        raise ValueError("invalid input role")
    endpoints = []
    for side in ("left", "right"):
        regs = {role: [Fraction(i == input_index and j == n - 1)
                       for j in range(n)] for i, role in enumerate(roles)}
        for ins in program[side]:
            dst = ins["dst"]
            if ins["op"] == "linear":
                result = [Fraction(0)] * n
                for src, scalar in ins["terms"]:
                    for j, value in enumerate(regs[src]):
                        result[j] += Fraction(scalar) * value
            else:
                src = dst if ins["op"] == "apply" else ins["src"]
                value = action(bands[ins["operator"]], regs[src], ins["direction"])
                result = value if ins["op"] == "apply" else [
                    old + Fraction(ins["coefficient"]) * new
                    for old, new in zip(regs[dst], value)]
            regs[dst] = result
        endpoints.append([regs[role] for role in roles])
    return [[a - b for a, b in zip(left, right)]
            for left, right in zip(*endpoints)]


def degree_bound(program, dimension):
    q = sum(ins["op"] != "linear" for side in ("left", "right") for ins in program[side])
    return dimension * q

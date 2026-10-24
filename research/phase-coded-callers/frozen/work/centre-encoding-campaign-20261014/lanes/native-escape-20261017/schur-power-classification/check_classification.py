"""Check the actual singular mode and the coherent-power Schur classification."""

from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
import json

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
SOURCE = BASE / "owner-review/centre-schur-singularity"
PINS = {
    "SINGULAR-WITNESS.md": "bb3685f88876c941d2340a4e22f5622d844fb78ed33b0588017af40ad0e91368",
    "SINGULAR-WITNESS.json": "fda1f40ef3f9f80af736570394260c21abbf737c31fe3228ca6883bd29812401",
    "check_singular_witness.py": "8ddb01debc65ae9d7c401a868f3c25cf9e86d3b0fceb79e817aff916649b0641",
}


def need(ok, label):
    if not ok:
        raise ValueError(label)


def read(path, pin):
    raw = path.read_bytes()
    need(sha256(raw).hexdigest() == pin, "Pinned source: " + str(path))
    return json.loads(raw)


for name, pin in PINS.items():
    need(sha256((SOURCE / name).read_bytes()).hexdigest() == pin, "Frozen singular witness")
spectral = read(BASE / "owner-review/centre-schur-probe/SCHUR-PROBE.json",
                "ebff70f4ff3d28c345080a4d7b1d90cd952a6208b7f6449037b96dbf3531c024")
review = read(BASE / "schur-review/REVIEW.json", "574007db390991f2eeb058e22d733bef4238a739e545318eeff229909a2bd36b")
need(review["status"] == "PASS_INDEPENDENT_SCHUR_REVIEW", "Independent all-width inverse proof")
original = {}
for name in ("interface", "phases"):
    pin = spectral["source_pins"][name]
    original[name] = read(Path(pin["path"]), pin["sha256"])
R = [[F(row.get(str(p), 0)) for p in range(112)] for row in original["interface"]["R"]]
q = [row["q"] for row in original["phases"]["recipes"]]
A = [0, 7, 20, 27, 36, 46, 57, 111]
U = [p for p in range(112) if p not in A]
B = [[sum(row[a] * row[p] for row in R) / 4 for p in U] for a in A]
need(all(sum(B[i][p] * B[j][p] for p in range(104)) == 13 * int(i == j) for i in range(8) for j in range(8)), "Actual BD=13I")
characters = (1, 2, 3, 6, 6)
for label in range(512):
    phase = sum((label & character).bit_count() % 2 for character in characters) % 4
    x, y, z = [(label >> j) & 1 for j in range(3)]
    need(phase == (2 * (x * y + x + z)) % 4, "Exact width-five quadratic phase")
    need(phase == 3 * phase % 4, "The same witness has inverse-line orientation")
signs = [1 if sum((q[p] & character).bit_count() % 2 for character in characters) % 4 == 0 else -1 for p in U]
S = [[sum(B[i][p] * B[j][p] * signs[p] for p in range(104)) for j in range(8)] for i in range(8)]
null = [0, 0, 1, 0, -1, 1, 0, 1]
need(all(sum(coefficient * value for coefficient, value in zip(row, null)) == 0 for row in S), "Exact nonzero null vector")


def determinant(matrix):
    matrix = [row[:] for row in matrix]
    result = F(1)
    for j in range(len(matrix)):
        pivot = next((i for i in range(j, len(matrix)) if matrix[i][j]), None)
        if pivot is None:
            return F(0)
        if pivot != j:
            matrix[j], matrix[pivot] = matrix[pivot], matrix[j]
            result = -result
        value = matrix[j][j]
        result *= value
        matrix[j] = [entry / value for entry in matrix[j]]
        for i in range(j + 1, len(matrix)):
            factor = matrix[i][j]
            matrix[i] = [entry - factor * above for entry, above in zip(matrix[i], matrix[j])]
    return result


minor = determinant([row[:7] for row in S[:7]])
need(minor == -73 and determinant(S) == 0, "Exact rank seven")
ordinary = [sum(B[i][p] * null[i] for i in range(8)) for p in range(104)]
need(sum(value**2 for value in ordinary) == 52, "The lost ordinary image is nonzero")
need(all(sum(B[i][p] * signs[p] * ordinary[p] for p in range(104)) == 0 for i in range(8)), "The line image lies in the query kernel")
need(signs.count(1) == 54 and signs.count(-1) == 50, "Actual phase partition")
result = dict(status="PASS_COHERENT_POWER_SCHUR_CLASSIFICATION", source_pins=PINS,
              characters=list(characters), selected_ports=A, null_vector=null,
              singular_matrix=[[str(value) for value in row] for row in S],
              leading_minor=str(minor), rank=7, ordinary_image_squared_norm="52",
              classification_mod4={"0": "13I at every width", "1": "Singular at every width at least five",
                                   "2": "All-width invertible translation operator with reviewed finite kernel",
                                   "3": "Singular at every width at least five"},
              minimum_singular_width_claimed=False, supplier_decoder_claimed=False,
              checker_sha256=sha256(Path(__file__).read_bytes()).hexdigest())
(HERE / "CHECKS.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
print(result["status"])

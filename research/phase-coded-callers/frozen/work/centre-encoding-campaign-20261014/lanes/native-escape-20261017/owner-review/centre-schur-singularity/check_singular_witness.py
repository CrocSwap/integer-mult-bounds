"""Check a width-five Schur null vector directly from the source columns."""

from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
import json
import shutil

HERE = Path(__file__).resolve().parent
PROBE_PIN = "ebff70f4ff3d28c345080a4d7b1d90cd952a6208b7f6449037b96dbf3531c024"
MINOR_PIN = "8839f7aa1b8bb273e747b9a2ed21de2fd5f8e185ad92cae7a9d0cfe9f85f9745"
A = [0, 7, 20, 27, 36, 46, 57, 111]
U = [p for p in range(112) if p not in A]
CHARACTERS = [1, 2, 3, 6, 6]
VECTOR = [0, 0, 1, 0, -1, 1, 0, 1]
TWICE_S = [
    [1, -1, -4, 7, -4, 0, -5, 0],
    [-1, 5, 0, -5, -4, -4, 3, 0],
    [-4, 0, -3, 4, -1, 3, 0, -1],
    [7, -5, 4, 1, 0, -4, -5, 0],
    [-4, -4, -1, 0, 1, 3, 0, -1],
    [0, -4, 3, -4, 3, 1, 0, -1],
    [-5, 3, 0, -5, 0, 0, 1, 0],
    [0, 0, -1, 0, -1, -1, 0, 1],
]


def need(ok, label):
    if not ok:
        raise ValueError(label)


def pinned(path, pin):
    raw = path.read_bytes()
    need(sha256(raw).hexdigest() == pin, "Source pin: " + str(path))
    return json.loads(raw)


def determinant(matrix):
    matrix = [[F(c) for c in row] for row in matrix]
    value = F(1)
    n = len(matrix)
    for j in range(n):
        pivot = next((i for i in range(j, n) if matrix[i][j]), None)
        if pivot is None:
            return F(0)
        if pivot != j:
            matrix[j], matrix[pivot] = matrix[pivot], matrix[j]
            value = -value
        divisor = matrix[j][j]
        value *= divisor
        for i in range(j + 1, n):
            coefficient = matrix[i][j] / divisor
            for k in range(j + 1, n):
                matrix[i][k] -= coefficient * matrix[j][k]
    return value


need(shutil.disk_usage(HERE).free >= 3 * 2**30, "At least 3 GiB free")
probe = pinned(HERE.parent / "centre-schur-probe/SCHUR-PROBE.json", PROBE_PIN)
minor = pinned(HERE.parent / "minor-collective-service/MINOR-COLLECTIVE-SERVICE.json", MINOR_PIN)
need(probe["source_pins"] == minor["source_pins"], "Retained source pins")
sources = {}
for key, pin in probe["source_pins"].items():
    raw = Path(pin["path"]).read_bytes()
    need(sha256(raw).hexdigest() == pin["sha256"], "Current source: " + key)
    if key in ("interface", "phases"):
        sources[key] = json.loads(raw)
rows = [{int(p): int(c) for p, c in row.items()} for row in sources["interface"]["R"]]
q = [item["q"] for item in sources["phases"]["recipes"]]
columns = {}
for p in U:
    numerator = [sum(row.get(a, 0) * row.get(p, 0) for row in rows) for a in A]
    need(all(c % 2 == 0 for c in numerator), "Integral twice-normalized source column")
    columns[p] = [c // 2 for c in numerator]
need(all(sum(v[i] * v[j] for v in columns.values()) == 52 * (i == j)
         for i in range(8) for j in range(8)), "B D = 13 I")
for label in range(512):
    phase = sum((label & chi).bit_count() % 2 for chi in CHARACTERS) % 4
    target = 2 * (((label & 1) * ((label >> 1) & 1) + (label & 5).bit_count()) % 2)
    need(phase == target, "Exact quadratic phase identity")
real, imaginary = [[0] * 8 for _ in range(8)], [[0] * 8 for _ in range(8)]
phase_counts = {0: 0, 2: 0}
for p, column in columns.items():
    phase = sum((q[p] & chi).bit_count() % 2 for chi in CHARACTERS) % 4
    real_unit, imaginary_unit = ((1, 0), (0, 1), (-1, 0), (0, -1))[phase]
    need(phase in phase_counts, "Real phase on each actual ordinary port")
    phase_counts[phase] += 1
    for i in range(8):
        for j in range(8):
            real[i][j] += real_unit * column[i] * column[j]
            imaginary[i][j] += imaginary_unit * column[i] * column[j]
need(not any(c for row in imaginary for c in row), "Zero imaginary part")
need(real == [[2 * c for c in row] for row in TWICE_S], "Direct source Gaussian matrix")
need(any(VECTOR) and all(sum(c * v for c, v in zip(row, VECTOR)) == 0 for row in real), "Exact nonzero null vector")
minor_determinant = determinant([[F(c, 2) for c in row[:7]] for row in TWICE_S[:7]])
need(minor_determinant == -73, "Exact rank-seven minor")
ordinary = [F(sum(c * v for c, v in zip(column, VECTOR)), 2) for column in columns.values()]
need(sum(c * c for c in ordinary) == 52, "The ordinary source mode is nonzero")
for key, pin in probe["source_pins"].items():
    need(sha256(Path(pin["path"]).read_bytes()).hexdigest() == pin["sha256"], "Source unchanged: " + key)
receipt = dict(status="PASS_DIRECT_SOURCE_SCHUR_SINGULAR_WITNESS",
               checker_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
               source_probe_receipt_sha256=PROBE_PIN, source_minor_receipt_sha256=MINOR_PIN,
               source_pins=probe["source_pins"], selected_ports=A, ordinary_ports=U,
               width=5, characters=CHARACTERS, spectator_character_coordinates=list(range(9, 73)),
               phase="2*(q0*q1+q0+q2) modulo 4", label_phase_checks=512,
               actual_port_phase_counts={str(k): v for k, v in phase_counts.items()},
               twice_S=TWICE_S, null_vector=VECTOR, rank=7,
               leading_seven_by_seven_minor_determinant=str(minor_determinant),
               ordinary_mode_squared_norm="52", ordinary_mode_support=sum(c != 0 for c in ordinary),
               padding="Append zero characters. The same Schur matrix occurs at every width at least five.",
               scope="S=B Q_U D is singular at the stated mode. This rules out an inverse on arbitrary centres at widths at least five. It is not a minimum-width claim or a native lower bound.")
(HERE / "SINGULAR-WITNESS.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
print(receipt["status"])
print(json.dumps(dict(characters=CHARACTERS, rank=7, null_vector=VECTOR, minor_determinant=str(minor_determinant)), sort_keys=True))

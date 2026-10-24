"""Check raw selected subsets and the dyadic borrowed block."""

from copy import deepcopy
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
import gzip
import importlib.util
import json

HERE = Path(__file__).resolve().parent
UTILITY = HERE / "emit_raw_selected_backward.py"
UTILITY_PIN = "ed9b91708d16226a51fb0f76e3b0c9392553cc316da7c24b9cc1fe21759d6bc0"
if sha256(UTILITY.read_bytes()).hexdigest() != UTILITY_PIN:
    raise RuntimeError("Ordered operator utility pin")
spec = importlib.util.spec_from_file_location("raw_backward", UTILITY)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
need, plus, line = m.need, m.plus, m.line
MINORS = [
    [0, 7, 20, 27, 36, 46, 57, 111],
    [21, 37, 47, 76, 81, 87, 92, 110],
    [1, 6, 22, 28, 33, 49, 58, 109],
    [2, 9, 14, 19, 88, 95, 101, 106],
    [3, 8, 15, 18, 89, 94, 102, 105],
    [4, 11, 12, 17, 90, 97, 99, 104],
    [5, 10, 13, 16, 91, 96, 100, 103],
    [23, 30, 60, 75, 82, 85, 98, 108],
    [24, 34, 50, 74, 83, 86, 93, 107],
    [25, 35, 41, 48, 52, 59, 61, 84],
    [26, 38, 43, 53, 54, 68, 71, 79],
    [29, 32, 40, 45, 55, 66, 73, 80],
    [31, 39, 42, 63, 64, 67, 72, 78],
    [44, 51, 56, 62, 65, 69, 70, 77],
]
need(sorted(p for minor in MINORS for p in minor) == list(range(112)), "The fourteen minors partition all ports")
core = m.read(m.LANES / "circuit-interface/CENTRE-FREE-PROGRAMS.json.gz", m.PINS["core"], True)["backward"]
interface = m.read(m.LANES / "circuit-interface/INTERFACE.json", m.PINS["interface"])
word_raw = (m.REPO / "work/five-pr-sprint-20261013/lanes/centre-sharing/CANONICAL-WORD.json.gz").read_bytes()
need(sha256(word_raw).hexdigest() == m.PINS["word"], "Canonical word pin")
word = json.loads(gzip.decompress(word_raw))
R = [[F(row.get(str(p), 0)) for p in range(112)] for row in interface["R"]]
K = [[R[i][p] / 4 for i in range(8)] for p in range(112)]
KR = [[sum(K[p][i] * R[i][q] for i in range(8)) for q in range(112)] for p in range(112)]
J = [[F(p == q) - KR[p][q] for q in range(112)] for p in range(112)]
for minor in MINORS:
    need(all(sum(R[i][p] * K[p][j] for p in minor) == (i == j) for i in range(8) for j in range(8)), "Each minor has R_A K_A=I")
identity = [{(p, ()): F(1)} for p in range(712)]


def exchange(selected):
    out = []
    for p in selected:
        out += [m.raw_scalar("add", p, 112 + p, 1), m.raw_scalar("add", 112 + p, p, -1),
                m.raw_scalar("add", p, 112 + p, 1), m.raw_scalar("scale", 112 + p, coefficient=-1)]
    return out


def replay(selected, tail=()):
    physical = deepcopy(identity)
    for p in range(112):
        physical[p] = line(physical[p], p, 1)
    physical = m.boundary(exchange(selected), physical)
    logical = deepcopy(physical)
    for p in range(112):
        logical[p] = line(logical[p], p, -1)
    logical = m.core_replay(core, logical, word)
    logical = m.boundary(tail, logical)
    physical = deepcopy(logical)
    for p in range(112):
        physical[112 + p] = line(physical[112 + p], p, -1)
    return logical, physical


def target(selected):
    selected = set(selected)
    px = [line(identity[112 + p], p, -1) if p in selected else identity[p] for p in range(112)]
    py = [line(identity[p], p, 1) if p in selected else identity[112 + p] for p in range(112)]
    out = deepcopy(identity)
    out[704:] = [{} for _ in range(8)]
    for p in range(112):
        out[p] = dict(px[p])
        for q in range(112):
            if J[p][q]:
                plus(out[p], py[q], -J[p][q])
        out[112 + p] = dict(py[p])
    return out


def h_tape(k, inverse):
    need(k < 14, "A nonempty complement")
    d = F(k - 13)
    need(d and abs(d.numerator) & (abs(d.numerator) - 1) == 0, "A dyadic unit eigenvalue")
    selected = set(p for minor in MINORS[:k] for p in minor)
    pivot = MINORS[k]
    rest = [p for p in range(112) if p not in selected and p not in pivot]
    upper = [m.raw_scalar("add", a, w, KR[a][w]) for a in pivot for w in rest if KR[a][w]]
    lower = [m.raw_scalar("add", w, a, KR[w][a] if inverse else -KR[w][a])
             for w in rest for a in pivot if KR[w][a]]
    scales = [m.raw_scalar("scale", a, coefficient=1 / d if inverse else d) for a in pivot]
    unupper = [m.raw_scalar("add", a, w, -KR[a][w]) for a in pivot for w in rest if KR[a][w]]
    return upper + (scales + lower if inverse else lower + scales) + unupper


def h_apply(row, ordinary):
    out = deepcopy(row)
    for p in ordinary:
        for q in ordinary:
            if KR[p][q]:
                plus(out[p], row[q], -KR[p][q])
    return out


cases = []
for k in range(1, 15):
    selected = sorted(p for minor in MINORS[:k] for p in minor)
    ordinary = sorted(set(range(112)) - set(selected))
    mu, d = 14 - k, k - 13
    need(all(sum(R[i][p] * K[p][j] for p in ordinary) == mu * (i == j) for i in range(8) for j in range(8)), "Complement centre Gram")
    actual, physical = replay(selected)
    need(actual == target(selected), "All 712 columns of the raw subset map")
    need(all(physical[112 + p] == identity[p] for p in selected), "Each selected Y holds physical F original X")
    need(actual[224:704] == identity[224:704] and actual[704:] == [{}] * 8, "Inherited helper values and private zero")
    unit = bool(d) and abs(d) & (abs(d) - 1) == 0
    row = dict(k=k, selected_fields=len(selected), ordinary_fields=len(ordinary), centre_eigenvalue=d,
               dyadic_borrowed_unit=unit, swap_scalar=m.scalar_price(exchange(selected)))
    if unit and k < 14:
        forward, inverse = h_tape(k, False), h_tape(k, True)
        h_actual = m.boundary(forward, identity)
        need(h_actual == h_apply(identity, ordinary), "No-scratch scalar H factorization")
        need(m.boundary(inverse, h_actual) == identity, "H inverse after H")
        need(m.boundary(forward, m.boundary(inverse, identity)) == identity, "H after H inverse")
        need(F(1, d) - 1 - F(mu, d) == 0, "Woodbury coefficient identity")
        row.update(H_scalar=m.scalar_price(forward), H_inverse_scalar=m.scalar_price(inverse))
    elif k == 14:
        need(not ordinary, "The empty complement is a unit")
    elif not d:
        need(all(J[p][q] == 0 for p in ordinary for q in ordinary), "The thirteenth complement block is zero")
        row["rational_nullity_channels"] = 8
    else:
        prime = next(p for p in (3, 5, 7, 11, 13) if d % p == 0)
        def mod(c):
            return c.numerator * pow(c.denominator, -1, prime) % prime
        need(all(sum(mod(J[p][q]) * mod(K[q][j]) for q in ordinary) % prime == 0
                 for p in ordinary for j in range(8)), "Eight exact odd-prime kernel channels")
        row.update(odd_prime=prime, modular_nullity_channels=8)
    cases.append(row)
    print("checked k=" + str(k), flush=True)
need([c["k"] for c in cases if c["dyadic_borrowed_unit"]] == [5, 9, 11, 12, 14], "Exact admitted k values")

k = 5
selected = sorted(p for minor in MINORS[:k] for p in minor)
ordinary = sorted(set(range(112)) - set(selected))
normal = h_tape(k, True)
upper = [m.raw_scalar("add", p, q, KR[p][q]) for p in selected for q in ordinary if KR[p][q]]
actual, physical = replay(selected, normal + upper)
centre = []
for i in range(8):
    row = {}
    for p in range(112):
        source = line(identity[p], p, 1) if p in selected else identity[p]
        plus(row, source, R[i][p])
    centre.append(row)
expected = deepcopy(identity)
expected[704:] = [{} for _ in range(8)]
for p in range(112):
    if p in selected:
        expected[p] = line(identity[112 + p], p, -1)
        plus(expected[p], line(identity[p], p, 1), -1)
        expected[112 + p] = line(identity[p], p, 1)
    else:
        expected[p] = dict(identity[p])
        plus(expected[p], identity[112 + p], -1)
    for i in range(8):
        plus(expected[p], centre[i], -K[p][i] / 8)
need(actual == expected, "Five-minor diagonal borrowed block on every operator column")
need(all(physical[112 + p] == identity[p] for p in selected), "Forty physical selected outputs remain productive")
pivot = MINORS[5]
rest = [p for p in ordinary if p not in pivot]
cut = sum(bool(KR[a][w]) for a in pivot for w in rest) + len(pivot)
fused_scatter = [m.raw_scalar("add", p, a, KR[p][a]) for p in selected for a in pivot if KR[p][a]]
fused = normal[:cut] + fused_scatter + normal[cut:]
need(replay(selected, fused)[0] == expected, "The pivot query gives the same selected upper map")
controls = dict(
    omit_H_inverse=replay(selected, upper)[0] != expected,
    omit_upper=replay(selected, normal)[0] != expected,
    wrong_selected_count=target(sorted(p for minor in MINORS[:4] for p in minor)) != target(selected),
)
need(all(controls.values()), "Negative controls")
payload = dict(schema="raw-five-minor-backward-v1", source_pins=m.PINS, selected=selected,
               pivot=MINORS[5], raw_exchange=exchange(selected), retained_core=core,
               full_XU_H_inverse=normal, optional_full_XS_upper=upper,
               fused_diagonal_borrowed_post=fused,
               minors=MINORS, added_native_lines=0)
encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
(HERE / "RAW-FIVE-MINOR-PROGRAM.json.gz").write_bytes(gzip.compress(encoded, mtime=0))
scalar_parts = dict(core=202138, raw_exchange=m.scalar_price(exchange(selected)),
                    H_inverse=m.scalar_price(normal), optional_upper=m.scalar_price(upper),
                    fused_upper_increment=m.scalar_price(fused_scatter), fused_post=m.scalar_price(fused))
receipt = dict(status="PASS_RAW_MINOR_SUBSET_UNITS", checker_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
               utility_sha256=UTILITY_PIN, source_pins=m.PINS, minors=MINORS, cases=cases,
               all_formal_columns_per_local=712, raw_local_variants_checked=14,
               inherited_logical_helpers=480, owned_private_zero=8, payload_sha256=sha256(encoded).hexdigest(),
               five_minor_scalar_parts=scalar_parts, native_mass=5522, added_native_lines=0, controls=controls,
               scope="Actual minor partition, literal local raw swaps and core, exact dyadic scalar normal forms, and odd-prime channel obstruction. Full physical core proof is inherited.",
               open=["Independent review", "Global controller and final decoder", "Actual owner phases and complete recursive invoice"])
(HERE / "RAW-MINOR-SUBSETS.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
print(receipt["status"])
print(json.dumps({"five_minor_scalar_parts":scalar_parts,"payload_sha256":receipt["payload_sha256"]},sort_keys=True))

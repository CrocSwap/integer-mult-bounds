"""Emit and check centre translation shears with one owned field."""

from collections import Counter, defaultdict
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
import gzip
import json
import shutil

HERE = Path(__file__).resolve().parent
PROBE_PIN = "ebff70f4ff3d28c345080a4d7b1d90cd952a6208b7f6449037b96dbf3531c024"
MINOR_PIN = "8839f7aa1b8bb273e747b9a2ed21de2fd5f8e185ad92cae7a9d0cfe9f85f9745"
A = [0, 7, 20, 27, 36, 46, 57, 111]
U = [p for p in range(112) if p not in A]
C0 = 16
BORROWED = list(range(17, 25))
UNIT = [1 << i for i in range(73)]


def need(ok, label):
    if not ok:
        raise ValueError(label)


def pinned(path, pin):
    raw = path.read_bytes()
    need(sha256(raw).hexdigest() == pin, "Source pin: " + str(path))
    return json.loads(gzip.decompress(raw) if path.suffix == ".gz" else raw)


def initial():
    return [{(i, 0): F(1)} for i in range(25)]


def add(row, source, coefficient):
    norm_change = F(0)
    for key, value in source.items():
        old = row.get(key, F(0))
        new = old + coefficient * value
        norm_change += abs(new) - abs(old)
        if new:
            row[key] = new
        else:
            row.pop(key, None)
    return norm_change


def run(state, word):
    norms = [sum(map(abs, row.values())) for row in state]
    maximum = max(norms)
    counts = Counter()
    for gate in word:
        kind, target = gate[:2]
        need(target == C0 or 8 <= target < 16, "Only target centres and C0 can change")
        if kind == "ADD":
            source, coefficient = gate[2], F(gate[3])
            need(source != target and abs(coefficient) in (1, F(1, 2)), "Unit or half ADD")
            norms[target] += add(state[target], state[source], coefficient)
            counts["unit_adds" if abs(coefficient) == 1 else "half_adds"] += 1
            counts["scalar_primitives"] += 8 if abs(coefficient) == 1 else 10
        elif kind == "COPY":
            need(target == C0 and gate[2] < 8, "Owned source copy")
            state[target] = dict(state[gate[2]])
            norms[target] = norms[gate[2]]
            counts["scalar_primitives"] += 2
        elif kind == "CLEAR":
            need(target == C0, "Only the owned field can be cleared")
            state[target], norms[target] = {}, F(0)
            counts["scalar_primitives"] += 2
        elif kind == "SCALE2":
            need(target == C0 and gate[2] in (-1, 1), "One binary scale on C0")
            coefficient = F(2) ** gate[2]
            state[target] = {key: coefficient * value for key, value in state[target].items()}
            norms[target] *= coefficient
            counts["scalar_primitives"] += 2
            counts["double" if gate[2] == 1 else "halve"] += 1
        elif kind == "DIVIDE_ODD":
            need(target == C0 and gate[2] == 2145, "One explicit fixed odd divisor")
            state[target] = {key: value / 2145 for key, value in state[target].items()}
            norms[target] /= 2145
            counts["real_odd_division_scans"] += 2
        else:
            need(kind == "TRANSLATE" and target == C0 and 0 < gate[2] < 512, "Nine-coordinate translation on C0")
            state[target] = {(origin, delta ^ gate[2]): value for (origin, delta), value in state[target].items()}
            counts["translation_maps"] += 1
        counts[kind] += 1
        maximum = max(maximum, norms[target])
    need(not state[C0], "Owned output is zero")
    need(all(state[p] == {(p, 0): F(1)} for p in list(range(8)) + BORROWED), "Source and borrowed fields are unchanged")
    return dict(counts), str(maximum)


def gate_add(target, source, coefficient):
    return ["ADD", target, source, str(coefficient)]


def forward_word(B, q):
    word = [["CLEAR", C0]]
    for p in U:
        for j, coefficient in B[p].items():
            word.append(gate_add(C0, j, coefficient))
        word.append(["TRANSLATE", C0, q[p]])
        for i, coefficient in B[p].items():
            word.append(gate_add(8 + i, C0, coefficient))
        word.append(["CLEAR", C0])
    return word


def inverse_word(groups, schedule):
    word = []
    for source in range(8):
        word += [["COPY", C0, source], ["DIVIDE_ODD", C0, 2145],
                 ["SCALE2", C0, -1], ["SCALE2", C0, -1]]
        current_shift = 0
        shifts = sorted(delta for j, delta in groups if j == source)
        if schedule == "few_maps":
            for position, delta in enumerate(shifts):
                word.append(["TRANSLATE", C0, current_shift ^ delta])
                current_shift = delta
                coefficients = groups[source, delta]
                last_bit = max(abs(c).bit_length() - 1 for c in coefficients.values())
                for bit in range(last_bit + 1):
                    for target, coefficient in sorted(coefficients.items()):
                        if abs(coefficient) >> bit & 1:
                            word.append(gate_add(8 + target, C0, 1 if coefficient > 0 else -1))
                    if bit < last_bit:
                        word.append(["SCALE2", C0, 1])
                if position + 1 < len(shifts):
                    word += [["SCALE2", C0, -1] for _ in range(last_bit)]
        else:
            need(schedule == "few_scalars", "Known schedule")
            last_bit = max(abs(c).bit_length() - 1 for delta in shifts for c in groups[source, delta].values())
            for bit in range(last_bit + 1):
                for delta in shifts:
                    coefficients = groups[source, delta]
                    if not any(abs(c) >> bit & 1 for c in coefficients.values()):
                        continue
                    offset = current_shift ^ delta
                    if offset:
                        word.append(["TRANSLATE", C0, offset])
                    current_shift = delta
                    for target, coefficient in sorted(coefficients.items()):
                        if abs(coefficient) >> bit & 1:
                            word.append(gate_add(8 + target, C0, 1 if coefficient > 0 else -1))
                if bit < last_bit:
                    word.append(["SCALE2", C0, 1])
        word.append(["CLEAR", C0])
    return word


def negative(word):
    return [[*gate[:3], str(-F(gate[3]))] if gate[0] == "ADD" and 8 <= gate[1] < 16 else list(gate) for gate in word]


def expected(entries, sign=1):
    result = initial()
    result[C0] = {}
    for delta, target, source, coefficient in entries:
        add(result[8 + target], {(source, delta): F(coefficient)}, F(sign))
    return result


def exchange(word_T, word_inverse):
    def swap_banks(word):
        result = []
        for gate in word:
            gate = list(gate)
            gate[1] = gate[1] ^ 8 if gate[1] < 16 else gate[1]
            if gate[0] in ("ADD", "COPY"):
                gate[2] = gate[2] ^ 8 if gate[2] < 16 else gate[2]
            result.append(gate)
        return result
    return swap_banks(word_T) + negative(word_inverse) + swap_banks(word_T)


def invoice(word):
    counts = Counter()
    for gate in word:
        kind = gate[0]
        counts[kind] += 1
        if kind == "ADD":
            counts["scalar_primitives"] += 8 if abs(F(gate[3])) == 1 else 10
        elif kind in ("COPY", "CLEAR", "SCALE2"):
            counts["scalar_primitives"] += 2
        elif kind == "DIVIDE_ODD":
            counts["real_odd_division_scans"] += 2
        else:
            need(kind == "TRANSLATE", "Literal instruction")
            counts["translation_maps"] += 1
    return dict(counts)


def act(columns, vector):
    result = 0
    while vector:
        bit = vector & -vector
        result ^= columns[bit.bit_length() - 1]
        vector ^= bit
    return result


def transpose(columns):
    return [sum(((v >> i) & 1) << j for j, v in enumerate(columns)) for i in range(len(columns))]


need(shutil.disk_usage(HERE).free >= 3 * 2**30, "At least 3 GiB free")
probe = pinned(HERE / "SCHUR-PROBE.json", PROBE_PIN)
minor = pinned(HERE.parent / "minor-collective-service/MINOR-COLLECTIVE-SERVICE.json", MINOR_PIN)
need(probe["source_pins"] == minor["source_pins"], "Same five source pins")
sources = {key: pinned(Path(pin["path"]), pin["sha256"]) for key, pin in probe["source_pins"].items()}
rows = [{int(p): F(c) for p, c in row.items()} for row in sources["interface"]["R"]]
q = [r["q"] for r in sources["phases"]["recipes"]]
B = {p: {j: sum(row.get(a, 0) * row.get(p, 0) for row in rows) / 4 for j, a in enumerate(A)} for p in U}
B = {p: {j: c for j, c in row.items() if c} for p, row in B.items()}
need(all(len(row) == 4 and all(abs(c) == F(1, 2) for c in row.values()) for row in B.values()), "Actual graph columns")
groups = defaultdict(dict)
for delta, target, source, coefficient in probe["kernels"]["inverse"]["entries"]:
    integer = 8580 * F(coefficient)
    need(integer.denominator == 1, "Exact integer kernel numerator")
    groups[source, delta][target] = integer.numerator
need(len(groups) == 2048, "All source-shift groups")
positive = {"T": forward_word(B, q)}
positive.update({name: inverse_word(groups, name) for name in ("few_maps", "few_scalars")})
words, results = {}, {}
identity = initial()
identity[C0] = {}
for name, word in positive.items():
    kernel = probe["kernels"]["translation" if name == "T" else "inverse"]["entries"]
    for sign, suffix in ((1, "plus"), (-1, "minus")):
        label = name + "_" + suffix
        actual_word = word if sign == 1 else negative(word)
        words[label] = actual_word
        state = initial()
        counts, maximum = run(state, actual_word)
        need(state == expected(kernel, sign), "Exact kernel service: " + label)
        need(all(counts[k] == value for k, value in invoice(actual_word).items()), "Independent instruction invoice")
        results[label] = dict(counts=counts, maximum_intermediate_row_one_norm=maximum)
    for first, second in ((word, negative(word)), (negative(word), word)):
        state = initial()
        run(state, first)
        run(state, second)
        need(state == identity, "Both shear inverse orders: " + name)
need(results["T_plus"]["counts"]["scalar_primitives"] == 8530, "Forward scalar invoice")
need(results["few_maps_plus"]["counts"]["scalar_primitives"] == 166912, "Few-map scalar invoice")
need(results["few_scalars_plus"]["counts"]["scalar_primitives"] == 114528, "Few-scalar invoice")
need(results["few_maps_plus"]["counts"]["translation_maps"] == 2048, "Few-map translation invoice")
need(results["few_scalars_plus"]["counts"]["translation_maps"] == 8944, "Few-scalar translation invoice")
for name in ("few_maps", "few_scalars"):
    for sign, suffix in ((1, "plus"), (-1, "minus")):
        label = "exchange_" + name + "_" + suffix
        words[label] = exchange(positive["T"] if sign == 1 else negative(positive["T"]),
                                positive[name] if sign == 1 else negative(positive[name]))
        results[label] = dict(counts=invoice(words[label]), maximum_intermediate_row_one_norm_upper_bound="472511/715")

# Check the composition on formal operator symbols. The pinned kernel proof gives T V = V T = I.
def operator_product(a, b):
    out = [[defaultdict(F) for _ in range(2)] for _ in range(2)]
    for i in range(2):
        for j in range(2):
            for k in range(2):
                for left, c in a[i][k].items():
                    for right, d in b[k][j].items():
                        out[i][j][left + right] += c * d
    return [[{k: v for k, v in cell.items() if v} for cell in row] for row in out]


unit, zero = {0: F(1)}, {}
identity2 = [[unit, zero], [zero, unit]]
upper = [[unit, {1: F(1)}], [zero, unit]]
lower = [[unit, zero], [{-1: F(-1)}, unit]]
J = operator_product(upper, operator_product(lower, upper))
need(J == [[zero, {1: F(1)}], [{-1: F(-1)}, zero]], "Exact coded exchange")
minus_J = [[{k: -v for k, v in cell.items()} for cell in row] for row in J]
need(operator_product(J, minus_J) == operator_product(minus_J, J) == identity2, "Both exchange inverse orders")
need(operator_product(operator_product(J, J), operator_product(J, J)) == identity2, "Fourth power")

views = [v for v in sources["views"]["views"] if v["side"] == "X" and v["port"] in A]
need({(v["stage"], v["port"]) for v in views} == {(s, p) for s in range(1, 9) for p in A}, "All selected completed views")
for view in views:
    rho, delta = view["route_columns"], view["translation_after_route"]
    rt = transpose(rho)
    need([act(rho, x) for x in rho] == UNIT and rho == rt, "Actual orthogonal involution")
    need(act(rho, delta) == view["translation_before_route"], "Exact view order")
    linear = [(v.bit_count() + 2 * ((delta >> i) & 1) - 1) % 4 for i, v in enumerate(rt)]
    quadratic = [(-2 * (a & b).bit_count()) % 4 for i, a in enumerate(rt) for b in rt[i + 1:]]
    need(not any(linear + quadratic), "FULL phase endpoint")
    need(any((v.bit_count() - 1) % 4 for v in rt), "Translation is necessary")
wrappers = {}
for stage in range(1, 9):
    enter = [["VIEW", row, stage, A[row % 8], False] for row in range(16)]
    leave = [["VIEW", row, stage, A[row % 8], True] for row in reversed(range(16))]
    wrappers[str(stage)] = dict(enter=enter, leave=leave)

controls = {}
for label, changed in (
    ("omit_odd_division", [g for g in positive["few_scalars"] if g[0] != "DIVIDE_ODD"]),
    ("omit_translations", [g for g in positive["few_maps"] if g[0] != "TRANSLATE"]),
    ("omit_binary_halves", [g for g in positive["few_scalars"] if g[0] != "SCALE2" or g[2] != -1]),
):
    state = initial()
    run(state, changed)
    need(state != expected(probe["kernels"]["inverse"]["entries"]), "Control must fail: " + label)
    controls[label] = True

payload = dict(schema="one-owned-centre-translation-service-v1", selected_ports=A,
               rows=dict(source=list(range(8)), target=list(range(8, 16)), owned=C0, borrowed=BORROWED),
               bodies=words, stage_wrappers=wrappers, completed_views=views,
               assembly="For a stage and body, concatenate enter, body, and leave. No instruction is omitted.",
               view_order="Forward: route, then translation. Inverse: undo translation, then inverse route.",
               translation_rule="Repeat the nine-bit shift in every tensor copy; the other coordinates are unchanged.",
               odd_division_contract="Exact rational division on the explicit 2145 odd grid, charged as two real scans.")
raw = (json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n").encode()
program_path = HERE / "TRANSLATION-SERVICE-PROGRAMS.json.gz"
program_path.write_bytes(gzip.compress(raw, mtime=0))
for key, pin in probe["source_pins"].items():
    need(sha256(Path(pin["path"]).read_bytes()).hexdigest() == pin["sha256"], "Source unchanged: " + key)
need(sha256((HERE / "SCHUR-PROBE.json").read_bytes()).hexdigest() == PROBE_PIN, "Frozen probe unchanged")
receipt = dict(status="PASS_ONE_OWNED_TRANSLATION_SERVICE", cases=results, controls=controls,
               checker_sha256=sha256(Path(__file__).read_bytes()).hexdigest(), probe_receipt_sha256=PROBE_PIN,
               source_minor_receipt_sha256=MINOR_PIN, source_pins=probe["source_pins"],
               payload_raw_sha256=sha256(raw).hexdigest(), payload_compressed_sha256=sha256(program_path.read_bytes()).hexdigest(),
               arbitrary_live_columns=16, arbitrary_owned_input_columns=1, arbitrary_borrowed_columns=8,
               owned_zero_outputs=True, completed_phase_views_checked=64, completed_view_maps_per_call=32,
               rank_one_children=0, native_wrapper_maps=0, shear_inverse_orders_checked=6,
               exchange_inverse_orders_checked=2, exchange_power=4,
               inverse_kernel_unit_adds=14288, odd_divisor=2145, inverse_real_odd_division_scans=16,
               maximum_odd_denominator_height_increase_per_shear_or_exchange=1,
               exchange_proof="Exact checked shear bodies compose in the Laurent ring with T T^-1 = T^-1 T = I from the pinned all-width kernel proof.",
               scope="Local centre services on two existing FULL selected banks and one owned field. The exact odd-grid backend and its bit cost remain supplier obligations. This does not invert B Q_U D or complete a decoder.")
(HERE / "TRANSLATION-SERVICE.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
print(receipt["status"])
print(json.dumps({name: dict(scalar=item["counts"]["scalar_primitives"], maps=item["counts"]["translation_maps"],
                            real_odd_scans=item["counts"].get("real_odd_division_scans", 0)) for name, item in results.items()}, sort_keys=True))

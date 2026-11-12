#!/usr/bin/env python3
"""Signed invoice for the forward full-frame transport of F9 operator 2.

The merged fixed-vector audit evaluates one circuit for each canonical class:
the width-9 Fourier adjoint, then K_G, then the Fourier. It calls that circuit
the full-frame transport. On operator 2 the circuit fixes |0> with phase +1.
This checker prices that same circuit. The matrix element at |0> is one
address of the resulting monomial, not the invoice.

Standard library only. Amplitudes come from the pinned quadratic engine.
No selected-frontier change.
"""
from collections import Counter
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import gzip
import json
import tarfile

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
PACKET = ROOT / "research/filtered-native-kappa004/inputs/original-packet.tar.gz"
QUADRATIC = ROOT / "research/active-mode-delivery-frontier/source/quadratic.py"
SELECTED = ROOT / "certificates/selected-result.json"
MEMBER = (
    "filtered_native_implementation/research/retained_state_next/"
    "F9-SOURCE-DAG-ALL8-WORD.json.gz"
)
PACKET_SHA = "595f988e748b1f3b25e7525a226da173966e4278a70f511b2919245cec1b45f7"
QUADRATIC_SHA = "d406584aed1479b75c387bc964b9e797b2f4f75e5f8c6bbea00df07f7d590a91"
WORD_SHA = "934fea11e51f674ce2031b7d3127b994a921a9d83317b00359292752563a1775"
N = 9
OPERATOR = 2

# Locked invoice. The census below has to reproduce every entry.
EXPECT = {
    "op": 2,
    "G_columns": [1, 2, 4, 8, 128, 394, 165, 80, 78],
    "K_permutation_rows": [65, 290, 324, 296, 128, 64, 384, 112, 32],
    "K_quadratic_rows": [32, 336, 112, 336, 46, 501, 110, 288, 426],
    "K_linear_Z4": [0, 0, 0, 0, 0, 1, 1, 0, 1],
    "transport_matrix_rows": [1, 2, 4, 8, 398, 85, 270, 16, 58],
    "transport_quadratic_rows": [85, 186, 213, 186, 111, 26, 21, 270, 384],
    "transport_linear_Z4": [3, 1, 1, 1, 2, 0, 0, 0, 3],
    "transport_offset": 0,
    "transport_global_phase": 0,
    "compiled_peak_support": 0,
    "sandwich_peak_support": 9,
    "fourier_support_on_zero": 9,
    "addresses": 512,
    "moved_addresses": 496,
    "identity_agreements": 16,
    "fixed_addresses": [0, 10, 38, 44, 150, 156, 176, 186, 258, 264, 292, 302, 404, 414, 434, 440],
    "phase_histogram": {"0": 144, "1": 144, "2": 112, "3": 112},
    "defect_rank": 5,
    "signed_order": 10,
    "operator1_zero_offset": 48,
    "operator1_zero_phase": [-1, 0],
    "backward_variant_zero_offset": 352,
    "backward_variant_zero_phase": [0, 1],
}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def transpose(rows, n):
    return tuple(sum(((rows[j] >> i) & 1) << j for j in range(n)) for i in range(n))


def inverse_matrix(rows, n):
    augmented = [row | (1 << (n + i)) for i, row in enumerate(rows)]
    for column in range(n):
        pivot = next(i for i in range(column, n) if augmented[i] >> column & 1)
        augmented[column], augmented[pivot] = augmented[pivot], augmented[column]
        for i in range(n):
            if i != column and augmented[i] >> column & 1:
                augmented[i] ^= augmented[column]
    need([row & ((1 << n) - 1) for row in augmented] == [1 << i for i in range(n)],
         "singular frame matrix")
    return tuple(row >> n for row in augmented)


def parity(value):
    return value.bit_count() & 1


def matvec(rows, vector):
    return sum(parity(row & vector) << i for i, row in enumerate(rows))


def diagonal_data(columns):
    matrix = transpose(tuple(columns), N)
    cols = transpose(inverse_matrix(matrix, N), N)
    quadratic = tuple(
        (1 << i) ^ sum(parity(a & b) << j for j, b in enumerate(cols))
        for i, a in enumerate(cols)
    )
    linear = tuple((quadratic[i] >> i) & 1 for i in range(N))
    return matrix, quadratic, linear


def k_circuit(columns, backward=False):
    matrix, quadratic, linear = diagonal_data(columns)
    if backward:
        linear = tuple((-value) % 4 for value in linear)
    return [("P", matrix), ("D", quadratic, linear)]


def adjoint(circuit):
    out = []
    for gate in reversed(circuit):
        kind = gate[0]
        if kind == "P":
            out.append(("P", inverse_matrix(gate[1], N)))
        elif kind == "D":
            out.append(("D", gate[1], tuple((-value) % 4 for value in gate[2])))
        elif kind == "C":
            out.append(("C", gate[1], -gate[2]))
        elif kind == "phase":
            out.append(("phase", (-gate[1]) % 4))
        else:
            raise ValueError("unexpected gate " + kind)
    return out


def fourier():
    return [("C", 1 << i, 1) for i in range(N)]


def fourier_adjoint():
    return [("C", 1 << i, -1) for i in reversed(range(N))]


def qvalue(quadratic, linear, vector):
    total = sum(linear[i] for i in range(N) if vector >> i & 1)
    total += 2 * sum(
        parity((quadratic[i] >> (i + 1)) & (vector >> (i + 1)))
        for i in range(N) if vector >> i & 1
    )
    return total % 4


def binary_rank(rows):
    pivots = {}
    for row in rows:
        value = row
        while value:
            bit = value.bit_length() - 1
            if bit not in pivots:
                pivots[bit] = value
                break
            value ^= pivots[bit]
    return len(pivots)


def load_engine():
    need(digest(QUADRATIC) == QUADRATIC_SHA, "quadratic.py pin")
    spec = spec_from_file_location("f9_operator2_quadratic", QUADRATIC)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_word():
    need(digest(PACKET) == PACKET_SHA, "packet pin")
    with tarfile.open(PACKET, "r:gz") as archive:
        raw = archive.extractfile(MEMBER).read()
    need(sha256(raw).hexdigest() == WORD_SHA, "F9 word member pin")
    word = json.loads(gzip.decompress(raw))
    warps = word["canonical"]["warps"]
    need(len(warps) == 72 and [row["op"] for row in warps] == list(range(1, 73)),
         "canonical warp operators are not exactly 1..72")
    frames = word["canonical"]["frames"]
    need([i for i, basis in enumerate(frames) if len(basis) == 9] == [1],
         "frame 1 is not the unique full frame")
    need(len(frames[1]) == 9, "full frame width")
    return word


def describe(engine, circuit, vector):
    counts = {}
    state = engine.signature(N, circuit, vector, counts)
    width, offset, columns, terms, real, imag, denominator = state
    return {
        "width": width,
        "offset": offset,
        "support": len(columns),
        "terms": len(terms),
        "phase": (real, imag),
        "denominator": denominator,
        "peak": counts.get("peak_support_rank", 0),
    }


def pure_table(engine, circuit):
    """Return (address, phase exponent) for every basis input, and the peak support."""
    table = []
    peak = 0
    phases = {(1, 0): 0, (0, 1): 1, (-1, 0): 2, (0, -1): 3}
    for vector in range(1 << N):
        row = describe(engine, circuit, vector)
        need(row["width"] == N and row["support"] == 0 and row["terms"] == 0
             and row["denominator"] == 0, "image is not a pure basis vector")
        need(row["phase"] in phases, "phase is not a unit in {1, i, -1, -i}")
        table.append((row["offset"], phases[row["phase"]]))
        peak = max(peak, row["peak"])
    return table, peak


def compose(left, right):
    """Apply left, then right, adding phase exponents."""
    out = []
    for vector, (image, phase) in enumerate(left):
        nxt, extra = right[image]
        out.append((nxt, (phase + extra) % 4))
    return out


def fit_monomial(table):
    images = [image for image, _ in table]
    phases = [phase for _, phase in table]
    need(images[0] == 0 and phases[0] == 0, "transport does not fix |0> with phase +1")
    columns = tuple(images[1 << i] for i in range(N))
    rows = tuple(sum(((columns[k] >> i) & 1) << k for k in range(N)) for i in range(N))
    need(all(matvec(rows, vector) == images[vector] for vector in range(1 << N)),
         "address map is not the linear map read from the basis")
    linear = tuple(phases[1 << i] % 4 for i in range(N))
    quadratic = []
    for i in range(N):
        mask = (linear[i] & 1) << i
        for j in range(i + 1, N):
            cross = (phases[(1 << i) | (1 << j)] - linear[i] - linear[j]) % 4
            need(cross in (0, 2), "weight-2 phase is outside the quadratic Z4 shape")
            if cross == 2:
                mask |= 1 << j
        quadratic.append(mask)
    symmetric = []
    for i in range(N):
        mask = quadratic[i]
        for j in range(i):
            if quadratic[j] >> i & 1:
                mask |= 1 << j
        symmetric.append(mask)
        need((mask >> i) & 1 == linear[i] % 2, "quadratic diagonal disagrees with the linear sign")
    symmetric = tuple(symmetric)
    need(all(phases[vector] == qvalue(symmetric, linear, vector) for vector in range(1 << N)),
         "quadratic phase misses an address")
    return rows, symmetric, linear


def program_facts(word):
    frames = word["canonical"]["frames"]
    out = {}
    for direction, events in word["programs"].items():
        climbs = Counter()
        centers = 0
        full = []
        other = []
        for index, event in enumerate(events):
            kind = event[0]
            if kind == "climb":
                need(len(event) == 6 and isinstance(event[5], int), "climb rank field")
                climbs[event[5]] += 1
            elif kind == "center":
                centers += 1
            elif kind == "warp" and abs(event[2]) % 1000000 == OPERATOR:
                dims = (len(frames[event[3]]), len(frames[event[4]]))
                record = {
                    "index": index,
                    "opcode": event[2],
                    "ref": event[1],
                    "frames": [event[3], event[4]],
                    "dims": list(dims),
                }
                if dims == (9, 9):
                    full.append(record)
                else:
                    other.append(record)
        out[direction] = {
            "events": len(events),
            "climb_ranks": {str(rank): count for rank, count in sorted(climbs.items())},
            "center_events": centers,
            "class2_full_frame": full,
            "class2_other": other,
        }
    return out


def controls(engine, columns, transport, table):
    zero = describe(engine, transport + [("phase", 1)], 0)
    need(zero["offset"] == 0 and zero["phase"] == (0, 1) and zero["denominator"] == 0,
         "a global factor i must be visible at |0>")
    bare = describe(engine, k_circuit(columns), 1)
    moved = describe(engine, transport, 1)
    need(bare["support"] == 0 and moved["support"] == 0, "control states leave the basis")
    need((bare["offset"], bare["phase"]) != (moved["offset"], moved["phase"]),
         "deleting both Fourier factors must change address 1")
    backward = fourier_adjoint() + k_circuit(columns, backward=True) + fourier()
    back_zero = describe(engine, backward, 0)
    need(back_zero["support"] == 0 and back_zero["denominator"] == 0, "backward variant is not pure")
    need(back_zero["offset"] == EXPECT["backward_variant_zero_offset"]
         and list(back_zero["phase"]) == EXPECT["backward_variant_zero_phase"],
         "backward-sign sandwich does not have the locked image of |0>")
    need(back_zero["offset"] != 0, "backward-sign sandwich must leave |0>")
    squared = compose(table, table)
    identity = [(vector, 0) for vector in range(1 << N)]
    need(squared != identity, "the transport is not an involution")
    fourier_zero = describe(engine, fourier(), 0)
    adjoint_zero = describe(engine, fourier_adjoint(), 0)
    need(fourier_zero["support"] == EXPECT["fourier_support_on_zero"]
         and adjoint_zero["support"] == EXPECT["fourier_support_on_zero"],
         "each Fourier factor must have support rank 9 on |0>")
    need(fourier_zero["peak"] == 9 and adjoint_zero["peak"] == 9, "Fourier peak support")


def invoice(engine, word):
    by_op = {row["op"]: tuple(row["G_columns"]) for row in word["canonical"]["warps"]}
    columns = by_op[OPERATOR]
    need(list(columns) == EXPECT["G_columns"], "operator 2 columns changed")
    matrix, quadratic, linear = diagonal_data(columns)
    need(list(matrix) == EXPECT["K_permutation_rows"], "K permutation rows")
    need(list(quadratic) == EXPECT["K_quadratic_rows"], "K quadratic rows")
    need(list(linear) == EXPECT["K_linear_Z4"], "K linear signs")
    forward = k_circuit(columns)
    transport = fourier_adjoint() + forward + fourier()
    table, peak = pure_table(engine, transport)
    need(peak == EXPECT["sandwich_peak_support"], "sandwich peak support")
    need(all(describe(engine, transport, vector)["peak"] == EXPECT["sandwich_peak_support"]
             for vector in range(1 << N)),
         "every basis input must see sandwich peak support 9")
    rows, sym, phase_linear = fit_monomial(table)
    need(list(rows) == EXPECT["transport_matrix_rows"], "transport matrix")
    need(list(sym) == EXPECT["transport_quadratic_rows"], "transport quadratic form")
    need(list(phase_linear) == EXPECT["transport_linear_Z4"], "transport linear signs")
    monomial = [("D", sym, phase_linear), ("P", rows)]
    compiled, compiled_peak = pure_table(engine, monomial)
    need(compiled == table, "compiled diagonal-then-permutation disagrees with the sandwich")
    need(compiled_peak == EXPECT["compiled_peak_support"], "compiled peak support")
    adjoint_table, adjoint_peak = pure_table(
        engine, fourier_adjoint() + adjoint(forward) + fourier())
    need(adjoint_peak == EXPECT["sandwich_peak_support"], "adjoint sandwich peak")
    inverse = [None] * (1 << N)
    for vector, (image, phase) in enumerate(table):
        need(inverse[image] is None, "address map is not bijective")
        inverse[image] = (vector, (-phase) % 4)
    need(all(item is not None for item in inverse), "address map missed an output")
    need(inverse == adjoint_table, "adjoint sandwich is not the inverse")
    power = table
    identity = [(vector, 0) for vector in range(1 << N)]
    order = 1
    while power != identity:
        power = compose(power, table)
        order += 1
        need(order <= 16, "signed order did not close by 16")
    need(order == EXPECT["signed_order"], "signed order")
    fixed = [vector for vector, (image, phase) in enumerate(table) if image == vector and phase == 0]
    moved = sum(image != vector for vector, (image, phase) in enumerate(table))
    kernel = [vector for vector in range(1 << N) if matvec(rows, vector) == vector]
    defect_rows = [rows[i] ^ (1 << i) for i in range(N)]
    defect = binary_rank(defect_rows)
    need(defect == EXPECT["defect_rank"], "rank of M+I")
    need(kernel == fixed, "phase-+1 fixed set is not ker(M+I)")
    need(len(fixed) == 1 << (N - defect) == EXPECT["identity_agreements"], "fixed-space count")
    need(fixed == EXPECT["fixed_addresses"], "fixed addresses")
    need(moved == EXPECT["moved_addresses"], "moved-address count")
    histogram = Counter(phase for _, phase in table)
    need({str(key): histogram[key] for key in range(4)} == EXPECT["phase_histogram"],
         "phase histogram")
    one = by_op[1]
    one_zero = describe(engine, fourier_adjoint() + k_circuit(one) + fourier(), 0)
    need(one_zero["support"] == 0 and one_zero["denominator"] == 0, "operator 1 image is not pure")
    need(one_zero["offset"] == EXPECT["operator1_zero_offset"]
         and list(one_zero["phase"]) == EXPECT["operator1_zero_phase"],
         "operator 1 sentinel moved off its locked image")
    controls(engine, columns, transport, table)
    facts = program_facts(word)
    for direction in ("backward", "forward"):
        row = facts[direction]
        need(row["center_events"] == 0, direction + " program contains a centre opcode")
        need(row["climb_ranks"] == {"1": 2201, "2": 412, "3": 510, "4": 127, "5": 40},
             direction + " climb histogram")
        need(len(row["class2_full_frame"]) == 1, direction + " full-frame class-2 count")
        full = row["class2_full_frame"][0]
        need(full["opcode"] == -2 and full["ref"] == ["L", 250] and full["frames"] == [1, 1],
             direction + " full-frame class-2 event")
        need(len(row["class2_other"]) == 1, direction + " other class-2 count")
        other = row["class2_other"][0]
        need(other["opcode"] == 2 and other["ref"] == ["L", 250]
             and other["frames"] == [292, 3941] and other["dims"] == [4, 4],
             direction + " rank-4 class-2 event")
    profile = {str(key): int(value) for key, value in word["canonical"]["local_profile"].items()}
    need(profile == {"1": 2201, "2": 412, "3": 510, "4": 127, "5": 40, "8": 8},
         "canonical local profile")
    selected = json.loads(SELECTED.read_text(encoding="utf-8"))
    need(selected["kappa"] == "363005817/100000000000", "selected kappa changed")
    need(selected["decimal"] == "0.00363005817", "selected decimal changed")
    return {
        "schema": "f9-operator2-full-frame-invoice/v1",
        "evidence_class": "exhaustive finite census",
        "word_member": MEMBER,
        "word_sha256": WORD_SHA,
        "operator": EXPECT["op"],
        "circuit": "Fourier adjoint, then forward K_G, then Fourier",
        "G_columns": EXPECT["G_columns"],
        "K_permutation_rows": EXPECT["K_permutation_rows"],
        "K_quadratic_rows": EXPECT["K_quadratic_rows"],
        "K_linear_Z4": EXPECT["K_linear_Z4"],
        "monomial": {
            "matrix_rows": EXPECT["transport_matrix_rows"],
            "offset": EXPECT["transport_offset"],
            "quadratic_rows": EXPECT["transport_quadratic_rows"],
            "linear_Z4": EXPECT["transport_linear_Z4"],
            "global_phase": EXPECT["transport_global_phase"],
            "action": "T|x> = i^{q(x)} |Mx>, with q the Z4 form of those rows",
        },
        "frame_change": {
            "compiled_support_rank": EXPECT["compiled_peak_support"],
            "sandwich_peak_support_on_every_basis_input": EXPECT["sandwich_peak_support"],
            "each_fourier_factor_support_on_zero": EXPECT["fourier_support_on_zero"],
        },
        "restoration": {
            "inverse": "the same sandwich with K_G replaced by its gate adjoint",
            "signed_order": EXPECT["signed_order"],
            "involution": False,
        },
        "target_debit": {
            "moved_addresses": EXPECT["moved_addresses"],
            "identity_agreements": EXPECT["identity_agreements"],
            "fixed_addresses": EXPECT["fixed_addresses"],
            "defect_rank_of_M_plus_I": EXPECT["defect_rank"],
            "phase_histogram": EXPECT["phase_histogram"],
            "zero_matrix_element": [1, 0],
        },
        "centre_comparison": {
            "inherited_unit": "one rank-8 centre, H8, from the active-mode delivery contract",
            "compiled_support_rank": 0,
            "pays_one_H8": False,
            "program_center_opcodes": 0,
            "program_rank8_climbs": 0,
            "local_profile_rank8": 8,
        },
        "word_occurrences": facts,
        "selected_kappa": "363005817/100000000000",
        "no_new_kappa": True,
    }


def main():
    engine = load_engine()
    word = load_word()
    record = invoice(engine, word)
    expected_path = HERE / "RESULT.json"
    if "--record" in __import__("sys").argv:
        expected_path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    else:
        saved = json.loads(expected_path.read_text(encoding="utf-8"))
        need(saved == record, "RESULT.json disagrees with the recomputation")
    print(
        "PASS_F9_OPERATOR2_FULL_FRAME_INVOICE "
        "op=2 support_rank=0 sandwich_peak=9 moved=496 fixed=16 "
        "order=10 defect_rank=5 no_new_kappa=true"
    )


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Audit the F9 common-fixed-vector premise against full-frame transport.

The scalar observer used by PR5720 and PR5745 leaves a rational coefficient
unchanged at a warp. That agrees with evaluating each canonical K_G on |0>.
The full-frame transport F† K F does not fix |0> for 64 of the 72 classes.

Standard library only. The amplitude engine is the pinned quadratic.py.
No clifford_exact import and no selected-frontier change.
"""
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
MEMBER = (
    "filtered_native_implementation/research/retained_state_next/"
    "F9-SOURCE-DAG-ALL8-WORD.json.gz"
)
PACKET_SHA = "595f988e748b1f3b25e7525a226da173966e4278a70f511b2919245cec1b45f7"
QUADRATIC_SHA = "d406584aed1479b75c387bc964b9e797b2f4f75e5f8c6bbea00df07f7d590a91"
WORD_SHA = "934fea11e51f674ce2031b7d3127b994a921a9d83317b00359292752563a1775"
N = 9


def need(ok, message):
    if not ok:
        raise ValueError(message)


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def transpose(rows, n):
    return tuple(sum(((rows[j] >> i) & 1) << j for j in range(n)) for i in range(n))


def inverse(rows, n):
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


def diagonal_data(columns):
    matrix = transpose(tuple(columns), N)
    inverse_matrix = inverse(matrix, N)
    cols = transpose(inverse_matrix, N)
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
            out.append(("P", inverse(gate[1], N)))
        elif kind == "D":
            out.append(("D", gate[1], tuple((-value) % 4 for value in gate[2])))
        elif kind == "X":
            out.append(gate)
        elif kind == "phase":
            out.append(("phase", (-gate[1]) % 4))
        else:
            raise ValueError("unexpected gate " + kind)
    return out


def fourier():
    return [("C", 1 << i, 1) for i in range(N)]


def fourier_adjoint():
    return [("C", 1 << i, -1) for i in reversed(range(N))]


def load_engine():
    need(digest(QUADRATIC) == QUADRATIC_SHA, "quadratic.py pin")
    spec = spec_from_file_location("f9_fixed_vector_quadratic", QUADRATIC)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def image_of_zero(engine, circuit):
    state = engine.signature(N, circuit, 0)
    width, offset, columns, terms, real, imag, denominator = state
    need(width == N and columns == () and terms == () and denominator == 0,
         "image of |0> is not a pure basis vector")
    pair, den = engine.amplitude(state, offset)
    need(pair == (real, imag) and den == 0, "phase disagrees with the support")
    if offset:
        zero, zero_den = engine.amplitude(state, 0)
        need(zero == (0, 0) and zero_den == 0, "nonzero offset still has |0> mass")
    other = 1 if offset == 0 else 0
    absent, absent_den = engine.amplitude(state, other)
    need(absent == (0, 0) and absent_den == 0, "a second basis vector is occupied")
    return offset, (real, imag)


def load_word():
    need(digest(PACKET) == PACKET_SHA, "packet pin")
    with tarfile.open(PACKET, "r:gz") as archive:
        raw = archive.extractfile(MEMBER).read()
    need(sha256(raw).hexdigest() == WORD_SHA, "F9 word member pin")
    word = json.loads(gzip.decompress(raw))
    warps = word["canonical"]["warps"]
    need(len(warps) == 72 and [row["op"] for row in warps] == list(range(1, 73)),
         "canonical warp operators are not exactly 1..72")
    canonical = {row["op"] for row in warps}
    for direction in ("forward", "backward"):
        seen = set()
        for event in word["programs"][direction]:
            if event[0] != "warp":
                continue
            seen.add(abs(event[2]) % 1000000)
        need(seen == canonical, direction + " warp operators differ from the 72 classes")
    return warps


def variants(columns):
    forward = k_circuit(columns)
    backward = k_circuit(columns, backward=True)
    return (forward, adjoint(forward), backward, adjoint(backward))


def census(engine, warps):
    records = []
    for row in warps:
        columns = tuple(row["G_columns"])
        need(len(columns) == N, "warp width")
        for circuit in variants(columns):
            offset, phase = image_of_zero(engine, circuit)
            need(offset == 0 and phase == (1, 0), "a K_G variant moves |0>")
        offset, phase = image_of_zero(
            engine, fourier_adjoint() + k_circuit(columns) + fourier())
        records.append({
            "op": row["op"],
            "offset": offset,
            "phase": [phase[0], phase[1]],
        })
    return records


def controls(engine, warps):
    columns = tuple(warps[0]["G_columns"])
    moved, _ = image_of_zero(engine, k_circuit(columns) + [("phase", 1)])
    need(moved == 0, "phase control changed the address")
    pair = engine.amplitude(engine.signature(N, k_circuit(columns) + [("phase", 1)], 0), 0)
    need(pair == ((0, 1), 0), "a global factor i must be visible")
    translated = k_circuit(columns)
    translated.insert(0, ("X", 1))
    offset, _ = image_of_zero(engine, translated)
    need(offset != 0, "an address translation must leave |0>")
    identity = tuple(1 << i for i in range(N))
    for circuit in variants(identity):
        offset, phase = image_of_zero(engine, circuit)
        need(offset == 0 and phase == (1, 0), "identity K_G must fix |0>")
    for row in warps:
        offset, phase = image_of_zero(engine, k_circuit(tuple(row["G_columns"])))
        need(offset == 0 and phase == (1, 0),
             "removing the Fourier sandwich must restore the K_G fixed vector")


def main():
    engine = load_engine()
    warps = load_word()
    records = census(engine, warps)
    controls(engine, warps)
    identity = [row for row in records if row["offset"] == 0 and row["phase"] == [1, 0]]
    nonzero = [row for row in records if row["offset"] != 0]
    need(len(identity) == 8 and len(nonzero) == 64, "8/64 transport split")
    need(all(row["phase"] == [1, 0] for row in records if row["offset"] == 0),
         "an offset-zero transport has a nontrivial phase")
    units = {(1, 0), (0, 1), (-1, 0), (0, -1)}
    need(all(tuple(row["phase"]) in units for row in records), "non-unit transport phase")
    expected = json.loads((HERE / "RESULT.json").read_text(encoding="utf-8"))
    need(expected["records"] == records, "RESULT.json disagrees with the recomputation")
    need(expected["transport_identity_on_zero"] == 8, "recorded identity count")
    need(expected["transport_nonzero_offset"] == 64, "recorded moved count")
    need(expected["word_sha256"] == WORD_SHA, "recorded word pin")
    print(
        "PASS_F9_FIXED_VECTOR_TRANSPORT_AUDIT "
        f"classes=72 k_variants=288 transport_identity_on_zero=8 "
        f"transport_nonzero_offset=64 no_new_kappa=true"
    )


if __name__ == "__main__":
    main()

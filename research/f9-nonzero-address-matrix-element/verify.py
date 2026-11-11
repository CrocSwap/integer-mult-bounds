#!/usr/bin/env python3
"""Census K_G matrix elements on every computational address of the F9 word.

The predecessor audit shows that every signed variant of each of the 72
canonical operators fixes |0> with phase +1. This checker evaluates the same
operators on all 512 computational basis states. It is an exhaustive finite
census of that domain, not a new kappa and not a caller invoice.

Standard library only. The amplitude engine is the pinned quadratic.py.
"""
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import gzip
import json
import sys
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
ADDRESSES = 1 << N
PHASES = {(1, 0): 0, (0, 1): 1, (-1, 0): 2, (0, -1): 3}


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


def matrix_vector(rows, vector):
    return sum(((row & vector).bit_count() & 1) << j for j, row in enumerate(rows))


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


def negate(linear):
    return tuple((-value) % 4 for value in linear)


def exponent(quadratic, linear, address):
    """Constant i-power of D on one computational basis state.

    This is the empty-support case of the pinned engine's D gate: each linear
    sign contributes itself when that bit is set, and each upper-triangular
    quadratic 1 contributes 2 when both bits are set. No support column appears.
    """
    total = 0
    for i in range(N):
        if ((address >> i) & 1) == 0:
            continue
        total += linear[i]
        row = quadratic[i] >> (i + 1)
        while row:
            bit = row & -row
            column = i + 1 + bit.bit_length() - 1
            if (address >> column) & 1:
                total += 2
            row ^= bit
    return total % 4


def k_circuit(columns, backward=False):
    matrix, quadratic, linear = diagonal_data(columns)
    signs = negate(linear) if backward else linear
    return [("P", matrix), ("D", quadratic, signs)]


def adjoint(circuit):
    out = []
    for gate in reversed(circuit):
        kind = gate[0]
        if kind == "P":
            out.append(("P", inverse(gate[1], N)))
        elif kind == "D":
            out.append(("D", gate[1], negate(gate[2])))
        else:
            raise ValueError("unexpected gate " + kind)
    return out


def variants(columns):
    forward = k_circuit(columns)
    backward = k_circuit(columns, backward=True)
    return (forward, adjoint(forward), backward, adjoint(backward))


def predicted(columns):
    """Address and i-power for each signed variant, as a function of the input."""
    matrix, quadratic, linear = diagonal_data(columns)
    inverse_matrix = inverse(matrix, N)
    negated = negate(linear)

    def forward(address):
        image = matrix_vector(matrix, address)
        return image, exponent(quadratic, linear, image)

    def adjoint_forward(address):
        return matrix_vector(inverse_matrix, address), exponent(quadratic, negated, address)

    def backward(address):
        image = matrix_vector(matrix, address)
        return image, exponent(quadratic, negated, image)

    def adjoint_backward(address):
        return matrix_vector(inverse_matrix, address), exponent(quadratic, linear, address)

    return (forward, adjoint_forward, backward, adjoint_backward)


def load_engine():
    need(digest(QUADRATIC) == QUADRATIC_SHA, "quadratic.py pin")
    spec = spec_from_file_location("f9_nonzero_address_quadratic", QUADRATIC)
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
    canonical = {row["op"] for row in warps}
    for direction in ("forward", "backward"):
        seen = set()
        for event in word["programs"][direction]:
            if event[0] != "warp":
                continue
            seen.add(abs(event[2]) % 1000000)
        need(seen == canonical, direction + " warp operators differ from the 72 classes")
    return warps


def engine_image(engine, circuit, address):
    state = engine.signature(N, circuit, address)
    width, offset, columns, terms, real, imag, denominator = state
    need(width == N and columns == () and terms == () and denominator == 0,
         "image is not a pure basis vector")
    pair, den = engine.amplitude(state, offset)
    need(pair == (real, imag) and den == 0, "support phase disagrees")
    other = 1 if offset == 0 else 0
    absent, absent_den = engine.amplitude(state, other)
    need(absent == (0, 0) and absent_den == 0, "a second basis vector is occupied")
    return offset, PHASES[(real, imag)]


def reduced_basis(vectors):
    """Return pivot-reduced basis pairs. Each pivot bit belongs to one vector."""
    pivots = {}
    for vector in vectors:
        value = vector
        while value:
            pivot = value.bit_length() - 1
            if pivot not in pivots:
                pivots[pivot] = value
                break
            value ^= pivots[pivot]
    order = sorted(pivots)
    for pivot in order:
        for other in order:
            if other != pivot and pivots[other] >> pivot & 1:
                pivots[other] ^= pivots[pivot]
    return [(pivot, pivots[pivot]) for pivot in order]


def coefficients(reduced, vector):
    coords = 0
    for index, (pivot, basis_vector) in enumerate(reduced):
        if vector >> pivot & 1:
            coords |= 1 << index
            vector ^= basis_vector
    return None if vector else coords


def span(vectors):
    points = [0]
    for vector in vectors:
        need(vector != 0, "a zero basis vector would duplicate the span")
        # Snapshot first. Extending a list from a generator over itself never stops.
        points.extend(value ^ vector for value in tuple(points))
    return set(points)


def classify(engine, warps):
    records = []
    common = set(range(ADDRESSES))
    minus_total = 0
    for row in warps:
        columns = tuple(row["G_columns"])
        need(len(columns) == N, "warp width")
        forecasts = predicted(columns)
        circuits = variants(columns)
        plus = []
        kernel = []
        minus = []
        address_one = None
        for address in range(ADDRESSES):
            images = [forecast(address) for forecast in forecasts]
            for variant, circuit in enumerate(circuits):
                observed = engine_image(engine, circuit, address)
                need(observed == images[variant],
                     f"engine disagrees with the phase formula at op {row['op']} "
                     f"variant {variant} address {address}")
            image, power = images[0]
            if address == 1:
                address_one = {"offset": image, "phase_power": power}
            if image != address:
                continue
            need(power in (0, 2), f"odd phase on a fixed address at op {row['op']}")
            kernel.append(address)
            if power == 0:
                plus.append(address)
            else:
                minus.append(address)
        plus_set = set(plus)
        power = {address: (0 if address in plus_set else 2) for address in kernel}
        kernel_basis = reduced_basis(kernel)
        for address in kernel:
            coords = coefficients(kernel_basis, address)
            need(coords is not None, f"fixed space is not a span at op {row['op']}")
            predicted_power = 0
            for index, (_, basis_vector) in enumerate(kernel_basis):
                if coords >> index & 1:
                    predicted_power = (predicted_power + power[basis_vector]) % 4
            need(predicted_power == power[address],
                 f"phase on the fixed space is not a character at op {row['op']}")
        basis = [vector for _, vector in reduced_basis(plus)]
        need(span(basis) == set(plus), f"phase-+1 set is not the recorded span at op {row['op']}")
        need(0 in plus, f"op {row['op']} moves |0>")
        minus_total += len(minus)
        common &= set(plus)
        records.append({
            "op": row["op"],
            "plus_basis": basis,
            "plus_count": len(plus),
            "kernel_count": len(kernel),
            "minus_count": len(minus),
            "address_one": address_one,
        })
    return records, sorted(common), minus_total


def controls(engine, warps):
    identity = tuple(1 << i for i in range(N))
    forecasts = predicted(identity)
    for address in range(ADDRESSES):
        image, power = forecasts[0](address)
        need(image == address and power == 0, "identity K_G must fix every basis vector")
        need(engine_image(engine, k_circuit(identity), address) == (address, 0),
             "engine rejects the identity control")
    columns = tuple(warps[0]["G_columns"])
    moved = engine_image(engine, k_circuit(columns) + [("phase", 1)], 0)
    need(moved == (0, 1), "a global factor i must be visible at |0>")
    matrix, quadratic, linear = diagonal_data(columns)
    witness = 17
    image = matrix_vector(matrix, witness)
    at_input = exponent(quadratic, linear, witness)
    at_image = exponent(quadratic, linear, image)
    need(image != witness and at_input != at_image, "gate-order witness did not separate the phases")
    need(engine_image(engine, k_circuit(columns), witness) == (image, at_image),
         "engine does not evaluate the diagonal phase at Gx")
    row = warps[5]
    need(row["op"] == 6, "operator 6 is not the sixth canonical class")
    columns = tuple(row["G_columns"])
    for forecast, circuit in zip(predicted(columns), variants(columns)):
        need(forecast(328) == (328, 2), "operator 6 must multiply |328> by -1")
        need(engine_image(engine, circuit, 328) == (328, 2),
             "engine disagrees on the operator-6 phase -1 witness")


def certificate(records, common, minus_total):
    exceptions = [row["op"] for row in records
                  if not (row["address_one"]["offset"] == 1 and row["address_one"]["phase_power"] == 0)]
    need(exceptions == [30, 66], "address-1 exceptions are not operators 30 and 66")
    for op in exceptions:
        row = records[op - 1]
        need(row["address_one"] == {"offset": 2, "phase_power": 0},
             f"operator {op} does not send |1> to |2> with phase +1")
    witness = records[25]
    need(witness["op"] == 26 and witness["plus_basis"] == [1] and witness["plus_count"] == 2,
         "operator 26 does not have phase-+1 space {0, 1}")
    need(1 not in span(records[29]["plus_basis"]), "operator 30 fixes address 1")
    need(common == [0], "a nonzero address is fixed with phase +1 by every class")
    need(minus_total == sum(row["minus_count"] for row in records), "minus tally")
    return {
        "schema": "f9-nonzero-address-matrix-element/v1",
        "word_member": MEMBER,
        "word_sha256": WORD_SHA,
        "quadratic_sha256": QUADRATIC_SHA,
        "classes": 72,
        "addresses": ADDRESSES,
        "variants": 4,
        "common_phase_one_addresses": common,
        "address_one_phase_one_count": 70,
        "address_one_exceptions": [
            {"op": op, "offset": 2, "phase": [1, 0]} for op in exceptions
        ],
        "witness": {
            "operator_26_plus_space": [0, 1],
            "operator_30_image_of_address_1": {"offset": 2, "phase": [1, 0]},
            "conclusion": "The only address in every phase-+1 set is 0.",
        },
        "minus_incidences": minus_total,
        "operators": records,
        "selected_kappa_unchanged": "363005817/100000000000",
    }


def main():
    engine = load_engine()
    warps = load_word()
    controls(engine, warps)
    records, common, minus_total = classify(engine, warps)
    produced = certificate(records, common, minus_total)
    result_path = HERE / "RESULT.json"
    if "--record" in sys.argv:
        result_path.write_text(json.dumps(produced, indent=2) + "\n", encoding="utf-8")
    recorded = json.loads(result_path.read_text(encoding="utf-8"))
    need(recorded == produced, "RESULT.json disagrees with the recomputation")
    print(
        "PASS_F9_NONZERO_ADDRESS_MATRIX_ELEMENT "
        "classes=72 addresses=512 variants=4 "
        "common_phase_one_addresses=1 address_one_exceptions=30,66 "
        f"minus_incidences={minus_total} no_new_kappa=true"
    )


if __name__ == "__main__":
    main()

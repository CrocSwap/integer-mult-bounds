"""Check the all-width word over a free group of port operators."""

from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import gzip
import json


HERE = Path(__file__).resolve().parent
PHYS = HERE.parents[1]
LANES = PHYS.parents[1]
WORKSPACE = LANES.parents[2]
MODES = (225, 226, 229, 232, 241, 242, 257, 258)
PINS = {
    "proof": (PHYS / "ORIGINAL-CLEAN-SOURCE.md", "dcd43c16e61fbf4aa2092b26cc1e1d09ce5c2e9ce4ad1a9bfd919ee4125676ab"),
    "payload": (PHYS / "ORIGINAL-CLEAN-SOURCE-PROGRAMS.json.gz", "abfcbfc40bac24e284be63623d9b18f1bb6d4d6ec1b9fa7e9bba27330f323667"),
    "receipt": (PHYS / "ORIGINAL-CLEAN-SOURCE.json", "4732d3d45ec4be3a06d0f5bcc56fd4a14cdb1a18b357be5e3d2b06b5f0fa68d1"),
    "producer": (PHYS / "emit_original_clean_source.py", "68bb00b61f0e430a56f0fb6786d507e07122dbd11e0ccf85f3f022accc2f04ea"),
    "R": (LANES / "circuit-interface/INTERFACE.json", "5c6c51fbffc07a683e922f17532fd90262ae9e23cc3560a696002073dd234ef3"),
    "core": (LANES / "history-encoding/FULL-MODE-PROGRAMS.json.gz", "f271842a741584389e166e700e262f161b0dd570ce8c7a540f2717e90ead5205"),
    "core_review": (LANES / "interface-proof/FULL-MODE-PORT-REVIEW.json", "ff123b08b3ac58f20d12d4fbec575472086ace1708d3242519884dbffe534372"),
    "original_native_frame_review": (LANES / "coherent-port/ORIGINAL-PAIRED-GAP-NATIVE-REVIEW.json", "e79603bee7c4077b3637f9b7891bac59719183e922a71d5994aaf9d405d5322f"),
    "canonical": (WORKSPACE / "work/five-pr-sprint-20261013/lanes/centre-sharing/CANONICAL-WORD.json.gz", "4ddb29fb9bc6f27e0c0fbfcf19a2a93a3496ad900d0f6d89059d0305c9576c0c"),
    "scalar_cost_convention": (LANES / "history-encoding/verify_echo.py", "3a595446631e133c994efa2d10c7b00cae0b8100e45f3990c8f55db82101fe49"),
}


def need(condition, reason):
    if not condition:
        raise ValueError(reason)


def load(name):
    path, pin = PINS[name]
    raw = path.read_bytes()
    if path.suffix == ".gz":
        raw = gzip.decompress(raw)
    need(sha256(raw).hexdigest() == pin, name + " pin")
    return json.loads(raw) if path.suffix in (".gz", ".json") else raw


def add(*terms):
    result = {}
    for coefficient, row in terms:
        for key, value in row.items():
            total = result.get(key, 0) + coefficient * value
            if total:
                result[key] = total
            else:
                result.pop(key, None)
    return result


def line(row, port, inverse=False):
    # Signed letters give the free group normal form. Only inverse pairs cancel.
    letter = -(port + 1) if inverse else port + 1
    result = {}
    for (word, origin), value in row.items():
        new_word = word[1:] if word and word[0] == -letter else (letter,) + word
        key = (new_word, origin)
        result[key] = result.get(key, 0) + value
    return {key: value for key, value in result.items() if value}


def linear(matrix, rows):
    return [add(*[(q, rows[j]) for j, q in row.items()]) for row in matrix]


def vadd(a, b, scale=1):
    return [add((1, x), (scale, y)) for x, y in zip(a, b)]


def scalar_cost(gate):
    q = Q(*gate[2:4]) if gate[0] == "scale" else Q(*gate[3:5])
    a, b = abs(q.numerator), q.denominator
    need(a > 0 and not b & (b - 1), "dyadic coefficient")
    if gate[0] == "scale":
        need(not a & (a - 1), "binary scale")
        return 2 * (abs(a.bit_length() - b.bit_length()) + int(q < 0))
    need(gate[0] == "add", "ADD or SCALE")
    return 2 * (3 + a.bit_length() - 1 + a.bit_count() + b.bit_length() - 1)


def binary_rank(rows):
    pivots = {}
    for row in rows:
        while row:
            lead = row.bit_length() - 1
            if lead not in pivots:
                pivots[lead] = row
                break
            row ^= pivots[lead]
    return len(pivots)


def main():
    data = {name: load(name) for name in PINS}
    packet, report, word = data["payload"], data["receipt"], data["canonical"]
    need(packet["core_payload_sha256"] == PINS["core"][1], "core binding")
    need(packet["interface_sha256"] == PINS["R"][1], "R binding")
    need(data["core_review"]["program_payload_sha256"] == PINS["core"][1], "core review binding")
    need(packet["mode_carriers"] == list(MODES), "helper slots")
    need(packet["physical_frames"] == {"X": ["Q", "F"], "Y": ["I", "F Q^-1"], "modes": ["I", "F"]}, "original frame contract")
    need(packet["width_requirement"] == "Every positive integer lambda", "all-width contract")
    need(set(packet["programs"]) == {"forward", "backward"}, "two directions")
    R = [{int(p): Q(q) for p, q in row.items()} for row in data["R"]["R"]]
    K = [{k: row[p] / 4 for k, row in enumerate(R) if p in row} for p in range(112)]
    need(len(R) == 8 and sum(map(len, R)) == 448, "actual R graph")
    need(word["ports"] == data["R"]["ports"], "port order")
    need(all(sum(R[i].get(p, 0) * R[j].get(p, 0) for p in range(112)) == 56 * (i == j)
             for i in range(8) for j in range(8)), "actual Gram identity")
    for p, normal in enumerate(word["ports"]):
        need(word["frames"][word["start"][p]] == [normal] and word["final"][p] == 1, "X line-to-full frame")
        basis = word["frames"][word["final"][112 + p]]
        need(word["start"][112 + p] == 0 and binary_rank(basis) == 8, "Y empty-to-hyperplane frame")
        need(all((normal & v).bit_count() % 2 == 0 for v in basis), "Y normal complement")
    need(all(word["start"][j] == 0 and word["final"][j] == 1 for j in MODES), "helper empty-to-full frames")
    identity = [{((), j): Q(1)} for j in range(704)]
    need(line(line(identity[0], 0), 0, True) == identity[0], "inverse cancellation")
    q4 = identity[0]
    for _ in range(4):
        q4 = line(q4, 0)
    need(q4 != identity[0], "no fourth-power reduction")
    need(line(line(identity[0], 0), 1) != line(line(identity[0], 1), 0), "no distinct-port commutation")

    def endpoint(rows, events, is_input, wrong_output_phase=False):
        result = [row.copy() for row in rows]
        offset = 0 if is_input else 112
        inverse = not is_input and not wrong_output_phase
        for p in range(112):
            result[offset + p] = line(result[offset + p], p, inverse)
        for event in events:
            need(event["endpoint"] == ("input" if is_input else "output"), "endpoint tag")
            target, coefficient = event["target"], Q(event["coefficient"])
            need(isinstance(target, int) and (0 <= target < 224 or target in MODES), "one-copy target")
            if event["kind"] == "physical_add":
                need(set(event) == {"kind", "target", "source", "coefficient", "endpoint"}, "ADD schema")
                source = event["source"]
                need(isinstance(source, int) and (0 <= source < 224 or source in MODES) and target != source, "distinct local operands")
                result[target] = add((1, result[target]), (coefficient, result[source]))
            else:
                need(event["kind"] == "physical_scale", "no added map or native event")
                need(set(event) == {"kind", "target", "coefficient", "endpoint"}, "scale schema")
                need(not is_input and target in MODES and coefficient == -1, "mode negation")
                result[target] = add((-1, result[target]))
        for p in range(112):
            result[offset + p] = line(result[offset + p], p, not inverse)
        return result

    def raw(rows, direction):
        result = [row.copy() for row in rows]
        x, y, z = rows[:112], rows[112:224], [rows[j] for j in MODES]
        read = linear(R, x if direction == "forward" else y)
        pterm, kterm = linear(K, read), linear(K, z)
        if direction == "forward":
            result[112:224] = vadd(vadd(vadd(y, x), pterm, -1), kterm, -1)
            modes = [add((-1, u), (-2, r)) for u, r in zip(z, read)]
        else:
            result[:112] = vadd(vadd(vadd(x, y, -1), pterm, -1), kterm, -8)
            modes = [add((-1, u), (Q(-1, 4), r)) for u, r in zip(z, read)]
        for j, value in zip(MODES, modes):
            result[j] = value
        return result

    def D(rows, inverse_phase=False):
        shifted = [line(row, p, inverse_phase) for p, row in enumerate(rows)]
        return vadd(rows, linear(K, linear(R, vadd(shifted, rows, -1))))

    def expected(direction):
        result = [row.copy() for row in identity]
        source_offset = 0 if direction == "forward" else 112
        source = identity[source_offset:source_offset + 112]
        result[112 - source_offset:224 - source_offset] = vadd(identity[112 - source_offset:224 - source_offset],
                                                             D(source, direction == "backward"),
                                                             1 if direction == "forward" else -1)
        return result

    checks = {}
    for direction, program in packet["programs"].items():
        need(set(program) == {"prefix", "suffix", "core_orientation"} and program["core_orientation"] == direction, "program schema")
        pre, post = program["prefix"], program["suffix"]
        def replay(a, b, wrong_phase=False):
            return endpoint(raw(endpoint(identity, a, True), direction), b, False, wrong_phase)
        actual, target = replay(pre, post), expected(direction)
        need(actual == target, direction + " all 704 columns")
        restored = sum(actual[j] == identity[j] for j in range(224, 704))
        leakage = sum(origin >= 224 for row in actual[:224] for _, origin in row)
        need(restored == 480 and leakage == 0, "all helpers and no data leakage")
        controls = {
            "missing_prefix": replay([], post) != target,
            "missing_negations": replay(pre, [e for e in post if e["kind"] != "physical_scale"]) != target,
            "missing_mode_read_cleanup": replay(pre, post[-8:] if direction == "forward" else post[:896] + post[-8:]) != target,
            "wrong_order": (replay(list(reversed(pre)), post) if direction == "forward"
                            else replay(pre, list(reversed(post)))) != target,
        }
        if direction == "backward":
            controls["Q_in_place_of_Q_inverse"] = replay(pre, post, True) != target
        need(all(controls.values()), direction + " mutation controls")
        events = pre + post
        adds = [e for e in events if e["kind"] == "physical_add"]
        negations = [e for e in events if e["kind"] == "physical_scale"]
        need(post[-8:] == negations and [e["target"] for e in negations] == list(MODES), "last eight negations")
        cost = 0
        for e in events:
            q = Q(e["coefficient"])
            cost += scalar_cost(["add", None, None, q.numerator, q.denominator] if e["kind"] == "physical_add"
                                else ["scale", None, q.numerator, q.denominator])
        core = data["core"][direction]
        current = word["start"].copy()
        scalar_frames = 0
        for event in core:
            if event[0] == "climb":
                need(current[event[2]] == event[3], "retained native entry frame")
                current[event[2]] = event[4]
            elif event[0] == "scalar":
                gate, frame = event[1:]
                need(gate[1][0] == "L" and current[gate[1][1]] == frame, "retained scalar target frame")
                if gate[0] == "add":
                    need(gate[2][0] == "L" and current[gate[2][1]] == frame, "retained scalar source frame")
                scalar_frames += 1
        need(current == word["final"], "retained complete endpoint frames")
        raw_cost = sum(scalar_cost(e[1]) for e in core if e[0] == "scalar")
        profile = dict(sorted(Counter(str(e[5]) for e in core if e[0] == "climb").items()))
        need(profile == report["paid_profile"], "retained paid profile")
        result = {"arbitrary_input_columns": 704, "restored_helper_fields": restored, "restored_mode_fields": 8,
                  "helper_input_coefficients_in_data": leakage, "physical_complex_ADDs": len(adds),
                  "physical_complex_negations": len(negations), "ADD_coefficient_magnitudes": dict(Counter(str(abs(Q(e["coefficient"]))) for e in adds)),
                  "added_real_primitives": cost, "core_and_added_real_primitives": raw_cost + cost,
                  "new_native_children": 0, "new_fields": 0, "new_address_or_phase_maps": 0,
                  "retained_native_events": sum(e[0] in ("climb", "adapter", "residual_adapter") for e in core),
                  "paid_native_rank": sum(e[5] for e in core if e[0] == "climb")}
        need(result == report["checks"][direction], direction + " literal invoice")
        checks[direction] = {**result, "mutation_controls": controls, "paid_profile": profile,
                             "retained_scalar_frame_checks": scalar_frames,
                             "formal_nonzero_terms": sum(map(len, actual))}

    basis = identity[:112]
    q_basis = [line(row, p) for p, row in enumerate(basis)]
    qi_basis = [line(row, p, True) for p, row in enumerate(basis)]
    need(vadd(D(qi_basis), D(basis, True)) == vadd(basis, qi_basis), "D_plus Q_inverse plus D_minus")
    need(vadd(D(q_basis, True), D(basis)) == vadd(basis, q_basis), "D_minus Q plus D_plus")
    need(D(basis) != D(basis, True), "distinct free phase kernels")
    result = {"status": "PASS_INDEPENDENT_ORIGINAL_CLEAN_SOURCE_FREE_Q",
              "source_pins": {name: pin for name, (_, pin) in PINS.items()}, "checks": checks,
              "formal_algebra": "Free group on signed port letters; only adjacent inverse letters cancel.",
              "finite_order_or_involution_used": False, "producer_imported_or_executed": False,
              "ordered_D_identities_checked": 2, "raw_content_map_or_native_kernel_replay": False,
              "raw_frame_chronology_checked": True,
              "scope": "Local physical endpoint graphs and clean content map under the inherited original native interface. Global owner, controller, and recursion admission are excluded."}
    (HERE / "CHECK.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"])
    print(json.dumps({"complete_scalar_costs": {key: value["core_and_added_real_primitives"] for key, value in checks.items()},
                      "restored_helpers": {key: value["restored_helper_fields"] for key, value in checks.items()}}, sort_keys=True))


if __name__ == "__main__":
    main()

"""Check complete bridge phases, source gauges, and scalar programs.

The phase check evaluates Fourier characters. It does not import the route,
bridge, or Clifford checkers. Values on inputs of weight at most two determine
these phase functions modulo four, because every binary parity has degree at
most two modulo four. The zero input also checks the constant phase.
"""

from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import argparse
import gzip
import json
import resource
import subprocess
import tarfile
import time


BASE = "bce54fb3f895cbe5cd4c0eb477c3afeed100190f"
ARCHIVE = "research/community-frontier1042-audit/selected-replay.tar.gz"
ARCHIVE_HASH = "22c3f4dce4b897a1d423d1388801933e288b6a6b1906cb15e1b16a5eb68db754"
INTERFACE_HASH = "5c6c51fbffc07a683e922f17532fd90262ae9e23cc3560a696002073dd234ef3"
PHASE = "t16/global/base/work/complex-nine-native/DATA-PHASES.json"
TEMPLATE = "t16/global/hosted/GLOBAL-TEMPLATE.json.gz"
PINS = {
    PHASE: "c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa",
    TEMPLATE: "73f47a1e60b1e4ea66dbca9a497c411c8e6adc7984e276a437a10a9a7a13b47a",
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sources(repo):
    command = ["git", "show", BASE + ":" + ARCHIVE]
    proc = subprocess.Popen(command, cwd=repo, stdout=subprocess.PIPE)
    digest = sha256()
    while block := proc.stdout.read(65536):
        digest.update(block)
    require(proc.wait() == 0 and digest.hexdigest() == ARCHIVE_HASH, "Archive source pin")
    proc = subprocess.Popen(command, cwd=repo, stdout=subprocess.PIPE)
    result = {}
    with tarfile.open(fileobj=proc.stdout, mode="r|gz") as archive:
        for item in archive:
            if item.name in PINS:
                raw = archive.extractfile(item).read()
                require(sha256(raw).hexdigest() == PINS[item.name], item.name + " source pin")
                result[item.name] = json.loads(
                    gzip.decompress(raw) if item.name.endswith(".gz") else raw)
    require(proc.wait() == 0 and set(result) == set(PINS), "Archive extraction")
    return result[PHASE], result[TEMPLATE]


def parity(value):
    return value.bit_count() & 1


def basis(q):
    hole = next(i for i in range(9) if not (q >> i) & 1)
    transvection = q ^ (1 << hole)
    order = list(range(9))
    order[0], order[hole] = order[hole], order[0]
    out = tuple((1 << i) ^ (transvection if (transvection >> i) & 1 else 0)
                for i in order)
    require(out[0] == q, "Port basis first column")
    require(all(parity(a & b) == (i == j)
                for i, a in enumerate(out) for j, b in enumerate(out)), "Port basis isometry")
    return out


def route(value, chart, stage):
    if not stage:
        return value
    start = 9 + 8 * (stage - 1)
    out = value & ~(511 | (255 << start))
    out ^= chart[0] if parity(value & chart[0]) else 0
    for i, v in enumerate(chart[1:]):
        out ^= (1 << (start + i)) if parity(value & v) else 0
        out ^= v if (value >> (start + i)) & 1 else 0
    return out


def phase(terms, frequency):
    return sum(sign * parity(axis & frequency) for axis, sign in terms) % 4


def phase_points(n):
    return [0] + [1 << i for i in range(n)] + [
        (1 << i) | (1 << j) for i in range(n) for j in range(i)]


def equal_phase(left, right, shift, points):
    return all((phase(left, value) - phase(right, value) -
                2 * parity(shift & value)) % 4 == 0 for value in points)


def scalar_word(rows, inverse=False):
    # Earlier row updates leave all later row sums unchanged, since R R^T=56I.
    word = []
    for row in rows:
        word.append(["clear", 112])
        word.extend(["add", 112, p, int(value)] for p, value in row.items())
        word.append(["quarter", 112])
        if inverse:
            word.append(["divide13", 112])
        word.extend(["add", p, 112, -int(value)] for p, value in row.items())
        word.append(["clear", 112])
    return word


def scalar_map(word):
    rows = [{i: Q(1)} for i in range(113)]
    for gate in word:
        op, target = gate[:2]
        if op == "clear":
            rows[target] = {}
        elif op in ("quarter", "divide13"):
            divisor = 4 if op == "quarter" else 13
            rows[target] = {j: value / divisor for j, value in rows[target].items()}
        else:
            require(op == "add", "Unknown scalar instruction")
            for j, value in list(rows[gate[2]].items()):
                result = rows[target].get(j, Q(0)) + gate[3] * value
                if result:
                    rows[target][j] = result
                else:
                    rows[target].pop(j, None)
    return rows


def divider_certificate():
    # Encode (remainder, input bit) by five bits. Build each valid case once.
    # Each indicator uses four AND gates. Five NOT gates supply all literals.
    patterns = [[2 * remainder + bit, (2 * remainder + bit) // 13,
                 (2 * remainder + bit) % 13]
                for remainder in range(13) for bit in range(2)]
    output_ones = [sum((quotient << 4 | remainder) >> i & 1
                       for _, quotient, remainder in patterns) for i in range(5)]
    gates = 5 + 4 * len(patterns) + sum(count - 1 for count in output_ones)
    require(gates == 161, "Unsigned division gate invoice")

    def transition(remainder, bit):
        state = 2 * remainder + bit
        output = 0
        for pattern, quotient, next_remainder in patterns:
            indicator = all(((state >> i) & 1) == ((pattern >> i) & 1) for i in range(5))
            if indicator:
                output |= (quotient << 4) | next_remainder
        return output >> 4, output & 15

    require(all(transition(remainder, bit) == divmod(2 * remainder + bit, 13)
                for remainder in range(13) for bit in range(2)), "All division state transitions")

    def conditional_negation(value, negative, width):
        carry = negative
        result = 0
        for i in range(width):
            bit = ((value >> i) & 1) ^ negative
            result |= (bit ^ carry) << i
            carry &= bit
        return result

    def divide_signed(value, width):
        bits = value & ((1 << width) - 1)
        negative = (bits >> (width - 1)) & 1
        magnitude = conditional_negation(bits, negative, width)
        remainder = quotient = 0
        for i in reversed(range(width)):
            digit, remainder = transition(remainder, (magnitude >> i) & 1)
            quotient = (quotient << 1) | digit
        quotient = conditional_negation(quotient, negative, width)
        signed = quotient - (1 << width) if (quotient >> (width - 1)) & 1 else quotient
        return signed, remainder

    checks = 0
    rejected = 0
    for value in range(-8192, 8192):
        quotient, remainder = divide_signed(value, 14)
        require(remainder == abs(value) % 13, "Signed division remainder")
        if remainder:
            rejected += 1
        else:
            require(13 * quotient == value, "Exact signed division")
        checks += 1
    # Each conditional negation has two XOR gates and one AND per bit.
    # Four AND/OR/NOT gates implement each XOR, so two scans cost 18 per bit.
    return {
        "divisor": 13,
        "valid_state_transitions": 26,
        "unsigned_AND_OR_NOT_gates_per_numerator_bit": gates,
        "signed_AND_OR_NOT_gates_per_numerator_bit": gates + 18,
        "scan_order": "Conditional negation from low to high; unsigned division from high to low; conditional negation from low to high",
        "extra_finite_control_bits_upper_bound": 32,
        "signed_14_bit_inputs_checked": checks,
        "nondivisible_inputs_with_nonzero_remainder": rejected,
        "exactness_condition": "Input numerator is divisible by 13 under the common odd-grid invariant",
        "excluded_costs": ["stream reads and writes", "address routing", "root common-grid conversions"],
    }


def run(repo, interface):
    started = time.monotonic()
    raw = interface.read_bytes()
    require(sha256(raw).hexdigest() == INTERFACE_HASH, "Interface source pin")
    data = json.loads(raw)
    phases, template = sources(repo)
    ports = data["ports"]
    require([entry["q"] for entry in phases["recipes"]] == ports, "Pinned port order")
    require(template["exact_data_phase_recipe_sha256"] == PINS[PHASE], "Template phase reference")
    require(template["route_semantics"]["data"] ==
            "physical cover class d*rho(stage,port); rho is the exact orthogonal involution from data_phases.py",
            "Template cover route")
    require(all(call["owners"][p][1] == [1, call["stage"], p % 112]
                for call in template["calls"] for p in range(224)), "Actual data owner routes")

    points = phase_points(17)
    entry_exit_checks = 0
    character_checks = 0
    tensor_checks = 0
    controls = Counter()
    for entry in phases["recipes"]:
        q = entry["q"]
        chart = basis(q)
        beta = sum((((v.bit_count() - 1) // 2) & 1) << i for i, v in enumerate(chart[1:]))
        local_beta = 0
        for i, v in enumerate(chart[1:]):
            if (beta >> i) & 1:
                local_beta ^= v
        moved_local = [(route(1 << i, chart, 1), 1) for i in range(9)]
        moved_full = [(route(1 << i, chart, 1), 1) for i in range(17)]
        standard_full = [(1 << i, 1) for i in range(17)]
        standard_external = [(1 << i, 1) for i in range(9, 17)]
        dy = q ^ (beta << 9)
        dx = local_beta ^ (beta << 9)
        moved_y = moved_local + [(q, -1)]
        require(equal_phase(moved_y, standard_external, dy, points), "Complete Y bridge phase")
        require(equal_phase(moved_full, standard_full, dx, points), "Complete X bridge phase")
        require(equal_phase(moved_local, [(q, 1)] + standard_external, dy, points),
                "Complete local source entrance phase")
        character_checks += 3 * len(points)
        controls["omitted_Y_translation_rejected"] += not equal_phase(
            moved_y, standard_external, 0, points)
        controls["omitted_X_translation_rejected"] += not equal_phase(
            moved_full, standard_full, 0, points)
        controls["reversed_Y_route_translation_order_rejected"] += not equal_phase(
            moved_y, standard_external, route(dy, chart, 1), points)
        # A tensor correction repeats the translation on both address factors.
        for a, b in zip(points, reversed(points)):
            left = phase(moved_y, a) + phase(moved_y, b)
            right = phase(standard_external, a) + phase(standard_external, b)
            right += 2 * (parity(dy & a) + parity(dy & b))
            require((left - right) % 4 == 0, "Two-factor Fourier operator phase")
            tensor_checks += 1
        for stage, recipe in enumerate(entry["stage_alignment"]):
            if not stage:
                expected_in = expected_out = 0
            else:
                lifted_beta = beta << (9 + 8 * (stage - 1))
                expected_in = q ^ local_beta
                expected_out = local_beta ^ lifted_beta
                require(route(expected_in, chart, stage) == q ^ lifted_beta,
                        "Owner-coordinate entry transport")
                require(route(expected_out, chart, stage) == expected_out,
                        "Owner-coordinate exit transport")
            require(recipe == dict(entry_X=expected_in, entry_Y=expected_in,
                                   exit_X=expected_out, exit_Y=expected_out), "Actual entry/exit gauge")
            entry_exit_checks += 1
    require(all(value == 112 for value in controls.values()), "A phase control was not rejected")

    r = [{int(p): Q(value) for p, value in row.items()} for row in data["R"]]
    require(len(r) == 8 and sum(map(len, r)) == 448, "Centre incidence count")
    require(all(value in (-1, 1) for row in r for value in row.values()), "Centre coefficient alphabet")
    require(all(sum(r[i].get(p, 0) * r[j].get(p, 0) for p in range(112)) == 56 * (i == j)
                for i in range(8) for j in range(8)), "Orthogonal centre rows")
    scalar = {}
    for inverse in (False, True):
        word = scalar_word(r, inverse)
        result = scalar_map(word)
        denominator = 52 if inverse else 4
        expected = []
        for i in range(112):
            values = {}
            for j in range(112):
                value = Q(i == j) - sum(row.get(i, 0) * row.get(j, 0) for row in r) / denominator
                if value:
                    values[j] = value
            expected.append(values)
        expected.append({})
        require(result == expected, "Complete scalar bridge map, including arbitrary private input")
        require(scalar_map(word[1:]) != expected, "Private CLEAR omission control")
        if inverse:
            changed = list(word)
            changed.remove(["divide13", 112])
            require(scalar_map(changed) != expected, "Odd divisor omission control")
        counts = Counter(gate[0] for gate in word)
        bound = 2 * (4 * counts["add"] + 2 * counts["quarter"] + counts["clear"])
        require(bound == 7232, "Dyadic scalar invoice")
        scalar["inverse" if inverse else "forward"] = {
            "events": len(word), "macros": dict(counts), "maximum_live_private_arrays": 1,
            "dyadic_real_primitive_bound": bound,
            "additional_real_divide_by_13_streams": 2 * counts["divide13"],
            "native_children": 0,
            "full_input_columns_checked": 113,
            "private_input_and_output_zero": True,
        }
    return {
        "status": "PASS_EXACT_BRIDGE_OPERATORS_AND_ACTUAL_LOCAL_GAUGE",
        "source_base": BASE, "archive_sha256": ARCHIVE_HASH,
        "source_pins": PINS, "interface_sha256": INTERFACE_HASH,
        "phase_method": "Exact Fourier-character evaluation on all weight-zero, one, and two inputs in the active 17-dimensional space",
        "complete_phase_identity_character_checks": character_checks,
        "actual_stage_entry_exit_gauges_checked": entry_exit_checks,
        "actual_data_owner_routes_checked": len(template["calls"]) * 224,
        "two_factor_phase_checks": tensor_checks,
        "phase_controls": dict(controls),
        "operator_alignment": "A=Z_delta D; A T_boundary=T_common D",
        "logical_bridge": "A^-1 J A T_boundary=T_boundary D J D; the same identity holds for J^-1",
        "actual_local_shear": "D L(J) D or D U(-J^T) D in the pinned boundary gauges",
        "scalar_programs": scalar,
        "divide13_finite_bit_circuit": divider_certificate(),
        "scope": "Exact native operator and finite scalar macro invoice. Address routing, bit division cost, and a complete controller invoice remain separate.",
        "seconds": time.monotonic() - started,
        "maximum_resident_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--interface", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = run(args.repo, args.interface)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"])
    print("phase_gauges=1008 scalar_columns=226 one_private_array=true")
    print("forward_real_bound=7232 inverse_extra_real_divide13_streams=16")

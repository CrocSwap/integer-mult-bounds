"""Emit clean one-core shears in the original complex frames."""

from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
import gzip
import importlib.util
import json


HERE = Path(__file__).resolve().parent
LANES = HERE.parents[1]
ROOT = HERE.parents[4]
CORE_PIN = "f271842a741584389e166e700e262f161b0dd570ce8c7a540f2717e90ead5205"
R_PIN = "5c6c51fbffc07a683e922f17532fd90262ae9e23cc3560a696002073dd234ef3"
MODES = [225, 226, 229, 232, 241, 242, 257, 258]


def need(value, reason):
    if not value:
        raise ValueError(reason)


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def plus(target, source, coefficient):
    for key, value in source.items():
        value = target.get(key, F(0)) + coefficient * value
        if value:
            target[key] = value
        else:
            target.pop(key, None)


def line(row, port, exponent):
    result = {}
    for (origin, word), value in row.items():
        power = exponent
        if word and word[0][0] == port:
            power += word[0][1]
            word = word[1:]
        if power:
            word = ((port, power),) + word
        plus(result, {(origin, word): value}, F(1))
    return result


def compose(matrix, rows):
    result = []
    for coefficients in matrix:
        row = {}
        for index, coefficient in coefficients.items():
            plus(row, rows[index], coefficient)
        result.append(row)
    return result


def main():
    echo = module("original_clean_echo", LANES / "history-encoding/verify_echo.py")
    raw = (ROOT / "work/five-pr-sprint-20261013/lanes/centre-sharing/CANONICAL-WORD.json.gz").read_bytes()
    need(sha256(raw).hexdigest() == echo.PINS["CANONICAL-WORD.json.gz"], "Native word pin")
    word = json.loads(gzip.decompress(raw))
    raw = gzip.decompress((LANES / "history-encoding/FULL-MODE-PROGRAMS.json.gz").read_bytes())
    need(sha256(raw).hexdigest() == CORE_PIN, "Raw core pin")
    core = json.loads(raw)
    raw = (LANES / "circuit-interface/INTERFACE.json").read_bytes()
    need(sha256(raw).hexdigest() == R_PIN, "Actual R pin")
    R = [{int(p): F(q) for p, q in row.items()} for row in json.loads(raw)["R"]]
    K = [{k: row[p] / 4 for k, row in enumerate(R) if p in row} for p in range(112)]
    P = echo.multiply(K, R)
    identity = [{j: F(1)} for j in range(704)]
    formal = [{(j, ()): F(1)} for j in range(704)]

    def add(target, source, coefficient, endpoint):
        return {"kind": "physical_add", "target": target, "source": source,
                "coefficient": str(F(coefficient)), "endpoint": endpoint}

    def scale(target):
        return {"kind": "physical_scale", "target": target,
                "coefficient": "-1", "endpoint": "output"}

    def R_add(bank, coefficient, where):
        return [add(MODES[k], bank + p, coefficient * q, where)
                for k, row in enumerate(R) for p, q in sorted(row.items())]

    def K_add(bank, coefficient, where):
        return [add(bank + p, MODES[k], coefficient * q, where)
                for p, row in enumerate(K) for k, q in sorted(row.items())]

    def endpoint(events, rows, where, output_power=-1):
        result = [row.copy() for row in rows]
        bank, power = (0, 1) if where == "input" else (112, output_power)
        for p in range(112):
            result[bank + p] = line(result[bank + p], p, power)
        for event in events:
            need(event["endpoint"] == where, "Endpoint tag")
            q = F(event["coefficient"])
            if event["kind"] == "physical_add":
                need(event["source"] != event["target"], "Distinct ADD fields")
                plus(result[event["target"]], result[event["source"]], q)
            else:
                need(event["kind"] == "physical_scale", "Literal event kind")
                result[event["target"]] = {key: q * value for key, value in result[event["target"]].items()}
        for p in range(112):
            result[bank + p] = line(result[bank + p], p, -power)
        return result

    programs, checks = {}, {}
    for orientation in ("forward", "backward"):
        echo.check_frames(core[orientation], word)
        raw_map = echo.replay(core[orientation], identity)
        if orientation == "forward":
            prefix = R_add(0, F(1), "input")
            prefix += K_add(112, F(1), "input")
            prefix += R_add(0, F(-1), "input")
            suffix = R_add(0, F(2), "output")
        else:
            prefix = R_add(112, F(-1, 4), "input")
            suffix = R_add(112, F(1, 8), "output")
            suffix += K_add(0, F(-8), "output")
            suffix += R_add(112, F(-1, 8), "output")
        suffix += [scale(slot) for slot in MODES]

        def replay(pre, post, output_power=-1):
            return endpoint(post, compose(raw_map, endpoint(pre, formal, "input")), "output", output_power)

        actual = replay(prefix, suffix)
        expected = [row.copy() for row in formal]
        source, target, sign, phase_power = ((0, 112, F(1), 1) if orientation == "forward"
                                             else (112, 0, F(-1), -1))
        for p in range(112):
            plus(expected[target + p], formal[source + p], sign)
            for j, coefficient in P[p].items():
                plus(expected[target + p], formal[source + j], -sign * coefficient)
                plus(expected[target + p], line(formal[source + j], j, phase_power), sign * coefficient)
        need(actual == expected, orientation + " clean map on all 704 input columns")
        need(all(actual[j] == formal[j] for j in range(224, 704)), "All 480 arbitrary helpers restore")
        need(all(origin < 224 for row in actual[:224] for origin, _ in row),
             "No helper input enters data output")
        need(replay([], suffix) != expected, "Missing prefix control")
        need(replay(prefix, suffix[:-8]) != expected, "Missing final negation control")
        if orientation == "backward":
            need(replay(prefix, suffix, 1) != expected, "Wrong inverse line control")
        else:
            need(replay(prefix[:448] + prefix[896:] + prefix[448:896], suffix) != expected,
                 "Wrong input scatter order control")
        cost = 0
        magnitudes = {}
        for event in prefix + suffix:
            q = F(event["coefficient"])
            if event["kind"] == "physical_add":
                gate = ["add", ["L", 0], ["L", 1], q.numerator, q.denominator]
                magnitudes[str(abs(q))] = magnitudes.get(str(abs(q)), 0) + 1
            else:
                gate = ["scale", ["L", 0], q.numerator, q.denominator]
            cost += 2 * echo.primitive_bound(gate)
        programs[orientation] = {"prefix": prefix, "core_orientation": orientation, "suffix": suffix}
        checks[orientation] = {
            "arbitrary_input_columns": 704, "restored_helper_fields": 480,
            "restored_mode_fields": 8, "helper_input_coefficients_in_data": 0,
            "physical_complex_ADDs": 1792, "physical_complex_negations": 8,
            "ADD_coefficient_magnitudes": magnitudes, "added_real_primitives": cost,
            "core_and_added_real_primitives": 204418 + cost,
            "new_native_children": 0, "new_fields": 0, "new_address_or_phase_maps": 0,
            "retained_native_events": sum(e[0] in ("climb", "adapter", "residual_adapter")
                                          for e in core[orientation]),
            "paid_native_rank": 5522,
        }
    payload = {
        "schema": "original-complex-clean-source-v1", "core_payload_sha256": CORE_PIN,
        "interface_sha256": R_PIN, "width_requirement": "Every positive integer lambda",
        "mode_carriers": MODES, "programs": programs,
        "expansion": "Old entry alignment; the orientation prefix; the unchanged raw core; the orientation suffix; the old exit/owner view. Keep all original idle maps, stage alignments, and the original terminal rule.",
        "event_semantics": "physical_add adds coefficient times the source physical complex field pointwise. Its coefficient is real dyadic, so apply the same real ADD macro to the real and imaginary components. physical_scale negates both components. No source field is overwritten by an ADD.",
        "content_contract": {"D_plus": "I-KR+KRQ", "D_minus": "I-KR+KRQ^-1",
                             "forward": "x'=x, y'=y+D_plus x, all480helpercontents unchanged",
                             "backward": "x'=x-D_minus y, y'=y, all480helpercontents unchanged"},
        "physical_frames": {"X": ["Q", "F"], "Y": ["I", "F Q^-1"], "modes": ["I", "F"]},
        "physical_contract": "Each of all480 helper fields completes its original full native job on arbitrary physical input. The actual owner binding and changed data controller are separate obligations.",
        "source_attribution": "The coordinating agent supplied the all-width cleaning formulas. This emitter binds them to the earlier raw helper-mode core in its original complex frames.",
    }
    raw = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode()
    (HERE / "ORIGINAL-CLEAN-SOURCE-PROGRAMS.json.gz").write_bytes(gzip.compress(raw, mtime=0))
    receipt = {
        "status": "PASS_ORIGINAL_COMPLEX_CLEAN_SOURCE_ALL_WIDTHS",
        "program_payload_sha256": sha256(raw).hexdigest(), "core_payload_sha256": CORE_PIN,
        "interface_sha256": R_PIN, "formal_relation": "Only adjacent Q_p and Q_p^-1 cancel; no finite order or commutation is used.",
        "checks": checks, "paid_profile": {"1": 2412, "2": 418, "3": 432, "4": 142, "5": 82},
        "not_claimed": ["D_plus equals D_minus", "Global changed controller", "Complete supplier invoice"],
    }
    (HERE / "ORIGINAL-CLEAN-SOURCE.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(receipt["status"])
    print(receipt["program_payload_sha256"])
    for name, check in checks.items():
        print(name, check["core_and_added_real_primitives"], check["retained_native_events"])


if __name__ == "__main__":
    main()

"""Check the five current cuts and the complete three-stage raw code."""

from collections import defaultdict
from fractions import Fraction as F
from hashlib import sha256
import gzip
import importlib.util
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
GAUGE = "independent-review-20261017/matched-full-gauge-20261018/FULL-GAUGE.json"
GAUGE_PIN = "ea8717a63861b7bc9acc2d8e8b0501503a928859042e453234a2fc0c65797f89"
SOURCE_PIN = "d2954018666ea2c1b6557615fdf0e6eba7b651fc89e4fdac899b0ccc0f16b839"
CONTROLLER = "encoded-controller/one-pair-current-codes-20261018/PROGRAM.json"
CONTROLLER_PIN = "f66186f2f67ea00eb8ae6447ec9cbddbdf410f141e61149871b0915e599845d7"


def need(ok, label):
    if not ok:
        raise ValueError(label)


def dot(a, b):
    return (a & b).bit_count() & 1


def binary_solution(equations):
    pivots = {}
    for row, rhs in equations:
        while row:
            lead = row.bit_length() - 1
            if lead not in pivots:
                pivots[lead] = (row, rhs)
                break
            old, value = pivots[lead]
            row ^= old
            rhs ^= value
        need(row or not rhs, "Consistent basis extension")
    value = 0
    for lead, (row, rhs) in sorted(pivots.items()):
        if dot(row, value) != rhs:
            value ^= 1 << lead
    need(all(dot(row, value) == rhs for row, rhs in equations), "Exact binary solution")
    return value


def child_basis(base, wanted):
    unit = [1 << j for j in range(25)]
    columns = list(unit)
    transvections = []
    for j, target in enumerate(wanted):
        current = columns[j]
        if current == target:
            continue
        if not dot(current, target):
            changes = [current ^ target]
        else:
            middle = binary_solution([((1 << 25) - 1, 1), (current, 0), (target, 0)]
                                     + [(v, 0) for v in wanted[:j]])
            changes = [current ^ middle, middle ^ target]
        for vector in changes:
            need(vector and not dot(vector, vector), "An orthogonal transvection")
            need(all(not dot(vector, v) for v in wanted[:j]), "The earlier child axes stay fixed")
            columns = [v ^ (vector if dot(vector, v) else 0) for v in columns]
            transvections.append(vector)
        need(columns[j] == target, "The next child axis")
    inverse = [sum(((columns[j] >> i) & 1) << j for j in range(25)) for i in range(25)]
    need(columns[:len(wanted)] == wanted, "The stated native axes")
    need([base.act(columns, v) for v in inverse] == unit, "The left basis inverse")
    need([base.act(inverse, v) for v in columns] == unit, "The right basis inverse")
    return columns, inverse, transvections


def native_record(base, target, source, lines, translation, route, sign=1):
    columns, inverse, steps = child_basis(base, lines)
    need(all(dot(a, b) == int(i == j)
             for i, a in enumerate(lines) for j, b in enumerate(lines)),
         "The native line directions are orthonormal")
    wanted = base.add_phase(base.product([(v, 1) for v in lines]), base.line(translation, 2))
    characters = [0] + [1 << j for j in range(25)]
    characters += [(1 << i) ^ (1 << j) for i in range(25) for j in range(i)]
    for eta in characters:
        transformed = base.act(inverse, eta)
        expected = sum(dot(v, eta) for v in lines) + 2 * dot(translation, eta)
        actual = (transformed & ((1 << len(lines)) - 1)).bit_count() + 2 * dot(translation, eta)
        need((actual - expected) % 4 == 0, "The complete child phase polynomial")
    return {
        "target": target, "source": source, "rank": len(lines), "sign": sign,
        "cover_route_columns": route,
        "child_basis_columns": columns, "child_basis_inverse_columns": inverse,
        "basis_transvections_in_time_order": steps,
        "output_translation": translation,
        "factor_in_output_coordinates": "sign * X_translation * P_G * H_rank * P_G^-1 * P_route",
        "phase": list(wanted), "phase_coefficient_checks": len(characters),
    }


def main():
    path = HERE / "check_matched_access.py"
    need(sha256(path.read_bytes()).hexdigest() == SOURCE_PIN, "Frozen stage checker")
    spec = importlib.util.spec_from_file_location("triple25_source", path)
    source = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(source)
    base, ports, data = source.load()
    need(sha256((source.LANES / CONTROLLER).read_bytes()).hexdigest() == CONTROLLER_PIN,
         "The actual three-call controller pin")
    q = [p["q"] for p in ports]
    unit = [1 << j for j in range(25)]
    mask = (1 << 25) - 1
    views = {(v["stage"], v["port"], v["side"]): v for v in data["views"]["views"]}
    rho = {(s, p): unit if s == 0 else views[s, p, "X"]["route_columns"][:25]
           for s in range(3) for p in range(112)}
    full = base.product([(v, 1) for v in unit])
    matched = source.rows(data["matching"]["response"])
    preferred = [dict(row) for row in matched]
    for p in data["permutation64"]["active_ports"]:
        preferred[p] = source.rows([data["permutation64"]["response"][p]])[0]
    raw = (source.LANES / GAUGE).read_bytes()
    need(sha256(raw).hexdigest() == GAUGE_PIN, "Improved scalar gauge pin")
    gauge = json.loads(raw)
    need(source.rows(gauge["response"]) == preferred, "Improved gauge uses this actual response")
    word = []
    for event in gauge["events"]:
        if event[0] == "add":
            op, p, r, a, b = event
        else:
            op, p, a, b = event
            r = p
        word.append([op, p, r, str(F(a, b))])
    invoice = source.replay(word, preferred)
    need(invoice["real_scalar_primitives"] == 2396 and invoice["peak_row_one_norm"] == "4",
         "Improved scalar invoice and guard")
    source.replay(source.inverse_word(word), preferred)
    small = set(data["permutation64"]["active_ports"])
    dense = set(range(112)) - small
    dense_word = [event for event in word if event[1] in dense]
    need(all(event[2] in dense for event in dense_word), "The dense code has no small-port read")
    dense_target = [preferred[p] if p in dense else {p: F(1)} for p in range(112)]
    dense_invoice = source.replay(dense_word, dense_target)
    source.replay(source.inverse_word(dense_word), dense_target)
    need(dense_invoice["real_scalar_primitives"] == 1564, "The restricted dense scalar invoice")
    cuts = []
    for label, stage, side, level in (("after_F0", 0, "X", 0), ("before_B1", 1, "Y", 0),
                                      ("after_B1", 1, "X", 1), ("before_F2", 2, "Y", 1),
                                      ("after_F2", 1, "X", 2)):
        records = []
        for p in range(112):
            route = rho[stage, p]
            delta = 0 if stage == 0 else views[stage, p, side]["translation_after_route"]
            need(delta <= mask, "The cut translation is in D25")
            terms = [(base.act(route, v), 1) for v in unit[:9 + 8 * level]]
            if side == "Y":
                terms.append((q[p], -1))
            actual = base.add_phase(base.product(terms), base.line(delta, 2))
            axes = unit[:9 + 8 * level] if side == "X" else unit[9:9 + 8 * level] + unit[9 + 8 * (stage - 1):9 + 8 * stage]
            expected = base.product([(v, 1) for v in axes])
            need(actual == expected, "Exact five-cut common frame")
            records.append({"port": p, "route_columns": route, "translation_after_route": delta,
                            "inverse_translation_after_route": base.act(route, delta)})
        cuts.append({"cut": label, "stage_code": stage, "side": side, "global_level": level,
                     "views": records, "scalar_gauge": GAUGE, "scalar_gauge_sha256": GAUGE_PIN,
                     "monomial_view_calls_bound": 224, "real_scalar_primitives": 2396})
    path_records = {}
    reports = {}
    for name, matrix in (("half_hadamard64", matched), ("permutation64", preferred)):
        reports[name] = {}
        for direction, stages in (("T", (2, 1, 0)), ("T_inverse", (0, 1, 2))):
            grouped = defaultdict(set)
            records = []
            orthogonal = 0
            for p, row in enumerate(matrix):
                for j, a in row.items():
                    for k, b in matrix[j].items():
                        for r, c in matrix[k].items():
                            factors = [rho[stages[0], p], rho[stages[0], j], rho[stages[1], j],
                                       rho[stages[1], k], rho[stages[2], k], rho[stages[2], r]]
                            route = list(unit)
                            for factor in reversed(factors):
                                route = [base.act(factor, v) for v in route]
                            key = tuple(route)
                            need(key not in grouped[p, r], "Distinct complete triple owner paths")
                            grouped[p, r].add(key)
                            second = base.act(route, q[r])
                            need(q[p] != second, "The two raw terminal line factors do not cancel")
                            correction = base.add_phase(full, base.negative(base.product([(v, 1) for v in route])))
                            need(correction[0] == correction[2] == 0, "Triple FULL conjugation is a translation")
                            phase = base.add_phase(base.product([(q[p], 1), (second, -1)]), correction)
                            need(phase[0] == q[p] ^ second, "Complete raw triple odd phase")
                            coefficient = a * b * c
                            record = {"target": p, "middle": [j, k], "source": r,
                                      "coefficient": str(coefficient), "route_columns": route,
                                      "lines": [q[p], second], "line_powers": [1, -1],
                                      "FULL_translation": correction[1], "phase": list(phase)}
                            records.append(record)
                            orthogonal += (q[p] & second).bit_count() % 2 == 0
            reports[name][direction] = {"stages": stages, "path_blocks": len(records),
                                        "rank_two_path_blocks": len(records), "orthogonal_line_pairs": orthogonal,
                                        "port_blocks": len(grouped), "first_witness": records[0]}
            if name == "permutation64":
                path_records[direction] = records
    need(reports["permutation64"]["T"]["path_blocks"] == 3136, "Preferred complete triple count")
    need(reports["half_hadamard64"]["T"]["path_blocks"] == 7168, "Alternative complete triple count")
    fused = []
    source_ports = set()
    for record in path_records["T_inverse"]:
        if record["target"] not in small:
            continue
        need(record["coefficient"] == "-1", "The exact small-path scalar sign")
        a, b = record["lines"]
        translation = record["FULL_translation"] ^ b
        child = native_record(base, record["target"], record["source"], [a, b],
                              translation, record["route_columns"], -1)
        need(child["phase"] == record["phase"], "Absorb the inverse line as a translation")
        need(base.add_phase(base.product([(a, 1), (b, 1)]), base.line(translation, 2))
             == tuple(record["phase"]), "The full signed-line identity")
        fused.append(child)
        source_ports.add(record["source"])
    need(len(fused) == 64 and source_ports == small, "The complete small-port bijection")
    dense_lines = []
    for power in (-1, 1):
        for p in sorted(dense):
            dense_lines.append(native_record(base, p, p, [q[p]], q[p] if power == -1 else 0,
                                             unit))
    need(len(dense_lines) == 96, "The two complete dense line passes")
    mixed = {
        "chronology": ["dense48 inverse lines", "dense48 E2 inverse code",
                       "dense48 E1 inverse code", "dense48 E0 inverse code",
                       "dense48 positive lines", "small64 direct rank-two paths"],
        "dense48_line_children": dense_lines, "small64_children": fused,
        "dense48_scalar_inverse_events": source.inverse_word(dense_word),
        "dense48_scalar_code_stages_in_time_order": [2, 1, 0],
        "dense48_code_real_scalar_primitives": 3 * dense_invoice["real_scalar_primitives"],
        "small64_complex_signs": 64, "small64_sign_real_scalar_primitives": 128,
        "profile": {"1": 96, "2": 64}, "native_rank_mass": 224,
        "owned_fields": 0, "private_fields": 0,
        "map_inventory": {"dense48_code_views": 288, "dense48_child_wrappers": 192,
                          "small64_child_wrappers": 128},
        "scope": "Exact operators and native recipes. Recursive hosting and finite map cost are separate.",
    }
    program = {"schema": "matched-triple25-v1", "source_pins": source.PINS,
               "controller_path": CONTROLLER, "controller_sha256": CONTROLLER_PIN,
               "stage_checker_sha256": SOURCE_PIN, "dimension": 25, "five_scalar_codes": cuts,
               "preferred_response": [{str(j): str(c) for j, c in row.items()} for row in preferred],
               "raw_code": "Q (E2 E1 E0) Q^-1", "raw_inverse": "Q (E0 E1 E2) Q^-1",
               "path_records": path_records,
               "safe_native_line_word": ["Q^-1 on112 fields", "three admitted final-FULL scalar E gauges", "Q on112 fields"],
               "safe_native_profile": {"1": 224}, "mixed_native_decoder": mixed,
               "dense_H2_fusion_claimed": False}
    encoded = (json.dumps(program, sort_keys=True, separators=(",", ":")) + "\n").encode()
    (HERE / "TRIPLE25-PROGRAMS.json.gz").write_bytes(gzip.compress(encoded, mtime=0))
    receipt = {"status": "PASS_MATCHED_TRIPLE25_AND_FIVE_CUTS", "source_pins": source.PINS,
               "checker_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
               "program_decompressed_sha256": sha256(encoded).hexdigest(),
               "five_cut_phase_checks": 560, "scalar_gauge_pin": GAUGE_PIN,
               "controller_sha256": CONTROLLER_PIN,
               "independent_scalar_gauge_replay": invoice, "terminal_path_checks": reports,
               "dense48_scalar_gauge_replay": dense_invoice,
               "safe_profile": {"1": 224}, "mixed_profile": mixed["profile"],
               "mixed_native_rank_mass": mixed["native_rank_mass"],
               "mixed_child_phase_coefficient_checks": sum(c["phase_coefficient_checks"]
                                                          for c in fused + dense_lines),
               "mixed_scalar_real_primitives": 3 * dense_invoice["real_scalar_primitives"] + 128,
               "mixed_map_inventory": mixed["map_inventory"],
               "dense_H2_fusion_claimed": False,
               "scope": "Exact current cuts and triple raw operator. No coupled native lower bound or supplier improvement."}
    (HERE / "TRIPLE25-CHECKS.json").write_text(json.dumps(receipt, sort_keys=True, indent=2) + "\n")
    print(receipt["status"])


if __name__ == "__main__":
    main()

"""Combine the last 64 completions with their exact terminal paths."""

from collections import Counter
from hashlib import sha256
import gzip
import importlib.util
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
LANES = HERE.parents[1]
PINS = {
    "stage": ("bridge-access-20261017/matched-stage-access-20261018/check_matched_access.py",
              "d2954018666ea2c1b6557615fdf0e6eba7b651fc89e4fdac899b0ccc0f16b839"),
    "triple_checker": ("bridge-access-20261017/matched-stage-access-20261018/check_triple25.py",
                       "847d0dd8cfaf869b2a425fbd3b05c309d4d5859e8eab7dd1f0cb77dd761d4b57"),
    "triple": ("bridge-access-20261017/matched-stage-access-20261018/TRIPLE25-PROGRAMS.json.gz",
               "b65a2b14a1e61c566063195d0ef363c7dae0d06bb2232e4c872275479f327419"),
    "native": ("oblique-native-20261017/matched-native-involution/MATCHED-NATIVE-PROGRAM.json.gz",
               "95f11d2b13fc75cb0d07e79ea17afdf3f46b4aca294117ffe1a988779e99f025"),
    "permutation": ("history-encoding/permutation64-native-20261018/PERMUTATION64-PROGRAMS.json.gz",
                    "87c76a500f8e22e4b500a5f5a64f23ef8cecadd0036785d7f54b2415972f1ff9"),
    "phase": ("interface-proof/verify_native_lift.py",
              "087ad4cc683e5caf1f2a8cd62d5f65c9b4dde2636593b417f8f5099a29875c8b"),
}


def need(condition, label):
    if not condition:
        raise ValueError(label)


def read(name):
    path, pin = PINS[name]
    raw = (LANES / path).read_bytes()
    if path.endswith(".gz"):
        raw = gzip.decompress(raw)
    need(sha256(raw).hexdigest() == pin, name + " source pin")
    return raw


def module(name):
    read(name)
    spec = importlib.util.spec_from_file_location("rank9_" + name, LANES / PINS[name][0])
    value = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = value
    spec.loader.exec_module(value)
    return value


def rank(vectors):
    pivots = {}
    for value in vectors:
        while value:
            lead = value.bit_length() - 1
            if lead not in pivots:
                pivots[lead] = value
                break
            value ^= pivots[lead]
    return len(pivots)


def root_basis(helper, wanted):
    columns = [1 << j for j in range(9)]
    for j, target in enumerate(wanted):
        current = columns[j]
        if current == target:
            continue
        if helper.dot(current, target):
            middle = helper.binary_solution([(511, 1), (current, 0), (target, 0)]
                                            + [(v, 0) for v in wanted[:j]])
            changes = [current ^ middle, middle ^ target]
        else:
            changes = [current ^ target]
        for vector in changes:
            need(vector < 512 and not helper.dot(vector, vector), "A root orthogonal transvection")
            columns = [v ^ (vector if helper.dot(v, vector) else 0) for v in columns]
        need(columns[:j + 1] == wanted[:j + 1], "The root basis has the required first axes")
    need(all(helper.dot(a, b) == int(i == j) for i, a in enumerate(columns)
             for j, b in enumerate(columns)), "The full root basis is orthonormal")
    return columns


def embed(circuit):
    out = []
    for gate in circuit:
        if gate[0] == "P":
            out.append(("P", tuple(gate[1]) + tuple(1 << j for j in range(9, 25))))
        elif gate[0] == "D":
            out.append(("D", tuple(gate[1]) + (0,) * 16, tuple(gate[2]) + (0,) * 16))
        else:
            out.append(gate)
    return tuple(out)


def scalar_phase(phase, gate, x):
    return (sum(gate[2][i] for i in range(25) if x >> i & 1)
            + 2 * sum(phase.parity((gate[1][i] >> (i + 1)) & (x >> (i + 1)))
                      for i in range(25) if x >> i & 1)) % 4


def monomial_action(phase, circuit, x):
    power = 0
    for gate in circuit:
        if gate[0] == "P":
            x = phase.mul(gate[1], x)
        elif gate[0] == "X":
            x ^= gate[1]
        elif gate[0] == "D":
            power += scalar_phase(phase, gate, x)
        else:
            need(gate[0] == "phase", "A monomial wrapper")
            power += gate[1]
    return x, power % 4


def mono_circuit(record):
    return (("D", tuple(record["quadratic_rows"]), tuple(record["linear_Z4"])),
            ("P", tuple(record["matrix_rows"])), ("X", record["offset"]),
            ("phase", record["phase"]))


def fold_monomial(phase, circuit):
    offset, constant = monomial_action(phase, circuit, 0)
    singles = [monomial_action(phase, circuit, 1 << j) for j in range(25)]
    columns = [x ^ offset for x, _ in singles]
    linear = [(power - constant) % 4 for _, power in singles]
    quadratic = [(linear[j] % 2) << j for j in range(25)]
    for i in range(25):
        for j in range(i):
            x, power = monomial_action(phase, circuit, (1 << i) ^ (1 << j))
            need(x == offset ^ columns[i] ^ columns[j], "The affine wrapper map")
            cross = (power - constant - linear[i] - linear[j]) % 4
            need(cross in (0, 2), "The quadratic wrapper phase")
            if cross:
                quadratic[i] ^= 1 << j
                quadratic[j] ^= 1 << i
    record = {"matrix_rows": list(phase.transpose(columns)), "offset": offset,
              "quadratic_rows": quadratic, "linear_Z4": linear, "phase": constant}
    folded = mono_circuit(record)
    need(phase.tableau(folded, 25) == phase.tableau(circuit, 25),
         "The wrapper has the complete signed Pauli action")
    need(monomial_action(phase, folded, 0) == monomial_action(phase, circuit, 0),
         "The wrapper has the exact constant phase")
    return record


def sparse_state(phase, circuit, basis=0):
    value, denominator = {basis: (1, 0)}, 0
    for gate in circuit:
        tag = gate[0]
        if tag == "C":
            moved = {}
            direction, sign = gate[1:]
            for x, (a, b) in value.items():
                for target, term in ((x, (a - sign * b, b + sign * a)),
                                     (x ^ direction, (a + sign * b, b - sign * a))):
                    old = moved.get(target, (0, 0))
                    moved[target] = (old[0] + term[0], old[1] + term[1])
            value = {x: pair for x, pair in moved.items() if pair != (0, 0)}
            denominator += 1
        elif tag == "P":
            value = {phase.mul(gate[1], x): pair for x, pair in value.items()}
        elif tag == "X":
            value = {x ^ gate[1]: pair for x, pair in value.items()}
        elif tag == "D":
            value = {x: phase.rotate(pair, scalar_phase(phase, gate, x))
                     for x, pair in value.items()}
        else:
            need(tag == "phase", "An exact state gate")
            value = {x: phase.rotate(pair, gate[1]) for x, pair in value.items()}
        while denominator and all((a | b) % 2 == 0 for a, b in value.values()):
            value = {x: (a // 2, b // 2) for x, (a, b) in value.items()}
            denominator -= 1
    return value, denominator


def main():
    source, helper, phase = module("stage"), module("triple_checker"), module("phase")
    base, ports, data = source.load()
    triple = json.loads(read("triple"))
    native = json.loads(read("native"))
    permutation = json.loads(read("permutation"))
    small = set(permutation["active_ports"])
    paths = {r["target"]: r for r in triple["path_records"]["T_inverse"]
             if r["target"] in small}
    views = {(v["stage"], v["port"], v["side"]): v for v in data["views"]["views"]}
    unit = [1 << j for j in range(25)]
    records, reports = {}, {}
    for provider, words in permutation["providers"].items():
        word = words["forward"]
        whole = native["providers"][provider]["forward"]
        need(whole["events"][whole["inherited_64_first_event"]:] == word["events"],
             "The complete core retains the literal 64-port event suffix")
        adapters = {(r["port"], r["role"]): r for r in word["endpoint_adapters"]}
        endpoint_records, total_checks = [], 0
        for p, path in sorted(paths.items()):
            r = path["source"]
            transfer = next(x for x in word["transfers"] if x["source_port"] == p)
            need(transfer["target_port"] == r, "The final transfer and terminal pair agree")
            event = word["events"][transfer["event"] + 2]
            need(event[:2] == ["native", 112 + r] and event[4] == 7,
                 "The last target completion is the required H7")
            for later in word["events"][transfer["event"] + 3:]:
                touched = [later[1]] if later[0] == "native" else later[1][1:3]
                need(112 + r not in touched, "No later local event reads the deferred target")
            completion = word["native_recipes"][event[5]]
            need(completion == whole["native_recipes"][event[5]],
                 "The complete core uses the same rank-seven recipe")
            source_adapter = phase.recipe(adapters[p, "source"])
            target_adapter = phase.recipe(adapters[r, "target"])
            qp, qr = ports[p]["q"], ports[r]["q"]
            local_actual = phase.recipe(completion) + phase.adjoint(target_adapter)
            local_expected = phase.adjoint(source_adapter) + (("C", qp, -1), ("C", qr, -1)) + phase.fourier(9)
            phase.equal(local_actual, local_expected, "The conventional target completion")
            local_basis = root_basis(helper, [qr, qp])
            complement = local_basis[2:9]
            local_phase = base.add_phase(base.product([(v, 1) for v in unit[:9]]),
                                         base.negative(base.product([(v, 1) for v in local_basis[:9]])))
            need(local_phase[0] == local_phase[2] == 0, "The local full-frame correction is a translation")
            local_delta = local_phase[1]
            local_factored = phase.adjoint(source_adapter) + tuple(("C", v, 1) for v in complement) + (("X", local_delta),)
            phase.equal(local_actual, local_factored, "The exact seven-axis completion")
            route = path["route_columns"]
            rho = views[2, r, "X"]["route_columns"][:25]
            composed = [base.act(route, v) for v in rho]
            exit_delta = ports[r]["stage_alignment"][2]["exit_Y"]
            a, b = path["lines"]
            need(a == qp and b == base.act(route, qr), "The terminal line order")
            lines = [a, b] + [base.act(composed, v) for v in complement]
            translation = path["FULL_translation"] ^ base.act(route, exit_delta ^ base.act(rho, local_delta))
            child = helper.native_record(base, p, r, lines, translation, composed, -1)
            right_circuit = embed(phase.adjoint(source_adapter)) + (
                ("P", phase.transpose(composed)), ("P", phase.transpose(child["child_basis_inverse_columns"])))
            left_circuit = (("P", phase.transpose(child["child_basis_columns"])), ("X", translation))
            right, left = fold_monomial(phase, right_circuit), fold_monomial(phase, left_circuit)
            actual = embed(local_actual) + (
                ("P", phase.transpose(rho)), ("X", exit_delta), ("X", qr),
                ("P", phase.transpose(route)), ("C", b, -1), ("C", a, 1),
                ("X", path["FULL_translation"]), ("phase", 2))
            compiled = mono_circuit(right) + tuple(("C", 1 << j, 1) for j in range(9)) + mono_circuit(left) + (("phase", 2),)
            expected_tableau = phase.tableau(actual, 25)
            need(phase.tableau(compiled, 25) == expected_tableau,
                 "The full native completion and terminal have the same signed Pauli action")
            need(sparse_state(phase, compiled) == sparse_state(phase, actual),
                 "The full native completion and terminal have the same exact Gaussian phase")
            need(rank([x for x, _, _ in expected_tableau[25:]]) == 9,
                 "The complete product has Fourier rank nine")
            wrong = dict(left, offset=left["offset"] ^ 1)
            bad = mono_circuit(right) + tuple(("C", 1 << j, 1) for j in range(9)) + mono_circuit(wrong)
            need(phase.tableau(bad, 25) != expected_tableau, "An incorrect output translation is rejected")
            total_checks += child["phase_coefficient_checks"]
            endpoint_records.append({
                "source_field_before_signed_exchange": 112 + r,
                "source_field_after_signed_exchange": r,
                "output_field": p, "source_port": r, "output_port": p,
                "last_transfer_source_port": p, "removed_native_event": transfer["event"] + 2,
                "old_completion_recipe_key": event[5], "rank": 9, "sign": -1,
                "right": right, "left": left, "native_axes": lines,
                "cover_route_columns": composed, "terminal_route_columns": route,
                "stage2_route_columns": rho, "source_canonical_adapter": adapters[p, "source"],
                "local_seven_axes": complement, "local_full_translation": local_delta,
                "output_translation": translation,
                "basis_transvections_in_time_order": child["basis_transvections_in_time_order"],
            })
        need(len(endpoint_records) == 64 and {r["source_port"] for r in endpoint_records} == small,
             "The complete output assignment is a bijection")
        records[provider] = endpoint_records
        reports[provider] = {
            "rank9_children": 64, "signed_Pauli_columns": 64 * 50,
            "complete_Gaussian_state_checks": 64, "local_phase_checks": 128,
            "native_phase_coefficient_checks": total_checks,
            "wrong_translation_controls": 64, "source_and_output_bijection": True,
        }
        print(provider, "PASS_RANK9_COMPLETION", flush=True)
    old = Counter({1: 480, 2: 144, 5: 144, 7: 336, 8: 192})
    old.update({1: 96, 2: 64})
    new = old.copy()
    new.subtract({7: 64, 2: 64})
    new.update({9: 64})
    need(sum(r * c for r, c in old.items()) == sum(r * c for r, c in new.items()) == 5600,
         "The complete native rank is unchanged")
    program = {"schema": "matched-last-completion-rank9-v1", "dimension": 25,
               "source_pins": PINS, "providers": records,
               "complete_native_profile_before": dict(sorted(old.items())),
               "complete_native_profile_after": dict(sorted(new.items())),
               "replaced_children": {"rank7": 64, "rank2": 64}, "new_children": {"rank9": 64},
               "new_wrapper_calls": 128, "complex_signs": 64, "real_sign_primitives": 128,
               "owned_fields": 0, "private_fields": 0,
               "chronology": ["Complete the final 64 scalar transfers at their canonical line cuts.",
                              "Omit their last H7 target completions, target exit adapters, and stage exit maps.",
                              "Complete all remaining disjoint work and the final X-only scalar code.",
                              "Apply the retained signed bank exchange, without its Q^2 map on these 64 ports.",
                              "Apply the emitted H9 recipes to the 64 fields now in the first bank.",
                              "Assign the 64 results to their specified output fields and cover owners."],
               "scope": "Exact adjacent native contraction. No rank saving or complete finite supplier price."}
    raw = (json.dumps(program, sort_keys=True, separators=(",", ":")) + "\n").encode()
    (HERE / "RANK9-PROGRAMS.json.gz").write_bytes(gzip.compress(raw, mtime=0))
    receipt = {"status": "PASS_MATCHED_LAST_COMPLETION_RANK9", "source_pins": PINS,
               "checker_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
               "program_decompressed_sha256": sha256(raw).hexdigest(), "providers": reports,
               "complete_native_profile_before": program["complete_native_profile_before"],
               "complete_native_profile_after": program["complete_native_profile_after"],
               "complete_native_rank": 5600, "child_count_reduction": 64,
               "complete_finite_map_price_claimed": False, "kappa_improvement_claimed": False}
    (HERE / "CHECKS.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(receipt["status"], flush=True)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Exact source-bound tests for grouped rounding in a matching layer.

The independent oracle uses integer divmod, frozen gate inputs, and vector
identities. Only the retained Gaussian-rational scalar representation is reused.
Source write observations add one AST call and leave its arithmetic unchanged.
Substantial OpenAI Codex assistance. Apache-2.0.
"""
import ast
import copy
from fractions import Fraction as Q
from hashlib import sha256
import itertools
import json
from pathlib import Path
import sys
from types import FunctionType

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
EXACT = "research/rational-unitary-fft/exact.py"
ENGINE = "research/rational-unitary-fft/engine.py"
ORACLE = "research/cubic-cyclic-inverse/vendor/interval_kernel.py"
CIRCUIT = "research/capped-phase-fusion/evidence/inplace_algebra_ultra/check_circuits.py"
SOURCE_MANIFEST = "research/rational-unitary-fft/SOURCES.json"
HOOK = "_matching_layer_rounding_observe_write"
C = None


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def rounded_q(value, bits):
    """Nearest grid point, ties toward +infinity; no source rounding helper."""
    numerator = value.numerator * (1 << bits)
    quotient, remainder = divmod(numerator, value.denominator)
    return Q(quotient + int(2 * remainder >= value.denominator), 1 << bits)


def rounded_z(value, bits):
    return C(rounded_q(value.re, bits), rounded_q(value.im, bits))


def norm2(values):
    return sum((v.re * v.re + v.im * v.im for v in values), Q())


def plus(a, b):
    need(len(a) == len(b), "vector addition dimensions")
    return [x + y for x, y in zip(a, b)]


def minus(a, b):
    need(len(a) == len(b), "vector subtraction dimensions")
    return [x - y for x, y in zip(a, b)]


def support(layer, n):
    used = set()
    for ids, gate in layer:
        need(len(ids) in (1, 2) and len(gate) == len(ids)
             and all(len(row) == len(ids) for row in gate), "complete scalar/two-wire gate")
        need(len(set(ids)) == len(ids) and all(type(i) is int and 0 <= i < n for i in ids),
             "valid coordinate support")
        need(not used.intersection(ids), "matching layer: disjoint supports")
        used.update(ids)
    return used


def linear(layer, state):
    """Independent simultaneous linear layer: every gate reads frozen state."""
    support(layer, len(state))
    result = list(state)
    for ids, gate in layer:
        for wire, row in zip(ids, gate):
            result[wire] = sum((coefficient * state[j] for coefficient, j in zip(row, ids)), C())
    return result


def synchronous(layer, state, bits):
    used = support(layer, len(state))
    exact = linear(layer, state)
    return [rounded_z(x, bits) if i in used else x for i, x in enumerate(exact)]


def residual_check(residual, used, bits):
    half = Q(1, 1 << (bits + 1))
    need(all(i in used or x == 0 for i, x in enumerate(residual)), "residual support")
    need(all(abs(x.re) <= half and abs(x.im) <= half for x in residual),
         "one output rounding: component residual bound")
    need(norm2(residual) <= len(used) * 2 * half * half, "aggregate layer residual bound")


def reject(operation, label):
    try:
        operation()
    except ValueError:
        return label
    raise ValueError("control unexpectedly passed: " + label)


def instrument(exact_module, raw_source):
    """Add an observation immediately after the source's sole coordinate write.

    The callback only snapshots tuples; checks run after apply returns. Rebinding
    the generated code to the original module globals preserves the source C
    class's TRACK accounting. The original apply function is never replaced.
    """
    source_tree = ast.parse(raw_source)
    functions = [x for x in source_tree.body if isinstance(x, ast.FunctionDef) and x.name == "apply"]
    need(len(functions) == 1, "one retained apply function")
    original = functions[0]
    need(not any(isinstance(node, ast.Name) and node.id == HOOK for node in ast.walk(original)),
         "fresh observation name")
    wanted = ast.dump(ast.parse("state[i] = value").body[0], include_attributes=False)

    class Observe(ast.NodeTransformer):
        count = 0

        def visit_Assign(self, node):
            if ast.dump(node, include_attributes=False) != wanted:
                return self.generic_visit(node)
            self.count += 1
            hook = ast.parse(HOOK + "(tuple(state), i, tuple(ids))").body[0]
            return [node, ast.copy_location(hook, node)]

    class Strip(ast.NodeTransformer):
        count = 0

        def visit_Expr(self, node):
            if (isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Name)
                    and node.value.func.id == HOOK):
                self.count += 1
                return None
            return self.generic_visit(node)

    observer = Observe()
    observed = ast.fix_missing_locations(observer.visit(copy.deepcopy(original)))
    stripper = Strip()
    stripped = stripper.visit(copy.deepcopy(observed))
    original_dump = ast.dump(original, include_attributes=False)
    need(observer.count == stripper.count == 1, "exactly one write observation inserted/removed")
    need(ast.dump(stripped, include_attributes=False) == original_dump,
         "observation-stripped AST equals original apply AST")
    scratch = {}
    exec(compile(ast.Module(body=[observed], type_ignores=[]), "<observed pinned apply>", "exec"), scratch)
    function = FunctionType(scratch["apply"].__code__, exact_module.__dict__,
                            "observed_apply", exact_module.apply.__defaults__)
    evidence = {"inserted_observation_calls": observer.count,
                "original_apply_ast_sha256": sha256(original_dump.encode()).hexdigest(),
                "stripped_apply_ast_sha256": sha256(ast.dump(stripped, include_attributes=False).encode()).hexdigest(),
                "observed_apply_ast_sha256": sha256(ast.dump(observed, include_attributes=False).encode()).hexdigest()}
    return function, evidence


def trace_writes(exact_module, observed, plan, initial, bits, boundaries, original_result):
    events = []
    need(HOOK not in exact_module.__dict__, "no stale observation hook")
    exact_module.__dict__[HOOK] = lambda state, wire, ids: events.append((state, wire, ids))
    try:
        observed_result = observed(plan, initial, bits)
    finally:
        del exact_module.__dict__[HOOK]
    need(observed_result == original_result, "observed and unmodified source results/statistics agree")
    event_index = 0
    for layer, (before, after) in zip(plan, boundaries):
        written = set()
        exact_after = linear(layer, before)
        layer_residual = minus(after, exact_after)
        for ids, _ in layer:
            for wire in ids:
                need(event_index < len(events), "source write observation present")
                actual, recorded_wire, recorded_ids = events[event_index]
                need(recorded_wire == wire and recorded_ids == tuple(ids), "source coordinate write order")
                written.add(wire)
                splice = tuple(after[i] if i in written else before[i] for i in range(len(before)))
                need(actual == splice, "every source coordinate write splices layer endpoints")
                cut_linear = [exact_after[i] if i in written else before[i] for i in range(len(before))]
                cut_residual = minus(actual, cut_linear)
                need(cut_residual == [z if i in written else C() for i, z in enumerate(layer_residual)],
                     "coordinate-write residual is projected original layer residual")
                residual_check(cut_residual, written, bits)
                need(all(abs(value.re) <= max(abs(before[i].re), abs(after[i].re))
                         and abs(value.im) <= max(abs(before[i].im), abs(after[i].im))
                         for i, value in enumerate(actual)), "coordinate magnitude never exceeds endpoint maximum")
                for i, value in enumerate(actual):
                    for part, start, end in zip((value.re, value.im), (before[i].re, before[i].im),
                                                (after[i].re, after[i].im)):
                        grid, first, last = (x * (1 << bits) for x in (part, start, end))
                        need(grid.denominator == first.denominator == last.denominator == 1,
                             "coordinate writes preserve original data grid")
                        need(abs(grid.numerator).bit_length()
                             <= max(abs(first.numerator).bit_length(), abs(last.numerator).bit_length()),
                             "grid numerator width never exceeds endpoint width")
                need(norm2(actual) <= norm2(before) + norm2(after), "write-cut Euclidean splice envelope")
                event_index += 1
    need(event_index == len(events), "every observed source write checked")
    return events


def check_plan(label, plan, initial, bits, exact_module, observed):
    n = len(initial)
    need(all((part * (1 << bits)).denominator == 1 for z in initial for part in (z.re, z.im)),
         "input on declared data grid")
    current, exact_path, accumulated = list(initial), list(initial), [C() for _ in initial]
    boundaries = []
    permutation_count = prefix_count = nonzero_residuals = signed_ties = 0
    max_residual_component = Q()
    for layer in plan:
        used = support(layer, n)
        before = list(current)
        exact_next = linear(layer, before)
        after = synchronous(layer, before, bits)
        residual = minus(after, exact_next)
        residual_check(residual, used, bits)
        nonzero_residuals += int(any(x != 0 for x in residual))
        max_residual_component = max(max_residual_component,
                                     *(abs(part) for z in residual for part in (z.re, z.im)))
        signed_ties += sum((part * (1 << bits)).denominator == 2
                           for i in used for part in (exact_next[i].re, exact_next[i].im))
        for permutation in itertools.permutations(layer):
            permutation_count += 1
            serial_plan = [[gate] for gate in permutation]
            serial, stats = exact_module.apply(serial_plan, before, bits)
            need(serial == after, "all gate permutations preserve rounded layer endpoint")
            need(stats["rounded_outputs"] == len(used), "one source rounding per touched output")
            for k in range(len(permutation) + 1):
                chosen = list(permutation[:k])
                chosen_support = support(chosen, n)
                actual, prefix_stats = exact_module.apply(serial_plan[:k], before, bits)
                expected = synchronous(chosen, before, bits)
                selected_residual = [z if i in chosen_support else C() for i, z in enumerate(residual)]
                need(actual == expected == plus(linear(chosen, before), selected_residual),
                     "rounded prefix equals exact partial layer plus projected realized residual")
                need(prefix_stats["rounded_outputs"] == len(chosen_support), "prefix rounding count")
                residual_check(minus(actual, linear(chosen, before)), chosen_support, bits)
                prefix_count += 1
        exact_path = linear(layer, exact_path)
        accumulated = plus(linear(layer, accumulated), residual)
        need(minus(after, exact_path) == accumulated, "layer-grouped realized error recurrence")
        current = after
        boundaries.append((before, after))
    original_result = exact_module.apply(plan, initial, bits)
    need(original_result[0] == current, "independent synchronous oracle equals complete unmodified apply")
    writes = trace_writes(exact_module, observed, plan, initial, bits, boundaries, original_result)
    need(original_result[1]["rounded_outputs"] == len(writes), "full source output-rounding count")
    return {"label": label, "dimension": n, "bits": bits, "layers": len(plan),
            "gates": sum(len(layer) for layer in plan), "permutation_orders": permutation_count,
            "rounded_gate_prefixes": prefix_count, "source_coordinate_writes": len(writes),
            "nonzero_layer_residuals": nonzero_residuals, "halfway_components": signed_ties,
            "max_component_residual_in_grid_units": str(max_residual_component * (1 << bits))}


def controls(exact_module, observed):
    bits, u = 3, Q(1, 8)
    controls_out = []
    state = [C(1), C(2)]
    gate = [[C(1), C(1)], [C(1), C(-1)]]
    correct = synchronous([((0, 1), gate)], state, bits)
    overwritten = list(state)
    for i, row in enumerate(gate):
        overwritten[i] = rounded_z(sum((a * z for a, z in zip(row, overwritten)), C()), bits)
    need(correct == [C(3), C(-1)] and overwritten == [C(3), C(1)], "sequential-overwrite witness")
    controls_out.append(reject(lambda: need(overwritten == correct, "mutant differs"), "sequential-overwrite-inside-two-wire-gate"))
    halfgate = [[C(Q(1, 2)), C(Q(1, 2))], [C(Q(1, 2)), C(Q(-1, 2))]]
    pair = [C(u), C(u)]
    termwise = [sum((rounded_z(a * z, bits) for a, z in zip(row, pair)), C()) for row in halfgate]
    linear_pair = linear([((0, 1), halfgate)], pair)
    need(synchronous([((0, 1), halfgate)], pair, bits) == [C(u), C()], "whole-output rounding witness")
    need(termwise[0] == C(2 * u), "extra product-rounding event witness")
    controls_out.append(reject(lambda: residual_check(minus(termwise, linear_pair), {0, 1}, bits), "rounding-each-product-exceeds-layer-budget"))
    a, b = ((0,), [[C(Q(1, 2))]]), ((0,), [[C(Q(3, 2))]])
    controls_out.append(reject(lambda: support([a, b], 1), "overlapping-support-oracle-rejects"))
    controls_out.append(reject(lambda: exact_module.apply([[a, b]], [C(u)], bits), "overlapping-support-source-rejects"))
    ab, _ = exact_module.apply([[a], [b]], [C(u)], bits)
    ba, _ = exact_module.apply([[b], [a]], [C(u)], bits)
    need(ab == [C(2 * u)] and ba == [C(u)], "overlap can destroy rounded commutation")
    controls_out.append("overlap-order-dependence-witness")
    controls_out.append(reject(lambda: residual_check([C(), C(u / 4)], {0}, bits), "residual-leakage-on-idle-wire"))
    # Residuals are functions of actual rounded inputs, never fixed on the exact path.
    first = synchronous([a], [C(u)], bits)
    actual_second = synchronous([a], first, bits)
    actual_r1 = minus(first, linear([a], [C(u)]))
    actual_r2 = minus(actual_second, linear([a], first))
    exact_first = linear([a], [C(u)])
    stale_r2 = minus(synchronous([a], exact_first, bits), linear([a], exact_first))
    need(actual_r1 == actual_r2 == [C(u / 2)] and stale_r2 == [C(-u / 4)], "data-dependent residual witness")
    stale_prediction = plus(plus(linear([a], exact_first), linear([a], actual_r1)), stale_r2)
    controls_out.append(reject(lambda: need(stale_prediction == actual_second, "stale residual invalid"), "residual-computed-on-exact-instead-of-rounded-input"))
    swap = [[((0, 1), [[C(), C(1)], [C(1), C()]])]]
    snapshots = []
    for initial in ([C(), C(1)], [C(1), C(1)]):
        final_result = exact_module.apply(swap, initial, bits)
        events = trace_writes(exact_module, observed, swap, initial, bits,
                              [(initial, synchronous(swap[0], initial, bits))], final_result)
        snapshots.append(events[0][0])
    need(snapshots[0] == snapshots[1] == (C(1), C(1)), "noninjective proper write-cut witness")
    need(norm2(snapshots[0]) == 2 and norm2([C(), C(1)]) == 1, "Euclidean amplification at a source write")
    return controls_out, {"input": [["0", "0"], ["1", "0"]],
                          "first_write_state": [["1", "0"], ["1", "0"]],
                          "input_squared_norm": "1", "first_write_squared_norm": "2",
                          "component_magnitude_bound": "1", "noninjective": True,
                          "extra_observed_source_writes": 4}


def main():
    global C
    manifest = json.loads((HERE / "SOURCES.json").read_text())
    raw = {}
    for row in manifest["files"]:
        if row["usage"] == "input":
            contents = (ROOT / row["path"]).read_bytes()
            need(sha256(contents).hexdigest() == row["sha256"], "authenticated source: " + row["path"])
            raw[row["path"]] = contents
    need({EXACT, ENGINE, ORACLE, CIRCUIT, SOURCE_MANIFEST}.issubset(raw), "complete runtime source closure")
    child_sources = {row["path"]: row["sha256"] for row in json.loads(raw[SOURCE_MANIFEST])["files"]}
    need(all(child_sources[path] == sha256(raw[path]).hexdigest() for path in (ORACLE, CIRCUIT)),
         "retained Builder input authentication")
    sys.path.insert(0, str(ROOT / "research/rational-unitary-fft"))
    import exact
    from engine import Builder, Phases
    C = exact.C
    observed, observation_evidence = instrument(exact, raw[EXACT])
    cases = []
    bits, u = 3, Q(1, 8)
    for numerator, expected in zip((-5, -3, -1, 1, 3, 5), (-2, -1, 0, 1, 2, 3)):
        value = Q(numerator, 2) * u
        need(rounded_q(value, bits) == expected * u, "signed half-grid tie convention")
        plan = [[((0,), [[C(value, -value)]])]]
        cases.append(check_plan("signed-complex-half-tie-" + str(numerator), plan, [C(1)], bits, exact, observed))
    plan = [
        [((0, 2), [[C(Q(1, 2)), C(Q(1, 2))], [C(Q(1, 2)), C(Q(-1, 2))]]),
         ((3,), [[C(Q(1, 3), Q(1, 5))]])],
        [((0, 1), [[C(1), C(0, Q(1, 2))], [C(Q(-1, 3)), C(1)]]),
         ((2,), [[C(Q(2, 3))]]), ((3,), [[C(Q(3, 2), Q(-1, 4))]])],
        [],
    ]
    initial = [C(u, u), C(-2 * u, u), C(u, -u), C(3 * u, 2 * u), C(-u)]
    cases.append(check_plan("mixed-scalar-two-wire-complex-with-idle-and-empty-layer", plan, initial, bits, exact, observed))
    half = ((0,), [[C(Q(1, 2))]])
    cases.append(check_plan("data-dependent-two-layer-half-rounding", [[half], [half]], [C(u)], bits, exact, observed))
    builder = Builder(Phases(10, raw[ORACLE]), 10, raw[CIRCUIT])
    toeplitz = exact.Mat([[C(Q(1, 2)), C(Q(1, 4), Q(1, 8))],
                         [C(Q(-1, 8), Q(1, 16)), C(Q(1, 2))]])
    actual_plan = builder.plan(toeplitz)
    actual_inputs = [[C(3 * u, u), C(-2 * u, 3 * u), C(5 * u, -2 * u), C(-u, -4 * u)],
                     [C(u), C(), C(-2 * u, u), C(3 * u, -u)]]
    for i, initial in enumerate(actual_inputs):
        cases.append(check_plan("actual-Builder-Toeplitz-shear-n2-input" + str(i), actual_plan, initial,
                                bits, exact, observed))
    negative_controls, write_witness = controls(exact, observed)
    need(any(case["nonzero_layer_residuals"] >= 2 for case in cases), "multiple realized nonzero residuals exercised")
    result = {"status": "PASS_MATCHING_LAYER_ROUNDING", "schema_version": 1,
              "arithmetic": "exact Gaussian rationals; independent integer-divmod rounding",
              "sources_authenticated": len(raw), "cases": cases,
              "total_permutation_orders": sum(c["permutation_orders"] for c in cases),
              "total_rounded_gate_prefixes": sum(c["rounded_gate_prefixes"] for c in cases),
              "total_source_coordinate_writes": sum(c["source_coordinate_writes"] for c in cases) + 4,
              "observation": observation_evidence, "controls": negative_controls,
              "write_cut_singular_witness": write_witness,
              "Builder_source_ast_sha256": builder.original_ast,
              "Builder_adapted_ast_sha256": builder.adapted_ast,
              "scope": "Finite source-bound evidence for layer-grouped residuals and coordinate-write splices; no physical-tape execution, all-size proof-kernel acceptance, or inverse contract inside a gate."}
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()

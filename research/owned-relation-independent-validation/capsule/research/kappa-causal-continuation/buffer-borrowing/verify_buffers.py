#!/usr/bin/env python3
"""Independent literal native replay with arbitrary dirty cleanup buffers.

The retained emitter supplies words; this module imports no retained evaluator.
Free warp symbols distinguish primal and inverse-transpose operators. Physical
phase receipts are authenticated inherited evidence, not regenerated here.
Apache-2.0. Substantial OpenAI assistance.
"""
from collections import Counter, defaultdict
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
import argparse
import ast
import gzip
import json


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CORE = ROOT / "research/kappa-native-resume/native-source/rebased-core"
PACKET = ROOT / "research/kappa-native-resume/causal-controller/sources/research/joint-query/certificate.json.gz"
TAGS = ("THREE-base", "THREE-extra", "FOUR-base", "FOUR-extra")
Q = Fraction


def need(condition, message):
    if not condition:
        raise ValueError(message)


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == ".gz" else raw)


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def authenticate():
    pins = read(HERE / "SOURCES.json")
    for relative, expected in pins.items():
        need(digest(ROOT / relative) == expected, "Changed retained source: " + relative)
    return pins


def emit_original(canonical):
    """Reuse only the pinned source's pure writer; no source verifier executes."""
    source = CORE / "sources/bw_emit.py"
    names = {"basis", "reg", "dual", "scalar", "lregs", "expand", "emit", "primitive_bound"}
    tree = ast.parse(source.read_text())
    functions = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in names]
    need({n.name for n in functions} == names, "Exact writer function inventory")
    context = dict(c=canonical, frames=canonical["frames"], v=112, R=408, h=9, n=632, Q=Q)
    exec(compile(ast.Module(body=functions, type_ignores=[]), str(source), "exec"), context)
    return {"forward": context["emit"](False), "backward": context["emit"](True)}


def span(basis):
    points = {0}
    for vector in basis:
        need(isinstance(vector, int) and 0 <= vector < 512, "Nine-dimensional frame")
        points |= {v ^ vector for v in tuple(points)}
    return frozenset(points)


def identity(role):
    return {(role, ()): Q(1)}


def add(destination, source, coefficient):
    for key, value in tuple(source.items()):
        value = destination.get(key, Q(0)) + coefficient * value
        if value:
            destination[key] = value
        else:
            destination.pop(key, None)


def warp(row, operator, backward):
    symbol = (1 if operator > 0 else -1) * (abs(operator) + (10**6 if backward else 0))
    out = {}
    for (variable, word), coefficient in row.items():
        moved = word[1:] if word and word[0] == -symbol else (symbol,) + word
        key = variable, moved
        out[key] = out.get(key, Q(0)) + coefficient
    return {k: v for k, v in out.items() if v}


def expected(role, R, backward, clean):
    out = identity(role)
    name, i = role
    if name != "L":
        return out
    target = i < 112 if backward else 112 <= i < 224
    if not target:
        return out
    port = i if backward else i - 112
    source_offset = 112 if backward else 0
    sign = -1 if backward else 1
    add(out, identity(("L", source_offset + port)), Q(sign))
    if clean:
        for query in R:
            if port in query:
                for j, value in query.items():
                    add(out, identity(("L", source_offset + j)), -sign * query[port] * value / 4)
    return out


def replay(program, canonical, R, backward, clean, omit_cleanup_last=False):
    """All L inputs and all Z inputs are independent, including dirty outputs."""
    n = 2 * canonical["v"] + canonical["R"]
    need(n == 632, "Retained compact width")
    rows = {("L", i): identity(("L", i)) for i in range(n)}
    current = {("L", i): frame for i, frame in enumerate(canonical["start"])}
    center_indices = set()
    for event in program:
        if event[0] == "scalar":
            op = event[1]
            for register in op[1:3] if op[0] in ("add", "copy") else op[1:2]:
                if register[0] == "C":
                    center_indices.add(register[1])
        elif event[0] == "center":
            center_indices.add(event[1])
    need(center_indices <= set(range(8)), "Known center workspace indices")
    for i in center_indices:
        rows["C", i] = identity(("C", i))
        current["C", i] = None
    spaces = [span(vectors) for vectors in canonical["frames"]]
    dimensions = [len(s).bit_length() - 1 for s in spaces]
    need(dimensions[1] == 9, "Cleanup uses the full native frame")
    live = set()
    profile = Counter()
    counts = Counter()
    scalar_primitives = 0
    cleanup_start = next(i for i, event in enumerate(program) if event == ["phase", "full_frame_cleanup"])
    last_scalar = max(i for i, event in enumerate(program) if event[0] == "scalar" and i > cleanup_start)
    for position, event in enumerate(program):
        kind = event[0]
        counts[kind] += 1
        if kind in ("climb", "center"):
            if kind == "climb":
                _, part, index, old, new, rank = event
                role = "L", index
                need(spaces[old] < spaces[new], "Non-nested or empty paid climb")
            else:
                _, index, old, new, rank = event
                role = "C", index
                need(spaces[old] < spaces[new] or spaces[new] < spaces[old], "Center residual is not nested")
            need(current[role] == old and rank == abs(dimensions[new] - dimensions[old]), "Paid edge source/rank")
            current[role] = new
            profile[rank] += 1
        elif kind == "zero_buffer":
            _, action, index = event
            role = "Z", index
            if action == "alloc":
                need(role not in rows and role not in live, "Cleanup buffer duplicate")
                rows[role] = identity(role)
                current[role] = 1
                live.add(role)
            else:
                need(action == "free" and role in live and current[role] == 1, "Cleanup buffer retirement")
                live.remove(role)
        elif kind == "warp":
            _, role, operator, old, new = event
            role = tuple(role)
            need(current[role] == old, "Warp entrance frame")
            rows[role] = warp(rows[role], operator, backward)
            current[role] = new
        elif kind == "scalar":
            op, frame = event[1:]
            target = tuple(op[1])
            if op[0] == "clear":
                need(target[0] == "C", "A borrowed input was cleared")
                rows[target] = {}
                current[target] = frame
                scalar_primitives += 1
                continue
            need(current[target] == frame, "Scalar target frame")
            if op[0] in ("add", "copy"):
                source = tuple(op[2])
                need(current[source] == frame, "Scalar source frame")
                if op[0] == "copy":
                    need(target[0] == "C", "Copy overwrites borrowed state")
                    rows[target] = dict(rows[source])
                    scalar_primitives += 1
                    continue
                coefficient = Q(op[3], op[4])
                need(target != source, "Self-ADD is not a reversible shear")
                numerator, denominator = abs(coefficient.numerator), coefficient.denominator
                need(numerator and denominator & (denominator - 1) == 0, "Non-dyadic ADD")
                scalar_primitives += 3 + numerator.bit_length() - 1 + numerator.bit_count() + denominator.bit_length() - 1
                if not (omit_cleanup_last and position == last_scalar):
                    add(rows[target], rows[source], coefficient)
            else:
                need(op[0] == "scale", "Unknown scalar event")
                coefficient = Q(op[2], op[3])
                numerator, denominator = abs(coefficient.numerator), coefficient.denominator
                need(numerator and numerator & (numerator - 1) == 0 and denominator & (denominator - 1) == 0,
                     "Nonunit dyadic SCALE")
                scalar_primitives += abs(numerator.bit_length() - denominator.bit_length()) + int(coefficient < 0)
                if not (omit_cleanup_last and position == last_scalar):
                    rows[target] = {k: coefficient * v for k, v in rows[target].items()}
        else:
            need(kind in ("phase", "adapter", "residual_adapter"), "Unknown native event")
    need(not live and [current["L", i] for i in range(n)] == canonical["final"], "Retired fields/final frames")
    need(dict(profile) == {int(k): v for k, v in canonical["local_profile"].items()}, "Complete paid profile")
    mismatches = []
    for role, actual in rows.items():
        wanted = {} if role[0] == "C" else expected(role, R, backward, clean)
        if actual != wanted:
            mismatches.append({"role": list(role), "unequal_coefficients": sum(actual.get(k, 0) != wanted.get(k, 0) for k in set(actual) | set(wanted))})
    if not omit_cleanup_last:
        need(not mismatches, "Native dirty-buffer operator mismatch: " + repr(mismatches[:3]))
    else:
        need(mismatches, "Missing-cleanup negative control unexpectedly accepted")
    buffer_count = sum(role[0] == "Z" for role in rows)
    return dict(direction="backward" if backward else "forward", clean_J=clean,
                independent_borrowed_input_fields=632+buffer_count, original_data_fields=224,
                expected_restored_helpers=408, expected_restored_arbitrary_cleanup_buffers=buffer_count,
                explicitly_owned_C_fields_cleared=len(center_indices), event_counts=dict(counts),
                paid_profile=dict(sorted(profile.items())), paid_rank_mass=sum(k*v for k,v in profile.items()),
                conservative_real_scalar_primitive_allowance=2*scalar_primitives,
                all_scalar_frames_checked=True, dyadic_coefficients_and_unit_scales_checked=True,
                free_warp_operator_endpoint_matches=not mismatches,
                negative_control_omitted_last_cleanup_scalar=omit_cleanup_last,
                mismatch_examples=mismatches[:3])


def liveness(canonical):
    times = defaultdict(list)
    for i, event in enumerate(canonical["cleanup"]):
        for role in event[1:3] if event[0] == "add" else event[1:2]:
            role = tuple(role) if isinstance(role, list) else ("L", role)
            times[role].append(i)
    full = [i for i, f in enumerate(canonical["final"]) if f == 1]
    candidates = []
    for z in canonical["zero_buffers"]:
        begin, end = min(times["Z", z]), max(times["Z", z])
        possible = [i for i in range(112) if all(t < begin or t > end for t in times["L", i])]
        candidates.append(dict(buffer=z, first_use=begin, last_use=end,
                               noninterfering_same_call_X_candidates=possible,
                               noninterfering_full_frame_L_candidates=[i for i in full if all(t < begin or t > end for t in times["L", i])]))
    return dict(full_frame_live_roles=len(full), full_frame_roles_unused_in_cleanup=[i for i in full if not times["L", i]],
                same_call_X_outputs_touched=sum(bool(times["L", i]) for i in range(112)),
                buffers_with_no_noninterfering_same_call_X=sum(not row["noninterfering_same_call_X_candidates"] for row in candidates),
                buffers_with_no_noninterfering_full_frame_L=sum(not row["noninterfering_full_frame_L_candidates"] for row in candidates),
                intervals=candidates,
                conclusion="Arbitrary-buffer restoration does not establish a legal same-call completed-output alias.",
                external_same_frame_bank_requirement=91,
                external_bank_hosting_constructed=False)


def find_aliases(canonical):
    """Injective lifetime-safe matching; no native L access during its Z span."""
    options = {row["buffer"]: row["noninterfering_full_frame_L_candidates"]
               for row in liveness(canonical)["intervals"]}
    owner = {}

    def augment(z, seen):
        for role in options[z]:
            if role in seen:
                continue
            seen.add(role)
            if role not in owner or augment(owner[role], seen):
                owner[role] = z
                return True
        return False

    for z in sorted(options, key=lambda z: (len(options[z]), z)):
        augment(z, set())
    bindings = {z: role for role, z in owner.items()}
    need(len(set(bindings.values())) == len(bindings), "Alias must be injective")
    need(all(role in options[z] for z, role in bindings.items()), "Interfering alias")
    return bindings


def alias_program(program, bindings):
    """Replace only Z register operands, retaining every native/scalar event."""
    out = []

    def mapped(role):
        return ["L", bindings[role[1]]] if role[0] == "Z" and role[1] in bindings else list(role)

    for event in program:
        if event[0] == "zero_buffer" and event[2] in bindings:
            continue
        if event[0] == "scalar":
            op = event[1].copy()
            op[1] = mapped(op[1])
            if op[0] in ("add", "copy"):
                op[2] = mapped(op[2])
            out.append(["scalar", op, event[2]])
        elif event[0] == "warp":
            out.append([event[0], mapped(event[1]), *event[2:]])
        else:
            out.append(event)
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=HERE / "RESULT.json")
    args = parser.parse_args()
    pins = authenticate()
    R = [{int(k): Q(v) for k, v in row.items()} for row in read(PACKET)["R_rows"]]
    providers = {}
    for tag in TAGS:
        providers[tag] = {}
        for clean in (False, True):
            folder = "converted" if clean else "sources"
            canonical = read(CORE / folder / (tag + "-CANONICAL.json.gz"))
            programs = read(CORE / folder / (tag + "-NATIVE-WORD.json.gz")) if clean else emit_original(canonical)
            checks = [replay(programs[direction], canonical, R, direction == "backward", clean)
                      for direction in ("forward", "backward")]
            bindings = find_aliases(canonical)
            aliases = {direction: alias_program(program, bindings) for direction, program in programs.items()}
            aliased_checks = [replay(aliases[direction], canonical, R, direction == "backward", clean)
                              for direction in ("forward", "backward")]
            need(len(bindings) == 53, "Expected source-bound 53-field lifetime match")
            for original, aliased in zip(checks, aliased_checks):
                need(original["paid_profile"] == aliased["paid_profile"] and
                     original["conservative_real_scalar_primitive_allowance"] == aliased["conservative_real_scalar_primitive_allowance"],
                     "Aliasing changes the charged operation list")
            providers[tag]["clean_J" if clean else "ordinary"] = dict(checks=checks, liveness=liveness(canonical),
                lifetime_alias_bindings={str(z): role for z, role in sorted(bindings.items())},
                aliased_checks=aliased_checks,
                eliminated_cleanup_fields=len(bindings), remaining_cleanup_fields=91-len(bindings),
                aliased_word_sha256={direction: sha256(json.dumps(program, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
                                     for direction, program in aliases.items()})
        print("PASS all arbitrary cleanup inputs", tag, flush=True)
    canonical = read(CORE / "converted/THREE-base-CANONICAL.json.gz")
    programs = read(CORE / "converted/THREE-base-NATIVE-WORD.json.gz")
    controls = [replay(programs[direction], canonical, R, direction == "backward", True, True)
                for direction in ("forward", "backward")]
    result = dict(schema="literal-native-dirty-buffers/1", status="PASS_NATIVE_ARBITRARY_DIRTY_BUFFER_REPLAY",
                  new_multiplication_kappa=False, physical_phase_generation_rerun=False,
                  phase_evidence="Pinned inherited exact native phase receipts; unchanged native edges.",
                  source_hashes=pins, verifier_sha256=digest(Path(__file__)), providers=providers,
                  negative_controls=controls,
                  lifetime_safe_local_full_frame_aliases_per_word=53,
                  remaining_external_bank_fields_per_word=38,
                  all_91_local_output_alias_claim=False, external_bank_placement_and_cost_closed=False)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(result["status"], flush=True)


if __name__ == "__main__":
    main()

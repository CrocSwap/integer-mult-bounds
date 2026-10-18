"""Exact finite JP8 numerator-recoding check. Apache-2.0, Codex assisted."""

import ast
from collections import Counter
from fractions import Fraction as Q
from functools import lru_cache
import gzip
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lowering import circuit

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PROVIDER = "research/community-k492-audit/pr626/replay/mixed-global/base/providers/jp8/"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def load_sources():
    sources = json.loads((HERE / "SOURCES.json").read_text())
    data = {}
    for name, pin in sources["files"].items():
        raw = (ROOT / name).read_bytes()
        require(hashlib.sha256(raw).hexdigest() == pin["sha256"], "source drift: " + name)
        blob = b"blob " + str(len(raw)).encode() + b"\0" + raw
        require(hashlib.sha1(blob).hexdigest() == pin["git_blob"], "blob drift: " + name)
        if name.endswith(".gz"):
            raw = gzip.decompress(raw)
            require(hashlib.sha256(raw).hexdigest() == pin["payload_sha256"], "payload drift")
        data[name] = raw
    return data


def execute(ops):
    """Independent three-column interpreter; no digit identities assumed."""
    rows = {r: [Q(i == j) for j in range(3)] for i, r in enumerate(("t", "s", "w"))}
    scratch_peak = Q(0)
    for op in ops:
        tag, target, *rest = op
        if tag == "clear":
            rows[target] = [Q(0)] * 3
        elif tag in ("double", "half"):
            rows[target] = [x * (2 if tag == "double" else Q(1, 2)) for x in rows[target]]
        elif tag in ("add", "sub"):
            sign = 1 if tag == "add" else -1
            rows[target] = [x + sign*y for x, y in zip(rows[target], rows[rest[0]])]
        else:
            raise ValueError("unknown primitive")
        scratch_peak = max(scratch_peak, sum(map(abs, rows["w"])))
    return rows, scratch_peak


def validate_circuit(q, ops):
    require(ops[0] == ("clear", "w") and ops[-1] == ("clear", "w"), "private boundary")
    require(ops[-2] == ("add" if q > 0 else "sub", "t", "w"), "target boundary")
    require(all(op in (("double", "w"), ("half", "w"), ("add", "w", "s"), ("sub", "w", "s"))
                for op in ops[1:-2]), "coefficient preparation touches an external register")
    rows, peak = execute(ops)
    require(rows == {"t": [Q(1), q, Q(0)], "s": [Q(0), Q(1), Q(0)], "w": [Q(0)]*3},
            "coefficient boundary or private erasure failed")
    require(peak <= abs(q.numerator) + 1, "scratch peak exceeds numerator plus one")
    return peak


@lru_cache(None)
def checked(q):
    old, new = circuit(q, False), circuit(q)
    old_peak = validate_circuit(q, old)
    new_peak = validate_circuit(q, new)
    require(old_peak == abs(q.numerator), "reference scratch bound")
    require(len(new) <= len(old), "cost regression")
    return old, new, old_peak, new_peak


def add_row(target, source, q):
    result = dict(target)
    for key, value in source.items():
        value = result.get(key, Q(0)) + q*value
        if value:
            result[key] = value
        else:
            result.pop(key, None)
    return result


def replay(events, orientation, native_bound, canonical, original_checks, prior):
    n, v = 2*canonical["v"] + canonical["R"], canonical["v"]
    state = {("L", r): {r: Q(1)} for r in range(n)}
    envelope = {r: Q(1) for r in state}
    peaks = [Q(1), Q(1)]
    counts = [0, 0]
    paid, coefficients = Counter(), Counter()
    changed = overshoots = macros = 0
    recipe = []
    for index, event in enumerate(events):
        if event[0] in ("climb", "center"):
            paid[event[5] if event[0] == "climb" else event[4]] += 1
        elif event[0] == "scalar":
            macros += 1
            op = event[1]
            tag, target = op[0], tuple(op[1])
            old_count = new_count = native_bound(op)
            if tag == "clear":
                state[target], envelope[target] = {}, Q(0)
            elif tag == "copy":
                source = tuple(op[2])
                state[target], envelope[target] = dict(state[source]), envelope[source]
            elif tag == "scale":
                q = Q(op[2], op[3])
                state[target] = {r: q*x for r, x in state[target].items()}
                envelope[target] *= abs(q)
            elif tag == "add":
                source, q = tuple(op[2]), Q(op[3], op[4])
                require(target != source, "aliased scalar operands")
                old, new, old_peak, new_peak = checked(q)
                require(len(old) == old_count, "native invoice mismatch")
                new_count = len(new)
                coefficients[str(q)] += 1
                for i, scratch in enumerate((old_peak, new_peak)):
                    peaks[i] = max(peaks[i], scratch*envelope[source])
                if new_count < old_count:
                    changed += 1
                    overshoots += new_peak > old_peak
                    recipe.append([index, str(q), new])
                # The three-column primitive check supplies this exact macro map.
                state[target] = add_row(state.get(target, {}), state[source], q)
                envelope[target] = envelope.get(target, Q(0)) + abs(q)*envelope[source]
            else:
                raise ValueError("unknown scalar operation")
            for i, count in enumerate((old_count, new_count)):
                counts[i] += 2*count
                peaks[i] = max(peaks[i], envelope[target])
        else:
            require(event[0] in ("adapter", "residual_adapter", "phase"), "unknown event")
    for r in range(n):
        expected = {r: Q(1)}
        if orientation == "forward" and v <= r < 2*v:
            expected[r-v] = Q(1)
        elif orientation == "backward" and r < v:
            expected[v+r] = Q(-1)
        require(state[("L", r)] == expected, "scalar projection column mismatch")
    require(all(not row for r, row in state.items() if r[0] == "C"), "centre dirt remains")
    require(counts[0] == original_checks["real_component_primitive_bound"], "original cost receipt")
    require(macros == original_checks["scalar_macros"], "original macro receipt")
    require(dict(paid) == {int(r): k for r, k in canonical["local_profile"].items()}, "paid profile")
    bits = [x.numerator.bit_length() - x.denominator.bit_length() + 1 for x in peaks]
    require(peaks[0] == Q(prior["prefix_l1_upper"]) and bits[0] == prior["prefix_bits_upper"],
            "reference envelope receipt")
    require(peaks[1] < 2**prior["charged_payload_bits"], "retained local payload exceeded")
    return {
        "events": len(events), "scalar_macros": macros, "scalar_projection_columns": n,
        "distinct_signed_coefficients": len(coefficients), "changed_additions": changed,
        "changed_with_scratch_overshoot": overshoots,
        "real_primitives_before": counts[0], "real_primitives_after": counts[1],
        "saved_real_primitives": counts[0] - counts[1],
        "prefix_l1_before": str(peaks[0]), "prefix_l1_after": str(peaks[1]),
        "prefix_bits_before": bits[0], "prefix_bits_after": bits[1],
        "charged_local_payload_bits": prior["charged_payload_bits"],
        "paid_profile": {str(k): z for k, z in sorted(paid.items())},
        "changed_recipe_sha256": digest(recipe), "coefficient_census_sha256": digest(coefficients),
    }


def controls():
    def rejected(action):
        try:
            action()
        except ValueError:
            return
        raise ValueError("negative control was accepted")

    q = Q(31, 8)
    ops = circuit(q)
    require(len(ops) < len(circuit(q, False)), "control witness must improve")
    mutants = {
        "wrong_signed_digit": [("add", *op[1:]) if op[0] == "sub" else op for op in ops],
        "missing_initial_clear": ops[1:],
        "missing_final_clear": ops[:-1],
        "missing_target_accumulation": ops[:-2] + ops[-1:],
    }
    half = next(i for i, op in enumerate(ops) if op[0] == "half")
    mutants["missing_halving"] = ops[:half] + ops[half+1:]
    for mutant in mutants.values():
        rejected(lambda mutant=mutant: validate_circuit(q, mutant))
    rejected(lambda: circuit(Q(1, 3)))
    rejected(lambda: circuit(0))
    rejected(lambda: require(validate_circuit(q, ops) <= 31, "undercharged scratch"))
    # An endpoint-neutral target excursion must not bypass the scratch-only proof.
    excursion = ops[:-2] + [("double", "t"), ("half", "t")] + ops[-2:]
    rejected(lambda: validate_circuit(q, excursion))
    return list(mutants) + ["nondyadic", "zero", "undercharged_scratch", "target_excursion"]


def verify():
    data = load_sources()
    emitter = "research/complex-k492-owner-repair/code/hpe_emit_local.py"
    tree = ast.parse(data[emitter])
    node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "primitive_bound")
    scope = {"Q": Q}
    exec(compile(ast.Module(body=[node], type_ignores=[]), emitter, "exec"), scope)
    programs = json.loads(data[PROVIDER + "LOCAL-PROGRAMS.json.gz"])
    canonical = json.loads(data[PROVIDER + "CANONICAL-WORD.json.gz"])
    original = json.loads(data[PROVIDER + "LOCAL-CHECKS.json"])
    prior = json.loads(data[PROVIDER + "INDEPENDENT-LOCAL-REPLAY.json"])
    require(set(programs) == {"forward", "backward"}, "orientation inventory")
    require((canonical["v"], canonical["R"], canonical["h"]) == (112, 492, 9), "source geometry")
    results = {o: replay(programs[o], o, scope["primitive_bound"], canonical, original[o], prior["local"][o])
               for o in ("forward", "backward")}
    return {"status": "PASS_COMPLEX_SIGNED_DIGIT", "provider": "jp8", "assignment_seed": 36,
            "programs": results, "negative_controls": controls()}


if __name__ == "__main__":
    require(sys.argv[1:] in ([], ["--report"]), "usage: verify.py [--report]")
    receipt = verify()
    if sys.argv[1:] == ["--report"]:
        print(json.dumps(receipt, indent=2))
    else:
        require(receipt == json.loads((HERE / "EXPECTED.json").read_text()), "committed receipt mismatch")
        print("PASS_COMPLEX_SIGNED_DIGIT jp8 additions=250+250 real_saved=3276+3276 columns=716 controls=9")

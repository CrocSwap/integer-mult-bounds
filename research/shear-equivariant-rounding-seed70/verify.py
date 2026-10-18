#!/usr/bin/env python3
"""Exact finite evidence for the shear-rounding boundary; Apache-2.0.

Sricharan Vagvala (@theon199), with substantial OpenAI Codex assistance.
The written orbit proof supplies the universal statement, not this replay.
"""
import argparse
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE_HEAD = "407f00df6ca0bf86b455b5640f18ec2f62ee77b9"
SOURCE_BLOB = "b9800377dae28f3dd85c15def0db34fa36a11ff2"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def no_duplicates(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate JSON key: " + key)
        result[key] = value
    return result


def read_json(path):
    return json.loads(path.read_text(), object_pairs_hook=no_duplicates)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def certificate_text(value):
    # Keep each completed orbit and witness on one reviewable line.
    lines = ["{"]
    items = sorted(value.items())
    for index, (key, item) in enumerate(items):
        suffix = "," if index + 1 < len(items) else ""
        if key in ("orbit_rows", "witnesses"):
            lines.append("  " + json.dumps(key) + ": [")
            for j, row in enumerate(item):
                lines.append("    " + json.dumps(row, sort_keys=True)
                             + ("," if j + 1 < len(item) else ""))
            lines.append("  ]" + suffix)
        else:
            lines.append("  " + json.dumps(key) + ": " + json.dumps(item, sort_keys=True) + suffix)
    return "\n".join(lines + ["}"])


def check_reference(directory=HERE):
    sources = read_json(directory / "SOURCES.json")
    rows = sources["retained_external_sources"]
    require(len(rows) == 1, "expected one retained external source")
    row = rows[0]
    require(row["head"] == SOURCE_HEAD and row["git_blob"] == SOURCE_BLOB,
            "external source provenance drift")
    require(row["local_path"] == "references/pr1537-README.md", "external source path drift")
    data = (directory / row["local_path"]).read_bytes()
    blob = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
    require(blob == SOURCE_BLOB, "external source Git blob mismatch")
    require(hashlib.sha256(data).hexdigest() == row["sha256"], "external source SHA256 mismatch")
    require(b"R_i P = Q R_i" in data and b"integer coefficients" in data,
            "missing audited contract or integer-reader scope")
    return row["sha256"]


def shear(v, k=1):
    return (v[0] + k * v[1], v[1])


def repeated_shear(v, k):
    # A separate recurrence, used to check the closed power formula.
    a, b = v
    step = 1 if k >= 0 else -1
    for _ in range(abs(k)):
        a += step * b
    return (a, b)


def sharp_bound(k):
    require(type(k) is int and k >= 0, "invalid orbit horizon")
    q, r = divmod(k, 4)
    return max(F(1, 2), q + (F(0), F(1, 2), F(1), F(1))[r])


def orbit_radius(k, a, b):
    # Direct chronological evaluation; no closed power or endpoint shortcut.
    actual = (F(a), F(b))
    radius = F(0)
    for j in range(k + 1):
        ideal = (F(j, 2), F(1, 2))
        radius = max(radius, abs(actual[0] - ideal[0]), abs(actual[1] - ideal[1]))
        actual = (actual[0] + actual[1], actual[1])
    return radius


def integer_oracle(k):
    # Half-grid units, independently of Fraction and sharp_bound. A concrete
    # seed output bounds the census. Every improving output satisfies the k=0
    # constraints below, so omitted integers cannot beat the incumbent.
    # Endpoint maxima are valid for the affine first-coordinate error.
    candidate = (k + 1) // 4
    incumbent = max(abs(2 * candidate), abs(2 * candidate - k), 1)
    best, seeds, covered = incumbent, [], 0
    for a in range(-incumbent, incumbent + 1):
        if abs(2 * a) > incumbent:
            continue
        for b in range(-incumbent, incumbent + 1):
            if abs(2 * b - 1) > incumbent:
                continue
            covered += 1
            radius = max(abs(2 * a), abs(2 * a + k * (2 * b - 1)), abs(2 * b - 1))
            if radius < best:
                best, seeds = radius, [(a, b)]
            elif radius == best:
                seeds.append((a, b))
    require(bool(seeds), "empty integer oracle")
    return F(best, 2), sorted(seeds), covered


def trunc_scalar(v, delta):
    z = v / delta
    sign = -1 if z < 0 else 1
    return delta * sign * (abs(z.numerator) // z.denominator)


def nearest_scalar(v, delta):
    z = v / delta
    a, remainder = divmod(z.numerator, z.denominator)
    twice = 2 * remainder
    if twice > z.denominator or (twice == z.denominator and a % 2):
        a += 1
    return delta * a


def quantize(v, delta, mode="trunc"):
    require(mode in ("trunc", "nearest-even", "floor"), "unknown rounder")
    if mode == "floor":
        return tuple(delta * (x // delta) for x in v)
    scalar = trunc_scalar if mode == "trunc" else nearest_scalar
    return tuple(scalar(x, delta) for x in v)


def word(carried):
    if carried:
        return [("read", 1), ("w", 1), ("d", 1), ("read", 1),
                ("w", 1), ("w", -2), ("d", -1)]
    return [("read", 1), ("w", 1), ("w", -1)] * 2


def inverse(instructions):
    return [(tag, -amount) for tag, amount in reversed(instructions)]


def run(instructions, d, w, delta, mode="trunc", exact=False):
    d, w = tuple(d), tuple(w)
    for tag, amount in instructions:
        if tag == "read":
            image = tuple(v / 2 for v in w)
            if not exact:
                image = quantize(image, delta, mode)
            d = tuple(u + amount * v for u, v in zip(d, image))
        elif tag == "w":
            w = repeated_shear(w, amount)
        elif tag == "d":
            d = repeated_shear(d, amount)
        else:
            raise ValueError("unknown instruction")
    return d, w


def echo(instructions, d, dirt, source, delta, mode="trunc", exact=False):
    loaded = tuple(a + b for a, b in zip(dirt, source))
    d, restored = run(instructions, d, loaded, delta, mode, exact)
    unloaded = tuple(a - b for a, b in zip(restored, source))
    return run(inverse(instructions), d, unloaded, delta, mode, exact)


def pair_json(v):
    return [str(x) for x in v]


def replay():
    source_digest = check_reference()
    rows, census, direct_checks = [], 0, 0
    for k in range(161):
        bound = sharp_bound(k)
        best, seeds, coverage = integer_oracle(k)
        require(bound == best, "sharp-bound/oracle disagreement")
        census += coverage
        for a, b in seeds:
            require(orbit_radius(k, a, b) == bound, "attaining orbit failed")
            direct_checks += 1
        rows.append({"k": k, "radius_grid_units": str(bound),
                     "minimizing_seed_outputs": [list(v) for v in seeds],
                     "census_outputs": coverage})

    power_cases = defect_cases = 0
    for p in range(13):
        delta = F(1, 2 ** p)
        for k in range(-80, 81):
            v = (F(-3, 2) * delta, F(1, 2) * delta)
            require(shear(v, k) == repeated_shear(v, k), "power direction mismatch")
            power_cases += 1
        require(delta * orbit_radius(70, 17, 0) == delta * sharp_bound(70),
                "seed70 scaled radius mismatch")
        for mode, budget in (("trunc", delta), ("nearest-even", delta / 2)):
            for a in range(-3, 4):
                for b in (-3, -1, 1, 3):
                    v = (a * delta / 2, b * delta / 2)
                    for k in range(21):
                        left = quantize(shear(v, k), delta, mode)
                        right = shear(quantize(v, delta, mode), k)
                        require(abs(left[0] - right[0]) >= max(F(0), k * delta / 2 - 2 * budget),
                                "quantitative equivariance-defect bound failed")
                        defect_cases += 1

    eager, carried = word(False), word(True)
    echo_cases = disagreements = exact_cases = inverse_cases = 0
    witnesses = []
    for p in (0, 1, 7, 12):
        delta = F(1, 2 ** p)
        d = (2 * delta, -delta)
        for u0 in range(-2, 3):
            for u1 in range(-2, 3):
                dirt = (u0 * delta, u1 * delta)
                for x0 in range(-2, 3):
                    for x1 in range(-2, 3):
                        x = (x0 * delta, x1 * delta)
                        ideal = tuple(a + b for a, b in zip(d, x))
                        for instructions in (eager, carried):
                            output, restored = echo(instructions, d, dirt, x, delta, exact=True)
                            require(output == ideal and restored == dirt, "exact child control failed")
                            exact_cases += 1
                        for mode in ("trunc", "nearest-even"):
                            e, eu = echo(eager, d, dirt, x, delta, mode)
                            c, cu = echo(carried, d, dirt, x, delta, mode)
                            require(eu == dirt and cu == dirt, "rounded scratch restoration failed")
                            echo_cases += 1
                            if e != c:
                                disagreements += 1
                            for instructions in (eager, carried):
                                final = run(instructions, d, dirt, delta, mode)
                                require(run(inverse(instructions), *final, delta, mode) == (d, dirt),
                                        "literal rounded inverse failed")
                                inverse_cases += 1
        for mode in ("trunc", "nearest-even"):
            dirt, x = ((delta, delta), (F(0), delta)) if mode == "trunc" else ((F(0), delta), (delta, F(0)))
            e, eu = echo(eager, d, dirt, x, delta, mode)
            c, cu = echo(carried, d, dirt, x, delta, mode)
            require(e != c and eu == cu == dirt, "rounded echo witness vanished")
            witnesses.append({"p": p, "rounder": mode, "d": pair_json(d),
                              "dirt": pair_json(dirt), "source": pair_json(x),
                              "eager_output": pair_json(e), "carried_output": pair_json(c),
                              "difference": pair_json(tuple(a - b for a, b in zip(c, e)))})

    restricted = finite_order = 0
    for a in range(-9, 10):
        for b in range(-3, 4):
            v = (F(a, 2), F(b))
            for k in range(-3, 4):
                require(quantize(shear(v, k), F(1), "floor") == shear(quantize(v, F(1), "floor"), k),
                        "restricted exact transverse grid failed")
                restricted += 1
            v = (F(a, 2), F(b, 2))
            require(quantize(tuple(-x for x in v), F(1)) == tuple(-x for x in quantize(v, F(1))),
                    "finite-order signed rounder failed")
            finite_order += 1

    controls = []
    def control(name, condition):
        require(condition, "control failed: " + name)
        controls.append(name)

    control("fixed_half_grid_budget_fails_at_K2", sharp_bound(2) > F(1, 2))
    control("ignoring_entrance_misses_K70_radius", orbit_radius(70, 35, 0) > sharp_bound(70))
    control("omitting_transverse_error_misses_K0", sharp_bound(0) == F(1, 2))
    v = (F(0), F(1, 2))
    control("ordinary_truncation_power2_defect", quantize(shear(v, 2), F(1)) != shear(quantize(v, F(1)), 2))
    v = (F(1, 2), F(1, 2))
    control("ordinary_truncation_one_step_defect", quantize(shear(v), F(1)) != shear(quantize(v, F(1))))
    v = (F(0), F(1, 2))
    control("dropping_two_endpoint_errors_is_false", quantize(shear(v), F(1), "nearest-even") == shear(quantize(v, F(1), "nearest-even")))
    d, u = (F(2), F(0)), (F(1), F(1))
    control("omitted_workspace_return", run(carried[:-2] + carried[-1:], d, u, F(1))[1] != u)
    control("omitted_output_return", run(carried[:-1], d, u, F(1), exact=True)[0] != tuple(a + b for a, b in zip(d, u)))
    out = run(carried, d, u, F(1))
    control("forward_is_not_inverse", run(carried, *out, F(1)) != (d, u))
    control("rounded_transport_changes_output", disagreements > 0)

    return {"status": "PASS_SHEAR_EQUIVARIANT_ROUNDING", "assignment_seed": 70,
            "source_head": SOURCE_HEAD, "source_readme_sha256": source_digest,
            "theorem": "No globally bounded grid rounder is exactly Q-equivariant on the half-grid.",
            "scope": "Written proof plus exact finite corroboration; no current defect, supplier admission or new kappa.",
            "domain": {"horizons": [0, 160], "power_exponents": [-80, 80],
                       "power_grid_p": [0, 12], "echo_grid_p": [0, 1, 7, 12],
                       "echo_source_and_dirt_coordinates": [-2, 2],
                       "rounders": ["toward-zero", "nearest-even"]},
            "orbit_rows": rows, "census_outputs": census,
            "attaining_orbits": direct_checks, "signed_power_cases": power_cases,
            "quantitative_defect_cases": defect_cases,
            "rounded_echo_cases": echo_cases, "rounded_echo_disagreements": disagreements,
            "exact_echo_cases": exact_cases, "literal_inverse_cases": inverse_cases,
            "restricted_grid_cases": restricted, "finite_order_cases": finite_order,
            "eager_word": [list(x) for x in eager], "carried_word": [list(x) for x in carried],
            "witnesses": witnesses, "controls": controls}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true", help="print certificate without writing files")
    args = parser.parse_args()
    try:
        result = replay()
        if args.emit:
            print(certificate_text(result))
        else:
            require(canonical(result) == canonical(read_json(HERE / "EXPECTED.json")),
                    "certificate mismatch")
            print("PASS_SHEAR_EQUIVARIANT_ROUNDING K70=18_grid_units horizons=161 "
                  f"echo_disagreements={result['rounded_echo_disagreements']} "
                  f"controls={len(result['controls'])} no_new_kappa")
    except (OSError, ValueError, KeyError, TypeError) as exc:
        parser.exit(1, str(exc) + "\n")


if __name__ == "__main__":
    main()

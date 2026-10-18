"""Source-bound rounded-lattice counterexample. Apache-2.0; stdlib only."""
from fractions import Fraction as F
from itertools import product
from math import lcm
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
VENDOR = "research/dirty-prefix-precision/vendor/pr628/"
ZERO = (F(0), F(0))
ONE = (F(1), F(0))
FACTOR = (False, (F(1, 4), F(0)), F(1))
PHASE = (F(3, 5), F(4, 5))
SOURCE = (F(-17), F(4))
REQUIRED = {
    "certificates/selected-result.json", "docs/research/agent-task-catalog.json",
    "docs/research/community-batch1099-review.md",
    "research/dirty-prefix-precision/PROOF.md",
    "research/mixed-precision-inverse-boundary/README.md",
    *(VENDOR + name for name in (
        "NOTICE.md", "dirty.py", "weighted.py", "check.py", "scan.py", "interval_kernel.py"
    )),
}


def need(condition, message):
    if not condition:
        raise ValueError(message)


def rejected(call, message):
    try:
        call()
    except ValueError:
        return
    raise ValueError("control accepted: " + message)


def validate_bytes(data, pin):
    need(hashlib.sha256(data).hexdigest() == pin["sha256"], "source SHA256: " + pin["path"])
    blob = b"blob " + str(len(data)).encode() + b"\0" + data
    need(hashlib.sha1(blob).hexdigest() == pin["git_blob"], "source Git blob: " + pin["path"])


def load_source():
    pins = json.loads((HERE / "SOURCES.json").read_text())["files"]
    need({p["path"] for p in pins} == REQUIRED and len(pins) == len(REQUIRED), "source inventory")
    for pin in pins:
        if pin["usage"] == "provenance":
            data = subprocess.check_output(["git", "cat-file", "blob", pin["git_blob"]], cwd=ROOT)
        else:
            need(pin["usage"] == "input", "source usage")
            data = (ROOT / pin["path"]).read_bytes()
        validate_bytes(data, pin)
        rejected(lambda: validate_bytes(data + b"\ncorrupt", pin), "source corruption")
    spec = importlib.util.spec_from_file_location("closure_pr628", ROOT / VENDOR / "dirty.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def rnd(value, bits):
    """Independent integer quotient/remainder nearest rule; ties toward +infinity."""
    scaled = value * (1 << bits)
    quotient, remainder = divmod(scaled.numerator, scaled.denominator)
    return F(quotient + (2 * remainder >= scaled.denominator), 1 << bits)


def add(a, b):
    return (a[0] + b[0], a[1] + b[1])


def scale(a, b):
    return (a[0] * b, a[1] * b)


def mul(a, b):
    return (a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0])


def divide(a, b):
    return scale(mul(a, (b[0], -b[1])), 1 / (b[0] ** 2 + b[1] ** 2))


def rounded(z, bits):
    return tuple(rnd(v, bits) for v in z)


def scalar_trace(source, phase, bits):
    """Derived length-one formula, with no predecessor arithmetic imported."""
    power = rounded(scale(phase, F(1, 4)), bits)
    denominator = add(ONE, scale(power, -1))
    seed = rounded(divide(source, denominator), bits)
    correction = rounded(mul(power, seed), bits)
    value = add(source, correction)
    increment = rounded(scale(value, F(-1, 4)), bits)
    return dict(power=power, denominator=denominator, seed=seed,
                correction=correction, value=value, increment=increment)


def actual(module, source, phase, bits, target=ZERO, direction=1, sign=1):
    x, y = [source], [target]
    phases = [phase]
    module.compose(x, y, [FACTOR], [], phases, F(1, 2), bits, direction, sign)
    need(x == [source] and phases == [phase], "source or phase changed")
    return y[0]


def paired(target, value, coarse, fine):
    return target + rnd(value, coarse) - rnd(value, fine)


def witness(module):
    trace = scalar_trace(SOURCE, PHASE, 4)
    expected = {
        "power": (F(1, 8), F(3, 16)),
        "denominator": (F(7, 8), F(-3, 16)),
        "seed": (F(-39, 2), F(3, 8)),
        "correction": (F(-5, 2), F(-29, 8)),
        "value": (F(-39, 2), F(3, 8)),
        "increment": (F(39, 8), F(-1, 16)),
    }
    need(trace == expected, "independent exact trace")
    observed = actual(module, SOURCE, PHASE, 4)
    need(observed == expected["increment"], "actual leaf witness")
    ideal = divide(SOURCE, add(PHASE, (F(-4), F(0))))
    need(ideal == (F(5), F(0)), "ideal preimage identity")
    need(module.exact_operator([SOURCE], [FACTOR], [PHASE], 1) == [ideal], "source dense oracle")
    need(paired(F(0), observed[0], 0, 4) == F(1, 8), "downstream residual")
    need(actual(module, SOURCE, PHASE, 4, observed, sign=-1) == ZERO, "literal inverse")
    for target in (F(-7, 3), F(0), F(11, 16)):
        need(paired(target, ideal[0], 0, 4) == target, "ideal positive control")
        need(paired(target, observed[0], 0, 4) == target + F(1, 8), "arbitrary dirty residual")
        for bits in (0, 4):
            need(paired(target, observed[0], bits, bits) == target, "same-grid control")
    # Better precision can restore equality without restoring the exact lattice.
    high = actual(module, SOURCE, PHASE, 8)
    need(high == (F(639, 128), F(-1, 128)), "higher-precision witness")
    need(high[0].denominator != 1 and paired(F(0), high[0], 0, 4) == 0, "closure not necessary")
    need(rounded(ideal, 4) != observed, "single ideal rounding is not actual leaf")
    need(rnd(F(-3, 32), 4) == F(-1, 16), "negative half-up tie")
    rejected(lambda: actual(module, SOURCE, PHASE, 2), "underprecision")
    rejected(lambda: actual(module, (F(1, 3), F(0)), PHASE, 4), "off-grid input")
    rejected(lambda: actual(module, SOURCE, (F(2), F(0)), 4), "nonunit phase")
    def aliased():
        data = [SOURCE]
        module.compose(data, data, [FACTOR], [], [PHASE], F(1, 2), 4, 1)
    rejected(aliased, "aliased target")
    return {"source": [str(v) for v in SOURCE], "phase": [str(v) for v in PHASE],
            "bits": 4, "ideal": [str(v) for v in ideal],
            "actual": [str(v) for v in observed], "downstream_residual": "1/8",
            "trace": {k: [str(v) for v in z] for k, z in trace.items()}}


def cell_controls():
    cases = 0
    for w, gap, integer in product(range(4), range(1, 5), range(-4, 5)):
        v = w + gap
        center = F(integer, 1 << w)
        radius = F(1, 1 << (v + 1))
        for numerator in range(-12, 13):
            error = numerator * radius / 8
            same_center = rnd(center + error, w) == rnd(center + error, v) == center
            need(same_center == (-radius <= error < radius), "sharp half-open cell")
            cases += 1
        need(paired(F(0), center - radius, w, v) == 0, "negative endpoint admitted")
        need(paired(F(0), center + radius, w, v) != 0, "positive endpoint rejected")
    return cases


def census(module):
    phases = (ONE, (F(-1), F(0)), (F(0), F(1)), (F(0), F(-1)), PHASE,
              (F(3, 5), F(-4, 5)), (F(-5, 13), F(12, 13)), (F(8, 17), F(15, 17)))
    precisions = (*range(3, 13), 16, 32)
    dirt = (ZERO, (F(7, 8), F(-3, 8)), (F(-13, 8), F(11, 8)))
    cases = escaped = dyadic_exact = 0
    for phase, bits, k, direction, target, sign in product(
            phases, precisions, range(-3, 4), (-1, 1), dirt, (-1, 1)):
        denominator = lcm(*(v.denominator for v in phase))
        source = scale(add(phase, (F(-4), F(0))), denominator * k)
        ideal = (F(denominator * k), F(0))
        need(divide(source, add(phase, (F(-4), F(0)))) == ideal, "ideal lattice closure")
        trace = scalar_trace(source, phase, bits)
        observed = actual(module, source, phase, bits, target, direction, sign)
        need(observed == add(target, scale(trace["increment"], sign)), "independent leaf formula")
        restored = actual(module, source, phase, bits, observed, direction, -sign)
        need(restored == target, "actual same-grid inverse")
        if denominator == 1:
            need(trace["increment"] == ideal, "Gaussian-unit exact positive control")
            dyadic_exact += 1
        increment = trace["increment"]
        escaped += increment[1] != 0 or (increment[0] / denominator).denominator != 1
        cases += 1
    need(cases == 8064 and dyadic_exact == 4032 and escaped > 0, "census coverage")
    return {"actual_leaf_cases": cases, "literal_inverses": cases,
            "gaussian_unit_exact_cases": dyadic_exact, "lattice_escape_cases": escaped}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--witness-only", action="store_true")
    args = parser.parse_args()
    module = load_source()
    result = {"witness": witness(module)}
    if not args.witness_only:
        result.update(census(module))
        result["sharp_cell_cases"] = cell_controls()
    print(json.dumps(result, indent=2, sort_keys=True))
    print("PASS_ROUNDED_LEAF_LATTICE_CLOSURE" + ("_WITNESS" if args.witness_only else ""))


if __name__ == "__main__":
    main()

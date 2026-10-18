"""Exact source-bound diagnostic evidence for the README's universal proof."""
from __future__ import annotations

import argparse
from fractions import Fraction as F
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile

P = Path(__file__).resolve().parent
ROOT = P.parents[1]
VENDOR = "research/dirty-prefix-precision/vendor/pr628/"
ZERO, ONE = (F(0), F(0)), (F(1), F(0))


def need(ok, why):
    if not ok:
        raise ValueError(why)


def add(a, b): return (a[0] + b[0], a[1] + b[1])
def neg(a): return (-a[0], -a[1])
def sub(a, b): return add(a, neg(b))
def mul(a, b): return (a[0]*b[0]-a[1]*b[1], a[0]*b[1]+a[1]*b[0])
def norm2(a): return a[0]*a[0]+a[1]*a[1]
def scale(a, q): return (a[0]*q, a[1]*q)
def conj(a): return (a[0], -a[1])
def div(a, b): return scale(mul(a, conj(b)), 1/norm2(b))


def rounded(a, bits):
    def scalar(x):
        q = x*(1 << bits) + F(1, 2)
        return F(q.numerator // q.denominator, 1 << bits)
    return tuple(scalar(x) for x in a)


def within(actual, expected, bound, label):
    need(all(norm2(sub(a, b)) <= bound*bound
             for a, b in zip(actual, expected)), label)


def shadow(x, factor, phases, bits, d):
    """No data rounding; retain the independently computed rounded powers."""
    inside, b, gain = factor
    count = len(x)
    order = list(range(count))
    if (-d if inside else d) == -1:
        order.reverse()
    prefixes, powers = {}, {}
    h, power = ZERO, ONE
    for i in order:
        coefficient = mul(b, conj(phases[(i+d) % count]) if inside else phases[i])
        h = add(x[i], mul(coefficient, h))
        power = rounded(mul(coefficient, power), bits)
        prefixes[i], powers[i] = h, power
    seed = div(h, sub(ONE, power))
    out = [ZERO] * count
    for i in order:
        multiplier = scale(conj(phases[i]) if inside else neg(b), gain)
        target = (i-d) % count if inside else i
        out[target] = mul(multiplier, add(prefixes[i], mul(powers[i], seed)))
    return out


def authenticate():
    manifest = json.loads((P / "SOURCES.json").read_text(encoding="utf-8"))
    files = {}
    for row in manifest["files"]:
        if row["usage"] != "input":
            continue
        data = (ROOT / row["path"]).read_bytes()
        need(hashlib.sha256(data).hexdigest() == row["sha256"],
             "source SHA-256: " + row["path"])
        blob = b"blob " + str(len(data)).encode() + b"\0" + data
        need(hashlib.sha1(blob).hexdigest() == row["git_blob"],
             "source Git blob: " + row["path"])
        files[row["path"]] = data
    return files


def digest(rows):
    return hashlib.sha256(json.dumps(rows, default=str, separators=(",", ":")).encode()).hexdigest()


def ideal_operator(dirty, x, factors, phases, direction):
    need(all(inside or norm2(b) != 0 for inside, b, _ in factors),
         "outside exact inverse oracle requires b != 0")
    return dirty.exact_operator(x, factors, phases, direction)


def run(dirty):
    beta, R = F(1, 2), F(2)
    L = 4*R/beta**2
    units = [ONE, (F(3, 5), F(4, 5)), (F(0), F(1))]
    factors = [(True, (F(1, 3), F(0)), F(2)),
               (False, (F(1, 5), F(1, 7)), F(1)),
               (False, (F(1, 3), F(0)), F(-1))]
    leaf_rows = []
    for bits in (4, 7, 12):
        u = F(1, 1 << bits)
        E0, delta = 8*R*u/beta**2, 4*R*u/beta**4
        for length in (1, 2, 3, 8):
            phases = [units[i % len(units)] for i in range(length)]
            for direction in (-1, 1):
                for factor_index, factor in enumerate(factors):
                    for magnitude in (0, 1 << 20, -(1 << 80)):
                        x = [(F(magnitude+i, 1 << bits), F(2*i-1, 1 << bits))
                             for i in range(length)]
                        initial = x[:]
                        y = [(F(17-i), F(i-3)) for i in range(length)]
                        y0 = y[:]
                        dirty.leaf(x, y, factor, phases, beta, bits, direction, 1, None)
                        need(x == initial, "leaf source restored")
                        net = [sub(a, b) for a, b in zip(y, y0)]
                        linear = shadow(initial, factor, phases, bits, direction)
                        within(net, linear, E0, "uniform actual leaf defect")
                        ideal = ideal_operator(dirty, initial, [factor], phases, direction)
                        B = max(abs(a)+abs(b) for a, b in initial)
                        within(linear, ideal, delta*B, "shadow/ideal perturbation")
                        within(linear, [ZERO]*length, L*B, "shadow norm")
                        dirty.leaf(x, y, factor, phases, beta, bits, direction, -1, None)
                        need(x == initial and y == y0, "leaf inverse")
                        leaf_rows.append([bits, length, direction, factor_index,
                                          str(magnitude), digest(net)])
    compose_rows = []
    for bits in (4, 12):
        u = F(1, 1 << bits)
        E0, delta = 8*R*u/beta**2, 4*R*u/beta**4
        for count in (1, 2, 3, 5, 8):
            fs = [factors[i % len(factors)] for i in range(count)]
            for length in (1, 2, 3):
                phases = [units[i % len(units)] for i in range(length)]
                for direction in (-1, 1):
                    initial = [(F(i-1, 4), F(2-i, 8)) for i in range(length)]
                    B = max(abs(a)+abs(b) for a, b in initial)
                    linear = initial[:]
                    for factor in fs:
                        linear = shadow(linear, factor, phases, bits, direction)
                    ideal = ideal_operator(dirty, initial, fs, phases, direction)
                    for dirt in (0, 1 << 64, -(1 << 128)):
                        x = initial[:]
                        y = [(F(dirt+i, 1 << bits), F(dirt-i, 1 << bits))
                             for i in range(length)]
                        y0 = y[:]
                        scratch = [[(F(dirt+2*i+j, 1 << bits), F(dirt-3*i-j, 1 << bits))
                                    for i in range(length)]
                                   for j in range((count-1).bit_length())]
                        saved = [v[:] for v in scratch]
                        stats = dict(leaves=0, scalar_steps=0)
                        dirty.compose(x, y, fs, scratch, phases, beta, bits, direction, stats=stats)
                        need(x == initial and scratch == saved, "whole-word restoration")
                        net = [sub(a, b) for a, b in zip(y, y0)]
                        amplification = count*L**(count-1)
                        within(net, linear, amplification*E0, "tree shadow defect")
                        within(net, ideal, amplification*(E0+delta*B), "tree ideal endpoint")
                        dirty.compose(x, y, fs, scratch, phases, beta, bits, direction, -1)
                        need(x == initial and y == y0 and scratch == saved, "whole-word inverse")
                        compose_rows.append([bits, count, length, direction, str(dirt),
                                             stats["leaves"], digest(net)])

    controls = []
    # The ideal leaf has a coefficient error: its error cannot be globally additive.
    x = [(F(1 << 40), F(0))]
    y = [ZERO]
    factor = (False, (F(1, 3), F(0)), F(1))
    dirty.leaf(x, y, factor, [ONE], beta, 4, 1, 1, None)
    frozen = shadow(x, factor, [ONE], 4, 1)
    ideal = ideal_operator(dirty, x, [factor], [ONE], 1)
    within(y, frozen, F(2), "large input frozen-power shadow")
    need(frozen[0][0] == -F(16, 33)*x[0][0], "actual rounded-power coefficient")
    need(ideal[0][0] == -F(1, 2)*x[0][0], "ideal coefficient")
    need(norm2(sub(y[0], ideal[0])) > 1000**2, "ideal uniform-defect control")
    controls.append(dict(name="ideal_is_not_uniform_shadow", actual=str(y[0][0]),
                         shadow=str(frozen[0][0]), ideal=str(ideal[0][0])))
    # A(t)=round(t/3), B(x)=x, x=z=1: two A errors have opposite signs.
    difference = sub(rounded((F(2, 3), F(0)), 0), rounded((F(1, 3), F(0)), 0))
    need(difference[0]-F(1, 3) == F(2, 3) > F(1, 2), "factor two required")
    controls.append(dict(name="two_reader_defects_required", error="2/3", leaf_error="1/2"))
    need((101**2-100**2)-1 == 200, "quadratic dirty amplification")
    controls.append(dict(name="unbounded_defect_can_amplify_dirt", error=200))
    # Find an actual source witness; do not substitute an illustrative rounded map.
    outputs = []
    for source_numerator in range(1, 33):
        outputs = []
        for numerator in range(17):
            xx, yy, zz = [(F(source_numerator, 16), F(0))], [ZERO], [[(F(numerator, 16), F(0))]]
            dirty.compose(xx, yy, [factor, factor], zz, [ONE], beta, 4, 1)
            outputs.append(yy[0][0])
        if len(set(outputs)) > 1:
            break
    need(len(set(outputs)) > 1, "actual nonlinear increment varies with dirt")
    controls.append(dict(name="actual_increment_varies_with_dirt",
                         source=str(F(source_numerator, 16)), helper_numerators=list(range(17)),
                         outputs=[str(v) for v in outputs]))
    try:
        within([(F(100), F(0))], [ZERO], F(1), "corrupt endpoint")
    except ValueError:
        controls.append(dict(name="corrupt_endpoint_rejected"))
    else:
        raise ValueError("corrupt endpoint accepted")
    try:
        ideal_operator(dirty, [ONE], [(False, ZERO, F(1))], [ONE], 1)
    except ValueError as error:
        controls.append(dict(name="outside_zero_exact_oracle_rejected", reason=str(error)))
    else:
        raise ValueError("outside zero coefficient admitted to exact inverse oracle")
    return dict(schema_version=1, status="PASS_DIRTY_ENDPOINT_DEFECT",
                source_head="0768f97d06c623b8211e651543c66135796b62bf",
                beta=str(beta), multiplier_bound=str(R), shadow_bound=str(L),
                leaf_cases=leaf_rows, composition_cases=compose_rows, controls=controls,
                scope="Finite exact source binding; universal bound is proved in README.md.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    files = authenticate()
    # Execute precisely authenticated bytes, not any pre-existing Python bytecode.
    with tempfile.TemporaryDirectory(prefix="dirty-endpoint-") as temporary:
        directory = Path(temporary)
        for path, data in files.items():
            if path.startswith(VENDOR) and path.endswith(".py"):
                (directory / Path(path).name).write_bytes(data)
        spec = importlib.util.spec_from_file_location("endpoint_source", directory / "dirty.py")
        dirty = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(dirty)
        result = run(dirty)
    encoded = json.dumps(result, indent=2) + "\n"
    if args.out:
        with args.out.open("x", encoding="utf-8", newline="\n") as handle:
            handle.write(encoded)
    else:
        need((P / "receipt.json").read_text(encoding="utf-8") == encoded,
             "saved canonical receipt differs")
    print(result["status"], len(result["leaf_cases"]), "leaves,",
          len(result["composition_cases"]), "compositions,", len(result["controls"]), "controls")


if __name__ == "__main__":
    main()

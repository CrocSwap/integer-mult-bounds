#!/usr/bin/env python3
"""Exact, bounded audit of rounded Neumann evaluation. Apache-2.0.

Hanson Sun, with substantial OpenAI Codex assistance. The oracles below
are contract fixtures, not implementations of the Gaussian resampler.
No repository mathematical implementation is imported.
"""
import argparse
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
QMAX = Q(21, 50)


def require(ok, message):
    if not ok:
        raise ValueError(message)


def trunc(n, d):
    require(d > 0, "nonpositive denominator")
    return (1 if n >= 0 else -1) * (abs(n) // d)


def sgn(n):
    return (n > 0) - (n < 0)


def add(x, y):
    require(len(x) == len(y), "vector length mismatch")
    return tuple(a + b for a, b in zip(x, y))


def sub(x, y):
    require(len(x) == len(y), "vector length mismatch")
    return tuple(a - b for a, b in zip(x, y))


def disk(x, scale):
    require(len(x) > 0 and len(x) % 2 == 0, "nonempty complex vector required")
    return all(x[i] ** 2 + x[i + 1] ** 2 <= scale ** 2
               for i in range(0, len(x), 2))


def below(x, bound, strict=False):
    require(len(x) > 0 and len(x) % 2 == 0 and bound >= 0, "invalid norm comparison")
    squares = (x[i] ** 2 + x[i + 1] ** 2 for i in range(0, len(x), 2))
    return all(s < bound ** 2 if strict else s <= bound ** 2 for s in squares)


def real_matrix(matrix, denominator=64):
    """Gaussian-rational matrix as a real block matrix; independent of emitter."""
    n = len(matrix)
    out = [[Q(0) for _ in range(2 * n)] for _ in range(2 * n)]
    for i, row in enumerate(matrix):
        for j, (a, b) in enumerate(row):
            out[2*i][2*j], out[2*i][2*j+1] = Q(a, denominator), Q(-b, denominator)
            out[2*i+1][2*j], out[2*i+1][2*j+1] = Q(b, denominator), Q(a, denominator)
    return out


def mv(matrix, x):
    return tuple(sum(a*b for a, b in zip(row, x)) for row in matrix)


def inverse_target(matrix, u):
    """Dense rational elimination for (I+E)y=u/2, not a Neumann computation."""
    n = len(u)
    rows = [[Q(i == j) + matrix[i][j] for j in range(n)] + [Q(u[i], 2)]
            for i in range(n)]
    for c in range(n):
        pivot = next((i for i in range(c, n) if rows[i][c]), None)
        require(pivot is not None, "singular inverse fixture")
        rows[c], rows[pivot] = rows[pivot], rows[c]
        z = rows[c][c]
        rows[c] = [v/z for v in rows[c]]
        for i in range(n):
            if i != c:
                z = rows[i][c]
                rows[i] = [v-z*w for v, w in zip(rows[i], rows[c])]
    return tuple(row[-1] for row in rows)


class GridOracle:
    """Exact Gaussian-integer multiply, then truncation/outward real bias.

    Values are integer numerators on the 2^-p grid. With bias b>=1,
    the local squared error is < b^2+1 grid units. With b=0 it is <2.
    This includes zero-preserving, odd, nonlinear approximation fixtures.
    """
    def __init__(self, matrix, bias=0, denominator=64):
        self.matrix, self.bias, self.denominator = matrix, bias, denominator
        self.calls = 0

    def __call__(self, x):
        self.calls += 1
        out = []
        for row in self.matrix:
            re = sum(a*x[2*j] - b*x[2*j+1] for j, (a, b) in enumerate(row))
            im = sum(a*x[2*j+1] + b*x[2*j] for j, (a, b) in enumerate(row))
            out.extend((trunc(re, self.denominator) + self.bias*sgn(re),
                        trunc(im, self.denominator)))
        return tuple(out)


def fraction_oracle(matrix, x, bias):
    """Separate Fraction/block-matrix implementation of the fixture oracle."""
    values = mv(matrix, x)
    rounded = [int(v) for v in values]
    for i in range(0, len(values), 2):
        rounded[i] += bias * sgn(values[i])
    return tuple(rounded)


def horner(u, k, oracle, p, check_disk=True):
    require(type(k) is int and k >= 1, "positive integer term count required")
    require(type(p) is int and p > 100, "source precision domain")
    scale = 1 << p
    require(all(type(x) is int for x in u) and disk(u, scale), "input outside disk grid")
    v = tuple(trunc(x, 2) for x in u)
    y = v
    trace = [y]
    for _ in range(k - 1):
        z = oracle(y)
        require(len(z) == len(u) and all(type(x) is int for x in z), "invalid oracle grid vector")
        require(not check_disk or disk(z, scale), "oracle outside disk grid")
        y = sub(v, z)
        require(not check_disk or disk(y, scale), "Horner iterate outside disk grid")
        trace.append(y)
    return y, trace


def power_sum(u, k, oracle):
    v = tuple(trunc(x, 2) for x in u)
    total, trace = v, [v]
    for j in range(1, k):
        v = oracle(v)
        total = add(total, tuple((-1)**j*x for x in v))
        trace.append(v)
    return total, trace


def fraction_horner(u, k, matrix, bias):
    v = tuple(int(Q(x, 2)) for x in u)
    state, trace = v, [v]
    for _ in range(k-1):
        image = fraction_oracle(matrix, state, bias)
        state = tuple(a-b for a, b in zip(v, image))
        trace.append(state)
    return state, trace


def source_pins():
    sources = json.loads((HERE / "SOURCES.json").read_text())
    pins = {}
    for row in sources["files"]:
        if row["usage"] != "input":
            continue
        name = row["path"]
        path = ROOT / name
        require(path.is_file() and not path.is_symlink(), "missing source: " + name)
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        require(digest == row["sha256"], "source drift: " + name)
        pins[name] = digest
    require(len(pins) == 3, "incomplete live source inventory")
    return pins


def fixtures():
    z = (0, 0)
    return [
        [[z]], [[(16, 0)]], [[(-16, 0)]], [[(0, 16)]],
        [[z, (16, 0)], [(16, 0), z]],
        [[(8, 0), (8, 0)], [z, (-16, 0)]],
        [[(0, 8), (8, 0)], [(-8, 0), (0, 8)]],
        [[z, (16, 0), z], [z, z, (16, 0)], [(16, 0), z, z]],
        [[(8, 0), (0, 8), (-8, 0)], [z, (0, 16), z], [(8, 8), z, (8, 0)]],
    ]


def exact_fixture_audit():
    count = states = halves = calls = 0
    digest = hashlib.sha256()
    for p in (101, 128, 257):
        scale, a = 1 << p, (p-1)//9
        for matrix in fixtures():
            q = max(sum(abs(a)+abs(b) for a, b in row) for row in matrix) / Q(64)
            require(q <= QMAX, "fixture contraction bound")
            dense = real_matrix(matrix)
            n = len(matrix)
            inputs = [tuple(v for j in range(n) for v in pair(j)) for pair in (
                lambda j: (scale * (-1)**j, 0),
                lambda j: (0, scale * (-1)**j),
                lambda j: ((3*scale)//5 * (-1)**j, (4*scale)//5),
                lambda j: (2*j+1, -2*j-3),
            )]
            for u in inputs:
                target = inverse_target(dense, u)
                for k in (1, 2, p):
                    for bias in (0, 3*a):
                        oracle = GridOracle(matrix, bias)
                        y, trace = horner(u, k, oracle, p)
                        other, other_trace = fraction_horner(u, k, dense, bias)
                        require((y, trace) == (other, other_trace), "independent grid trace mismatch")
                        require(oracle.calls == k-1, "unpaid or omitted E call")
                        exact = tuple(Q(x, 2) for x in u)
                        err_bound = Q(1)
                        for j, state in enumerate(trace):
                            require(below(sub(state, exact), err_bound), "finite-polynomial error bound")
                            if j+1 < len(trace):
                                image = fraction_oracle(dense, state, bias)
                                require(below(sub(image, mv(dense, state)), Q(p, 3), True),
                                        "oracle contract fails at computed input")
                                exact = sub(tuple(Q(x, 2) for x in u), mv(dense, exact))
                                err_bound = 1 + q*err_bound + Q(p, 3)
                        # Grid units: the inverse-tail allowance includes 2^p.
                        bound = err_bound + q**k * scale / (2*(1-q))
                        require(below(sub(y, target), bound), "dense inverse error bound")
                        if k == p:
                            require(q**k * scale <= 1, "power residual premise")
                            require(below(sub(y, target), Q(p), True), "linear p error conclusion")
                        require(disk(y, scale), "output disk invariant")
                        digest.update(json.dumps([p, matrix, u, k, bias, y, trace], separators=(',', ':')).encode())
                        count += 1
                        states += len(trace)
                        calls += oracle.calls
                        halves += len(u)
    return dict(cases=count, complete_state_comparisons=states,
                oracle_calls=calls, component_halvings=halves, trace_sha256=digest.hexdigest())


def quadratic_family():
    count, max_calls = 0, 0
    digest = hashlib.sha256()
    representative = None
    for p in [*range(101, 261), 511, 512, 1024]:
        a, scale = (p-1)//9, 1 << p
        require(9*a*a+1 < Q(p*p, 9), "strict uniform oracle budget")
        require(8*a <= scale, "family input disk")
        matrix = [[(0, 0), (16, 0)], [(16, 0), (0, 0)]]
        u = (8*a, 0, -8*a, 0)
        for k in sorted({(p+1)//2, p}):
            require(Q(1, 4)**k <= Q(1, scale), "family residual premise")
            old_oracle, new_oracle = GridOracle(matrix, 3*a), GridOracle(matrix, 3*a)
            old, old_trace = power_sum(u, k, old_oracle)
            new, _ = horner(u, k, new_oracle, p)
            require(disk(old, scale), "power-sum family output outside disk")
            exact = (Q(16*a, 3), Q(0), Q(-16*a, 3), Q(0))
            require(old == (4*a*k, 0, -4*a*k, 0), "closed oscillating witness")
            require(all(v == tuple((-1)**j*x for x in (4*a, 0, -4*a, 0))
                        for j, v in enumerate(old_trace)), "family full trace")
            err = Q(4*a)*(k-Q(4, 3))
            require(err >= Q(2*p*p, 15) and err < Q(3*p*p, 4), "quadratic error scale")
            require(err > p, "false linear claim not falsified")
            require(below(sub(new, exact), Q(p), True), "Horner family conclusion")
            require(old_oracle.calls == new_oracle.calls == k-1, "unequal E budgets")
            if p == 128 and k == 64:
                representative = dict(p=p, k=k, a=a, source_numerators=list(u),
                    exact_inverse_numerators=[str(x) for x in exact],
                    power_sum_numerators=list(old), horner_numerators=list(new),
                    power_sum_error_in_grid_units=str(err),
                    horner_error_in_grid_units=str(abs(new[0]-exact[0])),
                    old_bound_in_grid_units=str(Q(3*p*p, 4)),
                    new_bound_in_grid_units=str((Q(p, 3)+Q(3, 2))/(1-QMAX)))
            digest.update(json.dumps([p, k, old, new], separators=(',', ':')).encode())
            count += 1
            max_calls = max(max_calls, k-1)
    return dict(cases=count, maximum_calls_per_evaluation=max_calls,
                trace_sha256=digest.hexdigest(), representative=representative)


def controls():
    p, k, scale = 101, 101, 1 << 101
    exact = GridOracle([[(16, 0)]])
    u = (scale, 0)
    # Wrong sign converges to (I-E)^-1/2 instead of (I+E)^-1/2.
    v = tuple(x//2 for x in u)
    wrong = v
    for _ in range(k-1):
        wrong = add(v, exact(wrong))
    target = (Q(2*scale, 5), Q(0))
    require(not below(sub(wrong, target), Q(p)), "wrong-sign control survived")
    require(not below(sub(u, v), Q(p)), "missing-half control survived")
    require(not below(sub(v, target), Q(p)), "missing-tail control survived")
    wrong = v
    for _ in range(k-1):
        wrong = sub(wrong, exact(wrong))
    require(not below(sub(wrong, target), Q(p)), "overwritten-source control survived")

    # q<1/2 without a fixed margin does not suffice for disk-grid induction.
    q = Q(1, 2) - Q(1, scale)
    state, first_exit = scale//2, None
    for j in range(1, k):
        oracle_value = -trunc((scale//2-1)*state, scale) - 3*sgn(state)
        require(abs(oracle_value) <= scale, "margin-control oracle output invalid")
        require(abs(Q(oracle_value)+q*state) < Q(p, 3), "margin-control oracle budget")
        state = scale//2 - oracle_value
        if state > scale:
            first_exit = j
            break
    require(first_exit is not None and q**k <= Q(1, scale), "weak-margin witness failed")
    require(QMAX + Q(p, 3*scale) < Q(1, 2), "published margin not sufficient")
    return dict(rejected_false_claims=["plus_sign", "omitted_half", "omitted_residual_premise",
                "overwritten_constant_source", "q_less_than_half_without_disk_slack",
                "linear_error_for_original_power_sum"],
                weak_margin_witness=dict(p=p, k=k, first_exit=first_exit,
                    iterate_numerator=state, disk_radius_numerator=scale, q=str(q)))


def result():
    return dict(schema_version=1, status="PASS_NEUMANN_ROUNDING_AUDIT",
                source_sha256=source_pins(), seed=68,
                scope="Exact contract audit and conditional alternative evaluation; no Gaussian implementation or new kappa",
                fixture_audit=exact_fixture_audit(), quadratic_family=quadratic_family(), controls=controls())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", type=Path, help="write a new receipt, refusing overwrite")
    args = parser.parse_args()
    if args.write:
        require(not args.write.exists(), "refusing to overwrite receipt")
    actual = result()
    encoded = json.dumps(actual, indent=2, sort_keys=True) + '\n'
    if args.write:
        with args.write.open('x') as handle:
            handle.write(encoded)
    else:
        expected = (HERE / "RESULT.json").read_text()
        require(encoded == expected, "receipt mismatch")
    print(actual['status'], 'fixtures='+str(actual['fixture_audit']['cases']),
          'family='+str(actual['quadratic_family']['cases']),
          'controls='+str(len(actual['controls']['rejected_false_claims'])))


if __name__ == '__main__':
    main()

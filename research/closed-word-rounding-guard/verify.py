"""Exact bounded corroboration for the endpoint-conditioned error theorem."""

from __future__ import annotations

import argparse
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path


Matrix = tuple[tuple[F, F], tuple[F, F]]
I: Matrix = ((F(1), F(0)), (F(0), F(1)))
ZERO: Matrix = ((F(0), F(0)), (F(0), F(0)))


def need(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def mul(a: Matrix, b: Matrix) -> Matrix:
    return tuple(tuple(sum(a[i][k] * b[k][j] for k in range(2))
                       for j in range(2)) for i in range(2))


def add(a: Matrix, b: Matrix) -> Matrix:
    return tuple(tuple(a[i][j] + b[i][j] for j in range(2))
                 for i in range(2))


def sub(a: Matrix, b: Matrix) -> Matrix:
    return tuple(tuple(a[i][j] - b[i][j] for j in range(2))
                 for i in range(2))


def inv(a: Matrix) -> Matrix:
    det = a[0][0] * a[1][1] - a[0][1] * a[1][0]
    need(det != 0, "singular matrix")
    return ((a[1][1] / det, -a[0][1] / det),
            (-a[1][0] / det, a[0][0] / det))


def norm(a: Matrix) -> F:
    return max(sum(abs(x) for x in row) for row in a)


def shear(t: F) -> Matrix:
    return ((F(1), F(0)), (t, F(1)))


def scale(t: F) -> Matrix:
    need(t > 0, "scale must be positive")
    return ((t, F(0)), (F(0), 1 / t))


def trajectory(gates: list[Matrix], errors: list[Matrix], noise: list[Matrix]):
    """Propagate both input columns and their additive forcing together."""
    need(1 <= len(gates) <= 256, "gate count outside bounded replay")
    need(len(gates) == len(errors) == len(noise), "unaligned trajectory")
    exact, rounded, forced, interaction, forcing = I, I, I, I, ZERO
    radius, envelope = F(0), F(1)
    for a, error, u in zip(gates, errors, noise, strict=True):
        previous = exact
        exact = mul(a, previous)
        rounded = mul(add(a, error), rounded)
        forced = add(mul(add(a, error), forced), u)
        d = mul(mul(inv(exact), error), previous)
        interaction = mul(add(I, d), interaction)
        forcing = add(mul(add(I, d), forcing), mul(inv(exact), u))
        radius += norm(d)
        envelope = max(envelope, norm(exact), norm(inv(exact)))
        need(rounded == mul(exact, interaction), "interaction order/index")
        need(forced == mul(exact, add(interaction, forcing)), "forcing order")
    return exact, rounded, forced, radius, envelope


def check_bound(gates, errors, noise) -> tuple[F, F, F]:
    exact, rounded, forced, rho, b = trajectory(gates, errors, noise)
    need(rho < 1, "small interaction budget required")
    c = norm(exact)
    budget = c * (rho + b * sum(norm(u) for u in noise)) / (1 - rho)
    need(norm(sub(forced, exact)) <= budget, "endpoint trajectory bound")
    need(norm(sub(rounded, exact)) <= c * rho / (1 - rho),
         "endpoint coefficient bound")
    return rho, b, c


def excursion(q: int, pairs: int, closed: bool, eta: F):
    need(1 <= q <= 16 and 1 <= pairs <= 32, "excursion outside replay caps")
    need(type(closed) is bool and 0 < eta <= F(1, 4), "bad excursion data")
    up, down = scale(F(2)), scale(F(1, 2))
    gates = [up] * q + [shear(F(1, 2)), shear(F(-1, 2))] * pairs
    gates += [down] * (q if closed else 2 * q)
    error = sub(shear(eta), I)
    errors = [ZERO] * q + [error] * (2 * pairs)
    errors += [ZERO] * (q if closed else 2 * q)
    return gates, errors


def check_excursions() -> dict:
    cases = prefixes = sharp_controls = 0
    for q in range(1, 13):
        b = F(2**q)
        for pairs in (1, q, 16):
            for closed in (True, False):
                eta = F(1, 2 ** (4 * q + 12))
                gates, errors = excursion(q, pairs, closed, eta)
                exact, rounded, _, rho, envelope = trajectory(
                    gates, errors, [ZERO] * len(gates))
                c = F(1) if closed else b
                expected = I if closed else scale(1 / b)
                defect = ((F(0), F(0)), (2 * pairs * b**2 * c * eta, F(0)))
                need(exact == expected, "exact endpoint")
                need(sub(rounded, exact) == defect, "sharp defect identity")
                need(rho == 2 * pairs * b**2 * eta, "exact interaction radius")
                need(envelope == 3 * b / 2, "exact prefix envelope")
                need(max(norm(a) for a in gates) <= 2, "bounded exact gates")
                need(max(norm(inv(a)) for a in gates) <= 2, "bounded inverses")
                for a, e in zip(gates, errors, strict=True):
                    r = add(a, e)
                    need(r[0][0] * r[1][1] - r[0][1] * r[1][0] == 1,
                         "rounded shear determinant")
                check_bound(gates, errors, [ZERO] * len(gates))
                if q >= 4 and pairs == q:
                    need(norm(defect) > len(gates) * envelope * c * eta,
                         "quadratic power cannot be replaced by linear")
                    sharp_controls += 1
                cases += 1
                prefixes += len(gates)
    return {"sharp_families": cases, "literal_prefixes": prefixes,
            "lower_power_rejections": sharp_controls}


def check_guard() -> dict:
    cases = 0
    noncommuting = [shear(F(1, 2)), ((F(1), F(1, 2)), (F(0), F(1)))]
    for q in range(1, 7):
        gates, _ = excursion(q, q, True, F(1, 16))
        gates[q:q] = noncommuting + [inv(a) for a in reversed(noncommuting)]
        _, _, _, _, b = trajectory(gates, [ZERO] * len(gates), [ZERO] * len(gates))
        for p in (0, 1, 8, 32):
            k = len(gates)
            guard = 0
            for exponent in range(128):
                if 2**exponent >= 8 * k * b**2:
                    guard = exponent
                    break
            need(guard > 0, "guard search exhausted")
            eta = F(1, 2 ** (p + guard))
            errors = [((eta, -eta), (eta, eta))] * k
            noise = [((eta, F(0)), (-eta, F(0)))] * k
            rho, _, c = check_bound(gates, errors, noise)
            exact, _, forced, _, _ = trajectory(gates, errors, noise)
            need(c == 1 and rho <= F(1, 4), "closed guard prerequisites")
            need(norm(sub(forced, exact)) <= F(1, 2**p), "precision target")
            cases += 1
    return {"simultaneous_guard_cases": cases}


def check_controls() -> dict:
    rejected = 0
    for operation in (
        lambda: inv(ZERO),
        lambda: excursion(0, 1, True, F(1, 8)),
        lambda: excursion(1, 33, True, F(1, 8)),
        lambda: trajectory([I], [], [ZERO]),
        lambda: check_bound([I], [sub(shear(F(1)), I)], [ZERO]),
    ):
        try:
            operation()
        except ValueError:
            rejected += 1
        else:
            raise ValueError("invalid input accepted")
    gates, errors = excursion(2, 2, True, F(1, 2**12))
    exact, rounded, _, _, _ = trajectory(gates, errors, [ZERO] * len(gates))
    need(norm(sub(rounded, exact)) > sum(norm(e) for e in errors),
         "endpoint-only premise control")
    for q in range(1, 7):
        b = F(2**q)
        a = scale(1 / b**2)
        delta = ((-1 / b**2, F(0)), (F(0), F(0)))
        try:
            inv(add(a, delta))
        except ValueError:
            rejected += 1
        else:
            raise ValueError("singular perturbation accepted")
    return {"invalid_input_rejections": rejected, "endpoint_only_rejections": 1}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true", help="print generated receipt")
    args = parser.parse_args()
    package = Path(__file__).resolve().parent
    source = package.parents[1] / "research/simultaneous-gate-rounding/README.md"
    pins = json.loads((package / "SOURCES.json").read_text())
    pin = next(row for row in pins["files"] if row["usage"] == "input")
    need(hashlib.sha256(source.read_bytes()).hexdigest() == pin["sha256"],
         "predecessor source bytes differ")
    result = {"status": "PASS_CLOSED_WORD_ROUNDING_GUARD", "claim_type": "scoped proof"}
    result.update(check_excursions())
    result.update(check_guard())
    result.update(check_controls())
    if args.emit:
        result["files_sha256"] = {
            name: hashlib.sha256((package / name).read_bytes()).hexdigest()
            for name in ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")
        }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

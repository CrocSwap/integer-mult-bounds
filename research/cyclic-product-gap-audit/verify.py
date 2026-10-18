"""Exact product-gap audit. The retained caller and its sources are unchanged."""
from fractions import Fraction as F
import argparse
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path
import random
import sys

sys.dont_write_bytecode = True
PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
ZERO, ONE = (F(0), F(0)), (F(1), F(0))
SUBJECT = "research/cubic-cyclic-inverse/source_scan.py"


def need(ok, message):
    if not ok:
        raise ValueError(message)


def add(a, b): return a[0]+b[0], a[1]+b[1]
def sub(a, b): return a[0]-b[0], a[1]-b[1]
def mul(a, b): return a[0]*b[0]-a[1]*b[1], a[0]*b[1]+a[1]*b[0]
def norm2(a): return a[0]*a[0]+a[1]*a[1]
def cap(a): return abs(a[0])+abs(a[1])


def divide(a, b):
    q = norm2(b)
    need(q > 0, "zero denominator")
    return ((a[0]*b[0]+a[1]*b[1])/q, (a[1]*b[0]-a[0]*b[1])/q)


def grid(a, bits):
    """Independent quotient/remainder rounding; ties towards +infinity."""
    need(type(bits) is int and bits >= 0, "nonnegative integer precision")
    scale = 1 << bits
    out = []
    for v in a:
        q, r = divmod(v.numerator*scale, v.denominator)
        out.append(F(q+(2*r >= v.denominator), scale))
    return tuple(out)


def check_sources(root=ROOT):
    sources = json.loads((PACKAGE/"SOURCES.json").read_text())
    for row in sources["files"]:
        if row["usage"] == "input":
            path = root/row["path"]
            need(path.is_file(), "missing source: "+row["path"])
            need(hashlib.sha256(path.read_bytes()).hexdigest() == row["sha256"],
                 "source drift: "+row["path"])
    return sources


def load_subject(root=ROOT):
    spec = importlib.util.spec_from_file_location("cyclic_gap_subject", root/SUBJECT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def replay_subject(subject, x, coefficients, beta, bits, direction):
    """Observe the unchanged helper's accesses, roundings and completed values."""
    class Array(list):
        reads = 0
        writes = 0

        def __getitem__(self, key):
            self.reads += 1
            return super().__getitem__(key)

        def __setitem__(self, key, value):
            self.writes += 1
            return super().__setitem__(key, value)

    array = Array(x)
    calls = dict(coefficients=0, rounds=0)
    maximum = F(1)  # Initialized running product.
    original_round, original_sub = subject.rnd, subject.sub

    def observe_round(value, precision):
        nonlocal maximum
        result = original_round(value, precision)
        maximum = max(maximum, norm2(value), norm2(result))
        calls["rounds"] += 1
        return result

    def observe_sub(a, b):
        nonlocal maximum
        result = original_sub(a, b)
        maximum = max(maximum, norm2(result))
        return result

    def coefficient(i):
        calls["coefficients"] += 1
        return coefficients[i]

    subject.rnd, subject.sub = observe_round, observe_sub
    try:
        subject.inverse_scan(array, coefficient, beta, bits, direction)
    finally:
        subject.rnd, subject.sub = original_round, original_sub
    n = len(x)
    need((array.reads, array.writes, calls["coefficients"], calls["rounds"]) ==
         (2*n, n, 2*n, 3*n+1), "literal scan cost/access census")
    return list(array), maximum, calls["rounds"]


def rounded_scan(x, coefficients, bits):
    """Algorithm replay; dense_solve is the separately represented oracle."""
    need(len(x) > 0 and len(x) == len(coefficients), "scan shape")
    z, product = ZERO, ONE
    for b, v in zip(coefficients, x):
        z = grid(add(v, mul(b, z)), bits)
        product = grid(mul(b, product), bits)
    previous = grid(divide(z, sub(ONE, product)), bits)
    output = []
    for b, v in zip(coefficients, x):
        previous = grid(add(v, mul(b, previous)), bits)
        output.append(previous)
    return output


def dense_solve(x, coefficients):
    """Real 2L-by-2L rational elimination, without the affine scan identity."""
    n = len(x)
    need(n > 0 and len(coefficients) == n, "dense shape")
    a = [[F(0) for _ in range(2*n+1)] for _ in range(2*n)]
    for i, (ar, ai) in enumerate(coefficients):
        p = (i-1) % n
        a[2*i][2*i] += 1
        a[2*i+1][2*i+1] += 1
        a[2*i][2*p] -= ar
        a[2*i][2*p+1] += ai
        a[2*i+1][2*p] -= ai
        a[2*i+1][2*p+1] -= ar
        a[2*i][-1], a[2*i+1][-1] = x[i]
    for col in range(2*n):
        pivot = next((r for r in range(col, 2*n) if a[r][col]), None)
        need(pivot is not None, "singular cyclic operator")
        a[col], a[pivot] = a[pivot], a[col]
        d = a[col][col]
        a[col] = [v/d for v in a[col]]
        for r in range(2*n):
            if r != col:
                d = a[r][col]
                a[r] = [v-d*w for v, w in zip(a[r], a[col])]
    return [(a[2*i][-1], a[2*i+1][-1]) for i in range(n)]


def certificate(x, coefficients, bits):
    """Offline exact arithmetic; not a bounded-width production kernel."""
    need(len(x) > 0 and len(x) == len(coefficients), "certificate shape")
    need(type(bits) is int and bits >= 0, "nonnegative integer precision")
    B = max(map(cap, x))
    Q, P, product = F(0), F(1), ONE
    qs, ps = [], []
    for b in coefficients:
        A = cap(b)
        Q, P = 1+A*Q, A*P
        qs.append(Q)
        ps.append(P)
        product = mul(b, product)
    den = sub(ONE, product)
    delta = max(abs(den[0]), abs(den[1]))
    need(delta > 0, "singular cyclic operator")
    u = F(1, 1 << bits)
    need(u*Q < delta, "uncertified rounded denominator")
    seed = B*Q/delta
    seed_error = u*Q*(1+seed)/(delta-u*Q)+u
    errors = [p*seed_error+u*q for p, q in zip(ps, qs)]
    magnitude = max([F(1), B, 1+ps[-1]+u*qs[-1]] + [(B+u)*q for q in qs] +
                    [p+u*q for p, q in zip(ps, qs)] + [seed+seed_error] +
                    [(B+u)*q+p*(seed+seed_error) for p, q in zip(ps, qs)])
    return dict(delta=delta, qs=qs, ps=ps, seed_error=seed_error,
                errors=errors, magnitude=magnitude)


def certify_output(output, ideal, cert):
    need(len(output) == len(ideal) == len(cert["errors"]), "output shape")
    for actual, exact, bound in zip(output, ideal, cert["errors"]):
        need(norm2(sub(actual, exact)) <= bound*bound, "precision certificate")
        need(norm2(actual) <= cert["magnitude"]**2, "magnitude certificate")


def check_receipt(result, path):
    need(path.is_file(), "missing expected result")
    expected = json.loads(path.read_text())
    canonical = lambda value: json.dumps(value, sort_keys=True, separators=(",", ":"),
                                         allow_nan=False)
    need(canonical(expected) == canonical(result), "receipt drift")


def family(k, length):
    need(k >= 1 and length >= 2, "family domain")
    M = F(1 << k)
    bs = [(M, F(0))]+[ONE]*(length-2)+[(1/(4*M), F(0))]
    x = [ZERO]*(length-1)+[ONE]
    ideal = [(4*M/3, F(0))]*(length-1)+[(F(4, 3), F(0))]
    return x, bs, ideal


def run():
    sources = check_sources()
    subject = load_subject()
    seed, rng = 73, random.Random(73)
    k, bits = 8+seed % 8, 8+seed % 5
    x, bs, ideal = family(k, 2)
    witness_output, witness_height, _ = replay_subject(subject, x, bs, F(3, 4), bits, 1)
    witness_cert = certificate(x, bs, bits)
    certify_output(witness_output, ideal, witness_cert)
    need(witness_height <= witness_cert["magnitude"]**2, "witness scalar height")
    error = abs(witness_output[0][0]-ideal[0][0])
    reused_bound = 12*F(1, 1 << bits)/F(3, 4)**3
    need(error == F(1, 12) and reused_bound == F(1, 72), "pinned witness")
    transcript = hashlib.sha256()
    family_cases = certified = uncertified = 0
    rounding_events = 0
    domain = list(itertools.product(range(1, 17), range(2, 17), range(2, 9)))
    rng.shuffle(domain)
    for exponent, precision, length in domain:
        x, bs, ideal = family(exponent, length)
        for cut in range(length):
            rotate = lambda a: a[cut:]+a[:cut]
            xx, bb, ee = rotate(x), rotate(bs), rotate(ideal)
            for direction in (-1, 1):
                physical = xx[:] if direction == 1 else xx[::-1]
                coefficients = bb if direction == 1 else bb[::-1]
                physical, height, rounds = replay_subject(subject, physical, coefficients,
                                                         F(3, 4), precision, direction)
                rounding_events += rounds
                actual = physical if direction == 1 else physical[::-1]
                need(actual == rounded_scan(xx, bb, precision), "literal replay disagreement")
                big = (-cut) % length
                lower = F(1 << exponent, 3*(1 << precision))
                need(abs(actual[big][0]-ee[big][0]) >= lower, "all-cut lattice lower bound")
                scaled = actual[big][0]/F(1 << exponent)
                need(grid((scaled, F(0)), precision)[0] == scaled, "large output lattice")
                try:
                    cert = certificate(xx, bb, precision)
                except ValueError as exc:
                    need(str(exc) == "uncertified rounded denominator", "unexpected failure")
                    uncertified += 1
                else:
                    certify_output(actual, ee, cert)
                    need(height <= cert["magnitude"]**2, "family completed scalar height")
                    certified += 1
                transcript.update(json.dumps([exponent, precision, length, cut, direction,
                    [[str(v) for v in a] for a in actual]], separators=(",", ":")).encode())
                family_cases += 1

    alphabet = [ZERO, (F(1, 4), F(0)), (F(-1, 2), F(1, 4)),
                (F(0), F(3, 2)), (F(2), F(0)), (F(3, 5), F(4, 5))]
    dense_cases = 0
    for trial in range(240):
        n = 1+trial % 6
        bs = [rng.choice(alphabet) for _ in range(n)]
        x = [(F(rng.randrange(-8, 9), 8), F(rng.randrange(-8, 9), 8)) for _ in range(n)]
        product = ONE
        for b in bs:
            product = mul(b, product)
        if product == ONE:
            bs[-1] = ZERO
        cert = certificate(x, bs, 32)
        exact = dense_solve(x, bs)
        # This beta serves only the raw helper's denominator test.
        actual, height, rounds = replay_subject(subject, x, bs,
                                               min(F(1, 16), cert["delta"]), 32, 1)
        rounding_events += rounds
        need(actual == rounded_scan(x, bs, 32), "dense replay disagreement")
        certify_output(actual, exact, cert)
        need(height <= cert["magnitude"]**2, "dense completed scalar height")
        transcript.update(json.dumps([trial, [[str(v) for v in a] for a in exact]],
                                     separators=(",", ":")).encode())
        dense_cases += 1

    caller_cases = 0
    units = [ONE, (F(0), F(1)), (F(3, 5), F(4, 5)), (F(-5, 13), F(12, 13))]
    for length, direction, shift in itertools.product((1, 2, 3), (-1, 1), range(4)):
        phase = lambda i: units[(i+shift) % 4]
        factors = [((F(4), F(0)), F(3, 4), phase, direction)]
        x = [(F(i % 3, 4), F(-i % 2, 8)) for i in range(length)]
        y = [(F(1, 2), F(-1, 8))]*length
        initial_x, initial_y = x[:], y[:]
        target_error, _ = subject.validate(x, y, factors, 1, F(2), 4, 64, 12)
        subject.execute(x, y, factors, 1, F(2), 4, 64, 12)
        need(x == initial_x, "retained source recovery")
        order = list(range(length)) if direction == 1 else list(range(length-1, -1, -1))
        xx = [(-initial_x[i][0]/4, -initial_x[i][1]/4) for i in order]
        bb = [(phase(i)[0]/4, phase(i)[1]/4) for i in order]
        for i, exact in zip(order, dense_solve(xx, bb)):
            need(norm2(sub(sub(y[i], initial_y[i]), exact)) <= target_error**2,
                 "retained full-caller accuracy")
        caller_cases += 1

    controls = []
    def rejected(name, thunk, expected):
        try:
            thunk()
        except ValueError as exc:
            need(str(exc) == expected, "wrong rejection: "+name)
            controls.append(dict(name=name, rejected=str(exc)))
        else:
            raise ValueError("control accepted: "+name)

    x, bs, ideal = family(k, 2)
    u = F(1, 1 << bits)
    wrong = dict(witness_cert, errors=[witness_cert["seed_error"]+u*q
                                      for q in witness_cert["qs"]])
    rejected("omitted_prefix_amplification", lambda: certify_output(witness_output, ideal, wrong),
             "precision certificate")
    wrong = dict(witness_cert, errors=[reused_bound]*2)
    rejected("gap_substituted_for_pointwise_margin",
             lambda: certify_output(witness_output, ideal, wrong), "precision certificate")
    wrong = dict(witness_cert, magnitude=F(4, 3))
    rejected("gap_only_integer_height", lambda: certify_output(witness_output, ideal, wrong),
             "magnitude certificate")
    rejected("rounded_product_can_close_denominator",
             lambda: certificate([ONE], [(F(15, 16), F(0))], 3),
             "uncertified rounded denominator")
    bad = [ONE]
    rejected("actual_rounded_zero_denominator",
             lambda: subject.inverse_scan(bad, lambda i: (F(15, 16), F(0)), F(1, 16), 3, 1),
             "closure denominator")
    factors = [((F(4), F(0)), F(3, 4), lambda i: mul((F(4), F(0)), bs[i]), 1)]
    rejected("retained_caller_excludes_expansive_family",
             lambda: subject.validate(x, [ZERO, ZERO], factors, 1, F(1), 0, 40, 2), "unit phase")
    rejected("singular_exact_cycle", lambda: certificate([ONE, ZERO], [ONE, ONE], 64),
             "singular cyclic operator")
    rejected("source_shape", lambda: certificate([ONE], [ONE, ZERO], 64), "certificate shape")
    rejected("precision_type", lambda: certificate([ONE], [ZERO], True),
             "nonnegative integer precision")
    return dict(status="PASS_CYCLIC_PRODUCT_GAP_AUDIT", assignment_seed=seed,
                base_commit=sources["base_commit"], source_sha256={r["path"]: r["sha256"]
                    for r in sources["files"] if r["usage"] == "input"},
                witness=dict(k=k, bits=bits, length=2, cut=0, M=str(1 << k),
                             product="1/4", closure_gap="3/4", exact_large="2048/3",
                             rounded_large="2731/4", error=str(error),
                             invalid_gap_only_bound=str(reused_bound),
                             safe_error_bound=str(witness_cert["errors"][0]),
                             safe_magnitude_bound=str(witness_cert["magnitude"])),
                family_domain=dict(k=[1, 16], bits=[2, 16], length=[2, 8], cuts="every cut",
                                   directions=[-1, 1], reverse="reflected physical cycle",
                                   order="seed-73 permutation; complete enumeration"),
                family_cases=family_cases, certified_family_cases=certified,
                uncertified_family_cases=uncertified, independent_complex_dense_cases=dense_cases,
                audited_rounding_events=rounding_events,
                raw_helper_cost_census="Every family/dense call: 2L input reads, L writes, 2L coefficient queries and 3L+1 roundings; completed scalar heights checked when the certificate admits.",
                retained_full_caller_cases=caller_cases, transcript_sha256=transcript.hexdigest(),
                controls=controls,
                scope="Written all-length/all-cut obstruction and sufficient bound with exact finite evidence. No current-caller defect, supplier adoption, new kappa or full multiplication proof.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="regenerate this package's RESULT.json")
    args = parser.parse_args()
    result = run()
    path = PACKAGE/"RESULT.json"
    if args.write:
        path.write_text(json.dumps(result, indent=2)+"\n")
    else:
        check_receipt(result, path)
    print(result["status"], "family="+str(result["family_cases"]),
          "dense="+str(result["independent_complex_dense_cases"]),
          "caller="+str(result["retained_full_caller_cases"]),
          "controls="+str(len(result["controls"])), "no_new_kappa")


if __name__ == "__main__":
    main()

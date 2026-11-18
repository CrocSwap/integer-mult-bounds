"""Dense all-event finite replay adapted from the exact #7660 interpreter."""

from fractions import Fraction
from functools import cache
import hashlib
from math import isqrt
from random import Random
from struct import Struct
from time import monotonic_ns


DIM = 512
ADDRESS = range(DIM)
PACK_ROW = Struct("<512I")


class GateInterpreter:
    def __init__(self, prime, require):
        require(type(prime) is int and 5 <= prime < 2**31 and prime % 4 == 1,
                "modulus range and fourth root")
        require(all(prime % f for f in range(3, isqrt(prime) + 1, 2)), "modulus is not prime")
        self.p = prime
        for x in range(2, prime):
            root = pow(x, (prime - 1) // 4, prime)
            if root * root % prime == prime - 1:
                self.i = root
                break
        self.powers = (1, self.i, prime - 1, prime - self.i)
        self.zero = [0] * DIM
        self.gates = {}
        self.require = require

    def coefficient(self, script):
        q = Fraction(script)
        self.require(q.denominator % self.p != 0, "literal denominator vanishes in F_p")
        return q.numerator * pow(q.denominator, -1, self.p) % self.p

    def gate(self, spec):
        if spec in self.gates:
            return self.gates[spec]
        op, *params = spec
        if op == "P":
            rows, = params
            perm = [None] * DIM
            for prev in ADDRESS:
                after = sum(((prev & row).bit_count() % 2) << j for j, row in enumerate(rows))
                self.require(perm[after] is None, "non-permutation gate")
                perm[after] = prev
            gate = ("gather", perm)
        elif op == "X":
            offset, = params
            gate = ("gather", [x ^ offset for x in ADDRESS])
        elif op == "D":
            rows, linear = params
            weights = []
            for mask in ADDRESS:
                phase = 0
                for j, (row, weight) in enumerate(zip(rows, linear)):
                    if mask >> j & 1:
                        phase += weight + 2 * ((row & mask) >> (j + 1)).bit_count()
                weights.append(self.powers[phase % 4])
            gate = ("weights", weights)
        elif op == "phase":
            exponent, = params
            gate = ("phase", self.powers[exponent % 4])
        elif op == "C":
            line, sign = params
            half = (self.p + 1) // 2
            gate = ("mix", (1 + sign * self.i) * half % self.p,
                    (1 - sign * self.i) * half % self.p, [x ^ line for x in ADDRESS])
        else:
            raise ValueError(f"unknown physical gate {op}")
        self.gates[spec] = gate
        return gate

    def apply(self, gates, value):
        p = self.p
        for op, *spec in gates:
            if op == "gather":
                indices, = spec
                value = [value[j] for j in indices]
            elif op == "weights":
                weights, = spec
                value = [a * b % p for a, b in zip(value, weights)]
            elif op == "phase":
                weight, = spec
                if weight != 1:
                    value = [a * weight % p for a in value]
            else:
                c, d, indices = spec
                value = [(c * a + d * value[j]) % p for a, j in zip(value, indices)]
        return value

    def column_residue(self, exact):
        sparse, denominator = exact
        inverse = pow(2, -denominator, self.p)
        target = [0] * DIM
        for x, (re, im) in sparse.items():
            target[x] = (re + self.i * im) * inverse % self.p
        return target


def raw_ports(phase, w, require):
    """The 104 hosted parent-port equations, plus opposite-sign controls."""
    frames = w["frames"]
    require(len(w["live"]) == len(w["ports"]) == 104 and len(set(w["live"])) == 104,
            "raw port count")

    @cache
    def frame(i):
        return phase.frame_op(frames[i])

    def same(x, y):
        return x.tab == y.tab and all(phase.column(x.circ, j) == phase.column(y.circ, j) for j in (0, 1))

    full = phase.op_four(range(9))
    for r, q in zip(w["live"], w["ports"]):
        y = r + 112
        low_x, low_y = w["initial"][r], w["initial"][y]
        high_x, high_y = w["final"][r], w["final"][y]
        require(frames[low_x] == [q] and frames[low_y] == []
                and len(frames[high_x]) == 9 and len(frames[high_y]) == 8, f"port chart dimensions {r}")
        p, v, z = frame(high_y), frame(high_x), frame(low_y)
        qp, qm = phase.op_c(q, 1), phase.op_c(q, -1)
        d = qm.then(full)
        low_adapter = phase.lower(qp.dag().then(frame(low_x)))
        high_adapter = phase.lower(p.dag().then(d))
        require(low_adapter["rank"] == high_adapter["rank"] == 0, f"port adapter rank {r}")
        circ = phase.recipe_circuit(high_adapter)
        mp = phase.Op(phase.tableau(circ), circ)
        xx = qp.dag().then(v)
        yy = z.dag().then(p).then(mp)
        yx = qp.dag().then(p).then(mp)
        xy = z.dag().then(v)
        require(same(xx, d) and same(yy, d) and same(yx, qm.then(d)) and same(xy, qp.then(d)),
                f"raw port operator identity {r}")
        require(not same(xy, qm.then(d)) and not same(yx, qp.then(d)),
                f"raw port operator sign control {r}")
    return {"ports": 104, "directions": 4, "opposite_sign_rejections": 208,
            "comparisons": "signed Pauli action and Gaussian absolute phase"}


def digest(rows):
    value = hashlib.sha256()
    for row in rows:
        value.update(PACK_ROW.pack(*row))
    return value.hexdigest()


def evaluate(phase, source, candidate, prime, seed, altered_clock, test_wrong_phase, require):
    """Evaluate dense finite fields. Compiled MOVEs and oracle frame maps differ."""
    t0 = monotonic_ns()
    field = GateInterpreter(prime, require)
    frames, n = source["frames"], source["public"]
    size = n + source["owned_fields"]
    rand = Random(seed)
    initial = [[rand.randrange(prime) for _ in ADDRESS] for _ in range(n)]

    @cache
    def direct_frame(frame):
        return phase.frame_circuit(frames[frame])

    @cache
    def chart_operator(frame):
        return phase.frame_op(frames[frame])

    @cache
    def literal(a, b):
        return phase.dagger(direct_frame(a)) + direct_frame(b)

    @cache
    def compiled(a, b):
        lo, hi = (a, b) if len(frames[a]) < len(frames[b]) else (b, a)
        rec = phase.lower(chart_operator(lo).dag().then(chart_operator(hi)))
        require(rec["rank"] == len(frames[hi]) - len(frames[lo]), f"compiled MOVE rank {lo},{hi}")
        circ = phase.recipe_circuit(rec)
        if lo != a:
            circ = phase.dagger(circ)
        return tuple(field.gate(g) for g in circ)

    @cache
    def oracle(a, b):
        return tuple(field.gate(g) for g in literal(a, b))

    @cache
    def residue(value):
        return field.coefficient(value)

    def cvec(a, b, v):
        return field.apply(compiled(a, b), v)

    def pred_move(a, b, v):
        return field.apply(oracle(a, b), v)

    # Independently reduce the exact column convention before using a dense
    # finite vector. Use the actual candidate transition at the control clock.
    endpoints = tuple(candidate["program"][altered_clock][2:4])
    r0 = source["live"][0]
    boundary = (source["initial"][r0], source["final"][r0])
    witnesses = ((endpoints, cvec), (endpoints[::-1], cvec), (boundary, pred_move))
    for (a, b), move in witnesses:
        for j in (0, 5):
            v = [0] * DIM
            v[j] = 1
            require(move(a, b, v) == field.column_residue(phase.column(literal(a, b), j)),
                    f"finite versus exact interpreter column {a},{b},{j}")

    def scale(vector, a):
        return [a * x % prime for x in vector]

    def plus(x, a, y):
        return [(u + a * v) % prime for u, v in zip(x, y)]

    def replay(word, inject=False):
        values = initial + [field.zero] * (size - n)
        erased = hashlib.sha256()
        clears, copy_checks = 0, 0
        for i, e in enumerate(word["program"]):
            op, r = e[:2]
            if op == "MOVE":
                row = cvec(e[2], e[3], values[r])
                values[r] = scale(row, field.i) if inject and i == altered_clock else row
            elif op == "INIT":
                require(not any(values[r]), f"nonzero dead owned state at INIT {i}")
                values[r] = field.zero
            elif op == "CLEAR":
                erased.update(PACK_ROW.pack(*values[r]))
                values[r] = field.zero
                clears += 1
            elif op == "SCALE":
                values[r] = scale(values[r], residue(e[2]))
            else:
                if op == "COPY":
                    if any(values[r]) and inject:
                        return None, {"detected_at_COPY": i}
                    require(not any(values[r]), f"nonzero owned COPY target at {i}")
                    copy_checks += 1
                values[r] = plus(values[r], residue(e[3]), values[e[2]])
        require(not any(any(v) for v in values[n:]), "nonzero final owned payload")
        return values, {"events": len(word["program"]), "ordered_clear_values": erased.hexdigest(),
                        "clears": clears, "copy_zero_checks": copy_checks}

    H = source["hosted"]
    require(H["mode"] == "mix-t0", "hosted native model")
    live, dp = source["live"], H["Dports"]
    x2, y2 = H["X2"], H["Y2"]
    require(len(dp) == len(set(dp)) == len(x2) == len(y2) and set(dp) <= set(range(104)),
            "hosted second-port count")
    mains = set(live) | {r + 112 for r in live} | set(x2) | set(y2)
    require(len(mains) == 2 * (104 + len(x2)), "overlapping hosted role")
    alpha1, beta1 = map(Fraction, (H["alpha"], H["beta"]))
    alpha2, beta2 = map(Fraction, (H["alpha2"], H["beta2"]))
    require(alpha2, "nonzero second-port sign witness")
    lo, hi = source["initial"], source["final"]

    def row_from(r, s):
        return pred_move(lo[s], hi[r], initial[s])

    def expected(rows, r, s, a, b):
        rows[r] = plus(row_from(r, r), residue(a), row_from(r, s))
        rows[s] = plus(scale(row_from(s, r), residue(b)), residue(1 + a * b), row_from(s, s))

    ref = [None] * n
    for k, x in enumerate(live):
        a, b = (0, 1) if k in dp else (alpha1, beta1)
        expected(ref, x, x + 112, a, b)
    for x, y in zip(x2, y2):
        expected(ref, x, y, alpha2, beta2)
    for r in range(n):
        if r not in mains:
            ref[r] = row_from(r, r)
    require(all(row is not None for row in ref), "incomplete physical endpoint predictor")

    old, old_counts = replay(source)
    new, new_counts = replay(candidate)
    for label, data in (("source", old), ("candidate", new)):
        bad = [r for r in range(n) if data[r] != ref[r]]
        require(not bad, f"{label} physical endpoint mismatch {bad[:12]}")
    require(old == new, "paired physical endpoints differ")
    require(old_counts.keys() == new_counts.keys()
            and all(old_counts[k] == new_counts[k] for k in old_counts if k != "events"),
            "ordered CLEAR values or COPY zero observations differ")
    wrong_ref = [None] * n
    for x, y in zip(x2, y2):
        expected(wrong_ref, x, y, -alpha2, beta2)
    wrong_sign = [r for r in (*x2, *y2) if new[r] != wrong_ref[r]]
    require(bool(wrong_sign), "wrong second-port alpha sign accepted")
    failed = None
    if test_wrong_phase:
        mutated, counts = replay(candidate, inject=True)
        failed = counts if mutated is None else {"endpoint_rows": [
            r for r in range(n) if mutated[r] != ref[r]]}
        require(failed.get("detected_at_COPY") is not None or bool(failed.get("endpoint_rows")),
                "wrong edited transition phase accepted")
    return {
        "status": "PASS_PAIRED_DENSE_PHYSICAL_WORDS",
        "prime": prime, "seed": seed, "i_squared_minus_one": field.i,
        "endpoint_rows": n, "owned_zero_rows": size - n, "vector_width": DIM,
        "elapsed_ns": monotonic_ns() - t0,
        "digests": {"initial": digest(initial), "source": digest(old), "candidate": digest(new),
                    "reference_public": digest(ref)},
        "source": old_counts, "candidate": new_counts,
        "wrong_second_alpha_rows": wrong_sign, "wrong_edited_transition_phase": failed,
        "six_finite_exact_column_crosschecks": 6,
        "scope": "One deterministic dense input at this modulus through every literal event",
    }

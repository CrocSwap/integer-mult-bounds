"""Exact outer-interface experiments; no Gaussian or large-supplier execution."""
from fractions import Fraction as F
from importlib.util import module_from_spec, spec_from_file_location
from itertools import product
from math import prod
from random import Random

from packing import need, ordinary_product, read_signed, receipt, ring_product, signed_words


def load(path):
    spec = spec_from_file_location("retained_physical_layout", path)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def parameters():
    epsilon, c, delta = F(1, 40), F(1, 500), F(1, 16)
    tau, lamp, kappa = F(99830289, 10**8), F(599, 600), F(1, 20000000)
    gaps = {"prefix": 1 - epsilon * (1 + c),
            "exact_K_transposition": epsilon * c * (1 - tau),
            "normalized_layers": epsilon * (1 - lamp),
            "nonadjacent_exposure": (1 - tau) * (1 - epsilon),
            "Gaussian": 1 - F(3, 4) - delta - 3 * epsilon / 2,
            "scalar": 1 - epsilon - delta, "short_products": epsilon}
    need(all(x > kappa for x in gaps.values()), "all charged costs below target")
    need(min(gaps.values()) == F(169711, 2 * 10**12), "identified bottleneck")
    need(min(gaps.values()) - kappa == F(69711, 2 * 10**12), "strict log margin")
    need(1 - tau - epsilon * (2 - tau) < 0, "old adjacent exposure rejects candidate")
    need(min(gaps.values()) < 2 * kappa, "do not reuse doubled-margin assertion")
    need(F(8, 7)**20 > 6, "gamma constant replacement")
    # For b>=2^24, write x=log2(b)>=24. 32*b^(11/20)<=b/4
    # follows from (9/20)*x>=7. The final error follows from
    # log2(896)+x < 10+x < 3*2^x/4, increasing thereafter.
    need(F(9, 20) * 24 > 7 and 10 + 24 < 3 * (1 << 24) // 4,
         "gamma and exact recovery cutoff")
    return {"epsilon": str(epsilon), "spacing": str(c), "tau": str(tau),
            "lambdaPrime": str(lamp), "delta": str(delta), "kappa": str(kappa),
            "savings": {k: str(v) for k, v in gaps.items()},
            "minimum_gap_above_kappa": str(min(gaps.values()) - kappa),
            "layer_geometry": str(1 - epsilon * (1 + c)),
            "layer_precision": str(1 - epsilon), "spacing_growth": str(epsilon * c)}


def packing_checks():
    rng = Random(2287)
    account = receipt()
    cases = 0
    witness = None
    for p in (2, 3, 5, 9):
        for r in (2, 4, 8, 16):
            if r >= 1 << p:
                continue
            choices = [(0, 0), (1 << p, 0), (-(1 << p), 0),
                       (0, 1 << p), (0, -(1 << p)), (1, -1), (-1, 1)]
            for _ in range(24):
                f = [rng.choice(choices) for _ in range(r)]
                g = [rng.choice(choices) for _ in range(r)]
                exact, actual = ring_product(f, g, p, account)
                oracle = [[0, 0] for _ in range(r)]
                for i, (a, b) in enumerate(f):
                    for j, (c, e) in enumerate(g):
                        sign = 1 if i + j < r else -1
                        z = oracle[(i + j) % r]
                        z[0] += sign * (a * c - b * e)
                        z[1] += sign * (a * e + b * c)
                need(exact == [tuple(z) for z in oracle], "four packed products vs direct negacyclic")
                scale = 2**p * r
                need(actual == [tuple(int(F(v, scale)) for v in z) for z in oracle],
                     "truncation toward zero at output boundary")
                if witness is None and exact != ring_product(f, g, p, receipt(), "cyclic_wrap")[0]:
                    witness = {"p": p, "r": r, "f": [list(z) for z in f], "g": [list(z) for z in g]}
                cases += 1
    need(account["negative_evaluations"] > 0 and account["negative_product_end_carries"] > 0,
         "negative signed stream coverage")
    try:
        ordinary_product([-4, 0], [4, 0], 2, receipt(), "omit_sign_extension")
    except ValueError as exc:
        need("sign extension" in str(exc), "specific sign-extension rejection")
    else:
        raise ValueError("missing sign extension accepted")
    good = ring_product([(3, 0)] * 2, [(3, 0)] * 2, 2, receipt())[1]
    bad = ring_product([(3, 0)] * 2, [(3, 0)] * 2, 2, receipt(), "omit_r_normalization")[1]
    need(good != bad and witness is not None, "normalization and wrap controls")
    return {"cases": cases, "traffic": account, "wrong_wrap_witness": witness,
            "controls": ["missing negative sign extension", "cyclic wrap", "missing division by r"]}


def transform(data, schedule, physical, opposite=False, truncate=True):
    """Numerator arithmetic; each complete round has one p-grid truncation."""
    out = [[F(v) for v in row] for row in data]
    if not opposite:
        out = physical.relocate(out, schedule)
    r, slots = 1 << schedule["ell"], schedule["slots"]
    masks = {slot: 1 << (len(slots) - 1 - j) for j, slot in enumerate(slots)}
    levels = range(schedule["ell"]) if opposite else reversed(range(schedule["ell"]))
    for h in levels:
        axes = [i for i, a in enumerate(schedule["lengths"]) if h < a]
        if not axes:
            continue
        def twiddle():
            for address, row in enumerate(out):
                exponent = 0
                for i in axes:
                    low = sum(1 << v for v in range(h) if address & masks[i, v])
                    exponent -= (2 * r // (1 << (h + 1))) * bool(address & masks[i, h]) * low
                out[address] = physical.monomial(row, -exponent if opposite else exponent)
        if opposite:
            twiddle()
        for i in axes:
            mask = masks[i, h]
            for address in range(len(out)):
                if not address & mask:
                    other = address | mask
                    a, b = out[address], out[other]
                    out[address] = [(x + y) / 2 for x, y in zip(a, b)]
                    out[other] = [(x - y) / 2 for x, y in zip(a, b)]
        if not opposite:
            twiddle()
        if truncate:
            out = [[F(int(v)) for v in row] for row in out]
    return physical.relocate(out, schedule, inverse=True) if opposite else out


def convolution_checks(root):
    physical = load(root / "research/synthetic-layout-independent/physical.py")
    rng = Random(2291)
    cases, rounded_loss, max_ratio = 0, 0, F(0)
    for ell, width, longs in ((2, 1, (True,)), (3, 2, (False, True)),
                               (4, 2, (False,)), (3, 1, (True, False))):
        plan = physical.plan(ell, width, longs)
        M, r, p = 1 << sum(plan["lengths"]), 1 << ell, 10
        for _ in range(8):
            f = [[rng.randrange(-300, 301) for _ in range(r)] for _ in range(M)]
            g = [[rng.randrange(-300, 301) for _ in range(r)] for _ in range(M)]
            u, v = transform(f, plan, physical), transform(g, plan, physical)
            exact_u = [[F(x, M) for x in row] for row in physical.execute(f, plan)]
            need(transform(f, plan, physical, truncate=False) == exact_u,
                 "same normalized retained exact operator")
            need(max(abs(x - y) for a, b in zip(u, exact_u) for x, y in zip(a, b)) < ell,
                 "per-component complete-round error")
            packed = []
            for a, b in zip(u, v):
                _, out = ring_product([(int(x), 0) for x in a], [(int(x), 0) for x in b], p, receipt())
                packed.append([x for x, _ in out])
            actual = [[M * x for x in row] for row in transform(packed, plan, physical, opposite=True)]
            # Separate dense cyclic-address and negacyclic-coefficient oracle.
            sizes = [1 << a for a in plan["lengths"]]
            coords = list(product(*(range(s) for s in sizes)))
            def address(z):
                value = 0
                for x, s in zip(z, sizes):
                    value = value * s + x
                return value
            oracle = [[0] * r for _ in range(M)]
            for i, a in enumerate(coords):
                for j, b in enumerate(coords):
                    target = address([(x + y) % s for x, y, s in zip(a, b, sizes)])
                    for x in range(r):
                        for y in range(r):
                            oracle[target][(x + y) % r] += (1 if x + y < r else -1) * f[i][x] * g[j][y]
            error = max(abs(x - F(y, (1 << p) * r * M))
                        for a, b in zip(actual, oracle) for x, y in zip(a, b))
            bound = M * (3 * ell + 1)
            need(error < bound, "composed convolution per-component error")
            max_ratio = max(max_ratio, error / bound)
            rounded_loss += int(u != exact_u)
            cases += 1
    need(rounded_loss == cases, "nontrivial rounding in all fixtures")
    # A delta pair isolates the M normalization; no rounding is necessary.
    plan = physical.plan(2, 1, (True,))
    data = [[F(int(i == 0 and j == 0)) for j in range(4)] for i in range(4)]
    f = transform(data, plan, physical, truncate=False)
    pointwise = [[sum(a[k] * b[j - k] for k in range(j + 1)) / 4
                  - sum(a[k] * b[j + 4 - k] for k in range(j + 1, 4)) / 4
                  for j in range(4)] for a, b in zip(f, f)]
    inverse = transform(pointwise, plan, physical, opposite=True, truncate=False)
    need(inverse[0][0] == F(1, 64) and 4 * inverse[0][0] == F(1, 16),
         "M scale distinguishes convolution/T from convolution/(TM)")
    return {"cases": cases, "nonzero_rounding_cases": rounded_loss,
            "max_component_error_fraction_of_bound": str(max_ratio),
            "missing_M_control": [str(inverse[0][0]), str(4 * inverse[0][0])],
            "scope": "Small real channels with actual Qp and packed products; Gaussian channel bounds follow componentwise. Indexed layouts are retained finite models."}


def recovery_checks():
    rng = Random(20_000_000)
    count = 0
    for n in range(2, 97):
        b = (n - 1).bit_length()
        radix, scale = 1 << b, 1 << (2 * b + 4)
        q = (n + b - 1) // b
        # Small witness source sizes test the recovery boundary independently
        # of the eventual prime/FFT parameter regime.
        S = 2 * q + 1
        for x, y in [(0, 0), ((1 << n) - 1, (1 << n) - 1),
                     (rng.randrange(1 << n), rng.randrange(1 << n))]:
            a = [(x >> (j * b)) % radix for j in range(q)]
            c = [(y >> (j * b)) % radix for j in range(q)]
            coeff = [sum(a[i] * c[j - i] for i in range(q) if 0 <= j - i < q)
                     for j in range(S)]
            after_three = [F(z, scale * S * S) for z in coeff]
            recovered = [z * S * (scale * S) for z in after_three]
            need(recovered == coeff, "both source scales")
            if x * y:
                need([z * scale * S for z in after_three] != coeff, "missing source S rejected")
            carry, digits = 0, []
            for value in coeff:
                digit = (value + carry) % radix
                carry = (value + carry) // radix
                need(0 <= carry <= q * (radix - 1), "carry invariant")
                digits.append(digit)
            value = sum(z * radix**j for j, z in enumerate(digits)) + carry * radix**S
            need(value == x * y, "exact radix recovery")
            word = signed_words([value], 2 * n + 1)
            need(word[0] == 0 and len(word[1:]) == 2 * n and read_signed(word, 2 * n + 1) == [x * y],
                 "fixed output width including zero inputs")
            count += 1
    # Negative truncation differs from arithmetic shift; widening needs sign extension.
    need(int(F(-1, 2)) == 0 and (-1 >> 1) == -1, "signed truncation control")
    need(read_signed(signed_words([-17], 12), 12) == [-17], "negative widened word")
    need(read_signed(signed_words([-17], 12)[:6], 6) != [-17], "wrong width boundary rejected")
    return {"input_pairs": count, "bit_lengths": [2, 96],
            "controls": ["missing source S", "arithmetic shift for negative truncation", "old-width read after widening"]}


def crt_checks(root):
    physical = load(root / "research/synthetic-layout-independent/physical.py")
    shapes = ((3, 5), (5, 7), (7, 13), (13, 29, 31))
    total, swaps, wrong_direction = 0, 0, 0
    for source in shapes:
        target = [1 << s.bit_length() for s in source]
        widths = [t.bit_length() - 1 for t in target]
        need(max(widths) - min(widths) <= 1, "outer adjacent axis-width domain")
        d, S, T = len(source), prod(source), prod(target)
        prefixes = [prod(source[:i]) for i in range(d)]
        inverses = [pow(prefixes[i], -1, source[i]) for i in range(d)]
        # Original stream order is mixed radix with axis0 least significant.
        payload = []
        for z in product(*(range(t) for t in reversed(target))):
            coords = tuple(reversed(z))
            k = sum(a * P for a, P in zip(coords, prefixes))
            payload.append((k, -k - 1, 3 * k + 7) if all(a < s for a, s in zip(coords, source)) else None)
        original = payload.copy()
        current_widths = list(reversed(widths))

        def exchange(data, ws, i, j):
            nonlocal swaps
            left, right = sum(ws[:i]), sum(ws[:j])
            a, b = ws[i], ws[j]
            if a == b:
                operations = [("swap", left, right, a)]
            elif a == b + 1:
                operations = [("swap", left + 1, right, b), ("move", left, right - 1, 1)]
            else:
                operations = [("move", right, left, 1), ("swap", left + 1, right + 1, a)]
            out = data
            for op in operations:
                moved = [None] * len(out)
                for address, value in enumerate(out):
                    moved[physical.move_address(address, sum(ws), op)] = value
                out = moved
            ws[i], ws[j] = ws[j], ws[i]
            swaps += 1
            return out

        for i in range(d // 2):
            payload = exchange(payload, current_widths, i, d - 1 - i)
        need(current_widths == widths, "nonadjacent reversal")
        coords = list(product(*(range(t) for t in target)))
        def index(z):
            a = 0
            for v, t in zip(z, target):
                a = a * t + v
            return a
        def update(data, i, inverse=False):
            out = [None] * T
            for j, z in enumerate(coords):
                dest = list(z)
                if z[i] < source[i] and all(z[k] < source[k] for k in range(i)):
                    shift = inverses[i] * sum(z[k] * prefixes[k] for k in range(i))
                    dest[i] = (z[i] + (-shift if inverse else shift)) % source[i]
                out[index(dest)] = data[j]
            return out
        exposed = payload.copy()
        for i in reversed(range(d)):
            payload = update(payload, i)
        for address, value in enumerate(payload):
            z = coords[address]
            valid = all(a < s for a, s in zip(z, source))
            need((value is not None) == valid, "padded validity invariant")
            if valid:
                k = value[0]
                need(z == tuple(k * mu % s for mu, s in zip(inverses, source)),
                     "triangular shift equals algebraic Phi")
        bad = exposed.copy()
        for i in range(d):
            bad = update(bad, i)
        wrong_direction += int(bad != payload)
        # Widen and restore serialized signed payload before inverse routing.
        max_value = 3 * S + 7
        old_width = max_value.bit_length() + 2
        for j, row in enumerate(payload):
            if row is not None:
                words = signed_words(list(row), old_width + 7)
                payload[j] = tuple(read_signed(words, old_width + 7))
        for i in range(d):
            payload = update(payload, i, inverse=True)
        for i in reversed(range(d // 2)):
            payload = exchange(payload, current_widths, i, d - 1 - i)
        need(payload == original, "whole payload and padding inverse")
        total += T
    need(wrong_direction > 0, "updated lower-control chronology rejected")
    return {"shapes": [list(s) for s in shapes], "complete_padded_records": total,
            "whole_axis_exchanges": swaps, "wrong_update_order_witnesses": wrong_direction,
            "scope": "Finite physical address model with signed multiword payload; includes actual widening before the inverse."}


def floor_root(n, k):
    need(n >= 1 and k >= 1, "positive integer root")
    x = 1 << ((n.bit_length() + k - 1) // k)
    while True:
        y = ((k - 1) * x + n // x**(k - 1)) // k
        if y >= x:
            break
        x = y
    need(x**k <= n < (x + 1)**k, "exact root certificate")
    return x


def compressed_domains():
    records = []
    for log_b in (40, 1000, 20000, 40000, 524288):
        # n=2^b, b=2^log_b. We store log2(T), never n, T or r.
        b = 1 << log_b
        p = 6 * b
        d = floor_root(p, 40)
        K = floor_root(d, 500)
        log_T = b - log_b + 2
        ell = (log_T + d - 1) // d
        short_axes = d * ell - log_T
        alpha4 = 12 * d * d * b
        alpha = floor_root(alpha4, 4)
        alpha += alpha**4 != alpha4
        gamma = 2 * d * alpha * alpha
        G = 4 * p.bit_length() + 6
        H = d * G
        q0 = 2642 * 2 * d.bit_length()
        Q0 = q0 + (2 * H + K - 1) // K + (H + K - 1) // K
        need(0 <= short_axes < d and p <= 12 * d * ell <= 4 * p,
             "mixed long/short transform bands")
        need(d**40 <= p < (d + 1)**40 and d <= b and 1 <= K <= ell - 1,
             "literal extended layer parameters")
        need(gamma <= b // 4 and alpha * alpha < p, "original Gaussian domain")
        # log(r/2)>8d and r/2>8d^2*log(r/2), using log(2)>1/2.
        prime_room = ell - 1 > 16 * d and ell - 1 > 3 + 2 * d.bit_length() + ell.bit_length()
        conditions = {"prime_interval_room": prime_room, "nonempty_reserved_core": Q0 < d - 1,
                      "guard_at_most_p": (d << 210000) <= p,
                      "superlogarithmic_chunk_sample": K > p.bit_length()}
        records.append({"log2_b": log_b, "d_bits": d.bit_length(), "K_bits": K.bit_length(),
                        "ell_bits": ell.bit_length(), "conditions": conditions})
    need(all(records[-1]["conditions"].values()), "one compressed admitted large caller")
    need(not records[0]["conditions"]["guard_at_most_p"], "do not claim the early cutoff suffices")
    return {"samples": records,
            "scope": "Exact logarithmic-size descriptions, not allocated arrays or a proof of the entire eventual range."}

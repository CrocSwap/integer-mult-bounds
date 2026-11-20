#!/usr/bin/env python3
"""Recount the frozen pair and independently verify the #7831 finite delta."""

import argparse
from collections import Counter
from fractions import Fraction as Q
from functools import cache
import gzip
from hashlib import sha1, sha256
import importlib.util
import json
import os
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "source"
CACHE = Path(os.environ.get("P104_REVIEW_CACHE", HERE / "work-cache"))
HEAD = "2d1fb9c878ae1e292cb918de40fa8e4f7fa7f75e"
BASE = "14c74c6a67108f675ac1196a5f2415ead0920e71"
PRED = "89a67c404226d51028e135de2b9169e9020d57af"
PREMISES = ["native_all_columns", "owned_erasure", "compiler", "precision_tape", "analytic_recovery"]
GRID = 10**70
SOURCE_BLOBS = {
    "AUDIT.json": "9c523c63740eb3580bc22407cf2fc4d70dd25956",
    "BIT.json": "a85717b5fd10483540cc736750df75cfa7187b67",
    "BitTailCertificate.lean": "14146af0434a85031e7314e79124acaa2219214e",
    "LICENSE": "261eeb9e9f8b2b4b0d119366dda99c6fd7d35c64",
    "README.md": "4a1d053f5de294989226a69f07b973b5b9a8b74d",
    "RESULT.json": "f0df1c06f497e5645e4420d428114e9717b324f9",
    "SOURCES.json": "0ba3a8c4516ff567d4c9cabfa268647f648ba0bb",
    "verify.py": "73b2bf926599036c46e86f1c35809f9d5d8984df",
}


def check(condition, name):
    if not condition:
        raise ValueError(name)


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def read(path):
    data = path.read_bytes()
    return json.loads(gzip.decompress(data) if data.startswith(b"\x1f\x8b") else data)


def source_pins():
    receipts = {}
    for name, pin in SOURCE_BLOBS.items():
        path = SOURCE / name
        raw = path.read_bytes()
        header = f"blob {len(raw)}\0".encode()
        check(sha1(header + raw).hexdigest() == pin, f"exact Git blob {name}")
        receipts[name] = {"git_blob": pin, "sha256": digest(path)}
    dependencies = read(SOURCE / "SOURCES.json")
    for source in dependencies:
        path = CACHE / str(source["pr"]) / source["path"]
        check(digest(path) == source["sha256"], f"predecessor pin {path}")
    return receipts, dependencies


def ceildiv(a, b):
    return -((-a) // b)


def enclose(x):
    p = x.numerator * GRID
    return p // x.denominator, ceildiv(p, x.denominator)


def add(a, b):
    return a[0] + b[0], a[1] + b[1]


def sub(a, b):
    return a[0] - b[1], a[1] - b[0]


def mul(a, b):
    products = [x * y for x in a for y in b]
    return min(products) // GRID, ceildiv(max(products), GRID)


def quotient(a, b):
    check(0 <= a[0] <= a[1] and 0 < b[0] <= b[1], "positive interval division")
    return a[0] * GRID // b[1], ceildiv(a[1] * GRID, b[0])


def scale(a, c):
    return mul(a, enclose(Q(c)))


def report_interval(interval, places=48):
    factor = 10**places

    def fixed(value):
        head, tail = divmod(abs(value), factor)
        return f"{'-' if value < 0 else ''}{head}.{tail:0{places}}"

    return [fixed(interval[0] * factor // GRID),
            fixed(ceildiv(interval[1] * factor, GRID))]


def small_log(x):
    z = (x - 1) / (x + 1)
    z_squared = z * z
    power = z
    partial = Q(0)
    for term in range(80):
        partial += 2 * power / (2 * term + 1)
        power *= z_squared
    tail = 2 * power / (161 * (1 - z_squared))
    return enclose(partial)[0], enclose(partial + tail)[1]


@cache
def log_int(r):
    power = r.bit_length() - 1
    return add(scale(small_log(Q(2)), power), small_log(Q(r, 2**power)))


def exp_closed(x):
    """Positive Taylor series on [0, 1/8], then interval squaring."""
    check(x[0] >= 0, "nonnegative exponent argument")
    squarings, divisor = 0, 1
    while 8 * x[1] > divisor * GRID:
        squarings += 1
        divisor *= 2
    y = scale(x, Q(1, divisor))
    term = result = (GRID, GRID)
    for n in range(1, 57):
        term = scale(mul(term, y), Q(1, n))
        result = add(result, term)
    next_term = scale(mul(term, y), Q(1, 57))
    # Rounding y by one grid ulp still gives less than 1/7, so
    # twice the first omitted term bounds the whole positive tail.
    check(y[1] * 7 < GRID, "geometric exponential tail")
    result = result[0], result[1] + 2 * next_term[1]
    for _ in range(squarings):
        result = mul(result, result)
    return result


@cache
def power(rank, exponent):
    return exp_closed(scale(log_int(rank), exponent))


def moment(histogram, exponent):
    result = (0, 0)
    for rank, multiplicity in histogram.items():
        result = add(result, scale(power(rank, exponent), multiplicity))
    return result


def histogram(value):
    return Counter({int(rank): count for rank, count in value.items()})


def native_binary(word_path, caller_path):
    module_path = HERE.parents[1] / "p104-binary-three-ingress-cut" / "replay.py"
    check(digest(module_path) == "82c7fe4bd5cc0579c5bb86291edaca0e910bb0067654c7bf0c281c61b60d9d6e",
          "frozen independent S9 binary reviewer")
    spec = importlib.util.spec_from_file_location("s9_operator", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    word = module.load_json(word_path, module.WORD_GZIP, compressed=True)
    caller = module.load_json(caller_path, module.CALLER, compressed=True)
    check(module.canonical_hash(word) == module.WORD, "binary word identity")
    layout = module.canonical_hash({key: word[key] for key in ("frames", "start", "final")})
    check(layout == module.LAYOUT, "binary layout identity")
    atlas = module.Atlas(word["frames"])
    contacts = atlas.main_contacts(word["start"], word["final"])
    forward, adjoint, omitted_add = module.native_checks(word, atlas)
    forward_tape = {(k, p.source, p.receiver, p.grade, p.clock) for k, p in forward.packets.items()}
    adjoint_tape = {(k, p.receiver, p.source, p.grade, p.clock) for k, p in adjoint.packets.items()}
    check(forward_tape == adjoint_tape, "both orientations reconstructed identical paid grades")
    _, _, paid, targets = module.binary_invoice(word, caller, atlas, forward)
    ordinary = module.ordinary_boundary(word, caller, paid, targets)
    return paid, targets, {"public": word["public"], "main_contacts": contacts, "frames": len(atlas.body),
                           "dirty_retirement_each_way": forward.dirty, "caller_coefficients_each_way": 38**2,
                           "owner_411_bridge": 3553, "omitted_add_clock": omitted_add,
                           "layout": layout, "word": module.WORD, "caller": module.CALLER, **ordinary}


def native_rational(application):
    native, caller = application["native"], application["caller_census"]
    invoice = application["application"]["invoice"]
    check(caller["calls"] == 48 and native["public"] == 1289, "rational caller dimensions")
    check(native["retired_and_guards_restored"] and native["all_public_inputs_preserved_until_final_installs"]
          and native["exact_all_public_rows"] == native["exact_source_columns"] == 1289, "arbitrary rows and retirement")

    def recount(native_key, fixed_key, invoice_key):
        value = Counter({rank: caller["calls"] * n for rank, n in histogram(native[native_key]).items()})
        value.update(histogram(caller[fixed_key]))
        check(value == histogram(invoice[invoice_key]), f"complete caller histogram {invoice_key}")
        return value

    paid = recount("paid_native_ranks", "fixed_caller_paid", "paid")
    targets = recount("positive_helper_ranks", "fixed_root_targets", "targets")
    ordinary = application["application"]["ordinary"]
    check(sum(paid.values()) == ordinary["raw_paid_positions"]
          and sum(targets.values()) == ordinary["raw_productive_targets"], "matched rational ordinary counts")
    check(32 * sum(ordinary["raw_scalar_incidence_allowance_before_factor_32"].values())
          == ordinary["scalar_services"], "all charged scalar services")
    return paid, targets, ordinary


def directed_invoice(paid, targets, bracket, enrolled):
    lo, hi = (sub(moment(targets, 1 - Q(k)), moment(paid, 1 - Q(k))) for k in bracket)
    check(lo[0] > 0 > hi[1], "directed signs at raw crossing endpoints")
    coeff = targets.copy()
    coeff.subtract(paid)
    derivative_upper = 0
    for rank, signed_count in coeff.items():
        # Positive signed mass has a negative derivative with greatest value
        # at enrolled. Paid mass has a positive derivative maximized at zero.
        at = 1 - enrolled if signed_count > 0 else Q(1)
        term = scale(mul(power(rank, at), log_int(rank)), -signed_count)
        derivative_upper += term[1]
    check(derivative_upper < 0 and Q(bracket[1]) < enrolled, "unique decreasing crossing through target")
    signed = sub(moment(targets, 1 - enrolled), moment(paid, 1 - enrolled))
    check(signed[1] < 0, "negative signed target balance")
    return {"raw_crossing": bracket, "endpoint_margins": [report_interval(lo), report_interval(hi)],
            "derivative_upper_through_enrolled_target": report_interval((derivative_upper, derivative_upper))[1],
            "target_signed_margin": report_interval(signed),
            "required_saving": report_interval((-signed[1], -signed[0])),
            "paid": dict(paid), "productive": dict(targets)}


def bit_schedule(bit, paid, targets, seed):
    t, u, w = 1 - Q("0.003879928045154"), Q(11, 50), Q(3, 10)
    v, cutoff, floor, ambient = 416, 10, 16, 134
    raw = moment(targets, t)
    ratios = [quotient(moment(paid, t), raw),
              quotient(moment(paid, t + u), mul(power(cutoff, u), raw)),
              quotient(mul(power(floor, w), moment(targets, t - w)), raw)]
    bounds = [Q(999999999998669, 10**15), Q(473009043448109, 5 * 10**14), Q(94357873737351, 10**14)]
    check(1 - t <= u and w > 0 and max(paid) < max(targets) <= ambient, "tail inequality hypotheses")
    check(all(Q(interval[1], GRID) < cap for interval, cap in zip(ratios, bounds, strict=True))
          and list(map(Q, bit["separation"]["rational_upper_limits"])) == bounds, "outward rational tail caps")
    a, g, l = bounds
    gap = 1 - (1 / (1 + v * (1 - a)) + 2 * g**v + l**v)
    check(gap > Q(333056567, 10**18), "exact rational normalized surplus")
    check(paid[14] > 0 and cutoff**v < 14**v < 15**v, "a literal paid tensor tuple changes subdivision")

    theta, p, H = Q(5, 6), 44, 209400000000000
    check(cutoff**6 < floor**5 and 2 * cutoff**(v * 6) <= ambient**(v * 5),
          "full working ambient and shifted logarithm")
    check(all(cutoff**n >= floor**(n - 1) for n in range(2, 6)), "five-sixths is the first shift on this grid")
    ambient_power = power(ambient, v * (1 - t))
    eta = quotient(enclose(t), ambient_power)
    check(theta**p < Q(eta[0], GRID) <= Q(eta[1], GRID) <= theta**(p - 1)
          and Q(ambient_power[1], GRID) < 2**p, "uniform logarithm power and predecessor failure")
    loss = Q(1, 10**11)
    j = H // loss.denominator
    check(H * loss == j == 2094 and (H + 1)**p < 2**j
          and (H - loss.denominator + 1)**p >= 2**(j - 1), "integer uniform horizon")
    check(2**45 * loss > 256 and 1 + loss / 2 <= 2**j, "delayed-cover strict inequalities")
    check((bit["uniform"]["H"], bit["uniform"]["logarithm_power"]) == (H, p), "archived uniform controls")

    covered, rho, opening = 1 - t - 2 * loss, Q(1, 250), Q(seed)
    check(opening == Q("0.00385248") and covered == Q(bit["covered"]), "selected stock seed and both losses")
    old, stages = opening, []
    for stage in bit["ordinary_bootstrap"]:
        envelope = (1 - rho) * covered + rho * old
        claim = Q(stage["claim"])
        check(old == Q(stage["previous"]) and old < claim < envelope < rho < 1 - envelope
              and claim == Q(int(envelope * 10**15) - 1, 10**15), "literal strict stock stage")
        stages.append({"admitted": stage["claim"], "slack": str(envelope - claim)})
        old = claim
    check(len(stages) == 4 and old == Q(bit["ordinary_admitted"]), "four strict stock stages")
    field_count = sum(targets.values())
    paid_count = sum(paid.values())
    paid_rank_mass = sum(rank * n for rank, n in paid.items())
    check((field_count, paid_count, paid_rank_mass) == (20706, 107460, 291360), "complete finite product inputs")
    occurrences = sum(field_count**(v - 1 - i) * paid_count**i for i in range(v))
    return {"trial": str(1 - t), "ratios": [report_interval(x) for x in ratios],
            "tail_caps": list(map(str, bounds)), "normalized_surplus": report_interval(enclose(gap)),
            "tensor_power": v, "paid_cutoff": "10^416", "productive_floor": "16^416",
            "working_ambient": "134^416", "shift": str(theta), "log_power": p, "log2_carrier": H,
            "loss_each": str(loss), "stock": stages, "admitted": bit["ordinary_admitted"],
            "cover_prime": "odd q > 2^45*N^5 avoiding the frozen finite catalogue witnesses",
            "product_ordinary_record_upper_bit_length":
                (occurrences * bit["native"]["ordinary"]["ordinary_records"] + 2 * field_count**v).bit_length(),
            "product_owned_backing_upper_bit_length":
                (occurrences * bit["native"]["ordinary"]["owned_backing"] + field_count**v).bit_length(),
            "split_paid_call_upper_bit_length": (paid_rank_mass**v).bit_length()}


def outer_margins(kappa, gap, cap):
    """Evaluate the inherited outer conditions on the exact rational parameters."""
    b, a, q = (kappa + n * gap for n in (5, 4, 3))
    eps, beta = 1 - gap, 1 - 3 * gap
    sigma, tau = 1 - b, 1 - a
    internal = tau + (1 - gap) * max(sigma - tau, 0)
    leaf = sigma + gap * (1 - sigma)
    ell = 1 - (q + a) / 2
    xi = eps * (1 + q) - Q(3, 32) + gap
    r0, key = gap / 10, beta + 1 - eps
    recurrence = [eps * q, a, 1 - eps + q * beta, 1 - eps + a * beta, 1 - eps + beta,
                  Q(3, 32) + xi - eps, xi + Q(1, 2) - eps, eps, 1 - (eps + beta + 48 - 128 + 2)]
    strict = [
        cap - a, b - a, q, b - q, a - q, gap, 1 - gap, (1 - gap) * b - a,
        1 - internal - q, 1 - leaf - q, ell - tau, ell - sigma, ell - internal, 1 - q - ell, 1 - q - leaf,
        eps, 1 - eps, xi - Q(1, 2), eps - xi, beta, eps - beta, 1 - beta,
        1 - (2 * xi - 2) - r0 - beta, 1 - (2 * xi - 2) - beta, 1 - eps - r0, 1 - eps, r0, 1 - key,
        1 - beta - 2 * (1 - eps), 128 - 48 - beta, gap, eps - a, Q(1, 32) - b, 2**45 - 7**16,
        2, 2 - xi, 5, 1 - beta, 1 - beta, 1 - eps, recurrence[2] - recurrence[0],
        gap, kappa - Q(".001730970419199163702738"), 1 - eps, Q(11, 2),
    ] + [term - kappa for term in recurrence]
    functional = [1 - beta, beta * Q(997, 1000), 128 - 48 - eps - beta - 1, beta * Q(249, 250)]
    check(min(strict + functional) > 0, "all strict and functional outer conditions")
    return {"strict_count": len(strict), "functional_count": len(functional),
            "minimum_margin": str(min(strict + functional)),
            "BIT_just_below_effective_rejected": a - Q(1, 10**12) < a}


def rational_outer(application, audit, paid, targets, cap, published):
    compiler = audit["outer"]["finite_compiler"]
    claim = Q(published["claim"])
    tested = Q(compiler["tested"])
    gap = (tested - claim) / 7
    check(gap == Q(1, 10**14) and 0 < claim < tested < cap, "outer strict ordinary BIT headroom")
    raw = moment(targets, 1 - tested)
    alpha = quotient(moment(paid, 1 - tested), raw)
    gamma = quotient(moment(paid, 1 - tested + Q(1, 7)), mul(power(11, Q(1, 7)), raw))
    delta = quotient(enclose(Q(12 * sum(targets.values()))), mul(power(11, tested), raw))
    reserve, decay, v = Q(1, 10**27), Q(31, 32), 1920
    check(Q(alpha[1], GRID) < 1 - reserve and max(Q(gamma[1], GRID), Q(delta[1], GRID)) < decay
          and 1 / (1 + v * reserve) + 4 * decay**v < 1, "rational separated compiler moments")
    working_bound = power(153, v * tested)
    eta = quotient(enclose(1 - tested), working_bound)
    p, shift = 2381, Q(63, 64)
    check(shift**(p - 1) < Q(eta[0], GRID) <= Q(eta[1], GRID) <= shift**(p - 2)
          and Q(working_bound[1], GRID) < 2**p, "rational minimum and written log powers")
    check(11**64 < 12**63 and 2 * 11**(v * 64) <= 153**(v * 63), "rational shifted logarithm inequalities")
    H = int(compiler["H"])
    horizon = H // gap.denominator
    check(H * gap == horizon and (H + 1)**p < 2**horizon
          and (H + 1 - gap.denominator)**p >= 2**(horizon - 1), "rational carrier depth cutoff")
    common = application["common_root"]
    guards = application["common_depth_guards"]
    check(common["context_c"] == 856 and common["signed_width"] == "W=p+h+2D+3"
          and common["temporary_width"] == "W+26", "complete common-root width")
    for guard in guards.values():
        level = guard["compiler_H"]
        bits = (common["context_c"] * 1920 * 153**1920 * (level + 1)**2).bit_length()
        check(guard["strict_guard_passed"] and bits == guard["argument_bit_length"] < level, "common root depth")

    # Exact substitution into the inherited input-lift signed transfer.
    positive, negative = {7: 1, 3: 1, 5: 1}, {9: 1, 4: 1, 1: 2}
    d1, curvature = (0, 0), (0, 0)
    check(sum(r * n for r, n in positive.items()) == sum(r * n for r, n in negative.items()),
          "input-lift difference vanishes at zero")
    for rank, n in positive.items():
        d1 = add(d1, scale(log_int(rank), rank * n))
    for rank, n in negative.items():
        lg = log_int(rank)
        d1 = sub(d1, scale(lg, rank * n))
        curvature = add(curvature, scale(mul(lg, lg), rank * n))
    check(Q(d1[1], GRID) + cap * Q(curvature[1], GRID) < 0, "strict input lift throughout the cap interval")
    for k in (claim, tested):
        check(sub(moment(positive, 1 - k), moment(negative, 1 - k))[0] > 0, "positive signed input-lift margin")

    outer = outer_margins(claim, gap, cap)
    check(outer == audit["outer"]["outer_checks"] == published["sharp_outer"]
          and outer["BIT_just_below_effective_rejected"]
          and outer["strict_count"] == 54 and outer["functional_count"] == 4
          and Q(outer["minimum_margin"]) == gap / 10, "all matched outer conditions and below-cap control")
    return {"tested": str(tested), "cap_headroom": str(cap - tested), "H": H,
            "min_log_power": p - 1, "written_log_power": p, "common_depth_guards": guards,
            "moments": [report_interval(interval) for interval in (alpha, gamma, delta)], **outer}


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--replay", type=Path, default=HERE / "replayed")
    replay = cli.parse_args().replay
    source, dependencies = source_pins()
    published = read(SOURCE / "RESULT.json")
    bit = read(replay / "BIT.json")
    audit = read(replay / "AUDIT.json")
    app = read(replay / "APPLICATION.json")
    check(digest(replay / "BIT.json") == source["BIT.json"]["sha256"], "byte-exact BIT receipt")
    check(audit == read(SOURCE / "AUDIT.json"), "exact semantic audit receipt")
    check((SOURCE / "AUDIT.json").read_bytes().replace(b"\r\n", b"\n") == (replay / "AUDIT.json").read_bytes(),
          "audit byte difference is CRLF only")
    check(read(replay / "RESULT.json") == published, "same literal result fields")
    check(app["premises"] == audit["premises"] == published["premises"] == PREMISES, "inherited framework premises")
    pred = CACHE / "7786/research/p104-iterated-returns"
    chain = CACHE / "7830/research/p104-chart306-chain"
    retained = CACHE / "cache/source"
    old_bit = read(pred / "binary/INDEPENDENT.json")
    old_app = read(chain / "DOUBLE-APPLICATION.json")
    old_finite_path = pred / "binary/FINITE.json"
    check(digest(old_finite_path) == "0cebc543d64ca53ac6c7141dfab40c658bf451fe89bb7744befb76c116ea45e6",
          "frozen predecessor finite bridge")
    old_finite = read(old_finite_path)
    bit_caller = retained / "research/paired-query-only-bit/EFREE-CALLER.json.gz"
    binary_paid, binary_targets, binary = native_binary(pred / "binary/WORD.json.gz", bit_caller)
    check(binary_paid == histogram(old_bit["complete_paid"]) == histogram(bit["native"]["paid"])
          and binary_targets == histogram(old_bit["complete_productive"]) == histogram(bit["native"]["targets"]),
          "complete 36-call invoices unchanged")
    check(old_bit["word_sha256"] == binary["word"] == published["binary_word"]
          and bit["native"]["caller_sha256"] == binary["caller"], "binary word and caller anchors")
    check(bit["native"]["ordinary"] == old_bit["ordinary"]
          and binary["raw_records"] == old_bit["ordinary"]["ordinary_records"]
          and binary["owned_fields"] == old_bit["ordinary"]["owned_backing"], "complete binary ordinary account unchanged")
    rational_paid, rational_targets, rational = native_rational(app)
    check((rational_paid, rational_targets, rational) == native_rational(old_app), "complete rational invoices unchanged")
    check(all(app[k] == old_app[k] for k in ("word_sha256", "layout_sha256", "caller", "native",
                                             "caller_census", "caller_proof", "common_root", "conversion",
                                             "compiler_controls")), "unchanged complete physical caller, exact word and controls")
    check(app["word_sha256"] == published["rational_word"] == audit["word"]
          and app["layout_sha256"] == audit["layout"], "exact rational word and layout anchors")
    check(app["caller"] == audit["signed"]["caller_sha256"]
          == app["caller_proof"]["readback"]["event_stream_sha256"], "exact rational event-stream anchor")
    check(audit["scalar_plans"]["omitted_extra_clear_control"]["rejected"]
          and audit["actual_grid_fixture"]["exact_outputs_each"] == 1289, "rational replay controls")

    enrolled = Q("0.003889928046155")
    bit_bracket, rational_bracket = published["binary_raw_bracket"], published["rational_raw_bracket"]
    check(bit_bracket == old_bit["raw_crossing"]["bracket"] and rational_bracket == old_app["application"]["bracket"],
          "unchanged predecessor raw crossings")
    directed_bit = directed_invoice(binary_paid, binary_targets, bit_bracket, enrolled)
    directed_rational = directed_invoice(rational_paid, rational_targets, rational_bracket, enrolled)
    check(Q(bit_bracket[1]) < Q(rational_bracket[0]), "binary side limits joint raw crossing")
    check(enrolled - Q(bit_bracket[1]) == Q("0.00001"), "enrolled target unchanged")
    advertised = Q(published["claim"])
    gain = advertised - Q(old_app["application"]["claim"])
    check(gain == Q(published["gain"]) == Q("0.00000002061794"), "directed finite lower-bound gain")
    cap = Q(published["binary_ordinary"])
    seed_path = retained / "certificates/frontier7000/CLAIM.json"
    check(digest(seed_path) == "3f8add8252adb223b60418ec69351a69b6b5edfe601ec1c6b4b65cd9e2afd9b2",
          "frozen stock seed and premise declarations")
    seed = read(seed_path)
    schedule = bit_schedule(bit, binary_paid, binary_targets, seed["admitted_BIT_saving"])
    check(schedule["cover_prime"] == old_finite["cover_prime_condition"], "historical prime condition retained")
    schedule["previous_independent"] = {name: old_bit["finite"][name]
                                        for name in ("product_exponent", "cutoff", "productive_floor", "logarithm_power")}
    outer = rational_outer(app, audit, rational_paid, rational_targets, cap, published)
    check(Q(app["binary_ordinary"]) == cap == Q(audit["outer"]["pinned_binary_cap"]), "matched actual BIT service cap")

    print(json.dumps({"head": HEAD, "author": "Dugongue", "qualified_conditional_lower": published["claim"],
                      "supports_comparator_upgrade": True, "gain": "0.00000002061794",
                      "gap_to_enrolled_target": "0.000010000021095",
                      "enrolled_target": "0.003889928046155", "joint_raw_upper": bit_bracket[1],
                      "confidence": "high for this fixed-head conditional comparison",
                      "goal": "goal-c9b923e487624c27b9078b5182fc7dee", "step": "s11-rebalanced-comparator",
                      "binding_receipt": "progress.goal-c9b923e487624c27b9078b5182fc7dee.00000166",
                      "model": "mixed-target-unnormalized-power-v1", "premises": PREMISES,
                      "premise_statements": seed["assumptions"],
                      "binary": {"repricing": directed_bit, "physical": binary, "schedule": schedule},
                      "rational": {"repricing": directed_rational, "word": app["word_sha256"],
                                   "layout": app["layout_sha256"], "caller": app["caller"],
                                   "native_calls": 48, "ordinary": rational, "outer": outer},
                      "predecessor_heads": {"7830": BASE, "7786": PRED}, "source_blobs": source,
                      "pinned_predecessor_inputs": dependencies,
                      "offline_locked_dependencies_verified": 127,
                      "inherited_source_lock_sha256": digest(pred / "SOURCE-LOCK.json"),
                      "old_binary_finite_sha256": digest(old_finite_path),
                      "archived_audit_uses_crlf": digest(replay / "AUDIT.json") != source["AUDIT.json"]["sha256"],
                      "archive_and_replay_audit_sha256": [source["AUDIT.json"]["sha256"], digest(replay / "AUDIT.json")],
                      "replayed_application_sha256": digest(replay / "APPLICATION.json"),
                      "limits": ["Five framework premises remain assumptions",
                                 "Raw upper is for this fixed signed invoice",
                                 "Neither enrolled paid shortfall receives credit",
                                 "No product word materialization or Lean rebuild"]},
                     indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Rebuild the finite ordinary BIT certificate. Apache-2.0."""
import argparse
from collections import Counter
from fractions import Fraction as Q
import gzip
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
PAIRED = Path("research/paired-query-only-bit")
PACKAGE = Path("research/p104-dual-supplier-lift")
HEAD = "4f7c67ae387cc91580f469aeda4d508b372b9ec1"
BASE = "07f5fe923b50ecc26983054cf8f462b1a2b4a008a5e2c7a472209363abaaa35c"
WORD = "861f5181e4f34db638ab0c573c319fe26ff034d63b21242d67220a4a5d6433ff"
WORD_BYTES = "e5871a4cf87d62aa90e6660d351636aa5ca47f50239916a0943cd433c7f3d323"
DONOR_PINS = {
    "BIT-RESULT.json": "907858ba4c6f4c110662c8ea9faa1209acca07a9ae281ba29e9291a41fe8e6e1",
    "BIT-PROOF.md": "c87bd698ec5d9bb8741d509bc1d2f7d421d9686a95b515829c5c042a0a71f15b",
    "bit_native.py": "4368c62a5d42f81189d6776b8dba8c85a311b6a199b816244b545c6bb7d3dc1e",
    "bit_application.py": "fa76543d0aa0d515b48eaa9516f73df2c34a5f482114080fe3bcd6d37c32bbbd",
}
FINITE = PAIRED / "retained/inputs/credited_trim.py"
IV = PAIRED / "independent/interval_gate.py"
CALLER = PAIRED / "EFREE-CALLER.json.gz"
SELECTED = Path("certificates/frontier7000/CLAIM.json")
INPUT_PINS = {
    FINITE: "fcff17fdd3108be68761fbde0fcbfe218be166cf518c99f7163e60d53ab785d9",
    FINITE.parent / "inputs/exact_arithmetic.py": "0ce7e7137422d5ffeda22085c81fa88471bbe963100fdad62e659f1e3bf89326",
    IV: "8dc2bc4c64cba3f83c664373984a075f1a14b4d53958084091345c8cab189dec",
    CALLER: "757b3523798f840bdb02028b23708c3416627a99ea09e7a3c4bcdc5cd0c7ce4b",
    SELECTED: "3f8add8252adb223b60418ec69351a69b6b5edfe601ec1c6b4b65cd9e2afd9b2",
}
TRIAL = Q("0.00386970000")
STEPS = ("0.00386963090", "0.00386969950")
GAP = Q(1, 10**10)
POWER, CUTOFF, FLOOR, AMBIENT = 768, 15, 16, 134
OFFSET = Q(1, 5)


def need(condition, message):
    if not condition:
        raise ValueError(message)


def pinned(path, digest):
    contents = path.read_bytes()
    need(sha256(contents).hexdigest() == digest, f"pinned bytes for {path.name}")
    return contents


def load(path, name):
    spec = spec_from_file_location(name, path)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def counts(histogram):
    return Counter({int(r): n for r, n in histogram.items()})


def invoice(native, word, old, caller):
    need(old["native"]["program_sha256"] == BASE, "published #7776 binary word")
    events = Counter(e[0] for e in caller["events"])
    calls, ports, roles = events["LOCAL"], caller["ports"], caller["roles"]
    need((calls, ports, roles, native["signed_positions"]["ambient"]) == (36, 111, 38, AMBIENT),
         "complete paired caller")
    targets, paid = counts(native["targets"]), counts(native["paid"])
    original_t, original_p = counts(old["targets"]), counts(old["paid"])

    def signed_change(profile, merge, daughters, quantity):
        profile[merge] -= calls * quantity
        for r in daughters:
            profile[r] += calls * quantity

    signed_change(original_t, 8, (4, 4), 13)
    signed_change(original_t, 8, (1, 7), 8)
    for ranks, quantity in [((2, 2), 9), ((2, 4), 2), ((3, 4), 2), ((1, 6), 8)]:
        signed_change(original_p, sum(ranks), ranks, quantity)
    need(targets == original_t and paid == original_p, "complete #7776 invoice plus twenty-one births")
    need((sum(targets.values()), sum(paid.values())) == (20418, 107532), "target and paid position totals")
    need(sum(r*n for r, n in targets.items()) - sum(r*n for r, n in paid.items()) == 1506,
         "complete rank surplus")
    need((word["public"], word["owned_fields"]) == (672, 3548), "literal native boundaries")
    operations = Counter(e[0] for e in word["program"])
    need(operations == {"INIT": 3548, "ADD": 32486, "MOVE": 2876, "SWAP": 672, "CLEAR": 3548},
         "complete native opcode inventory")
    banks = word["public"] + word["owned_fields"] + 4
    native_transits = 16*banks*len(word["program"])
    caller_transits = 8*ports*(events["ADD"]+3*events["SWAP"]) + 256*ports*(calls+events["QUERY"]+roles)
    routes = 4*(sum(targets.values())+sum(paid.values())) + 8*ports*(calls+events["IDLE_ONE"])
    route_records = routes*8*(10*AMBIENT**2+10*AMBIENT)
    owned = calls*(word["owned_fields"]+4) + 2*ports*roles*len(caller["events"]) + 16*ports*(calls+events["QUERY"]+roles)
    ordinary = dict(native_banks_and_scratch=banks, native_bank_transits_per_call=native_transits,
                    caller_bank_transits=caller_transits, route_groups=routes, route_records=route_records,
                    ordinary_records=calls*native_transits+caller_transits+route_records, owned_backing=owned,
                    raw_ordinary_allowance=10**12, raw_owned_allowance=10**7)
    need(ordinary["ordinary_records"] < 10**12 and owned < 10**7, "complete ordinary and owned allowances")
    need(ordinary == native["ordinary"], "ordinary replay matches separate resource recount")
    return dict(targets), dict(paid), ordinary


def qualify(upstream, targets, paid, previous):
    iv = load(upstream / IV, "births_directed_intervals")
    compiler = load(upstream / FINITE, "births_finite_compiler")

    def margin(k):
        return iv.sub(iv.moment(targets, k), iv.moment(paid, k))

    scale = 10**15
    left, right = 3_870_020_000_000, 3_870_050_000_000
    need(margin(Q(left, scale))[0] > 0 > margin(Q(right, scale))[1], "outer crossing bracket")
    while right-left > 1:
        middle = (left+right)//2
        lower, upper = margin(Q(middle, scale))
        if lower > 0:
            left = middle
        else:
            need(upper < 0, "directed interior crossing sign")
            right = middle
    lo, hi = Q(left, scale), Q(right, scale)
    endpoints = [f"{k//scale}.{k%scale:015d}" for k in (left, right)]
    raw = margin(TRIAL)
    need(raw[0] > 0 and TRIAL < lo, "strict finite binary trial")
    need(margin(lo)[0] > 0 > margin(hi)[1], "complete binary crossing signs")
    derivative = (0, 0)
    for rank in targets.keys() | paid.keys():
        count = targets.get(rank, 0) - paid.get(rank, 0)
        bound = iv.mul(iv.power(rank, hi if count >= 0 else Q(0)), iv.log(rank))
        derivative = iv.add(derivative, iv.smul(bound, -count))
    need(derivative[1] < 0, "unique crossing on the tested interval")

    finite = compiler.certificate(targets, paid, TRIAL, POWER, CUTOFF, FLOOR, OFFSET, OFFSET,
                                  label="twenty-one binary helper births")
    need(finite.pop("ambient") == "127^768", "largest productive rank")
    finite["largest_productive_rank"] = "127^768"
    uniform = compiler.uniform_certificate(TRIAL, POWER, CUTOFF, FLOOR, AMBIENT, GAP)

    def expplus(x):
        return iv.div(iv.exact(1), iv.expminus(x))

    def shifted(histogram, offset):
        result = (0, 0)
        for rank, quantity in histogram.items():
            x = iv.smul(iv.log(rank), abs(offset))
            factor = expplus(x) if offset > 0 else iv.expminus(x)
            result = iv.add(result, iv.smul(iv.mul(iv.power(rank, TRIAL), factor), quantity))
        return result

    tt = iv.moment(targets, TRIAL)
    ratios = (
        iv.div(iv.moment(paid, TRIAL), tt),
        iv.div(shifted(paid, OFFSET), iv.mul(expplus(iv.smul(iv.log(CUTOFF), OFFSET)), tt)),
        iv.div(iv.mul(expplus(iv.smul(iv.log(FLOOR), OFFSET)), shifted(targets, -OFFSET)), tt),
    )
    limits = [Q(bound) for bound in finite["rational_upper_limits"]]
    need(all(0 < l <= u <= b*iv.B < iv.B for (l, u), b in zip(ratios, limits)),
         "independent interval comparison for all three ratios")
    alpha, gamma, loss = limits
    need(1/(1+POWER*(1-alpha))+2*gamma**POWER+loss**POWER < 1,
         "finite paid and surrendered productive moment")
    theta, power, h = Q(uniform["theta"]), uniform["logarithm_power"], uniform["H"]
    base = expplus(iv.smul(iv.log(AMBIENT), TRIAL))
    factor, n = iv.exact(1), POWER
    while n:
        if n & 1:
            factor = iv.mul(factor, base)
        n //= 2
        if n:
            base = iv.mul(base, base)
    eta = iv.div(iv.exact(1-TRIAL), factor)
    need(2*CUTOFF**(POWER*theta.denominator) <= AMBIENT**(POWER*theta.numerator),
         "shifted logarithm inequality")
    need(theta**power < Q(eta[0], iv.B) and Q(factor[1], iv.B) < 2**power,
         "working ambient logarithm inequalities")
    need((h+1)**power < 2**(h//GAP.denominator)
         and (h-GAP.denominator+1)**power >= 2**(h//GAP.denominator-1),
         "exact uniform threshold and preceding point")

    need(previous == Q("0.00385248"), "selected completed ordinary backend")
    covered, rho, steps = TRIAL-2*GAP, Q(1, 250), []
    for admitted in STEPS:
        saving = Q(admitted)
        envelope = (1-rho)*covered + rho*previous
        need(previous < saving < envelope < rho < 1-envelope, "acyclic ordinary bootstrap envelope")
        steps.append(dict(previous=str(previous), admitted=admitted, envelope=str(envelope), slack=str(envelope-saving)))
        previous = saving
    need(previous > Q("0.00386932267588"), "qualified ordinary backend headroom")
    return dict(raw_crossing=endpoints, crossing_margins=[iv.show(margin(lo)), iv.show(margin(hi))],
                derivative_upper_interval=iv.show(derivative), tested_saving="0.00386970000",
                trial_margin=iv.show(raw), finite_separation=finite, working_ambient="134^768",
                independent_ratio_intervals=[iv.show(row) for row in ratios], uniform=uniform,
                uniform_loss=str(GAP), delayed_cover_loss=str(GAP), covered="0.00386969980", rho=str(rho),
                ordinary_bootstrap=steps, ordinary_admitted=STEPS[-1])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--upstream", type=Path, required=True)
    parser.add_argument("--supplier", type=Path, required=True)
    parser.add_argument("--native-report", type=Path, required=True)
    parser.add_argument("--word", type=Path, default=HERE / "WORD.json.gz")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()

    file = args.word.read_bytes()
    raw = gzip.decompress(file) if file.startswith(b"\x1f\x8b") else file
    need(sha256(raw).hexdigest() == WORD_BYTES, "literal binary word bytes")
    word = json.loads(raw)
    canonical = json.dumps(word, sort_keys=True, separators=(",", ":")).encode()
    need(sha256(canonical).hexdigest() == WORD, "canonical binary word")
    native = json.loads(args.native_report.read_bytes())
    need(native["word_sha256"] == WORD and native["word_file_sha256"] == WORD_BYTES,
         "literal replay bound to the word")
    need(native["parent_pr"] == 7776 and native["source_head"] == HEAD and native["source_word_sha256"] == BASE,
         "literal replay bound to published #7776")

    path = args.supplier / PACKAGE
    if not path.is_dir():
        path = args.supplier
    donor = {name: pinned(path / name, digest) for name, digest in DONOR_PINS.items()}
    trusted = {name: pinned(args.upstream / name, digest) for name, digest in INPUT_PINS.items()}
    caller = json.loads(gzip.decompress(trusted[CALLER]))
    targets, paid, ordinary = invoice(native, word, json.loads(donor["BIT-RESULT.json"]), caller)
    previous = Q(json.loads(trusted[SELECTED])["admitted_BIT_saving"])
    finite = qualify(args.upstream, targets, paid, previous)
    report = dict(status="PASS_FINITE_BIT_BIRTHS_COMPILER_AND_ORDINARY_BOOTSTRAP",
                  donor_pr=7776, donor_head=HEAD, donor_word_sha256=BASE, word_sha256=WORD, word_file_sha256=WORD_BYTES,
                  trusted_inputs={str(name): value for name, value in INPUT_PINS.items()}, donor_inputs=DONOR_PINS,
                  targets=targets, paid=paid, ordinary=ordinary, **finite)
    if args.out:
        args.out.write_text(json.dumps(report, indent=2, sort_keys=True)+"\n")
    print(report["status"], report["ordinary_admitted"], *report["raw_crossing"])


if __name__ == "__main__":
    main()

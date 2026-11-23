#!/usr/bin/env python3
"""Replay a source-pinned, ordinary-only eta-lift candidate.

The Gaussian supplier is deliberately left at #8072 and is a negative control.
The script never claims a combined .0039 multiplier result.
"""

from dataclasses import replace
from fractions import Fraction as Q
from hashlib import sha1, sha256
import importlib.util
import json
from pathlib import Path
import runpy
import subprocess
import sys
from tempfile import TemporaryDirectory


HERE = Path(__file__).resolve().parent
ORIGINAL = HERE / "original"
PINS = {
    "verify.py": "10362de3ceaa651cde5b71c6599fd4683d9f1f4d76cc252178e915b43a098fee",
    "prepare.py": "76f9d4c6bfd880ee49f6ba5bde9138cf0856d669edb4d525e48ca71a9094eec3",
    "PEER-SOURCE.json": "798c2e6394c258986484a116198cc542a6d2b4c1f289e5816de2cfecf5141c51",
    "peer8057.tar.gz": "0e0d559bdb15e7b647f88a2b5e27fcdc9e28e81d8f4145459876ba6da2e9314c",
    "check_stage_seam.py": "128a93719bbfc2d69c442283b8cbaecd9a3ca4c2a2399a7964e4c882bf0bace1",
    "check_ordinary_floor.py": "65e3c3ca4cec73a9462973e651a66127ab894d0bc141c072e26416aedb48b543",
    "LICENSE": "c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4",
    "NOTICE.md": "4bb4aa63290a19282826ff57529293f8bfd12e3a2afe28bc6d48205c0cc976fc",
    "PROOF.md": "b667b8470f94015181ef577d6576859bebd76e7618ffb32c1197233f1e8212da",
    "README.md": "1347061750a0edb42a850206419afb39633c4b8c6a63f635362b9f7e4b93adb6",
    "source-pins.json": "09eb1c710a6382226b43dace5c73761ec4b84681e87e061e7aab813dfd1276cd",
}
HEAD_BLOBS = {
    "verify.py": "f460dbac14b3ef18f780105459e30883c95da461",
    "prepare.py": "048698f08d803810b5a6ffd8c2d6e2341100a45e",
    "PEER-SOURCE.json": "6f84b3aef4b8c5026e348d88700bc9401514ccab",
    "peer8057.tar.gz": "3a3ded828f6bbf9b6e6a76ba255d480452f4d269",
    "check_stage_seam.py": "cba442cfb92b02d63cee77f038bf69c8144f7702",
    "check_ordinary_floor.py": "80994309fb433928293d79f8b7dabf558b1b9a41",
    "LICENSE": "261eeb9e9f8b2b4b0d119366dda99c6fd7d35c64",
    "NOTICE.md": "cac7f9814f2e5fa1e5fb307e2de89f739348daef",
    "PROOF.md": "bf97b6e37fba359fe7205b658b984b1f5579d307",
    "README.md": "db7a838448c5159656e99da51984819c65f11b4d",
}
RUNTIME_PINS = {
    "installations.py": "c1bba07dfcf95f7a494e59d6e4de85b4d4537c144f0bcf6f7a1a02ecbe832dea",
    "ordinary_carrier.py": "aa1a64d48daf22f3918922481899a460dfe8e70268388e41f133279bc78f141d",
    "raw_binary_stage.py": "e24bd735598d278dbd46cada584a63da01796d77ad557a45b80a4dfc7bbbd0b0",
    "strong-bit.json.gz": "9e7392c52bcf29c0cc58c54c619f95c28f476394c33e8e0a5aa30c9557d31362",
    "transport.py": "9eb8f0d77a4c53fc4fddffdfe198cab930b6d1f49e2b6d43c970397051bb7818",
    "grades.py": "6124744b40f806c80b6f10010a72e755bc11d64a8cc9a04f5e8316799eb6f05d",
    "retimed_supplier.py": "2a87c2781ca93fa854aee098dcb7c50a65f2a46267ba926e3997b442e5a25f2c",
}
ETA = Q(1, 256)
RHO = Q(1, 250)
TARGET = Q("0.0039")
GAP = Q(1, 10**18)
Q_ORDINARY = TARGET + 5 * GAP
H = (8192, 106000, 1681001)
GAUSSIAN_H = 490950
DEBIT = Q(11239, 8192)
POSITIVE_DEBIT = Q(64939, 524288)
GRID = 10**21


def ceil(q):
    return -(-q.numerator // q.denominator)


def source_runtime(tree):
    for name, expected in PINS.items():
        assert sha256((ORIGINAL / name).read_bytes()).hexdigest() == expected, name
    pins = json.loads((ORIGINAL / "source-pins.json").read_bytes())
    assert pins["repository"] == "CrocSwap/integer-mult-bounds" and pins["pull_request"] == 8072
    assert pins["head"] == "75f7e1c44f48c43983016bcf8878c4d9e5e87c62"
    assert pins["base"] == "e54523517d0f03e58352e647c403a5af3e525a57"
    listed = pins["files"]
    prefix = "research/p104-weighted-capped-allocation-490950/"
    for name, expected in HEAD_BLOBS.items():
        data = (ORIGINAL / name).read_bytes()
        blob = sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
        assert blob == expected == listed[prefix + name], name
    peer = runpy.run_path(str(ORIGINAL / "verify.py"))["restore"](tree)
    runpy.run_path(str(ORIGINAL / "prepare.py"))["materialize"](peer)
    runtime = tree / "runtime"
    subprocess.run([sys.executable, "-IB", str(peer / "bootstrap.py"), str(runtime)], check=True)
    for name, expected in RUNTIME_PINS.items():
        assert sha256((runtime / name).read_bytes()).hexdigest() == expected, name
    return peer, runtime


class DyadicWidth(int):
    """The replacement is exact for the chosen power-of-two test widths."""

    def __pow__(self, exponent):
        assert self.bit_count() == 1 and exponent >= 0
        return 1 << ((self.bit_length() - 1) * exponent)


def dispatch_fixture(profile, cuts, stage, log_width):
    """Check real dispatch/layout code with exact dyadic root and a captured backend."""
    import ordinary_carrier as carrier

    assert stage in (2, 3) and log_width % 32000 == 0
    assert log_width >= cuts[stage - 1]
    number = DyadicWidth(1 << log_width)
    predecessor = 1 << cuts[stage - 2]
    width = max(predecessor + 1, 1 << (log_width // 250))
    component = 1 << (log_width // 256)
    count = -(-width // component)
    short, longer = divmod(width, count)
    expected_layout = (longer, short + 1, count - longer, short)
    expected_rank = 1 << profile.rank_logs[stage - 1]
    expected_direct = -(-number // width) <= 1 << (8 * profile.rank_logs[stage - 1])
    calls = []

    def exact_root(value, degree):
        assert value.bit_count() == 1
        exponent, remainder = divmod(value.bit_length() - 1, degree)
        assert not remainder
        return 1 << exponent

    def capture_receiver(dimension, layout, previous, *, direct, profile):
        assert dimension == expected_rank and layout == expected_layout
        assert direct == expected_direct and previous.func is carrier.ternary
        assert previous.keywords == {"maximum": stage - 1, "profile": profile}
        return stage

    def capture_body(source, target, digits, prefix, gap, suffix, backend):
        assert digits == number and (prefix, gap, suffix) == (1, 3, 5)
        assert backend == stage
        calls.append(1)

    saved = carrier.ceil_root, carrier.Receiver, carrier.root_body
    try:
        carrier.ceil_root, carrier.Receiver, carrier.root_body = (
            exact_root, capture_receiver, capture_body
        )
        carrier.ternary(None, None, number, 1, 3, 5, maximum=stage, profile=profile)
    finally:
        carrier.ceil_root, carrier.Receiver, carrier.root_body = saved
    assert calls == [1]
    return {"stage": stage, "width_log": log_width,
            "component_log": log_width // 256, "direct": expected_direct}


def run():
    if not __debug__:
        raise ValueError("Run this witness with assertions enabled")
    with TemporaryDirectory(prefix="eta-lift-8072-") as tmp:
        peer, runtime = source_runtime(Path(tmp))
        sys.path.insert(0, str(runtime))
        sys.path.insert(0, str(peer.parent / "tiered-native-multiplier" / "source"))
        sys.path.insert(0, str(peer.parent / "tiered-native-multiplier"))
        sys.argv = [str(HERE / "witness.py"), str(runtime)]
        spec = importlib.util.spec_from_file_location("original_receipt", peer / "receipt.py")
        receipt = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(receipt)
        from activation import resource_receipt
        from installations import BINARY_C, GAUSSIAN_C, ENTRY, TERMINAL
        from module_atoms import ceil_root
        from ordinary_carrier import stage_for_width_log
        from ordinary_clock import first_stage_bound
        from outer_budget import margins, qualify
        from staged_carriers import entrance_logs
        from band_product import prepare_native
        from raw_binary_stage import binary_word
        from strict_moment import UNIT
        from unpowered_price import intervals

        # These inequalities hold throughout the entire open interval stated
        # in the proof; the receipt uses ETA=1/256 as the concrete value.
        assert Q(1, 258) < Q(97, 25000) < TARGET < Q_ORDINARY < ETA < RHO
        assert 2 * Q_ORDINARY > RHO and Q_ORDINARY + RHO < 1
        assert Q(8192, 258) - 1 > 30
        assert 2660000 * 32 < 2**30
        assert first_stage_bound(ETA) == first_stage_bound(TERMINAL.eta)

        profile = replace(TERMINAL, rank_logs=H, complex_log=GAUSSIAN_H,
                          eta=ETA, kappa=TARGET)
        previous, rates = Q(0), []
        for i, height in enumerate(H):
            unclamped = (249 * (BINARY_C - DEBIT / height) + previous) / 250
            upper = min(ETA, unclamped)
            selected = (Q_ORDINARY if i == len(H) - 1
                        else Q((upper * GRID).__floor__() - 1, GRID))
            assert previous < selected < upper
            if i < len(H) - 1:
                assert unclamped < Q_ORDINARY  # no clamp for any eta > q
            rates.append({"height": height, "upper": str(upper),
                          "booked": str(selected), "slack": str(upper-selected)})
            previous = selected
        last_slack = Q(rates[-1]["slack"])
        assert last_slack == Q(18375833487309615126701,
                               1804961079885824000000000000000000000)
        b2 = Q(rates[1]["booked"])
        prev_height_upper = (249 * (BINARY_C - DEBIT / (H[-1] - 1)) + b2) / 250
        assert prev_height_upper < Q_ORDINARY
        old_height_upper = (249 * (BINARY_C - DEBIT / 524288) + b2) / 250
        assert old_height_upper < Q_ORDINARY
        assert min(TERMINAL.eta, (249 * (BINARY_C-DEBIT/H[-1])+b2)/250) < Q_ORDINARY
        threshold = DEBIT / (BINARY_C - (250 * Q_ORDINARY - b2) / 249)
        assert threshold.__floor__() + 1 == H[-1]
        assert min(Q_ORDINARY, (249 * (BINARY_C-DEBIT/H[-1])+b2)/250) == Q_ORDINARY
        assert not (RHO < RHO)  # strict endpoint in the source admission gate

        cuts = tuple(entrance_logs(H))
        assert cuts == (8290, 114354, 1795419)
        for i, cut in enumerate(cuts, 1):
            assert [stage_for_width_log(cut+d, len(H), H) for d in (-1, 0, 1)] == [i-1, i, i]
            assert stage_for_width_log(cut, i-1, H) == i-1
        qcuts = []
        for height in H:
            bound = ceil(Q(2*height+64) / (1-ETA))
            uniform = ceil(Q(250*(2*height+64), 249))
            assert (1-ETA)*bound >= 2*height+64 and bound <= uniform < 3*height < 8*height
            qcuts.append({"height": height, "eta_cut": bound, "uniform_cut": uniform})
        stock = resource_receipt(profile)
        assert stock["binary_cuts"] == list(cuts)
        assert stock["public_exponent_A"] == 2286624
        assert stock["retimed_first_stripe_margin"] == 1141254
        assert stock["retimed_all_size_margin_floor"] == 1105612
        for n in ((1 << 256) + 1, (1 << 257) - 1, (1 << 512) + 123):
            root = ceil_root(n, 256)
            assert (root-1)**256 < n <= root**256

        seams = [dispatch_fixture(profile, cuts, 2, 128000),
                 dispatch_fixture(profile, cuts, 3, 1824000),
                 dispatch_fixture(profile, cuts, 2, 1120000),
                 dispatch_fixture(profile, cuts, 3, 13568000)]
        assert [x["direct"] for x in seams] == [True, True, False, False]

        # These finite owner-return fixtures use the source's physical tape
        # implementation. They do not materialize the astronomical native field.
        original_seam = runpy.run_path(str(ORIGINAL / "check_stage_seam.py"))
        tapes = [original_seam["verify_tape"](1, [0, 1], [2, 1]),
                 original_seam["verify_tape"](2, [1, 7], [3, 1])]
        recipes = prepare_native(profile)
        word = binary_word()
        assert tuple(x.rank_log for x in recipes) == (*H, GAUSSIAN_H)
        assert all(r.level_floor == 18960 and r.trial == BINARY_C for r in recipes[:-1])
        assert all(r.targets is word.targets and r.paid is word.paid and r.cells is word.cells
                   for r in recipes[:-1])
        assert (len(word.targets), len(word.paid), len(word.cells)) == (18906, 104652, 24)
        floor_test = runpy.run_path(str(ORIGINAL / "check_ordinary_floor.py"))["all_size_stock"](
            word, BINARY_C, intervals, UNIT)

        gaussian = GAUSSIAN_C - POSITIVE_DEBIT / GAUSSIAN_H
        strict, functional, positive_margin = margins(TARGET, GAP, Q_ORDINARY, gaussian)
        assert len(strict) == 54 and len(functional) == 4 and min(strict + functional) > 0
        assert GAUSSIAN_C < Q_ORDINARY and positive_margin < 0
        try:
            qualify(TARGET, GAP, Q_ORDINARY, gaussian)
        except ArithmeticError:
            rejected = True
        else:
            raise AssertionError("The unchanged Gaussian incorrectly funded the target")

        # The actual complete-price routine is run at the old, Gaussian-funded
        # kappa. Independently, the same outer gate accepts the stronger q there.
        actual = replace(profile, kappa=TERMINAL.kappa)
        early, late = receipt.bank(ENTRY), receipt.bank(actual)
        strengthened_signed = qualify(TERMINAL.kappa, GAP, Q_ORDINARY, gaussian)
        premium = ceil((TERMINAL.kappa - ENTRY.kappa) * stock["public_exponent_A"])
        complete = 1 + max(early["log2_C"] + premium, late["log2_C"])
        assert (premium, late["log2_B"], late["log2_C"], complete) == (
            1025, 574461888, 682472490, 682472491)
        assert 92 * max(H) < 2**38 and stock["absolute_log2_private_control_envelope"] < 2**38
        assert max(H).bit_length() == 21
        setup = receipt.native_clock()
        assert setup["all_setup"] < 2**228

        result = {
            "source_head": "75f7e1c44f48c43983016bcf8878c4d9e5e87c62",
            "source_head_note": "Local bytes match captured #8072 changed-file blob pins; this check alone does not authenticate the Git history of the stated head.",
            "status": "ORDINARY_COMPONENT_PASS_COMBINED_TARGET_REJECTED",
            "eta": str(ETA), "admission_interval": [str(Q_ORDINARY), str(RHO)],
            "admission_interval_endpoints": "open", "rho": str(RHO),
            "target_kappa": str(TARGET), "ordinary_target": str(Q_ORDINARY),
            "ordinary_raw": str(BINARY_C), "ordinary_debit": str(DEBIT),
            "stage_rates": rates, "height_minus_one_fails": True,
            "height_minus_one_slack": str(prev_height_upper-Q_ORDINARY),
            "original_height_cap_slack": str(old_height_upper-Q_ORDINARY),
            "original_eta_rejects_target": True,
            "gaussian_raw": str(GAUSSIAN_C), "gaussian_priced": str(gaussian),
            "target_gaussian_margin": str(positive_margin),
            "target_signed_strict_passes": len(strict),
            "target_signed_functional_passes": len(functional),
            "target_combined_rejected": rejected,
            "cuts": list(cuts), "quotient_entry_guards": qcuts, "stock": stock,
            "stage_dispatch_fixtures": seams, "finite_signed_tape_fixtures": tapes,
            "ordinary_floor_all_size_stock": floor_test,
            "old_kappa": str(TERMINAL.kappa), "old_kappa_signed_with_stronger_q": strengthened_signed,
            "entry_conversion_bits": premium, "terminal_log2_B": late["log2_B"],
            "terminal_log2_C": late["log2_C"], "combined_log2_C_at_old_kappa": complete,
            "old_kappa_price_caveat": "Directed arithmetic and inherited clock premises; fresh full installation and physical replay not claimed.",
            "fixed_setup_caveat": "This receipt checks the original serial arithmetic bound and datum sizes only; see SETUP-PROOF.md for a separate conditional action extension and finite constructor census.",
            "max_height": max(H), "max_height_bit_length": max(H).bit_length(),
            "original_fixed_setup_bound": setup["setup_exponent"],
        }
        print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    run()

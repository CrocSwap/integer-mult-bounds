#!/usr/bin/env python3
"""Check the #8084 ordinary lift on the pinned, patched #8088 runtime.

Usage: python3.12 -I -B check_ordinary.py RUNTIME FREQUENCY_PACKAGE

This checks the literal stage parser with captured receiver/body seams, exact
directed prices and the source's outer admission and clock routine. It does not
run the astronomical physical product, prove inherited premises, or accept a
combined kappa result. The caller must reconstruct the two source directories
from the stated pinned predecessor; the checked runtime/source SHA-256 values
below fail closed on altered relevant files.
"""

from collections import Counter
from dataclasses import replace
from fractions import Fraction as Q
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory


RUNTIME_PINS = {
    "installations.py": "5df81fddba26013b142195f5c3119491fa2f07b1e72c3616ae76e7d7ffbb0fd1",
    "ordinary_carrier.py": "aa1a64d48daf22f3918922481899a460dfe8e70268388e41f133279bc78f141d",
    "raw_binary_stage.py": "e24bd735598d278dbd46cada584a63da01796d77ad557a45b80a4dfc7bbbd0b0",
    "binary_receiver.py": "a7cc759e9a88e60dbcd59ca314ae5b9d39a33b5c642b56e680bbab775b0f06c5",
    "transport.py": "9eb8f0d77a4c53fc4fddffdfe198cab930b6d1f49e2b6d43c970397051bb7818",
    "grades.py": "6124744b40f806c80b6f10010a72e755bc11d64a8cc9a04f5e8316799eb6f05d",
    "retimed_supplier.py": "2a87c2781ca93fa854aee098dcb7c50a65f2a46267ba926e3997b442e5a25f2c",
    "strong_complex.py": "8f3fb92523df006e2e94505127088aaf2e64fadd20b3cab2344f62d7690e875d",
    "strong-bit.json.gz": "9e7392c52bcf29c0cc58c54c619f95c28f476394c33e8e0a5aa30c9557d31362",
    "w5669_shortcut5.json.gz": "6ef741c346ea075c4f2ed11f9d42d7076103e72d4a9e5059d495f1cb990fd149",
    "inputs/triangular/staged_carriers.py": "6c925ae4b39dc9999ac5891d1a27dcbb38e129a36e1473b2b418f27a806b6fc4",
}
PEER_PINS = {
    "receipt.py": "504ece3196cf8d574d368c72918b9e4b4ce6837bd7241a6a4725b7a6ddbe7275",
    "independent_price.py": "fcd4254414d601a96b91822ff3c6b615de9caa1a9bb35ba1f5adff37745647ea",
}
TIERED_PINS = {
    "source/activation.py": "6e7f89d40a4d10ecd40a50e5b96334dfc64db90841ece7e3ef12eeca5ee5093b",
    "source/outer_budget.py": "ca4438db28a447ed5c43d87d43f0ac10a0cb2b4e183342ac93139d517b9d4d02",
    "source/ordinary_clock.py": "91dcf0ef72dddbde998b80f3d8b30c8036de9ce97e06e2bbd9c4159bf292020d",
}
K = Q(39, 10000)
GAP = Q(1, 10**18)
ORDINARY = K + 5 * GAP
ETA = Q(1, 256)
HEIGHTS = (8192, 106000, 1681001)
GAUSSIAN_H = 85406
OLD_DEBIT = Q(11239, 8192)
PARENT_DEBIT = Q(1420718, 2**20)
GAUSSIAN_DEBIT = Q(1039776, 2**23)


def pins(root, expected):
    for name, digest in expected.items():
        if sha256((root / name).read_bytes()).hexdigest() != digest:
            raise ValueError(f"Source image differs at {name}")


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class DyadicWidth(int):
    def __pow__(self, exponent):
        assert self.bit_count() == 1 and exponent >= 0
        return 1 << ((self.bit_length() - 1) * exponent)


def dispatch_fixture(profile, cuts, stage, log_width):
    """Execute real selection/layout with exact dyadic roots and captured sinks."""
    import ordinary_carrier as carrier

    assert stage in (2, 3) and log_width % 32000 == 0
    number = DyadicWidth(1 << log_width)
    previous = 1 << cuts[stage - 2]
    width = max(previous + 1, 1 << (log_width // 250))
    component = 1 << (log_width // 256)
    count = -(-width // component)
    short, longer = divmod(width, count)
    layout = (longer, short + 1, count - longer, short)
    rank = 1 << profile.rank_logs[stage - 1]
    direct = -(-number // width) <= 1 << (8 * profile.rank_logs[stage - 1])
    calls = []

    def root(value, degree):
        assert value.bit_count() == 1
        exponent, remainder = divmod(value.bit_length() - 1, degree)
        assert remainder == 0
        return 1 << exponent

    def receiver(dimension, actual_layout, prior, *, direct, profile):
        assert dimension == rank and actual_layout == layout
        assert direct == expected_direct and prior.func is carrier.ternary
        assert prior.keywords == {"maximum": stage - 1, "profile": profile}
        return stage

    def body(source, target, digits, prefix, gap, suffix, backend):
        assert digits == number and (prefix, gap, suffix, backend) == (1, 3, 5, stage)
        calls.append(stage)

    expected_direct = direct
    saved = carrier.ceil_root, carrier.Receiver, carrier.root_body
    try:
        carrier.ceil_root, carrier.Receiver, carrier.root_body = root, receiver, body
        carrier.ternary(None, None, number, 1, 3, 5, maximum=stage, profile=profile)
    finally:
        carrier.ceil_root, carrier.Receiver, carrier.root_body = saved
    assert calls == [stage]
    return {"stage": stage, "scanned_log": log_width,
            "component_log": log_width // 256, "direct": direct}


def rejected(label, function):
    try:
        function()
    except (AssertionError, ArithmeticError, ValueError):
        return label
    raise AssertionError(f"Control {label} was accepted")


def setup_parameter_guard(profile):
    """Check only #8084's numeric setup premises, not its fixed-word census."""
    heights = (*profile.rank_logs, profile.complex_log)
    scalars = (profile.kappa.numerator, profile.kappa.denominator,
               profile.eta.numerator, profile.eta.denominator,
               profile.positive_stop_denominator)
    if not all(isinstance(h, int) and 1024 <= h < 2**25 for h in heights):
        raise ValueError("A setup height is outside the 25-bit interval")
    if not all(isinstance(x, int) and abs(x).bit_length() <= 128 for x in scalars):
        raise ValueError("A setup scalar encoding exceeds 128 bits")
    if profile.positive_stop_denominator <= 0:
        raise ValueError("The stop denominator must be positive")
    return max(abs(x).bit_length() for x in scalars)


def main(runtime, peer):
    if not __debug__:
        raise ValueError("Run with assertions enabled")
    tiered = peer.parent / "tiered-native-multiplier"
    pins(runtime, RUNTIME_PINS)
    pins(peer, PEER_PINS)
    pins(tiered, TIERED_PINS)
    # -B does not prevent cache reads. Use a private, empty cache namespace for
    # imports from the runtime and its authenticated nested source bundles.
    with TemporaryDirectory(prefix="ordinary-check-cache-") as cache:
        sys.pycache_prefix = cache
        sys.dont_write_bytecode = True
        sys.path[:0] = [str(runtime), str(tiered / "source"), str(tiered)]
        from upstream import install
        install()
        from activation import resource_receipt
        from installations import BINARY_C, GAUSSIAN_C, ENTRY, TERMINAL, activation
        from module_atoms import ceil_root
        from ordinary_clock import first_stage_bound
        from ordinary_carrier import stage_for_width_log
        from outer_budget import qualify
        from raw_binary_stage import binary_recipe, binary_word
        from staged_carriers import entrance_logs
        import transport

        assert TERMINAL.rank_logs == HEIGHTS and TERMINAL.complex_log == GAUSSIAN_H
        assert TERMINAL.kappa == K and TERMINAL.eta == ETA
        assert TERMINAL.ordinary == ORDINARY and K < ORDINARY < ETA < Q(1, 250)
        assert BINARY_C == Q(4391986206293, 2**50)
        assert GAUSSIAN_C == Q(17158764376, 2**42)
        assert first_stage_bound(ETA) == first_stage_bound(ENTRY.eta)
        assert len(ENTRY.rank_logs) == 2 and len(TERMINAL.rank_logs) == 3
        scalar_bits = max(setup_parameter_guard(ENTRY), setup_parameter_guard(TERMINAL))

        # The 8088 word's positive trial and debit fund q only from G=85406.
        def positive_at(height):
            return GAUSSIAN_C - GAUSSIAN_DEBIT / height

        assert positive_at(GAUSSIAN_H - 1) < ORDINARY < positive_at(GAUSSIAN_H)
        assert positive_at(66037) < ORDINARY
        signed = qualify(K, GAP, ORDINARY, positive_at(GAUSSIAN_H))
        assert signed["strict"] == 54 and signed["functional"] == 4

        # The exact parent bank parser is reused, but its old 4474-floor debit
        # is temporarily replaced by the separately certified 18960-floor
        # debit. The parent receipt's hardcoded main/check is not called.
        saved_argv = sys.argv
        sys.argv = [str(peer / "receipt.py"), str(runtime)]
        try:
            receipt = load_module("ordinary_parent_receipt", peer / "receipt.py")
            price = load_module("ordinary_directed_price", peer / "independent_price.py")
        finally:
            sys.argv = saved_argv
        assert receipt.ORDINARY_DEBIT == PARENT_DEBIT
        assert receipt.DEBIT == GAUSSIAN_DEBIT
        old = receipt.ORDINARY_DEBIT
        receipt.ORDINARY_DEBIT = OLD_DEBIT
        try:
            early = receipt.bank(ENTRY)
            terminal = receipt.bank(TERMINAL)
            controls = [
                rejected("eta-equals-public-kappa", lambda: receipt.bank(replace(TERMINAL, eta=K))),
                rejected("eta-equals-ordinary-booking", lambda: receipt.bank(replace(TERMINAL, eta=ORDINARY))),
                rejected("eta-equals-rho", lambda: receipt.bank(replace(TERMINAL, eta=Q(1, 250)))),
                rejected("last-ordinary-height-minus-one", lambda: receipt.bank(replace(TERMINAL, rank_logs=(*HEIGHTS[:-1], HEIGHTS[-1] - 1)))),
                rejected("gaussian-height-minus-one", lambda: receipt.bank(replace(TERMINAL, complex_log=GAUSSIAN_H - 1))),
                rejected("setup-height-2^25", lambda: setup_parameter_guard(replace(TERMINAL, complex_log=2**25))),
                rejected("setup-scalar-over-128-bits", lambda: setup_parameter_guard(replace(TERMINAL, positive_stop_denominator=2**128))),
            ]
        finally:
            receipt.ORDINARY_DEBIT = old

        previous, stages = Q(0), []
        for i, height in enumerate(HEIGHTS):
            raw = (249 * (BINARY_C - OLD_DEBIT / height) + previous) / 250
            upper = min(ETA, raw)
            selected = ORDINARY if i == len(HEIGHTS) - 1 else Q((upper * 10**21).__floor__() - 1, 10**21)
            assert previous < selected < upper
            stages.append({"height": height, "raw_upper": str(raw), "upper": str(upper),
                           "booked": str(selected), "margin": str(upper - selected)})
            previous = selected
        assert terminal["ordinary_rates"] == [x["booked"] for x in stages]
        assert min(K, Q(stages[-1]["raw_upper"])) < ORDINARY

        # Bound the *chosen conservative expression*, including 256/255 and
        # the 47/20 child tariff, on a directed 192-bit grid. The last control
        # does not claim the actual physical factor is lower-bounded by it.
        delta = Q(1, 2**128)
        factor = (Q(47, 20) * Q(256, 255) * Q(4097, 4096) * Q(1028, 1024)
                  * (1 + Q(64, 18960) + delta) / ((1 - Q(10, 18960)) * (1 - delta)**3))
        low, high = price.powers(1024 * 134 * 18960, BINARY_C)
        factor_lo, factor_hi = factor * low, factor * high
        old_allow = 2 * price.powers(2, OLD_DEBIT - 1)[0]
        parent_allow = 2 * price.powers(2, PARENT_DEBIT - 1)[1]
        assert factor_hi < old_allow and factor_lo > parent_allow
        assert Q(75, 32) / Q(47, 20) == Q(375, 376)

        word = binary_word()
        assert (len(word.targets), len(word.paid), len(word.cells)) == (18906, 104652, 24)
        recipes = tuple(binary_recipe(h) for h in HEIGHTS)
        assert all(r.level_floor == 18960 and r.trial == BINARY_C
                   and r.targets is word.targets and r.paid is word.paid and r.cells is word.cells
                   for r in recipes)

        # Run the literal opening seam at the small candidate stage with the
        # eventual Plan captured; the two large calendars remain unopened.
        recipe = recipes[0]
        n = 1 << HEIGHTS[0]
        def capture(n0, targets, paid, cells, t, lower, upper, volume, ticks, rounds, **flags):
            assert n0 == n and lower == 18960 and t == 1 - BINARY_C
            assert targets is word.targets and paid is word.paid and cells is word.cells
            assert upper == 2 * (n // (2048 * recipe.ambient))
            assert (volume, ticks, rounds) == (n**6, n**82, n**2)
            assert flags == {"width": 1 << (92 * HEIGHTS[0]), "delay_base": 1 << 19}
            return True
        saved_plan = transport.Plan
        try:
            transport.Plan = capture
            assert recipe.open()
        finally:
            transport.Plan = saved_plan

        cuts = tuple(entrance_logs(HEIGHTS))
        assert cuts == (8290, 114354, 1795419)
        assert all(cuts[i - 1] + 2 < HEIGHTS[i] for i in (1, 2))
        for stage, cut in enumerate(cuts, 1):
            assert [stage_for_width_log(cut + d, len(HEIGHTS), HEIGHTS) for d in (-1, 0, 1)] == [stage - 1, stage, stage]
        seams = [dispatch_fixture(TERMINAL, cuts, 2, 128000),
                 dispatch_fixture(TERMINAL, cuts, 3, 1824000),
                 dispatch_fixture(TERMINAL, cuts, 2, 960000),
                 dispatch_fixture(TERMINAL, cuts, 3, 15136000)]
        assert [row["direct"] for row in seams] == [True, True, False, False]
        for value in ((1 << 256) + 1, (1 << 257) - 1, (1 << 512) + 123):
            root = ceil_root(value, 256)
            assert (root - 1)**256 < value <= root**256

        stock = resource_receipt(TERMINAL)
        assert stock["binary_cuts"] == list(cuts) and activation(TERMINAL) == stock["public_exponent_A"]
        conversion = ((K - ENTRY.kappa) * activation(TERMINAL)).__ceil__()
        complete = 1 + max(early["log2_C"] + conversion, terminal["log2_C"])
        assert terminal["log2_B"] == 128 + 9 + 320 * sum(HEIGHTS)
        assert complete == 1 + terminal["log2_C"]
        assert max(HEIGHTS).bit_length() == 21 and GAUSSIAN_H.bit_length() <= 20

        print(json.dumps({
            "status": "PASS_ORDINARY_COMPONENT_AND_FINITE_SEAMS",
            "source_head": "06691302af526a488f3dee0298035f86b6e69c51",
            "runtime_pins": RUNTIME_PINS,
            "kappa": str(K), "ordinary_booking": str(ORDINARY), "eta": str(ETA),
            "rho": str(Q(1, 250)), "heights": list(HEIGHTS), "stages": stages,
            "gaussian_height": GAUSSIAN_H,
            "gaussian_margin_over_booking": str(positive_at(GAUSSIAN_H) - ORDINARY),
            "gaussian_previous_height_margin": str(positive_at(GAUSSIAN_H - 1) - ORDINARY),
            "signed_outer": signed, "cuts": list(cuts), "seams": seams,
            "controls_rejected": controls,
            "ordinary_debit_used": str(OLD_DEBIT),
            "ordinary_conservative_factor_margin_lower": str(old_allow - factor_hi),
            "conservative_factor_exceeds_parent_debit_upper_by": str(factor_lo - parent_allow),
            "ordinary_floor": 18960, "native_recipe_open_seam": "PASS_CAPTURED_PLAN",
            "activation_exponent": activation(TERMINAL), "entry_log2_C": early["log2_C"],
            "entry_conversion_bits": conversion, "terminal_log2_B": terminal["log2_B"],
            "terminal_log2_C": terminal["log2_C"], "complete_log2_C": complete,
            "setup_numeric_guards": {"all_seven_heights_in_25_bit_range": True,
                                     "max_scalar_encoding_bits": scalar_bits,
                                     "scope": "Numeric premises only; the 8088 shortcut-word base action census needs separate rebinding."},
            "scope": "Exact ordinary component and captured direct/compiled dispatch only; no physical product or new portable trace. Parent receipt.bank was invoked with an explicit old-debit override, not via its unchanged hardcoded main check.",
        }, indent=2, sort_keys=True))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    main(Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve())

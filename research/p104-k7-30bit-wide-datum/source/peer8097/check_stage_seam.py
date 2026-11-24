"""Replay 6-stage 28-bit ordinary dispatch, all comparator controls, and bounded signed bank returns."""
from dataclasses import replace
from fractions import Fraction as Q
from hashlib import sha256
from io import BytesIO
from itertools import product
import json
from pathlib import Path
import sys

RUNTIME = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(RUNTIME))
from upstream import install

install()


class DyadicWidth(int):
    """Speed up exact exponentiation of a mathematically dyadic test width."""

    def __pow__(self, exponent):
        assert self.bit_count() == 1 and exponent >= 0
        return 1 << ((self.bit_length() - 1) * exponent)


def verify_stage(profile, cuts, number, log_width):
    import ordinary_carrier as carrier

    calls = []
    base = DyadicWidth(1 << log_width)
    prev = 1 << cuts[number - 2]
    power = 1 << (log_width // 250)
    eta = profile.eta
    assert log_width % 10000 == 0 and log_width * eta.numerator % eta.denominator == 0 and log_width % 250 == 0
    width = max(prev + 1, power)
    component = 1 << (log_width * eta.numerator // eta.denominator)
    count = -(-width // component)
    short, longer = divmod(width, count)
    expected_layout = (longer, short + 1, count - longer, short)
    rank = 1 << profile.rank_logs[number - 1]
    expect_direct = -(-base // width) <= 1 << (8 * profile.rank_logs[number - 1])

    def root(value, degree):
        assert value.bit_count() == 1
        quotient, remainder = divmod(value.bit_length() - 1, degree)
        assert not remainder
        return 1 << quotient

    def receiver(dimension, layout, previous, *, direct, profile):
        assert dimension == rank and layout == expected_layout and direct == expect_direct
        assert previous.func is carrier.ternary
        assert previous.keywords == {"maximum": number - 1, "profile": profile}
        return number

    def body(source, target, digits, prefix, gap, suffix, backend):
        assert digits == base and (prefix, gap, suffix) == (1, 3, 5) and backend == number
        calls.append((digits.bit_length() - 1, backend))

    actual = carrier.ceil_root, carrier.Receiver, carrier.root_body
    try:
        carrier.ceil_root, carrier.Receiver, carrier.root_body = root, receiver, body
        carrier.ternary(None, None, base, 1, 3, 5, maximum=number, profile=profile)
    finally:
        carrier.ceil_root, carrier.Receiver, carrier.root_body = actual
    assert calls == [(log_width, number)]
    return {
        "stage": number,
        "scanned_log": log_width,
        "rank_log": rank.bit_length() - 1,
        "predecessor_cut": cuts[number - 2],
        "direct": expect_direct,
        "component_log": component.bit_length() - 1,
    }


def verify_tape(width, u, v):
    from five_exchange import same_order_line
    from growing_binary import Weighted
    from same_order_body import SameOrderBody
    from streaming_routes import cold_swap_tape
    from ternary_leaf import select_pivot

    class Core(SameOrderBody, Weighted):
        def __init__(self):
            super().__init__(2, (1, width, 0, 0), cold_swap_tape)
            self.stock = self.owners
            self.calls = 0

        def weighted(self, *args, **kwargs):
            assert kwargs["atoms"] == 1 < self.n
            self.calls += 1
            return super().weighted(*args, **kwargs)

    core = Core()
    modulus = core.modulus
    assert modulus == 3**width and core.atom == modulus
    assert sum(a * b for a, b in zip(u, v, strict=True)) % modulus == 1
    weight = lambda row, j: (2, 4)[j]
    inverse = tuple(pow(weight(0, j), -1, modulus) for j in range(2))

    def dense(sign):
        out = bytearray(len(raw))
        size = modulus**4
        for x0, x1, y0, y1 in product(range(modulus), repeat=4):
            delta = sum(v[j] * (y - inverse[j] * x) for j, (x, y) in enumerate(zip((x0, x1), (y0, y1), strict=True))) % modulus
            target = (
                (x0 + sign * 2 * u[0] * delta) % modulus,
                (x1 + sign * 4 * u[1] * delta) % modulus,
                (y0 - sign * u[0] * delta) % modulus,
                (y1 - sign * u[1] * delta) % modulus,
            )
            i = ((x0 * modulus + x1) * modulus + y0) * modulus + y1
            k = 0
            for value in target:
                k = k * modulus + value
            assert 0 <= k < size
            out[4 * k : 4 * k + 4] = raw[4 * i : 4 * i + 4]
        return bytes(out)

    raw = b"".join(i.to_bytes(4, "little") for i in range(modulus**4))
    source, destination = BytesIO(raw), BytesIO()
    same_order_line(
        core,
        source,
        destination,
        pivot=select_pivot(u, v),
        factors=lambda _: (u, v),
        f=1,
        unused=1,
        heights=1,
        older=1,
        gap=1,
        suffix=4,
        weight=weight,
    )
    assert source.getvalue() == raw and source.tell() == len(raw)
    assert destination.getvalue() == dense(1)
    assert destination.getvalue() != dense(-1), "wrong signed return was accepted"
    assert 1 <= core.calls <= 5
    return {
        "component_width": width,
        "modulus": modulus,
        "records": modulus**4,
        "paid_exchanges": core.calls,
        "wrong_signed_return_rejected": True,
    }


def check():
    sys.path.append(str(Path(__file__).resolve().parent.parent / "tiered-native-multiplier" / "source"))
    from activation import full_entrance, resource_receipt
    from band_product import prepare_native
    from installations import BINARY_C, ENTRY, GAUSSIAN_C, TERMINAL, activation
    from outer_budget import qualify
    from raw_binary_stage import binary_word
    from staged_carriers import entrance_logs

    ORDINARY = Q(1418665, 2**20)  # periodic-integral suffix at L=1156, 2401/1024 tariff, FULL 256/255 reserve
    GAUSSIAN = Q(32401, 262144)    # w5664 10-shortcut + 3-type (1, 45, 2025)
    STOP = Q(1, 10**18)
    TOTAL = 171810078109
    PREMIUM = 242079
    BITS = 28
    TOP = (1 << BITS) - 1
    ranks = tuple(TERMINAL.rank_logs)
    last = len(ranks) - 1
    assert ranks == (8192, 63614, 1005821, 15903360, 251454111, TOP) and TERMINAL.complex_log == 52270
    assert GAUSSIAN_C == Q(17166573920, 2**42)
    assert TERMINAL.kappa == Q(".003900862325217")

    def ordinary_upper(heights, debit=ORDINARY, eta=TERMINAL.eta):
        r = Q(0)
        for i, h in enumerate(heights):
            u = min(eta, (249 * (BINARY_C - debit / h) + r) / 250)
            r = u if i == len(heights) - 1 else Q((u * 10**21).__floor__() - 1, 10**21)
        return r

    def gaussian_upper(h):
        return GAUSSIAN_C - GAUSSIAN / h

    def rejected(function, label):
        try:
            function()
        except (AssertionError, ArithmeticError, ValueError):
            return label
        raise AssertionError(f"Negative control {label} was not rejected")

    paid = TERMINAL.kappa + 5 * STOP
    assert TERMINAL.ordinary == paid
    assert ordinary_upper(ranks) > paid and gaussian_upper(TERMINAL.complex_log) > paid
    assert TERMINAL.kappa <= ordinary_upper(ranks) - 5 * STOP < TERMINAL.kappa + Q(1, 10**15)
    assert all(8192 <= h < 2**BITS for h in ranks) and 1024 <= TERMINAL.complex_log < 2**25
    assert TERMINAL.eta == Q(1, 256) and paid < TERMINAL.eta < Q(1, 250) and TERMINAL.eta * 8192 - 1 > 30
    assert 2 * TERMINAL.eta > Q(1, 250) and TERMINAL.eta > Q(1, 258)
    assert all(ordinary_upper(ranks[:i]) < TERMINAL.eta for i in range(1, len(ranks)))
    assert all(-(-(2 * h + 64) * 256 // 255) < 3 * h for h in ranks)
    assert 2660000 * (30 + 2) < 2**30 and 17**16 * 10 ** (21 * 16) < 2**1182

    stock = resource_receipt(TERMINAL)
    cuts = tuple(stock["binary_cuts"])
    assert tuple(entrance_logs(ranks)) == cuts
    assert all(cuts[i - 1] + 2 < ranks[i] for i in range(1, len(ranks)))
    assert activation(TERMINAL) == stock["public_exponent_A"]
    assert stock["retimed_first_stripe_margin"] > 1024 and stock["retimed_all_size_margin_floor"] > 1024
    signed = qualify(TERMINAL.kappa, STOP, paid, gaussian_upper(TERMINAL.complex_log))
    assert (signed["strict"], signed["functional"]) == (54, 4)

    logB = 128 + 3 * len(ranks) + 320 * sum(ranks)
    late = 1602 + 220 * TERMINAL.complex_log + logB
    conversion = ((TERMINAL.kappa - ENTRY.kappa) * activation(TERMINAL)).__ceil__()
    assert conversion == PREMIUM and logB == 171798577106
    assert 1 + max(125660246 + conversion, late) == TOTAL
    assert TOTAL > 318292011

    def at(index, delta):
        return tuple(h + (delta if j == index else 0) for j, h in enumerate(ranks))

    def require_funding(proposed, gaussian, eta=TERMINAL.eta):
        if ordinary_upper(proposed, eta=eta) <= paid or gaussian_upper(gaussian) <= paid:
            raise ArithmeticError("Profile does not fund the terminal price")

    def require_budget(cap):
        if 1 + max(125660246 + conversion, late) > cap:
            raise ArithmeticError("The full recurring invoice exceeds the declared cap")

    prev_8094 = ((31808, 502922, 7951907, 125730703, 134217727), 208653)
    prev_8090 = ((125432, 1988432, 31439868, 33554431), 198527)
    capped_20bit = ((62350, 985843, 1048575), 33856)
    five_stage_28 = ((63614, 1005841, 15903840, 251461645, TOP), TERMINAL.complex_log)
    assert ordinary_upper(five_stage_28[0]) < ordinary_upper(ranks)

    DROPS = (861, 231, 232, 232, 232, 2)
    for i, d in enumerate(DROPS):
        require_funding(at(i, -(d - 1)), TERMINAL.complex_log)

    controls = [
        rejected(lambda i=i, d=d: require_funding(at(i, -d), TERMINAL.complex_log), f"ordinary-height-{i}-minus-{d}")
        for i, d in enumerate(DROPS)
    ]
    controls += [
        rejected(lambda i=i: resource_receipt(replace(TERMINAL, rank_logs=at(i, 1))), f"ordinary-height-{i}-plus-one-breaks-prefix")
        for i in range(last)
    ]
    controls += [
        rejected(lambda: (_ for _ in ()).throw(AssertionError()) if min(at(0, -1)) < 8192 else None, "first-ordinary-height-below-8192"),
        rejected(lambda: require_funding(*five_stage_28), "five-stage-28bit-profile-at-new-rate"),
        rejected(lambda: require_funding(*prev_8094), "pr8094-27bit-profile-at-new-rate"),
        rejected(lambda: require_funding(*prev_8090), "pr8090-25bit-profile-at-new-rate"),
        rejected(lambda: require_funding(*capped_20bit, eta=Q(39, 10000)), "capped-20bit-profile-at-new-rate"),
        rejected(lambda: require_funding(ranks, TERMINAL.complex_log - 1), "gaussian-height-minus-one"),
        rejected(lambda: require_funding(ranks, TERMINAL.complex_log) or require_budget(318292011), "inherited-cap-318292011"),
        rejected(lambda: qualify(TERMINAL.kappa, STOP, paid - STOP, gaussian_upper(TERMINAL.complex_log)), "outer-ordinary-margin-removed"),
        rejected(lambda: resource_receipt(replace(TERMINAL, rank_logs=(ranks[0], cuts[0] + 2, *ranks[2:]))), "prefix-height-at-previous-cut"),
        rejected(lambda: require_budget(TOTAL - 1), "recurring-bound-minus-one"),
        rejected(lambda: (_ for _ in ()).throw(AssertionError()) if min(Q(39, 10000), ordinary_upper(ranks)) <= paid else None, "old-eta-39/10000"),
    ]
    assert ranks[last] == TOP and TOP.bit_length() == BITS and 1024 * (TOP + 1) + 3 >= 2**38

    # Local optimality of free prefix with h5 pinned at 2^28 - 1 and h4 pinned by cut prefix rule.
    def max_penultimate(prefix):
        lo, hi = prefix[-1], TOP
        while hi - lo > 1:
            mid = (lo + hi) // 2
            try:
                resource_receipt(replace(TERMINAL, rank_logs=(*prefix, mid, TOP)))
                lo = mid
            except AssertionError:
                hi = mid
        return lo

    free = ranks[: last - 1]
    assert max_penultimate(free) == ranks[last - 1]
    neighbours = []
    for i in range(len(free)):
        for s in (-16, 16):
            t = list(free)
            t[i] += s
            if t[0] >= 8192:
                neighbours.append(ordinary_upper((*t, max_penultimate(t), TOP)))
    assert all(n <= ordinary_upper(ranks) for n in neighbours)

    # Verify all five comparator control tiers under our exact debits (retaining FULL 256/255):
    def check_control(c_ranks, c_G, c_kappa, c_eta, c_cap=None, tight_floor=True):
        c_paid = c_kappa + 5 * STOP
        u = ordinary_upper(c_ranks, eta=c_eta)
        assert u > c_paid and gaussian_upper(c_G) > c_paid
        if tight_floor:
            assert u - Q(1, 10**15) <= c_paid
        else:
            assert ordinary_upper(c_ranks[:-1] + (c_ranks[-1] - 1,), eta=c_eta) <= c_paid
        assert gaussian_upper(c_G - 1) <= c_paid
        assert entrance_logs(c_ranks) and all(entrance_logs(c_ranks)[i - 1] + 2 < c_ranks[i] for i in range(1, len(c_ranks)))
        c_A = full_entrance(entrance_logs(c_ranks)[-1], c_G)
        c_prem = ((c_kappa - ENTRY.kappa) * c_A).__ceil__()
        c_late = 1602 + 220 * c_G + 128 + 3 * len(c_ranks) + 320 * sum(c_ranks)
        c_tot = 1 + max(125660246 + c_prem, c_late)
        if c_cap is not None:
            assert c_tot <= c_cap
        return c_tot, c_prem

    cap_tot, cap_prem = check_control((26960, 426219, 524288), 25003, Q(".003898283457829"), Q(39, 10000), 318291911)
    bit20_tot, bit20_prem = check_control((62350, 985843, 1048575), 33856, Q(".003899576196608"), Q(39, 10000))
    t39_tot, t39_prem = check_control((8192, 106000, 1656186), 38302, Q("0.0039"), Q(1, 256), tight_floor=False)
    bit25_tot, bit25_prem = check_control((125432, 1988431, 31439869, 33554431), 51501, Q(".003900827024476"), Q(1, 256))
    bit27_tot, bit27_prem = check_control((31808, 502922, 7951910, 125730700, 134217727), 52158, Q(".003900857282381"), Q(1, 256))
    assert cap_tot == 318291840 and cap_prem == 450
    assert bit20_tot == 678415820 and bit20_tot < 685495960
    assert t39_tot == 574949140 and t39_tot < 593252820
    assert bit25_tot == 21485944123 and bit25_tot < 21518289843
    assert bit27_tot == 85910697946 and bit27_tot < 85945126846

    assert sha256((RUNTIME / "strong-bit.json.gz").read_bytes()).hexdigest() == "9e7392c52bcf29c0cc58c54c619f95c28f476394c33e8e0a5aa30c9557d31362"
    assert sha256((RUNTIME / "w5664_shortcut10.json.gz").read_bytes()).hexdigest() == "ce395afbf5c32be64c4e62389acaf9ce8cf8a9aaaa2fb7a278135bcfa0e635aa"
    old = replace(TERMINAL, rank_logs=(62350, 985843, 1048575), complex_log=33856, kappa=Q(".003899576196608"), eta=Q(39, 10000))
    old_native, new_native = prepare_native(old), prepare_native(TERMINAL)
    word = binary_word()
    assert (len(word.targets), len(word.paid), len(word.cells)) == (18906, 104652, 24)
    assert old_native[-1].targets is new_native[-1].targets and old_native[-1].cells is new_native[-1].cells
    assert all(
        v.level_floor == 1156 and v.targets is word.targets and v.paid is word.paid and v.cells is word.cells
        for v in (*old_native[:-1], *new_native[:-1])
    )

    def round_up(n):
        return ((n + 159999) // 160000) * 160000  # lcm(10000, 250, 256)

    direct = [verify_stage(TERMINAL, cuts, i, round_up(cuts[i - 1])) for i in range(2, len(ranks) + 1)]
    compiled = [verify_stage(TERMINAL, cuts, i, round_up(9 * ranks[i - 1])) for i in range(2, len(ranks) + 1)]
    assert all(x["direct"] for x in direct) and not any(x["direct"] for x in compiled)
    tape = [verify_tape(1, [0, 1], [2, 1]), verify_tape(2, [1, 7], [3, 1])]
    print(
        "PASS_10SHORTCUT_3TYPE_28BIT_6STAGE_SEAM",
        json.dumps(
            {
                "kappa": str(TERMINAL.kappa),
                "heights": ranks,
                "gaussian_height": TERMINAL.complex_log,
                "binary_cuts": cuts,
                "signed": signed,
                "conversion_bits": conversion,
                "log2_B": logB,
                "complete_log2_C": TOTAL,
                "comparators": {
                    "strict_cap": {"kappa": "0.003898283457829", "log2_C": cap_tot, "G": 25003},
                    "20bit": {"kappa": "0.003899576196608", "log2_C": bit20_tot, "G": 33856},
                    "8089_0039": {"kappa": "0.0039", "log2_C": t39_tot, "G": 38302},
                    "25bit_4stage": {"kappa": "0.003900827024476", "log2_C": bit25_tot, "G": 51501},
                    "27bit_5stage": {"kappa": "0.003900857282381", "log2_C": bit27_tot, "G": 52158},
                },
                "controls": controls,
                "direct_stage_seams": direct,
                "compiled_stage_seams": compiled,
                "signed_tape": tape,
            },
            sort_keys=True,
            default=str,
        ),
        flush=True,
    )


if __name__ == "__main__":
    check()

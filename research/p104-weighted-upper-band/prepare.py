"""Install a single directed finite-debit retune on the exact weighted producer."""
from hashlib import sha256
import json

NEW_INSTALLATION = "64f415e0d6c13776c1b73c71c687ea989d8fea9807340fd0ca39517f99dd04b0"


def replace(path, replacements):
    source = path.read_text()
    for old, new in replacements:
        if source.count(old) != 1:
            raise ValueError(f"Expected one change point for {old!r} in {path.name}")
        source = source.replace(old, new)
    path.write_text(source)


OLD_EDGE = '''    # The first three positive terms of log(k/r) suffice for each real edge.
    psi = Q(0)
    for (r, k), share in cells.items():
        u = Q(k - r, k + r)
        log_lower = 2 * (u + u**3 / 3 + u**5 / 5)
        psi += paid[r] * share * r * log_lower'''

DIRECTED_EDGE = '''    # Integrate each exact directed edge, retaining both rounding ends.
    # A downward ratio of outward powers bounds ((k/r)^c-1)/c.
    psi = Q(0)
    for (r, k), share in cells.items():
        floor = intervals(k, c)[0] * UNIT // intervals(r, c)[1]
        assert floor > UNIT
        psi += paid[r] * share * r * (Q(floor, UNIT) - 1) / c'''

NATIVE_SETUP = '''    setup = native_clock()
    grade_count = len(low[-1].paid.histogram) + len(low[-1].targets.histogram)
    actual_roles = sum(len(v.targets) + len(v.paid) for v in high[-1].types())
    assert actual_roles < 2**20 and grade_count < 2**8
    assert len(low) + len(high) == 7 and max(heights[-1].bit_length() for heights in (ENTRY.rank_logs, TERMINAL.rank_logs)) == 20
    grade_actions = 2**20 * 256 + 2**8 * 256 * 8 + 32 * (grade_count + 2)**2 + 2**12
    assert grade_actions < 2**32 and setup["all_setup"] < 2**228'''

EDITS = {
    "runtime.patch": (
        ('TERMINAL = Profile((8192, 129414, 524288), 483871, Q(".00389821"))',
         'TERMINAL = Profile((8192, 129414, 524395), 483871, Q(".00389821053"))'),
    ),
    "positive_debit.py": (
        ("from strict_moment import UNIT, power_interval", "from strict_moment import UNIT, power_interval\nfrom unpowered_price import intervals"),
        ("POSITIVE_DEBIT = Q(65081, 524288)", "POSITIVE_DEBIT = Q(64944, 524288)"),
        (OLD_EDGE, DIRECTED_EDGE),
        ("assert psi > Q(1790217668064, 10000)", 'assert psi > Q("926899828.8291")'),
        ("assert fringe < Q(7579, 1000)", 'assert fringe < Q("7.335168")'),
    ),
    "receipt.py": (
        ('sys.path.append(str(HERE / "portable"))', 'sys.path.append(str(HERE.parent / "tiered-native-multiplier"))'),
        ("from verify_receipt import verify as fixed_installation", "from check_serial_setup import clock as native_clock"),
        ("DEBIT = Q(65081, 2**19)", "DEBIT = Q(64944, 2**19)"),
        ("assert cost == 318259431 and premium == 514", "assert cost == 318293671 and premium == 514"),
        ("(517430, 483870)", "(517533, 483791)"),
        ('older = Q(".0038982016137")', 'older = Q(".00389821040")'),
        ("assert gain == Q(83863, 10**13)", "assert gain == Q(13, 100_000_000_000)"),
        ("    setup = fixed_installation()", NATIVE_SETUP),
        ('''        log2_fixed_setup_upper=setup["trace_exponent"],
        log2_portable_setup_guard=setup["conservative_exponent"],
        log2_full_store_setup_upper=setup["full_store_trace_exponent"],
        portable_setup_transition_upper=setup["transitions"],''',
         '''        log2_fixed_setup_upper=setup["setup_exponent"],
        native_setup_transition_upper=setup["all_setup"],
        native_setup_grade_actions=grade_actions,'''),
    ),
    "independent_price.py": (
        ("lower = powers(2, Q(65081, 524288))[0]", "lower = powers(2, Q(64944, 524288))[0]"),
        ('assert lower - upper > Q("0.00012957")', 'assert lower - upper > Q("0.000007887415")'),
        ("TERMINAL.kappa - peer == Q(83863, 10**13)", "TERMINAL.kappa - peer == Q(89163, 10**13)"),
    ),
}


# Apply exact real-integer frequencies and reprice the full typed calendar.
EDITS["runtime.patch"] += (
    ("+GAUSSIAN_C = Q(17145637167, 2**42)", "+GAUSSIAN_C = Q(17145637307, 2**42)"),
)
EDITS["grades.py"] = (("WEIGHTS = (1, 90)", "WEIGHTS = (5, 451)"),)
EDITS["positive_debit.py"] += (
    ("assert target_axes == 135150528", "assert target_axes == 677246016"),
    ("assert 91 / (t * 2**10)", "assert sum((5, 451)) / (t * 2**10)"),
)
EDITS["receipt.py"] += (
    ("def raw_counts(base, multiplicity):", "def raw_counts(base, multiplicity, primary=1):"),
    ("t, p = targets.copy(), paid.copy()",
     "t = Counter({grade: entry * primary for grade, entry in targets.items()})\n"
     "    p = Counter({grade: entry * primary for grade, entry in paid.items()})"),
    ("p[1] -= 1008\n    p[Q(1, 2)] += 2016",
     "p[1] -= 1008 * primary\n    p[Q(1, 2)] += 2016 * primary"),
    ("def total_interval(counts):", "def total_interval(counts, trial=GAUSSIAN_C):"),
    ("intervals(grade, 1 - GAUSSIAN_C)", "intervals(grade, 1 - trial)"),
    ("WEIGHTS == (1, 90)", "WEIGHTS == (5, 451)"),
    ("t, p = raw_counts(base, 90)", "t, p = raw_counts(base, WEIGHTS[1], WEIGHTS[0])"),
    ("<= 261", "<= 270"),
    ("    cuts = {}",
     "    high = total_interval({k: n for k, n in t.items() if k > 2})\n"
     "    required = total_interval({r: n for r, n in p.items() if 5 * r > 8})\n"
     "    assert high[0] - required[1] > 462\n"
     "    past_targets, past_paid = raw_counts(base, 541, 6)\n"
     "    assert total_interval(past_targets)[1] < total_interval(past_paid)[0]\n"
     "    old_tariff = Q(17145637167, 2**42)\n"
     "    cuts = {\"new\": [str(high[0] - required[1]), str(high[1] - required[0])]}"),
    ("        cap = total_interval({k: n for k, n in chosen.items() if k > 2})",
     "        cap = total_interval({k: n for k, n in chosen.items() if k > 2}, old_tariff)"),
    ("        load = total_interval({r: n for r, n in required.items() if 5 * r > 8})",
     "        load = total_interval({r: n for r, n in required.items() if 5 * r > 8}, old_tariff)"),
    ("        net = total_interval(chosen)[0] - total_interval(required)[1]",
     "        net = total_interval(chosen, old_tariff)[0] - total_interval(required, old_tariff)[1]"),
)
EDITS["independent_price.py"] += (
    ('assert psi > Q("184971191.2157")', 'assert psi > Q("926899828.8291")'),
)
EDITS["check_placement.py"] = (
    ("assert 90 * (hi - lo) * M * pi > 4", "assert WEIGHTS[1] * (hi - lo) * M * pi > 4"),
)
EDITS["check_exterior.py"] = (
    ("from band_product import production_supplier", "from band_product import production_supplier\nfrom installations import GAUSSIAN_C"),
    ("c = Q(17145637167, 2**42)", "c = GAUSSIAN_C"),
)
EDITS["check_nested.py"] = (
    ("        * cells[1, 2]\n        * 90", "        * cells[1, 2]\n        * types[0].multiplicity\n        * types[1].multiplicity"),
    ("share == cells[1, 2] * 90 / t[2]", "share == cells[1, 2] * types[1].multiplicity / t[2]"),
    ("and grant.numerator // grant.denominator == 899557645", "and 4_400_000_000 < grant.numerator // grant.denominator < 4_600_000_000"),
)
EDITS["check_ownership.py"] = (
    ("def run(freq, ticks, lower, upper, volume, n, rounds, delay):",
     "def run(freq, ticks, lower, upper, volume, n, rounds, delay, primary=1):"),
    ("NativeType((2,), (1, 1), 1)", "NativeType((2,), (1, 1), primary)"),
    ("(1, 1, 0, 2): Q(1, 2 * freq)", "(1, 1, 0, 2): Q(primary, 2 * freq)"),
    ("1 - Q(1, 2 * freq)", "1 - Q(primary, 2 * freq)"),
    ("        frequency=freq,", "        frequency=(primary, freq),"),
    ("run(90, 8, 10, 42, 450, 384, 32, 4)]",
     "run(90, 8, 10, 42, 450, 384, 32, 4), run(451, 8, 10, 42, 90, 384, 32, 4, primary=5)]"),
)


# Keep the reproduced lower edge and widen the actual even upper fence.
EDITS["grades.py"] += (
    ("LOWER = 2048", "LOWER = 1874\nUPPER_DIVISOR = 1724"),
    ("2048 * self.ambient", "UPPER_DIVISOR * self.ambient"),
)
EDITS["positive_debit.py"] += (
    ("BAND_LOWER = 2048", "BAND_LOWER = 1874"),
    ("from unpowered_price import intervals", "from unpowered_price import intervals\nfrom grades import UPPER_DIVISOR"),
    ("    upper = 2 * (M // (2048 * recipe.ambient))",
     "    scale = UPPER_DIVISOR * recipe.ambient // 2\n"
     "    upper = 2 * (M // (2 * scale))\n"
     "    assert 4 * max(targets) * (upper - 8) < M and 516 * (upper + 2) < M"),
    ("1024 * recipe.ambient * upper", "scale * upper"),
    ("Q(4 * max(targets), 1024 * recipe.ambient)", "Q(4 * max(targets), scale)"),
    ("power_interval(1024 * recipe.ambient * lower, c)", "power_interval(scale * lower, c)"),
    ('        "lower_band": lower,', '        "lower_band": lower,\n        "upper_divisor": UPPER_DIVISOR,\n        "upper_scale": scale,'),
    ("assert t > Q(996, 1000) and 11 * t > 10",
     "assert t > Q(996, 1000) and power_interval(lower, t)[0] > 1024 * UNIT"),
)
EDITS["receipt.py"] += (("and LOWER == 2048", "and LOWER == 1874"),)
EDITS["independent_price.py"] += (
    ("from installations import BINARY_C, TERMINAL", "from installations import BINARY_C, TERMINAL\nfrom grades import LOWER, UPPER_DIVISOR"),
    ("    upper = (", "    scale = UPPER_DIVISOR * recipe.ambient // 2\n    upper = ("),
    ("Q(4 * 258, 1024 * 306)", "Q(4 * 258, scale)"),
    ("powers(1024 * 306 * 2048, c)[1]", "powers(scale * LOWER, c)[1]"),
    ("fringe / 2048", "fringe / LOWER"),
    ('    assert lower - upper > Q("0.000007887415")',
     '    assert lower - upper > Q("0.000007887415")\n'
     '    psi_hi = sum(recipe.paid.histogram[r] * share * r * (powers(Q(k,r), c)[1] - 1) / c\n'
     '                 for (r,k), share in recipe.cells.items())\n'
     '    prior_fringe = 10 * axes / ((1-c) * psi_hi)\n'
     '    prior_scale = 1024 * recipe.ambient\n'
     '    prior_factor = ((1+delta) * (1+Q(4*258,prior_scale)) * powers(prior_scale*LOWER,c)[0]\n'
     '                    * (1+prior_fringe/LOWER+delta) / (1-delta)**4)\n'
     '    assert prior_factor - powers(2, Q(64944,524288))[1] > Q("0.000051649827")'),
)
EDITS["check_placement.py"] += (
    ("from grades import numerical_recipe, WEIGHTS", "from grades import numerical_recipe, LOWER, UPPER_DIVISOR, WEIGHTS"),
    ("    U = 2 * (M // (2048 * 306))",
     "    scale = UPPER_DIVISOR * recipe.ambient // 2\n"
     "    assert UPPER_DIVISOR == 1724 and scale == 263772\n"
     "    U = 2 * (M // (2 * scale))"),
    ("    assert U < lo < hi < M", "    assert LOWER < e < U < lo < hi < M"),
    ("    assert period == 1620 and tickets == (0, 324, 648) and f.swaps[0] == (1, 324, 1)",
     "    assert period == 1364 and tickets == (0, 272, 545) and f.swaps[0] == (1, 272, 1)"),
)
EDITS["verify.py"] = (
    ('("check_calendar.py", "check_ownership.py")',
     '("check_calendar.py", "check_ownership.py", "check_cutoff.py")'),
)


def materialize(package):
    for name, replacements in EDITS.items():
        replace(package / name, replacements)
    path = package / "SOURCES.json"
    pins = json.loads(path.read_bytes())
    pins["runtime_images"]["installations.py"]["after"] = NEW_INSTALLATION
    for name in ("runtime.patch", "grades.py"):
        pins["local_sources"][name] = sha256((package / name).read_bytes()).hexdigest()
    pins["runtime_images"]["grades.py"]["after"] = pins["local_sources"]["grades.py"]
    path.write_text(json.dumps(pins, indent=2) + "\n")

"""Install the stacked retune on the five-shortcut Gaussian word at 27-bit heights, 5 ordinary stages and eta 1/256 (enlarged budget)."""
from hashlib import sha256
import json

NEW_INSTALLATION = "5b31cca69a8f10c78152ae030ae7c7ab156d22feec83347b887aa3fe78098ee7"
RAW_FLOOR_IMAGES = {
    "before": "0c805a525322acf4eb03f083c2c763f3046c3d488e1f993beb484a3e2c2ff4a9",
    "after": "8020d33828233e7016700849a507a8cee78db8a17a33b6063b737313ea05b07f",
}
RAW_FLOOR_PATCH = """--- a/raw_binary_stage.py
+++ b/raw_binary_stage.py
@@ -45,7 +45,7 @@
 @cache
 def binary_recipe(height):
     word = binary_word()
-    return Recipe(height, word.tagged.ambient, word.targets, word.paid, word.cells, BINARY_C)
+    return Recipe(height, word.tagged.ambient, word.targets, word.paid, word.cells, BINARY_C, level_floor=4474)
""" + " \n \n def run(recipe, fields, machine):\n"


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
    assert len(low) + len(high) == 9 and max(h.bit_length() for h in (*ENTRY.rank_logs, ENTRY.complex_log, *TERMINAL.rank_logs, TERMINAL.complex_log)) <= 27
    # 27-bit indexed setup, extending the #8081/#8087 SETUP-PROOF (see SETUP-27BIT.md): every 92H stays below the\n    # datum bound w = 2^38, the Gaussian carriers stay below 2^25 bits, and each of the 9 recipes gets 2^24 actions.
    assert 92*(2**27-1) < 2**38 and 1024*(2**27-1)+3 < 2**38\n    assert TERMINAL.complex_log < 2**25 and ENTRY.complex_log < 2**25
    assert 2*2048*(2**25+1) + 9*2**24 == 137589952512 < 2**40
    assert TERMINAL.eta == Q(1, 256) and all(abs(x).bit_length() <= 128 for x in (TERMINAL.eta.numerator, TERMINAL.eta.denominator, TERMINAL.kappa.numerator, TERMINAL.kappa.denominator))
    grade_actions = 2**20 * 256 + 2**8 * 256 * 8 + 32 * (grade_count + 2)**2 + 2**12
    assert grade_actions < 2**32 and setup["all_setup"] < 2**228'''

DIRECTED_ORDINARY = '''def ordinary_debit():
    delta = Q(1, 2**128)
    predecessor_tariff = Q(47, 20)
    child_tariff = Q(2401, 1024)

    def bounds(floor, suffix, tariff=child_tariff, reserve=Q(1)):
        # #8082: the ordinary contraction is paid by the clock sum, so the
        # positive 256/255 summation reserve is not charged here.
        multiplier = (
            tariff * reserve * Q(4097, 4096) * Q(1028, 1024)
            * (1 + Q(suffix, floor) + delta) / ((1 - Q(10, floor)) * (1 - delta)**3)
        )
        lo, hi = powers(1024 * 134 * floor, BINARY_C)
        return multiplier * lo, multiplier * hi

    lo, hi = bounds(4474, Q(186, 25))
    # #8073's own booking at its floor, kept as a positive control.
    k_lo, k_hi = bounds(18960, 8, predecessor_tariff, Q(256, 255))
    # #8076's own booking (floor 18960, 8/L, child tariff) at 11178/8192.
    t_lo, t_hi = bounds(18960, 8, child_tariff, Q(256, 255))
    assert t_hi < 2 * powers(2, Q(2986, 8192))[0]
    # Our earlier retune (floor 4474, (186/25)/L, tariff 47/20) at 1430037/2^20.
    r_lo, r_hi = bounds(4474, Q(186, 25), predecessor_tariff, Q(256, 255))
    # #8082 (reserve dropped, tariff 47/20) at 1424116/2^20, and the tariff stack with 256/255 at 1426639/2^20.
    e_lo, e_hi = bounds(4474, Q(186, 25), predecessor_tariff)
    assert e_hi < 2 * powers(2, Q(375540, 2**20))[0]
    c_lo, c_hi = bounds(4474, Q(186, 25), child_tariff, Q(256, 255))
    assert c_hi < 2 * powers(2, Q(378063, 2**20))[0]
    assert r_hi < 2 * powers(2, Q(381461, 2**20))[0]
    assert 2 * powers(2, Q(3012, 8192))[0] - k_hi > Q("0.0000277614405947")
    prior_lo, prior_hi = bounds(18960, 64, predecessor_tariff, Q(256, 255))
    old_lo, old_hi = bounds(32768, 64, predecessor_tariff, Q(256, 255))
    allowance_lo, allowance_hi = (2 * end for end in powers(2, Q(372142, 2**20)))
    finer_allowance = 2 * powers(2, Q(372141, 2**20))[1]
    reserve = allowance_lo - hi
    assert reserve > 0 and lo - finer_allowance > 0
    # The new allowance also fails at #8073's floor 18960 with the 8/L suffix.
    assert k_lo > allowance_hi
    # Both parent bookings fail the combined allowance.
    assert t_lo > allowance_hi and r_lo > allowance_hi and e_lo > allowance_hi and c_lo > allowance_hi
    print("ORDINARY_RESERVE", float(reserve), float(lo - finer_allowance), float(k_lo - allowance_hi))
    assert prior_lo > allowance_hi
    assert 2 * powers(2, Q(3047, 8192))[0] - prior_hi > Q("0.000062662376093595")
    assert prior_lo - 2 * powers(2, Q(6093, 16384))[1] > Q("0.000046832527238212")
    assert prior_hi**1024 < 2**1405 < old_lo**1024
    assert old_hi**512 < 2**703
    assert Q(75, 32) / Q(47, 20) == Q(375, 376)

    # #8076: an equal tariff gives unit contraction; 2401/1024 gives sum 2401.
    child_volume = Q(75, 32)
    old_ratio, new_ratio = child_volume / predecessor_tariff, child_volume / child_tariff
    assert new_ratio == Q(2400, 2401) and 1 / (1 - new_ratio) == 2401
    old_sum, new_sum = 1 / (1 - old_ratio), 1 / (1 - new_ratio)
    assert old_sum == 376 and old_sum < new_sum < 8 * old_sum
    assert 2**16 < (Q(7, 10) * old_sum)**2 < 2**17
    assert 2**21 < (Q(7, 10) * new_sum)**2 < 2**22
    print("PASS_DIRECTED_ORDINARY_DEBIT", 4474, "1420718/1048576", "2400/2401", "(186/25)/L, no 256/255")
    print("PASS_CHILD_TARIFF", "2401/1024", "volume<=75/32", "sum=2401", "entry+5", "terminal+9")


'''

EDITS = {
    "runtime.patch": (
        ('TERMINAL = Profile((8192, 129414, 524288), 483871, Q(".00389821"))',
         'TERMINAL = Profile((31808, 502922, 7951907, 125730703, 134217727), 208653, Q(".003900857267786"), Q(1, 256))'),
    ),
    "positive_debit.py": (
        ("from strict_moment import UNIT, power_interval", "from strict_moment import UNIT, power_interval\nfrom unpowered_price import intervals"),
        ("POSITIVE_DEBIT = Q(65081, 524288)", "POSITIVE_DEBIT = Q(1039776, 2**23)"),
        (OLD_EDGE, DIRECTED_EDGE),
        ("assert psi > Q(1790217668064, 10000)", 'assert psi > Q("926190717.2837")'),
        ("assert fringe < Q(7579, 1000)", 'assert fringe < Q("7.340806")'),
    ),
    "receipt.py": (
        ('sys.path.append(str(HERE / "portable"))', 'sys.path.append(str(HERE.parent / "tiered-native-multiplier"))'),
        ("from verify_receipt import verify as fixed_installation", "from check_serial_setup import clock as native_clock"),
        ("DEBIT = Q(65081, 2**19)", "DEBIT = Q(1039776, 2**23)\nORDINARY_DEBIT = Q(1420718, 2**20)\nCHILD_TARIFF = Q(2401, 1024)"),
        ("def tape_factor(ambient, rate):", "def tape_factor(ambient, rate, lower, suffix=64):"),
        ("    delta, lower = Q(1, 2**128), 32768", "    delta = Q(1, 2**128)"),
        ("(1 + Q(64, lower) + delta)", "(1 + Q(suffix, lower) + delta)"),
        ("assert ordinary.ambient == 134 and ordinary.trial == BINARY_C",
         "assert ordinary.ambient == 134 and ordinary.trial == BINARY_C\n"
         "            assert ordinary.level_floor == 4474"),
        ("Q(11, 8 * height)", "ORDINARY_DEBIT / height"),
        ("Q(11, 8) / (BINARY_C - TERMINAL.ordinary)",
         "ORDINARY_DEBIT / (BINARY_C - TERMINAL.ordinary)"),
        ("        bound = 128 + 320 * sum(heights)",
         "        # The complete per-stage envelope grows by <8 (#8076).\n"
         "        bound = 128 + 3 * len(heights) + 320 * sum(heights)"),
        ("        bound = 40 + 17 + 16384 * sum(heights) + sum(additions)",
         "        # Charge the square of the new geometric child sum (#8076).\n"
         "        bound = 40 + 22 + 16384 * sum(heights) + sum(additions)"),
        ("    assert (tape_factor(134, BINARY_C) * Q(47, 20)) ** 8 < 2**11",
         '    ordinary_upper = Q("2.557796525567700799")\n'
         "    assert tape_factor(134, BINARY_C, 4474, Q(186, 25)) * Q(255, 256) * CHILD_TARIFF < ordinary_upper\n"
         "    assert ordinary_upper**1048576 < 2**1420718\n"
         "    assert Q(75, 32) / CHILD_TARIFF == Q(2400, 2401)"),
        ("assert cost == 318259431 and premium == 514", "assert cost == 85945126846 and premium == 121121\n"
         "    assert early['log2_C'] == 125660246 and late['log2_B'] == 85899221583"),
        ("(517430, 483870)", "(134145233, 208653)"),
        ('older = Q(".0038982016137")', 'older = Q(".003898219753506")'),
        ("assert gain == Q(83863, 10**13)", "assert gain == Q(\".003900857267786\") - Q(\".003898219753506\")"),
        ("        complete_log2_C=cost,", "        complete_log2_C=cost,\n"
         "        ordinary_floor=4474,\n"
         "        ordinary_matched_suffix_coefficient=\"186/25\",\n"
         "        ordinary_finite_debit=str(ORDINARY_DEBIT),\n"
         "        ordinary_child_tariff=str(CHILD_TARIFF),\n"
         '        ordinary_child_contraction="2400/2401",\n'
         "        ordinary_child_geometric_sum=2401,\n"
         "        ordinary_entry_clock_extra=5,\n"
         "        ordinary_terminal_clock_extra=3 * len(TERMINAL.rank_logs),"),
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
        ("lower = powers(2, Q(65081, 524288))[0]", "lower = powers(2, Q(1039776, 2**23))[0]"),
        ('assert lower - upper > Q("0.00012957")', 'assert lower - upper > Q("0.000007887415")'),
        ("TERMINAL.kappa - peer == Q(83863, 10**13)", 'TERMINAL.kappa - peer == Q(".003900857267786") - Q(".0038982016137")'),
        ("def rounded_peer():", DIRECTED_ORDINARY + "def rounded_peer():"),
        ("    weighted()\n    rounded_peer()", "    weighted()\n    ordinary_debit()\n    rounded_peer()"),
    ),
}


# Apply exact real-integer frequencies and reprice the full typed calendar.
EDITS["runtime.patch"] += (
    ("+GAUSSIAN_C = Q(17145637167, 2**42)", "+GAUSSIAN_C = Q(17158764376, 2**42)"),
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
    ('assert psi > Q("184971191.2157")', 'assert psi > Q("926190717")'),
    ('fringe < Q("7.335168")', 'fringe < Q("7.340806")'),
)
EDITS["independent_price.py"] += (
    ("assert (targets.total(), paid.total()) == (105216, 564142)", "assert (targets.total(), paid.total()) == (105216, 563662)"),
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
EDITS["receipt.py"] += (("and LOWER == 2048", "and LOWER == 1874"),
    # The shortcut word moves #8057's single-weight capacity control.
    ("assert cap[1] - load[0] < -1515 and net > Q(3, 100)", "assert cap[1] - load[0] < -960 and net > Q(3, 100)"),
)
EDITS["independent_price.py"] += (
    ("from installations import BINARY_C, TERMINAL", "from installations import BINARY_C, TERMINAL\nfrom grades import LOWER, UPPER_DIVISOR"),
    ("    upper = (", "    scale = UPPER_DIVISOR * recipe.ambient // 2\n    upper = ("),
    ("Q(4 * 258, 1024 * 306)", "Q(4 * 258, scale)"),
    ("powers(1024 * 306 * 2048, c)[1]", "powers(scale * LOWER, c)[1]"),
    ("fringe / 2048", "fringe / LOWER"),
    ('    assert lower - upper > Q("0.000007887415")',
     '    assert lower - upper > 0 and lower - upper > Q("0.000000019")\n'
     '    assert powers(2, Q(1039775, 2**23))[0] < upper\n'
     '    psi_hi = sum(recipe.paid.histogram[r] * share * r * (powers(Q(k,r), c)[1] - 1) / c\n'
     '                 for (r,k), share in recipe.cells.items())\n'
     '    prior_fringe = 10 * axes / ((1-c) * psi_hi)\n'
     '    prior_scale = 1024 * recipe.ambient\n'
     '    prior_factor = ((1+delta) * (1+Q(4*258,prior_scale)) * powers(prior_scale*LOWER,c)[0]\n'
     '                    * (1+prior_fringe/LOWER+delta) / (1-delta)**4)\n'
     '    assert prior_factor - powers(2, Q(64939,524288))[1] > Q("0.000127791")'),
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
     '("check_calendar.py", "check_ownership.py", "check_cutoff.py", "check_stage_seam.py", "check_ordinary_floor.py")'),
)


SHORTCUT_FILE = "w5669_shortcut5.json.gz"
SHORTCUT_SHA = "6ef741c346ea075c4f2ed11f9d42d7076103e72d4a9e5059d495f1cb990fd149"
SHORTCUT_PATCH = '--- a/strong_complex.py\n+++ b/strong_complex.py\n@@ -8,6 +8,7 @@\n import json\n \n WORD = "38d2b3a2311a9ba5fee091cc7aa204c7ed95651aec95d75184b2391df090cbfb"\n+SHORTCUT_WORD = "ed3bea7186f962f3a8a8ae389cecce3d1ef48a7a832cf9af6c9048a6b5919b35"\n LAYOUT = "0ce3f9e383fc4bfdd22612b9e34fc9759d97204215937b82d23aec2cedd9b8ee"\n ADDITIONAL = "6ff19e063214b1698165d9da1fcd6182d9b837ac2d6e61aa71658b629aabbc95"\n GRID = 154113755636630124932500335624192000\n@@ -42,7 +43,16 @@\n     graph, _ = reconstruct(parent, read("BANK-FACTORS.json.gz"))\n     if digest(graph) != WORD or digest(layout) != LAYOUT:\n         raise ValueError("The reconstructed Gaussian graph or its owner layout differs")\n-    return graph, layout\n+    # Install the five exact chart-3 relay shortcuts on the reconstructed word.\n+    import gzip\n+    shortcut = json.loads(gzip.decompress((Path(__file__).resolve().parent / "w5669_shortcut5.json.gz").read_bytes()))\n+    if digest(shortcut) != SHORTCUT_WORD:\n+        raise ValueError("The shortcut Gaussian graph differs")\n+    if any(shortcut[key] != graph[key] for key in ("initial", "final", "frames", "first_output")):\n+        raise ValueError("The shortcut word changed an endpoint, chart or output")\n+    if (len(graph["moves"]), len(shortcut["moves"])) != (5674, 5669):\n+        raise ValueError("The shortcut word does not remove exactly five transfers")\n+    return shortcut, layout\n \n \n def required_pairs(graph, layout):\n@@ -85,7 +95,7 @@\n \n     graph, layout = load_changed(data)\n     catalogue = native_catalogue(graph, layout)\n-    if digest(catalogue) != "8a9ff9558bf5fa3854699937fe063f98c86467d5d32a4488bfc878d2be081e70":\n+    if digest(catalogue) != "f581128079a67c9fc6341ee96dce772342748f508c77f7d5956bf41408d97f58":\n         raise ValueError("The generated all-column Clifford catalogue differs")\n     tables = Path(grade) / "retained/data"\n     bases = read_json(tables / "CALLER-PHASE-BASES.json")["by_q"]\n'
SHORTCUT_IMAGES = {"before": 'b0f18924be837173ccbbd1b7814a7a9a27228d68ff0dcbaf44a90a2065d0574c', "after": "8f3fb92523df006e2e94505127088aaf2e64fadd20b3cab2344f62d7690e875d"}
EDITS["bootstrap.py"] = (
    ('for name in ("grades.py", "typed_raw.py", "typed_transport.py"):',
     'for name in ("grades.py", "typed_raw.py", "typed_transport.py", "w5669_shortcut5.json.gz"):'),
)


def materialize(package):
    from pathlib import Path
    word = (Path(__file__).resolve().parent / SHORTCUT_FILE).read_bytes()
    if sha256(word).hexdigest() != SHORTCUT_SHA:
        raise ValueError("The shortcut word archive differs")
    (package / SHORTCUT_FILE).write_bytes(word)
    for name, replacements in EDITS.items():
        replace(package / name, replacements)
    with (package / "runtime.patch").open("a") as patch:
        patch.write(RAW_FLOOR_PATCH)
        patch.write(SHORTCUT_PATCH)
    path = package / "SOURCES.json"
    pins = json.loads(path.read_bytes())
    pins["runtime_images"]["installations.py"]["after"] = NEW_INSTALLATION
    pins["runtime_images"]["raw_binary_stage.py"] = RAW_FLOOR_IMAGES
    pins["runtime_images"]["strong_complex.py"] = SHORTCUT_IMAGES
    for name in ("runtime.patch", "grades.py", SHORTCUT_FILE):
        pins["local_sources"][name] = sha256((package / name).read_bytes()).hexdigest()
    pins["runtime_images"]["grades.py"]["after"] = pins["local_sources"]["grades.py"]
    path.write_text(json.dumps(pins, indent=2) + "\n")

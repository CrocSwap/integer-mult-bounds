"""Install a single directed finite-debit retune on the exact weighted producer."""
from hashlib import sha256
import json

NEW_INSTALLATION = "5c597dedddbd8419595c0516dd0062805fc2117f403ad7e619cc69857f66f9ef"


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
         'TERMINAL = Profile((8192, 129414, 524349), 483871, Q(".00389821030"))'),
    ),
    "positive_debit.py": (
        ("from strict_moment import UNIT, power_interval", "from strict_moment import UNIT, power_interval\nfrom unpowered_price import intervals"),
        ("POSITIVE_DEBIT = Q(65081, 524288)", "POSITIVE_DEBIT = Q(65000, 524288)"),
        (OLD_EDGE, DIRECTED_EDGE),
        ("assert psi > Q(1790217668064, 10000)", 'assert psi > Q("184971191.2157")'),
        ("assert fringe < Q(7579, 1000)", 'assert fringe < Q("7.335168")'),
    ),
    "receipt.py": (
        ('sys.path.append(str(HERE / "portable"))', 'sys.path.append(str(HERE.parent / "tiered-native-multiplier"))'),
        ("from verify_receipt import verify as fixed_installation", "from check_serial_setup import clock as native_clock"),
        ("DEBIT = Q(65081, 2**19)", "DEBIT = Q(65000, 2**19)"),
        ("assert cost == 318259431 and premium == 514", "assert cost == 318278951 and premium == 514"),
        ("(517430, 483870)", "(517488, 483834)"),
        ('older = Q(".0038982016137")', 'older = Q(".00389821005")'),
        ("assert gain == Q(83863, 10**13)", "assert gain == Q(1, 4_000_000_000)"),
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
        ("lower = powers(2, Q(65081, 524288))[0]", "lower = powers(2, Q(65000, 524288))[0]"),
        ('assert lower - upper > Q("0.00012957")', 'assert lower - upper > Q("0.000012868675")'),
        ("TERMINAL.kappa - peer == Q(83863, 10**13)", "TERMINAL.kappa - peer == Q(86863, 10**13)"),
    ),
}


def materialize(package):
    for name, replacements in EDITS.items():
        replace(package / name, replacements)
    path = package / "SOURCES.json"
    pins = json.loads(path.read_bytes())
    pins["runtime_images"]["installations.py"]["after"] = NEW_INSTALLATION
    pins["local_sources"]["runtime.patch"] = sha256((package / "runtime.patch").read_bytes()).hexdigest()
    path.write_text(json.dumps(pins, indent=2) + "\n")

"""Install the exterior-period debit on the charged 25-bit profile.

The exact paid calendar, owner paths, and all earlier-stage charges remain
in place. The exterior-period upper bound funds the new Gaussian debit.
"""
from hashlib import sha256
import json
from pathlib import Path
import shutil

HERE = Path(__file__).resolve().parent
PARENT_INSTALLATION = 'TERMINAL = Profile((8192, 124649, 524288), 490950, Q(".003898214283192"))'

PROFILES = {
    "460": dict(
        kappa=".003898460000505", heights=(8192, 38102, 604363), gaussian=18845934,
        total=4354317451, premium=8744, floors=(569896, 18845933),
        gain="101/200000000000000", peer_gain="51677361/200000000000000",
        image_sha="387e60913e375316d904d4489e5ea5e69c0ac5729250f27fe52ef23910a07e13",
        max_height_bits=25,
    ),
}


def replace(path, changes):
    content = path.read_text()
    for before, after in changes:
        if content.count(before) != 1:
            raise ValueError(f"Expected exactly one {before!r} in {path}")
        content = content.replace(before, after)
    path.write_text(content)


def q(expr):
    a, b = expr.split("/")
    return f"Q({a}, {b})"


def install(peer, selected):
    p = PROFILES[selected]
    heights = p["heights"]
    terminal = f'TERMINAL = Profile({heights!r}, {p["gaussian"]}, Q("{p["kappa"]}"))'
    replace(peer / "runtime.patch", ((PARENT_INSTALLATION, terminal),))
    replace(peer / "receipt.py", (
        ("assert cost == 318292011 and premium == 515",
         f'assert cost == {p["total"]} and premium == {p["premium"]}'),
        ("(517115, 490950)", repr(p["floors"])),
        ('older = Q(".00389821412325")', 'older = Q(".00389846")'),
        ("DEBIT = Q(64939, 2**19)", "DEBIT = Q(64934, 2**19)"),
        ("    gain = TERMINAL.kappa - older",
         "    gain = TERMINAL.kappa - older\n"
         "    assert TERMINAL.kappa > GAUSSIAN_C - Q(64939, 524288 * 18845936) - Q(5, 10**18)"),
        ("assert gain == Q(79971, 500000000000000)", f'assert gain == {q(p["gain"])}'),
        ("max(heights[-1].bit_length() for heights in (ENTRY.rank_logs, TERMINAL.rank_logs)) <= 20",
         "max(h.bit_length() for h in (*ENTRY.rank_logs, ENTRY.complex_log, *TERMINAL.rank_logs, TERMINAL.complex_log)) <= 20"),
    ))
    if selected == "460":
        replace(peer / "receipt.py", (
            ('max(h.bit_length() for h in (*ENTRY.rank_logs, ENTRY.complex_log, *TERMINAL.rank_logs, TERMINAL.complex_log)) <= 20',
             'max(h.bit_length() for h in (*ENTRY.rank_logs, ENTRY.complex_log, *TERMINAL.rank_logs, TERMINAL.complex_log)) <= 25'),
            ('    setup = native_clock()',
             '    setup = native_clock()\n'
             '    # Reprice the larger source-specific serial installation with\n'
             '    # 2**40 extra actions; do not claim the old portable trace.\n'
             '    w, n = 2**38, 2**68 + 2**40\n'
             '    hh = 2*w + 2\n'
             '    lookup = 8 * (4*w*n) * 512 * 128\n'
             '    local = 2**16*(hh+4)*(7*hh+9) + 8*2**16*(hh+4)**2\n'
             '    expanded_setup = (n+1)*(lookup+local+2**120)*2**32\n'
             '    assert expanded_setup < 2**228\n'
             '    setup["all_setup"] = expanded_setup'),
        ))
    # For every exterior field, x=M/(4*size)>=x_min.  If x<=256,
    # ceil(x)/x<=256/x_min.  Otherwise m=ceil(x)-1>=256 and
    # ceil(x)/x<(m+1)/m<=257/256.  This leaves the actual period unchanged.
    replace(peer / "positive_debit.py", (
        ("POSITIVE_DEBIT = Q(64939, 524288)", "POSITIVE_DEBIT = Q(64934, 524288)"),
        ("    finite_factor = (",
         "    x_min = Q(scale, 4 * max(targets))\n"
         "    exterior_period = Q(257, 256)\n"
         "    assert 255 < x_min < 256\n"
         "    assert Q(256) / x_min < exterior_period < 1 + 1 / x_min\n"
         "    finite_factor = ("),
        ("        * (1 + Q(4 * max(targets), scale))", "        * exterior_period"),
        ('        "upper_factor": str(finite_factor),',
         '        "upper_factor": str(finite_factor),\n'
         '        "exterior_period_factor": str(exterior_period),'),
    ))
    replace(peer / "independent_price.py", (
        ("TERMINAL.kappa - peer == Q(126694920, 10000000000000000)",
         f'TERMINAL.kappa - peer == {q(p["peer_gain"])}'),
        ("    scale = UPPER_DIVISOR * recipe.ambient // 2\n    upper = (",
         "    scale = UPPER_DIVISOR * recipe.ambient // 2\n"
         "    exterior_period = Q(257, 256)\n"
         "    x_min = Q(scale, 4 * 258)\n"
         "    assert 255 < x_min < 256\n"
         "    assert Q(256) / x_min < exterior_period < 1 + 1 / x_min\n"
         "    upper = ("),
        ("        * (1 + Q(4 * 258, scale))", "        * exterior_period"),
        ("    lower = powers(2, Q(64939, 524288))[0]",
         "    lower = powers(2, Q(64934, 524288))[0]"),
        ('    assert lower - upper > Q("0.000000684423")',
         '    assert lower - upper > Q("0.000000232515772047")\n'
         '    coarse = upper * (1 + 1 / x_min) / exterior_period\n'
         '    assert powers(2, Q(64939, 524288))[0] - coarse > Q("0.000000684423")'),
        ("    prior_scale = 1024 * recipe.ambient",
         "    new_factor_lower = ((1+delta) * exterior_period * powers(scale*LOWER,c)[0]\n"
         "                        * (1+prior_fringe/LOWER+delta) / (1-delta)**4)\n"
         '    assert new_factor_lower - powers(2, Q(64933,524288))[1] > Q("0.000001208067461857")\n'
         '    print("PASS_EXTERIOR_PERIOD_DEBIT", "257/256", "64934/524288")\n'
         "    prior_scale = 1024 * recipe.ambient"),
    ))
    replace(peer / "verify.py", ((
        '"check_stage_seam.py", "check_ordinary_floor.py"',
        '"check_scaled.py", "check_ordinary_floor.py"',
    ), (
        '        if scope == "product":\n            product(runtime)\n            return',
        '        if scope == "product":\n'
        '            import fcntl\n'
        '            import os\n'
        '            lock_path = Path(os.environ.get("P104_PHYSICAL_PRODUCT_LOCK", '
        '"/tmp/p104-toiky-0039/physical-product.lock"))\n'
        '            lock_path.parent.mkdir(parents=True, exist_ok=True)\n'
        '            with lock_path.open("a+b") as lock:\n'
        '                fcntl.flock(lock.fileno(), fcntl.LOCK_EX)\n'
        '                try:\n'
        '                    product(runtime)\n'
        '                finally:\n'
        '                    fcntl.flock(lock.fileno(), fcntl.LOCK_UN)\n'
        '            return',
    ), (
        '                check=True,\n                capture_output=True,',
        '                check=False,\n                capture_output=True,',
    ), (
        '            if name == "receipt.py":',
        '            if out.returncode:\n'
        '                print(out.stdout, end="")\n'
        '                print(out.stderr, end="", file=sys.stderr)\n'
        '                raise RuntimeError(f"{name} failed with status {out.returncode}")\n'
        '            if name == "receipt.py":',
    )))

    # Retain the parent's literal source-bound calendar checks.  Only its
    # profile-specific expectations change; no fixture or predicate is removed.
    for name in ("check_cutoff.py", "check_stage_seam.py", "check_ordinary_floor.py", "check_scaled.py", "retune.py"):
        shutil.copyfile(HERE / name, peer / name)
    if selected == "460":
        # The exact trace checks the installed source's expressions and uses
        # algebra for terminal powers, which are too large for routine CI.
        shutil.copyfile(HERE / "check_cutoff_symbolic.py", peer / "check_cutoff.py")
    replace(peer / "check_cutoff.py", ((
        "assert heights == (1024, 490950)",
        f'assert heights == (1024, {p["gaussian"]})',
    ),))
    replace(peer / "check_ordinary_floor.py", (
        ("TERMINAL.rank_logs==(8192,124649,524288) and TERMINAL.complex_log==490950",
         f'TERMINAL.rank_logs=={heights!r} and TERMINAL.complex_log=={p["gaussian"]}'),
        ("(a[-1].rank_log,b[-1].rank_log)==(1024,490950)",
         f'(a[-1].rank_log,b[-1].rank_log)==(1024,{p["gaussian"]})'),
    ))

    pins_path = peer / "SOURCES.json"
    pins = json.loads(pins_path.read_bytes())
    if pins["runtime_images"]["installations.py"]["after"] != "c1bba07dfcf95f7a494e59d6e4de85b4d4537c144f0bcf6f7a1a02ecbe832dea":
        raise ValueError("The #8072 runtime image is not the expected parent")
    pins["runtime_images"]["installations.py"]["after"] = p["image_sha"]
    pins["local_sources"]["runtime.patch"] = sha256((peer / "runtime.patch").read_bytes()).hexdigest()
    pins_path.write_text(json.dumps(pins, indent=2) + "\n")

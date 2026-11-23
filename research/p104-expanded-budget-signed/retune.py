"""Install either enlarged-budget profile on the authenticated #8072 source.

The predecessor's physical suppliers and their bookings stay byte-bound; the
charged height envelope, all dependent receipts and literal checks change.
"""
from hashlib import sha256
import json
from pathlib import Path
import shutil

HERE = Path(__file__).resolve().parent
PARENT_INSTALLATION = 'TERMINAL = Profile((8192, 124649, 524288), 490950, Q(".003898214283192"))'

PROFILES = {
    "300": dict(
        kappa=".0038983", heights=(8192, 35682, 566698), gaussian=743589,
        total=358974351, premium=608, floors=(534380, 743589),
        gain="10714601/125000000000000", peer_gain="983863/10000000000000",
        image_sha="51fb3e8b7d6fe1aa7cbd5012eb011f46faa0b676bf69eb007f1ab8ef184a465a",
    ),
    "340": dict(
        kappa=".00389834", heights=(8192, 36220, 575705), gaussian=978582,
        total=413727211, premium=717, floors=(542837, 978582),
        gain="15714601/125000000000000", peer_gain="1383863/10000000000000",
        image_sha="b3063033c0dc82bc8f7c0ebefee3c6c8a598c0d1e975698995f584b0d81a3778",
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
        ('older = Q(".00389821412325")', 'older = Q(".003898214283192")'),
        ("assert gain == Q(79971, 500000000000000)", f'assert gain == {q(p["gain"])}'),
        ("max(heights[-1].bit_length() for heights in (ENTRY.rank_logs, TERMINAL.rank_logs)) <= 20",
         "max(h.bit_length() for h in (*ENTRY.rank_logs, ENTRY.complex_log, *TERMINAL.rank_logs, TERMINAL.complex_log)) <= 20"),
    ))
    replace(peer / "independent_price.py", ((
        "TERMINAL.kappa - peer == Q(126694920, 10000000000000000)",
        f'TERMINAL.kappa - peer == {q(p["peer_gain"])}',
    ),))
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

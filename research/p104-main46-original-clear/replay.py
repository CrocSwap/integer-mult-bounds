"""Rebuild the pinned main-46 edit and replay its native and signed application."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
from shutil import copyfile
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
RECEIPTS = ROOT / "receipts"
BASE = "e1d2756eecf03e146338239fee81772a99ba8d4c"
SOURCE = "https://github.com/CrocSwap/integer-mult-bounds.git"
PACKAGE = Path("research/p104-timed-helper757")
EDITS = ROOT / "inputs/edits7610.json"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def git(checkout, *arguments):
    return subprocess.check_output(["git", "-C", str(checkout), *arguments], timeout=120, text=True).strip()


def command(script, *args, timeout=35):
    result = subprocess.run([sys.executable, "-I", "-B", str(ROOT / script), *map(str, args)],
                            capture_output=True, timeout=timeout)
    if result.returncode:
        sys.stderr.write(result.stderr.decode())
        sys.stderr.write(result.stdout.decode())
        result.check_returncode()
    return result.stdout


def authenticate_7605(checkout):
    require(git(checkout, "rev-parse", "HEAD") == BASE, "Dependency must be exact #7605")
    seen = set()
    for line in (ROOT / "inputs/7605.sha256").read_text().splitlines():
        digest, name = line.split("  ", 1)
        path = Path(name)
        require(path.is_relative_to(PACKAGE) and ".." not in path.parts and path not in seen,
                f"Ambiguous or duplicate input path {name!r}")
        seen.add(path)
        source = checkout / path
        require(source.is_file() and source.resolve() == source, f"Missing or nonliteral path {name}")
        require(sha256(source.read_bytes()).hexdigest() == digest, f"Input hash diverged for {name}")
    actual = {p.relative_to(checkout) for p in (checkout / PACKAGE).rglob("*") if p.is_file()}
    require(actual == seen and len(seen) == 138, "Expected exact #7605 package closure")


def fetch_7605(checkout):
    checkout.mkdir()
    git(checkout, "init", "-q")
    git(checkout, "remote", "add", "source", SOURCE)
    git(checkout, "sparse-checkout", "set", "--no-cone", f"/{PACKAGE}/")
    git(checkout, "fetch", "-q", "--depth=1", "--filter=blob:none", "source", BASE)
    git(checkout, "checkout", "--detach", "-q", BASE)


def same_json(actual, expected):
    require(json.loads(actual) == json.loads(expected.read_bytes()), f"Replay differs from {expected.name}")


def main():
    if sys.version_info[:2] != (3, 12) or not __debug__:
        raise ValueError("Use CPython 3.12 with assertions enabled")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work", type=Path, required=True, help="a new evidence directory")
    parser.add_argument("--source-checkout", type=Path, help="pre-existing exact #7605 checkout")
    parser.add_argument("--finite-only", action="store_true", help="stop after exact finite gates")
    args = parser.parse_args()
    work = args.work.resolve()
    work.mkdir()
    checkout = args.source_checkout.resolve() if args.source_checkout else work / "source-7605"
    if not args.source_checkout:
        fetch_7605(checkout)
    authenticate_7605(checkout)
    src = checkout / PACKAGE
    inputs = work / "finite-inputs"
    inputs.mkdir()
    sources = {
        "word.json.gz": src / "data/word.json.gz",
        "FINAL.json": src / "data/FINAL.json",
        "invoice-new.json": src / "data/invoice-new.json",
        "7113-CALLER.json": src / "retained/role902/bench/inputs/7113-CALLER.json",
        "pricing.py": ROOT / "checks/pricing.py",
        "edits7610.json": EDITS,
    }
    for name, source in sources.items():
        copyfile(source, inputs / name)
    copyfile(inputs / "word.json.gz", inputs / "word7605.json.gz")
    candidate = work / "word.json.gz"
    emitted = command("checks/emit_main46.py", "--source", inputs / "word.json.gz", "--peer-edits", EDITS,
                      "--output", candidate)
    print(emitted.decode(), end="", flush=True)
    exact = command("checks/check_delta.py", "--input-root", inputs, "--candidate", candidate)
    same_json(exact, RECEIPTS / "EXACT.json")
    print(exact.decode(), end="", flush=True)
    phases = command("checks/check_main46_phase.py", "--word", inputs / "word.json.gz", "--engine-root",
                     src / "retained/role902/independent/engines", "--all-columns", timeout=60)
    same_json(phases, RECEIPTS / "PHASE.json")
    print(phases.decode(), end="", flush=True)
    invoice = command("checks/recount_main46.py", "--baseline", inputs, "--candidate", candidate)
    same_json(invoice, RECEIPTS / "INVOICE.json")
    (work / "INVOICE.json").write_bytes(invoice)
    print("PASS exact finite construction, phase and directed invoice", flush=True)
    if args.finite_only:
        return

    overlay = work / "overlay"
    command("application/prepare_overlay.py", "--source-checkout", checkout, "--overlay", overlay,
            "--candidate", candidate, "--peer-edits", EDITS, "--invoice-receipt", work / "INVOICE.json")
    main_module = overlay / "application.py"
    command("application/patch_native.py", main_module, "--output", overlay / "application-checked.py",
            "--receipt", work / "NATIVE-PATCH.json")
    (overlay / "application-checked.py").replace(main_module)
    for file in ("NATIVE.json", "SIGNED.json", "FINAL.json"):
        copyfile(RECEIPTS / file, overlay / "data" / file)
    for stage in ("native", "signed"):
        print(f"RUN complete {stage} application on the frozen word", flush=True)
        print(command("application/run_stage.py", stage, "--overlay", overlay, "--work", work / stage,
                      timeout=500).decode(), end="", flush=True)
    same_json((work / "signed/FINAL.json").read_bytes(), RECEIPTS / "FINAL.json")
    print("PASS full main-46 original-CLEAR conditional application")


if __name__ == "__main__":
    main()

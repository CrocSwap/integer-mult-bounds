"""Materialize one pinned source overlay without bootstrapping native runtime."""
from argparse import ArgumentParser
from hashlib import sha1, sha256
import json
from pathlib import Path
import runpy
import signal
from tarfile import open as tar_open
from tempfile import TemporaryDirectory

HERE = Path(__file__).resolve().parent
INPUTS_SHA = "cacf5d35f0a2c65df8d5b17b7075f6cea5d98be75d473dee1baa31724f319b64"
BASE = "c20a08dc0a79a989e3515068560d5da371c0a2a8"
PROBE_FILES = ("check_cutoff.py", "check_stage_seam.py", "check_ordinary_floor.py")
CHANGED = {"SOURCES.json", "runtime.patch", "receipt.py", "independent_price.py",
           "check_stage_seam.py", "PREDECESSOR-RESULT.json", "RESULT.json"}


def read_unique(pairs):
    result = dict(pairs)
    if len(result) != len(pairs):
        raise ValueError("Repeated source pin")
    return result


def digest(data):
    return sha256(data).hexdigest()


def verify_inputs(package):
    raw = (HERE / "INPUTS.json").read_bytes()
    if digest(raw) != INPUTS_SHA:
        raise ValueError("Source inventory differs")
    pins = json.loads(raw, object_pairs_hook=read_unique)
    if pins["head"] != BASE:
        raise ValueError("Incorrect comparator pin")
    for name, expected in pins["files"].items():
        data = (package / name).read_bytes()
        blob = sha1(f"blob {len(data)}\0".encode() + data).hexdigest()
        if (digest(data), blob, len(data)) != (expected["sha256"], expected["git_blob"], expected["size"]):
            raise ValueError(f"Incorrect source bytes for {name}")
    with tar_open(package / "peer8057.tar.gz") as archive:
        if sum(item.size for item in archive) > 32 * 1024 * 1024:
            raise ValueError("Archive exceeds the source-only capacity")


def inventory(root):
    return {p.relative_to(root).as_posix(): digest(p.read_bytes())
            for p in sorted(root.rglob("*")) if p.is_file()}


def materialize(package, tree):
    core = runpy.run_path(str(package / "verify.py"))
    peer = core["restore"](tree)
    runpy.run_path(str(package / "prepare.py"))["materialize"](peer)
    for name in PROBE_FILES:
        (peer / name).write_bytes((package / name).read_bytes())

    initial = inventory(peer)
    profile = runpy.run_path(str(HERE / "profile_source.py"))["patch_profile"](peer)
    runpy.run_path(str(HERE / "price_source.py"))["patch_prices"](peer)
    runpy.run_path(str(HERE / "seam_source.py"))["patch_stage_checks"](peer)
    (peer / "RESULT.json").rename(peer / "PREDECESSOR-RESULT.json")
    final = inventory(peer)
    changed = {name for name in initial.keys() | final.keys() if initial.get(name) != final.get(name)}
    if changed != CHANGED:
        raise ValueError(f"Unexpected changed prepared paths: {sorted(changed)}")
    for name in ("receipt.py", "independent_price.py", *PROBE_FILES, "verify.py", "bootstrap.py"):
        compile((peer / name).read_bytes(), name, "exec")
    assert not (peer / "RESULT.json").exists()
    assert (peer / "runtime.patch").read_text().count('Q(".003900857269150")') == 1
    result = dict(
        scope="Exact prepared sources and derived installation image hash only",
        parent=BASE,
        projected_kappa="0.003900857269150",
        physical_profile=profile,
        changed_prepared_paths={name: {"before": initial.get(name), "after": final.get(name)}
                                for name in sorted(changed)},
        prepared_peer_path=peer.relative_to(tree).as_posix(),
        file_count=len(final),
        native_bootstrap="not run",
        candidate_RESULT="not generated",
    )
    (tree / "SOURCE-ASSEMBLY.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result


def timeout(_signal, _frame):
    raise TimeoutError("The one-package source preparation reached its 45-second cap")


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--package-root", required=True, type=Path)
    parser.add_argument("--output", type=Path, help="Persist the exact prepared source in a new directory")
    args = parser.parse_args()
    assert __debug__
    package = args.package_root.resolve()
    output = args.output.resolve() if args.output else None
    if output and output.exists():
        parser.error("--output must name a new directory")
    signal.signal(signal.SIGALRM, timeout)
    signal.alarm(45)
    try:
        verify_inputs(package)
        with TemporaryDirectory(prefix="k7-source-overlay-", dir=output.parent if output else None) as temp:
            tree = Path(temp) / "prepared"
            result = materialize(package, tree)
            if output:
                tree.rename(output)
        print(json.dumps(result, indent=2, sort_keys=True))
    finally:
        signal.alarm(0)


if __name__ == "__main__":
    main()

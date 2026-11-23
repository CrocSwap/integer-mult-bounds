"""Assemble the single sharper-period candidate from exact frozen public inputs."""
from argparse import ArgumentParser
from hashlib import sha256
import json
from pathlib import Path
import runpy
import signal
from tempfile import TemporaryDirectory

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PEER = "c20a08dc0a79a989e3515068560d5da371c0a2a8"
PINS = {
    "r415/overlay/assemble.py": "0a5311eb25e889155d025a689236a3e5a434ec82d47a905fdf321eaf6a95d828",
    "r415/overlay/ASSEMBLY.json": "a9b1fc38145ee605f35feb1277be316919e74c6747355c4c199cd3430b2dfab9",
    "r417/setup-receipt/check_patch.py": "c9f034036518f4fb9329d7e151f43d238efeab3c20e5f2c8b3e4c1b07a157b7e",
    "r417/setup-receipt/RECEIPT.json": "a690d662d0c9e137a6673d1c9c8dac24d2183e8ccd612b09ab13eb01a1c9d99e",
    "r419/cross-price/RECEIPT.json": "f2f2c6ffb164084c3e977a1b7699754918ed1e15bee585c1285dbae3d7afb42d",
}
CHANGED = {"runtime.patch", "SOURCES.json", "receipt.py", "independent_price.py",
           "positive_debit.py", "check_stage_seam.py"}


def materialize(root, package, tree):
    for name, expected in PINS.items():
        if sha256((root / name).read_bytes()).hexdigest() != expected:
            raise ValueError(f"Incorrect inherited exact input {name}")
    prior = runpy.run_path(str(root / "r415/overlay/assemble.py"))
    prior["verify_inputs"](package)
    result = prior["materialize"](package, tree)
    if result != json.loads((root / "r415/overlay/ASSEMBLY.json").read_bytes()):
        raise ValueError("The frozen tariff assembly differs")
    peer = tree / result["prepared_peer_path"]
    old = prior["inventory"](peer)

    correct = runpy.run_path(str(root / "r417/setup-receipt/check_patch.py"))["check"]
    evidence, corrected = correct((peer / "receipt.py").read_bytes())
    if evidence != json.loads((root / "r417/setup-receipt/RECEIPT.json").read_bytes()):
        raise ValueError("The exact setup receipt correction differs")
    (peer / "receipt.py").write_bytes(corrected)
    profile = runpy.run_path(str(HERE / "profile.py"))["patch_profile"](peer)
    runpy.run_path(str(HERE / "price.py"))["patch_price"](peer)
    runpy.run_path(str(HERE / "seam.py"))["patch_stage_checks"](peer)

    new = prior["inventory"](peer)
    actual_changed = {name for name in old.keys() | new.keys() if old.get(name) != new.get(name)}
    if actual_changed != CHANGED:
        raise ValueError(f"Unexpected prepared source changes: {sorted(actual_changed)}")
    for name in ("receipt.py", "positive_debit.py", "independent_price.py", "check_stage_seam.py",
                 "verify.py", "bootstrap.py"):
        compile((peer / name).read_bytes(), name, "exec")
    assert "RESULT.json" not in new
    receipt = dict(
        scope="Exact positive-period source assembly; native replay unrun",
        original_peer=PEER,
        projected_kappa="0.003900857312000",
        prior_projected_kappa=result["projected_kappa"],
        prepared_peer_path=result["prepared_peer_path"],
        physical_profile=profile,
        changed_from_frozen={name: {"before": old[name], "after": new[name]}
                             for name in sorted(actual_changed)},
        native_bootstrap="not run", candidate_RESULT="not generated",
    )
    (tree / "PERIOD-ASSEMBLY.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    return receipt


def timeout(_signal, _frame):
    raise TimeoutError("The source assembly reached its 45-second cap")


def main():
    assert __debug__
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--package-root", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    output = args.output.resolve() if args.output else None
    if output and output.exists():
        parser.error("--output must be fresh")
    signal.signal(signal.SIGALRM, timeout)
    signal.alarm(45)
    try:
        with TemporaryDirectory(prefix="period-source-", dir=output.parent if output else None) as tmp:
            tree = Path(tmp) / "prepared"
            result = materialize(args.root.resolve(), args.package_root.resolve(), tree)
            if output:
                tree.rename(output)
        print(json.dumps(result, indent=2, sort_keys=True))
    finally:
        signal.alarm(0)


if __name__ == "__main__":
    main()

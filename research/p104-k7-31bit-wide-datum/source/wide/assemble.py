"""Apply the 31-bit profile, w=2^41 datum width and paid child sum 2925 in one layer.

Input: the complete #8098 domain assembly (exact head fae237c8aee774bb2256d4e394fed9f3934147c2).
Structure follows #8098's source/domain/assemble.py.
"""

from argparse import ArgumentParser
from hashlib import sha256
import json
import os
from pathlib import Path
import runpy
import shutil
import signal
from subprocess import run
from tempfile import TemporaryDirectory


HERE = Path(__file__).resolve().parent
PEER = Path("research/frequency-weighted-native-multiplier")
INSTALLATIONS = Path("research/tiered-native-multiplier/installations.py")
PINS = {
    "receipt.py": "7720731fde6b8c2793bcd64d58d5d00e60eb05a22197fde12a9da927d89999bd",
    "independent_price.py": "f6d3533e7bae8f7cb7b4d6d8e70885ff79186398c72c96c100254c673f102cdc",
    "check_stage_seam.py": "0e0d9f2986c77285f1704a97f0afd8a24b420c48816dc9680df1335c42678e62",
    "check_ordinary_floor.py": "9c60d0ff1d88a0981625ae1c998638a8ad28d7ce0d3ffa01eba141cbbb99c3a8",
    "check_cutoff.py": "e0c7e48d4469844de861e1e4ba83eed9c5ccd58e5c9f480c4a6a82da7524e31c",
    "runtime.patch": "81223960c0d5cddbca86cba29498c436bb58ac9b327897e535b245fa7dacdd39",
    "SOURCES.json": "fc44126841019e6356387c2f938171ce74f69a2f713d2cf3ce659c1a6f4f4fa4",
}
ADDED = ("check_wide_setup.py",)
PEER_HEAD = "fae237c8aee774bb2256d4e394fed9f3934147c2"
PREIMAGE = "1c6978b8c7d136ef87191512d9ab9eb3dda8a818844244b96cb165d46d97b1df"
OLD_IMAGE = "2d55f0269164878a6507c6756f2f27ccd6b3a6d2cbd5b3232e89ebc8e1b7a422"
OLD_RATE = "0.003900862349168"
NEW_RATE = "0.003900866740647"
SELECTOR = (b'TERMINAL = Profile((8192, 63614, 1005821, 15903360, 251454111, 268435455), 52270, '
            b'Q(".003900862349168"), Q(1, 256))')
NEW_SELECTOR = (b'TERMINAL = Profile((16096, 254464, 4023296, 63614464, 2079574939, 2147483647), 52367, '
                b'Q(".003900866740647"), Q(1, 256))')


def digest(data):
    return sha256(data).hexdigest()


def authenticated(path, expected):
    raw = path.read_bytes()
    if digest(raw) != expected:
        raise ValueError(f"Unexpected frozen source at {path.name!r}")
    return raw


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate manifest key {key!r}")
        result[key] = value
    return result


def replace_unique(text, before, after):
    if text.count(before) != 1:
        raise ValueError(f"Expected one source anchor, found {text.count(before)}: {before[:110]!r}")
    return text.replace(before, after, 1)


def image(preimage, patch, stage):
    with TemporaryDirectory(prefix="selector-", dir=stage) as temporary:
        target = Path(temporary) / "installations.py"
        target.write_bytes(preimage)
        env = dict(os.environ, GIT_CEILING_DIRECTORIES=str(stage))
        run(["git", "apply", "--no-index", "--include=installations.py", "--whitespace=nowarn", "-"],
            cwd=temporary, env=env, input=patch, check=True, timeout=10)
        return target.read_bytes()


def inventory(root):
    files = {}
    for path in root.rglob("*"):
        if path.is_symlink():
            raise ValueError(f"A source symlink is outside this assembly: {path.relative_to(root)}")
        if path.is_file():
            files[path.relative_to(root).as_posix()] = digest(path.read_bytes())
    return files


def materialize(frozen, stage):
    prior = {name: authenticated(frozen / PEER / name, pin) for name, pin in PINS.items()}
    manifest_raw = (HERE / "PREIMAGE.json").read_bytes()
    frozen_manifest = json.loads(manifest_raw, object_pairs_hook=unique_object)
    before = inventory(frozen)
    if (frozen_manifest["head"] != PEER_HEAD or not frozen_manifest["source_only"]
            or before != frozen_manifest["files"] or len(before) != 94):
        raise ValueError("The complete materialized #8098 domain inventory differs")
    preimage = authenticated(frozen / INSTALLATIONS, PREIMAGE)
    baseline = image(preimage, prior["runtime.patch"], stage)
    if digest(baseline) != OLD_IMAGE:
        raise ValueError("The installed #8098 image differs")
    patch = replace_unique(prior["runtime.patch"], b"+" + SELECTOR, b"+" + NEW_SELECTOR)
    installed = image(preimage, patch, stage)
    if installed != replace_unique(baseline, SELECTOR, NEW_SELECTOR):
        raise ValueError("The selector patch made another change to installations.py")
    compile(installed, "installations.py", "exec")
    manifest = json.loads(prior["SOURCES.json"], object_pairs_hook=unique_object)
    pins = manifest["runtime_images"]["installations.py"]
    if pins != {"before": PREIMAGE, "after": OLD_IMAGE} or manifest["local_sources"]["runtime.patch"] != PINS["runtime.patch"]:
        raise ValueError("The old selector pins differ")
    pins["after"] = digest(installed)
    manifest["local_sources"]["runtime.patch"] = digest(patch)
    edits = runpy.run_path(str(HERE / "edits.py"))["EDITS"]
    changed = {
        "runtime.patch": patch,
        "SOURCES.json": (json.dumps(manifest, indent=2) + "\n").encode(),
    }
    for name, replacements in edits.items():
        text = prior[name].decode()
        for anchor, replacement in replacements:
            text = replace_unique(text, anchor, replacement)
        compile(text, name, "exec")
        changed[name] = text.encode()
    if set(changed) != set(PINS):
        raise ValueError("The changed source inventory differs")
    for name in ADDED:
        raw = (HERE / name).read_bytes()
        compile(raw, name, "exec")
        changed[name] = raw
    old_result = (PEER / "RESULT.json").as_posix()
    candidate = stage / "candidate"
    shutil.copytree(frozen, candidate)
    for name, raw in changed.items():
        (candidate / PEER / name).write_bytes(raw)
    after = inventory(candidate)
    differences = {p for p in before.keys() | after.keys() if before.get(p) != after.get(p)}
    expected = {(PEER / name).as_posix() for name in changed}
    if differences != expected or old_result in after:
        raise ValueError("An unexpected source changed or a stale receipt survived")
    return candidate, {
        "scope": "Frozen source assembly and exact selector image only. Installed replay unrun.",
        "peer_head": PEER_HEAD,
        "complete_preimage_manifest_sha256": digest(manifest_raw),
        "preimage_terminal_kappa": OLD_RATE,
        "projected_terminal_kappa": NEW_RATE,
        "projected_delta": "4391479/1000000000000000",
        "datum_width_bits": "2^41",
        "ordinary_child_geometric_sum": 2925,
        "installation_preimage_sha256": PREIMAGE,
        "old_installation_sha256": OLD_IMAGE,
        "candidate_installation_sha256": digest(installed),
        "changed": {p: {"before": before.get(p), "after": after[p]} for p in sorted(expected)},
        "candidate_RESULT": "not generated",
    }


def timeout(_signal, _frame):
    raise TimeoutError("Source assembly reached the 45-second cap")


def main():
    if not __debug__:
        raise RuntimeError("Run with assertions enabled")
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--frozen", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    frozen, output = args.frozen.resolve(), args.output.resolve()
    if args.output.is_symlink() or output.exists() or output.is_relative_to(frozen):
        parser.error("--output must be a fresh path outside the frozen tree")
    signal.signal(signal.SIGALRM, timeout)
    signal.alarm(45)
    try:
        with TemporaryDirectory(prefix="wide-datum-source-", dir=output.parent) as temporary:
            candidate, receipt = materialize(frozen, Path(temporary))
            (candidate / "WIDE-ASSEMBLY.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
            candidate.rename(output)
        print(json.dumps(receipt, indent=2, sort_keys=True))
    finally:
        signal.alarm(0)


if __name__ == "__main__":
    main()

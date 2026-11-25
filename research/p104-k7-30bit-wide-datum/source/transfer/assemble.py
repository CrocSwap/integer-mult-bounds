"""Apply the exact child tariff transfer to the frozen #8097 source."""

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
    "receipt.py": "57bbecc48227e3bf938920221d0ec4b260452031c9afbb18ee28fbccda096c7b",
    "independent_price.py": "b250c6169229b33b7a50bb6921a48cda3a47ad4fa1d0e88fe7289d4f469da79b",
    "check_stage_seam.py": "f65ba986ef88b58c2e88fd43fdf40043d9b47f9952a83cb8277881776c914183",
    "runtime.patch": "3a7653a0a3a508587870712076737467501b9e69a5ec8b9ffbf4ac50399e5379",
    "SOURCES.json": "f5690dee0461295b8312f0611805dc5c837a4929fd8b6e4df51a9068fcaa2b0d",
}
PEER_HEAD = "e1c251401fe254909ac7e7bf2c773b921a1b6b57"
FULL_PREIMAGE = "48fe570b5c7ad6099cd6e886df880a959a3fe6582cb18dad44509d26e2757291"
SCREEN = "923a6c8fc1e15f6ca087b4de5d93e40bc49a889708f97e2dc7718f66053747ca"
PREIMAGE = "1c6978b8c7d136ef87191512d9ab9eb3dda8a818844244b96cb165d46d97b1df"
OLD_IMAGE = "cbf85060a63dc4433c706d71ec582b0ebe6a09bbe26963ff78acb4c08e5edd92"
OLD_RESULT = "2f4faa6648592f589df22a8a0a07ba6856d20786294a44a7776c7d6e0efa14a5"
OLD_RATE = "0.003900862325217"
NEW_RATE = "0.003900862339776"
SELECTOR = b'TERMINAL = Profile((8192, 63614, 1005821, 15903360, 251454111, 268435455), 52270, Q(".003900862325217"), Q(1, 256))'
NEW_SELECTOR = SELECTOR.replace(b".003900862325217", b".003900862339776")


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
    for path in (root / "research").rglob("*"):
        if path.is_symlink():
            raise ValueError(f"A source symlink is outside this assembly: {path.relative_to(root)}")
        if path.is_file():
            files[path.relative_to(root).as_posix()] = digest(path.read_bytes())
    return files


def materialize(frozen, stage):
    prior = {name: authenticated(frozen / PEER / name, pin) for name, pin in PINS.items()}
    frozen_manifest = json.loads(authenticated(HERE / "PREIMAGE.json", FULL_PREIMAGE),
                                 object_pairs_hook=unique_object)
    before = inventory(frozen)
    if not frozen_manifest["source_only"] or before != frozen_manifest["files"] or len(before) != 93:
        raise ValueError("The complete materialized #8097 source inventory differs")
    screen = json.loads(authenticated(HERE / "SCREEN.json", SCREEN), object_pairs_hook=unique_object)
    if (screen["binding"], screen["proposed_tariff"], screen["tested_debit"]) != (
        "ordinary", "10981863/4703998", "1414569/1048576"
    ):
        raise ValueError("The exact tariff screen differs")
    preimage = authenticated(frozen / INSTALLATIONS, PREIMAGE)
    baseline = image(preimage, prior["runtime.patch"], stage)
    if digest(baseline) != OLD_IMAGE:
        raise ValueError("The installed #8097 image differs")
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
    old_result = (PEER / "RESULT.json").as_posix()
    if old_result in before:
        authenticated(frozen / old_result, OLD_RESULT)
    candidate = stage / "candidate"
    shutil.copytree(frozen / "research", candidate / "research")
    (candidate / old_result).unlink(missing_ok=True)
    for name, raw in changed.items():
        (candidate / PEER / name).write_bytes(raw)
    after = inventory(candidate)
    differences = {p for p in before.keys() | after.keys() if before.get(p) != after.get(p)}
    expected = {(PEER / name).as_posix() for name in changed}
    if differences - {old_result} != expected or old_result in after:
        raise ValueError("An unexpected source changed or a stale receipt survived")
    return candidate, {
        "scope": "Frozen source assembly and exact selector image only. Installed replay unrun.",
        "peer_head": PEER_HEAD,
        "complete_preimage_manifest_sha256": FULL_PREIMAGE,
        "screen_sha256": SCREEN,
        "baseline_terminal_kappa": OLD_RATE,
        "projected_terminal_kappa": NEW_RATE,
        "projected_delta": "14559/1000000000000000",
        "inherited_archive_result_sha256": OLD_RESULT,
        "comparator_result_sha256": screen["inputs_sha256"]["peer/RESULT.json"],
        "installation_preimage_sha256": PREIMAGE,
        "old_installation_sha256": OLD_IMAGE,
        "candidate_installation_sha256": digest(installed),
        "changed": {p: {"before": before[p], "after": after[p]} for p in sorted(expected)},
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
        with TemporaryDirectory(prefix="exact-tariff-transfer-source-", dir=output.parent) as temporary:
            candidate, receipt = materialize(frozen, Path(temporary))
            (candidate / "TRANSFER-ASSEMBLY.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
            candidate.rename(output)
        print(json.dumps(receipt, indent=2, sort_keys=True))
    finally:
        signal.alarm(0)


if __name__ == "__main__":
    main()

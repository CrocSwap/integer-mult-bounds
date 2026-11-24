"""Apply the narrower quotient domain to the frozen #8098 source."""

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
    "receipt.py": "05976149ac2399da4da52a394c4f8b7e13af5c97f92419fd2bfc58cb96dfd880",
    "independent_price.py": "12481437e296aebf3172b1eeda8d73ff85b9e87cb7c221d4a618e726ec0319d7",
    "check_stage_seam.py": "408e1980656a3a986343fd344ad4960f80e0bf04ee3ce9b62d94462ff86c430b",
    "runtime.patch": "b3702cbac622d3803b8761832c4c741f323c97fdd4c2f815011a418cbce55462",
    "SOURCES.json": "a8b3a3cf67ce3448b5115a75250532888a8e91fc9ce60d804d2b91889648180f"
}
PEER_HEAD = "c7d4441c5e4406bff4a79576cf6b2ce0a596390a"
FULL_PREIMAGE = "112293072412fd884f8c5b75f8d0d1170dd2988acd8a9824e704a7ef0344e80d"
SCREEN = "cb0c087e9814d17af15fae513e739dc03b21a1c8978adc02f5ee541cdb2ae23c"
PREIMAGE = "1c6978b8c7d136ef87191512d9ab9eb3dda8a818844244b96cb165d46d97b1df"
OLD_IMAGE = "d34b860c4c35aeb302767216bf58dd9da627fe2b1b2b646fd70d6a544563648e"
OLD_RATE = "0.003900862339776"
NEW_RATE = "0.003900862349161"
SELECTOR = b'TERMINAL = Profile((8192, 63614, 1005821, 15903360, 251454111, 268435455), 52270, Q(".003900862339776"), Q(1, 256))'
NEW_SELECTOR = SELECTOR.replace(b".003900862339776", b".003900862349161")


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
    frozen_manifest = json.loads(authenticated(HERE / "PREIMAGE.json", FULL_PREIMAGE),
                                 object_pairs_hook=unique_object)
    before = inventory(frozen)
    if frozen_manifest["head"] != PEER_HEAD or not frozen_manifest["source_only"] or before != frozen_manifest["files"] or len(before) != 93:
        raise ValueError("The complete materialized #8098 source inventory differs")
    screen = json.loads(authenticated(HERE / "SCREEN.json", SCREEN), object_pairs_hook=unique_object)
    for bits in ("112", "192"):
        directed = screen["directed_results"][bits]
        expected = {"peer8098": (1412105, 1412104), "N_at_least_16": (1411929, 1411928)}
        for name, endpoints in expected.items():
            row = directed[name]
            if (row["first_funded_tick"], row["preceding_tick_rejected"]) != endpoints:
                raise ValueError("The exact directed tariff screen differs")
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
        "complete_preimage_manifest_sha256": FULL_PREIMAGE,
        "screen_sha256": SCREEN,
        "baseline_terminal_kappa": OLD_RATE,
        "projected_terminal_kappa": NEW_RATE,
        "projected_delta": "9385/1000000000000000",
        "comparator_result_sha256": screen["pinned_inputs"]["package/RESULT.json"],
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
        with TemporaryDirectory(prefix="narrower-tariff-domain-source-", dir=output.parent) as temporary:
            candidate, receipt = materialize(frozen, Path(temporary))
            (candidate / "DOMAIN-ASSEMBLY.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
            candidate.rename(output)
        print(json.dumps(receipt, indent=2, sort_keys=True))
    finally:
        signal.alarm(0)


if __name__ == "__main__":
    main()

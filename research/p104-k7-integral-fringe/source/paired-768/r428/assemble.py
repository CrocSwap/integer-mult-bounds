"""Apply the integral-fringe change solely to an authenticated Round 420 tree."""

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
    "positive_debit.py": "89e715555dee209867b45b0a763f207dd0a479f8bc9fbf542b73fa4048415def",
    "receipt.py": "3aca2167fbc5995cb3d928d0f08e087be0dfa4019dd689538d1e101366118b5e",
    "independent_price.py": "267fdaa92130165bd42c716a6579c3c25ea7424be654118d2a386ce6f1676b6e",
    "check_stage_seam.py": "57d5ac6ac268fc07fbd92447abf297a2e2f4ea4f5a6c2da95d0abb1ca75d08ca",
    "runtime.patch": "77dd66e595835c68a4d6a1df2e45e538a97d2fe046b2c18726281854af5b151e",
    "SOURCES.json": "bc16e0da6b59d42f22b81baeebc0ef50ed96a9e265922e678b0be72e5f22fe6c",
}
PREIMAGE = "1c6978b8c7d136ef87191512d9ab9eb3dda8a818844244b96cb165d46d97b1df"
OLD_IMAGE = "c5d83f8c6acdab6828185bc6bb67537cf320ba79ab177f9da535edae7b5af72e"
OLD_RESULT = "ad6ca3a20b296033ed586821db1f42ffee2d9b5cd9723dbcb1720605f143f609"
OLD_RATE = "0.003900857312000"
NEW_RATE = "0.003900857312674"
SELECTOR = b'TERMINAL = Profile((31808, 502922, 7951907, 125730703, 134217727), 208653, Q(".003900857312000"), Q(1, 256))'
NEW_SELECTOR = SELECTOR.replace(b".003900857312000", b".003900857312674")


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
    preimage = authenticated(frozen / INSTALLATIONS, PREIMAGE)
    baseline = image(preimage, prior["runtime.patch"], stage)
    if digest(baseline) != OLD_IMAGE:
        raise ValueError("The installed Round 420 image differs")
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
        for before, after in replacements:
            text = replace_unique(text, before, after)
        compile(text, name, "exec")
        changed[name] = text.encode()
    if set(changed) != set(PINS):
        raise ValueError("The changed source inventory differs")
    before = inventory(frozen)
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
        "baseline_terminal_kappa": OLD_RATE,
        "projected_terminal_kappa": NEW_RATE,
        "projected_delta": "337/500000000000000",
        "predecessor_result_sha256": OLD_RESULT,
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
        with TemporaryDirectory(prefix="fringe-source-", dir=output.parent) as temporary:
            candidate, receipt = materialize(frozen, Path(temporary))
            (candidate / "FRINGE-ASSEMBLY.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
            candidate.rename(output)
        print(json.dumps(receipt, indent=2, sort_keys=True))
    finally:
        signal.alarm(0)


if __name__ == "__main__":
    main()

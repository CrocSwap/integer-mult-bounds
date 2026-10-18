#!/usr/bin/env python3
"""Equivalence, rejection and pin controls for production joint-dual replay.

Read-only by default. Timing is not a pass gate; see benchmark.py / RESULT.json.
Under -O this script only checks that production and baseline modules refuse to
load (historical assert policy); full equivalence runs with assertions enabled.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
EXPERIMENTS = ROOT / "scripts" / "experiments"

BASE_COMMIT = "0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2"
ORIGINAL_BLOB = "a4897e5ecb5c92404257e85c8558e7264f0ef0bb"
ORIGINAL_SHA256 = "1a572dbb33faba6695b3293768a7e61392d11cb4c2d5f708eedcd2cb95d0aff9"
WORDS = {23: ROOT / "certificates/joint-dual-word-23.json.gz",
         25: ROOT / "certificates/joint-dual-word-25.json.gz"}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, f"missing module {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def digest_file(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def unique_object(pairs):
    out = {}
    for key, value in pairs:
        require(key not in out, f"duplicate JSON key: {key}")
        out[key] = value
    return out


def load_json_unique(path: Path):
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_object)


def check_baseline_bytes() -> None:
    original = subprocess.check_output(
        ["git", "show", f"{BASE_COMMIT}:scripts/experiments/binary_frame_replay.py"],
        cwd=ROOT,
    )
    require(sha256(original).hexdigest() == ORIGINAL_SHA256, "base binary_frame_replay.py sha256 drift")
    require(
        subprocess.check_output(
            ["git", "rev-parse", f"{BASE_COMMIT}:scripts/experiments/binary_frame_replay.py"],
            cwd=ROOT,
        )
        .decode()
        .strip()
        == ORIGINAL_BLOB,
        "base binary_frame_replay.py blob drift",
    )
    require(
        (PACKAGE / "baseline.py").read_bytes() == original,
        "baseline.py must be an exact copy of the base-commit source",
    )
    require(
        digest_file(EXPERIMENTS / "binary_frame_replay.py") != ORIGINAL_SHA256,
        "production source unexpectedly unchanged",
    )


def literal_expected(triples, common, triple):
    return sum(
        1 << i
        for i, t in enumerate(triples)
        if common in t and not (set(t) & (set(triple) - {common}))
    )


def check_mask_identity(production) -> int:
    checked = 0
    for h, path in WORDS.items():
        import gzip
        word = json.loads(gzip.decompress(path.read_bytes()))
        triples, center, pair, destinations, lookup = production._containment_tables(h)
        require(len(triples) == word["v"], f"triple count mismatch at h={h}")
        for s, g, common, triple in word["outputs"]:
            mask = production._expected_mask(center, pair, common, triple)
            require(mask == literal_expected(triples, common, triple),
                    f"mask nonequivalence at h={h} output role {s}")
            if len(triple) == 1:
                require(destinations[common] == [i for i, t in enumerate(triples) if common in t],
                        f"destination list drift at h={h} common={common}")
            else:
                require(lookup[tuple(triple)] == triples.index(tuple(triple)),
                        f"lookup drift at h={h}")
            checked += 1
    return checked


def check_replay_equivalence(baseline, production) -> list[dict]:
    stored = load_json_unique(ROOT / "certificates/joint-dual-compiler.json")
    rows = []
    for h, path in WORDS.items():
        old = baseline.replay(path)
        new = production.replay(path)
        require(old == new, f"replay receipt differs at h={h}")
        require(json.loads(json.dumps(new)) == stored["axes"][str(h)]["replay"],
                f"replay differs from compiler certificate at h={h}")
        rows.append(new)
    return rows


def check_rejections(baseline, production) -> None:
    import gzip
    with tempfile.TemporaryDirectory(prefix="joint-dual-replay-prod-") as tmp:
        dest = Path(tmp) / "bad-word.json.gz"
        raw = json.loads(gzip.decompress(WORDS[23].read_bytes()))
        raw["outputs"] = raw["outputs"][:-1]  # drop a paid output
        dest.write_bytes(gzip.compress((json.dumps(raw, separators=(",", ":")) + "\n").encode()))
        for eng, name in ((baseline, "baseline"), (production, "optimized")):
            try:
                eng.replay(dest)
            except (AssertionError, ValueError):
                pass
            else:
                raise AssertionError(f"{name} accepted truncated outputs")


def check_temp_corruption(production) -> None:
    with tempfile.TemporaryDirectory(prefix="joint-dual-replay-mutant-") as tmp:
        dest = Path(tmp) / "binary_frame_replay.py"
        shutil.copy2(EXPERIMENTS / "binary_frame_replay.py", dest)
        text = dest.read_text(encoding="utf-8")
        # Drop one pair-mask update so expected masks undercount; symbol assert fails.
        mutated = text.replace("pair[c][x]|=bit", "pass", 1)
        require(mutated != text, "mutation did not edit production source text")
        dest.write_text(mutated, encoding="utf-8")
        mutant = load_module(dest, "binary_frame_replay_mutant")
        try:
            mutant.replay(WORDS[23])
            raise AssertionError("pair-mask omission mutant accepted h=23 replay")
        except AssertionError as exc:
            require("assert" in str(exc).lower() or str(exc) == "", str(exc))
        # Live production path still matches the recorded receipt.
        production.replay(WORDS[23])


def check_pin_consistency() -> None:
    freeze = load_json_unique(ROOT / "research/joint-dual/SOURCE.json")
    require(
        freeze["files"]["scripts/experiments/binary_frame_replay.py"]
        == digest_file(EXPERIMENTS / "binary_frame_replay.py"),
        "SOURCE.json pin does not match working binary_frame_replay.py",
    )
    kappa = load_json_unique(ROOT / "certificates/joint-dual-kappa.json")
    require(
        kappa["local_source_sha256"]["scripts/experiments/binary_frame_replay.py"]
        == digest_file(EXPERIMENTS / "binary_frame_replay.py"),
        "joint-dual-kappa local pin drift",
    )
    require(
        kappa["source_manifest_sha256"] == digest_file(ROOT / "research/joint-dual/SOURCE.json"),
        "joint-dual-kappa source_manifest_sha256 drift",
    )
    skip = load_json_unique(ROOT / "certificates/skip-frame-kappa.json")
    require(
        skip["local_source_sha256"]["scripts/experiments/binary_frame_replay.py"]
        == digest_file(EXPERIMENTS / "binary_frame_replay.py"),
        "skip-frame-kappa local pin drift",
    )
    # Duplicate-key check already applied via load_json_unique above.


def check_optimize_refusal() -> None:
    env = dict(**{k: v for k, v in __import__("os").environ.items() if k != "PYTHONOPTIMIZE"})
    env["PYTHONOPTIMIZE"] = "1"
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    for rel in (
        "scripts/experiments/binary_frame_replay.py",
        "research/joint-dual-replay-production/baseline.py",
    ):
        proc = subprocess.run(
            [sys.executable, "-I", "-O", "-B", "-c",
             f"import importlib.util; p={str(ROOT / rel)!r}; "
             "s=importlib.util.spec_from_file_location('m', p); "
             "m=importlib.util.module_from_spec(s); s.loader.exec_module(m)"],
            cwd=ROOT,
            env=env,
            capture_output=True,
            text=True,
        )
        require(proc.returncode != 0, f"-O unexpectedly loaded {rel}")
        require("Assertions must remain enabled" in proc.stderr,
                f"-O refusal message missing for {rel}: {proc.stderr}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args(argv)

    if sys.flags.optimize:
        check_optimize_refusal()
        print("PASS_JOINT_DUAL_REPLAY_PRODUCTION_O_POLICY refused_by_assert_gate=2 no_new_kappa")
        return 0

    check_baseline_bytes()
    baseline = load_module(PACKAGE / "baseline.py", "binary_frame_replay_baseline")
    production = load_module(EXPERIMENTS / "binary_frame_replay.py", "binary_frame_replay_production")
    outputs = check_mask_identity(production)
    receipts = check_replay_equivalence(baseline, production)
    check_rejections(baseline, production)
    check_temp_corruption(production)
    check_pin_consistency()
    check_optimize_refusal()
    print(
        "PASS_JOINT_DUAL_REPLAY_PRODUCTION "
        f"words={[23, 25]} "
        f"outputs={outputs} "
        f"receipts={len(receipts)} "
        "no_new_kappa"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

# SPDX-License-Identifier: Apache-2.0
"""Reconstruct both suppliers and verify the conditional native A-stage format."""

import argparse
import hashlib
import json
import sys
import tempfile
from pathlib import Path

from check_integer import trace
from format import canonical, capacity, fourier_controls, require, stage
from numerators import controls

PACKAGE = Path(__file__).resolve().parent


def authenticate():
    records = json.loads((PACKAGE / "VENDOR.json").read_text())["files"]
    actual = {
        p.relative_to(PACKAGE).as_posix()
        for p in (PACKAGE / "vendor").rglob("*")
        if p.is_file() and "__pycache__" not in p.parts
    }
    require(actual == {r["path"] for r in records}, "complete frozen inventory")
    require(len(records) <= 32, "bounded frozen inventory")
    for record in records:
        path = PACKAGE / record["path"]
        require(
            not path.is_symlink() and path.stat().st_size <= 8_000_000,
            "bounded regular source",
        )
        require(
            hashlib.sha256(path.read_bytes()).hexdigest() == record["sha256"],
            "frozen source bytes",
        )
    return len(records)


def frame_contract(word):
    from vendor import clifford as c

    frames = word["frames"]
    require(len(frames) <= 4096, "bounded canonical frames")
    for frame in frames:
        require(
            len(frame) <= 9
            and all(type(x) is int and 0 < x < 512 for x in frame)
            and c.f2_rank(frame) == len(frame),
            "independent frame",
        )
        circuit = c.canonical_frame(frame)
        cs = [g for g in circuit if g[0] == "C"]
        require(cs == c.fourier(len(frame)), "canonical independent Fourier axes")
        require(
            all(g[0] in ("C", "P", "D") for g in circuit), "canonical gate alphabet"
        )
        require(len(circuit) <= 13, "bounded canonical circuit")
    require(len(word["warps"]) <= 256, "bounded logical warps")
    for warp in word["warps"]:
        columns = warp["G_columns"]
        require(
            len(columns) == 9
            and all(type(x) is int and 0 < x < 512 for x in columns)
            and c.f2_rank(columns) == 9,
            "invertible monomial warp",
        )
    return len(frames)


def run(work):
    count = authenticate()
    sys.path.insert(0, str(PACKAGE / "vendor/parent"))
    import replay_parent as inherited
    from contractions import produce
    from tariff import produce as parent

    inherited.check_pins()
    results = {}
    for provider in ("base", "extra"):
        raw = inherited.read(PACKAGE / f"vendor/parent/vendor/WORD-{provider}.json.gz")
        word = produce(
            parent(raw), inherited.read(PACKAGE / "vendor/parent/EDITS.json")
        )
        programs, checks = inherited.compile_word(word, work / provider)
        native = inherited.read(work / provider / "native/CANONICAL-WORD.json.gz")
        streams = {
            direction: stage(events, native) for direction, events in programs.items()
        }
        for direction, report in streams.items():
            require(
                trace(programs[direction]) == report["prefix_rows_sha256"],
                "integer/Fraction every-prefix equality",
            )
            for mode in ("gatewise", "paired", "pair_first"):
                capacity(
                    report[mode],
                    64,
                    report[mode]["fractional_bits"],
                    report[mode]["signed_width"],
                )
        results[provider] = {
            "frames": frame_contract(native),
            "native_checks": checks,
            "word_sha256": hashlib.sha256(canonical(word)).hexdigest(),
            "streams": streams,
        }
    return {
        "status": "PASS_CONDITIONAL_NATIVE_A_FORMAT_NO_NEW_KAPPA",
        "input_precision": 64,
        "frozen_files": count,
        "fourier_controls": fourier_controls(),
        "numerator_controls": controls(),
        "providers": results,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work", type=Path)
    args = parser.parse_args()
    if args.work:
        work = args.work.expanduser().resolve()
        require(
            not work.exists() and not work.is_relative_to(PACKAGE.parents[1]),
            "fresh external output directory",
        )
        work.mkdir(parents=True)
        result = run(work)
    else:
        with tempfile.TemporaryDirectory(prefix="rank7-native-A-") as directory:
            result = run(Path(directory))
    expected = PACKAGE / "RESULT.json"
    if expected.exists():
        require(
            result == json.loads(expected.read_text()),
            "deterministic committed receipt",
        )
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()

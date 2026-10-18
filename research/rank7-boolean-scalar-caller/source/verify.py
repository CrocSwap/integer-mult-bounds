# SPDX-License-Identifier: Apache-2.0
"""Fresh native compilation and every scalar recipe microstate through A."""

import argparse
import hashlib
import json
import sys
import tempfile
from pathlib import Path

from microstates import stage
from vendor.native.format import canonical, require
from vendor.native.vendor import clifford

PACKAGE = Path(__file__).resolve().parent


def authenticate():
    records = json.loads((PACKAGE / "VENDOR.json").read_text())["files"]
    actual = {
        p.relative_to(PACKAGE).as_posix()
        for p in (PACKAGE / "vendor").rglob("*")
        if p.is_file() and "__pycache__" not in p.parts
    }
    require(
        len(records) <= 32 and actual == {r["path"] for r in records},
        "complete source inventory",
    )
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
    frames = word["frames"]
    require(len(frames) == 1124, "complete canonical frame inventory")
    for frame in frames:
        require(
            len(frame) <= 9
            and all(type(x) is int and 0 < x < 512 for x in frame)
            and clifford.f2_rank(frame) == len(frame),
            "independent frame axes",
        )
        circuit = clifford.canonical_frame(frame)
        require(
            len(circuit) <= 13
            and all(g[0] in ("C", "P", "D") for g in circuit)
            and [g for g in circuit if g[0] == "C"] == clifford.fourier(len(frame)),
            "canonical independent Fourier factors",
        )
    require(len(word["warps"]) <= 256, "bounded warp inventory")
    for warp in word["warps"]:
        columns = warp["G_columns"]
        require(
            len(columns) == 9
            and all(type(x) is int and 0 < x < 512 for x in columns)
            and clifford.f2_rank(columns) == 9,
            "invertible Gaussian monomial warp",
        )
    return len(frames)


def run(work):
    count = authenticate()
    sys.path.insert(0, str(PACKAGE / "vendor/native/vendor/parent"))
    import replay_parent as parent
    from contractions import produce
    from tariff import produce as tariff_parent

    parent.check_pins()
    results = {}
    inherited = json.loads((PACKAGE / "vendor/native/RESULT.json").read_text())
    for provider in ("base", "extra"):
        raw = parent.read(
            PACKAGE / f"vendor/native/vendor/parent/vendor/WORD-{provider}.json.gz"
        )
        word = produce(
            tariff_parent(raw),
            parent.read(PACKAGE / "vendor/native/vendor/parent/EDITS.json"),
        )
        programs, checks = parent.compile_word(word, work / provider)
        native_word = parent.read(work / provider / "native/CANONICAL-WORD.json.gz")
        frame_count = frame_contract(native_word)
        require(
            checks == inherited["providers"][provider]["native_checks"],
            "inherited complete compiler checks",
        )
        streams = {d: stage(events, native_word, d) for d, events in programs.items()}
        for direction, result in streams.items():
            require(
                result["baseline"]
                == inherited["providers"][provider]["streams"][direction]["pair_first"],
                "reconstructed capacity baseline",
            )
        results[provider] = {
            "word_sha256": hashlib.sha256(canonical(word)).hexdigest(),
            "canonical_frames": frame_count,
            "streams": streams,
        }
        require(
            results[provider]["word_sha256"]
            == inherited["providers"][provider]["word_sha256"],
            "exact inherited provider word",
        )
    return {
        "status": "PASS_COEFFICIENT_CAPACITY_NO_NEW_KAPPA",
        "frozen_files": count,
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
            "fresh external output",
        )
        work.mkdir(parents=True)
        result = run(work)
    else:
        with tempfile.TemporaryDirectory(prefix="coefficient-capacity-") as directory:
            result = run(Path(directory))
    expected = PACKAGE / "RESULT.json"
    if expected.exists():
        require(
            result == json.loads(expected.read_text()),
            "deterministic committed receipt",
        )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

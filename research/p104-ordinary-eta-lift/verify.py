#!/usr/bin/env python3
"""Replay the two scoped receipts, their failure controls, or optional Git pins."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
HEAD = "75f7e1c44f48c43983016bcf8878c4d9e5e87c62"
PREFIX = "research/p104-weighted-capped-allocation-490950/"
VOLATILE_CENSUS = {
    "directory_bytes", "directory_sha256", "largest_directory_integer_bits", "record_count"
}


def child(script):
    # -B alone does not prevent reading an existing pyc. Every child gets a
    # fresh cache prefix, including direct standalone invocations.
    with tempfile.TemporaryDirectory(prefix="ordinary-replay-cache-") as cache:
        try:
            return subprocess.run(
                [sys.executable, "-I", "-B", "-X", f"pycache_prefix={cache}",
                 str(HERE / script)],
                cwd=HERE, check=True, capture_output=True, text=True,
            )
        except subprocess.CalledProcessError as error:
            if error.stdout:
                print(error.stdout, end="", file=sys.stderr)
            if error.stderr:
                print(error.stderr, end="", file=sys.stderr)
            raise


def read_json(name):
    return json.loads((HERE / name).read_bytes())


def ordinary():
    actual = json.loads(child("witness.py").stdout)
    if actual != read_json("RESULT.json"):
        raise ValueError("Ordinary receipt does not match the replay")
    print("PASS_ORDINARY_ETA_RECEIPT: strict three-stage rate; combined target rejected")


def setup():
    actual = json.loads(child("setup_scaling.py").stdout)
    expected = read_json("SETUP-RESULT.json")
    if actual.keys() != expected.keys() or actual["variants"].keys() != expected["variants"].keys():
        raise ValueError("Setup receipt has a different shape")
    for name in actual["variants"]:
        row = actual["variants"][name]
        if not (0 < row["record_count"] < 2**32
                and 0 < row["directory_bytes"] < 2**38
                and 0 < row["largest_directory_integer_bits"] < 2**38
                and len(row["directory_sha256"]) == 64):
            raise ValueError(f"Invalid directory census for {name}")
        print(f"CENSUS {name}: records={row['record_count']} bytes={row['directory_bytes']} "
              f"largest_integer_bits={row['largest_directory_integer_bits']} "
              f"sha256={row['directory_sha256']}")
        for field in VOLATILE_CENSUS:
            row.pop(field)
            expected["variants"][name].pop(field)
    if actual != expected:
        raise ValueError("Setup proof or profile fields do not match the replay")
    print("PASS_SETUP_25BIT: scoped serial bound and four finite constructor censuses")


def controls():
    done = child("controls.py")
    if done.stdout:
        print(done.stdout, end="")
    if done.stderr:
        print(done.stderr, end="", file=sys.stderr)
    print("PASS_NEGATIVE_CONTROLS")


def source_history(repository):
    sys.path.insert(0, str(HERE))
    import witness

    saved = read_json("original/source-pins.json")
    if saved["head"] != HEAD or saved["repository"] != "CrocSwap/integer-mult-bounds":
        raise ValueError("Unexpected recorded source identity")
    # Do not allow inherited Git settings or replacement refs to redirect the
    # repository or substitute different objects for the named commit.
    excluded = {"GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_OBJECT_DIRECTORY",
                "GIT_ALTERNATE_OBJECT_DIRECTORIES", "GIT_NAMESPACE", "GIT_CEILING_DIRECTORIES",
                "GIT_COMMON_DIR", "GIT_CONFIG_PARAMETERS", "GIT_CONFIG_COUNT"}
    env = {k: v for k, v in os.environ.items()
           if k not in excluded and not k.startswith(("GIT_CONFIG_KEY_", "GIT_CONFIG_VALUE_"))}
    env["GIT_NO_REPLACE_OBJECTS"] = "1"
    command = ["git", "--no-replace-objects", "-C", str(repository), "cat-file"]
    subprocess.run(command + ["-e", HEAD + "^{commit}"], env=env, check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    for name, expected_blob in witness.HEAD_BLOBS.items():
        data = (HERE / "original" / name).read_bytes()
        if hashlib.sha256(data).hexdigest() != witness.PINS[name]:
            raise ValueError(f"Retained source SHA-256 differs: {name}")
        if saved["files"][PREFIX + name] != expected_blob:
            raise ValueError(f"Recorded Git blob differs: {name}")
        source = subprocess.run(command + ["blob", HEAD + ":" + PREFIX + name],
                                env=env, check=True, capture_output=True).stdout
        if source != data:
            raise ValueError(f"Commit source bytes differ: {name}")
    print(f"PASS_SOURCE_HISTORY: {len(witness.HEAD_BLOBS)} retained files at {HEAD}")


def main():
    if not __debug__:
        raise ValueError("Run with assertions enabled")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("ordinary", "setup", "controls", "source-history"))
    parser.add_argument("repository", nargs="?", type=Path)
    args = parser.parse_args()
    if args.mode == "source-history":
        if args.repository is None:
            parser.error("source-history requires a local repository path")
        source_history(args.repository)
    else:
        if args.repository is not None:
            parser.error("repository is valid only with source-history")
        {"ordinary": ordinary, "setup": setup, "controls": controls}[args.mode]()


if __name__ == "__main__":
    main()

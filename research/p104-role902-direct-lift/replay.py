"""Rebuild and verify the role902 fusion from package-local pins."""
import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent


def unique(pairs):
    obj = dict(pairs)
    assert len(obj) == len(pairs), "duplicate key"
    return obj


def read(path):
    return json.loads(path.read_text(), object_pairs_hook=unique)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def authenticate():
    pins = read(HERE / "PINS.json")
    for name, digest in pins.items():
        path = HERE / name
        assert not path.is_symlink() and path.resolve().is_relative_to(HERE)
        assert sha(path.read_bytes()) == digest, name


def contained(root, command, *args, timeout, capture=False):
    environment = dict(os.environ, TMPDIR=str(root / "isolated"))
    result = subprocess.run(
        [sys.executable, "-I", "-B", str(command), *map(str, args)],
        cwd=root, env=environment, check=True, timeout=timeout, stdout=subprocess.PIPE if capture else None,
    )
    return result.stdout


def compare(record, expected, omit=()):
    actual, reference = read(record), read(expected)
    for key in omit:
        assert key in actual
        actual.pop(key)
        reference.pop(key, None)
    assert actual == reference, record.name


def main():
    assert __debug__ and sys.version_info[:2] == (3, 12)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", choices=("exact", "complete"), required=True)
    args = parser.parse_args()
    authenticate()
    with tempfile.TemporaryDirectory(prefix="composed-7481-7542-") as work:
        root = Path(work).resolve()
        (root / "isolated").mkdir()
        frozen = root / "frozen-composition"
        engine = HERE / "engines"
        inputs = HERE / "bench/inputs"
        old = inputs / "COMPOSED-WORD.json.gz"
        expected_word = HERE / "expected/role902-WORD.json.gz"
        emitted = root / "emitted.json.gz"
        quote = contained(root, HERE / "emit/check_role902_rung.py", inputs, "--candidate", emitted,
                          timeout=32, capture=True)
        assert quote == (HERE / "expected/PREFLIGHT.json").read_bytes()
        assert gzip.decompress(emitted.read_bytes()) == gzip.decompress(expected_word.read_bytes())
        if args.stage == "exact":
            obs = root / "physical.json"
            independent = HERE / "independent"
            obs.write_bytes(contained(root, independent / "check_role902_physical.py", inputs, expected_word,
                                      timeout=32, capture=True))
            compare(obs, HERE / "expected/PHYSICAL.json", ("seconds",))
            obs.write_bytes(contained(root, independent / "check_role902.py", old, independent / "peer_chart.py",
                                      timeout=32, capture=True))
            compare(obs, HERE / "expected/PEER-CHART.json")
            whole = root / "whole.json"
            whole.write_bytes(contained(root, independent / "check_role902_grid.py", inputs, expected_word,
                                        timeout=122, capture=True))
            compare(whole, HERE / "expected/WHOLE.json", ("seconds",))
            print("PASS_ROLE902_INDEPENDENT_WORD", flush=True)
        else:
            shutil.copytree(HERE / "upstream/inputs", root / "inputs")
            for name, src in (
                ("COMPOSED-WORD.json.gz",old), ("7481-WORD.json.gz",HERE/"bench/7481-WORD.json.gz"),
                ("7544-NATIVE.json",HERE/"bench/7544-NATIVE.json"),("role902-WORD.json.gz",expected_word),
            ):
                frozen.mkdir(exist_ok=True)
                shutil.copyfile(src,frozen/name)
            frozen_signed=root/"frozen-role902"
            frozen_signed.mkdir()
            for name,src in (
                ("7544-NATIVE.json",HERE/"bench/7544-NATIVE.json"),("7544-SIGNED.json",HERE/"bench/7544-SIGNED.json"),
                ("ROLE902-WORD.json.gz",expected_word),
            ):
                shutil.copyfile(src,frozen_signed/name)
            for name in ("reroute","validation_native","validation_signed"):
                (root/"producer54"/name).mkdir(parents=True)
            shutil.copyfile(expected_word,root/"producer54/reroute/WORD.json.gz")
            shutil.copyfile(engine/"7481-EMISSION.json",root/"producer54/reroute/RESULT.json")
            (root/"receipts").mkdir()
            contained(root,engine/"adapt_native902.py",engine/"7544-native.py",frozen,
                      root/"producer54/validation_native/run.py",timeout=5,capture=True)
            contained(root,engine/"adapt_signed902.py",root,engine/"7544-signed.py",
                      root/"producer54/validation_signed/role902_run.py",timeout=5,capture=True)
            shutil.copyfile(engine/"run_full_candidate.py",root/"run_full_candidate.py")
            try:
                contained(root,root/"run_full_candidate.py",timeout=990)
            except subprocess.CalledProcessError:
                for entry in sorted((root/"receipts").glob("*.stderr")):
                    sys.stderr.write(entry.read_text())
                raise
            compare(root/"producer54/validation_native/NATIVE-RESULT.json",HERE/"expected/NATIVE.json",("timings",))
            compare(root/"producer54/validation_signed/RESULT.json",HERE/"expected/SIGNED.json",("timings","elapsed_seconds"))
            recurrence=root/"recurrence.json"
            recurrence.write_bytes(contained(root,engine/"check_recurrence.py",old,expected_word,
                inputs/"7113-CALLER.json",HERE/"bench/7544-SIGNED.json",engine/"interval_gate.py",
                timeout=30,capture=True))
            assert recurrence.read_bytes() == (engine/"RECURRENCE.json").read_bytes()
            receipt=root/"final.json"
            receipt.write_bytes(contained(root,engine/"check_final902.py",root,recurrence,
                inputs/"COMPOSED-APPLICATION.json",timeout=30,capture=True))
            compare(receipt,HERE/"expected/FINAL.json",("native_result_sha256","signed_result_sha256"))
            print("PASS_ROLE902_COMPLETE_REPLAY",read(receipt)["claim_decimal"],flush=True)
    authenticate()


if __name__ == "__main__":
    main()

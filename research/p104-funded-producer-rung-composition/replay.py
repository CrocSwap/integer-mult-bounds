"""Rebuild and verify the literal #7481 + #7542 composition from local pins."""
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
        contained(root, HERE / "compose/compose.py", HERE / "bench/inputs", frozen, timeout=32)
        compare(frozen / "COMPOSITION.json", HERE / "expected/COMPOSITION.json", ("gzip_sha256",))
        emitted = frozen / "COMPOSED-WORD.json.gz"
        retained = HERE / "expected/COMPOSED-WORD.json.gz"
        assert gzip.decompress(emitted.read_bytes()) == gzip.decompress(retained.read_bytes())
        shutil.copyfile(retained, emitted)
        shutil.copyfile(HERE / "expected/COMPOSITION.json", frozen / "COMPOSITION.json")
        if args.stage == "exact":
            observed = root / "independent.json"
            observed.write_bytes(contained(root, HERE / "independent/check_composition.py",
                                           HERE / "bench", HERE / "peer", timeout=122, capture=True))
            assert read(observed)["composed_canonical_sha256"] == read(frozen / "COMPOSITION.json")["canonical_sha256"]
            compare(observed, HERE / "expected/INDEPENDENT.json", ("seconds",))
            print("PASS_COMPOSED_INDEPENDENT_WORD", flush=True)
        else:
            shutil.copytree(HERE / "upstream/inputs", root / "inputs")
            for name, source in (
                ("7481-WORD.json.gz", HERE / "bench/inputs/7481-WORD.json.gz"),
                ("7481-NATIVE.json", HERE / "bench/7481-NATIVE.json"),
                ("7481-SIGNED.json", HERE / "bench/7481-SIGNED-RESULT.json"),
            ):
                shutil.copyfile(source, frozen / name)
            for name in ("reroute", "validation_native", "validation_signed"):
                (root / "producer54" / name).mkdir(parents=True)
            shutil.copyfile(frozen / "COMPOSED-WORD.json.gz", root / "producer54/reroute/WORD.json.gz")
            shutil.copyfile(engine / "7481-EMISSION.json", root / "producer54/reroute/RESULT.json")
            (root / "receipts").mkdir()
            contained(root, engine / "adapt_native.py", root, engine / "native.py", timeout=5)
            signed = root / "producer54/validation_signed/composed_run.py"
            contained(root, engine / "adapt_signed.py", root, engine / "signed.py", signed, timeout=5)
            try:
                contained(root, engine / "run_full_candidate.py", root, timeout=1010)
            except subprocess.CalledProcessError:
                for entry in sorted((root / "receipts").glob("*.stderr")):
                    sys.stderr.write(entry.read_text())
                raise
            compare(root / "producer54/validation_native/NATIVE-RESULT.json", HERE / "expected/NATIVE.json", ("timings",))
            compare(root / "producer54/validation_signed/RESULT.json", HERE / "expected/SIGNED.json", ("timings", "elapsed_seconds"))
            receipt = root / "final.json"
            receipt.write_bytes(contained(root, engine / "check_final.py", root, engine / "interval_gate.py", timeout=20, capture=True))
            compare(receipt, HERE / "expected/FINAL.json", ("native_result_sha256", "signed_result_sha256"))
            print("PASS_COMPOSED_COMPLETE_REPLAY", read(receipt)["claim_decimal"], flush=True)
    authenticate()


if __name__ == "__main__":
    main()

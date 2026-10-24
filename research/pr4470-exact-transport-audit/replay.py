#!/usr/bin/env python3
"""Fresh execution and exact comparison with the first hosted transport receipt.

No mathematical field or source check is waived. Apache-2.0; OpenAI assistance.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
EXPECTED_SHA256 = "53bdd869ebeee0980b139e422043922c87585bef90c2989969532ccb7b289a00"
ENGINE_BLOB = "1c9a9d6410e29b7c201547be9f0bef8685c4571b"


def require(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def load_expected(path: Path = HERE / "RESULT.json") -> dict:
    require(path.is_file() and not path.is_symlink(), "Missing/aliased receipt")
    raw = path.read_bytes()
    require(hashlib.sha256(raw).hexdigest() == EXPECTED_SHA256, "Hosted receipt changed")
    return json.loads(raw)


def compare(actual: object, expected: dict) -> None:
    # Serialisation distinguishes bool/int and int/float, unlike dict equality.
    encode = lambda value: json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
    require(encode(actual) == encode(expected), "Scientific receipt mismatch")


def authenticate_engine(path: Path = HERE / "verify.py") -> None:
    require(path.is_file() and not path.is_symlink(), "Missing/aliased engine")
    raw = path.read_bytes()
    actual = hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()
    require(actual == ENGINE_BLOB, "Scientific engine changed")


def main() -> None:
    expected = load_expected()
    authenticate_engine()
    with tempfile.TemporaryDirectory(prefix="pr4470-exact-replay-") as directory:
        out = Path(directory) / "fresh.json"
        flags = ["-I", "-B"] + (["-O"] if sys.flags.optimize else [])
        subprocess.run([sys.executable, *flags, str(HERE / "verify.py"), "--out", str(out)],
                       check=True, timeout=550)
        compare(json.loads(out.read_text(encoding="utf-8")), expected)
    print("PASS_PR4470_EXACT_TRANSPORT_REGISTERED all_receipt_fields=true")


if __name__ == "__main__":
    main()

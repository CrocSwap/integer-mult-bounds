"""Verify the signed rank-nine caller with the transferred causal helper."""
from hashlib import sha256
import os
from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess
import sys
import tarfile

ARCHIVE_SHA = "c4f4f616a308839acc909abe72291f2e081aee320a8a7c38dc56a192daba3bf1"
root = Path(__file__).resolve().parent
archive = root / "REPLAY.tar.gz"
assert __debug__ and sys.version_info[:2] == (3, 12)
assert sha256(archive.read_bytes()).hexdigest() == ARCHIVE_SHA
with TemporaryDirectory(prefix="croc-retimed-package-") as tmp:
    source, result = Path(tmp) / "source", Path(tmp) / "result"
    source.mkdir()
    with tarfile.open(archive) as bundle:
        bundle.extractall(source, filter="data")
    subprocess.run(["bash", str(source / "verify.sh"), str(result)],
                   check=True, env=os.environ | {"RANK9_PYTHON": sys.executable})
    assert (result / "RESULT.json").read_bytes() == (root / "RESULT.json").read_bytes()

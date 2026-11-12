"""Replay the cocharted rank-nine helper split."""
from hashlib import sha256
import os
from pathlib import Path
import subprocess
import sys
import tarfile
from tempfile import TemporaryDirectory

ARCHIVE_SHA = "7a254b76dc6050451f01331205136d1be1ddae14f085cbd54adc44518793de94"
root = Path(__file__).resolve().parent
archive = root / "REPLAY.tar.gz"
assert __debug__ and sys.version_info[:2] == (3, 12)
assert sha256(archive.read_bytes()).hexdigest() == ARCHIVE_SHA
with TemporaryDirectory(prefix="croc-cochart-package-") as temp:
    source, result = Path(temp) / "source", Path(temp) / "result"
    source.mkdir()
    with tarfile.open(archive) as bundle:
        bundle.extractall(source, filter="data")
    subprocess.run(["bash", str(source / "verify.sh"), str(result)],
                   check=True, env=os.environ | {"RANK9_PYTHON": sys.executable})
    assert (result / "RESULT.json").read_bytes() == (root / "RESULT.json").read_bytes()

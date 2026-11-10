"""Verify the signed rank-nine caller with the transferred rank-eight helper split."""
from hashlib import sha256
import os
from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess
import sys
import tarfile

ARCHIVE_SHA = "1f00fd67a47d20ccea22e4eff66354fdba761688e95578a5bff5c5e722ba2dc7"
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
    cut = subprocess.check_output([sys.executable, "-I", "-B", str(root / "cut.py"),
                                   str(result / "BASE-WORD.json.gz")])
    assert cut == (root / "CUT.json").read_bytes()
    print("PASS_FULL_DOMAIN_RANK8_SPLIT_CUT_IDENTITIES")

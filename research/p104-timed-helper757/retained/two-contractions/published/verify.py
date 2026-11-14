# SPDX-License-Identifier: Apache-2.0
"""Bounded standalone archive replay; does not assert full-theorem verification."""
from hashlib import sha256
from pathlib import Path
import subprocess
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parent
ARCHIVE = ROOT / 'replay.zip'
EXPECTED = '0bf0082cab9b6d2bb6657903a4169a3d04c380927982fc4672a6a44edda79a2a'

def main():
    if sha256(ARCHIVE.read_bytes()).hexdigest() != EXPECTED:
        raise ValueError('Archive SHA256 mismatch')
    with tempfile.TemporaryDirectory(prefix='p104-two-chart-') as tmp:
        base = Path(tmp)
        source = base / 'source'
        source.mkdir()
        with zipfile.ZipFile(ARCHIVE) as archive:
            for member in archive.infolist():
                target = (source / member.filename).resolve()
                if not target.is_relative_to(source.resolve()):
                    raise ValueError('Unsafe archive member')
            archive.extractall(source)
        subprocess.run([sys.executable, '-I', '-B', '-S', '-W', 'error',
            str(source / 'round10' / 'check_replay_bundle.py'),
            str(ARCHIVE), str(base / 'fresh'), '--workers', '2'],
            check=True, timeout=300)

if __name__ == '__main__':
    main()


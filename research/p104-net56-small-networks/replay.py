from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parent
commands = [['small/check_separator.py'], ['small/check_hyperplanes.py'], ['normalization/check.py', 'small/DecoderWall4Data.lean'], ['normalization/zero_drop.py', 'small'], ['normalization/tighten.py', 'small']]
for args in commands:
    subprocess.run([sys.executable, "-B", *args], cwd=root, check=True)

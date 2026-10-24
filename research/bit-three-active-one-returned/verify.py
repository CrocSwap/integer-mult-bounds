#!/usr/bin/env python3
"""Run the saved complete verifier with its assertions enabled."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

if not __debug__:
    raise SystemExit("Run this verifier without -O. Historical sources use assert.")
root = Path(__file__).resolve().parent
manifest = json.loads((root / "SOURCE-MANIFEST.json").read_text())
for item in manifest["files"]:
    actual = hashlib.sha256((root / item["package"]).read_bytes()).hexdigest()
    if actual != item["sha256"]:
        raise SystemExit("Source hash: " + item["package"])
subprocess.run([sys.executable, "-E", "-B", str(root / "generate.py"), *sys.argv[1:]], check=True)

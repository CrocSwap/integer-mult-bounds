"""Fetch locked files and reproduce the archived independent comparator result."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import urllib.request

here = Path(__file__).resolve().parent
cli = argparse.ArgumentParser(description=__doc__)
cli.add_argument("directory", type=Path, help="new directory for cache and output")
args = cli.parse_args()
work = args.directory.resolve()
work.mkdir(parents=True, exist_ok=False)
cache = work / "cache"
output = work / "replayed"
finite = cache / "7786/research/p104-iterated-returns/binary/FINITE.json"
finite.parent.mkdir(parents=True)
url = "https://raw.githubusercontent.com/CrocSwap/integer-mult-bounds/89a67c404226d51028e135de2b9169e9020d57af/research/p104-iterated-returns/binary/FINITE.json"
with urllib.request.urlopen(url, timeout=60) as response:
    raw = response.read()
if hashlib.sha256(raw).hexdigest() != "0cebc543d64ca53ac6c7141dfab40c658bf451fe89bb7744befb76c116ea45e6":
    raise ValueError("Predecessor finite receipt digest changed")
finite.write_bytes(raw)
subprocess.run([sys.executable, "-IB", str(here / "source/verify.py"), "--fetch", "--work", str(cache), "--out", str(output)], check=True)
environment = dict(os.environ, P104_REVIEW_CACHE=str(cache))
audit = subprocess.check_output([sys.executable, "-IB", str(here / "reprice.py"), "--replay", str(output)], env=environment)
(work / "independent.json").write_bytes(audit)
expected = json.loads((here.parent / "receipts/7831-independent.json").read_bytes())
if json.loads(audit) != expected:
    raise ValueError("Independent comparator receipt disagreement")
print("Verified comparator", expected["qualified_conditional_lower"])

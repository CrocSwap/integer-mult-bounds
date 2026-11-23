#!/usr/bin/env python3
"""Optionally rebuild the pinned #8072 word from its separately supplied package.

This is not needed for the fast frozen-word replay. It authenticates the two
#8072 drivers before they authenticate and restore their own #8057 archive,
installs the temporary runtime and compares the full canonical graph and layout.
"""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import runpy
import subprocess
import sys
from tempfile import TemporaryDirectory

HERE = Path(__file__).resolve().parent
PINS = {
    "verify.py": "10362de3ceaa651cde5b71c6599fd4683d9f1f4d76cc252178e915b43a098fee",
    "prepare.py": "76f9d4c6bfd880ee49f6ba5bde9138cf0856d669edb4d525e48ca71a9094eec3",
}
WORD = "38d2b3a2311a9ba5fee091cc7aa204c7ed95651aec95d75184b2391df090cbfb"
LAYOUT = "0ce3f9e383fc4bfdd22612b9e34fc9759d97204215937b82d23aec2cedd9b8ee"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source_package", type=Path,
                        help="research/p104-weighted-capped-allocation-490950 at exact #8072 head")
    package = parser.parse_args().source_package.resolve()
    for name, pin in PINS.items():
        if hashlib.sha256((package / name).read_bytes()).hexdigest() != pin:
            raise ValueError(f"The #8072 source driver differs: {name}")
    with TemporaryDirectory(prefix="gaussian-rank-rebuild-") as temp:
        work = Path(temp)
        original = runpy.run_path(str(package / "verify.py"))
        peer = original["restore"](work)
        runpy.run_path(str(package / "prepare.py"))["materialize"](peer)
        runtime = work / "runtime"
        subprocess.run([sys.executable, "-I", "-B", str(peer / "bootstrap.py"), str(runtime)], check=True)
        sys.path.insert(0, str(runtime))
        from strong_complex import digest, load_changed
        graph, layout = load_changed(runtime / "inputs")
        frozen = gzip.decompress((HERE / "word.json.gz").read_bytes())
        canonical = json.dumps(graph, sort_keys=True, separators=(",", ":")).encode()
        if digest(graph) != WORD or digest(layout) != LAYOUT or canonical != frozen:
            raise ValueError("The source rebuild differs from the frozen graph or layout")
        print("PASS_PINNED_8072_SOURCE_REBUILD", WORD)


if __name__ == "__main__":
    main()

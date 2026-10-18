"""Run the unchanged inherited frame/wrapper auditor in a fresh directory.

This checks the pinned original macro word; primitive substitution is checked
by verify.py and independent.py. Ryan Haines / OpenAI Codex; Apache-2.0.
"""

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from verify import PROVIDER, ROOT, load_inputs, require


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    load_inputs()
    output = args.output.resolve()
    require(not output.exists(), "native replay requires a new directory")
    output.mkdir(parents=True)
    for name in ("CANONICAL-WORD.json.gz", "LOCAL-PROGRAMS.json.gz"):
        shutil.copyfile(ROOT / PROVIDER / name, output / name)
    auditor = ROOT / "research/complex-k492-owner-repair/code/hpe_audit_local.py"
    subprocess.run([sys.executable, "-I", "-B", str(auditor), str(output)], check=True)
    receipt = json.loads((output / "INDEPENDENT-LOCAL-REPLAY.json").read_text())
    # The inherited receipt hashes gzip containers; compare mathematical fields.
    del receipt["canonical_word_sha256"]
    del receipt["local_programs_sha256"]
    expected = json.loads((HERE / "NATIVE.json").read_text())
    require(receipt == expected, "native semantic receipt mismatch")
    print("PASS_UNCHANGED_NATIVE_JP8_REPLAY columns=716 "
          f"controls={len(receipt['negative_controls_rejected'])}")


if __name__ == "__main__":
    main()

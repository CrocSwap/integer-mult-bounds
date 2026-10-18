"""Check the unchanged historical macro frame/wrapper contract in scratch."""

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
    directory = args.output.resolve()
    require(not directory.exists(), "native replay requires a new directory")
    directory.mkdir(parents=True)
    for name in ("CANONICAL-WORD.json.gz", "LOCAL-PROGRAMS.json.gz"):
        shutil.copyfile(ROOT / PROVIDER / name, directory / name)
    auditor = ROOT / "research/complex-k492-owner-repair/code/hpe_audit_local.py"
    subprocess.run([sys.executable, "-I", "-B", str(auditor), str(directory)], check=True)
    result = json.loads((directory / "INDEPENDENT-LOCAL-REPLAY.json").read_text())
    del result["canonical_word_sha256"]
    del result["local_programs_sha256"]
    require(result == json.loads((HERE / "NATIVE.json").read_text()), "native semantic receipt")
    print("PASS_UNCHANGED_JP8_NATIVE_CONTRACT columns=716 "
          f"controls={len(result['negative_controls_rejected'])}")


if __name__ == "__main__":
    main()

"""Run the frozen #7000 driver with its original selected record in an isolated tree."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]


def main():
    checkpoint = ROOT / "certificates/checkpoints/frontier7000.json"
    record = json.loads(checkpoint.read_bytes())
    manifest = record["source_manifest"]
    files = json.loads((ROOT / manifest).read_bytes())["files"]
    with TemporaryDirectory() as tmp:
        tree = Path(tmp)
        for name in (*files, manifest):
            dest = tree / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, dest)
        shutil.copyfile(checkpoint, tree / "certificates/selected-result.json")
        subprocess.run([sys.executable, "-I", "-B", tree / "scripts/verify_frontier7000.py",
                        *sys.argv[1:]], check=True)


if __name__ == "__main__":
    main()

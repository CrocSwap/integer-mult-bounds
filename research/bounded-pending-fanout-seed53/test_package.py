"""Offline relocation and actual file-corruption controls for the public CLI."""

import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent


def run(folder, script="verify.py"):
    return subprocess.run([sys.executable, "-I", "-O", "-B", str(folder / script)],
                          cwd=folder.parent, text=True, capture_output=True, timeout=30)


def need(ok, message):
    if not ok:
        raise RuntimeError(message)


def main():
    baseline = run(HERE)
    need(baseline.returncode == 0, baseline.stderr)
    with tempfile.TemporaryDirectory(prefix="bounded-pending-") as root:
        destination = Path(root) / "package"
        shutil.copytree(HERE, destination, ignore=shutil.ignore_patterns("__pycache__"))
        clean = run(destination)
        need(clean.returncode == 0 and clean.stdout == baseline.stdout, "relocation differs")
        generated = run(destination, "schedule.py")
        need(generated.returncode == 0 and
             generated.stdout == (destination / "CERTIFICATE.json").read_text(),
             "literal certificate regeneration differs")
        for mutation in ("certificate", "commit", "source", "inventory", "producer"):
            shutil.rmtree(destination)
            shutil.copytree(HERE, destination, ignore=shutil.ignore_patterns("__pycache__"))
            if mutation in ("certificate", "commit"):
                path = destination / "CERTIFICATE.json"
                data = json.loads(path.read_text())
                if mutation == "certificate":
                    data["plans"]["bounded"]["leaves"].pop()
                else:
                    data["plans"]["bounded"]["commit_after"][0] = 0
                path.write_text(json.dumps(data))
            elif mutation == "source":
                path = destination / "sources/PR938-PROOF.md"
                path.write_bytes(path.read_bytes() + b"\nchanged\n")
            elif mutation == "inventory":
                path = destination / "SOURCES.json"
                data = json.loads(path.read_text())
                data["files"].pop()
                path.write_text(json.dumps(data))
            else:
                path = destination / "schedule.py"
                old = path.read_text()
                new = old.replace('word.append(["B", -1])', 'word.append(["B", 1])')
                need(new != old, "producer mutation not applied")
                path.write_text(new)
                changed = run(destination, "schedule.py")
                need(changed.returncode == 0, "mutated producer did not run")
                (destination / "CERTIFICATE.json").write_text(changed.stdout)
            result = run(destination)
            need(result.returncode != 0 and "ValueError" in result.stderr,
                 f"{mutation} corruption was not rejected")
    print("PASS_BOUNDED_PENDING_PACKAGE controls=5 relocated_optimized=PASS regeneration=identical")


if __name__ == "__main__":
    main()

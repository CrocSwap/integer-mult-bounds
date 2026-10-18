"""Real-file failures in a minimal Git-free copy; never edits original inputs."""
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def main():
    with tempfile.TemporaryDirectory(prefix="disposable-cut-") as temporary:
        target = Path(temporary)
        package = target / "research" / HERE.name
        shutil.copytree(HERE, package, ignore=shutil.ignore_patterns("__pycache__"))
        sources = json.loads((HERE / "SOURCES.json").read_text(encoding="utf-8"))
        inputs = [x["path"] for x in sources["files"] if x["usage"] == "input"]
        for name in inputs:
            dest = target / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, dest)
        originals = {p: p.read_bytes() for p in target.rglob("*") if p.is_file()}

        def run(wanted, diagnostic=None):
            cp = subprocess.run([sys.executable, "-I", "-O", "-B", str(package / "verify.py")],
                                cwd=target, capture_output=True, text=True, encoding="utf-8")
            if (cp.returncode == 0) != wanted or diagnostic and diagnostic not in cp.stdout + cp.stderr:
                raise ValueError("unexpected exported replay: " + cp.stdout + cp.stderr)

        run(True, "PASS_COMMON_FLAG_DISPOSABLE_WORKSPACE")
        changes = [
            (target / inputs[0], lambda b: b + b"\nsource drift", "source drift"),
            (package / "PROOF.md", lambda b: b + b"\nproof drift", "proof drift"),
            (package / "EXPECTED.json", lambda b: b.replace(b'"duplicate_copy_bill": 2', b'"duplicate_copy_bill": true'), "typed receipt mismatch"),
        ]
        for path, mutate, diagnostic in changes:
            changed = mutate(originals[path])
            if changed == originals[path]:
                raise ValueError("inert corruption control")
            path.write_bytes(changed)
            run(False, diagnostic)
            if path.read_bytes() != changed:
                raise ValueError("replay overwrote failed evidence")
            path.write_bytes(originals[path])
        if any(p.read_bytes() != b for p, b in originals.items()):
            raise ValueError("export changed")
    print("PASS_DISPOSABLE_CUT_INTEGRITY git_free_positive=1 real_file_rejections=3")


if __name__ == "__main__":
    main()

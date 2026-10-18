"""Check relocation and real on-disk corruptions using only the standard library."""
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent


def run(root, ok):
    result = subprocess.run([sys.executable, "-I", "-O", "-B", str(root / "verify.py")],
                            cwd=root.parent, capture_output=True, text=True)
    if (result.returncode == 0) != ok:
        raise ValueError(result.stdout + result.stderr)
    if ok and "PASS_OUTPUT_SIGN_RESTORATION" not in result.stdout:
        raise ValueError("missing success marker")
    if not ok and not any(message in result.stderr for message in
                          ("source SHA256 mismatch", "source Git blob mismatch", "certificate mismatch")):
        raise ValueError("corruption failed for an unrelated reason: " + result.stderr)


def main():
    with tempfile.TemporaryDirectory(prefix="output-sign-") as tmp:
        root = Path(tmp) / "relocated"
        shutil.copytree(HERE, root, ignore=shutil.ignore_patterns("__pycache__"))
        run(root, True)
        paths = ["sources/PR1155-README.md", "SOURCE-PINS.json", "CERTIFICATE.json"]
        originals = {name: (root / name).read_bytes() for name in paths}
        mutations = [
            (paths[0], lambda data: data + b"changed source\n"),
            (paths[1], lambda data: data.replace(b'"git_blob": "43ef54', b'"git_blob": "03ef54', 1)),
            (paths[2], lambda data: data.replace(b'"NEG_saved": 56', b'"NEG_saved": 57', 1)),
            (paths[2], lambda data: data.replace(b'"schedules": 21840', b'"schedules": 21839', 1))]
        for name, mutate in mutations:
            changed = mutate(originals[name])
            if changed == originals[name]:
                raise ValueError("mutation did not alter file")
            (root / name).write_bytes(changed)
            run(root, False)
            (root / name).write_bytes(originals[name])
    print("PASS_OUTPUT_SIGN_PACKAGE relocation=1 corruptions=4")


if __name__ == "__main__":
    main()

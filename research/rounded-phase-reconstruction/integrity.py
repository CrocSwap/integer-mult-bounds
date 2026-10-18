"""Git-free replay, pre-import authentication and typed receipt controls."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent


def need(ok, message):
    if not ok:
        raise ValueError(message)


def tree(root):
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob("*") if p.is_file()}


def main():
    controls = 0
    with tempfile.TemporaryDirectory(prefix="rounded-phase-export-") as tmp:
        root = Path(tmp).resolve()
        pkg = root / HERE.name
        shutil.copytree(HERE, pkg)
        def run(extra=(), expect="PASS_ROUNDED_PHASE_RECONSTRUCTION"):
            result = subprocess.run([sys.executable, "-I", "-O", "-B", str(pkg / "verify.py"), *extra],
                                    cwd=root, text=True, capture_output=True, timeout=120)
            output = result.stdout + result.stderr
            need("UNAUTHENTICATED_EXECUTION" not in output, "corrupt module executed before authentication")
            need((result.returncode == 0 if expect.startswith("PASS_") else result.returncode != 0) and expect in output,
                 "unexpected replay/control result: " + output)
        before = tree(root)
        run()
        need(tree(root) == before, "replay changed exported evidence")
        run(["--write"], "refuse receipt overwrite"); controls += 1
        run(["--unknown"], "unrecognized arguments"); controls += 1
        for filename in ("vendor/pr1141/phase_stream.py", "vendor/pr1141/vendor/pr1038/chirp.py",
                         "vendor/pr1141/vendor/pr1038/dirty_stride.py"):
            path = pkg / filename
            original = path.read_bytes()
            path.write_bytes(original + b'\nraise RuntimeError("UNAUTHENTICATED_EXECUTION")\n')
            run(expect="source SHA256")
            path.write_bytes(original); controls += 1
        path = pkg / "Reconstruction.lean"
        original = path.read_bytes(); path.write_bytes(original + b"\n-- changed proof\n")
        run(expect="formal source receipt mismatch")
        path.write_bytes(original); controls += 1
        path = pkg / "KERNEL.json"
        original = path.read_bytes(); value = json.loads(original)
        value["axioms"]["RoundedPhase.reconstruct"].append("sorryAx")
        path.write_text(json.dumps(value), encoding="utf-8")
        run(expect="formal receipt toolchain/axioms")
        path.write_bytes(original); controls += 1
        path = pkg / "RESULT.json"
        original = path.read_bytes(); value = json.loads(original)
        value["kernel_run_by_this_command"] = 0
        path.write_text(json.dumps(value), encoding="utf-8")
        run(expect="receipt mismatch")
        path.write_bytes(original); controls += 1
        need(tree(root) == before, "mutation controls failed to restore export")
    print("PASS_ROUNDED_PHASE_INTEGRITY git_free=1 controls=" + str(controls))


if __name__ == "__main__":
    main()

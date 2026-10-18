"""Behavioral checks of the source-bound export, not a substitute for the proof."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile

P = Path(__file__).resolve().parent
ROOT = P.parents[1]


def need(condition, message):
    if not condition:
        raise ValueError(message)


def tree(path):
    return {f.relative_to(path).as_posix(): hashlib.sha256(f.read_bytes()).hexdigest()
            for f in path.rglob("*") if f.is_file() and "__pycache__" not in f.parts}


def run(root, suffix=(), fail=None):
    package = root / "research/p104-dual-add-retiming"
    command = [sys.executable, "-I", "-O", "-B", str(package/"verify.py"), *map(str,suffix)]
    result = subprocess.run(command, cwd=root, capture_output=True, text=True, timeout=120)
    output = result.stdout + result.stderr
    if fail is None:
        need(result.returncode == 0 and "PASS_P104_DUAL_ADD_RETIMING" in output, output)
    else:
        need(result.returncode != 0 and fail in output, "unexpected fault outcome: " + output)
    return output


def main():
    with tempfile.TemporaryDirectory(prefix="p104-retiming-export-") as directory:
        export = Path(directory)
        package = export / "research/p104-dual-add-retiming"
        shutil.copytree(P, package, ignore=shutil.ignore_patterns("__pycache__"))
        pins = json.loads((P/"SOURCES.json").read_text())
        for pin in pins["files"]:
            if pin["usage"] == "input":
                target = export/pin["path"]
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT/pin["path"], target)
        before = tree(export)
        run(export)
        need(tree(export) == before, "verification changed export files")
        faults = [
            (package/"inputs/PR2662-WORD.json", b"\n", "source SHA256"),
            (export/"research/p104-native-channel/vendor/native_verify.py",
             b"\nraise RuntimeError('SHOULD_NOT_EXECUTE')\n", "source SHA256"),
        ]
        for path, addition, message in faults:
            old = path.read_bytes()
            try:
                path.write_bytes(old + addition)
                output = run(export, fail=message)
                need("RuntimeError: SHOULD_NOT_EXECUTE" not in output, "executed unauthenticated input")
            finally:
                path.write_bytes(old)
        receipt = package/"RESULT.json"
        old = receipt.read_bytes()
        try:
            value = json.loads(old)
            value["native"]["recipes"] = 2.0
            receipt.write_text(json.dumps(value))
            run(export, fail="complete typed receipt")
        finally:
            receipt.write_bytes(old)
        occupied = export/"occupied.json"
        occupied.write_text("keep this data")
        run(export, ("--out", occupied), fail="exclusive output")
        need(occupied.read_text() == "keep this data", "occupied output overwritten")
        occupied.unlink()
        need(tree(export) == before, "fault tests changed retained files")
    print("PASS_P104_RETIMING_BEHAVIOR export=pass unchanged_files=pass "
          "source_drift=reject executable_drift=reject typed_receipt=reject occupied_output=reject")


if __name__ == "__main__":
    main()

"""Source-export and corruption controls for the independent reset audit.

Hanson Sun with substantial OpenAI Codex assistance. Apache-2.0.
"""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent


def check(ok,message):
    if not ok:
        raise ValueError(message)


def run(package,script="verify.py",extra=(),success=True):
    proc = subprocess.run([sys.executable,"-I","-O","-B",str(package/script),*extra],
                          cwd=package.parent,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                          text=True,timeout=150)
    check((proc.returncode == 0) == success,
          f"unexpected exit {proc.returncode} for {script}: {proc.stdout[-800:]} {proc.stderr[-800:]}")
    return proc.stdout


def snapshot(package):
    return {str(p.relative_to(package)):hashlib.sha256(p.read_bytes()).hexdigest()
            for p in package.rglob("*") if p.is_file()}


def main():
    with tempfile.TemporaryDirectory(prefix="precision reset export ") as tmp:
        clone = Path(tmp)/"read only package"
        shutil.copytree(HERE,clone,ignore=shutil.ignore_patterns("__pycache__","*.pyc"))
        emitted = run(clone,extra=("--emit",))
        check(emitted == (clone/"RESULT.json").read_text(),"noncanonical regenerated receipt")
        before = snapshot(clone)
        try:
            for p in clone.rglob("*"):
                p.chmod(0o555 if p.is_dir() else 0o444)
            clone.chmod(0o555)
            check("PASS_INDEPENDENT_RESET_GRAPH" in run(clone),"missing relocated marker")
            check(snapshot(clone) == before,"read-only source export changed")
        finally:
            clone.chmod(0o755)
            for p in clone.rglob("*"):
                p.chmod(0o755 if p.is_dir() else 0o644)
        source = clone/"sources/pr1537-model.py"
        original = source.read_bytes()
        source.write_bytes(original+b"\n# altered source\n")
        run(clone,success=False)
        source.write_bytes(original)
        certificate = clone/"sources/pr1552-CERTIFICATE.json"
        original_certificate = certificate.read_bytes()
        obj = json.loads(original_certificate)
        obj["edges"][58]["peak"] -= 1
        certificate.write_text(json.dumps(obj))
        run(clone,success=False)
        certificate.write_bytes(original_certificate)
        result = clone/"RESULT.json"
        original = result.read_bytes()
        obj = json.loads(original)
        obj["frontier"][-1][1] -= 1
        result.write_text(json.dumps(obj))
        run(clone,success=False)
        result.write_bytes(original)
        check(snapshot(clone) == before,"corruption test did not restore export")
    print("PASS_RESET_AUDIT_PACKAGE readonly_relocation=1 deterministic_receipt=1 corrupted_files=3 rejecting_runs=3")


if __name__ == "__main__":
    main()

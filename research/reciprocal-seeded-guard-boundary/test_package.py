"""Exercise portable replay and real on-disk corruptions. Apache-2.0."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent


def run(path):
    return subprocess.run([sys.executable,"-I","-O","-B",str(path/"verify.py")],
                          cwd=path.parent, text=True, capture_output=True, timeout=20)


def repin_receipt(path):
    manifest=json.loads((path/"SOURCES.json").read_text())
    for item in manifest["package_files"]:
        if item["path"]=="CERTIFICATE.json":
            item["sha256"]=hashlib.sha256((path/item["path"]).read_bytes()).hexdigest()
    (path/"SOURCES.json").write_text(json.dumps(manifest))


def main():
    with tempfile.TemporaryDirectory(prefix="seeded reciprocal package ") as work:
        root=Path(work)
        clean=root/"read only source"
        shutil.copytree(HERE,clean,ignore=shutil.ignore_patterns("__pycache__"))
        try:
            for p in clean.rglob("*"):
                p.chmod(0o555 if p.is_dir() else 0o444)
            clean.chmod(0o555)
            result=run(clean)
            if result.returncode or "PASS_SEEDED_GUARD_BOUNDARY" not in result.stdout:
                raise ValueError(result.stdout+result.stderr)
        finally:
            clean.chmod(0o755)
            for p in clean.rglob("*"):
                p.chmod(0o755 if p.is_dir() else 0o644)
        for n in range(4):
            path=root/f"mutation{n}"
            shutil.copytree(HERE,path,ignore=shutil.ignore_patterns("__pycache__"))
            if n==0:
                with (path/"check_certificate.py").open("a") as f:
                    f.write("\n# changed source\n")
            else:
                certificate=json.loads((path/"CERTIFICATE.json").read_text())
                witness=certificate["witnesses"][2]
                if n==1:
                    witness["rows"][-1][3]+=1
                elif n==2:
                    witness["rows"].pop(1)
                else:
                    witness["failure_interval"][1]="254759/131072"
                (path/"CERTIFICATE.json").write_text(json.dumps(certificate))
                repin_receipt(path)  # Exercise semantics beyond a checksum failure.
            result=run(path)
            if not result.returncode:
                raise ValueError(f"accepted actual mutation {n}")
            expected=("source or certificate changed","invalid floor witness",
                      "wrong schedule","false interval failure")[n]
            if expected not in result.stderr:
                raise ValueError(f"unexpected failure {n}: {result.stderr}")
    print("PASS_SEEDED_GUARD_PACKAGE relocation=1 disk_corruptions=4")


if __name__=="__main__":
    main()

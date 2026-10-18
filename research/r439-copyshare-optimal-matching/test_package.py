#!/usr/bin/env python3
"""Git-free isolated replay and three on-disk corruption controls. Apache-2.0."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(ok, message):
    if not ok:
        raise ValueError(message)


def inventory(root):
    return {str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob("*") if p.is_file()}


def run(root, success, fragment):
    result = subprocess.run([sys.executable,"-I","-O","-B",
                             str(root/"research"/HERE.name/"verify.py")],
                            cwd=root,capture_output=True,text=True,timeout=180)
    need((result.returncode==0)==success, "unexpected exit: "+result.stdout+result.stderr)
    need(fragment in result.stdout+result.stderr,"missing expected diagnostic: "+fragment)


if __name__=="__main__":
    with tempfile.TemporaryDirectory(prefix="copyshare-relocation-") as temp:
        root=Path(temp)/"detached"
        package=root/"research"/HERE.name
        shutil.copytree(HERE,package,ignore=shutil.ignore_patterns("__pycache__"))
        for row in json.loads((HERE/"SOURCES.json").read_text())["files"]:
            if row["usage"]=="input":
                target=root/row["path"]
                target.parent.mkdir(parents=True,exist_ok=True)
                shutil.copyfile(ROOT/row["path"],target)
        before=inventory(root)
        run(root,True,"PASS_R439_COPYSHARE_OPTIMAL_MATCHING")
        need(inventory(root)==before,"verification wrote into source closure")
        source=root/"research/h2sem-matching-f-invoice/MATCHING7.json"
        original=source.read_bytes()
        source.write_bytes(original+b"\n")
        run(root,False,"source pin:")
        source.write_bytes(original)
        cert=package/"MATCHING.json"
        original=cert.read_bytes()
        data=json.loads(original)
        data["primary_dual"]["vertex_prices_2"][0][1]=-1
        cert.write_text(json.dumps(data))
        run(root,False,"negative vertex price")
        cert.write_bytes(original)
        expected=package/"EXPECTED.json"
        original=expected.read_bytes()
        data=json.loads(original)
        data["optimal_saving"]+=1
        expected.write_text(json.dumps(data))
        run(root,False,"complete expected receipt mismatch")
        expected.write_bytes(original)
        need(inventory(root)==before,"corruption controls did not restore closure")
    print("PASS_R439_COPYSHARE_PACKAGE optimized_git_free_read_only controls=3")

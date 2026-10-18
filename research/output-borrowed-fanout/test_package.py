#!/usr/bin/env python3
"""Offline relocation, exact payload regeneration, and defect sensitivity."""
import gzip
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent


def run(package, *arguments):
    return subprocess.run([sys.executable, "-I", "-O", "-B", str(package/"verify.py"), *arguments],
                          cwd=package.parent, text=True, capture_output=True)


def require(ok, message):
    if not ok:
        raise ValueError(message)


with tempfile.TemporaryDirectory(prefix="output-borrowed-fanout-") as directory:
    root = Path(directory)
    package = root/"standalone"
    shutil.copytree(HERE, package, ignore=shutil.ignore_patterns("__pycache__"))
    require(run(package).returncode == 0, "offline relocation")
    original = (package/"CERTIFICATE.json.gz").read_bytes()
    payload = gzip.decompress(original)
    for i in range(2):
        out = root/f"regenerated-{i}.json.gz"
        subprocess.run([sys.executable,"-I","-O","-B",str(package/"build.py"),"--out",str(out)],
                       cwd=root,check=True,capture_output=True)
        require(gzip.decompress(out.read_bytes()) == payload, "certificate payload regeneration")
    expected = (package/"EXPECTED.json").read_bytes()
    require(run(package, "--write").returncode == 0, "receipt regeneration")
    require((package/"EXPECTED.json").read_bytes() == expected, "complete receipt differs")
    corruptions = 0
    for name in ("omitted_restore", "aliased_port", "factor_order", "private_bill", "domain", "missing_comparator"):
        cert = json.loads(payload)
        case = cert["fixture"]
        schedule = case["schedules"]["borrowed"]
        if name == "omitted_restore":
            schedule["leaves"].pop()
        elif name == "aliased_port":
            schedule["leaves"][0][0] = schedule["leaves"][0][1]
        elif name == "factor_order":
            case["factors"]["B"].reverse()
        elif name == "private_bill":
            schedule["private_rows"] -= 1
        elif name == "domain":
            cert["cases"].pop()
        elif name == "missing_comparator":
            del case["schedules"]["dedicated"]
        (package/"CERTIFICATE.json.gz").write_bytes(gzip.compress(json.dumps(cert).encode(),mtime=0))
        require(run(package).returncode != 0, "accepted corruption: "+name)
        corruptions += 1
    (package/"CERTIFICATE.json.gz").write_bytes(original)
    ref = package/"references"/"PR889-README.md"
    clean = ref.read_bytes()
    ref.write_bytes(clean+b"\nchanged\n")
    require(run(package).returncode != 0, "accepted reference mutation")
    ref.write_bytes(clean)
    corruptions += 1
    (package/"EXPECTED.json").write_text("{}\n")
    require(run(package).returncode != 0, "accepted incomplete expected receipt")
    corruptions += 1
    (package/"EXPECTED.json").write_bytes(expected)
    require(run(package).returncode == 0, "clean replay after mutations")
print(f"PASS_OUTPUT_BORROWED_PACKAGE relocation=1 regenerations=3 corruptions={corruptions}")

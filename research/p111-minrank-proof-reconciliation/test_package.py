#!/usr/bin/env python3
"""Rejection tests and gzip-container invariance for the proof package."""
import gzip
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent


def run(path):
    return subprocess.run([sys.executable,"-B","-O",str(path/"verify.py")],
                          text=True,capture_output=True,timeout=180)


def main():
    manifest = json.loads((ROOT/"SOURCES.json").read_text())
    controls = []
    with tempfile.TemporaryDirectory(prefix="p111-proof-controls-") as folder:
        trial = Path(folder)/"copy"
        for filename in list(manifest["source_files"])+list(manifest["implementation_sha256"]):
            shutil.copytree(ROOT,trial)
            with (trial/filename).open('ab') as stream:
                stream.write(b"\n# changed bytes\n")
            result = run(trial)
            if result.returncode == 0 or "pin" not in result.stderr:
                raise ValueError("source mutation accepted or wrong failure: "+filename)
            controls.append("modified "+filename)
            shutil.rmtree(trial)
        for c in (8,9):
            shutil.copytree(ROOT,trial)
            path = trial/f"proofs/c{c}.lrat.gz"
            payload = gzip.decompress(path.read_bytes())
            path.write_bytes(gzip.compress(payload+b"1 0 0\n",mtime=0))
            result = run(trial)
            if result.returncode == 0 or "decoded proof pin" not in result.stderr:
                raise ValueError("proof mutation accepted or wrong failure")
            controls.append(f"modified c{c} decoded proof")
            shutil.rmtree(trial)
        for label,mutation in [
            ("changed conclusion",lambda x:x['conclusion'].update(archival_minrank_F2=8)),
            ("understated proof coverage",lambda x:x['certificates']['9']['proof'].update(hints_checked=1)),
            ("floating-point seed",lambda x:x.update(seed=95.0)),
        ]:
            shutil.copytree(ROOT,trial)
            path=trial/"EXPECTED.json";data=json.loads(path.read_text());mutation(data);path.write_text(json.dumps(data))
            result=run(trial)
            if result.returncode == 0 or "certificate differs" not in result.stderr:
                raise ValueError("receipt mutation accepted or wrong failure: "+label)
            controls.append(label);shutil.rmtree(trial)
        shutil.copytree(ROOT,trial)
        path=trial/"SOURCES.json";path.write_text(path.read_text().replace('"base_commit":','"base_commit":"duplicate","base_commit":',1))
        result=run(trial)
        if result.returncode == 0 or "duplicate JSON key" not in result.stderr:
            raise ValueError("duplicate JSON accepted or wrong failure")
        controls.append("duplicate manifest key");shutil.rmtree(trial)
        shutil.copytree(ROOT,trial)
        for c in (8,9):
            path=trial/f"proofs/c{c}.lrat.gz";original=path.read_bytes();payload=gzip.decompress(original)
            rewritten=gzip.compress(payload,compresslevel=1,mtime=95)
            if rewritten==original:raise ValueError("container control did not change bytes")
            path.write_bytes(rewritten)
        result=run(trial)
        if result.returncode:raise ValueError("equivalent gzip containers rejected: "+result.stderr)
    print(json.dumps({'status':'PASS','rejected':len(controls),'controls':controls,
                      'equivalent_recompressed_proofs_accepted':2},sort_keys=True))


if __name__ == '__main__':
    main()

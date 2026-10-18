#!/usr/bin/env python3
"""Full replay, minimal-source relocation and actual evidence corruption tests.

Apache-2.0. Prepared for ToikY with substantial OpenAI Codex assistance.
"""
import gzip
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(ok,message):
    if not ok: raise ValueError(message)


def invoke(path,arguments=(),accepted=True):
    start = time.monotonic()
    r = subprocess.run([sys.executable,'-I','-O','-B',str(path),*arguments],
                       capture_output=True,text=True,timeout=300)
    need((r.returncode == 0) == accepted,'unexpected result '+str(path)+'\n'+r.stdout+r.stderr)
    if accepted: need('PASS_' in r.stdout,'missing success marker')
    return r.stdout.strip(),round(time.monotonic()-start,3)


def snapshot():
    return {str(p.relative_to(HERE)):hashlib.sha256(p.read_bytes()).hexdigest()
            for p in HERE.rglob('*') if p.is_file() and '__pycache__' not in p.parts}


def main():
    before = snapshot()
    for name in ('verify.py','independent.py'):
        output,seconds = invoke(HERE/name)
        print(output);print('REPLAY_SECONDS '+name+'='+str(seconds))
    sources = json.loads((HERE/'SOURCES.json').read_text())
    count = 0
    with tempfile.TemporaryDirectory(prefix='seed17 cold package with spaces ') as temp:
        root = Path(temp);package = root/'research'/HERE.name
        shutil.copytree(HERE,package)
        for entry in sources['inputs']:
            dest = root/entry['path'];dest.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(ROOT/entry['path'],dest)
        invoke(package/'verify.py',('--witness-only',))
        candidate = package/'CANDIDATE.json.gz';original = candidate.read_bytes()
        # A recompressed equivalent payload must pass; compression is not mathematics.
        candidate.write_bytes(gzip.compress(gzip.decompress(original),mtime=12345))
        invoke(package/'verify.py',('--witness-only',));candidate.write_bytes(original)
        decoded = json.loads(gzip.decompress(original))
        for mode in ('omitted-chain-preparation','wrong-D-frame','changed-raw-continuation'):
            bad = json.loads(gzip.decompress(original))
            if mode == 'omitted-chain-preparation':bad['D'].pop(236)
            elif mode == 'wrong-D-frame':bad['D'][236][0] = 1
            else:bad['A'][0][2] = []
            candidate.write_bytes(gzip.compress(json.dumps(bad).encode(),mtime=0))
            invoke(package/'verify.py',('--witness-only',),False);count += 1
        candidate.write_bytes(original)
        certificate = package/'CERTIFICATE.json';original_cert = certificate.read_bytes()
        for mode in ('undercharged','boolean-gain','missing-source-pin','duplicate-key'):
            bad = json.loads(original_cert)
            if mode == 'undercharged':bad['winner']['invoice']['ADDs'] -= 4
            elif mode == 'boolean-gain':bad['winner']['gain'] = True
            elif mode == 'missing-source-pin':bad['source_pins'] -= 1
            if mode == 'duplicate-key':
                certificate.write_bytes(original_cert.replace(b'"new_kappa": false',b'"new_kappa": false, "new_kappa": false'))
            else:certificate.write_text(json.dumps(bad))
            invoke(package/'verify.py',('--witness-only',),False);count += 1
        certificate.write_bytes(original_cert)
        source = root/sources['inputs'][0]['path'];raw = source.read_bytes()
        source.write_bytes(raw+b'changed source')
        invoke(package/'verify.py',('--witness-only',),False);count += 1;source.write_bytes(raw)
        code = package/'independent.py';raw = code.read_bytes()
        code.write_bytes(raw+b'\n# changed verifier\n')
        invoke(package/'verify.py',('--witness-only',),False);count += 1;code.write_bytes(raw)
        manifest = package/'SOURCES.json';raw = manifest.read_bytes()
        changed = json.loads(raw)
        # Preserve count13 while hiding a consumed source behind a duplicate.
        changed['package_sources'][0] = changed['package_sources'][1]
        manifest.write_text(json.dumps(changed))
        invoke(package/'verify.py',('--witness-only',),False);count += 1;manifest.write_bytes(raw)
        receipt = package/'INDEPENDENT.json';absent = package/'INDEPENDENT.json.absent'
        receipt.rename(absent)
        invoke(package/'independent.py',(),False)
        need(not receipt.exists(),'default independent replay must not create missing evidence')
        count += 1;absent.rename(receipt)
        invoke(package/'verify.py',('--witness-only',))
    need(count == 11,'actual package fault coverage')
    need(before == snapshot(),'verification must preserve all saved evidence')
    print('PASS_R439_CHAIN_PACKAGE full_censuses=2 trials=32 controls=11 relocation=1 no_new_kappa')


if __name__ == '__main__':
    main()

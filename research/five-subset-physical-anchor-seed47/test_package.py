#!/usr/bin/env python3
"""Full exact replay, offline relocation and on-disk corruption controls.

Apache-2.0. Prepared for ToikY with substantial OpenAI Codex assistance.
"""
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


def need(ok, message):
    if not ok:
        raise ValueError(message)


def invoke(file, args=(), accepted=True):
    start = time.monotonic()
    r = subprocess.run([sys.executable, '-I', '-O', '-B', str(file), *args],
                       capture_output=True, text=True, timeout=180)
    need((r.returncode == 0) == accepted, 'unexpected replay: ' + str(file) + '\n' + r.stdout + r.stderr)
    if accepted:
        need('PASS_' in r.stdout, 'missing success marker')
    return r.stdout.strip(), round(time.monotonic() - start, 3)


def snapshot():
    return {str(p.relative_to(HERE)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in HERE.rglob('*') if p.is_file() and '__pycache__' not in p.parts}


def main():
    original = snapshot()
    for name in ('verify.py', 'independent.py'):
        out, seconds = invoke(HERE / name)
        print(out)
        print('REPLAY_SECONDS ' + name + '=' + str(seconds))
    sources = json.loads((HERE / 'SOURCES.json').read_text())
    count = 0
    with tempfile.TemporaryDirectory(prefix='seed47 physical export with spaces ') as temp:
        root = Path(temp)
        package = root / 'research' / HERE.name
        shutil.copytree(HERE, package)
        for rec in sources['repository_inputs']:
            dst = root / rec['path']
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / rec['path'], dst)
        invoke(package / 'verify.py', ('--quick',))
        invoke(package / 'independent.py')
        file = package / 'PROGRAMS.json'
        raw = file.read_bytes()
        for fault in ('omit-birth', 'bad-address-map', 'boolean-rank', 'wrong-half', 'duplicate-key'):
            p = json.loads(raw)
            if fault == 'omit-birth':
                del p['programs'][6]['stream'][1]
            elif fault == 'bad-address-map':
                p['programs'][6]['stream'][0][2][0] = p['programs'][6]['stream'][0][2][1]
            elif fault == 'boolean-rank':
                p['programs'][6]['stream'][1][2] = True
            elif fault == 'wrong-half':
                x = next(x for x in p['programs'][6]['stream'] if x[0] == 'AXPY' and x[4] == 1)
                x[4] = 0
            if fault == 'duplicate-key':
                file.write_bytes(raw.replace(b'"h": 9', b'"h": 9, "h": 9'))
            else:
                file.write_text(json.dumps(p))
            invoke(package / 'verify.py', ('--quick',), False)
            count += 1
        file.write_bytes(raw)
        receipt = package / 'RESULT.json'
        raw = receipt.read_bytes()
        p = json.loads(raw)
        p['programs'][6]['invoice']['rank_mass'] -= 9
        receipt.write_text(json.dumps(p))
        invoke(package / 'verify.py', ('--quick',), False)
        count += 1
        receipt.write_bytes(raw)
        file = package / sources['retained_inputs'][0]['path']
        raw = file.read_bytes()
        file.write_bytes(raw + b'changed input')
        invoke(package / 'verify.py', ('--quick',), False)
        count += 1
        file.write_bytes(raw)
        manifest = package / 'SOURCES.json'
        raw = manifest.read_bytes()
        p = json.loads(raw)
        p['package_sources'][0] = p['package_sources'][1]
        manifest.write_text(json.dumps(p))
        invoke(package / 'verify.py', ('--quick',), False)
        count += 1
        manifest.write_bytes(raw)
        file = package / 'independent.py'
        raw = file.read_bytes()
        file.write_bytes(raw + b'\n# changed independent checker\n')
        invoke(package / 'verify.py', ('--quick',), False)
        count += 1
        file.write_bytes(raw)
        receipt = package / 'INDEPENDENT.json'
        raw = receipt.read_bytes()
        receipt.unlink()
        invoke(package / 'independent.py', accepted=False)
        need(not receipt.exists(), 'default replay created absent evidence')
        count += 1
        receipt.write_bytes(raw)
        invoke(package / 'verify.py', ('--quick',))
    need(count == 10, 'file fault coverage')
    need(original == snapshot(), 'default replay changed saved package')
    print('PASS_SEED47_PHYSICAL_PACKAGE programs=7 columns=6656 controls=10 relocation=1 no_new_kappa')


if __name__ == '__main__':
    main()

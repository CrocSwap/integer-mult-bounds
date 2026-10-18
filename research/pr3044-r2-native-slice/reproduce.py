#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Optional inherited artifact regeneration, separate from independent verification."""
import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import types

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
ENGINE = 'research/two-sided-helper-extraction/vendor/fastnative/vendor/native/new/code/borrow/'
TOOLS = ('bw_transport.py', 'bw_emit.py', 'bw_phases.py', 'bw_adapters.py',
         'bw_gauss.py', 'vendor/clifford/clifford_exact.py')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', required=True, type=Path, help='new, disposable directory')
    args = ap.parse_args()
    verifier = types.ModuleType('r2_reproduction_binding')
    verifier.__file__ = str(PACKAGE / 'verify.py')
    exec(compile((PACKAGE / 'verify.py').read_bytes(), verifier.__file__, 'exec'), verifier.__dict__)
    blobs = verifier.pin_inputs()
    manifest = json.loads(blobs[verifier.SOURCE + 'SOURCE-MANIFEST.json'])
    args.output.mkdir(parents=True, exist_ok=False)
    for name in TOOLS:
        raw = blobs[ENGINE + name]
        verifier.need(hashlib.sha256(raw).hexdigest() == manifest['new/code/borrow/' + name],
                      'original release engine binding')
        target = args.output / 'tools' / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
    results = {}
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONUTF8='1')
    env.pop('PYTHONOPTIMIZE', None)
    for tag in ('base', 'extra'):
        retained = verifier.artifacts(blobs, tag, PACKAGE / 'data')
        word = args.output / f'WORD-{tag}.json.gz'
        word.write_bytes(blobs[verifier.SOURCE + f'WORD-{tag}.json.gz'])
        output = args.output / tag
        stages = [('bw_transport.py', [word, output]), ('bw_emit.py', [output]),
                  ('bw_adapters.py', [output / 'CANONICAL-WORD.json.gz', output / 'RESIDUAL-ADAPTERS.json',
                                      output / 'WRAPPERS.json']), ('bw_phases.py', [output])]
        results[tag] = {'stages': [], 'artifacts': {}}
        for tool, arguments in stages:
            start = time.monotonic()
            with (args.output / f'{tag}-{tool}.log').open('w') as log:
                subprocess.run([sys.executable, '-I', '-B', str(args.output / 'tools' / tool),
                                *map(str, arguments)], env=env, stdout=log, stderr=subprocess.STDOUT,
                               timeout=300, check=True)
            results[tag]['stages'].append({'tool': tool, 'seconds': time.monotonic() - start})
        for name in verifier.FILES:
            candidate = verifier.read(output / name)
            verifier.need(candidate == retained[name], 'regenerated proof-relevant payload: ' + name)
            results[tag]['artifacts'][name] = hashlib.sha256((output / name).read_bytes()).hexdigest()
        print('PASS_REGENERATED_NATIVE_PAYLOADS', tag, flush=True)
    (args.output / 'REGENERATION.json').write_text(json.dumps(results, indent=2) + '\n')


if __name__ == '__main__':
    main()

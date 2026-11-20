#!/usr/bin/env python3
"""Explicit optimized replays with fresh child bytecode namespaces."""
from pathlib import Path
import json
import subprocess
import sys
import tempfile
import time

HERE = Path(__file__).resolve().parent


def main():
    cases = [('check_source_predicates.py',90,[]), ('verify_application.py',120,[]),
             ('verify_fresh_catalogue.py',30,[]),
             ('review/binary/check_binary_seams.py',90,['--inputs',str(HERE/'inputs')]),
             ('review/complex/check_complex_seam.py',120,
              ['--word',str(HERE/'inputs/research/shared-wire-split-composition/data/final.json.gz'),
               '--caller',str(HERE/'inputs/research/shared-wire-split-composition/data/caller.json')]),
             ('verify_package.py',30,[])]
    results = []
    for relative, bound, extra in cases:
        started = time.monotonic()
        with tempfile.TemporaryDirectory(prefix='selected-native-pyc-') as cache:
            command = [sys.executable,'-I','-O','-B','-X','pycache_prefix='+cache,str(HERE/relative),*extra]
            result = subprocess.run(command,capture_output=True,text=True,timeout=bound)
        if result.returncode:
            raise ValueError(relative+' failed: '+result.stdout+result.stderr)
        if relative.startswith('review/'):
            expected = json.loads((HERE/relative).with_name('RESULT.json').read_text())
            if json.loads(result.stdout) != expected:
                raise ValueError(relative+' disagrees with the frozen independent receipt')
        results.append(dict(command=relative,exit_code=0,seconds=time.monotonic()-started))
    print(json.dumps(dict(status='PASS_OPTIMIZED_SELECTED_NATIVE_REPLAYS',results=results),indent=2))


if __name__ == '__main__':
    main()

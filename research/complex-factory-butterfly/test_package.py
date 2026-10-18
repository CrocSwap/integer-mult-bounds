#!/usr/bin/env python3
"""Minimal source-closure replay and meaningful adverse packaging controls.

Ross Richardson with substantial OpenAI Codex assistance. Apache-2.0.
"""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PACKAGE = HERE.relative_to(ROOT)


def run(root, *args, expect=None):
    result = subprocess.run([sys.executable, '-I', '-O', '-B',
        str(root / PACKAGE / 'verify.py'), *map(str,args)], cwd=root.parent,
        text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if expect is None:
        if result.returncode != 0 or 'PASS_FACTORY_BUTTERFLY' not in result.stdout:
            raise ValueError(result.stdout)
    elif result.returncode == 0 or expect not in result.stdout:
        raise ValueError('adverse control failed for unexpected reason: ' + result.stdout)
    return result.stdout


def main():
    with tempfile.TemporaryDirectory(prefix='factory package with spaces ') as tmp:
        root = Path(tmp) / 'minimal checkout'
        sources = json.loads((HERE / 'SOURCES.json').read_text())['files']
        for relative in sorted(set(sources) | {str(p.relative_to(ROOT))
                for p in HERE.iterdir() if p.is_file()}):
            target = root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / relative, target)
        run(root)
        candidate = root / PACKAGE / 'candidate.json'
        original = candidate.read_text()
        data = json.loads(original)
        next(e for e in data['replacement'] if e[0] == 'add')[3] *= -1
        candidate.write_text(json.dumps(data))
        run(root, expect='exact local map differs')
        candidate.write_text(original)
        relative = 'research/complex-factory5-resynthesis/CIRCUIT.json'
        source = root / relative
        saved = source.read_bytes()
        source.write_bytes(saved + b' ')
        run(root, expect='source changed: ' + relative)
        source.write_bytes(saved)
        existing = Path(tmp) / 'existing.json'
        existing.write_text('keep this file\n')
        run(root, '--write', existing, expect='refusing to overwrite a receipt')
        if existing.read_text() != 'keep this file\n':
            raise ValueError('existing output changed')
        run(root, '--out', root, expect='FileExistsError')
    print('PASS_FACTORY_PACKAGE minimal_source_closure=1 rejections=4 optimized=True')


if __name__ == '__main__':
    main()

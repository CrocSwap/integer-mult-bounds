#!/usr/bin/env python3
"""Relocation and real on-disk fault controls; Apache-2.0, Codex assisted."""
import json
import pathlib
import shutil
import subprocess
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent


def run(package, output):
    return subprocess.run([sys.executable, '-I', '-O', '-B',
                           str(package/'replay.py'), '--out', str(output)],
                          cwd=output.parent, text=True, capture_output=True,
                          timeout=120)


def main():
    with tempfile.TemporaryDirectory(prefix='two root package ') as work:
        root = pathlib.Path(work)
        package = root/'read only copy'
        shutil.copytree(HERE, package)
        for p in package.rglob('*'):
            p.chmod(0o555 if p.is_dir() else 0o444)
        package.chmod(0o555)
        try:
            result = run(package, root/'valid')
            if result.returncode or 'controls=28 machine_fixtures=36' not in result.stdout:
                raise ValueError('relocated replay: '+result.stdout+result.stderr)
        finally:
            package.chmod(0o755)
            for p in package.rglob('*'):
                p.chmod(0o755 if p.is_dir() else 0o644)
        controls = []
        for label in ('source', 'certificate', 'instruction', 'tape-trace'):
            mutant = root/label
            shutil.copytree(HERE, mutant)
            if label == 'source':
                p = mutant/'PR1526-README.md'
                p.write_text(p.read_text()+'\nchanged source\n')
            elif label == 'certificate':
                p = mutant/'expected/two_root_head_formula.json'
                data = json.loads(p.read_text())
                data['delta_against_compact13'][4] += 1
                p.write_text(json.dumps(data))
            elif label == 'instruction':
                p = mutant/'two_root_verify.py'
                text = p.read_text()
                old = "('R',2,1,0)"
                if old not in text:
                    raise ValueError('missing mutation target')
                p.write_text(text.replace(old,"('R',1,1,0)",1))
            else:
                p = mutant/'two_root_invoice.py'
                text = p.read_text()
                old = "out['head_moves']+=abs(a-pos)"
                if old not in text:
                    raise ValueError('missing trace mutation target')
                p.write_text(text.replace(old,"out['head_moves']+=abs(a-pos)+1"))
            output = root/(label+' output')
            result = run(mutant, output)
            if result.returncode == 0:
                raise ValueError('accepted '+label+' mutation')
            if label == 'source' and output.exists():
                raise ValueError('source failure occurs after output creation')
            controls.append(label)
        print('PASS_TWO_ROOT_PACKAGE relocation=1 corruptions='+str(len(controls)))


if __name__ == '__main__':
    main()

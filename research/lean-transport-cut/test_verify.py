#!/usr/bin/env python3
"""Artifact-boundary controls for the source/finite replay (stdlib only)."""
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
INPUT = 'research/p104-native-channel/inputs/LOWRANK-WITNESS.json'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def main():
    groups = []
    with tempfile.TemporaryDirectory(prefix='cut-artifacts-') as directory:
        root = Path(directory)
        package = root/'research'/'lean-transport-cut'
        package.mkdir(parents=True)
        for name in ['verify.py', 'EXPECTED.json', 'SourceCut.lean']:
            shutil.copyfile(HERE/name, package/name)
        source = root/INPUT
        source.parent.mkdir(parents=True)
        shutil.copyfile(ROOT/INPUT, source)
        def run(*args, optimized=False):
            cmd = [sys.executable, '-I', '-B'] + (['-O'] if optimized else [])
            return subprocess.run(cmd+[str(package/'verify.py'), *map(str,args)],
                                  cwd=root, capture_output=True, text=True, timeout=20)
        def rejected(message):
            result = run(optimized=True)
            require(result.returncode != 0 and message in result.stderr,
                    f'control not rejected at {message}: {result.stdout} {result.stderr}')
        baseline = run()
        optimized = run(optimized=True)
        require(baseline.returncode == optimized.returncode == 0, baseline.stderr+optimized.stderr)
        require(baseline.stdout == optimized.stdout, 'assertion-mode difference')
        groups.append('relocated_normal_and_optimized')
        # Read-only source export must remain reusable.
        for p in [source, *package.iterdir()]:
            p.chmod(0o444)
        package.chmod(0o555)
        require(run().returncode == 0, 'read-only replay failed')
        package.chmod(0o755)
        for p in [source, *package.iterdir()]:
            p.chmod(0o644)
        groups.append('read_only_export')
        expected = (package/'EXPECTED.json').read_text()
        altered = json.loads(expected)
        altered['source_sides'][0] = 1
        (package/'EXPECTED.json').write_text(json.dumps(altered))
        rejected('receipt mismatch')
        (package/'EXPECTED.json').write_text(expected)
        groups.append('typed_receipt_rejection')
        lean = (package/'SourceCut.lean').read_text()
        (package/'SourceCut.lean').write_text(lean.replace('inwardCount = 8', 'inwardCount = 7'))
        rejected('Lean source binding mismatch')
        (package/'SourceCut.lean').write_text(lean)
        groups.append('generated_lean_rejection')
        data = source.read_bytes()
        source.write_bytes(data+b'\n')
        rejected('immutable witness hash')
        source.write_bytes(data)
        groups.append('immutable_source_rejection')
        occupied = root/'occupied.json'
        occupied.write_text('sentinel')
        result = run('--write', occupied)
        require(result.returncode != 0 and occupied.read_text() == 'sentinel', 'overwritten output')
        groups.append('exclusive_output')
        (package/'EXPECTED.json').unlink()
        result = run()
        require(result.returncode != 0 and 'FileNotFoundError' in result.stderr, 'missing receipt accepted')
        groups.append('missing_receipt')
    spec = importlib.util.spec_from_file_location('cut_formal_checker', HERE/'check_lean.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    normal = "'N.one' depends on axioms: [propext,\n Classical.choice, Quot.sound]\n'N.two' does not depend on any axioms\n"
    module.audit(normal, 'N', ['one','two'])
    for bad in [normal.replace('propext', 'sorryAx'), normal.replace('propext', 'N.hidden'),
                normal.splitlines()[0], normal+normal]:
        try:
            module.audit(bad, 'N', ['one','two'])
        except ValueError:
            pass
        else:
            raise ValueError('axiom-audit mutation escaped')
    groups.append('axiom_audit_missing_duplicate_and_forbidden')
    print('PASS_TRANSPORT_CUT_ARTIFACT_CONTROLS groups='+str(len(groups)))


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Relocated optimized replay and deliberate mathematical/packaging faults.

Hanson Sun (@bbMisk), with substantial OpenAI Codex assistance. Apache-2.0.
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


def require(ok, message):
    if not ok:
        raise ValueError(message)


def invoke(args, cwd, expected=None):
    result = subprocess.run([sys.executable, '-I', '-O', '-B', *args],
                            cwd=cwd, capture_output=True, text=True, timeout=180)
    text = result.stdout + result.stderr
    if expected is None:
        require(result.returncode == 0 and 'PASS_PACKED_SOURCE_FIBERS' in text,
                'relocated replay failed: ' + text)
        print(result.stdout.strip())
    else:
        require(result.returncode != 0 and expected in text,
                'fault not rejected at intended boundary: ' + text)
    return text


def main():
    with tempfile.TemporaryDirectory(prefix='packed-source-fibers-') as directory:
        root = Path(directory)
        package = root / PACKAGE
        shutil.copytree(HERE, package)
        sources = json.loads((HERE / 'SOURCES.json').read_text())
        for row in sources['files']:
            if row['usage'] == 'input':
                target = root / row['path']
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / row['path'], target)
        verify = package / 'verify.py'
        invoke([str(verify)], root)
        original = verify.read_text()
        loader = ("import importlib.util; "
                  f"s=importlib.util.spec_from_file_location('audit', {str(verify)!r}); "
                  "m=importlib.util.module_from_spec(s); s.loader.exec_module(m); ")
        faults = [
            ('wrong gap numerator', 'Q(2, radix ** (right - left))',
             'Q(1, radix ** (right - left))', 'pattern_checks()', 'source-gap product formula'),
            ('ignore zeros between ones', 'radix ** (right - left)',
             'radix', 'pattern_checks()', 'source-gap product formula'),
            ('target-only acceptance', '(got_u, got_w) == (u ^ c, w)',
             'got_u == (u ^ c)', 'digit_checks()', 'boundary agreement'),
            ('wrong carry decay', 's: {0: b*(b-1), s: b}',
             's: {0: b*(b-1), s: b*b}', 'digit_checks()', 'conditional count table'),
        ]
        for name, old, new, call, expected in faults:
            require(old in original, 'missing mutation site: ' + name)
            verify.write_text(original.replace(old, new))
            invoke(['-c', loader + 'm.' + call], root, expected)
            verify.write_text(original)
        input_path = root / 'tests/test_finite_identities.py'
        input_bytes = input_path.read_bytes()
        input_path.write_bytes(input_bytes + b'\n# deliberate source drift\n')
        invoke(['-c', loader + 'm.source_check()'], root, 'source SHA256 drift')
        input_path.write_bytes(input_bytes)
        pins_path = package / 'SOURCES.json'
        pin_text = pins_path.read_text()
        pins = json.loads(pin_text)
        pins['files'] = [row for row in pins['files']
                         if row['path'] != 'tests/test_finite_identities.py']
        pins_path.write_text(json.dumps(pins))
        invoke(['-c', loader + 'm.source_check()'], root, 'incomplete input inventory')
        pins_path.write_text(pin_text)
        expected_path = package / 'EXPECTED.json'
        expected_text = expected_path.read_text()
        changed = json.loads(expected_text)
        changed['digit_cases'] -= 1
        expected_path.write_text(json.dumps(changed))
        invoke([str(verify)], root, 'receipt mismatch')
        expected_path.write_text(expected_text)
        invoke([str(verify), '--write', str(expected_path)], root, 'refusing to overwrite receipt')
        require(expected_path.read_text() == expected_text, 'overwrite changed the receipt')
    print('PASS_PACKED_SOURCE_PACKAGE mathematical_faults=4 packaging_faults=4 relocated_optimized_replay=PASS')


if __name__ == '__main__':
    main()

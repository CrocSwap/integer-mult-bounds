#!/usr/bin/env python3
"""Run relocated positive replay and fail-closed packaging controls."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    rows = []
    with tempfile.TemporaryDirectory(prefix='packed convolution isolated ') as temp:
        root = Path(temp)
        copied = root/'package with spaces'
        shutil.copytree(ROOT, copied)
        entry = copied/'verify.py'
        def invoke(name, flags=(), extra=(), expected_error=None):
            command = [sys.executable, '-I', '-B']+list(flags)+[str(entry)]+list(extra)
            process = subprocess.run(command, cwd=str(root), text=True, capture_output=True, timeout=30)
            if expected_error is None:
                require(process.returncode == 0 and 'PASS_INDEPENDENT_SIGNED_PACKED_CONVOLUTION' in process.stdout, name+' did not pass: '+process.stderr)
            else:
                require(process.returncode != 0 and expected_error in process.stderr, name+' did not fail for the expected reason: '+process.stderr)
            rows.append({'control': name, 'exit_code': process.returncode, 'expected_failure': expected_error})
        receipt = root/'fresh receipt.json'
        invoke('relocated-full-replay', extra=('--output', str(receipt)))
        require(receipt.read_bytes() == (ROOT/'EXPECTED.json').read_bytes(), 'relocated full receipt differs')
        invoke('optimized-python-rejected', flags=('-O',), expected_error='Run without -O')
        original = (copied/'vendor/branchfree.py').read_bytes()
        (copied/'vendor/branchfree.py').write_bytes(original+b'\n# corruption control\n')
        invoke('changed-source-rejected', expected_error='source SHA256 mismatch')
        (copied/'vendor/branchfree.py').write_bytes(original)
        expected = (copied/'EXPECTED.json').read_bytes()
        bad = json.loads(expected)
        bad['totals']['source_calls'] += 1
        (copied/'EXPECTED.json').write_text(json.dumps(bad))
        invoke('changed-evidence-rejected', expected_error='complete receipt differs')
        (copied/'EXPECTED.json').unlink()
        invoke('missing-evidence-rejected', expected_error='FileNotFoundError')
        (copied/'EXPECTED.json').write_bytes(expected)
        output = root/'existing sentinel.json'
        sentinel = b'preserve this existing output\n'
        output.write_bytes(sentinel)
        invoke('existing-output-rejected', extra=('--output', str(output)), expected_error='FileExistsError')
        require(output.read_bytes() == sentinel, 'existing output changed')
    result = {'status':'PASS_PACKED_CONVOLUTION_PACKAGE_CONTROLS',
              'receipt_sha256': hashlib.sha256((ROOT/'EXPECTED.json').read_bytes()).hexdigest(), 'checks':rows}
    if args.output:
        with args.output.open('x') as stream:
            json.dump(result, stream, indent=2, sort_keys=True)
            stream.write('\n')
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()

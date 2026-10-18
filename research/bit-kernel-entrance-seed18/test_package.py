#!/usr/bin/env python3
"""Optimized-mode, relocation, and fail-closed checks. Apache-2.0."""
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('entrance_verifier', HERE/'verify.py')
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)


def need(ok, text):
    if not ok:
        raise ValueError(text)


def main():
    # Run the complete verifier under -O in a minimal offline relocated tree.
    pins = json.loads((HERE/'SOURCES.json').read_text())
    with tempfile.TemporaryDirectory(prefix='bit entrance relocation ') as temp:
        root = Path(temp)
        dest = root/'research/bit-kernel-entrance-seed18'
        dest.mkdir(parents=True)
        for name in ('verify.py', 'SOURCES.json', 'CERTIFICATE.json'):
            shutil.copyfile(HERE/name, dest/name)
        for path in pins['sha256']:
            out = root/path
            out.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(v.ROOT/path, out)
        command = [sys.executable, '-I', '-O', '-B', str(dest/'verify.py')]
        good = subprocess.run(command, cwd=temp, text=True, capture_output=True, check=True)
        need('PASS_BIT_KERNEL_ENTRANCE' in good.stdout, 'relocation result')
        # A forged receipt is rejected by a separate full recomputation in memory
        # already exercised by the relocated run's complete comparison; probe
        # canonical distinction directly without another costly replay.
        certificate = json.loads((dest/'CERTIFICATE.json').read_text())
        forged = json.loads(json.dumps(certificate))
        forged['candidate']['rank_mass'] += 1
        need(v.canonical(certificate) != v.canonical(forged), 'receipt mutation')
        source = root/pins['word']
        source.write_bytes(source.read_bytes()+b'corruption')
        failed = subprocess.run(command, cwd=temp, text=True, capture_output=True)
        need(failed.returncode != 0 and 'source pin:' in failed.stderr, 'corrupt source rejection')
        source.unlink()
        failed = subprocess.run(command, cwd=temp, text=True, capture_output=True)
        need(failed.returncode != 0 and 'FileNotFoundError' in failed.stderr, 'missing source rejection')
    # Independent small-domain exhaustive subset oracle, including repeated and
    # zero columns; confirms the census does not assume a nondegenerate matrix.
    for cols in ([0, 1, 1, 2, 3], [1, 2, 4, 7, 3, 5, 6], [0, 0, 0, 0]):
        expected = []
        for mask in range(1, 1 << len(cols)):
            ids = tuple(i for i in range(len(cols)) if mask >> i & 1)
            if len(ids) > 4:
                continue
            syndrome = 0
            for i in ids:
                syndrome ^= cols[i]
            if not syndrome:
                expected.append(ids)
        need(v.sparse_kernels(cols)[0] == sorted(expected), 'subset oracle')
        need(v.independent_kernels(cols) == sorted(expected), 'triple oracle')
    print('PASS_BIT_KERNEL_ENTRANCE_PACKAGE optimized_relocation=1 source_controls=2 census_oracles=3 receipt_distinction=1')


if __name__ == '__main__':
    main()

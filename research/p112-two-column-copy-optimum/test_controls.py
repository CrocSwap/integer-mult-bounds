#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Deterministic adversarial controls; writes only to an automatically removed tempdir."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('copy_optimum_verify', HERE / 'verify.py')
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)


def reject(label, expected_reason, fn):
    try:
        fn()
    except ValueError as exc:
        v.require(str(exc) == expected_reason,
                  label + ': expected ' + repr(expected_reason) + ', got ' + repr(str(exc)))
        return label
    raise ValueError('negative control accepted: ' + label)


def main():
    src = v.load_source()
    witness = v.checked_json(HERE / 'WITNESS.json')
    v.validate_witness(witness)
    receipt = v.checked_json(HERE / 'CERTIFICATE.json')
    names = []
    for label, field, replacement in [('boolean root', 'root_lines', True), ('floating root', 'root_lines', 0.0), ('boolean label', 'binary_ports', True)]:
        bad = copy.deepcopy(src)
        if field == 'root_lines':
            bad[field][0][0] = replacement
        else:
            bad[field][0] = replacement
        names.append(reject(label, 'root numeric domain' if field == 'root_lines' else 'label numeric domain', lambda: v.validate_source(bad)))
    bad = copy.deepcopy(witness)
    bad['M'][8][8] = '0'
    names.append(reject('wrong compensation', 'coefficient compensation / ordinary duality', lambda: v.validate_witness(bad)))
    bad = copy.deepcopy(witness)
    bad['N'][0][0] = True
    names.append(reject('boolean rational', 'canonical rational domain', lambda: v.validate_witness(bad)))
    bad = copy.deepcopy(witness)
    bad['ranks'][0] = True
    names.append(reject('boolean COPY rank', 'COPY numeric domain', lambda: v.validate_witness(bad)))
    bad = copy.deepcopy(witness)
    bad['M'][0][0] = '2/2'
    names.append(reject('noncanonical rational', 'canonical rational domain', lambda: v.validate_witness(bad)))
    bad = copy.deepcopy(receipt)
    bad['kernels']['R'][0]['rank'] ^= 1
    names.append(reject('corrupt kernel certificate', 'certificate mismatch', lambda: v.compare(receipt, bad, 'certificate')))
    # A valid dual basis but altered submitted rank must also be rejected.
    bad = copy.deepcopy(witness)
    bad['ranks'][0] = 7
    v.validate_witness(bad)
    names.append(reject('corrupt witness rank', 'witness mismatch', lambda: v.compare(receipt['witness'], bad, 'witness')))
    with tempfile.TemporaryDirectory(prefix='copy-optimum-controls-') as td:
        export = Path(td) / 'export' / 'package'
        shutil.copytree(HERE, export, ignore=shutil.ignore_patterns('__pycache__'))
        for name, digest in [('ROOTS.json', v.EXTRACT_SHA), ('SOURCES.json', v.MANIFEST_SHA)]:
            path = export / name
            original = path.read_bytes()
            path.write_bytes(original + b' ')
            names.append(reject(name + ' source drift', 'source digest mismatch: ' + name, lambda: v.checked_json(path, digest)))
            path.write_bytes(original)
        # Present-but-corrupt canonical upstream input must not be ignored.
        upstream = Path(td) / v.SOURCE
        upstream.parent.mkdir(parents=True)
        original_upstream = HERE.parents[1] / v.SOURCE
        if original_upstream.exists():
            upstream.write_bytes(original_upstream.read_bytes())
            v.compare(v.load_source(export), src, 'present correct upstream')
            raw = upstream.read_bytes()
            upstream.write_bytes(bytes([raw[0] ^ 1]) + raw[1:])
        else:
            upstream.write_bytes(b'corrupted canonical prototype\n')
        names.append(reject('present corrupt prototype', 'source digest mismatch: PROTOTYPE.json', lambda: v.load_source(export)))
        upstream.unlink()
        # Invalid --write inputs must fail for the intended reason, before output exists.
        def failed_write(label, expected_reason):
            target = Path(td) / (label + '.json')
            run = subprocess.run([sys.executable, '-I', '-O', '-B', str(export / 'verify.py'), '--write', str(target)], text=True, capture_output=True, timeout=10)
            v.require(run.returncode == 1 and run.stderr.strip() == 'FAIL: ' + expected_reason,
                      label + ': wrong exit/reason: ' + repr((run.returncode, run.stderr)))
            v.require(not target.exists(), label + ': invalid input created output')
            names.append(label)
        wp = export / 'WITNESS.json'
        saved_witness = wp.read_bytes()
        for label, reason, change in [
                ('write invalid rational', 'canonical rational domain', lambda w: w['M'][0].__setitem__(0, '1.0')),
                ('write invalid rank', 'COPY numeric domain', lambda w: w['ranks'].__setitem__(0, 8.0))]:
            invalid = copy.deepcopy(witness)
            change(invalid)
            wp.write_text(json.dumps(invalid))
            failed_write(label, reason)
        wp.write_bytes(saved_witness)
        rp = export / 'ROOTS.json'
        saved_roots = rp.read_bytes()
        rp.write_bytes(b'{malformed')
        failed_write('write invalid source', 'source digest mismatch: ROOTS.json')
        rp.write_bytes(saved_roots)
        # Default replay from a detached export with read-only package files.
        before = {f.name: hashlib.sha256(f.read_bytes()).hexdigest() for f in export.iterdir() if f.is_file()}
        for path in export.iterdir():
            if path.is_file():
                path.chmod(0o444)
        export.chmod(0o555)
        run = subprocess.run([sys.executable, '-I', '-O', '-B', str(export / 'verify.py')], text=True, capture_output=True, timeout=150)
        v.require(run.returncode == 0, 'exported optimized replay: ' + run.stderr)
        after = {f.name: hashlib.sha256(f.read_bytes()).hexdigest() for f in export.iterdir() if f.is_file()}
        v.compare(before, after, 'read-only replay files')
        v.require(not (export / '__pycache__').exists(), 'bytecode write')
        # Explicit refusal happens before computation and preserves existing bytes.
        sentinel = Path(td) / 'existing.json'
        sentinel.write_text('do not overwrite\n')
        run = subprocess.run([sys.executable, '-I', '-O', '-B', str(export / 'verify.py'), '--write', str(sentinel)], text=True, capture_output=True, timeout=10)
        v.require(run.returncode == 1 and run.stderr.strip() == 'FAIL: --write refuses existing paths', 'overwrite control')
        v.require(sentinel.read_text() == 'do not overwrite\n', 'overwritten user file')
        # Permit automatic cleanup; package contents were never changed by replay.
        export.chmod(0o755)
    print('PASS: ' + ', '.join(names))
    print('PASS: detached read-only -I -O -B replay and explicit-write overwrite refusal')


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, TypeError, KeyError, subprocess.TimeoutExpired) as exc:
        print('FAIL: ' + str(exc), file=sys.stderr)
        sys.exit(1)

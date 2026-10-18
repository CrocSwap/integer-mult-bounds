#!/usr/bin/env python3
"""Git-free replay and integrity controls; standard library, Apache-2.0."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent


def need(condition, message):
    if not condition:
        raise ValueError(message)


def snapshot(root):
    return {str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob('*') if p.is_file()}


def run(root, *args):
    return subprocess.run([sys.executable,'-I','-O','-B',str(root/'verify.py'),*map(str,args)],
                          cwd=root.parent,capture_output=True,text=True,timeout=90)


def main():
    with tempfile.TemporaryDirectory(prefix='p104-mixed-grid-') as tmp:
        root = Path(tmp)/'standalone'
        shutil.copytree(HERE,root,ignore=shutil.ignore_patterns('__pycache__'))
        receipt = root/'RESULT.json'
        original = receipt.read_bytes()
        value = json.loads(original)
        # JSON presentation is not part of claim equality.
        receipt.write_text(json.dumps(dict(reversed(list(value.items()))),separators=(',',':')),encoding='utf-8')
        before = snapshot(root)
        result = run(root)
        need(result.returncode == 0 and 'PASS_P104_MIXED_GRID_COLLECTOR' in result.stdout, 'Git-free optimized replay: '+result.stderr)
        need(snapshot(root) == before, 'default replay must be read only')
        for key,replacement in [('minimum_outbound_extra_fractional_bits',4.0),
                                ('predecessor_receipt_unchanged',1),
                                ('private_extra_fractional_storage_bits',4095)]:
            changed = dict(value); changed[key] = replacement
            receipt.write_text(json.dumps(changed),encoding='utf-8')
            result = run(root)
            need(result.returncode != 0 and 'complete typed receipt equality' in result.stderr, 'receipt mutation: '+key)
        receipt.write_text(original.decode().replace('"status":','"status":"duplicate", "status":',1),encoding='utf-8')
        result = run(root)
        need(result.returncode != 0 and 'duplicate JSON key' in result.stderr, 'duplicate claim key')
        receipt.write_bytes(original)
        source = root/'vendor/pr2665/verify.py'
        source_bytes = source.read_bytes()
        source.write_bytes(source_bytes + b'\nraise RuntimeError("UNAUTHENTICATED_EXECUTION")\n')
        result = run(root)
        need(result.returncode != 0 and 'source SHA256' in result.stderr
             and 'UNAUTHENTICATED_EXECUTION' not in result.stderr, 'source before execution')
        source.write_bytes(source_bytes)
        result = run(root,'--unsupported')
        need(result.returncode != 0 and 'unrecognized arguments' in result.stderr, 'unknown CLI')
        destination = Path(tmp)/'occupied.json'; destination.write_bytes(b'keep\n')
        result = run(root,'--out',destination)
        need(result.returncode != 0 and destination.read_bytes() == b'keep\n', 'output overwrite')
    print('PASS_P104_MIXED_GRID_INTEGRITY git_free_read_only typed_receipt source_before_import cli')


if __name__ == '__main__':
    main()

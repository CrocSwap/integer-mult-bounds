#!/usr/bin/env python3
"""Verify source-only read-only replay, evidence binding and no-clobber."""
import importlib.util
import py_compile
import struct
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent


def need(condition, message):
    if not condition:
        raise ValueError(message)


def snapshot(root):
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob('*') if p.is_file()}


def replay(root, *args):
    return subprocess.run([sys.executable, '-I', '-O', '-B', str(root/'verify.py'), *map(str, args)],
                          cwd=root.parent, capture_output=True, text=True, timeout=30)


def check_bytecode_caches(root):
    """Cached code must not replace the authenticated arithmetic source."""
    source = root / 'vendor/fine_moment.py'
    original = source.read_bytes()
    stamp = source.stat()
    cache_dir = source.parent / '__pycache__'
    # This root is a new source-only export: no existing cache may be removed.
    need(not cache_dir.exists(), 'unexpected cache in fresh export')
    with tempfile.TemporaryDirectory(prefix='t74-cache-control-') as tmp:
        wrong_source = Path(tmp) / 'wrong.py'
        wrong_source.write_text("raise RuntimeError('UNAUTHENTICATED_BYTECODE_EXECUTED')\n")
        for mode in (py_compile.PycInvalidationMode.TIMESTAMP,
                     py_compile.PycInvalidationMode.UNCHECKED_HASH):
            for optimized in (False, True):
                cache = Path(importlib.util.cache_from_source(
                    str(source), optimization='1' if optimized else ''))
                cache.parent.mkdir(exist_ok=True)
                py_compile.compile(str(wrong_source), cfile=str(cache), dfile=str(source),
                                   doraise=True, optimize=int(optimized), invalidation_mode=mode)
                if mode == py_compile.PycInvalidationMode.TIMESTAMP:
                    data = bytearray(cache.read_bytes())
                    data[8:16] = struct.pack('<II', int(stamp.st_mtime) & 0xffffffff,
                                            stamp.st_size & 0xffffffff)
                    cache.write_bytes(data)
                before = snapshot(root)
                command = [sys.executable, '-I'] + (['-O'] if optimized else [])
                result = subprocess.run(command + ['-B', str(root / 'verify.py')],
                                        cwd=root.parent, capture_output=True, text=True, timeout=30)
                need(result.returncode == 0, 'cached code replaced pinned source: ' + result.stderr)
                need(snapshot(root) == before, 'cache control changed source or cached bytes')
                need(source.read_bytes() == original, 'cache control changed pinned source')
    shutil.rmtree(cache_dir)


def main():
    with tempfile.TemporaryDirectory(prefix='t74-width-cap-') as temp:
        dst = Path(temp)/'standalone'
        shutil.copytree(ROOT, dst, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
        before = snapshot(dst)
        for path in dst.rglob('*'):
            path.chmod(0o555 if path.is_dir() else 0o444)
        dst.chmod(0o555)
        try:
            result = replay(dst)
            need(result.returncode == 0, result.stdout+result.stderr)
            need(snapshot(dst) == before, 'read-only replay changed source')
        finally:
            dst.chmod(0o755)
            for path in dst.rglob('*'):
                path.chmod(0o755 if path.is_dir() else 0o644)
        result = replay(dst, '--record', dst/'EXPECTED.json')
        need(result.returncode != 0 and 'receipt already exists' in result.stderr, 'overwrite accepted')
        need(snapshot(dst) == before, 'overwrite changed receipt')
        check_bytecode_caches(dst)
        need(snapshot(dst) == before, 'bytecode controls changed export')
        source = dst/'inputs/pr2269-profile.json'
        old = source.read_bytes(); source.write_bytes(old+b' ')
        result = replay(dst)
        need(result.returncode != 0 and 'source digest' in result.stderr, 'altered input accepted')
        source.write_bytes(old)
        receipt = dst/'EXPECTED.json'
        changed = json.loads(receipt.read_text()); changed['certificate']['moment_lower'] = '2'
        receipt.write_text(json.dumps(changed))
        result = replay(dst)
        need(result.returncode != 0 and 'receipt mismatch' in result.stderr, 'altered expected result accepted')
    print('PASS_T74_WIDTH_CAP_EXPORT controls 8')


if __name__ == '__main__':
    main()

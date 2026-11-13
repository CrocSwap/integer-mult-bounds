"""Benign stale-bytecode control; preserves every source and prior cache."""
from pathlib import Path
import hashlib
import importlib.util
import json
import marshal
import struct
import subprocess
import sys

HERE = Path(__file__).resolve().parent


def main():
    # A legacy -B process can still read these valid timestamp caches. Their
    # only executable action is raising this explicit local-test sentinel.
    marker = 'ROUNDED_CACHE_CONTROL_READ'
    saved = {}
    before = {name: hashlib.sha256((HERE / (name + '.py')).read_bytes()).hexdigest()
              for name in ('rounded', 'endpoint', 'move')}
    old_prefix = sys.pycache_prefix
    sys.pycache_prefix = None
    try:
        for name in before:
            source = HERE / (name + '.py')
            cached = Path(importlib.util.cache_from_source(str(source)))
            saved[cached] = cached.read_bytes() if cached.exists() else None
            cached.parent.mkdir(exist_ok=True)
            stat = source.stat()
            code = compile("raise RuntimeError('" + marker + "')\n", str(source), 'exec')
            raw = importlib.util.MAGIC_NUMBER + struct.pack('<III', 0, int(stat.st_mtime), stat.st_size)
            cached.write_bytes(raw + marshal.dumps(code))
        unprotected = []
        for name in before:
            code = 'import sys;sys.path.insert(0,' + repr(str(HERE)) + ');import ' + name
            result = subprocess.run([sys.executable, '-I', '-B', '-c', code],
                                    text=True, capture_output=True)
            if result.returncode == 0 or marker not in result.stderr:
                raise ValueError('unprotected -B cache control failed: ' + name)
            unprotected.append(name)
        checked = subprocess.run([sys.executable, '-I', '-W', 'error', '-B',
                                  str(HERE / 'check_rounded.py'), '--quick'],
                                 text=True, capture_output=True, check=True)
        checked = json.loads(checked.stdout)
        bound = subprocess.run([sys.executable, '-I', '-W', 'error', '-B',
                                str(HERE / 'source_gate.py')],
                               text=True, capture_output=True, check=True)
        bound = json.loads(bound.stdout)
        if not checked['source_cache_isolated']:
            raise ValueError('protected cache isolation absent')
        return dict(marker='PASS_ROUNDED_SOURCE_CACHE_CONTROL',
                    legacy_B_reads_seeded_cache=unprotected,
                    protected_graph_sha256=checked['graph_sha256'],
                    protected_unit_marker=checked['marker'],
                    protected_source_marker=bound['marker'], sources_unchanged=True)
    finally:
        sys.pycache_prefix = old_prefix
        for path, raw in saved.items():
            if raw is None:
                path.unlink(missing_ok=True)
            else:
                path.write_bytes(raw)
        cache_dir = HERE / '__pycache__'
        if cache_dir.exists() and not any(cache_dir.iterdir()):
            cache_dir.rmdir()
        if any(hashlib.sha256((HERE / (name + '.py')).read_bytes()).hexdigest() != digest
               for name, digest in before.items()):
            raise ValueError('cache control changed a source')


if __name__ == '__main__':
    print(json.dumps(main(), indent=2, sort_keys=True))

"""Fixed small observer-control child; never used as a serializer substitute."""
import os
from pathlib import Path
import subprocess
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parent))
from bootstrap import closure
from custody import need, read_json
from effective import capture, unchanged


def main():
    mode = sys.argv[1]
    runtime_path, runtime_sha = sys.argv[2:4]
    runtime = read_json(Path(runtime_path), runtime_sha)
    package = Path(__file__).resolve().parent.parent
    before, objects = closure(runtime, package, Path(__file__).resolve(), main_path=Path(__file__).resolve())
    effective_before = capture(dict(sys.modules))
    if mode == 'allocation':
        data = bytearray(16 * 1024 * 1024)
        for i in range(0, len(data), 4096):
            data[i] = 1
        time.sleep(0.20)
    elif mode == 'concurrent':
        data = bytearray(16 * 1024 * 1024)
        for i in range(0, len(data), 4096):
            data[i] = 1
        child = subprocess.Popen([sys.executable, '-B', '-I', '-S', str(Path(__file__).resolve()), 'allocation', runtime_path, runtime_sha])
        child.wait()
        if child.returncode:
            raise SystemExit(child.returncode)
    elif mode == 'short':
        data = bytearray(1024)
    elif mode == 'timeout':
        time.sleep(2.0)
    elif mode == 'membership':
        child = subprocess.Popen([sys.executable, '-B', '-I', '-S', str(Path(__file__).resolve()), 'allocation', runtime_path, runtime_sha])
        child.wait()
        if child.returncode:
            raise SystemExit(child.returncode)
    elif mode == 'allocation-cap':
        data = bytearray(32 * 1024 * 1024)
        for i in range(0, len(data), 4096):
            data[i] = 1
        time.sleep(0.20)
    else:
        raise RuntimeError('undeclared fixture mode')
    after, actual = closure(runtime, package, Path(__file__).resolve(), main_path=Path(__file__).resolve())
    need(all(actual[k] is v for k, v in objects.items()), 'fixture callable drift')
    unchanged(effective_before, capture(dict(sys.modules)))


if __name__ == '__main__':
    main()

"""Scoped receipt, input binding, boundary and offline relocation controls."""
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(condition, message):
    if not condition:
        raise ValueError(message)


def load(name):
    spec = importlib.util.spec_from_file_location('control_' + name, HERE / (name + '.py'))
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def main():
    verifier, search = load('verify'), load('search')
    need(not verifier.same({'cost': 1}, {'cost': 1.0}), 'float receipt accepted')
    # A pending gauge may not flow through copy, non-scalar or frame boundaries.
    scale = ['scalar', ['scale', ['L', 0], 2, 1], 1]
    addition = ['scalar', ['add', ['L', 1], ['L', 0], 1, 2], 1]
    copy = ['scalar', ['copy', ['L', 2], ['L', 0]], 1]
    for barrier in (copy, ['phase', 1], ['scalar', addition[1], 2]):
        rows = list(search.intervals([scale, addition, barrier, addition]))
        need(rows and all(row['stop'] <= 2 for row in rows), 'crossed gauge barrier')
    clear = ['scalar', ['clear', ['L', 0]], 1]
    rows = list(search.intervals([scale, addition, clear]))
    need(any(row['mode'] == 'clear' and row['delta'] < 0 for row in rows),
         'free clear reset missing')
    try:
        search.lower(['add', ['L', 0], ['L', 0], 1, 1])
    except ValueError:
        pass
    else:
        raise ValueError('aliased addition accepted')
    # Only the package and its explicit source closure are copied. No Git/network.
    with tempfile.TemporaryDirectory(prefix='scale interval offline ') as work:
        target = Path(work)
        relative = HERE.relative_to(ROOT)
        shutil.copytree(HERE, target / relative, ignore=shutil.ignore_patterns('__pycache__'))
        sources = json.loads((HERE / 'SOURCES.json').read_text())['files']
        for path in sources:
            destination = target / path
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / path, destination)
        command = [sys.executable, '-I', '-O', '-B', str(target / relative / 'verify.py')]
        before = {p: (target / p).read_bytes() for p in sources}
        result = subprocess.run(command, capture_output=True, text=True)
        need(result.returncode == 0, 'offline replay failed: ' + result.stderr)
        need('backward_real_saving=66' in result.stdout, 'offline receipt missing')
        need(all((target / p).read_bytes() == raw for p, raw in before.items()), 'input changed')
        # Byte drift is rejected before executing predecessor code.
        selected = target / 'certificates/selected-result.json'
        selected.write_bytes(selected.read_bytes() + b' ')
        result = subprocess.run(command, capture_output=True, text=True)
        need(result.returncode != 0 and 'source changed:' in result.stderr,
             'source corruption accepted')
        selected.write_bytes(before['certificates/selected-result.json'])
        # A histogram-preserving replacement with floats is not exact evidence.
        census = target / relative / 'CENSUS.json'
        data = json.loads(census.read_text())
        data['backward']['intervals'] = float(data['backward']['intervals'])
        census.write_text(json.dumps(data))
        result = subprocess.run(command, capture_output=True, text=True)
        need(result.returncode != 0 and 'census drift:' in result.stderr,
             'typed census corruption accepted')
    print('PASS_SCALE_PACKAGE controls=9 offline_optimized_replay=PASS')


if __name__ == '__main__':
    main()

"""Opt-in replay of the unchanged ceiling fixtures with identical intervals."""
import argparse
from contextlib import redirect_stdout
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import sys
from fractions import Fraction

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from integer_exp import exp, require

ENGINE = 'research/complex-local-word-ceiling/ceiling.py'
FIXTURES = {'levers': 'research/complex-local-word-ceiling/levers.py',
            'selected': 'research/complex-local-word-ceiling/verify.py'}


def authenticate(root=ROOT):
    for row in json.loads((HERE/'SOURCES.json').read_text(encoding='utf-8'))['files']:
        if row['usage'] != 'input':
            continue
        raw = (root/row['path']).read_bytes()
        require(hashlib.sha256(raw).hexdigest() == row['sha256'], 'source hash: '+row['path'])
        blob = hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
        require(blob == row['git_blob'], 'source blob: '+row['path'])


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def canonical(value):
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, dict):
        return {str(k): canonical(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [canonical(v) for v in value]
    return value


def replay(mode, fixture, root=ROOT, observer=None):
    require(mode in ('baseline', 'optimized') and fixture in FIXTURES, 'replay mode')
    authenticate(root)  # Every declared live byte is checked before any source import.
    engine = load('retained_ceiling', root/ENGINE)
    operation = engine.exp if mode == 'baseline' else lambda lo, hi: exp(lo, hi, engine.PREC)
    trace, calls, ceilings = hashlib.sha256(), 0, []

    def traced_exp(lo, hi):
        nonlocal calls
        result = operation(lo, hi)
        if observer is not None:
            observer((lo, hi, result[0], result[1]))
        row = [str(lo), str(hi), str(result[0]), str(result[1])]
        trace.update((json.dumps(row, separators=(',', ':'))+'\n').encode())
        calls += 1
        return result

    original_ceiling = engine.ceiling

    def traced_ceiling(*args, **kwargs):
        result = original_ceiling(*args, **kwargs)
        ceilings.append({'args': canonical(args), 'kwargs': canonical(kwargs),
                         'result': canonical(result)})
        return result

    engine.exp, engine.ceiling = traced_exp, traced_ceiling
    old_module = sys.modules.get('ceiling')
    old_path, old_argv = sys.path[:], sys.argv[:]
    output = io.StringIO()
    try:
        sys.modules['ceiling'] = engine
        program = load('retained_'+fixture, root/FIXTURES[fixture])
        sys.argv = [str(root/FIXTURES[fixture])]
        with redirect_stdout(output):
            program.main()  # The complete original entry point, including its controls.
    finally:
        sys.path[:], sys.argv[:] = old_path, old_argv
        if old_module is None:
            sys.modules.pop('ceiling', None)
        else:
            sys.modules['ceiling'] = old_module
    return {'fixture': fixture, 'stdout': output.getvalue(), 'exp_calls': calls,
            'exp_trace_sha256': trace.hexdigest(), 'ceilings': ceilings}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mode', choices=('baseline', 'optimized'), default='optimized')
    parser.add_argument('--fixture', choices=tuple(FIXTURES), default='levers')
    args = parser.parse_args()
    print(json.dumps(replay(args.mode, args.fixture), sort_keys=True))


if __name__ == '__main__':
    main()

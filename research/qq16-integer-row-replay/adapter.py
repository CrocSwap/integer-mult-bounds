"""Exact integer-row execution for the pinned QQ16 scalar replay.

Prepared by ywz65 with OpenAI Codex assistance. Apache-2.0.
The QQ16 words and original checks are Ali Romman's credited #1969 package.
"""
from fractions import Fraction
from hashlib import sha256
from math import lcm
from pathlib import Path
import argparse
import json
import sys
import types

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PREFIX = 'research/joint-query/'
OUTPUTS = ('CLEAN-J-CHECKS.json', 'NATIVE-CHECKS.json', 'ORDERED-CHECKS.json',
           'REPLAY.json', 'SCALAR-CHECKS.json')


def need(condition, message):
    if not condition:
        raise ValueError(message)


def authenticate(root=ROOT):
    """Read and hash every live input before executing captured source bytes."""
    pins = json.loads((HERE / 'SOURCES.json').read_bytes())
    captured = {}
    for entry in pins['files']:
        if entry['usage'] != 'input':
            continue
        raw = (root / entry['path']).read_bytes()
        need(sha256(raw).hexdigest() == entry['sha256'],
             'Source pin differs: ' + entry['path'])
        captured[entry['path']] = raw
    return captured


def load(name, captured, root=ROOT):
    path = PREFIX + name + '.py'
    module = types.ModuleType('_qq16_' + name)
    module.__file__ = str(root / path)
    exec(compile(captured[path], module.__file__, 'exec', optimize=0), module.__dict__)
    return module


def replay(events, initial, register, require):
    """Each (d, row) represents row[j]/d, with d positive; no verdict cache.

    Domain: finite rows with exact int or Fraction values. The complete pinned
    caller supplies Fraction basis rows. Preserve explicit zero keys from SCALE,
    while ADD removes only zero entries visited by the original source loop.
    """
    rows = []
    for row in initial:
        require(all(type(v) in (int, Fraction) for v in row.values()),
                'Integer-row input values must be exact integers or Fractions')
        values = {k: Fraction(v) for k, v in row.items()}
        d = lcm(*(v.denominator for v in values.values()))
        rows.append((d, {k: v.numerator * (d // v.denominator)
                         for k, v in values.items()}))
    for event in events:
        if event[0] != 'scalar':
            require(event[0] in ('climb', 'phase', 'adapter', 'residual_adapter'),
                    'Known retained event')
            continue
        gate = event[1]
        at = register(gate[1])
        if gate[0] == 'clear':
            require(at >= 704, 'Only owned private contents are cleared')
            rows[at] = (1, {})
        elif gate[0] == 'add':
            source = register(gate[2])
            require(source != at, 'Distinct scalar source and target')
            value = Fraction(gate[3], gate[4])
            p, q = value.numerator, value.denominator
            dt, target = rows[at]
            ds, source_row = rows[source]
            denominator = lcm(dt, ds * q)
            left = denominator // dt
            right = p * (denominator // (ds * q))
            if left != 1:
                target = {k: v * left for k, v in target.items()}
            for key, value in source_row.items():
                result = target.get(key, 0) + right * value
                if result:
                    target[key] = result
                else:
                    target.pop(key, None)
            rows[at] = denominator, target
        else:
            require(gate[0] == 'scale', 'Known scalar gate')
            value = Fraction(gate[2], gate[3])
            denominator, row = rows[at]
            rows[at] = (denominator * value.denominator,
                        {k: v * value.numerator for k, v in row.items()})
    return [{k: Fraction(v, d) for k, v in row.items()} for d, row in rows]


def row_digest(rows):
    """Bind every returned row and coefficient, including explicit zero keys."""
    value = [[[key, x.numerator, x.denominator] for key, x in sorted(row.items())]
             for row in rows]
    return sha256(json.dumps(value, separators=(',', ':')).encode()).hexdigest()


def run(engine, out, root=ROOT):
    need(engine in ('reference', 'integer'), 'Known replay engine')
    captured = authenticate(root)
    caller = load('replay', captured, root)
    trace = []

    def module_loader(name):
        module = load(name, captured, root)
        if name == 'verify_scalar':
            original = module.replay

            def observed(events, initial):
                result = (original(events, initial) if engine == 'reference' else
                          replay(events, initial, module.register, module.need))
                trace.append({
                    'events': len(events),
                    'scalar_events': sum(e[0] == 'scalar' for e in events),
                    'input_rows': len(initial),
                    'event_sha256': sha256(json.dumps(events, separators=(',', ':')).encode()).hexdigest(),
                    'result_rows': len(result),
                    'result_terms': sum(map(len, result)),
                    'result_sha256': row_digest(result),
                })
                return result
            module.replay = observed
        return module

    caller.load_module = module_loader
    previous = sys.argv
    try:
        sys.argv = ['replay.py', '--repo', str(root), '--out', str(out)]
        caller.main()
    finally:
        sys.argv = previous
    need(len(trace) == 9 and all(t['input_rows'] == 712 for t in trace),
         'All nine original full-basis scalar calls execute')
    receipt = {
        'engine': engine,
        'original_outputs_sha256': {name: sha256((out / name).read_bytes()).hexdigest()
                                    for name in OUTPUTS},
        'scalar_calls': trace,
        'adapter_sha256': sha256(Path(__file__).read_bytes()).hexdigest(),
        'scope': 'Opt-in implementation of one scalar replay function; original caller and checks retained.',
    }
    (out / 'ADAPTER.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--engine', choices=('reference', 'integer'), default='integer')
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    run(args.engine, args.out)


if __name__ == '__main__':
    main()

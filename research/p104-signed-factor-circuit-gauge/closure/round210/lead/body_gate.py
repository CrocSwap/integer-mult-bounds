"""Expand the one nonunit stage into exact sign scales at its literal body contacts."""
import hashlib
import json
from pathlib import Path
import runpy
import signal

ROOT = Path(__file__).resolve().parents[2]
PINS = {
    'lead/dependency.py': '82959a8be9c332698e402fc963e0c3af8dfac6522128100851dd96c767e162d5',
    'lead/inputs/forward.py': '75d94780f9db49a4b08bb0e7fb4bd7fc04adb8cabbf73d83a809179c04c3d439',
    'lead/inputs/CALLER.json': '255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc',
    'round209/lead/RESULT.json': '7f72ff06f411cf86ebed076ed004660e7ffb04fc9ef317efb1f4a2a5525e1884',
}


def expand(events, skip_host_body=False):
    for event in events:
        yield event
        if event[:2] == ['J', 8] and not skip_host_body:
            for role in event[2]:
                yield ['A', 'SCALE', role, '-1']
        elif event[:2] == ['A', 'IDLE_ONE'] and 8 in event[3]:
            yield ['A', 'SCALE', event[2], '-1']


def stop(*_):
    raise TimeoutError('30-second one-profile body gate')


def main():
    assert __debug__
    signal.signal(signal.SIGALRM, stop)
    signal.alarm(30)
    for name, digest in PINS.items():
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest
    lead = runpy.run_path(str(ROOT / 'lead/dependency.py'))
    source = runpy.run_path(str(ROOT / 'lead/inputs/forward.py'))
    unit, apply = source['unit'], source['apply']
    caller = json.loads((ROOT / 'lead/inputs/CALLER.json').read_bytes())
    a = caller['types']['A']
    tape = caller['events']
    old = json.loads((ROOT / 'round209/lead/RESULT.json').read_bytes())
    case = old['chosen']
    assert a['alpha2'] == '-1' and len(case) == 20 and case[:2] == [0, 1]

    def evaluate(events, col, q, inverse=False):
        return apply(list(expand(events)), col, q, inverse)

    units = [unit(i) for i in range(36)]
    factors, keys = lead['source_factors'](unit, evaluate, tape)
    for i, col in enumerate(units):
        exponents = a['diagonal'][i]
        assert exponents[:2] == [-1, 0] and len(exponents) == 19
        for q in (1, -1):
            expected = [x * q * (-1) ** exponents[9] for x in col]
            assert evaluate(tape, col, q) == expected
            assert evaluate(tape, expected, q, inverse=True) == col
        assert lead['product'](factors, col) == [-x for x in col]
    cols, pivots = lead['target'](case, factors, lead['suffix_transport'](factors), units)
    cols = [[str(x) for x in col] for col in cols]
    changes = [[i, j, old_entry, new_entry] for j, (a, b) in enumerate(zip(old['target_columns'], cols, strict=True))
               for i, (old_entry, new_entry) in enumerate(zip(a, b, strict=True)) if old_entry != new_entry]
    mutant = list(expand(tape, skip_host_body=True))
    mutant_basis = next(i for i, col in enumerate(units) if apply(mutant, col, 1) != evaluate(tape, col, 1))
    signal.alarm(0)
    print(json.dumps({'pins': PINS, 'case': case, 'factor_keys': keys, 'nonunit_stage': 8,
                      'rank': len(pivots), 'pivots': pivots, 'target_columns': cols,
                      'changed_entries': changes, 'mutant_basis': mutant_basis, 'case_cap': 1,
                      'runner_cap_seconds': 30}, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()

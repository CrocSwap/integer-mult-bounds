"""Check solver rediscovery by exact feasibility and residual bill, not tie breaking.

Maintainer portability fix, October 2026. The frozen selection is still the
input to the independent physical emitter/auditor. No floating objective or
solver success flag is accepted as a mathematical certificate here.
"""
import importlib.util
import json
from collections import Counter
from pathlib import Path
import sys


def require(ok, message):
    if not ok:
        raise ValueError(message)


def bill(data, windows, copies=1920, stages=11, helpers=3840):
    require(set(data) == {'bit'}, 'supplier key')
    data = data['bit']
    patterns, assigned = {}, {}
    for i, pattern, count in data['patterns']:
        key = (i, tuple(pattern))
        require(i in windows and key not in patterns, 'unknown/duplicate pattern')
        require(type(count) is int and count > 0, 'nonpositive/noninteger count')
        require(all(type(w) is int and w == 8 for w in pattern), 'residual width')
        require(sum(pattern) <= windows[i][1], 'capacity')
        patterns[key] = count
    for i, width, stage, count in data['stages']:
        key = (i, width, stage)
        require(i in windows and key not in assigned, 'unknown/duplicate assignment')
        require(type(count) is int and count > 0, 'nonpositive/noninteger assignment')
        require(width == 8 and stage in windows[i][2], 'assignment outside idle interval')
        assigned[key] = count
    profile = Counter()
    for i, (_, rank, _) in windows.items():
        require(sum(n for (j, _), n in patterns.items() if j == i) == copies, 'child count')
        needed = sum(len(p) * n for (j, p), n in patterns.items() if j == i)
        require(sum(n for (j, _, _), n in assigned.items() if j == i) == needed, 'slot conservation')
        for (j, p), n in patterns.items():
            if j == i:
                profile[rank - sum(p)] += n
    for stage in range(stages):
        require(sum(n for (_, _, s), n in assigned.items() if s == stage) == helpers, 'helper coverage')
    return dict(sorted(profile.items()))


def main():
    candidate, frozen, output = map(Path, sys.argv[1:])
    source = Path(__file__).resolve().parents[2] / 'e8-bit-carrier-skeleton/discovery/host_select.py'
    spec = importlib.util.spec_from_file_location('hosting_nomination', source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    windows = {i: x for i, x in module.HC.windows(module.schedule()).items() if x[1] and x[2]}
    left = bill(json.loads(candidate.read_text()), windows)
    right = bill(json.loads(frozen.read_text()), windows)
    require(left == right, 'different exact residual histogram')
    output.write_text(json.dumps({'status': 'PASS_EXACT_FEASIBILITY_AND_BILL',
                                 'residual_histogram': left,
                                 'identical_selection': json.loads(candidate.read_text()) == json.loads(frozen.read_text()),
                                 'scope': 'Both integral allocations satisfy every capacity, window and helper count; the frozen allocation receives the subsequent physical audit.'}, indent=2) + '\n')
    print('PASS exact hosting feasibility and residual histogram; solver tie breaking may differ')


if __name__ == '__main__':
    main()

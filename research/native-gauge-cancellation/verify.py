"""Verify the fixed native simplification and its complete local bill.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
Both native interpreters and the prior scalar constructor are reused.
"""
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha1, sha256
from pathlib import Path
import argparse
import json
import importlib.util
import sys
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('native_gauge_constructor', HERE / 'construct.py')
C = importlib.util.module_from_spec(spec)
spec.loader.exec_module(C)
ROOT = C.ROOT


def need(ok, message):
    if not ok:
        raise ValueError(message)


def digest(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def authenticate():
    for row in json.loads((HERE / 'SOURCES.json').read_text())['files']:
        if row['usage'] != 'input':
            continue
        path = ROOT / row['path']
        need(not path.is_symlink(), 'Source alias')
        data = path.read_bytes()
        need(sha256(data).hexdigest() == row['sha256'], 'Changed source: ' + row['path'])
        need(sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest() == row['git_blob'], 'Changed Git blob')


def small_controls():
    def add(d, s, c):
        return ['scalar', ['add', ['L', d], ['L', s], c, 1], 0]
    def dense(program):
        rows = [[Q(i == j) for j in range(3)] for i in range(3)]
        for e in program:
            g = e[1]
            r = g[1][1]
            if g[0] == 'add':
                rows[r] = [a + Q(*g[3:5]) * b for a, b in zip(rows[r], rows[g[2][1]])]
            elif g[0] == 'scale':
                rows[r] = [Q(*g[2:4]) * a for a in rows[r]]
            elif g[0] == 'clear':
                rows[r] = [Q(0)] * 3
            else:
                raise ValueError(g)
        return rows
    fixtures = {
        'source_write': [add(0, 1, 1), add(1, 2, 1), add(0, 1, -1)],
        'target_read': [add(0, 1, 1), add(2, 0, 1), add(0, 1, -1)],
        'scale_weight': [add(0, 1, 1), ['scalar', ['scale', ['L', 1], 2, 1], 0], add(0, 1, -1)],
        'reset_barrier': [add(0, 1, 1), ['scalar', ['clear', ['L', 1]], 0], add(0, 1, -1)],
    }
    for name, program in fixtures.items():
        indexed, _, _ = C.simplify(program)
        changed = [e for _, e in indexed]
        need(dense(changed) == dense(program), 'Dense control: ' + name)
        if name != 'scale_weight':
            need(changed == program, 'Required dependency barrier: ' + name)
    scaled = fixtures['scale_weight']
    need(dense([scaled[1]]) != dense(scaled), 'Unweighted scale cancellation is false')
    warp = ['warp', ['L', 1], 1, 0, 0]
    unequal = [add(0, 1, 1), warp, add(0, 1, -1)]
    indexed, _, _ = C.simplify(unequal)
    need([e for _, e in indexed] == unequal, 'Distinct native words cannot cancel')
    return sorted(fixtures) + ['unequal_native_word', 'false_unweighted_cancellation']


def run():
    authenticate()
    controls = small_controls()
    original, prior, new, patches = C.construct()
    V = C.load(ROOT / 'research/kappa-causal-continuation/buffer-borrowing/verify_buffers.py', 'gauge_rows')
    X = C.load(ROOT / 'research/kappa-rebuild/complex/native_extensions.py', 'gauge_literal')
    c = deepcopy(new['canonical'])
    c['R'] = len(c['start']) - 2*c['v']
    c['local_profile'] = {int(k): v for k, v in c['local_profile'].items()}
    result = {'status': 'PASS_NATIVE_GAUGE_CANCELLATION_NO_KAPPA_CHANGE', 'new_kappa': None,
              'controls': controls, 'directions': {}, 'patches': patches}
    def replay(program, direction):
        rows, receipt = X.literal_replay(V, c, program, direction == 'backward')
        need(all(rows['L', r] == V.expected(('L', r), [], direction == 'backward', False) for r in range(632)), 'Every persistent endpoint')
        second = V.replay(program, c, [], direction == 'backward', False)
        return receipt, second
    for direction, program in new['programs'].items():
        before, previous = original['programs'][direction], prior['programs'][direction]
        first, second = replay(program, direction)
        prior_first, _ = replay(previous, direction)
        def paid_path(word):
            return [e for e in word if e[0] in ('climb', 'center')]
        need(paid_path(program) == paid_path(previous), 'Every prior paid record is unchanged')
        need(Counter(tuple(e[2:]) for e in program if e[0] == 'climb') == Counter(tuple(e[2:]) for e in before if e[0] == 'climb'), 'Original role/frame/rank census')
        need([e for e in program if e[0] in ('phase', 'adapter', 'center')] == [e for e in previous if e[0] in ('phase', 'adapter', 'center')], 'Phase, adapter and center records')
        counts = lambda word: dict(sorted(Counter(e[0] for e in word).items()))
        need(len(before) - len(program) == 253, '193 scalar and 60 native-map deletions')
        need(counts(previous)['scalar'] - counts(program)['scalar'] == 42, '42 new scalar deletions')
        need(counts(previous)['warp'] - counts(program)['warp'] == 60, '60 new native-map deletions')
        need(prior_first['real_scalar_allowance'] - first['real_scalar_allowance'] == 236, 'New scalar allowance saving')
        need(first['real_scalar_allowance'] == (156716 if direction == 'backward' else 156668), 'Complete scalar allowance')
        need(first['max_formal_prefix_l1'] == ('169' if direction == 'backward' else '457'), 'Retained prefix envelope')
        mutation = deepcopy(program)
        pos = next(i for i, e in reversed(list(enumerate(mutation))) if e[0] == 'scalar' and e[1][0] == 'add')
        mutation[pos][1][3] *= -1
        rejected = []
        try:
            rows, _ = X.literal_replay(V, c, mutation, direction == 'backward')
            need(all(rows['L', r] == V.expected(('L', r), [], direction == 'backward', False) for r in range(632)), 'Corrupt scalar endpoint')
        except ValueError:
            rejected.append('literal_endpoint')
        try:
            V.replay(mutation, c, [], direction == 'backward', False)
        except ValueError:
            rejected.append('second_endpoint')
        need(len(rejected) == 2, 'Both interpreters reject the actual scalar mutation')
        result['directions'][direction] = {
            'original_counts': counts(before), 'prior_counts': counts(previous), 'new_counts': counts(program),
            'program_sha256': digest(program), 'first_interpreter': first, 'second_interpreter': second,
            'mutation_rejections': rejected, 'new_scalar_allowance_saving': 236,
            'total_scalar_allowance_saving_from_4610': 1452}
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = json.loads(json.dumps(run()))
    path = HERE / 'RESULT.json'
    if args.write:
        path.write_text(json.dumps(result, indent=2) + '\n')
    else:
        need(json.loads(path.read_text()) == result, 'Deterministic complete receipt')
    print(result['status'])


if __name__ == '__main__':
    main()

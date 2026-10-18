"""Complete pinned-caller equivalence plus exact arithmetic failure controls."""
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
import argparse
import copy
import json
import random
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import adapter


def controls():
    scalar = adapter.load('verify_scalar', adapter.authenticate())
    fast = lambda events, initial: adapter.replay(events, initial, scalar.register, scalar.need)
    rng = random.Random(0x361969)
    active = list(range(6)) + list(range(704, 708))
    reg = lambda i: ['L', i] if i < 704 else ['C', i - 704]
    checked = 0
    for case in range(96):
        initial = [{i: F(1)} for i in range(712)]
        for i in active:
            initial[i] = {0: F(rng.randrange(-4, 5), rng.choice([1, 2, 3, 5, 7])),
                          i + 20: F(rng.randrange(-4, 5), rng.choice([1, 4, 9, 11]))}
        before = copy.deepcopy(initial)
        events = []
        for step in range(32):
            at = rng.choice(active)
            p, q = rng.randrange(-3, 4), rng.choice([1, 2, 3, 4, 5, 7])
            choice = rng.randrange(5)
            if choice == 0 and at >= 704:
                gate = ['clear', reg(at)]
            elif choice == 1:
                gate = ['scale', reg(at), p, q]
            else:
                source = rng.choice([i for i in active if i != at])
                gate = ['add', reg(at), reg(source), p, q]
            events.append(['scalar', gate, 'synthetic exact row'])
            if step % 4 == 3:
                expected = scalar.replay(events, initial)
                adapter.need(fast(events, initial) == expected, 'All exact synthetic prefix rows')
                checked += 1
        adapter.need(initial == before, 'Caller initial rows remain unchanged')
    initial = [{i: F(1)} for i in range(712)]
    bad = [
        [['scalar', ['clear', ['L', 0]]]],
        [['scalar', ['add', ['L', 0], ['L', 0], 1, 1]]],
        [['scalar', ['multiply', ['L', 0], 2, 1]]],
        [['unknown-retained-event']],
        [['scalar', ['add', ['L', 0], ['C', 8], 1, 1]]],
        [['scalar', ['scale', ['L', 0], 1, 0]]],
    ]
    for events in bad:
        errors = []
        for function in (scalar.replay, fast):
            try:
                function(events, initial)
            except (ValueError, ZeroDivisionError) as exc:
                errors.append((type(exc).__name__, str(exc)))
            else:
                raise ValueError('An original event guard stopped rejecting')
        adapter.need(errors[0] == errors[1], 'Same original exception and message')
    # Omitting the target's D/d_t factor gives (1+2)/15 rather than 7/15.
    initial[0], initial[1] = {9: F(1, 3)}, {9: F(2, 5)}
    event = [['scalar', ['add', ['L', 0], ['L', 1], 1, 3]]]
    result = fast(event, initial)
    adapter.need(result[0] == {9: F(7, 15)}, 'Odd-denominator alignment witness')
    bad_target_scale = F(1 + 2, 15)
    adapter.need(result[0] != {9: bad_target_scale}, 'Unaligned numerator corruption detected')
    shared = {77: F(5, 7)}
    initial[2] = initial[3] = shared
    events = [['scalar', ['add', ['L', 2], ['L', 3], -1, 1]]]
    result = fast(events, initial)
    adapter.need(result == scalar.replay(events, initial) and result[2] == {}
                 and result[3] == shared and initial[2] is initial[3], 'Aliased input dictionaries')
    return {'synthetic_words': 96, 'exact_prefix_comparisons': checked,
            'original_guard_pairs': len(bad), 'unaligned_denominator_control': 'REJECTED',
            'input_alias_and_zero_key_control': 'PASS'}


def arm(engine, out):
    result = subprocess.run([sys.executable, '-I', '-O', '-B', str(HERE / 'adapter.py'),
                             '--engine', engine, '--out', str(out)],
                            cwd=adapter.ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    adapter.need(result.returncode == 0, 'Complete caller failed: ' + result.stderr.decode(errors='replace'))
    return result, json.loads((out / 'ADAPTER.json').read_bytes())


def compare(left_dir, right_dir, left, right, stdout_left, stdout_right):
    adapter.need(stdout_left == stdout_right, 'Complete original stdout equality')
    adapter.need(left['scalar_calls'] == right['scalar_calls'], 'All nine complete scalar results')
    adapter.need(left['original_outputs_sha256'] == right['original_outputs_sha256'], 'All output digests')
    for name in adapter.OUTPUTS:
        adapter.need((left_dir / name).read_bytes() == (right_dir / name).read_bytes(),
                     'Complete original output bytes: ' + name)


def verify():
    local = controls()
    with tempfile.TemporaryDirectory(prefix='qq16-integer-review-') as temporary:
        root = Path(temporary)
        reference, left = arm('reference', root / 'reference')
        integer, right = arm('integer', root / 'integer')
        compare(root / 'reference', root / 'integer', left, right, reference.stdout, integer.stdout)
        altered = copy.deepcopy(right)
        altered['scalar_calls'][0]['result_sha256'] = '0' * 64
        try:
            compare(root / 'reference', root / 'integer', left, altered, reference.stdout, integer.stdout)
        except ValueError:
            pass
        else:
            raise ValueError('Changed scalar-map witness accepted')
        path = root / 'integer' / 'SCALAR-CHECKS.json'
        path.write_bytes(path.read_bytes() + b' ')
        try:
            compare(root / 'reference', root / 'integer', left, right, reference.stdout, integer.stdout)
        except ValueError:
            pass
        else:
            raise ValueError('Changed original receipt byte accepted')
    return {
        'status': 'PASS_QQ16_INTEGER_ROW_REPLAY',
        'original_outputs_sha256': left['original_outputs_sha256'],
        'scalar_calls': left['scalar_calls'],
        'original_stdout_bytes_equal': True,
        'controls': local | {'changed_map_witness': 'REJECTED', 'changed_receipt_byte': 'REJECTED'},
        'scope': 'Exact pinned full-caller equivalence, all original tests retained; not a supplier or new mathematical construction.',
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--emit', action='store_true')
    args = parser.parse_args()
    result = verify()
    destination = HERE / 'RESULT.json'
    if args.emit:
        destination.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    else:
        adapter.need(result == json.loads(destination.read_bytes()), 'Fixed result receipt differs')
    print(result['status'])

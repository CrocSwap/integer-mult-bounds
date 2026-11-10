"""Check the new finite tape machine, without replaying predecessor sampling claims."""
from collections import Counter
from fractions import Fraction
from hashlib import sha256
from itertools import product
import argparse
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
# Run precisely these source bytes, without consulting bytecode caches.
# dataclasses resolves its defining module through sys.modules.
import types
module = types.ModuleType('marked_tape_machine')
sys.modules[module.__name__] = module
exec(compile((HERE / 'machine.py').read_bytes(), str(HERE / 'machine.py'), 'exec'), module.__dict__)
require = module.require


def load_sampler():
    origin = json.loads((HERE / 'vendor/ORIGIN.json').read_text())
    for row in origin['files']:
        raw = (HERE / 'vendor' / row['file']).read_bytes()
        require(sha256(raw).hexdigest() == row['sha256'], 'retained source bytes changed')
    path = HERE / 'vendor/paired_sampler.py'
    raw = path.read_bytes()
    scope = {'__name__': 'retained_sampler_definitions', '__file__': str(path)}
    exec(compile(raw, str(path), 'exec'), scope)
    return scope['make'](1, 1)


def rejected(fn):
    try:
        fn()
    except ValueError:
        return
    raise ValueError('negative control accepted')


def check_local_injectivity(rules):
    """Check global one-step injectivity using the destination head displacement."""
    incoming = {}
    for (control, symbol, accumulator), (target, written, out, move) in rules.items():
        require(symbol == written or (symbol, written) in (('_', '#'), ('#', '_')),
                'random data must be immutable')
        require(move in (-1, 0, 1), 'local head motion')
        # Each destination control has one incoming direction. The prior cell
        # is therefore known, so written symbol and output determine a unique key.
        if target in incoming:
            require(incoming[target] == move, 'destination has inconsistent incoming direction')
        incoming[target] = move
    images = Counter((target, written, out) for target, written, out, _ in rules.values())
    require(max(images.values()) == 1, 'one-step machine is not injective')
    return len(incoming)


def one_path(rules, bits, output, depth, accumulator=0, start=3):
    trace = module.execute(rules, bits, accumulator, start)
    require(trace.output == accumulator ^ output, 'wrong dirty output XOR')
    require(trace.steps == 3 * depth + 4, 'wrong exact transition tariff')
    require(trace.head_moves == 2 * depth + 4, 'wrong exact tape travel')
    require(trace.marker_writes == 2 and trace.max_excursion == depth, 'marker or excursion')
    return trace


def short_paths(rules, table):
    total = 0
    for bits in product((0, 1), repeat=10):
        state, result = 0, None
        for depth, bit in enumerate(bits[:9], 1):
            state = table[state][bit]
            if state >= 312:
                result = (state - 312, depth)
                break
        if result is None:
            continue
        for accumulator in range(4):
            one_path(rules, bits, *result, accumulator=accumulator, start=1 + total % 7)
            total += 1
    return total


def wrap_paths(rules, table):
    """Enumerate every surviving prefix compactly, then each terminating edge."""
    active = [(0, ())]
    paths = revisits = deepest = 0
    wrapped_fixture = None
    for depth in range(1, 471):
        nxt = []
        for state, prefix in active:
            for bit in (0, 1):
                target = table[state][bit]
                bits = prefix + (bit,)
                if target >= 312:
                    trace = one_path(rules, bits + (0,), target - 312, depth)
                    revisits += trace.root_revisits
                    if trace.root_revisits:
                        wrapped_fixture = (bits + (0,), target - 312, depth)
                    deepest = max(deepest, depth)
                    paths += 1
                else:
                    nxt.append((target, bits))
        require(len(nxt) <= 3, 'fixture worklist capacity exceeded')
        active = nxt
    require(wrapped_fixture is not None, 'missing wrapped fixture')
    return paths, revisits, deepest, active[0][1], wrapped_fixture


def controls(rules):
    # A one-bit termination exists on coin zero, with a guard bit afterwards.
    rejected(lambda: one_path(rules, (0, 1), 1, 1))
    rejected(lambda: module.execute(rules, (0,)))
    rejected(lambda: module.execute(rules, (0, 1), max_steps=1))
    rejected(lambda: module.execute(rules, (2, 1)))
    rejected(lambda: module.execute(rules, (0, 1), accumulator=4))
    bad = dict(rules)
    del bad[(('read', 0, 0), '#', 0)]
    rejected(lambda: module.execute(bad, (0, 1)))
    # A wrapped root must continue left instead of declaring early completion.
    bad = dict(rules)
    for bit in (0, 1):
        bad[(('back', 0, 0), bit, 0)] = (module.HALT, bit, 0, 0)
    return bad


def compute():
    _, counts, table, mean = load_sampler()
    rules, targets = module.build_rules(table, counts)
    destinations = check_local_injectivity(rules)
    states = {key[0] for key in rules} | {value[0] for value in rules.values()}
    require(destinations == len(states) - 1, 'entry must be the only source-only control')
    short = short_paths(rules, table)
    wrapped, revisits, deepest, survivor, wrap_fixture = wrap_paths(rules, table)
    bad = controls(rules)
    bits, output, depth = wrap_fixture
    rejected(lambda: one_path(bad, bits, output, depth))
    rejected(lambda: module.execute(rules, survivor + (0,), max_steps=100))
    require((len(rules), len(states), targets) == (10000, 1563, 624), 'machine inventory')
    expected = 3 * mean + 4  # The predecessor expectation is cited, not rederived.
    require(expected < Fraction(43, 4), 'expected transition consequence')
    bound_files = ['machine.py', 'verify.py', 'PROOF.md', 'vendor/ORIGIN.json']
    bound_files += ['vendor/' + row['file'] for row in
                    json.loads((HERE / 'vendor/ORIGIN.json').read_text())['files']]
    hashes = {name: sha256((HERE / name).read_bytes()).hexdigest() for name in bound_files}
    return dict(status='PASS_MARKED_TAPE_DDG_REVERSAL', source_sha256=hashes, rules=len(rules),
                finite_control_states=len(states), reverse_targets=targets,
                short_dirty_output_runs=short, terminating_wrap_paths=wrapped,
                root_revisits=revisits, deepest_fixture=deepest,
                transitions='3*T+4', head_moves='2*T+4', owned_delimiter_cells=1,
                marker_writes=2, expected_transitions=str(expected),
                expected_transitions_upper='43/4',
                claim_type='scoped proof with finite machine certificate',
                scope='marked resident tape; fixed pair; no caller, freshness or new kappa')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-result', type=Path)
    args = parser.parse_args()
    result = compute()
    encoded = json.dumps(result, indent=2, sort_keys=True) + '\n'
    if args.write_result:
        args.write_result.write_text(encoded)
    else:
        require(json.loads((HERE / 'RESULT.json').read_text()) == result, 'stored result changed')
    print(encoded, end='')


if __name__ == '__main__':
    main()

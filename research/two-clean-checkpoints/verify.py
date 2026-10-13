#!/usr/bin/env python3
"""Reproduce the finite checkpoint evidence; fail closed on changed inputs."""
import argparse
from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path
import random
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import independent_check
import planner
import rounded_check


def require(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'))


def sha(data):
    return hashlib.sha256(data).hexdigest()


def source_check():
    manifest = json.loads((ROOT / 'SOURCES.json').read_text())
    for entry in manifest['files']:
        path = ROOT / entry['local_path']
        require(path.resolve().is_relative_to(ROOT), 'source outside package')
        require(sha(path.read_bytes()) == entry['sha256'], 'source drift: ' + entry['local_path'])
    return dict(files=len(manifest['files']), manifest_sha256=sha((ROOT / 'SOURCES.json').read_bytes()))


def witness(prices, scratch, clean):
    answer = planner.solve(prices, scratch, clean)
    require(answer is not None, 'fixture is infeasible')
    cost, tree = answer
    dirty_ids = tuple(range(2, 2 + scratch - clean))
    clean_ids = tuple(range(2 + scratch - clean, 2 + scratch))
    word = tuple(planner.emit(tree, 0, 1, dirty_ids, clean_ids))
    counts = Counter(i for i, _, _, _ in word)
    prof = planner.profile(tree)
    require(dict(counts) == prof['leaves'], 'profile differs from word')
    require(cost == sum(prices[i] * count for i, count in counts.items()), 'word bill differs')
    # Free-algebra execution checks every initial source/dirt coefficient at
    # once, including the larger witness beyond the exhaustive small census.
    initial = [{('a' + str(i),): 1} if i not in clean_ids else {}
               for i in range(2 + scratch)]
    actual = [dict(row) for row in initial]
    independent_check._symbolic_execute(word, actual)
    expected = [dict(row) for row in initial]
    expected[1][tuple('f' + str(i) for i in reversed(range(len(prices)))) + ('a0',)] = 1
    require(actual == expected, 'large witness product/restoration')
    return dict(prices=list(prices), scratch=scratch, clean=clean, cost=cost,
                leaf_calls=len(word), clean_dispatches=prof['C'], dirty_dispatches=prof['D'],
                multiplicities=[counts[i] for i in range(len(prices))], tree=tree,
                literal_word_sha256=sha(canonical(word).encode()))


def predecessor_check():
    spec = importlib.util.spec_from_file_location('predecessor788', ROOT / 'vendor/pr788/checkpoint.py')
    previous = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(previous)
    rng = random.Random(50)
    fixtures = [(tuple([1] * n), (n - 1).bit_length()) for n in range(1, 55)]
    fixtures += [(tuple(rng.choice((1, 3, 5)) for _ in range(n)), (n - 1).bit_length())
                 for n in range(2, 17)]
    checks = 0
    for prices, cap in fixtures:
        for clean in (0, 1):
            if cap < clean:
                continue
            ours = planner.solve(prices, cap, clean)
            old = previous.optimize(prices, cap, bool(clean))
            require(ours[0] == old[0], 'one-clean predecessor minimum changed')
            checks += 1
    return dict(comparisons=checks, weighted_seed=50,
                scope='all-dirty and one-clean restrictions match pinned PR788')


def negative_controls():
    rejected = []
    invalid = [([], 1, 1), ([True], 1, 1), ([0], 1, 1), ([1], -1, 0),
               ([1], 1, 2), ([1], 2, True)]
    for args in invalid:
        try:
            planner.solve(*args)
        except ValueError:
            rejected.append('invalid_plan_' + str(len(rejected)))
        else:
            raise ValueError('invalid planning input accepted')
    require(planner.solve([1] * 5, 2, 2) is None, 'capacity violation accepted')
    rejected.append('insufficient_total_scratch')
    t = ('C', ('C', 0, 1), ('C', 2, 3))
    for label, call in (
        ('insufficient_clean', lambda: planner.emit(t, 0, 1, (2,), (3,))),
        ('role_alias', lambda: planner.emit(t, 0, 1, (2,), (0, 3))),
        ('bad_sign', lambda: planner.emit(t, 0, 1, (), (2, 3), True)),
        ('reversed_order', lambda: planner.profile(('D', 1, 0))),
        ('duplicate_leaf', lambda: planner.profile(('C', 0, 0))),
    ):
        try:
            call()
        except ValueError:
            rejected.append(label)
        else:
            raise ValueError('invalid interface accepted: ' + label)

    word = tuple(planner.emit(t, 0, 1, (), (2, 3)))
    initial = [{('a0',): 1}, {('a1',): 1}, {}, {}]
    correct = [dict(x) for x in initial]
    independent_check._symbolic_execute(word, correct)
    mutants = {'omit_restoration': word[:-1],
               'reverse_factor_order': tuple((3 - i, s, d, z) for i, s, d, z in word),
               'wrong_sign': ((word[0][0], word[0][1], word[0][2], -word[0][3]),) + word[1:]}
    for label, mutant in mutants.items():
        result = [dict(x) for x in initial]
        independent_check._symbolic_execute(mutant, result)
        require(result != correct, 'undetected word mutation: ' + label)
        rejected.append(label)
    # A claimed clean connector may be restored yet still corrupt the target.
    dirty = [dict(x) for x in initial]
    dirty[2] = {('unexpected_dirt',): 1}
    independent_check._symbolic_execute(word, dirty)
    require(dirty[1] != correct[1], 'nonzero clean input undetected')
    rejected.append('dirty_as_clean_algebra')
    require(sum(planner.profile(t)['leaves'].values()) == 9, 'two-clean count')
    require(sum(1 for step in word if step[3] == 1) < len(word), 'cleanup is charged')
    rejected.append('positive_calls_only_undercharge')
    mutable_tree = ['C', 0, 1]
    stream = planner.emit(mutable_tree, 0, 1, (), (2,))
    mutable_tree[2] = 0
    require(tuple(stream) == tuple(planner.emit(('C', 0, 1), 0, 1, (), (2,))),
            'mutation after validation changed the instruction stream')
    rejected.append('mutation_after_lazy_validation')
    return rejected


def evidence():
    sources = source_check()
    independent = independent_check.run_checks()
    main = [witness([1] * 50, 6, clean) for clean in range(3)]
    require([w['cost'] for w in main] == [2752, 1728, 1248], 'primary fixture changed')
    saturated = []
    for depth in range(7):
        for clean in range(depth + 1):
            cost = planner.solve([1] * (1 << depth), depth, clean)[0]
            expected = 4 ** (depth - clean) * 3 ** clean
            require(cost == expected, 'saturated formula failed')
            saturated.append(dict(depth=depth, clean=clean, cost=cost))
    rounded = rounded_check.run_checks()
    # Bind every exact rounded output and invoice without duplicating 192 rows.
    rounded_summary = {key: value for key, value in rounded.items() if key != 'rows'}
    rounded_summary['rows_sha256'] = sha(canonical(rounded['rows']).encode())
    rounded_summary['forward_leaf_calls'] = sum(row['calls'] for row in rounded['rows'])
    rounded_summary['forward_phase_reads'] = sum(row['phase_reads'] for row in rounded['rows'])
    return dict(format=1, sources=sources, independent=independent,
                primary=main, saturated=saturated,
                weighted=witness([1, 3, 1, 1], 2, 2),
                predecessor=predecessor_check(), negative_controls=negative_controls(),
                rounded=rounded_summary,
                scope='Ordered binary reserved connectors; no new kappa or full multiplication proof')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true', help='explicitly regenerate EXPECTED.json')
    args = parser.parse_args()
    result = evidence()
    path = ROOT / 'EXPECTED.json'
    if args.write:
        path.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    else:
        require(canonical(result) == canonical(json.loads(path.read_text())), 'certificate mismatch')
    print('PASS_TWO_CLEAN_CHECKPOINTS: 1619 trees; 192 rounded cases; n50/s6: 1728 -> 1248; no new kappa')


if __name__ == '__main__':
    main()

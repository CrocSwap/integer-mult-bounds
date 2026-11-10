"""Independent signed-Pauli and Gaussian checks of every native rank factor.

Uses the retained Clifford compiler only to propose a factorization. A separate
Gaussian-dyadic interpreter proves its Pauli action and absolute phase.
Adapted from Ali Romman's helper verifier by @CubeJerry with substantial OpenAI
assistance. Apache-2.0; see NOTICE.md for the complete source attribution.
"""
from collections import Counter
from functools import lru_cache
import argparse
import copy
import json
import sys
from linear import HERE, digest, load, main_roles, need, read, span


def map_pairs(word):
    return ({(e[2], e[3]) for e in word['program'] if e[0] == 'MOVE'}
            | {(word['initial'][r], word['final'][r]) for r in range(word['public'])
               if r not in main_roles(word)})


def verify(word, previous=None):
    root = HERE / 'retained/retained/native'
    compiler = load(root / 'clifford_exact.py', 'helper_split_clifford')
    gaussian = load(root / 'native_verify.py', 'helper_split_gaussian')
    dimensions = list(map(len, word['frames']))
    inherited_pairs = set()
    if previous is not None:
        need(word['frames'] == previous['frames'], 'Frozen chart table for exact pair-set reuse')
        need(all(word[k] == previous[k] for k in ('live', 'ports', 'hosted')),
             'Frozen main adapters for exact pair-set reuse')
        inherited_pairs = map_pairs(previous)
    @lru_cache(None)
    def chart(frame):
        return compiler.canonical_frame(9, tuple(word['frames'][frame]))
    recipes = {}
    def check(old, new):
        if (old, new) in inherited_pairs:
            return {'rank': abs(dimensions[new] - dimensions[old])}
        if (old, new) not in recipes:
            recipe, _ = compiler.lower_child(chart(old).adjoint().then(chart(new)))
            expected = (gaussian.adjoint(gaussian.frame(tuple(word['frames'][old]), 9))
                        + gaussian.frame(tuple(word['frames'][new]), 9))
            gaussian.equal(gaussian.recipe(recipe), expected,
                           'Native chart change: signed Pauli action and absolute phase')
            need(recipe['rank'] == abs(dimensions[new] - dimensions[old]),
                 'Exact rank of the nested native chart change')
            recipes[old, new] = recipe
        return recipes[old, new]
    for event in word['program']:
        if event[0] == 'MOVE':
            check(event[2], event[3])
    helper_ranks = Counter()
    for role in range(word['public']):
        if role not in main_roles(word):
            helper_ranks[check(word['initial'][role], word['final'][role])['rank']] += 1
    adapters = []
    for x, q, x2, y2 in zip(word['live'], word['ports'], word['hosted']['X2'], word['hosted']['Y2']):
        y = x + 112
        need(word['frames'][word['initial'][x]] == [q], 'Literal central input port')
        need(span(word['frames'][word['final'][y]])
             == frozenset(z for z in range(512) if not (z & q).bit_count() % 2),
             'Literal output hyperplane')
        need((word['initial'][x2], word['final'][x2]) == (word['initial'][x], word['final'][x])
             and (word['initial'][y2], word['final'][y2]) == (word['initial'][y], word['final'][y]),
             'Both main planes use the checked boundary charts')
        tests = [
            (compiler.cgate(9, q, 1).adjoint().then(chart(word['initial'][x])),
             gaussian.adjoint((('C', q, 1),)) + gaussian.frame(tuple(word['frames'][word['initial'][x]]), 9)),
            (chart(word['final'][y]).adjoint().then(compiler.cgate(9, q, -1).then(compiler.fourier(9))),
             gaussian.adjoint(gaussian.frame(tuple(word['frames'][word['final'][y]]), 9))
             + (('C', q, -1),) + gaussian.fourier(9))]
        for actual, expected in tests:
            recipe, _ = compiler.lower_child(actual)
            need(recipe['rank'] == 0, 'Intrinsic main adapter is ordinary')
            gaussian.equal(gaussian.recipe(recipe), expected, 'Main endpoint absolute phase')
            adapters.append(recipe)
    need(recipes, 'At least one native map is checked in this invocation')
    old, new = next(iter(recipes))
    bad = copy.deepcopy(recipes[old, new])
    bad['left']['phase'] = (bad['left']['phase'] + 1) % 4
    expected = (gaussian.adjoint(gaussian.frame(tuple(word['frames'][old]), 9))
                + gaussian.frame(tuple(word['frames'][new]), 9))
    try:
        gaussian.equal(gaussian.recipe(bad), expected, 'Phase-only corruption control')
    except ValueError:
        pass
    else:
        raise ValueError('Phase-only corrupted child was accepted')
    payload = [[old, new, recipes[old, new]] for old, new in sorted(recipes)] + adapters
    return dict(word_payload_sha256=digest(word),
                distinct_native_maps=len(recipes), main_adapter_recipes=len(adapters),
                main_adapter_instances=2 * len(adapters), helper_normalizers=2 * sum(helper_ranks.values()),
                helpers=dict(helper_ranks), recipe_payload_sha256=digest(payload),
                exact_signed_pauli_and_gaussian=True, phase_only_corruption_rejected=True,
                checked_pairs=sorted(recipes), inherited_pairs_count=len(map_pairs(word) & inherited_pairs),
                complete_pairset_sha256=digest(sorted(map_pairs(word))),
                scope='new maps only; previous map proof required' if previous is not None else 'all maps')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('word', nargs='?', default=str(HERE / 'WORD.json.gz'))
    parser.add_argument('--new-maps-from')
    parser.add_argument('--receipt')
    args = parser.parse_args()
    word = read(args.word)
    previous = read(args.new_maps_from) if args.new_maps_from else None
    report = verify(word, previous)
    if args.receipt:
        need(json.loads(json.dumps(report)) == read(args.receipt),
             'Exact source-bound physical coverage and recipe receipt')
    print(json.dumps({k: v for k, v in report.items() if k != 'checked_pairs'}, sort_keys=True))
    print('PASS_NATIVE_PHYSICAL_FACTOR_RANKS_AND_PHASES')

"""Check the attaining paid word by independent adjoint substitution. Apache-2.0."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from word import check_causality, read_word, require


def add(row, other, factor):
    for k, value in other.items():
        combined = row.get(k, 0) + value * factor
        if combined:
            row[k] = combined
        elif k in row:
            del row[k]


def pullback(schedule, forms, key):
    terms = {key: 1}
    for node in reversed(schedule):
        coefficient = terms.pop(node, 0)
        if coefficient:
            add(terms, forms[node], coefficient)
    require(all(k < 0 for k in terms), 'adjoint terminated at public coordinates')
    return terms


def main():
    word, original, routes, terminals = read_word()
    check_causality(word, original, routes, terminals)
    schedule = word['schedule']
    old_in, old_out = 95914, 88
    first, second = 155442, 155490
    owner, local_copy = 674, 101539
    require(word['initial'][owner] == 11 and routes[local_copy] == (658,138),
            'live sources for the two replacement transfers')
    require(pullback(schedule,original,local_copy) == {~780:1}, 'literal copy of x780')
    require(original[first][old_out] == original[second][old_out] == 1,
            'same coefficient on old outlet')
    desired = {~674:1, ~780:-1}
    require(pullback(schedule,original,first) == desired, 'given output row')
    replacement = original.copy()
    rewired = routes | {old_in:(11,127), old_out:(138,127)}
    replacement[old_in] = {~owner:1}
    replacement[old_out] = {local_copy:1}
    replacement[first] = {old_in:1,old_out:-1}
    second_new = original[second].copy()
    add(second_new,original[first],-1)
    add(second_new,replacement[first],1)
    replacement[second] = second_new
    check_causality(word, replacement, rewired, terminals)

    # Both word versions have the same index order. Outside the union of
    # their dependency cones equality follows by induction at every node.
    affected = set()
    for k in schedule:
        if original[k] != replacement[k] or affected.intersection(original[k]) or affected.intersection(replacement[k]):
            affected.add(k)
    require(affected == {old_in,old_out,first,second}, 'exact influence cone')
    for k in sorted(affected & terminals.keys()):
        require(pullback(schedule,replacement,k) == pullback(schedule,original,k),
                'all 1289 coefficients of changed terminal')

    # Mistakenly retaining the old second output changes its identity.
    broken = replacement | {second: original[second]}
    require(pullback(schedule,broken,second) != pullback(schedule,original,second),
            'unchanged receiving decoder control')
    # Swapping the two raw owners' signs must reverse the entire restored row.
    flipped = replacement | {first:{old_in:-1,old_out:1}}
    require(pullback(schedule,flipped,first) == {k:-q for k,q in desired.items()},
            'wrong-sign control')
    require(len(terminals)-len(affected & terminals.keys()) == 1287, 'untouched terminals')
    print('PASS 1289 outputs on all 1289 rational coordinates, two adjusted terminals,'
          ' 1287 unaffected; rank-eight and rank-one sends from charts 11 and 138.')
    print('Schedule positions:', [(k,schedule.index(k)) for k in
                                  (old_in,local_copy,old_out,second,first)])


if __name__ == '__main__':
    main()

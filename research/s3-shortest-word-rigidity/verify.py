"""Exact symbolic coefficients and boundary controls; no predecessor imports."""
from itertools import permutations, product
import json
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
E = (0, 1, 2)
S = (1, 0, 2)
T = (0, 2, 1)
Z = (2, 1, 0)
GROUP = tuple(permutations(range(3)))


def need(ok, why):
    if not ok:
        raise ValueError(why)


def compose(a, b):
    return tuple(a[b[i]] for i in range(3))


def expand(labels):
    # Coefficients are free, noncommutative F2-polynomials in A, B, C.
    terms = {(E, ())}
    for symbol, label in zip('ABC', labels):
        out = set()
        for g, word in terms:
            for h, suffix in ((E, ()), (E, (symbol,)), (label, (symbol,))):
                term = (compose(g, h), word + suffix)
                if term in out:
                    out.remove(term)
                else:
                    out.add(term)
        terms = out
    return {g: {''.join(w) or 'I' for h, w in terms if h == g} for g in GROUP}


def mm(a, b):
    rows = []
    for row in a:
        value = 0
        for j in range(len(b)):
            if row >> j & 1:
                value ^= b[j]
        rows.append(value)
    return tuple(rows)


def mx(*matrices):
    return tuple(_xor(row) for row in zip(*matrices))


def _xor(values):
    out = 0
    for value in values:
        out ^= value
    return out


def eye(n):
    return tuple(1 << i for i in range(n))


def zero(n):
    return (0,) * n


def factor(label, p):
    return {E: mx(eye(len(p)), p), label: p}


def ring_product(a, b):
    n = len(next(iter(a.values())))
    out = {}
    for g, m in a.items():
        for h, q in b.items():
            key = compose(g, h)
            out[key] = mx(out.get(key, zero(n)), mm(m, q))
    return {g: m for g, m in out.items() if any(m)}


def word(labels, projectors):
    out = {E: eye(len(projectors[0]))}
    for label, p in zip(labels, projectors):
        out = ring_product(out, factor(label, p))
    return out


def target(p):
    return {g: m for g, m in factor(Z, p).items() if any(m)}


def rank(matrix):
    pivots = {}
    for row in matrix:
        while row:
            pivot = row.bit_length() - 1
            if pivot in pivots:
                row ^= pivots[pivot]
            else:
                pivots[pivot] = row
                break
    return len(pivots)


def result():
    st, ts = compose(S, T), compose(T, S)
    expected = {
        E: {'I', 'A', 'B', 'C', 'AB', 'BC'},
        S: {'A', 'C', 'AB', 'BC'},
        T: {'B', 'AB', 'BC', 'ABC'},
        st: {'AB', 'ABC'},
        ts: {'BC', 'ABC'},
        Z: {'ABC'},
    }
    need(expand((S, T, S)) == expected, 'noncommutative coefficient expansion')
    swapped = {compose(Z, compose(g, Z)): terms for g, terms in expected.items()}
    need(expand((T, S, T)) == swapped, 'generator-swap symmetry')
    label_words = tuple(product((S, T), repeat=3))
    support = [labels for labels in label_words if expand(labels)[Z]]
    need(support == [(S, T, S), (T, S, T)], 'only alternating labels reach z')
    need(all(not expand(labels)[Z] for size in (1, 2)
             for labels in product((S, T), repeat=size)), 'inherited short support bound')

    p = (1, 0, 0)
    coupled_rank_one = (1, 1, 0)
    coupled_rank_two = (1, 6, 0)
    controls = []
    need(rank(p) == rank(coupled_rank_one) == 1, 'rank-one controls')
    need(mm(coupled_rank_one, coupled_rank_one) == coupled_rank_one, 'oblique idempotent')
    for q in (p, coupled_rank_one):
        for labels in support:
            need(word(labels, (q, q, q)) == target(q), 'coordinate/oblique positive control')
    controls.append('coordinate_and_oblique_targets')

    for omitted in range(3):
        labels = tuple(h for i, h in enumerate((S, T, S)) if i != omitted)
        need(word(labels, (p,) * 2) != target(p), 'omitted paid factor accepted')
    controls.append('omitted_factor_rejected')
    for labels in label_words:
        if labels not in support:
            need(word(labels, (p,) * 3) != target(p), 'nonalternating label accepted')
    controls.append('nonalternating_labels_rejected')
    for changed in range(3):
        ps = tuple(coupled_rank_one if i == changed else p for i in range(3))
        need(word((S, T, S), ps) != target(p), 'mismatched projector accepted')
    controls.append('changed_projector_rejected')

    dirty = word((S, T, S), (coupled_rank_one,) * 3)
    desired = target(p)
    need(all(dirty.get(g, zero(3))[0] == desired.get(g, zero(3))[0]
             for g in GROUP), 'data-only false positive fixture')
    need(dirty != desired, 'dirty scratch return omitted')
    controls.append('data_only_acceptance_rejected')

    need(rank(coupled_rank_two) == 2 and mm(coupled_rank_two, coupled_rank_two) == coupled_rank_two,
         'higher-rank idempotent control')
    need(mm(coupled_rank_two, p) == mm(p, coupled_rank_two) == p, 'nested projector control')
    need(word((S, T, S), (coupled_rank_two, p, coupled_rank_two)) == target(p),
         'general-rank equality case')
    need(coupled_rank_two != p, 'rank-one necessity control')
    controls.append('rank_one_premise_is_essential')

    need(word((Z,), (p,)) == target(p), 'changed alphabet control')
    controls.append('paying_z_changes_the_alphabet')
    need(mm(p, coupled_rank_one) != mm(coupled_rank_one, p), 'matrix order control')
    bad = dict(expected)
    bad[st] = {'BA', 'ABC'}
    need(expand((S, T, S)) != bad, 'commuted matrix product accepted')
    controls.append('noncommutative_order_preserved')
    return {
        'scope': 'symbolic coefficients and exact boundary controls; universal theorem is the README proof',
        'coefficient_polynomials_sts': {
            name: sorted(expected[g]) for name, g in
            (('e', E), ('s', S), ('t', T), ('st', st), ('ts', ts), ('z', Z))
        },
        'label_words': 8,
        'alternating_label_words': 2,
        'control_groups': controls,
    }


def main():
    actual = result()
    expected = json.loads((PACKAGE / 'RESULT.json').read_text())['symbolic']
    need(actual == expected, 'symbolic result receipt drift')
    print('PASS_S3_SHORTEST_WORD_RIGIDITY symbolic_coefficients=6 control_groups=8')


if __name__ == '__main__':
    main()

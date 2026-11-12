"""Exact unchanged-chronology replay of the single R209 J1 extension."""
from fractions import Fraction as Q
from hashlib import sha256
from json import dumps
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal
from sys import argv, implementation, version_info

SECONDS = 20
CHOSEN = (0, 1, 2, 4, 6, 8, 10, 12, 14, 18, 19, 20, 22, 24, 26, 28, 30, 32, 34, 36)
REPLAY_SHA = '91c17d100b8f06a1fd8b8bc8e5f4a1b2cc3bf5900d0a9e70f8faeb27e3da48df'


def multiply(columns, v):
    return [sum(a * b for a, b in zip(row, v, strict=True) if a and b)
            for row in zip(*columns, strict=True)]


def difference(columns):
    return [[x - Q(i == j) for i, x in enumerate(column)] for j, column in enumerate(columns)]


def is_involution(columns):
    return all(multiply(columns, column) == [Q(i == j) for i in range(len(columns))]
               for j, column in enumerate(columns))


def stop(*_):
    raise TimeoutError(f'R209 independent {SECONDS}-second cap')


def main():
    assert __debug__ and implementation.name == 'cpython' and version_info[:2] == (3, 12)
    assert len(argv) == 3, 'pass the authenticated R208 runner and #7435 package root'
    predecessor, root = [Path(s).resolve() for s in argv[1:]]
    assert sha256(predecessor.read_bytes()).hexdigest() == REPLAY_SHA
    old = run_path(str(predecessor))
    signal(SIGALRM, stop)
    alarm(SECONDS)
    tape = old['read'](root, 'inputs/CALLER.json')['events']
    manifest = old['read'](root, 'inputs/7113-SHA256.json')
    pins = old['PINS']
    assert manifest['expected/ODD-TYPE-AB-CALLER.json'] == pins['inputs/CALLER.json']
    predecessor_receipt = old['read'](root, 'inputs/R195.json')
    assert (predecessor_receipt['head'], predecessor_receipt['caller']) == (old['HEAD'], old['CALLER'])
    original, labels = old['signed_prefix'](tape, -1)
    assert len(original) == 38 and labels == predecessor_receipt['factor_labels']
    assert labels[0][:3] == [43, 1, 0] and labels[1][:3] == [43, 1, 1]
    kept = [factor for i, factor in enumerate(original) if i not in CHOSEN]
    assert len(kept) == 18
    unit, apply, echelon = [old[k] for k in ('unit', 'apply', 'echelon')]
    target = []
    for j in range(36):
        basis = unit(j)
        unchanged_inverse = apply(kept, basis, inverse=True)
        assert apply(kept, unchanged_inverse) == basis
        column = apply(original, unchanged_inverse)
        assert column == [-x for x in unchanged_inverse]
        target.append(column)
    # The inverse old complement appears on the right, applied first.
    target_delta = difference(target)
    displacement_rank = len(echelon(target_delta))
    blocks = []
    split = (range(18), range(18, 36))
    for a, rows in enumerate(split):
        for b, cols in enumerate(split):
            data = [[target_delta[j][i] for i in rows] for j in cols]
            witness = next(((i, j, str(target_delta[j][i])) for j in cols for i in rows if target_delta[j][i]), None)
            item = {'row_plane': a, 'column_plane': b, 'displacement_rank': len(echelon(data)), 'first_nonzero': witness}
            if a == b:
                item['restriction_involution'] = is_involution([[target[j][i] for i in rows] for j in cols])
            blocks.append(item)
    preserving = all(row['displacement_rank'] == 0 for row in blocks if row['row_plane'] != row['column_plane'])
    assert displacement_rank == 19 and not is_involution(target)
    assert not preserving, 'the stipulated coordinate-plane obstruction failed'
    assert [b['displacement_rank'] for b in blocks] == [18, 0, 1, 1]
    assert target[1][18] == 4
    assert all(target[j][:18] == [-x for x in unit(j)[:18]] for j in range(18))
    # Any lower-plane-preserving transvection changes at most one diagonal block.
    # The quotient -I needs at least 19, and the lower block needs one more.
    # Flip one unchanged factor's sign. The resulting exact matrix differs.
    u, v = kept[0]
    altered = [([-x for x in u], v), *kept[1:]]
    assert any(apply(altered, unit(j), inverse=True) != apply(kept, unit(j), inverse=True) for j in range(36))
    alarm(0)
    print(dumps({'head': old['HEAD'], 'caller': old['CALLER'], 'pins': pins,
                 'r208_runner_sha256': REPLAY_SHA, 'runner_cap_seconds': SECONDS,
                 'chosen': CHOSEN, 'kept': [i for i in range(38) if i not in CHOSEN],
                 'displacement_rank': displacement_rank, 'involution': is_involution(target),
                 'blocks': blocks, 'preserves_both_coordinate_planes': preserving,
                 'preserving_factorization_possible': False,
                 'lower_plane_preserving_length_lower_bound': 20,
                 'nonpreserving_factors_lower_bound_if_length_19': 2,
                 'corrupted_unchanged_factor_rejected': True,
                 'target_columns': [[str(x) for x in c] for c in target]}, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()

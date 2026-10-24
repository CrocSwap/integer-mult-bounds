"""Independent faithful regular-action census: binary 18x18 matrices, no imports."""
from itertools import permutations
import hashlib
import json
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent


def require(ok, why):
    if not ok:
        raise ValueError(why)


def product_rows(left, right):
    answer = []
    for mask in left:
        row = 0
        while mask:
            bit = mask & -mask
            row ^= right[bit.bit_length() - 1]
            mask ^= bit
        answer.append(row)
    return tuple(answer)


def run():
    group = tuple(permutations(range(3)))
    number = {g: i for i, g in enumerate(group)}
    identity = tuple(1 << i for i in range(18))
    s, t, z = (1, 0, 2), (0, 2, 1), (2, 1, 0)
    projectors = tuple((u, v) for u in range(1, 8) for v in range(1, 8)
                       if (u & v).bit_count() % 2)
    require(len(projectors) == 28, 'projector count')

    def action(h, u, v):
        rows = list(identity)
        # Left regular action [h] sends basis[g] to basis[h g].
        for g_index, g in enumerate(group):
            hg_index = number[tuple(h[g[k]] for k in range(3))]
            for target_role in range(3):
                if not u >> target_role & 1:
                    continue
                for source_role in range(3):
                    if v >> source_role & 1:
                        bit = 1 << (6 * source_role + g_index)
                        rows[6 * target_role + hg_index] ^= bit
                        rows[6 * target_role + g_index] ^= bit
        return tuple(rows)

    moves = tuple((label, u, v, action(h, u, v))
                  for label, h in (('s', s), ('t', t)) for u, v in projectors)
    require(len(moves) == len({m[3] for m in moves}) == 56, 'distinct paid actions')
    require(all(product_rows(m[3], m[3]) == identity for m in moves), 'paid involutions')
    targets = {action(z, u, v): (u, v) for u, v in projectors}
    require(len(targets) == 28, 'distinct faithful targets')
    # The regular action is faithful: [g] sends basis[e] to six different columns.
    regular_e_images = {number[tuple(h[k] for k in range(3))] for h in group}
    require(len(regular_e_images) == 6, 'regular basis collision')
    hits = {p: [] for p in projectors}
    evaluated = 0
    digest = hashlib.sha256()
    for a, first in enumerate(moves):
        for b, second in enumerate(moves):
            pair = product_rows(first[3], second[3])
            require(pair not in targets, 'short-word control')
            for c, third in enumerate(moves):
                state = product_rows(pair, third[3])
                evaluated += 1
                hit = targets.get(state)
                if hit is not None:
                    hits[hit].append([a, b, c])
                    digest.update(bytes((a, b, c)))
    require(evaluated == 56 ** 3, 'incomplete domain')
    for projector, words in hits.items():
        require(len(words) == 2, 'a target does not have exactly two words')
        observed = set()
        for indices in words:
            triple = tuple(moves[i] for i in indices)
            require(all((m[1], m[2]) == projector for m in triple), 'a coupled word attained target')
            observed.add(''.join(m[0] for m in triple))
        require(observed == {'sts', 'tst'}, 'unexpected shortest labels')
    return {
        'scope': 'complete three-register faithful regular-action census, not an all-size proof',
        'registers': 3,
        'regular_action_dimension': 18,
        'rank_one_idempotents': 28,
        'paid_moves': 56,
        'ordered_length_three_words': evaluated,
        'rank_one_targets': 28,
        'hits_per_target': 2,
        'total_target_hits': sum(map(len, hits.values())),
        'fixed_coordinate_target_hits': hits[(1, 1)],
        'hit_word_indices_sha256': digest.hexdigest(),
    }


def main():
    actual = run()
    expected = json.loads((PACKAGE / 'RESULT.json').read_text())['census']
    require(actual == expected, 'finite census receipt drift')
    print('PASS_S3_SHORTEST_WORD_CENSUS words=175616 rank_one_targets=28 hits=56 fixed_target_hits=2')


if __name__ == '__main__':
    main()

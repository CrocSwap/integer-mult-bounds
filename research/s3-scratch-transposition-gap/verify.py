#!/usr/bin/env python3
"""Length-2 words in the paid S3 alphabet miss the transposition (0 2).

The paid moves are right-multiplications by I + (h + e) P, with h one of the
two generating transpositions and P a 3x3 rank-1 idempotent over F2. The same
support bound holds for every matrix size and every F2-valued P.
"""

from itertools import product

PACKAGE_LEMMA = (
    "No length-2 word in the paid alphabet writes the transposition (0 2) "
    "on one register, with or without scratch."
)


def require(ok, why):
    if not ok:
        raise SystemExit(why)


def compose(later, earlier):
    """Apply earlier first, then later."""
    return tuple(later[earlier[i]] for i in range(3))


def algebra():
    group = sorted(__import__("itertools").permutations(range(3)))
    index = {item: i for i, item in enumerate(group)}
    identity = (0, 1, 2)
    s = (1, 0, 2)
    t = (0, 2, 1)
    gap = (2, 1, 0)
    table = [[index[compose(left, right)] for right in group] for left in group]
    return group, index, identity, s, t, gap, table


def support_ball():
    """Group elements representable by a word of length at most 2 in {s, t}."""
    _, _, identity, s, t, gap, _ = algebra()
    ball = {identity, s, t, compose(s, t), compose(t, s), compose(s, s), compose(t, t)}
    return ball, gap


def rank1_idempotents():
    """The 28 rank-1 idempotent 3x3 matrices over F2."""
    found = []
    for image in range(1, 8):
        for mask in range(8):
            # phi(e_j) = bit j of mask. Keep phi(image) = 1.
            value = 0
            for bit in range(3):
                if (image >> bit) & 1 and (mask >> bit) & 1:
                    value ^= 1
            if value != 1:
                continue
            matrix = tuple(
                tuple(1 if (mask >> col) & 1 and (image >> row) & 1 else 0 for col in range(3))
                for row in range(3)
            )
            square = tuple(
                tuple(
                    (matrix[row][0] & matrix[0][col])
                    ^ (matrix[row][1] & matrix[1][col])
                    ^ (matrix[row][2] & matrix[2][col])
                    for col in range(3)
                )
                for row in range(3)
            )
            if square != matrix:
                continue
            rows = [list(row) for row in matrix]
            pivot = 0
            for col in range(3):
                chosen = next((i for i in range(pivot, 3) if rows[i][col]), None)
                if chosen is None:
                    continue
                rows[pivot], rows[chosen] = rows[chosen], rows[pivot]
                for i in range(3):
                    if i != pivot and rows[i][col]:
                        rows[i] = [a ^ b for a, b in zip(rows[i], rows[pivot])]
                pivot += 1
            if pivot == 1 and matrix not in found:
                found.append(matrix)
    return tuple(found)


def zero_matrix():
    return [[0, 0, 0] for _ in range(3)]


def identity_matrix(identity_index):
    out = zero_matrix()
    for i in range(3):
        out[i][i] = 1 << identity_index
    return out


def algebra_mul(left, right, table):
    out = 0
    for a in range(6):
        if (left >> a) & 1:
            for b in range(6):
                if (right >> b) & 1:
                    out ^= 1 << table[a][b]
    return out


def matrix_mul(left, right, table):
    out = zero_matrix()
    for i in range(3):
        for j in range(3):
            value = 0
            for k in range(3):
                value ^= algebra_mul(left[i][k], right[k][j], table)
            out[i][j] = value
    return out


def paid(label_index, projector, identity_index):
    out = identity_matrix(identity_index)
    delta = (1 << label_index) ^ (1 << identity_index)
    for i in range(3):
        for j in range(3):
            if projector[i][j]:
                out[i][j] ^= delta
    return out


def gap_bit_count(state, gap_index):
    return sum((entry >> gap_index) & 1 for row in state for entry in row)


def length3_coordinate_writes_gap(table, index, identity, s, t, gap):
    """Right-multiply register 0 by s, then t, then s."""
    state = identity_matrix(index[identity])
    coordinate = ((1, 0, 0), (0, 0, 0), (0, 0, 0))
    for label in (s, t, s):
        state = matrix_mul(state, paid(index[label], coordinate, index[identity]), table)
    expected = identity_matrix(index[identity])
    expected[0][0] = 1 << index[gap]
    return state == expected


def enumerate_short_words():
    group, index, identity, s, t, gap, table = algebra()
    projectors = rank1_idempotents()
    moves = []
    for label in (s, t):
        for projector in projectors:
            moves.append(paid(index[label], projector, index[identity]))
    gap_index = index[gap]
    length1 = sum(gap_bit_count(move, gap_index) for move in moves)
    # A length-1 state is the move itself, because I * move = move.
    length2 = 0
    for left, right in product(moves, repeat=2):
        state = matrix_mul(left, right, table)
        length2 += gap_bit_count(state, gap_index)
    return {
        "projectors": len(projectors),
        "moves": len(moves),
        "length1_gap_bits": length1,
        "length2_gap_bits": length2,
        "length3_control": length3_coordinate_writes_gap(table, index, identity, s, t, gap),
        "group_order": len(group),
    }


def main():
    from pathlib import Path

    readme = (Path(__file__).resolve().parent / "README.md").read_text(encoding="utf-8")
    require(PACKAGE_LEMMA in readme, "README dropped the lemma")
    ball, gap = support_ball()
    require(gap not in ball, "gap fell inside the length-2 ball")
    require(len(ball) == 5, "length-2 ball is not five elements")
    require(compose((1, 0, 2), (1, 0, 2)) == (0, 1, 2), "s is not an involution")
    require(compose((0, 2, 1), (0, 2, 1)) == (0, 1, 2), "t is not an involution")
    counts = enumerate_short_words()
    require(counts["group_order"] == 6, "S3 order changed")
    require(counts["projectors"] == 28, "rank-1 idempotent count changed")
    require(counts["moves"] == 56, "paid move count changed")
    require(counts["length1_gap_bits"] == 0, "length 1 reached the gap")
    require(counts["length2_gap_bits"] == 0, "length 2 reached the gap")
    require(counts["length3_control"], "length-3 coordinate control missed the gap")
    print(
        "PASS_S3_SCRATCH_TRANSPOSITION_GAP "
        f"ball=5 length2_gap_bits=0 moves=56 length3_control=1"
    )


if __name__ == "__main__":
    main()

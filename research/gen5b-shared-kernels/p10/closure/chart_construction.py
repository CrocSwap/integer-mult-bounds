"""Our previously authored exact weighted chart constructors.
Prepared with substantial OpenAI assistance. Apache-2.0.
"""
import chart_rational as base
def gram(a, b):
    return 9 * sum(x * y for x, y in zip(a, b)) - sum(a) * sum(b)


def checked_chart(columns, residual_rank):
    assert len(columns) == 20 and all(len(c) == 20 for c in columns)
    assert 0 < residual_rank < 20
    assert all(gram(a, b) == 0 for a in columns[:residual_rank]
               for b in columns[residual_rank:])
    matrix = [list(row) for row in zip(*columns)]
    assert len(base.rref(matrix)[1]) == 20
    f = base.factor(matrix)  # Includes an exact inverse-program replay.
    assert f['determinant'] and f['count'] <= 400
    assert f['max_numerator'] < 2**80 and f['max_denominator'] < 2**80
    return dict(basis_columns=columns, residual_rank=residual_rank,
                completion_rank=20-residual_rank, **f)


def line_chart(i, j, residual_rank):
    assert type(i) is int and type(j) is int and 0 <= i < j < 20
    line = [int(k == i) - int(k == j) for k in range(20)]
    complement = [[int(k == r) for k in range(20)] for r in range(20) if r not in (i, j)]
    complement.append([int(k == i or k == j) for k in range(20)])
    assert gram(line, line) == 18
    if residual_rank == 1:
        columns = [line] + complement
    elif residual_rank == 19:
        columns = complement + [line]
    else:
        raise ValueError('A line chart has residual rank 1 or 19')
    return dict(line=[i, j], **checked_chart(columns, residual_rank))


def first_frame_chart(frame, line):
    """F/L from ker(A) intersect L-perp; completion is L direct-sum F-perp."""
    ann = frame['a'] if 'a' in frame else base.nullspace(frame['b'])
    d = frame['dim']; i, j = line
    assert len(base.rref(ann)[1]) == 20 - d
    v = [int(k == i) - int(k == j) for k in range(20)]
    assert all(sum(a * b for a, b in zip(row, v)) == 0 for row in ann)
    assert gram(v, v) == 18
    # Since sum(v)=0, the weighted condition <v,x>=0 is x_i=x_j.
    residual = base.nullspace(ann + [v])
    assert len(residual) == d - 1
    # (9I-J)^(-1) a is proportional to 11*a-sum(a).
    exterior = [base.primitive([11 * x - sum(row) for x in row]) for row in ann]
    assert len(exterior) == 20 - d
    assert all(sum(a * b for a, b in zip(row, col)) == 0
               for row in ann for col in residual + [v])
    assert all(gram(col, other) == 0 for col in residual + [v] for other in exterior)
    out = checked_chart(residual + [v] + exterior, d - 1)
    out.update(first_dimension=d, line=line)
    return out



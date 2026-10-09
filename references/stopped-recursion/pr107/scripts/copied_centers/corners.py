"""Exact selected PR31/PR33 corner witness and zero-minor verification.

Original corner and incidence methods: Rohan Arun, PR31, commit
02f68f95369c39955c5ffcfddbd75cd83e26b305 (Apache-2.0; OpenAI Codex assistance).
Parameterization: Dominik Scholz, PR33, commit
a499a345c040aa15b68e984a0904eadc485c7a7e (Apache-2.0; recorded Anthropic
Claude Opus 5.5 and OpenAI GPT-6 Astra/Codex assistance).
Modification copyright 2026 icekylinx, Apache-2.0, with OpenAI GPT-6 Astra
and Codex assistance: verify the selected (25,23) saved partitions directly;
omit exploratory matroid search and unrelated historical dimensions.
See repository NOTICE, LICENSE and SOURCES.json for retained notices.
"""
from fractions import Fraction as Q
from functools import reduce
from math import gcd


def require(condition, message):
    if not condition:
        raise ValueError(message)


def integer_rank(matrix):
    """PR31 exact rank by integer row operations and gcd reduction."""
    matrix = [row[:] for row in matrix]
    height = len(matrix)
    width = len(matrix[0]) if height else 0
    rank = 0
    for col in range(width):
        pivot = next((r for r in range(rank,height) if matrix[r][col]),None)
        if pivot is None:
            continue
        matrix[rank],matrix[pivot] = matrix[pivot],matrix[rank]
        for row in range(rank+1,height):
            if not matrix[row][col]:
                continue
            d = gcd(matrix[rank][col],matrix[row][col])
            u,v = matrix[rank][col]//d,matrix[row][col]//d
            matrix[row] = [u*x-v*y for x,y in zip(matrix[row],matrix[rank])]
            common = reduce(gcd,matrix[row],0)
            if common:
                matrix[row] = [x//common for x in matrix[row]]
        rank += 1
        if rank == height:
            break
    return rank


def incidence(edges, mask, constant):
    bits = []
    while mask:
        bit = mask & -mask
        bits.append(bit)
        mask ^= bit
    return [[int(bit == constant or bit == 1 << u or bit == 1 << v)
             for bit in bits] for u,v in edges]


def verify(certificate):
    a,b = 25,23
    m,d = a*b,a+b-1
    rows = (list(range(a))+list(range(1,a))+[0])[:d]
    cols = ([a-1]+list(range(a-1))+list(range(a)))[-d:]
    require(certificate['dimensions'] == [a,b] and certificate['m'] == m
            and certificate['d'] == d, 'Wrong selected corner dimensions')
    require(certificate['R'] == rows and certificate['C'] == cols,
            'Wrong controlled boundary prescription')
    require(certificate['gamma_offset'] == (m-d)%b, 'Wrong column residue offset')
    left = [Q((r+1)**2,sum(s*s for s in range(1,a+1))) for r in range(a)]
    right = [Q((t+1)**3,sum(s**3 for s in range(1,b+1))) for t in range(b)]
    witness = certificate['witness']
    require(list(map(Q,witness['left_weights'])) == left and
            list(map(Q,witness['right_weights'])) == right,
            'Wrong rational witness weights')
    require(sum(left) == sum(right) == 1 and all(left) and all(right),
            'Degenerate normalized witness')
    matrix = [[Q(rows[i]==cols[j])/left[rows[i]]
               +Q(i%b==(m-d+j)%b)/right[i%b]-1
               for j in range(d)] for i in range(d)]
    available = list(range(d))
    pivots = []
    require(len(witness['pivots']) == d, 'Incomplete rational pivot certificate')
    for row,(saved_row,saved_col,saved_value) in enumerate(witness['pivots']):
        col = next((j for j in reversed(available) if matrix[row][j]),None)
        require(saved_row == row and col == saved_col and col is not None,
                'Wrong rightmost rational pivot')
        value = matrix[row][col]
        require(value == Q(saved_value) and value != 0, 'Wrong rational pivot value')
        pivots.append((row,col))
        available.remove(col)
        for r in range(row+1,d):
            if matrix[r][col]:
                ratio = matrix[r][col]/value
                for c in available:
                    matrix[r][c] -= ratio*matrix[row][c]
                matrix[r][col] = 0
    runs = []
    for row,col in pivots:
        if runs and row == runs[-1][-1][0]+1 and col == runs[-1][-1][1]+1:
            runs[-1].append([row,col])
        else:
            runs.append([[row,col]])
    require(certificate['runs'] == runs, 'Wrong contiguous pivot runs')
    profile = dict(singletons=sum(len(run)==1 for run in runs),
                   blocks=[len(run) for run in runs if len(run)>1]+[m-2*d],
                   rank=m-d)
    require(profile == certificate['data_profile'] ==
            dict(singletons=11,blocks=[21,15,481],rank=528),
            'Wrong selected data profile')
    constant = 1 << (a+b)
    full = (constant << 1)-1
    zero_records = certificate['zero_minor_certificates']
    require(len(zero_records) == 315, 'Wrong number of zero-minor certificates')
    selected_rows,selected_cols = [],[]
    position = 0
    for row,pivot in pivots:
        for col in range(pivot+1,d):
            if col in selected_cols:
                continue
            require(position < len(zero_records), 'Missing rightmost-zero minor')
            record = zero_records[position]
            position += 1
            require((record['row'],record['col'],record['size']) ==
                    (row,col,row+1), 'Wrong zero-minor coverage/order')
            partition = record['partition']
            require(isinstance(partition,int) and 0 <= partition <= full,
                    'Invalid incidence partition')
            row_edges = [(rows[i],a+i%b) for i in selected_rows+[row]]
            col_edges = [(cols[j],a+(m-d+j)%b) for j in selected_cols+[col]]
            r1 = integer_rank(incidence(row_edges,partition,constant))
            r2 = integer_rank(incidence(col_edges,full^partition,constant))
            require(r1 == record['row_rank'] and r2 == record['column_rank'],
                    'Wrong exact partition ranks')
            require(r1+r2 < row+1, 'Partition fails to force zero minor')
            require(record['common_independent_size'] == r1+r2,
                    'Inconsistent archived intersection rank')
        selected_rows.append(row)
        selected_cols.append(pivot)
    require(position == len(zero_records), 'Unused or duplicated minor certificate')
    return dict(dimensions=[a,b], rational_pivots=d, zero_minors=position,
                integer_rank_checks=2*position, data_profile=profile,
                exact=True, matroid_search_repeated=False)

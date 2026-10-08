"""Exact ordered-corner certificates for PR29's retained (55,53) basis."""
from pathlib import Path
from fractions import Fraction as Q
import importlib.util
import json

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('incidence_rank',HERE/'a5-residual-symbolic.py')
helpers = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helpers)


def setup(a,b):
    assert a == b+2
    m,d = a*b,a+b-1
    rows = (list(range(a))+list(range(1,a))+[0])[:d]
    cols = ([a-1]+list(range(a-1))+list(range(a)))[-d:]
    helpers.A,helpers.B = a,b
    helpers.VERTICES = a+b
    helpers.CONSTANT = 1 << (a+b)
    helpers.ALL = (helpers.CONSTANT << 1)-1
    helpers.LEFT = (1 << a)-1
    helpers.RIGHT = helpers.CONSTANT-1-helpers.LEFT
    return m,d,rows,cols


def rational_pivots(a,b,rows,cols):
    m,d = a*b,a+b-1
    left = [Q((r+1)**2,sum(s*s for s in range(1,a+1))) for r in range(a)]
    right = [Q((t+1)**3,sum(s**3 for s in range(1,b+1))) for t in range(b)]
    assert sum(left) == sum(right) == 1
    matrix = [[Q(rows[i]==cols[j])/left[rows[i]]
        +Q(i%b==(m-d+j)%b)/right[i%b]-1 for j in range(d)] for i in range(d)]
    available = list(range(d))
    pivots = []
    for row in range(d):
        col = next(j for j in reversed(available) if matrix[row][j])
        value = matrix[row][col]
        pivots.append((row,col,value))
        available.remove(col)
        for r in range(row+1,d):
            if matrix[r][col]:
                ratio = matrix[r][col]/value
                for c in available:
                    matrix[r][c] -= ratio*matrix[row][c]
                matrix[r][col] = 0
    return dict(left_weights=list(map(str,left)),right_weights=list(map(str,right)),
        pivots=[(r,c,str(v)) for r,c,v in pivots])


def run(a=55,b=53):
    m,d,rows,cols = setup(a,b)
    witness = rational_pivots(a,b,rows,cols)
    print('Exact rational pivots:',len(witness['pivots']),flush=True)
    pivots = [(r,c) for r,c,_ in witness['pivots']]
    runs = []
    for r,c in pivots:
        if runs and r == runs[-1][-1][0]+1 and c == runs[-1][-1][1]+1:
            runs[-1].append((r,c))
        else:
            runs.append([(r,c)])
    assert [len(run) for run in runs] == [1,51,1,1,1,1,1,1,45,1,1,1,1]
    print('Ordered runs:',[len(run) for run in runs],flush=True)
    selected_rows,selected_cols = [],[]
    zeros = []
    for row,pivot in pivots:
        row_edges = [(rows[i],a+i%b) for i in selected_rows+[row]]
        f = helpers.Forest(row_edges)
        for col in range(pivot+1,d):
            if col in selected_cols:
                continue
            col_edges = [(cols[j],a+(m-d+j)%b) for j in selected_cols+[col]]
            g = helpers.Forest(col_edges)
            independent,partition = helpers.common_basis_or_partition(f,g)
            r1,r2 = f.rank(partition),g.rank(helpers.ALL^partition)
            size = row+1
            assert r1+r2 < size,(row,col,size,r1,r2)
            assert helpers.integer_rank(helpers.incidence(row_edges,partition)) == r1
            assert helpers.integer_rank(helpers.incidence(col_edges,helpers.ALL^partition)) == r2
            zeros.append(dict(row=row,col=col,size=size,partition=partition,
                row_rank=r1,column_rank=r2,common_independent_size=independent.bit_count()))
        selected_rows.append(row)
        selected_cols.append(pivot)
    assert len(zeros) == 2265
    return dict(dimensions=[a,b],m=m,d=d,R=rows,C=cols,gamma_offset=(m-d)%b,
        witness=witness,runs=runs,zero_minor_certificates=zeros,
        data_profile=dict(singletons=11,blocks=[51,45,m-2*d],rank=m-d),
        status='EXACT LOCAL CORNER CERTIFICATE; NO NETWORK OR EXPONENT UPDATE')


if __name__ == '__main__':
    result = run()
    path = HERE/'a5-residual-two-stage.json'
    path.write_text(json.dumps(result,indent=2)+'\n')
    print('PASS',len(result['zero_minor_certificates']),'exact zero-minor certificates',flush=True)

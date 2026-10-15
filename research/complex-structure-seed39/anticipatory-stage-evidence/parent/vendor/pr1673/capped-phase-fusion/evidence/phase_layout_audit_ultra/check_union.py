"""Independent exact five-factor and sparse-union stream audit."""
from fractions import Fraction as Q
from itertools import product
from pathlib import Path
import json
HERE=Path(__file__).resolve().parent

def eye(n):return [[Q(i==j) for j in range(n)] for i in range(n)]
def mm(a,b):return [[sum(x*y for x,y in zip(row,col)) for col in zip(*b)] for row in a]
def inverse(a):
    n=len(a);rows=[r.copy()+e for r,e in zip(a,eye(n))]
    for j in range(n):
        k=next(i for i in range(j,n) if rows[i][j]);rows[j],rows[k]=rows[k],rows[j]
        v=rows[j][j];rows[j]=[x/v for x in rows[j]]
        for i in range(n):
            if i!=j:
                v=rows[i][j]
                if v:rows[i]=[x-v*y for x,y in zip(rows[i],rows[j])]
    return [r[n:] for r in rows]
def block(h,rows,cols):return [[h[i][j] for j in cols] for i in rows]
def put(base,rows,cols,a):
    for ii,i in enumerate(rows):
        for jj,j in enumerate(cols):base[i][j]=a[ii][jj]
    return base
def add(a,b,sgn=1):return [[x+sgn*y for x,y in zip(r,s)] for r,s in zip(a,b)]
def embedded(a,I,n):return put(eye(n),I,I,a)

def factors(n,den):
    H=eye(n)
    for i in range(n-1):H[i][i+1]=H[i+1][i]=Q(1,den)
    J=[0,5,6,11];I=[i for i in range(n) if i not in J]
    A,B,C,D=block(H,I,I),block(H,I,J),block(H,J,I),block(H,J,J)
    Ai=inverse(A);S=add(D,mm(mm(C,Ai),B),-1);Si=inverse(S)
    lower=put(eye(n),J,I,[[-x for x in r] for r in C])
    upper=put(eye(n),I,J,[[-x for x in r] for r in B])
    seq=[embedded(Ai,I,n),lower,embedded(Si,J,n),embedded(A,I,n),upper,embedded(Ai,I,n)]
    full=eye(n)
    for f in seq:full=mm(f,full)
    assert full==inverse(H)
    E=sorted({j+v for j in J for v in (-1,0,1) if 0<=j+v<n})
    for f in (lower,embedded(Si,J,n),upper):
        assert all(f[i][j]==Q(i==j) for i in range(n) for j in range(n) if i not in E or j not in E)
    return H,seq,E,I,J

def axis_apply(state,mat,axis,n,g):
    out={}
    for other in product(range(n),repeat=g-1):
        def index(i):return other[:axis]+(i,)+other[axis:]
        old=[state[index(i)] for i in range(n)]
        for i,row in enumerate(mat):out[index(i)]=sum(x*y for x,y in zip(row,old))
    return out

def union_window(state,mats,Es,n,g):
    U=[x for x in product(range(n),repeat=g) if any(x[i] in Es[i] for i in range(g))]
    sparse={x:state[x] for x in U};ref=state.copy();counts=[]
    for i,mat in enumerate(mats):
        Ui=[x for x in U if x[i] in Es[i]]
        assert len(Ui)==len(Es[i])*n**(g-1)
        extracted={x:sparse[x] for x in Ui}
        restricted=block(mat,Es[i],Es[i]);updated={}
        for other in product(range(n),repeat=g-1):
            def index(j):return other[:i]+(j,)+other[i:]
            vec=[extracted[index(j)] for j in Es[i]]
            for j,row in zip(Es[i],restricted):updated[index(j)]=sum(a*b for a,b in zip(row,vec))
        assert set(updated)==set(Ui)
        sparse.update(updated);ref=axis_apply(ref,mat,i,n,g)
        assert all(sparse[x]==ref[x] for x in U)
        assert all(ref[x]==state[x] for x in state if x not in sparse)
        counts.append(len(Ui))
    out=state.copy();out.update(sparse);assert out==ref
    return out,dict(union_records=len(U),axis_rectangles=counts,all_rectangles_complete=True)

def main():
    n=12;g=2;data={x:Q(1+sum((i+2)*(v+1)**2 for i,v in enumerate(x))) for x in product(range(n),repeat=g)}
    Fs=[factors(n,den) for den in (16,17)];Es=[f[2] for f in Fs]
    reference=data
    for i,(H,seq,E,I,J) in enumerate(Fs):reference=axis_apply(reference,inverse(H),i,n,g)
    state=data.copy();windows=[]
    for stage in (0,):
        for i,f in enumerate(Fs):state=axis_apply(state,f[1][stage],i,n,g)
    # Consecutive C and S^-1 sparse stages share one gathered union.
    for stage in (1,2):
        state,receipt=union_window(state,[f[1][stage] for f in Fs],Es,n,g);windows.append(receipt)
    for i,f in enumerate(Fs):state=axis_apply(state,f[1][3],i,n,g)
    state,receipt=union_window(state,[f[1][4] for f in Fs],Es,n,g);windows.append(receipt)
    for i,f in enumerate(Fs):state=axis_apply(state,f[1][5],i,n,g)
    assert state==reference
    # Dense A^-1 must not be restricted to the sparse union.
    U={x for x in data if any(x[i] in Es[i] for i in range(g))}
    probe={x:Q(int(x==(1,2))) for x in data}
    assert (1,2) in U
    spread=axis_apply(probe,Fs[0][1][0],0,n,g)
    escapes=[x for x in data if x not in U and spread[x]]
    assert escapes
    out=dict(status='PASS_EXACT_FIVE_FACTOR_SPARSE_UNION_STREAM_AUDIT',n=n,g=g,total_records=len(data),
        axes=[dict(boundary_J=f[4],closed_support_E=f[2]) for f in Fs],
        tensor_inverse_matches_grouped_six_stages=True,arbitrary_signed_input_columns_supported=True,
        sparse_stage_replays=windows,physical_sparse_windows=2,
        consecutive_C_and_S_inverse_reuse_same_closed_union=True,
        dense_A_inverse_escapes_union_control=[list(x) for x in escapes],
        scope='Exact scalar/tensor identity, complete restricted rectangles and missing-zero control; no floating arithmetic.')
    (HERE/'UNION-CONTROLS.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':main()

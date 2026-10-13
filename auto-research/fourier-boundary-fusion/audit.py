"""Fourier propagation through a copied-center scatter and coordinate cuts.

Douglas Colkitt, with OpenAI Codex assistance. Apache-2.0.
All arithmetic is exact over Q(i); no new network or exponent.
"""
from fractions import Fraction as Q
from itertools import combinations
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
_spec=importlib.util.spec_from_file_location(
    'direct_selected_xor_audit',ROOT/'research/direct-selected-xor/audit.py')
_direct=importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_direct)
walsh=_direct.walsh
sys.path.insert(0,str(ROOT/'research/geometry-circuit-discovery'))
from screen import rational_rank,encode,require

ZERO=(Q(0),Q(0));ONE=(Q(1),Q(0))


def add(a,b):return a[0]+b[0],a[1]+b[1]
def mul(a,b):return a[0]*b[0]-a[1]*b[1],a[0]*b[1]+a[1]*b[0]
def scale(a,b):return a[0]*b,a[1]*b


def c_direction(values,mask,inverse=False):
    a=(Q(1,2),Q(-1 if inverse else 1,2))
    b=(Q(1,2),Q(1 if inverse else -1,2))
    return [add(mul(a,v),mul(b,values[i^mask])) for i,v in enumerate(values)]


def tensor_c(values,bits,inverse=False):
    for bit in bits:values=c_direction(values,1<<bit,inverse)
    return values


def phase(values,exponent):
    units=[ONE,(Q(0),Q(1)),(Q(-1),Q(0)),(Q(0),Q(-1))]
    return [mul(units[exponent(i)%4],v) for i,v in enumerate(values)]


def iw(values,bits):
    return [scale(v,Q(1,1<<len(bits))) for v in walsh(values,bits)]


def star(streams,coeffs,kind='B',h=4,omit=0,encoded=False,align_targets=True):
    """Actual copied-center subword in the suppressed active-factor chart.

    copy z; R on copy; y_t += alpha_t Rz; discard copy; Q on original z.
    D: U is the coordinate hyperplane. B: U=n^perp, n=all except omit.
    For even h, n has odd norm and C_n-line = C_n^(h-1 mod 4).
    """
    require(h%2==0 and len(streams)==len(coeffs)+1,'star contract')
    J=[j for j in range(h) if j!=omit];mask=sum(1<<j for j in J)
    w=h-1
    normphase=lambda index:w*((index&mask).bit_count()%2)
    z=list(streams[0]);targets=[list(x) for x in streams[1:]]
    if encoded:
        z=walsh(z,J)
        if align_targets:targets=[walsh(x,J) for x in targets]
        if kind=='D':
            read=phase(z,lambda i:-(i&mask).bit_count())
            cleanup=c_direction(z,1<<omit)
        else:
            read=c_direction(z,1<<omit,True)
            read=phase(read,lambda i:-(i&mask).bit_count()+normphase(i))
            cleanup=phase(z,normphase)
    else:
        if kind=='D':
            read=tensor_c(z,J,True);cleanup=c_direction(z,1<<omit)
        else:
            cleanup=c_direction(z,mask,inverse=(w%4==3))
            read=tensor_c(cleanup,list(range(h)),True)
    targets=[[add(y,scale(x,a)) for x,y in zip(read,target)] for target,a in zip(targets,coeffs)]
    if encoded:
        cleanup=iw(cleanup,J)
        if align_targets:targets=[iw(x,J) for x in targets]
    return [cleanup]+targets


def scatter_column(kind,h=28,d0=19):
    require(kind in ('D','B') and (h,d0)==(28,19),'pinned mixed-center instance')
    i=0 if kind=='D' else d0
    out=[]
    for S in combinations(range(h),3):
        k=sum(j<d0 for j in S)
        alpha=(-Q(int(i in S),2)+Q(k-1,32) if kind=='D'
               else Q(int(i in S),4)-Q(k-1,64))
        if alpha:out.append((S,alpha))
    return out


def operator_matrix(fn,width):
    columns=[]
    for j in range(width):columns.append(fn([ONE if i==j else ZERO for i in range(width)]))
    return [list(row) for row in zip(*columns)]


def complex_rank(matrix):
    # Realification has exactly twice the Q(i) rank.
    real=[[v[0] for v in row]+[-v[1] for v in row] for row in matrix]
    real += [[v[1] for v in row]+[v[0] for v in row] for row in matrix]
    r=rational_rank(real);require(r%2==0,'complex rank parity');return r//2


def defect(matrix,pout,pin):
    return [[scale(v,pout[i]-pin[j]) for j,v in enumerate(row)] for i,row in enumerate(matrix)]


def cut_checks():
    rows=[]
    for e in (1,2,3):
        M=1<<e
        full=operator_matrix(lambda v:tensor_c(v,list(range(e))),M)
        for j in range(e):
            p=[(i>>j)&1 for i in range(M)]
            r=complex_rank(defect(full,p,p));require(r==M,'full tensor cut rank')
            rows.append(dict(e=e,cut=j,target_rank=r,M=M))
        for subset in ([0],list(range(e))):
            child=operator_matrix(lambda v:tensor_c(v,subset),M)
            ranks=[]
            for j in range(e):
                p=[(i>>j)&1 for i in range(M)]
                r=complex_rank(defect(child,p,p));require(r==(M if j in subset else 0),'coordinate-child cut rank')
                ranks.append(r)
            require(sum(ranks)==len(subset)*M,'total coordinate rank budget')
    return rows


def audit():
    stars=[]
    for kind in ('D','B'):
        column=scatter_column(kind);coeffs=[column[0][1],column[-1][1]]
        require(len(set(coeffs))>0,'actual nonzero scatter coefficients')
        h=4;M=1<<h;trials=0;bad_example=None
        for j in range(3*M):
            streams=[[ONE if r*M+i==j else ZERO for i in range(M)] for r in range(3)]
            expected=star(streams,coeffs,kind,h)
            require(star(streams,coeffs,kind,h,encoded=True)==expected,'complete arbitrary-input star basis')
            if star(streams,coeffs,kind,h,encoded=True,align_targets=False)!=expected and bad_example is None:
                bad_example=j
            trials+=1
        require(bad_example is not None,'alignment cannot be omitted')
        k=len(column)
        stars.append(dict(kind=kind,h=28,nonzero_target_dependencies=k,
            scatter_coefficients=sorted(set(a for _,a in column)),
            local_basis_dimension=h,tested_basis_columns=trials,
            omitted_target_alignment_failure_column=bad_example,
            old_copy_and_cleanup_rank=28,
            new_coordinate_child_rank=2*27*(k+1)+1,
            scope='One isolated column of the actual scatter map, entering and returning every participating stream in its old frame. Active chart and partial-transform packing granted free; not a lower bound for every possible shared scatter implementation.'))
    sources=['notes/copied-centers-lemma.tex','notes/copied-centers-complex.tex',
        'notes/compact-control-layout.tex','research/direct-selected-xor/REPORT.md',
        'research/direct-selected-xor/audit.py',
        'research/geometry-circuit-discovery/screen.py',
        'research/fourier-boundary-fusion/audit.py',
        'research/fourier-boundary-fusion/test_audit.py']
    return dict(status='EXACT CROSS-GATE FUSION TEST AND SCOPED COORDINATE-CUT OBSTRUCTION',
        stars=stars,cut_rank_checks=cut_checks(),
        coordinate_cut_lemma=dict(necessary_budget='sum_l(q_l M_l) >= e M',
            consequence='A pure coordinate-kernel/diagonal/pointwise replacement cannot have strict normalized child-rank contraction.',
            scope='Linear arithmetic; arbitrary original inputs; fixed physical selected coordinates; free maps intertwine each cut; child dimension is actual coefficient-stream dimension. Noncoordinate movement is outside this model.'),
        new_exponent_claimed=False,positive_construction_selected=False,
        source_sha256={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in sources})


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path);args=parser.parse_args()
    result=audit()
    if args.output:args.output.write_text(json.dumps(encode(result),indent=2,sort_keys=True)+'\n')
    for s in result['stars']:print(s['kind'],'targets',s['nonzero_target_dependencies'],'old/new rank',s['old_copy_and_cleanup_rank'],s['new_coordinate_child_rank'])
    print('PASS exact star operators and coordinate cut-rank controls; no stronger exponent')

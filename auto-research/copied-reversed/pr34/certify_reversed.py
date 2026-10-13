"""Exact author certificate for the reversed (h,h+2) boundary family.

Only Python's standard library is imported. No supplier code is executed.
"""
from fractions import Fraction as Q
from pathlib import Path
import hashlib,json,time,argparse

ROOT=Path(__file__).resolve().parent

def geometry(h):
    a,b=h,h+2;d=a+b-1;m=a*b
    rows=list(range(h))+[h-1]+list(range(h))
    cols=list(range(h))+[0]+list(range(h))
    re=list(zip(rows,[i%b for i in range(d)]))
    ce=list(zip(cols,[(m-d+i)%b for i in range(d)]))
    assert len(rows)==len(cols)==d and (m-d)%b==3
    prescribed=[{} for _ in range(b)]
    for labels,start in [(rows,0),(cols,m-d)]:
        for i,label in enumerate(labels):
            physical=start+i;alpha,beta=divmod(physical,b)
            assert alpha not in prescribed[beta]
            assert label not in prescribed[beta].values()
            prescribed[beta][alpha]=label
    perms=[]
    for constraints in prescribed:
        unused=iter(v for v in range(a) if v not in constraints.values())
        perm=[constraints[i] if i in constraints else next(unused) for i in range(a)]
        assert sorted(perm)==list(range(a));perms.append(perm)
    piv=[2*h]+[i+h+1 for i in range(1,h-1)]+[2*h-i for i in range(h-1,h+5)]+[i-h-3 for i in range(h+5,2*h-1)]+[1,0]
    assert sorted(piv)==list(range(d))
    return a,b,d,m,rows,cols,re,ce,perms,piv

def forest_rank(a,b,edges,selected):
    parent=list(range(a+b))
    def find(i):
        while parent[i]!=i:i=parent[i]
        return i
    for u,v in edges:
        u,v=find(u),find(a+v)
        assert u!=v,'Cycle contradicts the tree/forest hypothesis'
        parent[u]=v
    comps={}
    for i in range(a+b):comps.setdefault(find(i),set()).add(i)
    value=0;constant_dependent=True
    for vs in comps.values():
        if len(vs)==1:continue
        value+=min(len(vs&selected),len(vs)-1)
        if any(i not in selected for i in vs if i<a) and any(i not in selected for i in vs if i>=a):constant_dependent=False
    if a+b in selected and not constant_dependent:value+=1
    return value

def exact_witness(a,b,rows,cols,re,ce,piv):
    sx=sum(i*i for i in range(1,a+1));sy=sum(i**3 for i in range(1,b+1))
    xx=[Q(sx,(i+1)**2) for i in range(a)]
    yy=[Q(sy,(j+1)**3) for j in range(b)]
    assert sum(1/x for x in xx)==sum(1/y for y in yy)==1
    mat=[[xx[r]*(r==c)+yy[be]*(be==ga)-1 for c,ga in ce] for r,be in re]
    values=[]
    for i,expected in enumerate(piv):
        nz=[j for j,z in enumerate(mat[i]) if z]
        assert nz and nz[-1]==expected,(i,expected,nz[-1] if nz else None)
        value=mat[i][expected];values.append(str(value))
        active=[j for j in range(expected+1) if mat[i][j]]
        for k in range(i+1,len(rows)):
            if mat[k][expected]:
                factor=mat[k][expected]/value
                for j in active:mat[k][j]-=factor*mat[i][j]
                assert not mat[k][expected]
    return dict(p='all ones',v='all ones',xi_denominator=sx,nu_denominator=sy,xi_numerators=[i*i for i in range(1,a+1)],nu_numerators=[i**3 for i in range(1,b+1)],pivot_values=values)

def certify(h):
    a,b,d,m,rows,cols,re,ce,perms,piv=geometry(h)
    universe=set(range(a+b+1));cuts=[]
    for i,j in enumerate(piv):
        prior=sum(q>j for q in piv[:i])
        if 1<=i<=h-2:
            selected=set(range(i+1,a))|set(range(a+i+1,a+b))|{a+b}
            expected=(1,0)
        elif h+5<=i<=2*h-2:
            t=i-h-5
            selected=set(range(3+t,a))|set(range(a+5+t,a+b))
            expected=(h-1-t,6+t)
        else:
            # All suffix columns were already selected; dimension is enough.
            assert prior==d-1-j
            cuts.append(dict(row=i,column=j,prior=prior,method='column_count'));continue
        r1=forest_rank(a,b,re[:i+1],selected)
        r2=forest_rank(a,b,ce[j+1:],universe-selected)
        assert (r1,r2)==expected and r1+r2==prior
        cuts.append(dict(row=i,column=j,prior=prior,method='incidence_cut',selected=sorted(selected),ranks=[r1,r2]))
    witness=exact_witness(a,b,rows,cols,re,ce,piv)
    profile=[1]*9+[h-2,h-6,m-2*d]
    assert sum(profile)==(a-1)*(b-1) and max(profile)<m
    runs=[]
    for i,j in enumerate(piv):
        if i and j==piv[i-1]+1:runs[-1]+=1
        else:runs.append(1)
    assert sorted(runs)==sorted([1]*9+[h-2,h-6])
    # Opposite h+2/h boundary residue does not describe this actual corner.
    assert (m-d)%b!=b-1
    # Check complete basis constraints in both directions from the saved permutations.
    for i,label in enumerate(rows):
        alpha,beta=divmod(i,b);assert perms[beta][alpha]==label
    for i,label in enumerate(cols):
        alpha,beta=divmod(m-d+i,b);assert perms[beta].index(label)==alpha
    return dict(h=h,a=a,b=b,m=m,d=d,row_labels=rows,column_labels=cols,row_edges=re,column_edges=ce,permutation_completions=perms,pivots=piv,runs=runs,profile=profile,rank_cuts=cuts,witness=witness)

def main():
    p=argparse.ArgumentParser();p.add_argument('--h',type=int,default=45);p.add_argument('--output',type=Path,default=ROOT/'REVERSED_45_CERTIFICATE.json');args=p.parse_args()
    started=time.monotonic();result=certify(args.h)
    result['checker_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(h=args.h,profile=result['profile'],exact_nonzero_pivots=len(result['witness']['pivot_values']),rank_cuts=len(result['rank_cuts']),seconds=time.monotonic()-started)))

if __name__=='__main__':main()

from pathlib import Path
from fractions import Fraction
from math import gcd
import hashlib,json,resource,time
resource.setrlimit(resource.RLIMIT_AS,(100*1024*1024,100*1024*1024))
resource.setrlimit(resource.RLIMIT_CPU,(110,110))
HERE=Path(__file__).resolve().parent

def exact_rank(rows):
    pivots={}
    for row in rows:
        row=list(row)
        for j,p in pivots.items():
            if row[j]:
                a,b=p[j],row[j]
                row=[a*x-b*y for x,y in zip(row,p)]
                factor=0
                for x in row:factor=gcd(factor,x)
                if factor:row=[x//factor for x in row]
        j=next((j for j,x in enumerate(row) if x),None)
        if j is not None:
            factor=0
            for x in row:factor=gcd(factor,x)
            if row[j]<0:factor=-factor
            pivots[j]=[x//factor for x in row]
    return len(pivots)

def corner_labels(h):
    d=2*h+1;b=h+2
    r=list(range(h))+[h-1]+list(range(h))
    c=list(range(h))+[0]+list(range(h))
    return [(r[i],i%b) for i in range(d)],[(c[j],(h*b-d+j)%b) for j in range(d)]

def expected_pivots(h):
    return [2*h]+[i+h+1 for i in range(1,h-1)]+[2*h-i for i in range(h-1,h+5)]+[i-h-3 for i in range(h+5,2*h-1)]+[1,0]

def completion(h,rows,cols):
    b=h+2;m=h*b;d=len(rows)
    partial=[{} for _ in range(b)]
    for seq,offset in [(rows,0),(cols,m-d)]:
        for k,(label,residue) in enumerate(seq):
            alpha,physical_residue=divmod(offset+k,b)
            assert residue==physical_residue
            assert alpha not in partial[residue] or partial[residue][alpha]==label
            assert label not in partial[residue].values() or partial[residue].get(alpha)==label
            partial[residue][alpha]=label
    result=[]
    for prescribed in partial:
        remaining=iter(sorted(set(range(h))-set(prescribed.values())))
        p=[prescribed[i] if i in prescribed else next(remaining) for i in range(h)]
        assert sorted(p)==list(range(h))
        result.append(p)
    for seq,offset in [(rows,0),(cols,m-d)]:
        for k,(label,residue) in enumerate(seq):
            assert result[residue][(offset+k)//b]==label
    assert [r for r,beta in rows[:h]]==list(range(h))
    assert [c for c,gamma in cols[-h:]]==list(range(h))
    assert [beta for r,beta in rows[:b]]==list(range(b))
    assert [gamma for c,gamma in cols[-b:]]==list(range(b))
    return result

def witness(h,rows,cols,degree):
    # This witness deliberately differs from the author's square/cubic weights.
    wa=[(i+1)**degree+1 for i in range(h)]
    wb=[(2*i+1)**degree+2 for i in range(h+2)]
    sa,sb=sum(wa),sum(wb);den=sa*sb;d=len(rows)
    A=[[int(beta==gamma)*wa[c]*sb+int(r==c)*wb[gamma]*sa-wa[c]*wb[gamma] for c,gamma in cols] for r,beta in rows]
    available=set(range(d));previous=1;pivs=[];vals=[];prefix=[]
    for i in range(d):
        col=max(j for j in available if A[i][j]);piv=A[i][col]
        pivs.append(col);vals.append(str(Fraction(piv,previous*den)));prefix.append(str(Fraction(piv,den**(i+1))))
        available.remove(col)
        for k in range(i+1,d):
            for j in available:
                value=piv*A[k][j]-A[k][col]*A[i][j]
                assert value%previous==0
                A[k][j]=value//previous
            A[k][col]=0
        previous=piv
    assert pivs==expected_pivots(h),(h,degree,pivs)
    widths=[]
    for i,j in enumerate(pivs):
        if i and j==pivs[i-1]+1:widths[-1]+=1
        else:widths.append(1)
    assert sorted(t for t in widths if t>1)==[h-6,h-2]
    assert widths.count(1)==9
    return {'degree':degree,'left_weights':wa,'right_weights':wb,'pivots':pivs,'pivot_values':vals,'ordered_prefix_determinants':prefix,'widths':widths}

def check_cuts(h,rows,cols,pivots):
    b=h+2;n=h+b+1;d=len(rows)
    F=[[int(k==r or k==h+beta or k==n-1) for k in range(n)] for r,beta in rows]
    G=[[int(k==c or k==h+gamma or k==n-1) for k in range(n)] for c,gamma in cols]
    records=[]
    for i,q in enumerate(pivots):
        preceding=sum(p>q for p in pivots[:i])
        if 1<=i<=h-2:
            selected=set(range(i+1,h))|set(range(h+i+1,h+b))|{n-1}
        elif h+5<=i<=2*h-2:
            t=i-h-5
            selected=set(range(3+t,h))|set(range(h+5+t,h+b))
        else:
            assert d-q-1==preceding
            records.append({'row':i,'pivot':q,'trivial_suffix_bound':preceding})
            continue
        left=exact_rank([[r[k] for k in range(n) if k in selected] for r in F[:i+1]])
        right=exact_rank([[r[k] for k in range(n) if k not in selected] for r in G[q+1:]])
        assert left+right<=preceding,(h,i,q,left,right,preceding)
        records.append({'row':i,'pivot':q,'selected':sorted(selected),'left_rank':left,'right_rank':right,'preceding_right_pivots':preceding})
    return records

def main():
    start=time.monotonic();out={'author_code_executed':False,'cases':[]}
    for h in [45,53]:
        rows,cols=corner_labels(h)
        result={'h':h,'dimensions':[h,h+2],'rows':rows,'columns':cols,'permutation_completions':completion(h,rows,cols),'cuts':check_cuts(h,rows,cols,expected_pivots(h)),'witnesses':[witness(h,rows,cols,degree) for degree in [1,2]]}
        result['rank_mass']=9+(h-2)+(h-6)+(h*h-2*h-2)
        assert result['rank_mass']==h*(h+2)-(2*h+1)
        out['cases'].append(result)
    out['elapsed_seconds']=time.monotonic()-start
    (HERE/'INDEPENDENT_CONTROLS.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'dimensions':[case['dimensions'] for case in out['cases']],'all_pass':True,'elapsed_seconds':out['elapsed_seconds']}))
if __name__=='__main__':main()

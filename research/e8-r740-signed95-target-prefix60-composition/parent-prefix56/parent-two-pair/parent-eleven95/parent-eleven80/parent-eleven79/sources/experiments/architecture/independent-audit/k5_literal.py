"""Independent tiny K5 dirty/private-work literal replay using integer32 grid."""
from fractions import Fraction as Q
from itertools import combinations
from pathlib import Path
import json
P=Path(__file__).resolve().parent;ROOT=P.parents[2];D=ROOT/'experiments/architecture/k5-dual'
def axpy(rows,d,s,c):
    for k,x in list(rows[s].items()):
        rows[d][k]=rows[d].get(k,0)+c*x
        if not rows[d][k]:del rows[d][k]
def generate(h,mode):
    ports=list(map(set,combinations(range(h),5)));v=len(ports);pairs=list(map(set,combinations(range(h),2)))
    members=([[i for i,S in enumerate(ports) if k in S] for k in range(h)] if mode=='bit' else [[i for i,S in enumerate(ports) if pair<=S] for pair in pairs]+[list(range(v))])
    corrections=[];scat=[]
    for t,T in enumerate(ports):
        if mode=='bit':scat.append([(i,Q(1)) for i in sorted(T)])
        else:
            row=[]
            for i,pair in enumerate(pairs):
                j=len(pair&T)
                if j:row.append((i,Q(1,16) if j==2 else Q(-3,32)))
            row.append((len(pairs),Q(3,8)));scat.append(row)
        for s,S in enumerate(ports):
            j=len(S&T)
            if t!=s and (j%2==1 if mode=='bit' else j%2==0):corrections.append((t,s,Q(-1) if mode=='bit' else -Q((j-1)*(j-3),8)))
    start=2*v;cs=start+len(corrections);N=cs+len(members);work=N
    copy=[(start+i,s,Q(1)) for i,(t,s,c) in enumerate(corrections)]
    side=[(v+t,start+i,c) for i,(t,s,c) in enumerate(corrections)]
    gather=[(cs+i,s,Q(1)) for i,mem in enumerate(members) for s in mem]
    scatter=[(v+t,cs+i,c) for t,row in enumerate(scat) for i,c in row]
    signed=lambda word,sgn:[(d,s,c*sgn) for d,s,c in word]
    gates=signed(side,-1)+signed(scatter,-1)+copy+gather+scatter+side+signed(gather,-1)+signed(copy,-1)
    literal=[]
    for d,s,c in gates:
        if c.denominator==1:literal += [('add',d,s,1 if c>0 else -1)]*abs(c.numerator)
        else:
            e=c.denominator.bit_length()-1;assert 2**e==c.denominator
            literal.append(('add',work,s,1));literal += [('half',work,work,0)]*e
            literal += [('add',d,work,1 if c>0 else -1)]*abs(c.numerator)
            literal += [('double',work,work,0)]*e;literal.append(('add',work,s,-1))
    return ports,N,literal
def replay(word,N):
    rows=[{i:32} for i in range(N)]+[{}];peak=32
    for op,d,s,c in word:
        if op=='add':axpy(rows,d,s,c)
        elif op=='double':rows[d]={k:2*x for k,x in rows[d].items()}
        else:
            assert op=='half' and all(x%2==0 for x in rows[d].values())
            rows[d]={k:x//2 for k,x in rows[d].items()}
        peak=max(peak,sum(abs(x) for x in rows[d].values()))
    return rows,Q(peak,32)
def main():
    claims=json.loads((D/'RESULT.json').read_text());checks=[]
    for h in [6,7]:
        for mode in ['bit','complex']:
            ports,N,word=generate(h,mode);v=len(ports);forward,peak=replay(word,N)
            expected=[{i:32} for i in range(N)]+[{}]
            inverseword=[('add',d,s,-c) if op=='add' else ('half' if op=='double' else 'double',d,s,0) for op,d,s,c in reversed(word)]
            inverse,ipeak=replay(inverseword,N);iexpected=[{i:32} for i in range(N)]+[{}]
            for t,T in enumerate(ports):
                for s,S in enumerate(ports):
                    j=len(S&T);coef=j-int(j%2==1 and t!=s) if mode=='bit' else int(t==s)
                    if coef:expected[v+t][s]=32*coef;iexpected[v+t][s]=-32*coef
            assert forward==expected and inverse==iexpected
            rec=next(x for x in claims['tiny'] if (x['h'],x['mode'])==(h,mode))
            assert len(word)==rec['literal_primitive_count'] and peak==Q(rec['literal_primitive_prefix_row_l1']) and ipeak==Q(rec['literal_primitive_inverse_prefix_row_l1'])
            checks.append(dict(h=h,mode=mode,all_signed_columns=N,private_work_zero=True,arbitrary_dirt_restored=True,source_restored=True,primitive_count=len(word),prefix=str(peak),inverse_prefix=str(ipeak)))
    out=dict(status='PASS_INDEPENDENT_ALL_TINY_K5_LITERAL_COLUMNS_DYADIC_GRID_DIRT_INVERSE_AND_PAYMENT',checks=checks,scope='Tiny scalar literal signed/dyadic programs on integer32 coefficient grid. No common-frame geometry, norm-contractive primitive admission, large-instance bank/layout or all-size supplier claim.')
    (P/'K5-LITERAL.json').write_text(json.dumps(out,indent=2)+'\n');print(out['status'])
if __name__=='__main__':main()

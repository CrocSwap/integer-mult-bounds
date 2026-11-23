"""Finite q-independent descriptor producer for the accepted dyadic catalogue.

New code prepared for CubeJerry with OpenAI assistance. Apache-2.0.
Accepted complete bases and predecessor semantics retain their own credit.
"""
from fractions import Fraction as F
from pathlib import Path
from hashlib import sha256
import json

HERE=Path(__file__).resolve().parent

def need(ok,message):
    if not ok:raise ValueError(message)
def eye(n):return [[F(i==j) for j in range(n)] for i in range(n)]
def mul(a,b):return [[sum((x*y for x,y in zip(r,c)),F(0)) for c in zip(*b)] for r in a]
def inverse(a):
    n=len(a);a=[list(row)+r for row,r in zip(a,eye(n))]
    for j in range(n):
        k=next((i for i in range(j,n) if a[i][j]),None)
        need(k is not None,'Singular source complete basis')
        a[j],a[k]=a[k],a[j];z=a[j][j];a[j]=[x/z for x in a[j]]
        for i in range(n):
            if i!=j:
                z=a[i][j];a[i]=[x-z*y for x,y in zip(a[i],a[j])]
    return [r[n:] for r in a]
def unit(v):
    v=abs(F(v));return bool(v) and not(v.numerator&(v.numerator-1)) and not(v.denominator&(v.denominator-1))

def eliminate(s):
    a=[list(x) for x in zip(*s)];n=len(a);ops=[];nonunit=[];repairs=[]
    for j in range(n):
        nz=next(i for i in range(j,n) if a[i][j])
        if not unit(a[nz][j]):nonunit.append([j,nz,str(a[nz][j])])
        k=next((i for i in range(j,n) if unit(a[i][j])),None)
        if k is None:
            short=next(((i,l,c) for i in range(j,n) for l in range(j,n) if i!=l
                        for c in (1,-1,2,-2) if unit(a[i][j]+c*a[l][j])),None)
            need(short is not None,'Outside this finite catalogue: no advertised short pivot repair')
            i,l,c=short
            repairs.append({'column':j,'target':i,'source':l,'coefficient':c,
                            'old_target':str(a[i][j]),'old_source':str(a[l][j])})
            a[i]=[x+c*y for x,y in zip(a[i],a[l])];ops.append(['add',i,l,str(c)]);k=i
        if k!=j:a[j],a[k]=a[k],a[j];ops.append(['swap',j,k])
        z=a[j][j]
        if z!=1:
            a[j]=[x/z for x in a[j]];ops.append(['scale',j,str(1/z)])
        for i in range(n):
            if i!=j and a[i][j]:
                z=a[i][j];a[i]=[x-z*y for x,y in zip(a[i],a[j])];ops.append(['add',i,j,str(-z)])
    need(a==eye(n),'Exact source route reduction')
    return ops,nonunit,repairs

def scale_atoms(coefficient):
    x=F(coefficient);need(unit(x),'Only dyadic-unit scales')
    exponent=abs(x.numerator).bit_length()-x.denominator.bit_length()
    if exponent==0:return ['-1'] if x<0 else []
    count=abs(exponent);one=F(2) if exponent>0 else F(1,2)
    return [str(-one if x<0 else one)]+[str(one)]*(count-1)

def main():
    bindings=json.loads((HERE/'INPUTS.json').read_text())
    for item in bindings['files']:
        need(sha256((HERE/item['path']).read_bytes()).hexdigest()==item['sha256'],'Source pin '+item['path'])
    rows=json.loads((HERE/'retained/bases.json').read_text());byrank={};out=[]
    for row in rows:
        b=[[F(x) for x in r] for r in row['alternative_basis']]
        pair,rank=row['pair'],row['rank']
        base_pair,target=byrank.setdefault(rank,(pair,b))
        s=mul(b,inverse(target));ops,bad,repairs=eliminate(s)
        counts={kind:sum(op[0]==kind for op in ops) for kind in ('swap','scale','add')}
        counts['earlier_target']=sum(op[0]=='add' and op[1]<op[2] for op in ops)
        counts['signed_dyadic_scale_atoms']=sum(len(scale_atoms(op[2])) for op in ops if op[0]=='scale')
        counts['full_ordinary_swaps']=8*(counts['swap']+2*counts['earlier_target'])
        counts['full_ordered_shifts_with_carry']=8*counts['add']+64
        counts['full_fixed_scalings']=8*counts['scale']
        counts['full_signed_dyadic_scale_atoms']=8*counts['signed_dyadic_scale_atoms']
        out.append({'pair':pair,'reference_pair':base_pair,'rank':rank,
                    'nonunit_first_pivots':bad,'short_repairs':repairs,'counts':counts,
                    'elimination_word':ops,'matrix':[[str(x) for x in r] for r in s]})
    report={'schema':'selected-dyadic-q-independent-route-words/1','base':bindings['canonical_base'],
            'catalogue_entries':len(out),'algorithm_scope':'this exact finite 513-entry catalogue; no universal short-repair guarantee',
            'routes':out}
    (HERE/'CATALOGUE.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'marker':'PASS_Q_INDEPENDENT_ROUTE_PRODUCTION','routes':len(out),
        'short_repairs':sum(len(r['short_repairs']) for r in out),
        'maxima':{k:max(r['counts'][k] for r in out) for k in out[0]['counts']}},sort_keys=True))

if __name__=='__main__':main()

#!/usr/bin/env python3
"""Independent bounded corroboration of the all-field odd-cycle proof."""
import argparse,copy,hashlib,itertools,json,sys
from functools import lru_cache
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE))
from cycle import construct,minimum,validate
from subspace import audit
def need(ok,message):
    if not ok:raise ValueError(message)
def authenticate():
    rows=json.loads((HERE/'SOURCES.json').read_text())['files']
    for row in rows:
        if row['usage']=='input':
            need(hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest()==row['sha256'],
                 'source hash '+row['path'])
    return sum(x['usage']=='input'for x in rows)
def brute_alpha(d):
    n=len(d)
    return max(sum(d[i]for i in range(n)if mask>>i&1)for mask in range(1<<n)
               if all(not(mask>>i&1 and mask>>((i+1)%n)&1)for i in range(n)))
def brute_sharing(d):
    n=len(d)
    @lru_cache(None)
    def extend(i,previous,first):
        if i==n-1:return 0 if previous+first<=d[-1]else -10**9
        return max(x+extend(i+1,x,first)for x in range(min(d[i]-previous,d[i+1])+1))
    return max(x+extend(0,x,x) for x in range(min(d[0],d[-1])+1))
def matrix(recipe):
    d=recipe['dimensions'];n=len(d);offset=[sum(d[:i])for i in range(n)]
    used=[0]*n;groups=[]
    for i,count in enumerate(recipe['edge']):
        j=(i+1)%n
        for _ in range(count):
            groups.append((offset[i]+used[i],offset[j]+used[j]));used[i]+=1;used[j]+=1
    for i,count in enumerate(recipe['private']):
        for _ in range(count):groups.append((offset[i]+used[i],));used[i]+=1
    need(used==d,'independent coordinate partition')
    out=[[0]*sum(d)for _ in range(sum(d))]
    for group in groups:
        for i in group:
            for j in group:out[i][j]=1
    return out

def fits(a,d):
    owner=[i for i,x in enumerate(d)for _ in range(x)];n=len(d);s=sum(d)
    need(len(a)==s and all(len(row)==s for row in a),'full fitting shape')
    for i in range(s):
        for j in range(s):
            x,y=owner[i],owner[j]
            if x==y or (x-y)%n not in(1,n-1):need(a[i][j]==int(i==j),'complete ordered fitting mask')
def rank(a,q):
    a=[[x%q for x in row]for row in a];r=0
    for c in range(len(a)):
        pivot=next((i for i in range(r,len(a))if a[i][c]),None)
        if pivot is None:continue
        a[r],a[pivot]=a[pivot],a[r];scale=pow(a[r][c],-1,q)
        a[r]=[v*scale%q for v in a[r]]
        for i in range(r+1,len(a)):
            factor=a[i][c]
            if factor:a[i]=[(x-factor*y)%q for x,y in zip(a[i],a[r])]
        r+=1
    return r

def binary_rank(rows):
    pivots={}
    for row in rows:
        while row:
            bit=row.bit_length()-1
            if bit not in pivots:pivots[bit]=row;break
            row^=pivots[bit]
    return len(pivots)
def run():
    inputs=authenticate();cases=0;field_checks=0;digest=hashlib.sha256()
    fixtures=[]
    for n,limit in [(5,3),(7,2),(9,1)]:
        for d in itertools.product(range(limit+1),repeat=n):
            recipe=construct(d);alpha=brute_alpha(d);sharing=brute_sharing(d)
            need(recipe['alpha']==alpha and recipe['rank']==sum(d)-sharing,
                 'independent subset/edge enumeration')
            need(recipe['rank']==max(alpha,(sum(d)+1)//2),'exact capacity formula')
            a=matrix(recipe);fits(a,d)
            for q in (2,3,101):need(rank(a,q)==recipe['rank'],'attaining field rank');field_checks+=1
            digest.update(json.dumps(recipe,sort_keys=True,separators=(',',':')).encode());cases+=1
    completions=[]
    for n in(5,7):
        best=n;hist={}
        for bits in range(1<<(2*n)):
            rows=[(1<<i)|(((bits>>(2*i))&1)<<((i-1)%n))|
                  (((bits>>(2*i+1))&1)<<((i+1)%n))for i in range(n)]
            r=binary_rank(rows);need(r>=(n+1)//2,'all directed binary fitting completions')
            best=min(best,r);hist[r]=hist.get(r,0)+1
        need(best==(n+1)//2,'scalar sharp rank')
        completions.append(dict(length=n,matrices=1<<(2*n),minimum=best,histogram=hist))
    for d in [(2,1,2,1,2,1,1),(2,2,2,2,2,2,2),(1,1,1,1,1,1,1),
              (100,1,1,1,1,1,1),(0,2,0,3,1,0,4,0,1)]:
        fixtures.append(construct(d))
    huge=[(1<<4096)+i for i in range(11)];large=construct(huge)
    need(large['path_evaluations']<=2*4097+1,'logarithmic compressed search')
    span_digest=hashlib.sha256();span_cases=0
    for n in(5,7,9):
        for q in(2,3,101):
            for seed in range(32):
                d=[(seed+2*i+i*i)%3 for i in range(n)]
                owner=[i for i,width in enumerate(d)for _ in range(width)]
                a=[[int(i==j)if x==y else ((seed+17*i+31*j)%q if (x-y)%n in(1,n-1)else 0)
                    for j,y in enumerate(owner)]for i,x in enumerate(owner)]
                fits(a,d);witness=audit(a,d,q)
                need(witness['rank']==rank(a,q),'independent column/row elimination')
                span_digest.update(json.dumps(witness,sort_keys=True).encode());span_cases+=1
    sharp=construct([2]*7);sharp_matrix=matrix(sharp);sharp_span=audit(sharp_matrix,[2]*7,101)
    need(sharp_span['rank']==7 and sharp_span['intersections']==[1]*7 and
         sharp_span['cuts']==[7]*7,'every subspace bound is attained')
    # Actual allowed 2x2 blocks can fail to commute even in a sharp attainer.
    x=[[sharp_matrix[i][2+j]for j in range(2)]for i in range(2)]
    y=[[sharp_matrix[2+i][4+j]for j in range(2)]for i in range(2)]
    product=lambda a,b:[[sum(a[i][h]*b[h][j]for h in range(2))for j in range(2)]for i in range(2)]
    need(product(x,y)!=product(y,x),'noncommuting permitted block fixture')
    controls=[]
    for bad in [[],[1]*3,[1]*6,[True]*5,[1,-1,1,1,1],[1.0]*5]:
        try:construct(bad)
        except ValueError:controls.append('invalid dimensions rejected')
        else:raise ValueError('invalid dimensions accepted')
    good=construct([2]*7)
    for name,mutate in [('omitted shared channel',lambda r:r['edge'].__setitem__(0,r['edge'][0]+1)),
        ('unpaid rank',lambda r:r.__setitem__('rank',r['rank']-1)),
        ('bool channel',lambda r:r['private'].__setitem__(0,False)),
        ('false independent witness',lambda r:r.__setitem__('independent',[0,1]))]:
        bad=copy.deepcopy(good);mutate(bad)
        try:validate(bad)
        except ValueError:controls.append(name)
        else:raise ValueError('mutant accepted '+name)
    a=matrix(good);a[0][4]=1
    try:fits(a,good['dimensions'])
    except ValueError:controls.append('forbidden directed block')
    else:raise ValueError('forbidden directed block accepted')
    return dict(status='PASS_ODD_CYCLE_QUERY_CAPACITY',live_inputs=inputs,width_cases=cases,
        field_rank_checks=field_checks,recipe_sha256=digest.hexdigest(),binary_completions=completions,
        fixtures=fixtures,subspace=dict(cases=span_cases,sha256=span_digest.hexdigest(),sharp=sharp_span,noncommuting_blocks=[x,y]),large=dict(length=11,width_bits=4097,rank_bits=large['rank'].bit_length(),
            path_evaluations=large['path_evaluations']),controls=controls,
        scope='All-field proof with finite corroboration; query dimension only, no physical supplier or kappa.')
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--write',action='store_true');a=parser.parse_args();result=run()
    if a.write:(HERE/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    else:need(json.dumps(json.loads((HERE/'RESULT.json').read_text()),sort_keys=True)==json.dumps(result,sort_keys=True),'typed deterministic receipt')
    print(result['status'])
if __name__=='__main__':main()

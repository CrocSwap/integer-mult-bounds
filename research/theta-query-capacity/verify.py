#!/usr/bin/env python3
"""Independent finite corroboration, not the all-width proof. JoyboyBrian."""
import argparse,functools,hashlib,itertools,json,random,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import theta

def need(ok,msg):
    if not ok:raise ValueError(msg)
def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=True)
def rejected(fn,msg):
    try:fn()
    except (ValueError,KeyError,TypeError):return
    raise RuntimeError('negative control accepted: '+msg)
def rank(a,q):
    if not a:return 0
    a=[[v%q for v in row]for row in a];r=0
    for c in range(len(a[0])):
        p=next((i for i in range(r,len(a))if a[i][c]),None)
        if p is None:continue
        a[r],a[p]=a[p],a[r];z=pow(a[r][c],-1,q);a[r]=[v*z%q for v in a[r]]
        for i in range(r+1,len(a)):
            z=a[i][c]
            if z:a[i]=[(x-z*y)%q for x,y in zip(a[i],a[r])]
        r+=1
        if r==len(a):break
    return r
# Independent graph literal, not imported from the constructor.
EDGE={(0,2),(1,2),(0,3),(3,4),(1,4),(0,5),(5,6),(1,6)}
def adjacent(i,j):return tuple(sorted((i,j)))in EDGE

def fit(M,d):
    owners=[i for i,n in enumerate(d)for _ in range(n)];S=len(owners)
    need(len(M)==S and all(len(row)==S for row in M),'matrix size')
    for i,x in enumerate(owners):
        for j,y in enumerate(owners):
            if x==y:need(M[i][j]==int(i==j),'identity block')
            elif not adjacent(x,y):need(M[i][j]==0,'ordered nonedge')
    return owners

def graph(d):
    own=[i for i,n in enumerate(d)for _ in range(n)]
    return [sum(1<<j for j,y in enumerate(own)if adjacent(x,y))for x in own]

def matching_oracle(d):
    adj=graph(d)
    @functools.lru_cache(None)
    def f(mask):
        if not mask:return 0
        bit=mask&-mask;i=bit.bit_length()-1;rest=mask^bit;ans=f(rest);js=adj[i]&rest
        while js:
            b=js&-js;js^=b;ans=max(ans,1+f(rest^b))
        return ans
    return f((1<<len(adj))-1)

def components(adj,mask):
    out=[]
    while mask:
        todo=mask&-mask;seen=0
        while todo:
            b=todo&-todo;todo^=b
            if seen&b:continue
            seen|=b;todo|=adj[b.bit_length()-1]&mask&~seen
        out.append(seen);mask&=~seen
    return out

def barrier(d):
    adj=graph(d);S=len(adj);full=(1<<S)-1;best=(-1,None)
    # Direct Tutte--Berge dual enumeration; independent of matching DP.
    for keep in range(1<<S):
        cc=components(adj,keep);lower=sum((c.bit_count()+1)//2 for c in cc)
        if lower>best[0]:best=(lower,keep)
    return best

def half_audit(M,d,q):
    fit(M,d);S=sum(d);off=[sum(d[:i])for i in range(7)]
    def dim(ids):return rank([[row[c]for i in ids for c in range(off[i],off[i]+d[i])]for row in M],q)
    r=rank(M,q);tu=d[2]+d[0]-dim([2,0]);tv=d[2]+d[1]-dim([2,1])
    need(tu+tv<=d[2],'disjoint shared-path intersections')
    need(r>=d[0]+d[4]+d[6]+d[2]-tu,'left induced edge and isolates')
    need(r>=d[1]+d[3]+d[5]+d[2]-tv,'right induced edge and isolates')
    need(2*r>=S,'half-total bound')
    return r

def local_mix(M,d,q,rng):
    # Full D M D^-1 via elementary within-group row and inverse-column steps.
    M=[row.copy()for row in M];off=[sum(d[:i])for i in range(7)]
    for i,n in enumerate(d):
        if n<2:continue
        for _ in range(4):
            a,b=rng.sample(list(range(off[i],off[i]+n)),2);z=rng.randrange(1,q)
            M[a]=[(x+z*y)%q for x,y in zip(M[a],M[b])]
            for row in M:row[b]=(row[b]-z*row[a])%q
    return M

def source_check():
    manifest=json.loads((HERE/'SOURCES.json').read_text());root=HERE.parents[1]
    rows=[x for x in manifest['files']if x['usage']=='input']
    need(bool(rows),'required source rows')
    for x in rows:
        need(hashlib.sha256((root/x['path']).read_bytes()).hexdigest()==x['sha256'],'source digest '+x['path'])
    return {x['path']:x['sha256']for x in rows}

def run():
    sources=source_check();rng=random.Random(131306)
    domain=set(itertools.product(range(2),repeat=7))
    domain.update([(2,)*7,(2,1,2,1,2,1,1),(0,3,2,1,0,2,1)])
    while len(domain)<180:
        d=tuple(rng.randrange(4)for _ in range(7))
        if sum(d)<=13:domain.add(d)
    receipts=[];mixed=0;partial=0
    for d in sorted(domain):
        rec=theta.construct(d);M=theta.matrix(rec);fit(M,d)
        target=sum(d)-matching_oracle(d)
        need(rec['rank']==target,'independent copy matching')
        for q in (2,3,101):
            need(rank(M,q)==target,'whole attaining rank')
            N=local_mix(M,d,q,rng);need(half_audit(N,d,q)==target,'mixed whole endpoint');mixed+=1
            keep=[i for i in range(sum(d))if rng.randrange(2)]
            own=[i for i,n in enumerate(d)for _ in range(n)]
            dd=tuple(sum(own[j]==i for j in keep)for i in range(7))
            P=[[N[i][j]for j in keep]for i in keep]
            half_audit(P,dd,q);partial+=1
        receipts.append(rec)
    arbitrary=0
    for q in (2,3,101):
        for trial in range(15):
            d=tuple(rng.randrange(1,4)for _ in range(7));own=[i for i,n in enumerate(d)for _ in range(n)]
            N=[[int(i==j) if x==y else rng.randrange(q) if adjacent(x,y) else 0
                for j,y in enumerate(own)]for i,x in enumerate(own)]
            r=half_audit(N,d,q)
            need(r>=sum(d)-matching_oracle(d),'arbitrary directed rectangular blocks')
            arbitrary+=1
    dual=[]
    for d in [(1,)*7,(2,)*7,(2,1,2,1,2,1,1),(0,3,2,1,0,2,1)]:
        bound,keep=barrier(d);expected=sum(d)-matching_oracle(d)
        need(bound==expected,'complete matching deficiency dual');dual.append({'widths':list(d),'rank':bound,'keep':keep})
    # Every binary scalar directed completion: sixteen independent edge entries.
    ordered=[(i,j)for i in range(7)for j in range(7)if adjacent(i,j)]
    minrank=7;counts=[0]*8
    for word in range(1<<len(ordered)):
        rows=[1<<i for i in range(7)]
        for k,(i,j)in enumerate(ordered):
            if word>>k&1:rows[i]|=1<<j
        basis={}
        for row in rows:
            while row:
                p=row.bit_length()-1
                if p in basis:row^=basis[p]
                else:basis[p]=row;break
        r=len(basis);counts[r]+=1;minrank=min(minrank,r)
    need(minrank==4 and sum(counts)==65536,'complete scalar completion boundary')
    controls=0
    for d in [(1,)*6,(True,0,0,0,0,0,0),(-1,0,0,0,0,0,0),(1.0,0,0,0,0,0,0)]:
        rejected(lambda d=d:theta.construct(d),'width');controls+=1
    rec=theta.construct((2,)*7)
    for field,index,delta in [('edges',0,1),('private',0,1)]:
        bad=json.loads(json.dumps(rec));bad[field][index]+=delta
        rejected(lambda bad=bad:theta.validate(bad),'coverage');controls+=1
    bad=json.loads(json.dumps(rec));bad['rank']-=1;rejected(lambda:theta.validate(bad),'invoice');controls+=1
    bad=json.loads(json.dumps(rec));bad['edges'][0]=True;rejected(lambda:theta.validate(bad),'typed count');controls+=1
    M=theta.matrix(theta.construct((1,)*7));M[0][0]=0;rejected(lambda:fit(M,(1,)*7),'identity');controls+=1
    M=theta.matrix(theta.construct((1,)*7));M[0][1]=1;rejected(lambda:fit(M,(1,)*7),'forbidden ordered block');controls+=1
    files=['theta.py','verify.py','PROOF.md','README.md','TASK.json']
    return {'schema_version':1,'width_vectors':len(domain),'fields':[2,3,101],'mixed_full_operators':mixed,
      'partial_coordinate_operators':partial,'arbitrary_block_operators':arbitrary,'scalar_completions':65536,'scalar_rank_histogram':counts,
      'dual_fixtures':dual,'rejecting_controls':controls,'recipe_sha256':hashlib.sha256(canonical(receipts).encode()).hexdigest(),
      'sources':sources,'package_sha256':{f:hashlib.sha256((HERE/f).read_bytes()).hexdigest()for f in files}}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--write-result',action='store_true');args=parser.parse_args()
    result=run();path=HERE/'RESULT.json'
    if args.write_result:path.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    else:need(canonical(result)==canonical(json.loads(path.read_text())),'complete typed receipt')
    print('PASS_THETA_QUERY_CAPACITY '+canonical(result))
if __name__=='__main__':main()

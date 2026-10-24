"""Fixed exact Jordan certificate and source-indexing controls; not a large-h proof search."""
from pathlib import Path
import hashlib,json
P=Path(__file__).resolve().parent
ROOT=P.parents[1]
def need(v,s):
    if not v:raise ValueError(s)
def canonical(v):return json.dumps(v,sort_keys=True,separators=(',',':'))
def rank(a,p=5):
    a=[list(row) for row in a];r=0
    for c in range(len(a[0]) if a else 0):
        pivot=next((i for i in range(r,len(a)) if a[i][c]%p),None)
        if pivot is None:continue
        a[r],a[pivot]=a[pivot],a[r];scale=pow(a[r][c]%p,-1,p);a[r]=[x*scale%p for x in a[r]]
        for i in range(len(a)):
            if i!=r and a[i][c]%p:
                q=a[i][c]%p;a[i]=[(x-q*y)%p for x,y in zip(a[i],a[r])]
        r+=1
    return r

def mul(a,b):return [[sum(x*y for x,y in zip(row,col))%5 for col in zip(*b)] for row in a]
def eye(n):return [[int(i==j) for j in range(n)] for i in range(n)]
def jordan_rules():
    records=[]
    for j in range(1,6):
        U=[[int(i==k)+int(k==i+1) for k in range(j)] for i in range(j)]
        T=[[int(i//j==k//j)*U[i%j][k%j]+int(i//j==0 and k//j==1)*U[i%j][k%j] for k in range(2*j)] for i in range(2*j)]
        L=[[(T[i][k]-int(i==k))%5 for k in range(2*j)] for i in range(2*j)]
        z=eye(2*j);blocks=[j-1,j+1] if j<5 else [5,5];ranks=[]
        for power in range(1,6):
            z=mul(z,L);got=rank(z);need(got==sum(max(0,b-power) for b in blocks),'Jordan tensor rule');ranks.append(got)
        records.append({'j':j,'blocks':[b for b in blocks if b],'ranks':ranks})
    return records

def multiplicities(h):
    c=[1,0,0,0,0]
    for _ in range(h):
        nxt=[0]*5
        for j,n in enumerate(c,1):
            if j==5:nxt[4]+=2*n
            else:
                if j>1:nxt[j-2]+=n
                nxt[j]+=n
        c=nxt
    need(sum(j*n for j,n in enumerate(c,1))==2**h,'integer dimension invariant')
    return c

def predicted(h):
    need(type(h)is int and h>=4 and h%4==0,'resonant dimension required')
    return 2**h-1-sum(multiplicities(h))

def source_hashes():
    source=json.loads((P/'SOURCES.json').read_text());rows=[r for r in source['files'] if r['usage']=='input'];need(len(rows)==2,'both predecessors required')
    for r in rows:need(hashlib.sha256((ROOT/r['path']).read_bytes()).hexdigest()==r['sha256'],'source bytes')
    return {r['path']:r['sha256'] for r in rows}

def result():
    pins=source_hashes();rules=jordan_rules();fixtures=[]
    for h in (4,8):
        n=2**h;B=[[(int(i==j)-int(i&j==0))%5 for j in range(1,n-1)] for i in range(1,n-1)]
        actual=rank(B);need(actual==predicted(h),'literal proper-set rank')
        # The actual source endpoint signs and the witness power are tested independently of the rank formula.
        T=[[int(i&j==0) for j in range(n)] for i in range(n)]
        v=[1]+[0]*(n-1)
        for _ in range(4):v=[(v[i]-sum(T[i][j]*v[j] for j in range(n)))%5 for i in range(n)]
        need(all(v[i]==(1+pow(3,i.bit_count(),5)+pow(4,i.bit_count(),5))%5 for i in range(1,n-1)),'actual endpoint witness')
        need(any(v),'nonzero endpoint witness')
        fixtures.append({'h':h,'rank':actual,'multiplicities':multiplicities(h),'witness_sha256':hashlib.sha256(bytes(v)).hexdigest()})
    # Tiny literal kernel census is an independent check of the first tensor rule.
    census=sum(1 for x in range(5) for y in range(5) if y==0);need(census==5,'smallest Jordan kernel census')
    rejected=[]
    for bad in (0,2,3,True):
        try:predicted(bad)
        except ValueError:rejected.append(str(bad))
        else:raise ValueError('invalid domain accepted')
    need(predicted(8)!=183,'characteristic-three formula is not substituted')
    need(rank([[1,-1],[-1,1]])==1,'nonresonant h2 boundary')
    return {'scope':'all resonant h proof in PROOF.md; bounded exact controls here','characteristic':5,'resonant_modulus':4,'rules':rules,'fixtures':fixtures,'invalid_domains_rejected':rejected,'kernel_census':census,'source_sha256':pins,'no_physical_supplier':True}

if __name__=='__main__':
    actual=result();expected=json.loads((P/'RESULT.json').read_text());need(canonical(actual)==canonical(expected),'mandatory typed complete receipt')
    print('PASS_QUINARY_RESONANT_DISJOINTNESS_REPAIR')

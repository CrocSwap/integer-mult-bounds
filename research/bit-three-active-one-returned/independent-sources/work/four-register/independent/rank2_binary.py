"""Write all retained rank-two orders before the finite quotient filter."""
import hashlib,json,struct
from pathlib import Path

root=Path(__file__).parent
families=json.loads((root.parent/'dirty_rank2.json').read_text())['families']

def outer(x,y):
    return sum(y<<(4*i) for i in range(4) if x>>i&1)

def commute(a,b):
    x,y=a;u,v=b
    return (outer(x,v) if (y&u).bit_count()%2 else 0)==(outer(u,y) if (v&x).bit_count()%2 else 0)

def normalized(w,c):
    result=[];left=list(range(len(w)))
    while left:
        choices=[i for i in left if all(c[w[j]][w[i]] for j in left if j<i)]
        i=min(choices,key=lambda i:(w[i],i))
        result.append(w[i]);left.remove(i)
    return tuple(result)

def orders(counts,c,w=()):
    if not any(counts):
        if w<=normalized(w[::-1],c):yield w
        return
    for j,k in enumerate(counts):
        if not k:continue
        blocked=False
        for old in reversed(w):
            if not c[old][j]:break
            if old>j:blocked=True;break
        if blocked:continue
        counts[j]-=1
        yield from orders(counts,c,w+(j,))
        counts[j]+=1

counts=[]
p=root/'rank2-words.bin'
with p.open('wb') as f:
    for family in families:
        ns=family['projectors'];c=[[commute(a,b) for b in ns] for a in ns]
        anc=sum(1<<i for i in family['ancillas']);n=0
        for w in orders(list(family['counts']),c):
            f.write(struct.pack('<9H',*(outer(*ns[j]) for j in w),anc));n+=1
        counts.append(n)
result={'families':len(families),'words':sum(counts),'family_counts':counts,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
(root/'rank2-binary-summary.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))

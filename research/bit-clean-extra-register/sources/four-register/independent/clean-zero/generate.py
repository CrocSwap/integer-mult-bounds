"""List every zero-active-off-pattern clean word with eight paid calls."""
from itertools import combinations_with_replacement, product
from pathlib import Path
import hashlib,json,math,struct,time

ROOT=Path(__file__).parent

def outer(x,y):
    return sum(y<<(4*i) for i in range(4) if x>>i&1)

families=[[(1<<i,1<<i),(1<<i,(1<<i)|8),((1<<i)|8,1<<i)] for i in range(3)]
projectors=sum(families,[])+[(15,8),(8,15)]
commute=[[a==b or (not ((a[0]&b[1]).bit_count()%2) and not ((b[0]&a[1]).bit_count()%2)) for b in projectors] for a in projectors]
matrices=[outer(*xy) for xy in projectors]

def orders(counts,word=()):
    if not any(counts):
        yield word
        return
    for j,count in enumerate(counts):
        if not count:continue
        blocked=False
        for old in reversed(word):
            if not commute[old][j]:break
            if old>j:blocked=True;break
        if blocked:continue
        counts[j]-=1
        yield from orders(counts,word+(j,))
        counts[j]+=1

start=time.time();records=[];offset=0;path=ROOT/'words.bin'
with path.open('wb') as out:
    for pieces in product(list(combinations_with_replacement(range(3),2)),repeat=3):
        counts=[0]*11
        for i,piece in enumerate(pieces):
            for j in piece:counts[3*i+j]+=1
        counts[9]=counts[10]=1
        raw=math.factorial(8)//math.prod(math.factorial(c) for c in counts)
        count=0
        for word in orders(counts):
            out.write(struct.pack('<8H',*(matrices[j] for j in word)))
            count+=1
        records.append({'family':len(records),'counts':counts[:],'raw_orders':raw,'offset':offset,'orders':count})
        offset+=count
result={'families':len(records),'projectors':projectors,'matrices':matrices,'raw_orders':sum(r['raw_orders'] for r in records),'commutation_orders':offset,'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'seconds':time.time()-start,'records':records}
(ROOT/'catalogue.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='records'}))

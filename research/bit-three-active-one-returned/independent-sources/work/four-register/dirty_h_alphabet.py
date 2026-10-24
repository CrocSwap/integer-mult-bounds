"""Check every eight-call word in the coordinate and complement bases."""
import dirty_ancilla as core
from itertools import combinations, combinations_with_replacement, permutations
from pathlib import Path
import json,time,math
P=[1,2,4,8,14,13,11,7]
PERMS=list(permutations(range(4)))

def subspaces():
    out=set()
    for n in (1,2,3):
        for bs in combinations(range(1,16),n):
            vs={0}
            for b in bs:vs|={v^b for v in tuple(vs)}
            if len(vs)==1<<n:out.add(tuple(sorted(vs)))
    return list(out)
SUBSPACES=subspaces()

def irreducible(counts):
    xs=[P[i] for i,c in enumerate(counts) if c]
    for vs in SUBSPACES:
        if all(x in vs or not any((x&v).bit_count()%2 for v in vs) for x in xs):return False
    return True

def transform_counts(c,p):
    return tuple(c[p.index(i)] for i in range(4))+tuple(c[4+p.index(i)] for i in range(4))

def commute(a,b):
    return (a<4)==(b<4) or a%4==b%4

def normal(word):
    n=len(word);todo=(1<<n)-1;out=[]
    pred=[sum(1<<j for j in range(i) if not commute(word[i],word[j])) for i in range(n)]
    while todo:
        i=min((j for j in range(n) if todo>>j&1 and not pred[j]&todo),key=lambda j:(word[j],j))
        out.append(word[i]);todo^=1<<i
    return tuple(out)

def canonical(word,stabilizer):
    choices=[]
    for p in stabilizer:
        w=tuple((j//4)*4+p[j%4] for j in word)
        choices.extend((normal(w),normal(w[::-1])))
    return min(choices)

def words(counts,prefix=()):
    if not any(counts):yield prefix;return
    for j,c in enumerate(counts):
        if c:
            cc=list(counts);cc[j]-=1
            yield from words(tuple(cc),prefix+(j,))

def binary_reduce(v,basis):
    for b in basis:
        if v.bit_length()==b.bit_length():v^=b
        elif v.bit_length()>b.bit_length():
            if v>>(b.bit_length()-1)&1:v^=b
    return v

def parity_possible(word):
    fo=[sum(((core.outer(x,y)>>bit)&1)<<j for j,(x,y) in enumerate(word)) for bit in range(16) if core.OFF>>bit&1]
    bs={}
    for v in fo:
        while v:
            k=v.bit_length()-1
            if k in bs:v^=bs[k]
            else:bs[k]=v;break
    if len(bs)<3:return True
    if len(bs)>3:return False
    basis=[bs[k] for k in sorted(bs,reverse=True)]
    grouped={}
    for s,c in core.polynomial(word):
        key=binary_reduce(s,basis);grouped[key]=grouped.get(key,0)^c
    return not any(c&core.OFF for c in grouped.values())

if __name__=='__main__':
    started=time.time();families=[];out=[];totals={'raw_distance_classes':0,'irreducible_classes':0,'raw_orders':0,'canonical_orders':0,'parity_rejected':0,'searched_orders':0,'nodes':0,'terminals':0,'candidates':0}
    for v in combinations_with_replacement(range(8),8):
        c=tuple(v.count(i) for i in range(8))
        if c!=min(transform_counts(c,p) for p in PERMS):continue
        if not core.valid_distance([(P[j],P[j]) for j in v]):continue
        totals['raw_distance_classes']+=1
        if not irreducible(c):continue
        families.append(c)
    totals['irreducible_classes']=len(families)
    print(json.dumps({'families':families}),flush=True)
    for fi,c in enumerate(families):
        stabilizer=[p for p in PERMS if transform_counts(c,p)==c]
        seen=set();fstats={'counts':c,'raw':0,'canonical':0,'parity_rejected':0,'searched':0,'nodes':0,'terminals':0,'candidates':[]}
        for raw in words(c):
            fstats['raw']+=1
            if normal(raw)!=raw:continue
            w=canonical(raw,stabilizer)
            if w in seen:continue
            seen.add(w);fstats['canonical']+=1
            word=[(P[j],P[j]) for j in w]
            if not parity_possible(word):fstats['parity_rejected']+=1;continue
            result=core.solve(word);fstats['searched']+=1
            fstats['nodes']+=result['stats']['nodes'];fstats['terminals']+=result['stats']['terminals']
            if result['candidate']:fstats['candidates'].append(result)
            core.rref.cache_clear();core.rep.cache_clear();core.add.cache_clear()
        out.append(fstats)
        for a,b in [('raw_orders','raw'),('canonical_orders','canonical'),('parity_rejected','parity_rejected'),('searched_orders','searched'),('nodes','nodes'),('terminals','terminals')]:totals[a]+=fstats[b]
        totals['candidates']+=len(fstats['candidates'])
        print(json.dumps({'family':fi,'stats':fstats,'seconds':time.time()-started}),flush=True)
        Path(__file__).with_suffix('.json').write_text(json.dumps({'totals':totals,'families':out,'seconds':time.time()-started},indent=2)+'\n')

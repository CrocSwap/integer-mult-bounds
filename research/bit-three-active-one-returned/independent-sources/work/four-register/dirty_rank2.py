"""Prune all rank-two off-pattern pools for an eight-call dirty word."""
import json,math,time
from pathlib import Path
from itertools import combinations_with_replacement
import dirty_ancilla as core
from dirty_h_alphabet import SUBSPACES

def possible_ancillas(word):
    possible=set(range(4))
    for side in (0,1):
        for r in range(1,16):
            if sum((r&xy[side]).bit_count()%2 for xy in word)<3:
                if r.bit_count()!=1:return set()
                possible&={r.bit_length()-1}
    return possible

def irreducible(word):
    for vs in SUBSPACES:
        if all(x in vs or not any((y&v).bit_count()%2 for v in vs) for x,y in word):return False
    return True

def pattern_rows(word,anc=None):
    mask=core.OFF | (0 if anc is None else 1<<(anc*5))
    return [sum(((core.outer(x,y)>>bit)&1)<<j for j,(x,y) in enumerate(word)) for bit in range(16) if mask>>bit&1]

if __name__=='__main__':
    pools=json.loads(Path('work/four-register/independent/off-pattern-spaces.json').read_text())['levels'][1]['representatives']
    out=[];stats={'pool_classes':len(pools),'multisets':0,'distance':0,'irreducible':0,'augmented':0,'raw_order_bound':0}
    start=time.time()
    for pi,pool in enumerate(pools):
        ns=[tuple(v) for v in pool['projectors']]
        for choice in combinations_with_replacement(range(len(ns)),8):
            stats['multisets']+=1;word=[ns[j] for j in choice]
            if core.gf2_rank(pattern_rows(word))!=2:continue
            aa=possible_ancillas(word)
            if not aa:continue
            stats['distance']+=1
            if not irreducible(word):continue
            stats['irreducible']+=1
            aa=[a for a in aa if core.gf2_rank(pattern_rows(word,a))<=3]
            if not aa:continue
            stats['augmented']+=1
            counts=[choice.count(i) for i in range(len(ns))]
            orders=math.factorial(8)//math.prod(math.factorial(c) for c in counts)
            stats['raw_order_bound']+=orders
            out.append({'pool':pi,'projectors':ns,'counts':counts,'ancillas':aa,'raw_orders':orders})
    result={'stats':stats,'families':out,'seconds':time.time()-start}
    Path(__file__).with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'stats':stats,'seconds':result['seconds']}),flush=True)

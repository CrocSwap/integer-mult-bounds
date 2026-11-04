#!/usr/bin/env python3
"""All formal rank2 incidence patterns: optimistic bound for any stage ranks.

For a commuting stage projector of rank greater than two, delete one active
output placement for each charged whole idle. Concavity shows this can only
increase productive-minus-paid price. The resulting rank2 pattern need not
be realizable, making this a valid upper bound for every actual root.
"""
from pathlib import Path
from itertools import permutations
import json,argparse
H=Path(__file__).resolve().parent

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--prefix',default='PATTERN');args=ap.parse_args()
    patterns=[]
    def go(seq,last,left):
        if len(seq)==6:
            if left==[0,0,0,0]:
                m=[0]*16
                for v in seq:m[v]+=1
                patterns.append(m)
            return
        for m in range(last,16):
            nxt=[left[i]-((m>>i)&1)for i in range(4)]
            if min(nxt)<0 or max(nxt)>5-len(seq):continue
            go(seq+[m],m,nxt)
    go([],0,[2,2,2,2]);orbits={}
    for m in patterns:
        keys=[]
        for pp in permutations(range(4)):
            z=[0]*16
            for v,n in enumerate(m):z[sum(((v>>i)&1)<<pp[i]for i in range(4))]=n
            keys.append(tuple(z))
        orbits.setdefault(min(keys),m)
    pats=list(orbits.values())
    out=dict(status='EXHAUSTIVE_FORMAL_RANK2_OUTPUT_RELAXATION',patterns=pats,complete_pattern_count=len(patterns),economic_orbits=len(pats),proof='For x>=1,r>0, H(x+r)-H(r)<=H(x). Deleting each charged extra stage placement therefore raises the margin. Every remaining stage appears on exactly two of six output coordinates. All such multisets are enumerated and child sizes range over every stage permutation.',scope='Six output fields, seven query sites, four full binary children, fixed native source, all commuting projector ranks, charged extra whole idles. No helper consumption, altered binary child constructor, or different number of root fields.')
    (H/'FORMAL-RANK2-PATTERNS.json').write_text(json.dumps(out,indent=2)+'\n')
    lines=(H/(args.prefix+'-BOUND-TABLES.txt')).read_text().splitlines();N,np,G,L=map(int,lines[0].split())
    lines=[f'{N} {len(pats)} {G} {L}']+lines[1:N+2]+[' '.join(map(str,m))for m in pats]
    name='FORMAL-RANK2'if args.prefix=='PATTERN'else 'FORMAL-'+args.prefix
    (H/(name+'-BOUND-TABLES.txt')).write_text('\n'.join(lines)+'\n');print(len(patterns),len(pats),name)

if __name__=='__main__':main()

#!/usr/bin/env python3
"""Independent slow DRUP replay and faithful regular-representation controls.
Imports no constructor, CNF or watched-proof checker.
Cinna Davis with substantial OpenAI Codex assistance. Apache-2.0.
"""
import gzip,itertools,json,time
from pathlib import Path
ROOT=Path(__file__).resolve().parent

def require(ok,message):
    if not ok:raise RuntimeError(message)

def conflict(database,negated):
    assigned={}
    for literal in negated:
        variable=abs(literal);value=literal>0
        if variable in assigned and assigned[variable]!=value:return True
        assigned[variable]=value
    while True:
        change=False
        for row in database:
            available=[];satisfied=False
            for literal in row:
                variable=abs(literal)
                if variable not in assigned:available.append(literal)
                elif assigned[variable]==(literal>0):satisfied=True;break
            if satisfied:continue
            if not available:return True
            if len(available)==1:
                literal=available[0];variable=abs(literal);value=literal>0
                if variable in assigned and assigned[variable]!=value:return True
                if variable not in assigned:assigned[variable]=value;change=True
        if not change:return False

def replay(record):
    database=[tuple(row) for row in record['clauses']];steps=0;finished=False
    for line in record['proof']:
        pieces=line.split()
        if pieces[0]=='d':continue
        row=tuple(map(int,pieces));require(row[-1]==0 and 0 not in row[:-1],'bad proof syntax')
        row=row[:-1];require(all(abs(x)<=record['variables'] for x in row),'bad proof variable')
        require(conflict(database,[-x for x in row]),'independent non-RUP addition')
        database.append(row);steps+=1
        if not row:finished=True
    require(finished,'independent proof has no empty clause')
    return steps

def regular_controls():
    permutations=list(itertools.permutations(range(3)));index={g:i for i,g in enumerate(permutations)}
    def product(a,b):return tuple(a[b[i]] for i in range(3))
    ident=(0,1,2);a=(0,2,1);b=(2,1,0);swap=product(product(b,a),b)
    # Faithfulness: a group-algebra coefficient is visible on the identity basis vector.
    require(len({index[product(g,ident)] for g in permutations})==6,'regular representation is not faithful')
    columns=0
    for active in (1,2,3):
        word=[(role,label) for role in range(active) for label in (b,a,b)]
        for original in range(24):
            data=[0]*4;data[original//6]=1<<(original%6)
            initial=data[:]
            for role,label in word:
                moved=0
                for h in range(6):
                    if data[role]>>h&1:moved^=1<<index[product(label,permutations[h])]
                data[role]=moved
            expected=initial[:]
            for role in range(active):
                moved=0
                for h in range(6):
                    if initial[role]>>h&1:moved^=1<<index[product(swap,permutations[h])]
                expected[role]=moved
            require(data==expected,'full dirty regular-column witness failed');columns+=1
    # All six natural 2x2 address matrices sum to zero, but their regular sum is nonzero.
    coordinates=[g for g in range(16) if ((g&1)*((g>>3)&1)^((g>>1)&1)*((g>>2)&1))==1]
    natural=0
    for g in coordinates:natural^=g
    require(natural==0 and sum(1<<index[g] for g in permutations)==63,'natural-only endpoint control failed')
    require(not conflict([[1,2]],[-1]),'independent propagation rejects a satisfiable fixture')
    return columns

def main():
    started=time.monotonic();d=json.loads(gzip.decompress((ROOT/'CERTIFICATES.json.gz').read_bytes()))
    require([x['index'] for x in d['results']]==list(range(35)),'independent coverage mismatch')
    steps=0
    for record in d['results']:steps+=replay(record)
    columns=regular_controls()
    print(json.dumps({'status':'PASS_INDEPENDENT_THREE_SWAP_COMPRESSION','patterns':35,'slow_rup_additions':steps,'regular_dirty_columns':columns,'natural_only_endpoint_control':'rejected','elapsed_seconds':round(time.monotonic()-started,6)},sort_keys=True))
if __name__=='__main__':main()

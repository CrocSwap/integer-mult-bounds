#!/usr/bin/env python3
"""Different arithmetic checks: exhaustive characters and a 2D matrix oracle.

Written in this session by William Lawyer with OpenAI Codex assistance.
This is code separation, not independent human/agent review. Apache-2.0.
"""
from fractions import Fraction as Q
import gzip
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def demand(ok, why):
    if not ok:
        raise ValueError(why)


def main():
    sources = json.loads((HERE/'SOURCES.json').read_text(encoding='utf-8'))
    item = next(r for r in sources['files'] if r['path']=='research/joint-query/certificate.json.gz')
    raw = (ROOT/item['path']).read_bytes()
    demand(hashlib.sha256(raw).hexdigest()==item['sha256'],'source bytes')
    p = json.loads(gzip.decompress(raw))
    U,T = p['U_ports'],p['T_ports']
    maps = json.loads((HERE/'MAPS.json').read_text(encoding='utf-8'))
    # Direct character weights, without the primary phase-polynomial routine.
    # Every active 17-bit character is covered, with all other bits spectators.
    characters = 0
    for port in U+T:
        row = maps[str(port)]
        g = row['owner_columns'][:17]
        shift = row['translation']
        image = [0]*(1<<17)
        for x in range(1,1<<17):
            bit = x&-x
            image[x] = image[x^bit]^g[bit.bit_length()-1]
        # The actual rho is symmetric (orthogonal and involutive), so this is
        # its transpose action on characters as well as its vector action.
        demand(all(((g[i]>>j)&1)==((g[j]>>i)&1) for i in range(17) for j in range(17)),'symmetric actual route')
        for x,y in enumerate(image):
            demand((y.bit_count()+2*((shift&x).bit_count()%2)-x.bit_count())%4==0,'direct character lift')
            characters += 1
        demand(shift>>17==0,'translation spectators')
    # Test the ordered L2 data word with separately chosen, noncommuting 2x2
    # involutions. These are algebra fixtures, not representations of the full
    # actual cover group. No primary replay functions are imported.
    R = [[Q(row.get(str(i),0)) for i in range(112)] for row in p['R_rows']]
    word = json.loads((HERE/'WORD.json').read_text(encoding='utf-8'))
    fields = [f'X{i}' for i in U]+[f'Y{i}' for i in U]+[f'T{i}' for i in T]
    owned = [f'Z{i}' for i in U]+['C']
    def matrix(port,v):
        a = Q(1+(port%5))
        return (a*v[1],v[0]/a)
    def add(v,w,c):
        return v[0]+c*w[0],v[1]+c*w[1]
    def run(initial):
        state = dict(initial)
        for e in word:
            if e['op']=='clear':
                state[e['field']] = (Q(0),Q(0))
            elif e['op']=='add':
                state[e['dst']] = add(state[e['dst']],state[e['src']],Q(e['coefficient']))
            elif e['op']=='map':
                state[e['field']] = matrix(e['port'],state[e['field']])
        for f in fields:
            demand(state[f]==initial[f],'numeric source restoration')
        demand(state['C']==(0,0),'numeric scratch cleanup')
        for i in U:
            expected = add(initial[f'X{i}'],initial[f'Y{i}'],1)
            for t in T:
                c = -sum(R[k][i]*R[k][t] for k in range(8))/4
                expected = add(expected,matrix(i,matrix(t,initial[f'T{t}'])),c)
            demand(state[f'Z{i}']==expected,'numeric ordered operator')
    zero = {f:(Q(0),Q(0)) for f in fields+owned}
    for f in fields+owned:
        for coordinate in (0,1):
            initial = dict(zero)
            initial[f] = (Q(coordinate==0),Q(coordinate==1))
            run(initial)
    dirty = {f:(Q((i%11)-5),Q((i%7)-3)) for i,f in enumerate(fields+owned)}
    run(dirty)
    demand(matrix(U[0],matrix(U[1],(Q(1),Q(2)))) != matrix(U[1],matrix(U[0],(Q(1),Q(2)))),'noncommutation control')
    print('PASS_QQ16_DIRECT_CHARACTER_AND_MATRIX_ORACLE characters='+str(characters)+
          ' basis_coordinates='+str(2*len(zero))+' dirty_fixture=1')


if __name__=='__main__':
    main()

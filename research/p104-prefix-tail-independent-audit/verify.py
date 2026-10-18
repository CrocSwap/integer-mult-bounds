"""Independent rational trace and compression audit. Ross / OpenAI Codex.
Apache-2.0. No predecessor Python imports. Explicit Fraction rows and
canonical binary elimination replace the integer/8 changed-group collector.
"""
from collections import Counter, defaultdict
from fractions import Fraction as Q
from functools import lru_cache
from itertools import combinations, product
from pathlib import Path
import argparse
import hashlib
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(ok, message):
    if not ok:
        raise ValueError(message)


@lru_cache(None)
def frame(vectors):
    basis = {}
    for value in vectors:
        need(type(value) is int and 0 < value < 512, 'frame label')
        while value:
            bit = value.bit_length()-1
            if bit in basis:
                value ^= basis[bit]
            else:
                basis[bit] = value
                break
        need(value != 0, 'dependent frame')
    for bit in sorted(basis):
        for other in basis:
            if other > bit and (basis[other] >> bit) & 1:
                basis[other] ^= basis[bit]
    return tuple(basis[i] for i in sorted(basis, reverse=True))


def inside(a, b):
    for value in a:
        for pivot in b:
            if value >> (pivot.bit_length()-1) & 1:
                value ^= pivot
        if value:
            return False
    return True


def dot(a,b):
    return sum(x*y for x,y in zip(a,b))


def rank(matrix):
    basis = {}
    for row in matrix:
        row = list(map(Q,row))
        for pivot,old in sorted(basis.items()):
            if row[pivot]:
                scale = row[pivot]/old[pivot]
                row = [x-scale*y for x,y in zip(row,old)]
        pivot = next((i for i,x in enumerate(row) if x),None)
        if pivot is not None:
            basis[pivot] = row
    return len(basis)


def inputs():
    answer = {}
    for pin in json.loads((HERE/'SOURCES.json').read_text())['files']:
        if pin['usage'] == 'input':
            data = (ROOT/pin['path']).read_bytes()
            need(hashlib.sha256(data).hexdigest() == pin['sha256'],'source pin')
            answer[Path(pin['path']).name] = json.loads(data)
    return answer


def roots(fixture):
    result = set()
    for i,j in combinations(range(8),2):
        for sign in [-1,1]:
            row = [0]*8
            row[i],row[j] = 2,2*sign
            result.add(tuple(row))
    result.update((1,*s) for s in product([-1,1],repeat=7) if sum(x<0 for x in s)%2 == 0)
    removed = set(map(tuple,fixture['F0']+fixture['C']))
    need(len(result)==120 and len(removed)==16 and removed<=result,'puncture')
    result = sorted(result-removed)
    need(all(sum(r[i]*r[j] for r in result)==104*(i==j) for i in range(8) for j in range(8)),'RRt')
    return result


def replay(word,ports,certificate,reverse_basis=False):
    names = [f'{s}{i}' for s,n in [('X',104),('Y',104),('Q',8),('G',32),('D',32)] for i in range(n)]
    need(set(word['initial_frames'])==set(word['final_frames'])==set(names),'boundary names')
    need(len(word['program'])==4058,'4058 events')
    def chart(v):
        return frame(tuple(reversed(v)) if reverse_basis else tuple(v))
    frames = {r:chart(word['initial_frames'][r]) for r in names}
    values = {r:{i:Q(1)} for i,r in enumerate(names)}
    ids,frozen,row_ids = {},[],{}
    def intern(r):
        key = tuple(sorted(values[r].items()))
        if key not in ids:
            ids[key] = len(frozen)
            frozen.append(key)
        row_ids[r] = ids[key]
    for r in names:
        intern(r)
    need(all(frames[r]==() for r in names[104:]),'175 nuisance units per target')
    wants = {(t,c,r) for w in certificate['upper_witnesses'] for t,c,r,weight in w['terms']}
    requested = defaultdict(list)
    for t,c,r in wants:
        requested[c].append((t,r))
    captures,projected,seen = {},{},set()
    pools = [set() for _ in range(104)]
    checkpoints,profile,events = {},Counter(),Counter()
    copied = False
    def projection(row_id):
        if row_id not in projected:
            row = dict(frozen[row_id])
            alpha = tuple(sum((value*ports[i][j] for i,value in row.items() if i<104),Q(0))/104 for j in range(8))
            need(all(dot(alpha,r)==row.get(i,0) for i,r in enumerate(ports)),'source row outside code')
            projected[row_id] = alpha
        return projected[row_id]
    def inspect(cut):
        groups = defaultdict(list)
        for r in values:
            groups[frames[r]].append(r)
        # Every cut is visited. Full-row interning avoids repeated arithmetic,
        # without depending on a changed-frame-group notification algorithm.
        for t in range(104):
            target = f'Y{t}'
            for r in groups[frames[target]]:
                if r==target:
                    continue
                pair = t,row_ids[r]
                if pair in seen:
                    continue
                seen.add(pair)
                need(values[r].get(104+t,0)==0,'own target dirt')
                alpha = projection(row_ids[r])
                if any(alpha):
                    pools[t].add(alpha)
        if cut in (2753,2823):
            checkpoints[cut] = [set(p) for p in pools]
        for t,r in requested[cut]:
            need(r in values and r!=f'Y{t}' and frames[r]==frames[f'Y{t}'],'contact frame')
            captures[t,cut,r] = projection(row_ids[r])
    inspect(0)
    for cut,event in enumerate(word['program'],1):
        op,dst = event[:2]
        events[op] += 1
        if op=='transport':
            before,after = chart(event[2]),chart(event[3])
            need(frames[dst]==before,'transport entry')
            need(before!=after and (inside(before,after) or inside(after,before)),'nested frame')
            need(event[4]==abs(len(after)-len(before)),'paid rank')
            frames[dst] = after
            profile[event[4]] += 1
        elif op=='zero':
            need(dst=='C' and dst not in values and len(chart(event[2]))==8,'private allocation')
            values[dst],frames[dst],copied = {},chart(event[2]),False
            intern(dst)
        elif op=='erase':
            need(dst=='C' and copied and frames[dst]==chart(event[2]) and len(frames[dst])==1,'private discard')
            del values[dst],frames[dst],row_ids[dst]
        elif op in ('add','copy'):
            src = event[2]
            need(src!=dst and frames[src]==frames[dst]==chart(event[-1]),'scalar frame')
            if op=='copy':
                need(dst=='C' and not values[dst] and not copied,'private copy')
                values[dst],copied = dict(values[src]),True
            else:
                weight = Q(event[3])
                need(weight!=0,'zero scalar')
                new = dict(values[dst])
                for col,value in values[src].items():
                    new[col] = new.get(col,0)+weight*value
                    if not new[col]:
                        del new[col]
                values[dst] = new
            intern(dst)
        else:
            raise ValueError('unknown event')
        inspect(cut)
    need(set(values)==set(names),'private closure')
    for i,r in enumerate(names):
        expected = {i:Q(1)}
        if r.startswith('Y'):
            t = int(r[1:])
            expected.update({s:Q(dot(ports[t],root),8) for s,root in enumerate(ports) if dot(ports[t],root)})
        need(values[r]==expected,'complete endpoint '+r)
        need(frames[r]==chart(word['final_frames'][r]),'endpoint frame')
    need(dict(profile)=={1:1074,2:58,3:86,4:104,5:48,6:24,7:8,8:8},'profile')
    need(dict(events)=={'add':2624,'transport':1410,'zero':8,'copy':8,'erase':8},'event inventory')
    need(set(captures)==wants,'contact coverage')
    return checkpoints,captures,len(seen)


def lower(pool,ports,v,three):
    pairs = [('p','a'),('p','b'),('q','a')]
    if three:
        pairs += [('p','k'),('q','k'),('w','k')]
    for t,rows in enumerate(pool):
        for alpha in rows:
            need(all(dot(v[l],ports[t])*dot(alpha,v[r])==0 for l,r in pairs),'lower functional')
    need([dot(v['p'],v['a']),dot(v['p'],v['b']),dot(v['q'],v['a'])]==[0,-1,-1],'fixed 2x2 entries')
    if three:
        need([dot(v[x],v['k']) for x in ('p','q','w')]==[0,0,2],'fixed 3x3 entries')
    return sum(map(len,pool))


def upper(w,captures,ports):
    a = [[Q(0)]*8 for _ in ports]
    for t,c,r,weight in w['terms']:
        need(c<=w['cut'],'future contact')
        a[t] = [x+Q(weight)*y for x,y in zip(a[t],captures[t,c,r])]
    n = [[Q(i==j)-sum(ports[t][i]*a[t][j] for t in range(104)) for j in range(8)] for i in range(8)]
    k = [[Q(t==s)-Q(dot(ports[t],ports[s]),8)+12*dot(a[t],ports[s]) for s in range(104)] for t in range(104)]
    small,big = rank(n),rank(k)
    need(big==96+small==w['minimum'],'upper rank')
    if w['cut']==2754:
        x,u,e1,e2 = [0,0,-1,1,0,0,0,1],[0,1,0,0,0,0,0,2],[0,1,0,0,0,0,0,0],[0,0,1,0,0,0,0,0]
        need(n==[[x[i]*u[j]-e1[i]*e2[j] for j in range(8)] for i in range(8)],'explicit residual')
    return [w['cut'],small,big]


def run():
    raw = inputs()
    payload = (HERE/'WITNESS.json').read_bytes()
    need(hashlib.sha256(payload).hexdigest()=='8abbe9564e19ac966bf97480d7c00891289f9b1d6be13cfa9a2d604b97bc0a5c','certificate pin')
    cert = json.loads(payload)
    ports = roots(raw['P104-FIXTURE.json']['section4_explicit_P104'])
    pools,captures,seen = replay(raw['LOWRANK-WITNESS.json'],ports,cert)
    sizes = [lower(pools[c],ports,cert['lower_vectors'],c==2753) for c in (2753,2823)]
    need(sizes==[324,427] and seen==110814,'pool and snapshot census')
    return dict(status='PASS_INDEPENDENT_P104_TAIL_AUDIT',cuts=4059,columns=280,target_snapshots=seen,
                pool_pairs=sizes,uppers=[upper(w,captures,ports) for w in cert['upper_witnesses']],
                scope='Rational pooled availability only; no chronological or paid-cost claim')


if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out',type=Path)
    args = parser.parse_args()
    need(args.out is None or not args.out.exists(),'occupied output')
    result = run()
    need(result==json.loads((HERE/'RESULT.json').read_text()),'receipt mismatch')
    if args.out:
        with args.out.open('x') as f:
            json.dump(result,f,indent=2)
            f.write('\n')
    print(json.dumps(result,sort_keys=True))

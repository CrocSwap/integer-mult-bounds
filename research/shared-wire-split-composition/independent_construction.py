#!/usr/bin/env python3
"""Independent sparse checks of the composed wire and two nominated splits.
Read-only standard-library checker; complete endpoint/invoice checks are separate.
"""
from collections import Counter, defaultdict
from fractions import Fraction as Q
import argparse
import gzip
from hashlib import sha256
import json
from pathlib import Path



def need(ok, label):
    if not ok:
        raise ValueError(label)


def put(v, i, x):
    if x:
        v[i] = x
    else:
        v.pop(i, None)


def covector(v, events):
    v = v.copy()
    for e in reversed(events):
        op, r = e[:2]
        if op == 'MOVE':
            continue
        if op in ('INIT', 'CLEAR'):
            v.pop(r, None)
        elif op == 'SCALE':
            put(v, r, v.get(r, 0) * Q(e[-2]))
        else:
            s = e[2]
            put(v, s, v.get(s, 0) + Q(e[-2]) * v.get(r, 0))
            if op == 'COPY':
                v.pop(r, None)
    return v


def vector(v, events):
    v = v.copy()
    for e in events:
        op, r = e[:2]
        if op == 'MOVE':
            continue
        if op in ('INIT', 'CLEAR'):
            v.pop(r, None)
        elif op == 'SCALE':
            put(v, r, v.get(r, 0) * Q(e[-2]))
        else:
            old = 0 if op == 'COPY' else v.get(r, 0)
            put(v, r, old + Q(e[-2]) * v.get(e[2], 0))
    return v


def split(word_path, proof_path):
    raw = word_path.read_bytes()
    w = json.loads(gzip.decompress(raw))
    pr = json.loads(proof_path.read_text())
    a, b, c, d = ({int(k): Q(v) for k, v in pr[x].items()} for x in ['a', 'b', 'c', 'd'])
    cut, f, p = (pr[x] for x in ['cut', 'frame', 'pivot'])
    n = w['public']
    need(sum(v*b.get(k, 0) for k,v in a.items()) == 1, 'a.b=1')
    need(sum(v*d.get(k, 0) for k,v in c.items()) == 1, 'c.d=1')
    left = covector(a, w['program'][:cut+1])
    left = {r:v for r,v in left.items() if r < n}
    right = vector(b, w['program'][cut+1:])
    need(left == c, 'a.P=c on all independent public inputs')
    need(right == d, 'S.b=d on all outputs including owned')
    cur = w['initial'] + [None] * w['owned_fields']
    for e in w['program'][:cut+1]:
        if e[0] == 'MOVE': cur[e[1]] = e[3]
        elif e[0] == 'INIT': cur[e[1]] = e[2]
        elif e[0] == 'CLEAR': cur[e[1]] = None
    need(all(r<n and cur[r] == f for r in set(a)|set(b)), 'public cut supports at common frame')
    need(all(w['initial'][r] == w['initial'][p] and w['final'][r] == w['final'][p]
             for r in set(c)|set(d)), 'boundary supports at common entry/exit')
    for name, row, col in [('B0',c,d),('BF',c,d),('BC',a,b)]:
        need(covector({p:Q(1)}, pr[name]) == row, name+' pivot row')
        need(vector(col, pr[name]) == {p:Q(1)}, name+' inverse pivot column')
    mutant = a.copy()
    mutant[p] = mutant.get(p,0) + 1
    wrong = {r:v for r,v in covector(mutant,w['program'][:cut+1]).items() if r<n}
    need(wrong != c, 'wrong prefix witness rejected')
    mutant = b.copy()
    mutant[p] = mutant.get(p,0) + 1
    need(vector(mutant,w['program'][cut+1:]) != d, 'wrong suffix witness rejected')
    return {'word': word_path.name, 'sha256': sha256(raw).hexdigest(),
            'canonical_payload_sha256':sha256(json.dumps(w,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
            'proof_sha256':sha256(proof_path.read_bytes()).hexdigest(),
            'pivot':p,'cut_after':cut,'frame':f,'prefix':'PASS','suffix':'PASS',
            'basis':'PASS','common_frames':'PASS','controls':2}


def access(e):
    if e[0] in ('MOVE','INIT','CLEAR','SCALE'): return [(e[1],'M')]
    return [(e[1],'M' if e[0]=='COPY' else 'A'),(e[2],'R')]


def composition(package_root):
    mw = package_root/'data/main_6936.json.gz'
    ww = package_root/'data/wh_6937.json.gz'
    m,w = (json.loads(gzip.decompress(p.read_bytes())) for p in [mw,ww])
    def shift(e, boundary, amount):
        z=e.copy();z[1]+=amount*(z[1]>=boundary)
        if z[0] in ('ADD','COPY'):z[2]+=amount*(z[2]>=boundary)
        return tuple(z)
    mc=Counter(shift(e,1461,16) for e in m['program'])
    wc=Counter(shift(e,1459,2) for e in w['program'])
    special={1452,1455,1459,1460}
    touches=lambda e:any(r in special for r,k in access(e))
    wr=[e for e in (wc-mc).elements() if not touches(e)]
    mr=[e for e in (mc-wc).elements() if touches(e)]
    wregs={r for e in wr for r,k in access(e)}
    mregs={r for e in mr for r,k in access(e)}
    need(not wregs&mregs, 'retained branch-exclusive footprints disjoint')
    need(all(mc[e]==wc[e] for e in mc.keys()&wc.keys()), 'shared literal multiplicity')
    return {'retained_wh_only_events':len(wr),'retained_main_only_events':len(mr),
            'footprint_intersection':sorted(wregs&mregs),'shared_multiplicity_changes':0,
            'main_sha256':sha256(mw.read_bytes()).hexdigest(),'wh_sha256':sha256(ww.read_bytes()).hexdigest()}


def wire(build_dir):
    before = json.loads(gzip.decompress((build_dir/'composed.json.gz').read_bytes()))
    after = json.loads(gzip.decompress((build_dir/'extra_wire_0.json.gz').read_bytes()))
    h = before['public']
    involved = [(i,e) for i,e in enumerate(after['program']) if any(r==h for r,k in access(e))]
    moves = [e for i,e in involved if e[0]=='MOVE']
    adds = [(i,e) for i,e in involved if e[0]=='ADD']
    need(len(moves)==3 and len(adds)==8, 'new wire primitive counts')
    ids = [after['initial'][h]]+[e[3] for e in moves]
    dims = [len(after['frames'][f]) for f in ids]
    def span(basis):
        out={0}
        for v in basis:out|={x^v for x in tuple(out)}
        return out
    spaces=[span(after['frames'][f]) for f in ids]
    need(all(x<y for x,y in zip(spaces,spaces[1:])), 'nested helper itinerary')
    sources = {e[2] for i,e in adds if e[1]==h}
    targets = {e[1] for i,e in adds if e[2]==h}
    need(sources=={226,1206} and targets=={449,990}, 'four distinct wire partners')
    n = after['public']+after['owned_fields']
    def partner_window(r, source):
        points = [i for i,e in adds if (e[2] if source else e[1])==r]
        need(len(points)==2, 'paired partner contacts')
        for e in after['program'][points[0]+1:points[1]]:
            for rr,kind in access(e):
                if rr!=r: continue
                need(e[0]=='MOVE' or kind==('R' if source else 'A'), 'protected partner window')
    for r in sources:partner_window(r,True)
    for r in targets:partner_window(r,False)
    cur=after['initial']+[None]*after['owned_fields']
    for e in after['program']:
        if e[0]=='MOVE':cur[e[1]]=e[3]
        elif e[0]=='INIT':cur[e[1]]=e[2]
        elif e[0]=='CLEAR':cur[e[1]]=None
        elif e[0]=='ADD' and (e[1]==h or e[2]==h):
            need(cur[e[1]]==cur[e[2]]==e[-1], 'actual common frame at wire ADD')
    local=[e for i,e in involved]
    for r in sources|targets|{h}:
        col=vector({r:Q(1)},local)
        want={r:Q(1)}
        if r==226:want[449]=Q(1)
        if r==1206:want[990]=Q(-1)
        need(col==want, 'all five independent local columns')
    need(dims==[0,3,6,8], 'wire dimensions')
    return {'helper':h,'frames':ids,'dimensions':dims,'sources':sorted(sources),
            'targets':sorted(targets),'endpoint':'y+=x,u-=v,h restored',
            'protected_windows':'PASS','local_columns':5,
            'net_helper_profile':'H3+H3+H2-H8'}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package-root',type=Path,required=True)
    parser.add_argument('--build-dir',type=Path,required=True)
    args=parser.parse_args()
    build_dir=args.build_dir
    receipt={'composition':composition(args.package_root),'new_wire':wire(build_dir),'splits':[
        split(build_dir/'extra_wire_0.json.gz',build_dir/'split759.proof.json'),
        split(build_dir/'split759.json.gz',build_dir/'split759_450.proof.json')]}
    print(json.dumps(receipt,indent=2))
    print('PASS_CONSTRUCTION_INTERFACE_REVIEW')


if __name__ == '__main__':
    main()

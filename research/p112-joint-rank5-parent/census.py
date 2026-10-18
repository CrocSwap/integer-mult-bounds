"""Exact joint rank-five descendants of one named P112 parent.
SPDX-License-Identifier: Apache-2.0; prepared for woklerx with Codex assistance.
"""
from pathlib import Path
from collections import Counter
import argparse,hashlib,json
HERE=Path(__file__).resolve().parent
def need(x,s):
    if not x:raise ValueError(s)
def bits(x):
    while x:
        b=x&-x;yield b.bit_length()-1;x^=b
def basis(rows):
    piv={}
    for v in rows:
        while v:
            b=v&-v
            if b in piv:v^=piv[b]
            else:piv[b]=v;break
    return list(piv.values())
def span(bs):
    s=[0]
    for b in bs:s += [v^b for v in s]
    return sorted(s[1:])
def run():
    raw=(HERE/'inputs/MODEL.json').read_bytes();pin=json.loads((HERE/'DEPENDENCY.json').read_text())
    need(hashlib.sha256(raw).hexdigest()==pin['sha256'],'model pin')
    m=json.loads(raw);rs=m['lines'];live=m['live'];lm=sum(1<<i for i in live)
    ip=[[sum(x*y for x,y in zip(r,s))//4 for s in rs] for r in rs]
    pair=[sum(((x+1)&1)<<j for j,x in enumerate(row)) for row in ip]
    supports=[]
    for i in range(120):
        s=sum(1<<j for j in live if ip[i][j]);supports.extend((s,s&~(1<<i)))
    left,right=supports[7],supports[0]
    def rank(a,b):return len(basis(pair[i]&b for i in bits(a)))
    need(rank(left,right)==7,'parent rank7')
    rowcode=span(basis(pair[j]&left for j in bits(right)))
    colcode=span(basis(pair[i]&right for i in bits(left)))
    need(len(rowcode)==len(colcode)==127,'complete dimension7codes')
    adjacency=[sum(1<<j for j in live if i!=j and ip[i][j]==0) for i in range(120)]
    frames=[]
    def extend(q,c):
        if len(q)==8:frames.append(q);return
        while c.bit_count()>=8-len(q):
            b=c&-c;c^=b;i=b.bit_length()-1;extend(q+[i],c&adjacency[i])
    extend([],lm);need(len(frames)==1260,'full frame enumeration')
    incidence=[0]*120
    for k,f in enumerate(frames):
        for i in f:incidence[i]|=1<<k
    cache={}
    def hits(s):
        if s not in cache:
            h=0
            for i in bits(s):h|=incidence[i]
            cache[s]=h
        return cache[s]
    candidates=[];counts=Counter();spectrum=Counter();streams=hashlib.sha256()
    def add(kind,a,b,description):
        r=rank(a,b);spectrum[(kind,r)]+=1
        if r>5:return
        counts[kind]+=1
        h=(hits(a)&hits(b)).bit_count();d=(a&b).bit_count()
        candidates.append((h,d,kind,a,b,description))
        streams.update(f'{kind}:{a:x}:{b:x}:{r}:{h}:{d}\n'.encode())
    for kind,code,s,other in [('row2',rowcode,left,right),('col2',colcode,right,left)]:
        seen=0
        for a in code:
            for b in code:
                if not a<b<a^b:continue
                seen+=1;cut=s&~(a|b)
                add(kind,cut,other,[hex(a),hex(b)]) if kind=='row2' else add(kind,other,cut,[hex(a),hex(b)])
        need(seen==2667,'all dimension2dual subspaces')
    for a in rowcode:
        for b in colcode:add('joint11',left^a,right^b,[hex(a),hex(b)])
    best=max(candidates);max_hits=best[0];max_diagonal=max(c[1] for c in candidates)
    need(all(0<=r<=6 for (_,r) in spectrum),'only predicted ranks')
    controls={
        'parent_is_not_rank5':rank(left,right)==7,
        'single_cut_is_not_rank5':rank(left^rowcode[0],right)==6,
        'incompatible_joint_cut_is_rank6':spectrum[('joint11',6)]>0,
        'attaining_cut_rank5':rank(best[3],best[4])==5,
    };need(all(controls.values()),'positive and failure controls')
    by_kind={k:max(c[0] for c in candidates if c[2]==k) for k in counts}
    return dict(max_hits_by_kind=by_kind,status='PASS_JOINT_RANK5_PARENT',parent_tags=[7,0],parent_root_vectors=[rs[3],rs[0]],parent_support_sizes=[left.bit_count(),right.bit_count()],domain_counts=dict(counts),rank_spectrum={f'{k}:{r}':v for (k,r),v in sorted(spectrum.items())},max_frame_hits=max_hits,max_diagonal_entries=max_diagonal,maximizer_count=sum(c[0]==max_hits for c in candidates),best=dict(frame_hits=best[0],diagonals=best[1],kind=best[2],rows=list(bits(best[3])),columns=list(bits(best[4])),cut_codewords=best[5]),stream_sha256=streams.hexdigest(),controls=controls)
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');a=ap.parse_args();result=run();p=HERE/'CERTIFICATE.json'
    if a.write:p.write_text(json.dumps(result,indent=2)+'\n')
    else:need(result==json.loads(p.read_text()),'complete receipt')
    print('PASS_JOINT_RANK5_PARENT candidates=13335 max_hits='+str(result['max_frame_hits'])+' one_axis='+str(result['max_hits_by_kind'])+' controls=4')


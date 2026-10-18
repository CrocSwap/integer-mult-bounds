"""Independent support-representative screen. Apache-2.0; woklerx/Codex."""
from pathlib import Path
from itertools import combinations,product
from collections import Counter
import argparse,hashlib,json
HERE=Path(__file__).resolve().parent

def need(v,s):
    if not v:raise ValueError(s)
def bits(v):
    while v:
        b=v&-v;yield b.bit_length()-1;v^=b
def basis(rows):
    piv={}
    for v in rows:
        while v:
            b=v&-v
            if b in piv:v^=piv[b]
            else:piv[b]=v;break
    return list(piv.values())
def run():
    for p in json.loads((HERE/'DEPENDENCY.json').read_text()):
        need(hashlib.sha256((HERE/p['local']).read_bytes()).hexdigest()==p['sha256'],'dependency bytes')
    data=json.loads((HERE/'inputs/MODEL.json').read_text());cover=json.loads((HERE/'inputs/COVERING.json').read_text())
    rs=data['lines'];live=data['live'];lm=sum(1<<i for i in live)
    need(len(rs)==120 and len(live)==112 and len(set(tuple(r) for r in rs))==120,'root dimensions')
    ip=[[sum(x*y for x,y in zip(a,b))//4 for b in rs] for a in rs]
    need(all(sum(x*x for x in r)==8 for r in rs),'root norms')
    pair=[sum(((v+1)&1)<<j for j,v in enumerate(row)) for row in ip]
    support=[]
    for i in range(120):
        s=sum(1<<j for j in live if ip[i][j]);support.extend((s,s&~(1<<i)))
    adj=[sum(1<<j for j in live if i!=j and ip[i][j]==0) for i in range(120)]
    frames=[]
    def extend(q,c):
        if len(q)==8:frames.append(q);return
        while c.bit_count()>=8-len(q):
            b=c&-c;c^=b;i=b.bit_length()-1;extend(q+[i],c&adj[i])
    extend([],lm);need(len(frames)==1260,'frame count')
    incidence=[0]*120
    for k,f in enumerate(frames):
        for i in f:incidence[i]|=1<<k
    hits_cache={}
    def hits(m):
        if m not in hits_cache:
            v=0
            for i in bits(m):v|=incidence[i]
            hits_cache[m]=v
        return hits_cache[m]
    patterns=[];original_diagonal=0
    for a,b,cut in cover['terms']:
        l=support[a]^int(cut,16);r=support[b]
        need(len(basis(pair[i]&r for i in bits(l)))==6,'original rank')
        patterns.append(hits(l)&hits(r));original_diagonal|=l&r
    need(len(set(patterns))==10,'distinct hit patterns')
    frame_counts=[sum(p>>k&1 for p in patterns) for k in range(len(frames))]
    need(min(frame_counts)==8 and hashlib.sha256(bytes(frame_counts)).hexdigest()==cover['exact_check']['frame_counts_sha256'],'original full frame demand')
    need((lm&~original_diagonal).bit_count()==21,'original diagonal gap')
    exact=[dict(count=0,union=0,candidates=[]) for _ in patterns]
    monotone=[dict(count=0,union=0,candidates=[]) for _ in patterns]
    ranks=Counter();cases=0;unique={}
    for a,l in enumerate(support):
        for b,r in enumerate(support):
            bs=basis(pair[j]&l for j in bits(r));ranks[len(bs)]+=1
            if len(bs)!=7:continue
            words=[0]
            for g in bs:words += [w^g for w in words]
            for w in sorted(words[1:]):
                cases+=1;row=l^w;ph=hits(row)&hits(r);diag=row&r
                need(len(basis(pair[i]&r for i in bits(row)))==6,'every maximal slice is rank six')
                for k,target in enumerate(patterns):
                    if target&~ph:continue
                    rec=monotone[k];rec['count']+=1;rec['union']|=diag
                    # Transposition preserves hits and diagonal support, so it
                    # cannot enlarge these unions or representative classes.
                    rec['candidates'].append([a,b,hex(w),hex(diag)])
                    if ph==target:
                        rec=exact[k];rec['count']+=1;rec['union']|=diag;rec['candidates'].append([a,b,hex(w),hex(diag)])
    need(cases==967232 and ranks=={7:7616,8:37440,9:12544},'complete dictionary')
    result=dict(status='PASS_RANK6_REPRESENTATIVE_SCAN',parent_ranks=dict(sorted(ranks.items())),cases=cases,original_missing=list(bits(lm&~original_diagonal)))
    for name,records in [('exact',exact),('monotone',monotone)]:
        u=0
        for rec in records:u|=rec['union']
        result[name]=dict(missing_even_after_union=list(bits(lm&~u)),counts=[x['count'] for x in records],diagonal_union_sizes=[x['union'].bit_count() for x in records],candidates_sha256=hashlib.sha256(json.dumps([r['candidates'] for r in records],separators=(',',':')).encode()).hexdigest())
        # Complete finite multiple-choice union search. Equal union states may
        # safely be merged: future unions depend only on the covered set.
        states={0:[]}
        for rec in records:
            choices={int(v[3],16):v[:3] for v in rec['candidates']}
            states={old|mask:path+[witness] for old,path in states.items() for mask,witness in choices.items()}
        best=max(states,key=lambda s:(s.bit_count(),s))
        result[name]['distinct_final_unions']=len(states)
        result[name]['maximum_diagonals']=best.bit_count()
        result[name]['best_terms']=states[best]
        result[name]['best_missing']=list(bits(lm&~best))
    controls=[]
    def reject(name,condition):
        need(not condition,'false claim accepted: '+name);controls.append(name)
    reject('frame hits imply diagonal coverage',original_diagonal==lm)
    reject('any hit-preserving representatives can repair all diagonals',result['monotone']['maximum_diagonals']==112)
    a,b,cut=cover['terms'][0]
    reject('restoring removed rows preserves rank six',len(basis(pair[i]&support[b] for i in bits(support[a])))==6)
    # Transposition changes orientation, but never the diagonal supports or
    # frame-hit incidence; all column-side cuts are therefore included.
    need(all(len(basis(pair[i]&support[b] for i in bits(support[a]^int(cut,16))))==6
             for a,b,cut in result['exact']['best_terms']),'positive attaining representatives')
    need(result['exact']['maximum_diagonals']==99 and result['monotone']['maximum_diagonals']==99,'sharp diagonal cap')
    result['controls']=controls
    return result
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');args=ap.parse_args()
    result=json.loads(json.dumps(run()));path=HERE/'CERTIFICATE.json'
    if args.write:path.write_text(json.dumps(result,indent=2)+'\n')
    else:need(result==json.loads(path.read_text()),'complete certificate mismatch')
    print('PASS_RANK6_REPRESENTATIVES parents=7616 slices=967232 patterns=10 max_diagonals=99 unavoidable_missing=13 controls=3')

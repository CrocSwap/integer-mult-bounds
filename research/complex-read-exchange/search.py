#!/usr/bin/env python3
"""Bounded coupled entering-copy read-exchange nomination; not theorem admission.

Searches PR699's explicitly open cross-pair class. The rewrite semantics and
frame-floor policy follow its credited SW4 construction.
Candidate nomination uses floating moment ordering; exact verification is separate.
"""
import argparse
from collections import Counter, defaultdict
from functools import lru_cache
import gzip
import hashlib
import itertools
import json
import math
from pathlib import Path
import time

V = 112
FULL = (256, 128, 64, 32, 16, 8, 4, 2, 1)

@lru_cache(None)
def basis(vectors):
    piv = {}
    for x in vectors:
        while x:
            k = x.bit_length() - 1
            if k in piv:
                x ^= piv[k]
            else:
                piv[k] = x
                break
    for k in sorted(piv):
        for j in piv:
            if j > k and piv[j] >> k & 1:
                piv[j] ^= piv[k]
    return tuple(piv[k] for k in sorted(piv, reverse=True))

@lru_cache(None)
def join(a, b):
    return basis(a+b)

@lru_cache(None)
def cap_ok(frame, port):
    return all((x & port).bit_count() % 2 == 0 for x in frame)

@lru_cache(None)
def hyper(port):
    return basis(tuple(x for x in range(1, 512) if (x & port).bit_count() % 2 == 0))

def regs(e):
    return e[1:3] if e[0] == 'add' else e[1:2]

def read(path):
    raw = Path(path).read_bytes()
    if str(path).endswith('.gz'):
        raw = gzip.decompress(raw)
    return json.loads(raw), hashlib.sha256(raw).hexdigest()

def encode(x):
    return json.dumps(x, sort_keys=True, separators=(',', ':')).encode()

class Evaluator:
    def __init__(self, word):
        self.w = word
        n = 2*V+word['report']['R']
        start = [(p,) for p in word['ports']] + [()]*(n-V)
        for q, f in word['start_extra'].items():
            start[int(q)] = basis(tuple(f))
        end = [FULL]*V+[hyper(p) for p in word['ports']]+[FULL]*(n-2*V)
        for q, f in word['helper_final'].items():
            end[int(q)] = basis(tuple(f))
        cur = start[:]
        paid = [0]*10
        for e in word['A']:
            f = basis(tuple(e[-1]))
            for q in regs(e):
                if join(cur[q],f) != f:
                    raise ValueError(('A containment',q))
                d = len(f)-len(cur[q])
                if d: paid[d] += 1
                cur[q] = f
        levels = {int(t):basis(tuple(f)) for t,f in word.get('target_levels',{}).items()}
        for q, f in zip(word['centers'],word['center_frames']):
            f = basis(tuple(f))
            served = {levels.get(e[1]-V,()) for e in word['cut'] if e[2] == q}
            for t in sorted(served,key=lambda x:-len(x)):
                if t != f: paid[len(f)-len(t)] += 1
                f = t
        self.cur, self.paid, self.end = cur,paid,end
        self.gates = [(e[1:3] if e[0]=='add' else e[1:2],basis(tuple(e[-1]))) for e in word['B']]
        self.tails = [(regs(word['cleanup'][i]),basis(tuple(f))) for i,f in word.get('early_cleanup',[])]
        self.widths = Counter(len(end[q])-len(start[q]) for q in range(2*V,n))

    def run(self, moves=(), materialize=False):
        edits = {}
        delete = set()
        insert = defaultdict(list)
        for m in moves:
            i=m['read_index']
            if i in edits: return None,('conflicting_read',i)
            edits[i]=[m['target'],m['r'] if m['kind']=='h2r' else m['h']]
            if m['kind']=='h2r':
                if m['delete_preread_index'] in delete: return None,('conflicting_delete',i)
                delete.add(m['delete_preread_index'])
            else:
                insert[m['insert_preread_before']].append([m['target'],m['h']])
        if delete & set(edits): return None,('edit_delete',)
        cur = self.cur[:]
        paid = self.paid[:]
        frames = []
        def gate(rs, floor, origin):
            f=floor
            for q in rs: f=join(f,cur[q])
            for q in rs:
                if V<=q<2*V and not cap_ok(f,self.w['ports'][q-V]):
                    return ('cap',origin,q)
            for q in rs:
                d=len(f)-len(cur[q])
                if d: paid[d]+=1
                cur[q]=f
            if materialize: frames.append(list(f))
            return None
        for i,(rs,f) in enumerate(self.gates):
            for irs in insert.get(i,()):
                bad=gate(irs,(),['insert',i])
                if bad:return None,bad
            if i in delete:continue
            bad=gate(edits.get(i,rs),() if i in edits else f,i)
            if bad:return None,bad
        tails=[]
        for i,(rs,f) in enumerate(self.tails):
            for q in rs:f=join(f,cur[q])
            for q in rs:
                if join(cur[q],f)!=f or join(f,self.end[q])!=self.end[q]:
                    return None,('tail',i,q)
            for q in rs:
                d=len(f)-len(cur[q])
                if d:paid[d]+=1
                cur[q]=f
            if materialize:tails.append(list(f))
        for q,f in enumerate(self.end):
            if join(cur[q],f)!=f:return None,('end',q)
            d=len(f)-len(cur[q])
            if d:paid[d]+=1
        profile={str(k):v for k,v in enumerate(paid) if k and v}
        if materialize:return (profile,frames,tails),None
        return profile,None

def candidates(w):
    """Fixed pair rule and insertion point follow PR699 NOTES.md.

    Each h2r move requires one literal matching entrance pre-read. Other
    pre-read arrangements are outside this search, not silently extrapolated.
    """
    gates=w['B']
    found=[]
    for h in sorted(map(int,w['start_extra'])):
        touched=[i for i,e in enumerate(gates) if h in regs(e)]
        writes=[i for i in touched if gates[i][1]==h]
        if not writes:continue
        ci=writes[0]; e=gates[ci]
        if e[0]!='add' or e[3:5]!=[1,1] or V<=e[2]<2*V:continue
        r=e[2]
        before=[i for i in touched if i<ci]
        if any(not(gates[i][0]=='add' and V<=gates[i][1]<2*V and gates[i][2]==h) for i in before):continue
        stop=next((i for i in range(ci+1,len(gates)) if gates[i][1] in (h,r)),len(gates))
        insertion=before[-1]+1 if before else ci
        moves=[]
        for i in range(ci+1,stop):
            g=gates[i]
            if g[0]!='add' or not V<=g[1]<2*V or g[2] not in (h,r):continue
            t, a, b = g[1],g[3],g[4]
            m={'h':h,'r':r,'read_index':i,'target':t,'coef':[a,b]}
            if g[2]==h:
                pre=[j for j in before if gates[j][:5]==['add',t,h,-a,b]]
                if len(pre)!=1:continue
                m.update(kind='h2r',delete_preread_index=pre[0])
            else:
                m.update(kind='r2h',insert_preread_before=insertion,preread=['add',t,h,-a,b])
            moves.append(m)
        if moves: found.append({'h':h,'r':r,'copy_index':ci,'stop_index':stop,'moves':moves})
    return found

def rewrite(w,moves,ev):
    result,bad=ev.run(moves,materialize=True)
    if bad:raise ValueError(bad)
    prof,frames,tails=result
    edits={}; delete=set(); insert=defaultdict(list)
    for m in moves:
        g=list(w['B'][m['read_index']][:-1])
        g[2]=m['r'] if m['kind']=='h2r' else m['h']
        edits[m['read_index']]=g
        if m['kind']=='h2r':delete.add(m['delete_preread_index'])
        else:insert[m['insert_preread_before']].append(m['preread'])
    nb=[]
    for i,e in enumerate(w['B']):
        nb.extend([list(g) for g in insert.get(i,())])
        if i not in delete:nb.append(list(edits.get(i,e[:-1])))
    if len(nb)!=len(frames):raise ValueError('Frame/gate length mismatch')
    nw=dict(w,B=[g+[f] for g,f in zip(nb,frames)])
    nw['early_cleanup']=[[old[0],f] for old,f in zip(w.get('early_cleanup',[]),tails)]
    nw['report']=dict(w['report'],local_profile=prof,local_rank_mass=sum(int(k)*v for k,v in prof.items()))
    return nw

def cost(profile,exponent=0.0016634287545402057):
    return sum(v*(int(k)**(1-exponent)) for k,v in profile.items())

def masks(n):
    return range(1,1<<n)

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('word',type=Path)
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--baseline-recipe',type=Path,required=True)
    ap.add_argument('--pair-domain',choices=['shared-targets','all'],default='shared-targets')
    ap.add_argument('--arity',type=int,choices=[2,3],default=2)
    ap.add_argument('--seconds',type=float,default=1200)
    a=ap.parse_args(); a.out.mkdir(parents=True,exist_ok=True)
    started=time.monotonic()
    w,sha=read(a.word); rec=json.loads(a.baseline_recipe.read_text())
    if sha!=rec['input_sha256']:raise ValueError('Pinned promoted-input hash mismatch')
    ev=Evaluator(w)
    baseline,bad=ev.run()
    if bad or baseline!=rec['profile_in']:raise ValueError(('input profile',baseline,bad))
    sw,bad=ev.run(rec['moves'])
    if bad or sw!=rec['profile_out']:raise ValueError(('SW4 profile',sw,bad))
    sw_word=rewrite(w,rec['moves'],ev)
    if hashlib.sha256(encode(sw_word)).hexdigest()!=rec['output_sha256']:
        raise ValueError('Known SW4 rebuilt bytes differ')
    pairs=candidates(w)
    (a.out/'CANDIDATES.json').write_text(json.dumps({'input_sha256':sha,'pairs':pairs},indent=2)+'\n')
    print('BASELINE_OK',sha,'pairs',len(pairs),'single_subsets',sum((1<<len(p['moves']))-1 for p in pairs),flush=True)
    known=set(rec['pairs'])
    counts=Counter(); profiles=Counter(); better=[]; best=cost(sw)
    singles={}
    for p in pairs:
        for mask in masks(len(p['moves'])):
            moves=[m for j,m in enumerate(p['moves']) if mask>>j&1]
            profile,bad=ev.run(moves)
            counts['single_total']+=1
            counts['single_'+('legal' if profile else bad[0])]+=1
            singles[p['h'],mask]=(profile,bad)
    print('SINGLES',dict(counts),flush=True)
    pairs_tested=[]; stopped=False
    failure_sites=hashlib.sha256()
    # Hold known full exchanges on untouched pairs fixed, so any nominated
    # pair choice must improve the actual SW4 baseline, not the weaker input.
    for group in itertools.combinations(pairs,a.arity):
        ids={p['h'] for p in group}
        graph={p['h']:set() for p in group}
        for p,q in itertools.combinations(group,2):
            if {m['target'] for m in p['moves']}&{m['target'] for m in q['moves']}:
                graph[p['h']].add(q['h']);graph[q['h']].add(p['h'])
        reached={group[0]['h']}
        while True:
            expanded=reached|set().union(*(graph[x] for x in reached))
            if expanded==reached:break
            reached=expanded
        if a.pair_domain=='shared-targets' and reached!=ids:continue
        fixed=[m for m in rec['moves'] if m['h'] not in ids]
        nchecked=0
        for selection in itertools.product(*(masks(len(p['moves'])) for p in group)):
            if time.monotonic()-started>a.seconds:stopped=True;break
            if all(mask==(1<<len(p['moves']))-1 for p,mask in zip(group,selection)):continue
            selected=[m for p,mask in zip(group,selection) for j,m in enumerate(p['moves']) if mask>>j&1]
            moves=fixed+selected
            profile,bad=ev.run(moves)
            nchecked+=1;counts['coupled_total']+=1
            failure_sites.update(encode([[p['h'] for p in group],list(selection),list(bad) if bad else None])+b'\n')
            if profile is None:
                counts['coupled_'+bad[0]]+=1;continue
            counts['coupled_legal']+=1
            key=tuple(sorted((int(k),v) for k,v in profile.items()));profiles[key]+=1
            val=cost(profile)
            if val<cost(sw)-1e-9:counts['floating_improvements']+=1
            if val<best-1e-9:
                counts['successive_best']+=1
                item={'pairs':[p['h'] for p in group],'masks':list(selection),'profile':profile,'floating_cost_delta':val-cost(sw),'moves':moves}
                better.append(item);best=val
                (a.out/'BEST.json').write_text(json.dumps(item,indent=2)+'\n')
                raw=encode(rewrite(w,moves,ev));(a.out/'BEST-WORD.json.gz').write_bytes(gzip.compress(raw,mtime=0))
                print('BETTER',item['pairs'],item['masks'],item['floating_cost_delta'],profile,flush=True)
        pairs_tested.append([*[p['h'] for p in group],nchecked])
        if len(pairs_tested)%20==0:print('PROGRESS',len(pairs_tested),dict(counts),'seconds',round(time.monotonic()-started,1),flush=True)
        if stopped:break
    report={'status':'TIME_LIMIT' if stopped else 'COMPLETE_FINITE_DOMAIN','input_sha256':sha,'comparison_sha256':rec['output_sha256'],'domain':a.pair_domain,'arity':a.arity,'at_least_one_partial':True,'unchanged_other_sw4_pairs':True,'counts':dict(counts),'failure_site_sha256':failure_sites.hexdigest(),'pairs_tested':pairs_tested,'distinct_legal_profiles':[{'profile':dict(k),'count':v} for k,v in profiles.items()],'successive_best':better,'seconds':round(time.monotonic()-started,3),'scope':'Search nomination only. Scalar equality, exact cost and full supplier admission required for any positive candidate.'}
    (a.out/'SEARCH.json').write_text(json.dumps(report,indent=2)+'\n')
    print('DONE',report['status'],dict(counts),'seconds',report['seconds'],flush=True)

if __name__=='__main__':main()

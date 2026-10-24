#!/usr/bin/env python3
"""Bounded receiver-word transfer on PR4470. Apache-2.0; OpenAI assistance.

The pinned constructor emits the object under test. No predecessor proof engine
is imported by this checker. Physical lowering of a successful new frame path is
an explicit further obligation, not a consequence of this local search.
"""
from __future__ import annotations
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
from functools import lru_cache
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SCALE = 10**18
C = Q('0.00302015')
BASE_PAID = {1:2237,2:388,3:494,4:147,5:36,8:8}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def authenticate():
    rows=json.loads((HERE/'SOURCES.json').read_bytes())['files']
    for row in rows:
        if row['usage']!='input':
            continue
        path=ROOT/row['path']
        need(not path.is_symlink(), 'Source alias')
        data=path.read_bytes()
        need(hashlib.sha256(data).hexdigest()==row['sha256'],'Source SHA256 '+row['path'])
        need(hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==row['git_blob'],
             'Source blob '+row['path'])


def emit():
    authenticate()
    with tempfile.TemporaryDirectory(prefix='receiver-source-') as cache:
        code="import sys,json;sys.path.insert(0,sys.argv[1]);import native_joint; c,p,b,old,ch=native_joint.construct();print(json.dumps({'canonical':c,'programs':p}))"
        run=subprocess.run([sys.executable,'-I','-B','-X','pycache_prefix='+cache,'-c',code,
                            str(ROOT/'research/joint-helper-lattice')],check=True,
                           stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=60)
    return json.loads(run.stdout)


@lru_cache(None)
def space(basis):
    values={0}
    for x in basis:
        need(type(x) is int and 0<x<512,'Binary vector domain')
        old=set(values); values.update(v^x for v in old)
        need(len(values)==2*len(old),'Dependent basis')
    return frozenset(values)


def extend(prefix, target):
    out=list(prefix); have=set(space(tuple(prefix)))
    need(have<=target,'Flag extension domain')
    for v in sorted(target):
        if v not in have:
            out.append(v); have.update(x^v for x in tuple(have))
    need(have==target,'Flag completeness')
    return out


def rank(s):
    need(len(s)>0 and len(s)&(len(s)-1)==0,'Subspace cardinality')
    return len(s).bit_length()-1


def joined(a,b):
    return frozenset(x^y for x in a for y in b)


def flags(starts, ends):
    """All realisable dimension triples for this fixed three-shear word."""
    a,b,x=starts; ae,be,xe=ends
    l1=joined(a,b); l2=joined(l1,x); v3=ae&be; v2=v3&xe
    if not l2<=v2:
        return []
    path=extend([],l1); path=extend(path,l2); path=extend(path,v2); path=extend(path,v3)
    out=[]
    for i in range(rank(l1),rank(v2)+1):
        for j in range(max(i,rank(l2)),rank(v2)+1):
            for k in range(j,rank(v3)+1):
                out.append([path[:i],path[:j],path[:k]])
    return out


def matrix(word):
    out=[[int(i==j) for j in range(3)] for i in range(3)]
    for d,s,c in word:
        need(d!=s and c in (-1,1),'Unit shear domain')
        out[d]=[u+c*v for u,v in zip(out[d],out[s])]
    return out


def dual(word):
    return [(s,d,-c) for d,s,c in word]


def histogram(starts, ends, word, frame_bases):
    current=list(starts); counts=Counter()
    for (d,s,_),base in zip(word,frame_bases):
        frame=space(tuple(base))
        for role in (d,s):
            need(current[role]<=frame,'Illegal local forward frame')
            gap=rank(frame)-rank(current[role])
            if gap: counts[gap]+=1
            current[role]=frame
    for role,end in enumerate(ends):
        need(current[role]<=end,'Unpaid or illegal restoration')
        gap=rank(end)-rank(current[role])
        if gap: counts[gap]+=1
    return counts


def power_bounds():
    out={0:(0,0),1:(SCALE,SCALE)}
    for r in range(2,10):
        x=Q(r-1,r+1); term=x; lo=Q(0)
        for k in range(160):
            lo+=2*term/(2*k+1); term*=x*x
        hi=lo+2*term/(321*(1-x*x))
        t=1-C
        zlo=Q((lo*t*10**36).__floor__(),10**36)
        zhi=Q((hi*t*10**36).__ceil__(),10**36)
        def exp_bounds(z):
            term=Q(1); total=Q(1)
            for k in range(1,81):
                term*=z/k; total+=term
            first=term*z/81
            return total,total+first/(1-z/82)
        a=exp_bounds(zlo)[0]; b=exp_bounds(zhi)[1]
        out[r]=((a*SCALE).__floor__(),(b*SCALE).__ceil__())
    return out


def cost(profile, bounds):
    return (sum(n*bounds[r][0] for r,n in profile.items()),
            sum(n*bounds[r][1] for r,n in profile.items()))


def operands(e):
    if e[0]=='scalar':
        g=e[1]
        return g[1:3] if g[0] in ('add','copy') else g[1:2]
    return []


def consume(state,e):
    if e[0]=='scalar':
        for who in operands(e):
            if who[0]=='L': state[who[1]]=e[2]
    elif e[0]=='warp':
        state[e[1][1]]=e[4]


def full_bill(word,c):
    fs=[space(tuple(b)) for b in c['frames']]; state=list(c['start']); bill=Counter()
    def move(r,f):
        need(fs[state[r]]<=fs[f],'Full chronological nesting')
        gap=rank(fs[f])-rank(fs[state[r]])
        if gap: bill[gap]+=1
        state[r]=f
    for e in word:
        if e[0]=='scalar':
            for who in operands(e):
                if who[0]=='L':move(who[1],e[2])
        elif e[0]=='warp':move(e[1][1],e[3]);state[e[1][1]]=e[4]
        elif e[0]=='center':bill[e[4]]+=1
    for r,f in enumerate(c['final']):move(r,f)
    return bill


def windows(word,c):
    state=list(c['start']); phase=None; ordinal=Counter(); result=[]
    for i,e in enumerate(word):
        if e[0]=='phase':phase=e[1]
        key=(phase,ordinal[phase])
        if e[0]=='scalar' and all(w[0]=='L' for w in operands(e)):
            ordinal[phase]+=1
        if phase in ('B','cleanup_tail') and i+1<len(word):
            f=word[i+1]
            if e[0]==f[0]=='scalar' and e[1][0]==f[1][0]=='add':
                g,h=e[1],f[1]
                if all(w[0]=='L' for w in g[1:3]+h[1:3]):
                    a,x=g[1][1],g[2][1]; b,y=h[1][1],h[2][1]
                    ca,cb=Q(*g[3:]),Q(*h[3:])
                    if x==y and len({a,b,x})==3 and ca in (-1,1) and cb in (-1,1):
                        roles=[a,b,x]; end=[]
                        for r in roles:
                            target=c['final'][r]
                            for later in word[i+2:]:
                                if later[0]=='scalar' and ['L',r] in operands(later):target=later[2];break
                                if later[0]=='warp' and later[1]==['L',r]:target=later[3];break
                            end.append(target)
                        result.append(dict(index=i,phase=key[0],ordinal=key[1],roles=roles,
                            start=[c['frames'][state[r]] for r in roles],
                            end=[c['frames'][f] for f in end],
                            old_frames=[c['frames'][e[2]],c['frames'][f[2]]],
                            coefficients=[int(ca),int(cb)]))
        consume(state,e)
    return result


def self_tests():
    n=0
    for a in (-1,1):
        for b in (-1,1):
            old=[(0,2,a),(1,2,b)]; s=-a*b
            new=[(0,1,s),(1,2,b),(0,1,-s)]
            need(matrix(old)==matrix(new) and matrix(dual(old))==matrix(dual(new)),'Dirty identity')
            bad=new[:-1]+[(0,1,s)]
            need(matrix(bad)!=matrix(old),'Wrong restoration sign accepted');n+=3
    start=[space(()),space(()),space((1,))]; end=[space((1,2))]*3
    for f in flags(start,end):
        histogram(start,end,[(0,1,1),(1,2,-1),(0,1,-1)],f);n+=1
    need(not flags([space((1,)),space((2,)),space((4,))], [space((1,2))]*3),'Incompatible exit allowed')
    try: space((1,1))
    except ValueError:n+=1
    else:raise ValueError('Dependent basis accepted')
    return n+1


def run():
    tests=self_tests(); source=emit(); c=source['canonical']; progs=source['programs']
    words={d:[e for e in p if e[0]!='climb'] for d,p in progs.items()}
    for word in words.values():need(dict(full_bill(word,c))==BASE_PAID,'Source local bill')
    candidates=windows(words['forward'],c); chosen=candidates[:12]; bounds=power_bounds(); results=[]
    for w in chosen:
        ca,cb=w['coefficients']; old=[(0,2,ca),(1,2,cb)]; s=-ca*cb
        replacement=[(0,1,s),(1,2,cb),(0,1,-s)]
        starts=[space(tuple(b)) for b in w['start']]; ends=[space(tuple(b)) for b in w['end']]
        oldp=histogram(starts,ends,old,w['old_frames']); oldcost=cost(oldp,bounds)
        choices=flags(starts,ends); best=None
        for frames in choices:
            profile=histogram(starts,ends,replacement,frames); co=cost(profile,bounds)
            item=(co[1],json.dumps(frames),frames,profile,co)
            if best is None or item[:2]<best[:2]:best=item
        row={**w,'old_paid':dict(sorted(oldp.items())),'legal_dimension_triples':len(choices)}
        if best:
            _,_,frames,newp,newcost=best
            row.update(new_frames=frames,new_paid=dict(sorted(newp.items())),
                       paid_moment_gain_scaled_interval=[oldcost[0]-newcost[1],oldcost[1]-newcost[0]],
                       strictly_improves=oldcost[0]>newcost[1])
            bills=[]
            for d in ('forward','backward'):
                nc=deepcopy(c); nw=deepcopy(words[d]); i=w['index']; roles=w['roles']
                expected_old=old if d=='forward' else dual(old)
                for ev,op in zip(nw[i:i+2],expected_old):
                    need(ev[0]=='scalar' and ev[1]==['add',['L',roles[op[0]]],['L',roles[op[1]]],op[2],1],
                         'Both-orientation source position binding')
                events=[]
                for op,frame in zip(replacement if d=='forward' else dual(replacement),frames):
                    label=next((j for j,b in enumerate(nc['frames']) if space(tuple(b))==space(tuple(frame))),None)
                    if label is None:label=len(nc['frames']);nc['frames'].append(frame)
                    events.append(['scalar',['add',['L',roles[op[0]]],['L',roles[op[1]]],op[2],1],label])
                nw[i:i+2]=events; actual=full_bill(nw,nc)
                predicted=Counter(BASE_PAID);predicted.subtract(oldp);predicted.update(newp)
                need(+predicted==actual,'Complete invoice versus local delta')
                bills.append(dict(sorted(actual.items())))
            need(bills[0]==bills[1],'Dual bill mismatch')
            row['complete_paid']=bills[0]
        else:row['strictly_improves']=False;row['obstruction']='required common span does not fit exits'
        results.append(row)
    return dict(schema='receiver-window-transfer/v1',status='PASS_BOUNDED_RECEIVER_TRANSFER',
        source_head='b9a13c1673e0e9697de410de16e8bbf3207a7363',self_tests=tests,
        total_eligible_adjacent_pairs=len(candidates),tested_windows=len(chosen),
        certified_positive_windows=sum(r['strictly_improves'] for r in results),
        scale=SCALE,tested_saving=str(C),unchanged_productive_helpers=408,
        windows=results,new_kappa=False,
        not_covered=['global rewrite optimum','physical lowering of any new path','complete native endpoint','compiler and outer transfer'])


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--self-test',action='store_true');ap.add_argument('--write',action='store_true')
    args=ap.parse_args()
    result={'self_tests':self_tests()} if args.self_test else run()
    text=json.dumps(result,indent=2,sort_keys=True)+'\n'
    if args.write:(HERE/'RESULT.json').write_text(text)
    elif not args.self_test and (HERE/'RESULT.json').exists():need(json.loads((HERE/'RESULT.json').read_bytes())==result,'Stored result differs')
    print(text,end='')

if __name__=='__main__':main()

#!/usr/bin/env python3
"""Independent finite-alphabet optimistic ceilings. Apache-2.0; OpenAI assistance.

No construction checker or acceptance function is imported. Geometry is relaxed
only in the direction that can lower cost; optimistic profiles are not circuits.
"""
from collections import Counter
from fractions import Fraction as Q
from functools import lru_cache
from itertools import product
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import sys
import tempfile

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
SCALE=10**18;SAVING=Q('0.00302015')
GATES=tuple((i,j,s) for i in range(3) for j in range(3) if i!=j for s in (-1,1))
IDENTITY=tuple(int(i==j) for i in range(3) for j in range(3))

def need(ok,why):
    if not ok:raise ValueError(why)

def apply(m,g):
    i,j,s=g;out=list(m)
    for k in range(3):out[3*i+k]+=s*m[3*j+k]
    return tuple(out)

@lru_cache(None)
def matching_words(ca,cb):
    target=apply(apply(IDENTITY,(0,2,ca)),(1,2,cb))
    layer=[(IDENTITY,())];found=[];visited=0
    for length in range(5):
        visited+=len(layer)
        found.extend(w for m,w in layer if m==target)
        if length<4:layer=[(apply(m,g),w+(g,)) for m,w in layer for g in GATES]
    need(visited==22621,'Complete length-zero-through-four alphabet')
    return tuple(found)

@lru_cache(None)
def span(basis):
    values={0}
    for v in basis:
        need(type(v) is int and 0<v<512 and v not in values,'Independent binary basis')
        values|={x^v for x in tuple(values)}
    return frozenset(values)

def dim(s):return len(s).bit_length()-1

def sumspace(a,b):return frozenset(x^y for x in a for y in b)

def limits(starts,ends,word):
    if any(not a<=b for a,b in zip(starts,ends)):return None
    current=list(starts);lower=[]
    for i,j,s in word:
        f=sumspace(current[i],current[j]);lower.append(f);current[i]=current[j]=f
    current=list(ends);upper=[None]*len(word)
    for k in reversed(range(len(word))):
        i,j,s=word[k];f=current[i]&current[j];upper[k]=f;current[i]=current[j]=f
    if any(not a<=b for a,b in zip(lower,upper)):return None
    return [(dim(a),dim(b)) for a,b in zip(lower,upper)]

def relaxed_profiles(starts,ends,word):
    bounds=limits(starts,ends,word)
    if bounds is None:return set()
    end=tuple(map(dim,ends));initial=tuple(map(dim,starts));out=set()
    def visit(k,state,h):
        if k==len(word):
            hh=list(h)
            for a,b in zip(state,end):
                need(a<=b,'Relaxed terminal monotonicity')
                if b>a:hh[b-a]+=1
            need(sum(r*n for r,n in enumerate(hh))==sum(end)-sum(initial),'Complete exit rank mass')
            out.add(tuple(hh));return
        i,j,_=word[k];lo,hi=bounds[k]
        for d in range(max(lo,state[i],state[j]),min(hi,end[i],end[j])+1):
            hh=list(h);ss=list(state)
            for role in (i,j):
                gap=d-ss[role]
                if gap:hh[gap]+=1
                ss[role]=d
            visit(k+1,tuple(ss),tuple(hh))
    visit(0,initial,(0,)*10)
    return out

def actual_profile(starts,ends,word,frames):
    state=list(starts);out=[0]*10
    for (i,j,_),f in zip(word,frames):
        for r in (i,j):
            if not state[r]<=f:return None
            gap=dim(f)-dim(state[r]);out[gap]+=int(gap>0);state[r]=f
    for a,b in zip(state,ends):
        if not a<=b:return None
        gap=dim(b)-dim(a);out[gap]+=int(gap>0)
    need(sum(r*n for r,n in enumerate(out))==sum(map(dim,ends))-sum(map(dim,starts)),'Actual cleanup mass')
    return tuple(out)

def logarithm(x):
    e=0
    while x>=2:x/=2;e+=1
    def core(y):
        z=(y-1)/(y+1);p=z;lo=Q(0)
        for k in range(96):lo+=2*p/(2*k+1);p*=z*z
        return lo,lo+2*p/(193*(1-z*z))
    a,b=core(x);c,d=core(Q(2));return a+e*c,b+e*d

def weights():
    out=[(0,0),(SCALE,SCALE)]
    for r in range(2,10):
        a,b=logarithm(Q(r));a*=SAVING;b*=SAVING
        need(0<a<=b<Q(1,100),'Alternating exponential domain')
        def expminus(x):
            term=Q(1);total=Q(1)
            for n in range(1,25):term*=-x/n;total+=term
            return total+term*(-x)/25,total
        lo=r*expminus(b)[0];hi=r*expminus(a)[1]
        out.append(((lo*SCALE).__floor__(),(hi*SCALE).__ceil__()))
    return out

def gain(old,new,w):
    if old==new:return (0,0)
    delta=[a-b for a,b in zip(old,new)]
    return (sum(n*w[r][0 if n>=0 else 1] for r,n in enumerate(delta)),
            sum(n*w[r][1 if n>=0 else 0] for r,n in enumerate(delta)))

def authenticate():
    for r in json.loads((HERE/'SOURCES.json').read_bytes())['files']:
        if r['usage']!='input':continue
        p=ROOT/r['path'];need(p.is_file() and not p.is_symlink(),'Source location')
        b=p.read_bytes();need(hashlib.sha256(b).hexdigest()==r['sha256'],'Source SHA256')
        need(hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==r['git_blob'],'Source blob')

def source():
    authenticate()
    with tempfile.TemporaryDirectory(prefix='ceiling-source-cache-') as cache:
        code="import json,sys;sys.path.insert(0,sys.argv[1]);import native_joint;c,p,b,o,n=native_joint.construct();print(json.dumps({'c':c,'p':p['forward']}))"
        run=subprocess.run([sys.executable,'-I','-B','-X','pycache_prefix='+cache,'-c',code,str(ROOT/'research/joint-helper-lattice')],capture_output=True,check=True,timeout=60)
    return json.loads(run.stdout)

def windows(c,program):
    word=[e for e in program if e[0]!='climb'];state=list(c['start']);phase=None;ordinals=Counter();out=[]
    def roles(e):
        g=e[1];return g[1:3] if g[0] in ('add','copy') else g[1:2]
    for pos,e in enumerate(word):
        if e[0]=='phase':phase=e[1]
        ordinal=ordinals[phase]
        if e[0]=='scalar' and all(r[0]=='L' for r in roles(e)):ordinals[phase]+=1
        if phase in ('B','cleanup_tail') and pos+1<len(word):
            f=word[pos+1]
            if e[0]==f[0]=='scalar' and e[1][0]==f[1][0]=='add':
                g,h=e[1],f[1]
                if all(r[0]=='L' for r in roles(e)+roles(f)):
                    a,x,b,y=g[1][1],g[2][1],h[1][1],h[2][1]
                    ca,cb=Q(*g[3:]),Q(*h[3:])
                    if x==y and len({a,b,x})==3 and ca in (-1,1) and cb in (-1,1):
                        owners=(a,b,x);starts=[span(tuple(c['frames'][state[r]])) for r in owners];ends=[]
                        for r in owners:
                            target=c['final'][r]
                            for later in word[pos+2:]:
                                if later[0]=='scalar' and ['L',r] in roles(later):target=later[2];break
                                if later[0]=='warp' and later[1]==['L',r]:target=later[3];break
                            ends.append(span(tuple(c['frames'][target])))
                        out.append((dict(index=pos,phase=phase,ordinal=ordinal,roles=list(owners),coefficients=[int(ca),int(cb)]),starts,ends,[span(tuple(c['frames'][e[2]])),span(tuple(c['frames'][f[2]]))]))
        if e[0]=='scalar':
            for r in roles(e):
                if r[0]=='L':state[r[1]]=e[2]
        elif e[0]=='warp':state[e[1][1]]=e[4]
    return out

def self_tests():
    counts={}
    for a,b in product((-1,1),repeat=2):
        words=matching_words(a,b);counts[str((a,b))]=len(words)
        need(Counter(map(len,words))=={2:2,3:2,4:80},'Complete exact scalar-word census')
    spaces=[span(()),span((1,)),span((2,)),span((3,)),span((1,2))]
    checked=0
    for word in matching_words(1,-1):
        if len(word)>3:continue
        starts=[spaces[0]]*3;ends=[spaces[-1]]*3;relax=relaxed_profiles(starts,ends,word)
        for fs in product(spaces,repeat=len(word)):
            p=actual_profile(starts,ends,word,fs)
            if p is not None:need(p in relax,'Relaxation excluded an actual path');checked+=1
    p=actual_profile([spaces[0]]*3,[spaces[1]]*3,(),())
    need(p[1]==3 and p!=(0,)*10,'Exit charges may not be omitted')
    need(not relaxed_profiles([span((4,))]*3,[span((1,2))]*3,((0,1,1),)),'Incompatible exits')
    w=weights();need(gain(p,p,w)==(0,0),'Identical invoice is exact equality')
    return dict(word_counts=counts,enumerated_words_per_sign_case=22621,actual_small_paths_checked=checked,
                exit_charge_control=True,incompatible_exit_control=True,exact_equality_control=True)

def run():
    tests=self_tests();data=source();allwindows=windows(data['c'],data['p']);w=weights();results=[]
    for info,starts,ends,oldframes in allwindows[:12]:
        a,b=info['coefficients'];old=actual_profile(starts,ends,((0,2,a),(1,2,b)),oldframes)
        need(old is not None,'Actual source path')
        ps=set();admitted=0
        for word in matching_words(a,b):
            found=relaxed_profiles(starts,ends,word)
            if found:admitted+=1;ps.update(found)
        need(old in ps,'Relaxation includes original source word')
        intervals=[gain(old,p,w) for p in sorted(ps)]
        ceiling=max(hi for lo,hi in intervals)
        results.append({**info,'compatible_words':admitted,'relaxed_profiles':len(ps),
            'optimistic_gain_upper_scaled':ceiling,'certified_no_strict_gain':ceiling<=0,
            'optimistic_positive_profiles':sum(lo>0 for lo,hi in intervals),
            'old_paid':{r:n for r,n in enumerate(old) if n},
            'start_dimensions':list(map(dim,starts)),'exit_dimensions':list(map(dim,ends))})
    return dict(schema='four-shear-window-ceilings/v1',status='PASS_FINITE_ALPHABET_CEILINGS',
        source_head='b9a13c1673e0e9697de410de16e8bbf3207a7363',tested_saving=str(SAVING),scale=SCALE,
        total_eligible_windows=len(allwindows),tested_windows=len(results),windows=results,
        excluded_window_count=sum(r['certified_no_strict_gain'] for r in results),controls=tests,new_kappa=False,
        not_covered=['geometric attainability of relaxed profiles','nonadjacent or larger windows','joint overlapping rewrites','physical native admission','global ceiling or new kappa'])

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--self-test',action='store_true');ap.add_argument('--write',action='store_true');args=ap.parse_args()
    result=self_tests() if args.self_test else run();text=json.dumps(result,indent=2,sort_keys=True)+'\n'
    if args.write:(HERE/'RESULT.json').write_text(text)
    elif not args.self_test and (HERE/'RESULT.json').exists():need(json.loads((HERE/'RESULT.json').read_bytes())==result,'Receipt changed')
    print(text,end='')

if __name__=='__main__':main()

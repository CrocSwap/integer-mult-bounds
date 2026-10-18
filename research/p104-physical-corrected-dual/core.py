"""Exact physical dual construction; finite width-nine charts only."""
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter
from functools import lru_cache
from itertools import combinations, product
import hashlib, json, gzip, types

P = Path(__file__).resolve().parent
ROOT = P.parents[1]
BASE = ROOT / 'research/p104-native-channel'

def need(ok, why):
    if not ok:
        raise ValueError(why)

def authenticate():
    for x in json.loads((P/'SOURCES.json').read_text())['files']:
        if x['usage'] == 'input':
            raw = (ROOT/x['path']).read_bytes()
            need(hashlib.sha256(raw).hexdigest() == x['sha256'], 'source SHA256 '+x['path'])
            need(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest() == x['git_blob'], 'source blob')
    for x in json.loads((P/'PREDECESSORS.json').read_text())['files']:
        raw = (P/x['local']).read_bytes()
        need(hashlib.sha256(raw).hexdigest() == x['sha256'], 'predecessor SHA256')
        need(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest() == x['git_blob'], 'predecessor blob')

def module(filename):
    # Called only after authenticating the entire source set. Execute these
    # bytes directly so timestamp bytecode cannot replace authenticated code.
    path = BASE/'vendor'/filename
    raw = path.read_bytes()
    pin = next(x for x in json.loads((P/'SOURCES.json').read_text())['files'] if x['path'].endswith('/'+filename))
    need(hashlib.sha256(raw).hexdigest() == pin['sha256'], 'immediate executable pin')
    out = types.ModuleType(filename[:-3]);out.__file__ = str(path)
    exec(compile(raw,str(path),'exec'),out.__dict__)
    return out

def canonical(vs):
    piv = {}
    for x in vs:
        while x:
            k = x.bit_length()-1
            if k in piv: x ^= piv[k]
            else: piv[k] = x;break
    for k in sorted(piv):
        for j in piv:
            if j > k and piv[j]>>k&1: piv[j] ^= piv[k]
    return tuple(piv[k] for k in sorted(piv,reverse=True))

@lru_cache(None)
def complement(frame):
    return canonical(x for x in range(512) if all((x&v).bit_count()%2 == 0 for v in frame))

def conjugate(gates):
    out = []
    for e in gates:
        if e[0] == 'C': out.append(('C',e[1],-e[2]))
        elif e[0] == 'D': out.append(('D',tuple(e[1]),tuple(-a%4 for a in e[2])))
        elif e[0] == 'phase': out.append(('phase',-e[1]%4))
        else:
            need(e[0] in ('P','X'), 'conjugate gate type')
            out.append(tuple(e))
    return tuple(out)

def geometry(N):
    roots=[]
    for i,j in combinations(range(8),2):
        for s in (-1,1):
            a=[0]*8;a[i]=2;a[j]=2*s;roots.append(tuple(a))
    roots += [(1,*tail) for tail in product((-1,1),repeat=7) if tail.count(-1)%2 == 0]
    roots.sort()
    iso=json.loads(gzip.decompress((BASE/'NATIVE-RECIPES.json.gz').read_bytes()))['label_isometry']
    dot=lambda a,b:sum(x*y for x,y in zip(a,b))//4
    binary=[sum(((dot(a,b)+1)&1)<<j for j,b in enumerate(roots)) for a in roots]
    labels=[sum(((row>>j)&1)<<k for k,j in enumerate(iso['pivot_root_indices'])) for row in binary]
    gram=[labels[j] for j in iso['pivot_root_indices']]
    need(gram==iso['compressed_gram'], 'compressed Gram binding')
    inverse=N.inverse(tuple(gram));need(list(inverse)==iso['compressed_dual_gram'], 'inverse Gram binding')
    scalar=lambda a,b:(a&N.mul(inverse,b)).bit_count()%2
    orth=iso['orthonormal_basis_compressed']
    need(len(orth)==9 and all(scalar(a,b)==int(i==j) for i,a in enumerate(orth) for j,b in enumerate(orth)), 'orthonormality')
    cv=lambda x:sum(scalar(x,v)<<j for j,v in enumerate(orth))
    physical=list(map(cv,labels))
    need(physical==iso['physical_root_labels'], 'physical root label binding')
    need(all((a&b).bit_count()%2 == ((binary[i]>>j)&1) for i,a in enumerate(physical) for j,b in enumerate(physical)), '14400 pairings')
    f=json.loads((BASE/'inputs/P104-FIXTURE.json').read_text())['section4_explicit_P104']
    removed={tuple(x) for x in f['F0']+f['C']}
    ports=[x for x in roots if x not in removed]
    need(len(ports)==104,'P104 ports')
    return lambda vs:canonical(map(cv,vs)), ports

def build_word(cv):
    source=json.loads((P/'inputs/CLEAN-DUAL.json').read_text())
    old_initial={r:cv(f) for r,f in source['initial_frames'].items()}
    old_final={r:cv(f) for r,f in source['final_frames'].items()}
    initial=old_final;final=old_initial
    middle_initial={r:complement(f) for r,f in old_initial.items()}
    middle_final={r:complement(f) for r,f in old_final.items()}
    program=[]
    def edge(r,a,b):
        if a!=b: program.append(['transport',r,list(a),list(b),abs(len(a)-len(b))])
    for r in initial: edge(r,initial[r],middle_initial[r])
    for event in source['program']:
        e=list(event)
        if e[0]=='transport':
            e[2]=list(complement(cv(e[2])));e[3]=list(complement(cv(e[3])))
            if e[1]!='C':need(canonical(e[2]+e[3])==tuple(e[3]) and len(e[2])<len(e[3]),'increasing persistent middle path')
        elif e[0] in ('zero','erase'): e[2]=list(complement(cv(e[2])))
        elif e[0]=='add': e[4]=list(complement(cv(e[4])))
        elif e[0]=='sign': e[3]=list(complement(cv(e[3])))
        else: raise ValueError('source event '+e[0])
        program.append(e)
    for r in final: edge(r,middle_final[r],final[r])
    return dict(schema_version=1,chart='Delta_W = conjugate(Gamma_W) = Gamma_W^(-T)',initial_frames={r:list(f) for r,f in initial.items()},final_frames={r:list(f) for r,f in final.items()},program=program)

def replay(word,ports,dense=False):
    names=list(word['initial_frames']);frames={r:canonical(f) for r,f in word['initial_frames'].items()}
    scale=65536
    rows={r:([scale*int(r==s) for s in names] if dense else {r:Q(1)}) for r in names}
    profile=Counter();counts=Counter();erases=[]
    for i,e in enumerate(word['program']):
        op,r=e[:2];counts[op]+=1
        if op=='transport':
            a,b=canonical(e[2]),canonical(e[3]);need(frames[r]==a,'transport entry')
            need(canonical(a+b) in (a,b) and abs(len(a)-len(b))==e[4]>0,'nested transport')
            frames[r]=b;profile[e[4]]+=1
        elif op=='zero':
            need(r=='C' and r not in rows,'private fresh zero')
            rows[r]=[0]*len(names) if dense else {};frames[r]=canonical(e[2])
        elif op=='erase':
            need(r=='C' and frames[r]==canonical(e[2]),'erase frame')
            need(not any(rows[r]) if dense else not rows[r],'exact zero private erase')
            erases.append(i);del rows[r],frames[r]
        elif op=='sign':
            need(e[2]=='-1' and frames[r]==canonical(e[3]),'sign frame')
            rows[r]=[-x for x in rows[r]] if dense else {s:-x for s,x in rows[r].items()}
        else:
            need(op=='add','event type');_,r,s,c,f=e;c=Q(c)
            need(r!=s and frames[r]==frames[s]==canonical(f),'ADD common chart')
            if dense:
                need(all((x*c.numerator)%c.denominator==0 for x in rows[s]),'integer corroboration scaling exact')
                rows[r]=[a+b*c.numerator//c.denominator for a,b in zip(rows[r],rows[s])]
            else:
                for s2,x in list(rows[s].items()):
                    z=rows[r].get(s2,Q(0))+c*x
                    if z:rows[r][s2]=z
                    else:rows[r].pop(s2,None)
    need(set(rows)==set(names) and frames=={r:canonical(f) for r,f in word['final_frames'].items()},'persistent boundary')
    for r in names:
        want={r:Q(1)}
        if r.startswith('X'):
            s=int(r[1:])
            for t,a in enumerate(ports):
                c=Q(int(t==s)) if t<2 else Q(sum(x*y for x,y in zip(a,ports[s])),8)
                if c:want['Y'+str(t)]=-c
        need(rows[r]==([want.get(s,0)*scale for s in names] if dense else want),'all logical endpoint coefficients '+r)
    return dict(events=sum(counts.values()),counts=dict(sorted(counts.items())),profile=dict(sorted(profile.items())),rank_mass=sum(k*v for k,v in profile.items()),private_zero_erases=erases,boundary_coefficients=len(names)**2)

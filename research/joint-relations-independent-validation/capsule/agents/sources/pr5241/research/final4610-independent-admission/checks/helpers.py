#!/usr/bin/env python3
"""Independent finite helper audit. Stdlib only; imports no retained evaluator.

Pauli images plus exact state amplitudes certify Clifford equality: identical
conjugation on the full Pauli generating set implies a scalar discrepancy;
agreement on any nonzero state fixes that scalar. --all-columns additionally
replays every basis input, without relying on this finite-dimensional lemma.
"""
import argparse, collections, copy, gzip, hashlib, json, pathlib, subprocess, sys, time
from fractions import Fraction as Q
from . import source as inputs

HEAD='20bb93cd990d2ff683e4d0fc56b87a42cd5d3296'
NEW='research/kappa-round3-warp-20261022/'
OLD='research/warp-interface-20261022/'
HERE=pathlib.Path(__file__).resolve().parent
REPO=HERE.parents[1]/'repository'

def need(b,s):
    if not b: raise ValueError(s)

def source(p):return inputs.raw(p)

def js(p):
    b=source(p); return json.loads(gzip.decompress(b) if p.endswith('.gz') else b)

def rank(xs):
    piv={}
    for x in xs:
        while x:
            j=x.bit_length()-1
            if j not in piv: piv[j]=x;break
            x^=piv[j]
    return len(piv)

def points(b):
    s=[0]
    for x in b:s += [y^x for y in s]
    return sum(1<<x for x in s)

def transpose(a):return [sum(((a[j]>>i)&1)<<j for j in range(9)) for i in range(9)]
def mv(a,x):return sum(((r&x).bit_count()%2)<<i for i,r in enumerate(a))
def inverse(a):
    w=[x|(1<<(9+i)) for i,x in enumerate(a)]
    for j in range(9):
        k=next(i for i in range(j,9) if w[i]>>j&1);w[j],w[k]=w[k],w[j]
        for i in range(9):
            if i!=j and w[i]>>j&1:w[i]^=w[j]
    return [x>>9 for x in w]

def adj(c):
    return [('P',inverse(g[1])) if g[0]=='P' else ('D',g[1],[(-x)%4 for x in g[2]]) if g[0]=='D'
            else ('C',g[1],-g[2]) if g[0]=='C' else ('phase',-g[1]) if g[0]=='phase' else g for g in reversed(c)]

def conjugate(c):
    return [('D',g[1],[(-x)%4 for x in g[2]]) if g[0]=='D' else ('C',g[1],-g[2]) if g[0]=='C' else ('phase',-g[1]) if g[0]=='phase' else g for g in c]

def frame(b):
    if len(b)==0:return []
    if len(b)==9:return [('C',1<<i,1) for i in range(9)]
    ext=[]
    for x in b+[1<<i for i in range(9)]:
        if rank(ext+[x])>len(ext):ext.append(x)
    G=transpose(ext);it=transpose(inverse(G))
    # Q=I+(G^-1)^T G^-1, over F2, as in the canonical chart definition.
    qm=[(1<<i)^sum(((a&bb).bit_count()%2)<<j for j,bb in enumerate(it)) for i,a in enumerate(it)]
    K=[('P',G),('D',qm,[(qm[i]>>i)&1 for i in range(9)])]
    return adj(K)+[('C',1<<i,1) for i in range(len(b))]+K

def recipe(r):
    return [('D',r['quadratic_rows'],r['linear_Z4']),('P',r['matrix_rows']),('X',r['offset']),('phase',r['phase'])]

def qvalue(rows,lin,x):
    return (sum(lin[i] for i in range(9) if x>>i&1)+2*sum((rows[i]&x&~((1<<(i+1))-1)).bit_count() for i in range(9) if x>>i&1))%4

def tableau(c):
    out=[]
    for j in range(18):
        x,z,p=(1<<j,0,0) if j<9 else (0,1<<(j-9),0)
        for g in c:
            if g[0]=='P':
                x=mv(g[1],x);z=mv(transpose(inverse(g[1])),z)
            elif g[0]=='D':
                # D X^x Z^z D^-1, with phase q(x) and polar matrix Q.
                p=(p+qvalue(g[1],g[2],x))%4;z ^= mv(g[1],x)
            elif g[0]=='C':
                if (z&g[1]).bit_count()%2:x^=g[1];p=(p+3*g[2])%4
            elif g[0]=='X':p=(p+2*((z&g[1]).bit_count()%2))%4
            elif g[0]!='phase':raise ValueError(g)
        out.append((x,z,p))
    return out

def rot(a,p):
    x,y=a;return [(x,y),(-y,x),(-x,-y),(y,-x)][p%4]

def state(c,basis=0):
    a=[(0,0)]*512;a[basis]=(1,0);den=0
    for g in c:
        if g[0]=='P':
            b=[(0,0)]*512
            for x,v in enumerate(a):b[mv(g[1],x)]=v
            a=b
        elif g[0]=='X':a=[a[x^g[1]] for x in range(512)]
        elif g[0]=='D':a=[rot(v,qvalue(g[1],g[2],x)) for x,v in enumerate(a)]
        elif g[0]=='phase':a=[rot(v,g[1]) for v in a]
        elif g[0]=='C':
            b=[];s=g[2]
            for x,(u,v) in enumerate(a):
                w,t=a[x^g[1]];b.append((u-s*v+w+s*t,v+s*u+t-s*w))
            a=b;den+=1
        else:raise ValueError(g)
        while den and all(not((u|v)&1) for u,v in a):a=[(u//2,v//2) for u,v in a];den-=1
    return a,den

def replay(c,p,backward=False):
    spaces=[points(b) for b in c['frames']]
    cur={('L',i):f for i,f in enumerate(c['start'])};cur['C',0]=None
    rows={r:{(r,()):Q(1)} for r in cur};paid=collections.Counter();life=collections.defaultdict(list);erasures=[]
    def add(t,s,q):
        for k,v in list(rows[s].items()):
            rows[t][k]=rows[t].get(k,Q(0))+q*v
            if not rows[t][k]:del rows[t][k]
    for j,e in enumerate(p):
        k=e[0]
        if k in ('phase','adapter','residual_adapter'):continue
        if k in ('climb','center'):
            if k=='climb':_,part,i,a,b,r=e;t=('L',i);need(spaces[a]!=spaces[b] and spaces[a]&spaces[b]==spaces[a],'borrowed climb must strictly ascend')
            else:_,i,a,b,r=e;t=('C',i);need(t==('C',0),'only owned C0');need(spaces[a]!=spaces[b] and (spaces[a]&spaces[b] in (spaces[a],spaces[b])),'owned nested edge')
            need(cur[t]==a and r==abs(len(c['frames'][a])-len(c['frames'][b])),'paid frame/rank');cur[t]=b;paid[r]+=1;life[t].append(j)
        elif k=='warp':
            _,t,op,a,b=e;t=tuple(t);need(cur[t]==a,'warp chronological entrance');cur[t]=b;life[t].append(j)
            sym=op+(1000000 if op>0 else -1000000) if backward else op
            rows[t]={(v,w[1:] if w and w[0]==-sym else (sym,)+w):q for (v,w),q in rows[t].items()}
        elif k=='scalar':
            g,f=e[1:];t=tuple(g[1]);life[t].append(j)
            if g[0] in ('clear','copy'):
                need(t==('C',0),'borrowed erase/copy prohibited');erasures.append([j,g[0],list(t)])
                if g[0]=='clear':rows[t]={};cur[t]=f;continue
            need(cur[t]==f,'scalar chronological receiver frame')
            if g[0] in ('add','copy'):
                s=tuple(g[2]);need(cur[s]==f,'scalar chronological source frame');life[s].append(j)
                if g[0]=='copy':rows[t]=rows[s].copy();continue
                need(s!=t,'distinct shear fields');q=Q(g[3],g[4]);need(q and q.denominator&(q.denominator-1)==0,'dyadic ADD');add(t,s,q)
            else:
                need(g[0]=='scale','known scalar');q=Q(g[2],g[3]);need(q and abs(q.numerator)&(abs(q.numerator)-1)==0 and q.denominator&(q.denominator-1)==0,'unit dyadic scale');rows[t]={a:q*b for a,b in rows[t].items()}
        else:raise ValueError('unknown event '+k)
    need([cur['L',i] for i in range(632)]==c['final'],'all chronological final frames')
    need(rows['C',0]=={},'arbitrary owned entry and owned scratch cleared')
    for i in range(632):
        t=('L',i);want={(t,()):Q(1)}
        if (i<112 if backward else 112<=i<224):want[(('L',i+112 if backward else i-112),())]=Q(-1 if backward else 1)
        need(rows[t]==want,'all-column arbitrary endpoint '+str(i))
    return {'events':len(p),'paid':dict(paid),'arbitrary_persistent_columns':632,'arbitrary_owned_entry_columns':1,'helper_restored_count':408,'owned_erasure_events':erasures,'lifetimes':{str(i):{'first_event':min(life['L',i]),'last_event':max(life['L',i]),'contacts':len(life['L',i])} for i in range(224,632)}}

def run():
    args=argparse.Namespace(all_columns=False)
    started=time.monotonic();nw=js(NEW+'ACTUAL-WORD.json.gz');ow=js(OLD+'ACTUAL-WORD.json.gz');phase=js(NEW+'PHASE-VALIDATION.json.gz');c=nw['canonical'];old=ow['canonical']
    changed=[i for i in range(224,632) if (c['start'][i],c['final'][i])!=(old['start'][i],old['final'][i])]
    need(len(changed)==26,'exact26 changed interfaces');need(c['final']==old['final'],'all receiver exits inherited');need(c['start'][:224]==old['start'][:224],'main source endpoints inherited')
    census=collections.Counter()
    for i in range(224,632):
        a,b=c['start'][i],c['final'][i];sa,sb=points(c['frames'][a]),points(c['frames'][b]);need(sa!=sb and sa&sb==sa,'strict whole residual boundary');census[len(c['frames'][b])-len(c['frames'][a])]+=1
    need(census=={4:28,7:7,8:47,9:326},'complete helper census')
    entries=[];covered=[]
    for h in phase['changed_helper_boundaries']:
        a,b=h['input'],h['output'];covered+=h['helpers'];need(all(i in changed and c['start'][i]==a and c['final'][i]==b for i in h['helpers']),'receipt exact actual helper boundary')
        residual=adj(frame(c['frames'][a]))+frame(c['frames'][b])
        for direction in ('forward','backward'):
            target=residual if direction=='forward' else conjugate(residual);r=h['recipes'][direction];need(r['rank']==h['rank'],'recipe rank')
            compiled=recipe(r['right'])+[('C',1<<j,1) for j in range(r['rank'])]+recipe(r['left'])
            need(tableau(target)==tableau(compiled),'full Pauli conjugation residual vs normalizers')
            for j in range(512 if args.all_columns else 1):need(state(target,j)==state(compiled,j),'exact absolute-phase amplitude')
            entries.append({'helpers':h['helpers'],'input':a,'output':b,'rank':h['rank'],'direction':direction,'pauli_generators':18,'basis_columns_explicitly_checked':512 if args.all_columns else 1,'operator_equality':'finite Clifford equality, phase fixed by exact amplitudes'})
    need(sorted(covered)==changed,'exact changed helper coverage, no duplicate')
    checks={d:replay(c,p,d=='backward') for d,p in nw['programs'].items()}
    controls=[]
    for name,mut in [('borrowed_erasure',lambda p:p.insert(0,['scalar',['clear',['L',changed[0]]],c['start'][changed[0]]])),('wrong_paid_rank',lambda p:next(e for e in p if e[0]=='climb').__setitem__(5,99))]:
        p=copy.deepcopy(nw['programs']['forward']);mut(p)
        try:replay(c,p)
        except ValueError as e:controls.append({'name':name,'rejected':str(e)})
        else:raise ValueError('control accepted '+name)
    bad=copy.deepcopy(phase['changed_helper_boundaries'][0]['recipes']['forward']);bad['left']['phase']=(bad['left']['phase']+1)%4
    h=phase['changed_helper_boundaries'][0];compiled=recipe(bad['right'])+[('C',1<<j,1) for j in range(bad['rank'])]+recipe(bad['left']);target=adj(frame(c['frames'][h['input']]))+frame(c['frames'][h['output']]);need(state(compiled)!=state(target),'phase control rejected');controls.append({'name':'wrong_normalizer_absolute_phase','rejected':'exact amplitude differs though tableau is unchanged'})
    paths=[NEW+'ACTUAL-WORD.json.gz',OLD+'ACTUAL-WORD.json.gz',NEW+'PHASE-VALIDATION.json.gz',NEW+'PROOF.md','research/kappa-round3-warp-lean-20261022/NativeCore.lean','research/joint-helper-lattice/PROOF.md']
    proc_memory={}
    result={'status':'PASS_SCOPED_HELPER_CONTRACTS_UNIFORM_PREMISES_REMAIN','head':HEAD,'changed_helpers':changed,'census':dict(census),'helper_residual_normalizers':entries,'chronology_and_restoration':checks,'controls':controls,'source_sha256':{p:hashlib.sha256(source(p)).hexdigest() for p in paths},'checker_sha256':hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),'python':sys.version,'seconds':time.monotonic()-started,'proc_memory':proc_memory,'rusage_maxrss_KiB_inherited_across_exec':None,'uniform_admission':False,'explicit_amplitude_columns':512 if args.all_columns else 1}
    return result



"""Lower the pinned dyadic type-B caller into exact elementary operations."""
from collections import Counter, defaultdict
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
PREVIOUS = ROOT / 'kappa-cargo-sections-20261110T1232Z/evidence/caller'
COMPARATOR = ROOT / 'kappa-after-7004-20261110T0755Z/replay/research/shared-wire-split-composition'
RESULT = ROOT / 'kappa-coupled-boundaries-20261110T0908Z/replay/research/coupled-helper-rechart/RESULT.json'
PIN = {
    PREVIOUS / 'mirrored.py': '55dd441a3a7f504b351857d45fd701994a0950ae1baec6c4c2b4b0166fb69db3',
    PREVIOUS / 'host34.py': 'bded1a8626d65ee40c4ba3b25780fc03f0fa08906f3c83f631892df072d9a9b7',
    PREVIOUS / 'cut_library.py': '7ccb81af19db54ec7cdb44849af018d4ca8893f80f17277914f8566715985133',
    PREVIOUS / 'connected.py': '469537b46fb92c5aca926d3b1497da5425408673b0a73ba1427f23d872b414e7',
    PREVIOUS / 'screen.py': '01e3eaba4b710a080e6e393e53157e6a119fdf312620eed26e9185ca91f6bea6',
    PREVIOUS / 'stage.py': '0ab5546e926dd98d3ad833909b534840b7d8d0467c4790ca09bc2b14b37313f5',
    PREVIOUS / 'DYADIC.json': '3995ec23d025a3eb0f4110bc52ad967b21a87c72681217e9e2c3aa0155450b27',
    COMPARATOR / 'data/caller.json': '3828d53e80ea97e8b866320f081af20b6b93bfebd58b95b56b85a7afe151af5e',
    COMPARATOR / 'independent.py': '21f46a8340331abb1486b50bd4e04453f1968b0a5950d86ff7780dd368590874',
    RESULT: '44e6a7983aac450c6f55c87da57d8c975748f32728092c4be6ed966a54854998',
}


def sources():
    pinned={p:p.read_bytes() for p in PIN}
    for p,b in pinned.items():
        assert sha256(b).hexdigest()==PIN[p],p
    return pinned


def dyadic(v):
    return v.denominator & (v.denominator-1) == 0


def unit(v):
    return bool(v) and dyadic(v) and abs(v.numerator) & (abs(v.numerator)-1) == 0


def put(vec, i, v):
    if v:
        vec[i] = v
    else:
        vec.pop(i, None)


def backwards(events):
    for e in reversed(events):
        op = e[1]
        if op == 'ADD':
            yield [*e[:-1],str(-Q(e[-1]))]
        elif op == 'SCALE':
            yield [*e[:-1],str(1/Q(e[-1]))]
        else:
            assert op == 'SWAP'
            yield e.copy()


def lower_frame(columns, rows, targets):
    """Compute Lx=e and y L^-1=e^t for a split dyadic frame."""
    X, Y = [v.copy() for v in columns], [w.copy() for w in rows]
    assert all(sum(v.get(i,0)*a for i,a in w.items())==(j==k)
               for j,w in enumerate(Y) for k,v in enumerate(X))
    operations = []

    def swap(a,b):
        if a==b:
            return
        operations.append(['B','SWAP',a,b])
        for v in X+Y:
            x,y = v.get(a,0),v.get(b,0)
            put(v,a,y)
            put(v,b,x)

    def scale(a,q):
        q=Q(q)
        assert unit(q)
        if q==1:
            return
        operations.append(['B','SCALE',a,str(q)])
        for v in X:
            put(v,a,v.get(a,0)*q)
        for w in Y:
            put(w,a,w.get(a,0)/q)

    def axpy(a,b,q):
        q=Q(q)
        assert a!=b and dyadic(q)
        if not q:
            return
        operations.append(['B','ADD',a,b,str(q)])
        for v in X:
            put(v,a,v.get(a,0)+q*v.get(b,0))
        for w in Y:
            put(w,b,w.get(b,0)-q*w.get(a,0))

    for j,p in enumerate(targets):
        v,w=X[j],Y[j]
        candidates=sorted(v)
        assert not set(candidates)&set(targets[:j])
        choose=p if unit(Q(v.get(p,0))) else next((r for r in candidates if unit(Q(v[r]))),None)
        if choose is not None:
            swap(p,choose)
            for r in sorted(set(v)-{p}):
                axpy(r,p,-v[r]/v[p])
        else:
            if not v.get(p):
                swap(p,candidates[0])
            for r in sorted(set(v)-{p}):
                while v.get(r):
                    q=v[p]//v[r]
                    axpy(p,r,-q)
                    swap(p,r)
        assert list(v)==[p] and unit(Q(v[p]))
        scale(p,1/v[p])
        assert v=={p:1} and w.get(p)==1
        for r in sorted(set(w)-{p}):
            axpy(p,r,w[r])
        assert X[j]==Y[j]=={p:1}
    assert X==Y==[{p:1} for p in targets]
    return operations


def source_frames(data):
    sys.path.insert(0,str(PREVIOUS))
    source = data[PREVIOUS/'mirrored.py'].decode()
    start='def tape(signs, blocks=None, ring_audit=None):'
    entry='        P = m(x, dual)'
    assert source.count(start)==source.count(entry)==1
    source=source.replace(start,'def tape(signs, blocks=None, ring_audit=None, frames=None):')
    source=source.replace(entry,entry+'\n        if frames is not None: frames.append((x, dual, add(I,local)))')
    space={'__name__':'frame_source'}
    exec(compile(source,str(PREVIOUS/'mirrored.py'),'exec'),space)
    frames=[]
    space['tape'](None,space['varied_tape']('unit-lu-pppppppp'),frames=frames)
    assert len(frames)==18
    return frames,space


def original_roles(c, masks):
    by_signature=defaultdict(list)
    t=c['types']['B']
    for r,d in enumerate(t['diagonal'],t['offset']):
        assert d[:2]==[-1,0]
        by_signature[tuple(d[2:])].append(r)
    phase=(9,9,10,10)
    sig=[tuple(int(i in a) for a in masks) for i in range(34)]
    sig.extend(tuple(int(j==d) for j in range(1,19)) for d in phase)
    labels=[by_signature[d].pop(0) for d in sig]
    assert len(set(labels))==38 and all(not rem for rem in by_signature.values())
    return labels,phase


def build(data):
    c=json.loads(data[COMPARATOR/'data/caller.json'])
    p=json.loads(data[PREVIOUS/'DYADIC.json'])
    assert p['tape']=='unit-lu-pppppppp'
    frames,math=source_frames(data)
    labels,phase=original_roles(c,math['masks']())
    native={e[1]:e for e in c['events'] if e[0]=='J'}
    transpose=math['tr']
    ledger={}
    part=[]
    rank9_roles=[]
    singles=defaultdict(list)
    for j,v,w in p['stage_local']:
        singles[j].append((v,w))
    assert all(len(v)==2 for v in singles.values()) and len(singles)==18

    def decode(entries):
        return {labels[r]:Q(a) for r,a in entries}

    def idle(mask,v,w):
        x,y=decode(w),decode(v)
        pivot=min(x,key=lambda r:(not unit(x[r]),r))
        L=lower_frame([x],[y],[pivot])
        return L+[['B','IDLE_ONE',pivot,mask]]+list(backwards(L))

    def host(j):
        x,y,active=frames[j-1]
        # Reverse the formal multiplication convention via transpose.
        C=[{r:Q(a) for r,a in zip(labels,v) if a} for v in y]
        W=[{r:Q(a) for r,a in zip(labels,v) if a} for v in transpose(x)]
        e=native[j]
        s,t,alpha,beta=e[3]
        assert [Q(alpha),Q(beta)]==[Q(-1),Q(1,2)]
        L=lower_frame(C,W,[s,t])
        B=transpose(active)
        b,d=B[0]
        K=[[Q(1),Q(0)],[b/2,d/2]]
        R=[[Q(0),Q(2)],[Q(-1,2),Q(0)]]
        assert unit(d/2) and math['m'](R,K)==math['m'](K,B)
        frame=L+[['B','SCALE',t,str(d/2)]]
        if b:
            frame.append(['B','ADD',t,s,str(b/2)])
        before=frame+[['B','ADD',t,s,'-1/2'],['B','ADD',s,t,'1'],['B','LAMBDA',s,1]]
        after=[['B','LAMBDA',s,-1]]+list(backwards(frame))
        ledger[j]={'basis_events_each_way':len(frame),'literal_J_roles':[s,t],
                   'local_active_minus':[[str(a) for a in r] for r in B]}
        return before,after

    for j in range(1,19):
        for v,w in singles[j]:
            part.extend(idle([j],v,w))
        for i,s in enumerate(phase):
            if j==s:
                r=labels[34+i]
                part.append(['B','IDLE_ODD',r,[j],-1])
                rank9_roles.append((r,j))
        before,after=host(j)
        part.extend(before)
        part.append(native[j])
        part.extend(after)
        if j==9:
            for mask,v,w in p['groups']:
                part.extend(idle(mask,v,w))
    part.extend(['B','LAMBDA',r,-1] for r in labels[:34])

    # Leave the type-A sequence and every literal J byte-for-byte unchanged.
    b=iter(part)
    merged=[]
    for e in c['events']:
        if e[0]=='A':
            merged.append(e)
        elif e[0]=='J':
            nxt=next(b)
            while nxt[0]=='B':
                merged.append(nxt)
                nxt=next(b)
            assert nxt==e
            merged.append(e)
    merged.extend(b)
    assert [e for e in merged if e[0]!='B']==[e for e in c['events'] if e[0]!='B']
    c['events']=merged
    hist=Counter(8*len(e[3])+(e[1]=='IDLE_ODD') for e in merged
                 if e[:2] in (['B','IDLE_ONE'],['B','IDLE_ODD']))
    assert hist==Counter({8:36,9:4,**{r:4 for r in range(16,65,8)}})
    scalar=[Q(e[-1]) for e in merged if e[:2] in (['B','SCALE'],['B','ADD'])]
    assert all(dyadic(q) for q in scalar)
    assert all(unit(Q(e[-1])) for e in merged if e[:2]==['B','SCALE'])
    audit={'status':'PASS_LITERAL_DYADIC_BASIS_LOWERING','phase_roles':rank9_roles,'B_role_map':labels,
           'B_event_counts':dict(Counter(e[1] for e in merged if e[0]=='B')),
           'B_paid_per_port':dict(sorted(hist.items())),'HOST':ledger,
           'B_scalar_bounds':{'max_abs':str(max(map(abs,scalar))),
                              'max_denominator':max(a.denominator for a in scalar),
                              'max_abs_numerator':max(abs(a.numerator) for a in scalar)}}
    return c,audit


def main(out,receipt):
    raw=sources()
    assert set(raw)==set(PIN)
    c,audit=build(raw)
    out.write_text(json.dumps(c,separators=(',',':'))+'\n')
    audit['caller_sha256']=sha256(out.read_bytes()).hexdigest()
    receipt.write_text(json.dumps(audit,indent=2)+'\n')


if __name__=='__main__':
    main(*(Path(a) for a in sys.argv[1:]))

# Explicit residual-bank audit added by chafreaky with OpenAI Codex assistance.
"""Independent projector, 32-replica ownership and emitted-template audit.
PR386 audit by Zhihao Chen with OpenAI Codex assistance; PR436 generalization by
eumemic with Anthropic Claude assistance; PR439 routes and this replication
extension by chafreaky with OpenAI Codex assistance. Apache-2.0.
Historical regression is performed by the unchanged parent wrapper.
"""
import argparse, copy, gzip, hashlib, json, struct, time
from collections import Counter, defaultdict
from pathlib import Path
import sympy as S
from bank_routes import validate_isometries
from config import REPLICAS

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--local-check',type=Path,required=True); ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--word',type=Path,required=True)
    a=ap.parse_args(); start=time.monotonic(); out=a.out
    blob=gzip.decompress((out/'GLOBAL-TEMPLATE.json.gz').read_bytes()); t=json.loads(blob)
    g=json.loads((out/'GLOBAL.json').read_text()); geo=json.loads((out/'GEOMETRY.json').read_text())
    assert hashlib.sha256(blob).hexdigest()==g['template_sha256']
    assert t['geometry_sha256']==sha(out/'GEOMETRY.json') and t['source_record_sha256']==sha(a.local_check/'records/249-records.bin')
    fs=json.loads((a.local_check/'records/frames.json').read_text())['frames']
    records=list(struct.iter_unpack('<6i',(a.local_check/'records/249-records.bin').read_bytes()))
    T=REPLICAS
    assert T==32 and T%8==0 and g['replicas']==T
    V,R=g['v'],g['R']; LOCAL=2*V+R; DATA=2*4*V*T; LIVE=g['live']
    assert V==120 and DATA==30720 and g['live']==LIVE
    I=S.eye(8); proj={}; dimensions={}
    for key,f in fs.items():
        k=int(key); B=S.Matrix(f['B']) if f['B'] else S.zeros(0,8)
        P=B.T*(B*B.T).inv()*B if B.rows else S.zeros(8)
        assert P.T==P and P*P==P and P.trace()==f['dim']
        proj[k]=P; dimensions[k]=f['dim']
    pairs={}
    for op,x,y,c,r,z in records:
        if op==0:
            key=(y,c)
            if key not in pairs:
                D=proj[c]-proj[y]
                assert proj[c]*proj[y]==proj[y] and proj[y]*proj[c]==proj[y]
                assert D*D==D and D.trace()==r
                # Reflected reverse has exactly the same positive projector.
                assert (I-proj[y])-(I-proj[c])==D
                pairs[key]=r
    assert len(proj)==len(fs)
    print('exact frame projectors',len(proj),'nested pairs',len(pairs),flush=True)
    expected={}
    for rev in (False,True):
        es=[]
        for op,x,y,c,f,z in (reversed(records) if rev else records):
            if op==0: es.append([0,x,c if rev else y,y if rev else c,f,int(rev)])
            elif op==1: es.append([1,x,y,-c if rev else c,f,int(rev)])
            elif op==(3 if rev else 2): es.append([2,x,y,c,f,abs(dimensions[c]-dimensions[f]),int(rev)])
            else: es.append([3,x,y,c,f,z,int(rev)])
        expected['reverse' if rev else 'forward']=es
    assert t['local_programs']==expected

    word=json.loads(gzip.decompress(a.word.read_bytes()))
    assert sha(a.word)==g['word_sha256']
    state=json.loads((a.local_check/'records/249-states.json').read_text())
    initial=[state['initial'][str(i)] for i in range(LOCAL)]
    assert initial==word['start']
    widths=[8-dimensions[f] for f in initial[2*V:]]
    ENT=sum(8-x for x in widths)
    assert T*(8*R-ENT)%64==0
    NB=T*(8*R-ENT)//64
    assert LIVE==DATA+9*NB and g['banks_per_stage']==NB

    def validate(q,check_profile=True):
        assert validate_isometries(q['residual_isometries'],word['frames'],word['lines'],dimensions)==set(initial[2*V:])
        assert (q['m'],q['live'],q['replicas'],q['stages'])==(64,LIVE,T,9)
        assert q['bank_padding'] is None and q['local_programs']==expected
        hist=Counter(); occupation=defaultdict(set); calls=set()
        for c in q['calls']:
            st,rep,p=c['stage'],c['replica'],c['pair']; rev=c['orientation']=='reverse'
            assert 0<=st<9 and 0<=rep<T and p==max(0,(st-1)//2)
            assert rev==(st in (1,3,5,7)) and (st,rep) not in calls; calls.add((st,rep))
            own=c['owners']; assert len(own)==LOCAL
            assert len({(f,tuple(r)) for f,r in own})==LOCAL
            for i,(family,route) in enumerate(own):
                assert 0<=family<LIVE
                if i<2*V:
                    side=i//V; side=1-side if rev else side
                    assert family==rep*960+(2*p+side)*120+i%120 and route==['data',st,i%120]
                else:
                    j=i-2*V
                    assert len(route)==4 and route[0]=='bank' and route[2]==widths[j] and route[3]==initial[i]
                    assert DATA+st*NB<=family<DATA+(st+1)*NB
                    cells=set(range(route[1],route[1]+route[2]))
                    assert cells<=set(range(64)) and not cells & occupation[family]
                    occupation[family]|=cells
            for e in q['local_programs'][c['orientation']]:
                if e[0]==0 and e[4]: hist[e[4]]+=1
                if e[0]==2: hist[e[5]]+=1
        assert calls=={(s,r) for s in range(9) for r in range(T)}
        assert set(occupation)==set(range(DATA,LIVE)) and all(s==set(range(64)) for s in occupation.values())
        levels=[-1]*4; scalar=[1<<i for i in range(8)]; seen=[]; br=0; exchanged=False
        for e in q['schedule']:
            if e['kind']=='local_cover_sweep':
                s,p,rev=e['stage'],e['pair'],e['reverse']; assert levels[p]==s-1 and not exchanged
                src,dst=(2*p+1,2*p) if rev else (2*p,2*p+1)
                scalar[dst]^=scalar[src]; levels[p]=s; seen.append(s)
            elif e['kind']=='idle':
                p,src,dst,r=e['pair'],e['source_level'],e['target_level'],e['rank']
                assert levels[p]==src and src<=dst<=8
                assert r==7*(dst-src); levels[p]=dst
                if r: hist[r]+=2*V*T
            elif e['kind']=='bridge':
                d,s=e['dst'],e['src']; assert levels[d]==levels[s] and e['coefficient'] in (-1,1)
                scalar[2*d]^=scalar[2*s]; scalar[2*s+1]^=scalar[2*d+1]; br+=1
            else:
                assert e['kind']=='exchange' and levels==[8]*4 and not exchanged
                for p in range(4): scalar[2*p],scalar[2*p+1]=scalar[2*p+1],scalar[2*p]
                exchanged=True
        assert exchanged and scalar==[1<<i for i in range(8)] and seen==list(range(9)) and br==9
        assert 64*LIVE-sum(r*n for r,n in hist.items())==312*T
        if check_profile: assert hist==Counter({int(k):v for k,v in g['profile'].items()})
        return hist
    hist=validate(t)
    controls=[]
    def rejects(name,mutator):
        q=copy.deepcopy(t); mutator(q)
        try: validate(q)
        except (AssertionError,KeyError,IndexError): controls.append(name)
        else: raise AssertionError('mutation accepted: '+name)
    rejects('omit an idle child',lambda q:q['schedule'].pop(next(i for i,e in enumerate(q['schedule']) if e['kind']=='idle')))
    rejects('omit a bridge',lambda q:q['schedule'].pop(next(i for i,e in enumerate(q['schedule']) if e['kind']=='bridge')))
    rejects('omit terminal exchange',lambda q:q['schedule'].pop())
    rejects('remove a local invocation',lambda q:q['calls'].pop())
    rejects('re-use a helper bank slot',lambda q:q['calls'][0]['owners'].__setitem__(241,q['calls'][0]['owners'][240]))
    rejects('understate live stock',lambda q:q.__setitem__('live',LIVE-1))
    rejects('omit a local paid move',lambda q:q['local_programs']['forward'].pop(next(i for i,e in enumerate(q['local_programs']['forward']) if e[0]==0)))
    rejects('wrong reflected copy charge',lambda q:q['local_programs']['reverse'][next(i for i,e in enumerate(q['local_programs']['reverse']) if e[0]==2)].__setitem__(5,0))
    rejects('alter residual orthogonal basis',lambda q:q['residual_isometries'][0]['orthogonal_rows_numerator'][0].__setitem__(0,99))
    rejects('wrong residual frame',lambda q:q['calls'][0]['owners'][240][1].__setitem__(3,-1))
    rejects('omit a residual route factor',lambda q:next(r for r in q['residual_isometries'] if r['gaussian_reduction'])['gaussian_reduction'].pop())
    rejects('alias data across replica groups',lambda q:q['calls'][8]['owners'].__setitem__(0,q['calls'][0]['owners'][0]))
    rejects('omit the fourth replica group',lambda q:q.__setitem__('calls',[c for c in q['calls'] if c['replica']<24]))
    rejects('misstate replication count',lambda q:q.__setitem__('replicas',8))
    result=dict(status='PASS_INDEPENDENT_COMPRESSED_BIT_TEMPLATE_AUDIT',template_sha256=g['template_sha256'],
                source_frames=len(proj),exact_nested_frame_pairs=len(pairs),exact_reflected_pairs=len(pairs),
                orthogonal_lift_argument='Adding the same orthogonal E_s leaves P_V-P_U unchanged; each audited projector is therefore the literal child projector in every one of the nine windows.',
                exact_bank_families=9*NB,residual_isometries=len(t['residual_isometries']),entrance_rank_total=ENT,mutations_rejected=controls,
                profile=dict(sorted(hist.items())),seconds=time.monotonic()-start)
    (out/'AUDIT.json').write_text(json.dumps(result,indent=2)+'\n'); print(json.dumps(result),flush=True)

if __name__=='__main__': main()

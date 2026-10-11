"""Independent replay of the kernelized complex local programs and their exact residual routes.
usage: complex_kreplay.py KSC_WORKDIR   (reads split-centres/{CANONICAL-WORD.json.gz,LOCAL-PROGRAMS.json.gz,LOCAL-CHECKS.json,CLIFFORD-RECIPES.json})
Local replay adapted from icekylinx's PR433 complex_replay.py (Codex assistance); residual routes and kernel
adaptation by Rohan Arun with Claude Opus 5.5 (Anthropic). Apache-2.0."""
import copy,gzip,hashlib,json,sys
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path
W=Path(sys.argv[1]).resolve();OUT=W/'split-centres'
sys.path.insert(0,str(W/'work/odd-stages'))
from clifford_exact import canonical_frame,lower_child
c=json.load(gzip.open(OUT/'CANONICAL-WORD.json.gz'));programs=json.load(gzip.open(OUT/'LOCAL-PROGRAMS.json.gz'))
checks=json.loads((OUT/'LOCAL-CHECKS.json').read_text())
v,R,h=c['v'],c['R'],c['h'];n=2*v+R;frames=c['frames']
def contains(a,b):
    for x in a:
        for y in b:
            if x>>(y.bit_length()-1)&1:x^=y
        if x:return False
    return True
def local(events,back):
    rows={('L',r):{r:Q(1)} for r in range(n)};norm={('L',r):Q(1) for r in range(n)};prefix=Q(1);cur=c['start'].copy();private={}
    hist=Counter();phases=[];entry=[];exit=[];centers=[]
    allowed=['zero_frame_precondition','entry_adapters','A','centers','B','final','exit_adapters','full_frame_cleanup','done']
    for event in events:
        tag=event[0]
        if tag=='phase':
            phases.append(event[1]);assert phases==allowed[:len(phases)]
            if event[1]=='A':assert entry==list(enumerate(c['start']))
            if event[1]=='centers':assert all(cur[r]==0 for r in range(v,2*v))
            if event[1]=='full_frame_cleanup':assert cur==c['final'] and exit==list(enumerate(c['final']))
            assert not private
        elif tag=='adapter':
            assert event[3]==(c['start'] if event[1]=='old_to_new' else c['final'])[event[2]]
            (entry if event[1]=='old_to_new' else exit).append((event[2],event[3]))
        elif tag=='climb':
            _,part,r,a,b,rank=event
            assert not private and phases[-1]==part and cur[r]==a
            assert contains(frames[a],frames[b]) and rank==len(frames[b])-len(frames[a])>0
            hist[rank]+=1;cur[r]=b
        elif tag=='center':
            _,k,a,b,rank=event
            assert phases[-1]=='centers' and private=={('C',k):a}
            cf=c['center_frames'][k];cr=len(frames[cf])
            assert (a,b,rank)==((0,cf,cr) if back else (cf,0,cr))
            private['C',k]=b;hist[rank]+=1;centers.append(k)
        elif tag=='scalar':
            _,e,f=event;op=e[0];target=tuple(e[1]);source=tuple(e[2]) if op in ('copy','add') else None
            if target[0]=='C' and op=='clear':
                assert private.get(target,f)==f;private.pop(target,None)
            else:
                for r in (target,source):
                    if r is None:continue
                    if r[0]=='L':assert cur[r[1]]==f,('common frame',r,cur[r[1]],f)
                    else:
                        if r==target and r not in private:private[r]=f
                        assert private[r]==f
            if op=='clear':rows[target]={};norm[target]=Q(0)
            elif op=='copy':rows[target]=dict(rows[source]);norm[target]=norm[source]
            elif op=='scale':
                q=Q(e[2],e[3]);a,b=abs(q.numerator),q.denominator;assert a&(a-1)==0 and b&(b-1)==0
                rows[target]={j:q*x for j,x in rows[target].items()};norm[target]*=abs(q)
            else:
                q=Q(e[3],e[4]);a,b=abs(q.numerator),q.denominator;assert source!=target and b&(b-1)==0
                prefix=max(prefix,Q(a)*norm[source]);norm[target]=norm.get(target,Q(0))+abs(q)*norm[source]
                row=rows.setdefault(target,{})
                for j,x in list(rows[source].items()):
                    z=row.get(j,Q(0))+q*x
                    if z:row[j]=z
                    else:row.pop(j,None)
            prefix=max(prefix,norm[target])
        else:raise AssertionError(tag)
    assert phases==allowed and centers==list(range(len(c['centers']))) and not private
    assert all(not row for reg,row in rows.items() if reg[0]=='C')
    for r in range(n):
        expected={r:Q(1)}
        if back and r<v:expected[v+r]=Q(-1)
        elif not back and v<=r<2*v:expected[r-v]=Q(1)
        assert rows['L',r]==expected
    assert prefix<2**192
    return hist,prefix
res={}
for name in ('forward','backward'):
    hist,prefix=local(programs[name],name=='backward')
    assert dict(hist)=={int(r):z for r,z in c['local_profile'].items()}=={int(r):z for r,z in checks[name]['paid_profile'].items()}
    assert hashlib.sha256(json.dumps(programs[name],sort_keys=True,separators=(',',':')).encode()).hexdigest()==checks[name]['sha256']
    res[name]=dict(profile=dict(sorted(hist.items())),prefix_bits=prefix.numerator.bit_length()-prefix.denominator.bit_length()+1)
controls=[]
for name,mut in [('wrong_scale',lambda es:next(e for e in es if e[0]=='scalar' and e[1][0]=='scale')[1].__setitem__(2,3)),
                 ('missing_center',lambda es:es.pop(next(i for i,e in enumerate(es) if e[0]=='center'))),
                 ('wrong_common_frame',lambda es:next(e for e in es if e[0]=='scalar' and e[2]!=0).__setitem__(2,0)),
                 ('wrong_child_rank',lambda es:next(e for e in es if e[0]=='climb').__setitem__(5,99)),
                 ('pivot entry at frame zero',lambda es:next(e for e in es if e[0]=='adapter' and e[1]=='old_to_new' and e[3]!=0 and e[2]>=240).__setitem__(3,0)),
                 ('omitted kernel exit correction',lambda es:es.pop(max(i for i,e in enumerate(es) if e[0]=='scalar')))]:
    es=copy.deepcopy(programs['forward']);mut(es)
    try:local(es,False)
    except (AssertionError,KeyError):controls.append(name)
    else:raise AssertionError('mutation accepted: '+name)
# residual routes: the helper's net label change start(h) -> FULL is an exact rank (9-dim start) Clifford child,
# lowered as monomial . F_r . monomial (a signed coordinate permutation with Z4 phases around a Fourier block on r axes)
routes=[]
for f in sorted({c['start'][r] for r in range(2*v,n)}):
    op=canonical_frame(h,frames[f]).adjoint().then(canonical_frame(h,frames[1]))
    rec,compiled=lower_child(op);assert compiled.tab==op.tab and compiled.zero_state()==op.zero_state()
    assert rec['rank']==h-len(frames[f])
    routes.append(dict(start_frame=f,start_basis=frames[f],residual_rank=rec['rank'],left=rec['left'],right=rec['right'],helpers=sum(1 for r in range(2*v,n) if c['start'][r]==f)))
blob=json.dumps(routes,sort_keys=True,separators=(',',':')).encode();(OUT/'COMPLEX-RESIDUAL-ROUTES.json').write_bytes(blob)
out=dict(status='PASS_KERNEL_COMPLEX_LOCAL_REPLAY',local=res,mutation_controls_rejected=controls,residual_routes=len(routes),
         residual_routes_sha256=hashlib.sha256(blob).hexdigest(),helper_widths=dict(Counter(h-len(frames[c['start'][r]]) for r in range(2*v,n))),
         canonical_word_sha256=hashlib.sha256((OUT/'CANONICAL-WORD.json.gz').read_bytes()).hexdigest(),
         local_programs_sha256=hashlib.sha256((OUT/'LOCAL-PROGRAMS.json.gz').read_bytes()).hexdigest())
(OUT/'KERNEL-REPLAY.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))

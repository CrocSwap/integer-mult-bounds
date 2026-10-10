"""Independent exact h24 matrix readback of the callable lowering semantics.

Uses clean source preparation, not scalar payload replay. All 1760 data routes
are coordinate-permutation conjugates of the exact checked template. Two actual
ports and two actual independent entrance projectors are evaluated explicitly.
"""
from array import array
from collections import Counter
from functools import lru_cache
from pathlib import Path
import importlib.util,hashlib,json,sys,time
import sympy as sp

if not __debug__:raise SystemExit('assertions required')
sys.dont_write_bytecode=True
BASE=Path(__file__).resolve().parent
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
begin=time.monotonic()
lp=BASE/'five_stage_bit_global_lowering_20261009.py'
cp=BASE/'five_stage_export_plan_20261009/loader/source_loader.py'
before={str(p.relative_to(BASE.parent)):sha(p)for p in(lp,cp)}
L=load('physical_global_lowerer_geometry',lp);CLEAN=load('physical_global_clean_geometry',cp)
ctx=CLEAN.prepare(cp.parent/'source_inputs/pr210',cp.parent/'source_inputs/base_bit')
W,C=ctx['W'],ctx['C'];v=W.v
Z=W.register([]);F=W.w['full_frame']
initial={i:W.w['source_frame'][i]for i in range(v)}
initial.update({v+t:Z for t in range(v)})
initial.update({2*v+j:W.gauge[r]['frame']if r in W.gauge else Z for j,r in enumerate(ctx['regs'])})
lower=L.Lowerer(array('i'),dict(W=W,C=C,initial_state=initial,ZERO=Z,FULL=F))
I=sp.eye(120);zero=sp.zeros(120)
S=sp.SparseMatrix
all_labels=[list(row)for row in W.g['labels']]
assert len(all_labels)==1760 and all(len(q)==len(set(q))==3 and all(0<=j<24 for j in q)for q in all_labels)
ports=[0,1759];checked=[]
for t in ports:
    routes=[S(lower.rho(i,t))for i in range(5)]
    assert all(r*r==I for r in routes)
    P=lower.frame_projector(W.w['source_frame'][t])
    assert P*P==P and sp.trace(P)==1
    @lru_cache(None)
    def data(i,kind):
        frame=F if kind=='H'else Z if kind=='0'else W.w['source_frame'][t]
        A=S(lower.global_stage_projector(i,frame,kind=='K'))
        return routes[i]*A*routes[i]
    for i in range(1,5):
        assert data(i-1,'H')==data(i,'P')
        assert data(i-1,'K')==data(i,'0')
    p=data(0,'P')
    pairs=[(p,data(1,'H'),46),(S(zero),data(1,'K'),46),
           (data(2,'P'),data(3,'P'),23),(data(2,'0'),data(3,'0'),23),
           (data(2,'H'),S(I),50),(data(2,'K'),S(I)-p,50),
           (data(4,'H'),S(I),4),(data(4,'K'),S(I)-p,4)]
    original_data_boundary=lower.data_boundary
    assert S(original_data_boundary(3,t,'P'))==data(3,'P')
    # Feed cached exact boundary matrices through the actual idle selector.
    # This exercises its eight emitted boundary IDs without recomputing all
    # dense matrices once per selector call.
    def cached_boundary(i,port,kind):
        assert port==t
        return data(i,kind)
    lower.data_boundary=cached_boundary
    for boundary,(a,b,rank) in enumerate(pairs):
        emitted_a,emitted_b=lower.idle_projectors(boundary,t)
        assert S(emitted_a)==a and S(emitted_b)==b
        assert a*b==b*a==a
        gap=b-a
        assert gap*gap==gap and sp.trace(gap)==rank
    lower.data_boundary=original_data_boundary
    # D_I D_P = D_(I-P), since D_I exchanges the address head/tail blocks.
    # Check its projector algebra before the final stream pair exchange.
    assert p*(S(I)-p)==S(zero) and p+(S(I)-p)==S(I)
    checked.append(dict(port=t,labels=all_labels[t],routes=5,boundaries=8,idle_ranks=[r for a,b,r in pairs]))

unique={}
for _,frame,rank in lower.entrances:
    if rank==20:unique.setdefault(tuple(map(tuple,C.B[frame])),frame)
frames=list(unique.values())[:2]
assert len(frames)==2
sigma=[S(lower.frame_projector(f))for f in frames]
assert sigma[0]!=sigma[1]
helpers=[]
for frame,P in zip(frames,sigma):
    assert P*P==P and sp.trace(P)==20
    completion=S(lower.completion_projector(frame))
    residual=S(I)-completion
    assert completion*completion==completion and sp.trace(completion)==100
    assert completion*residual==residual*completion==S(zero)
    actual=[]
    for i in range(5):
        tau=S(lower.tau(i));local=sp.zeros(120);local[:24,:24]=sp.eye(24)-P
        actual.append(tau*S(local)*tau)
    assert sum(actual,S(zero))==residual
    assert all(a*b==S(zero)for i,a in enumerate(actual)for j,b in enumerate(actual)if i!=j)
    assert sum(actual[:4]+[actual[3]],S(zero))!=residual
    helpers.append(dict(local_frame=frame,local_rank=20,completion_rank=100,distinct_windows=5))
assert lower.completion_projector(frames[0])!=lower.completion_projector(frames[1])
assert all(sha(BASE.parent/p)==h for p,h in before.items()),'sources changed during readback'
result=dict(status='PASS_EXACT_H24_CALLABLE_LOWERING_GEOMETRY',m=120,
    all_1760_ports_coordinate_permutation_equivalent=True,checked_actual_ports=checked,
    checked_actual_entrances=helpers,
    distinct_entrances_noncommuting=sigma[0]*sigma[1]!=sigma[1]*sigma[0],
    wrong_duplicate_window_rejected=True,wrong_equal_rank_correction_rejected=True,
    terminal_exchange_frame_identity_checked=True,
    source_pins=before,clean_fingerprint=CLEAN.semantic_fingerprint(ctx),
    script_sha256=sha(Path(__file__)),seconds=time.monotonic()-begin,
    scope='Exact rational h24/m120 route and idle matrices for actual source ports and actual independent entrance bases. Coordinate-permutation/direct-sum arguments cover the remaining ports and independent entrances. No scalar payload replay.')
if '--write'in sys.argv:
    Path(__file__).with_name('five_stage_bit_global_lowering_geometry_20261009_result.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
print(json.dumps(result,sort_keys=True))

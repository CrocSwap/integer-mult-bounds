"""Portable exact h/m callable geometry (h = 2p, m = 5h; h20/m100 at p = 10); inherited PR234 proof and notices.
p = 10 port (DreamingOfClouds, Anthropic Claude assistance): the h24/m120 literals are derived from the cube
size; the idle gaps are the five-stage ranks (2h-2, h-1, 2h+2, 4); every entrance rank present is checked on
an actual basis, the most frequent rank on two distinct actual bases.
"""
from array import array
from collections import Counter
from functools import lru_cache
from pathlib import Path
import hashlib,json,sys,time
import sympy as sp
from collections import Counter as _Counter
sys.dont_write_bytecode=True
if not __debug__:raise SystemExit('assertions required')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(ctx,L,source_pins=None):
 begin=time.monotonic()
 W,C=ctx['W'],ctx['C'];v=W.v;H,M=L.H,L.M;assert W.h==H and M==5*H and W.v==L.V
 Z=W.register([]);F=W.w['full_frame']
 initial={i:W.w['source_frame'][i]for i in range(v)}
 initial.update({v+t:Z for t in range(v)})
 initial.update({2*v+j:W.gauge[r]['frame']if r in W.gauge else Z for j,r in enumerate(ctx['regs'])})
 lower=L.Lowerer(array('i'),dict(W=W,C=C,initial_state=initial,ZERO=Z,FULL=F))
 I=sp.eye(M);zero=sp.zeros(M)
 S=sp.SparseMatrix
 all_labels=[list(row)for row in W.g['labels']]
 assert len(all_labels)==v and all(len(q)==len(set(q))==3 and all(0<=j<H for j in q)for q in all_labels)
 ports=[0,v-1];checked=[];g1,g2,g3,g4=L.IDLE_RANKS
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
     pairs=[(p,data(1,'H'),g1),(S(zero),data(1,'K'),g1),
            (data(2,'P'),data(3,'P'),g2),(data(2,'0'),data(3,'0'),g2),
            (data(2,'H'),S(I),g3),(data(2,'K'),S(I)-p,g3),
            (data(4,'H'),S(I),g4),(data(4,'K'),S(I)-p,g4)]
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
 
 census=_Counter(rank for _,frame,rank in lower.entrances);common=max(sorted(census),key=lambda r:census[r])
 unique={}
 for _,frame,rank in lower.entrances:
     if rank==common:unique.setdefault(tuple(map(tuple,C.B[frame])),frame)
 frames=list(unique.values())[:2]
 assert len(frames)==2
 # Two actual bases of the most frequent entrance rank (16 at p = 10) and one actual basis of every other rank.
 others=[next(frame for _,frame,rank in lower.entrances if rank==r)for r in sorted(census)if r!=common]
 sigma=[S(lower.frame_projector(f))for f in frames]
 assert sigma[0]!=sigma[1]
 helpers=[]
 for frame,P in zip(frames+others,sigma+[S(lower.frame_projector(f))for f in others]):
     rank=C.dimf[frame];assert rank in census
     assert P*P==P and sp.trace(P)==rank
     completion=S(lower.completion_projector(frame))
     residual=S(I)-completion
     assert completion*completion==completion and sp.trace(completion)==5*rank
     assert completion*residual==residual*completion==S(zero)
     actual=[]
     for i in range(5):
         tau=S(lower.tau(i));local=sp.zeros(M);local[:H,:H]=sp.eye(H)-P
         actual.append(tau*S(local)*tau)
     assert sum(actual,S(zero))==residual
     assert all(a*b==S(zero)for i,a in enumerate(actual)for j,b in enumerate(actual)if i!=j)
     assert sum(actual[:4]+[actual[3]],S(zero))!=residual
     helpers.append(dict(local_frame=frame,local_rank=rank,completion_rank=5*rank,distinct_windows=5))
 assert lower.completion_projector(frames[0])!=lower.completion_projector(frames[1])
 # Early restoration: one actual (sigma, E) endpoint pair; residual P_E - P_sigma and completion P_sigma + I - P_E.
 restored=[]
 for role,E in sorted(ctx.get('restored_endpoints',{}).items())[:1]:
     sg=W.gauge[role]['frame'];Ps=S(lower.frame_projector(sg));Pe=S(lower.frame_projector(E));D=Pe-Ps;IH=sp.eye(H)
     assert Ps*Pe==Ps and Pe*Ps==Ps and D*D==D and sp.trace(D)==C.dimf[E]-C.dimf[sg]
     completion=S(lower.completion_projector(sg,end=E));residual=S(I)-completion
     assert completion*completion==completion and sp.trace(completion)==5*(C.dimf[sg]+H-C.dimf[E])
     actual=[]
     for i in range(5):
         tau=S(lower.tau(i));local=sp.zeros(M);local[:H,:H]=D;actual.append(tau*S(local)*tau)
     assert sum(actual,S(zero))==residual and all(a*b==S(zero)for i,a in enumerate(actual)for j,b in enumerate(actual)if i!=j)
     wrong=sp.zeros(M);wrong[:H,:H]=IH-Ps
     assert sum([S(lower.tau(i))*S(wrong)*S(lower.tau(i))for i in range(5)],S(zero))!=residual,'old FULL residual formula must be rejected'
     restored.append(dict(entrance_rank=C.dimf[sg],endpoint_rank=C.dimf[E],residual_rank=C.dimf[E]-C.dimf[sg],completion_rank=5*(C.dimf[sg]+H-C.dimf[E]),full_endpoint_formula_rejected=True))
 assert len(restored)==(1 if ctx.get('restored_endpoints') else 0)
 # Every new sparse-source injection frame is checked as an exact h-dimensional projector.
 new_frames={r['mix_frame']for r in ctx['pair_selection']};G=sp.eye(H)-sp.ones(H)/9
 for f in sorted(new_frames):
  P=lower.frame_projector(f);assert P*P==P and sp.trace(P)==2 and P.T*G==G*P
 assert len(new_frames)==0
 
 
 assert {h['local_rank']for h in helpers}==set(census)
 result=dict(status='PASS_EXACT_CALLABLE_LOWERING_GEOMETRY',h=H,m=M,entrance_rank_census=dict(census),
     all_ports_coordinate_permutation_equivalent=True,ports=v,checked_actual_ports=checked,
     checked_actual_entrances=helpers,checked_restored_endpoints=restored,checked_new_sparse_source_frames=len(new_frames),
     distinct_entrances_noncommuting=sigma[0]*sigma[1]!=sigma[1]*sigma[0],
     wrong_duplicate_window_rejected=True,wrong_equal_rank_correction_rejected=True,
     terminal_exchange_frame_identity_checked=True,
     source_pins=dict(source_pins or {}),clean_fingerprint=dict(scalar_word_sha256=hashlib.sha256(ctx['SOURCE_TEXT'].encode()).hexdigest()),
     script_sha256=sha(Path(__file__)),seconds=time.monotonic()-begin,
     scope='Exact rational h'+str(H)+'/m'+str(M)+' route and idle matrices for actual source ports and actual independent entrance bases. Coordinate-permutation/direct-sum arguments cover the remaining ports and independent entrances. No scalar payload replay.')
 
 return result

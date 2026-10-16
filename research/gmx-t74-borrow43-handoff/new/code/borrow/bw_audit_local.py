# Local independent replay of the attributed PR514 / PR433 checker (icekylinx with OpenAI Codex assistance), extended (BW) with
# monomial warps and private zero buffers for anticipatory dirty borrowing (PR2226, Cinna Davis @1337isnot1337, with OpenAI
# Codex assistance, Apache-2.0).  The exact Gaussian column products below are a port of PR2226's operators.py (change /
# monomial / apply_mono / coord / frame / check); they use only numpy and share no code with the emitter or with the
# clifford_exact phase compiler.  Every edit is marked "BW:".  The complete inherited checker and its controls are retained.
if not __debug__:
    raise RuntimeError('assertions must remain enabled')   # every check of this stage is an assert
import copy,gzip,hashlib,json,sys,time
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
OUT=Path(sys.argv[1])
c=json.load(gzip.open(OUT/'CANONICAL-WORD.json.gz'))
ir={'local_programs':json.load(gzip.open(OUT/'LOCAL-PROGRAMS.json.gz'))}
v,R,h=c['v'],c['R'],c['h'];n=2*v+R;frames=c['frames']
levels={int(t):f for t,f in c.get('target_levels',{}).items()}
entering=[r for r,f in enumerate(c['start']) if r>=2*v and f!=0]
plain={r for r in range(n) if r not in set(entering)}

def contains(a,b):
    for x in a:
        for y in b:
            if x>>(y.bit_length()-1)&1:x^=y
        if x:return False
    return True
hpe={r for r in range(2*v,n) if c['final'][r]!=1}
assert all(len(frames[c['final'][r]])<h for r in hpe)
cold=sorted(hpe-set(entering));wrapped=sorted(set(entering)|hpe);plain={r for r in range(n) if r not in set(wrapped)}
zb=list(c.get('zero_buffers',[]))
assert set(zb)==hpe,'every hyperplane-ended helper is replaced by a zero buffer in the FULL cleanup, and only those'

from bw_gauss import *   # BW: exact Gaussian column products (PR2226 operators.py port), numpy only
WARPCACHE={}
def warp_columns(op,f0,f1,G,qmut=None,table=None):
    """all 512 columns of  T_f0^-1 K_G^{+-1} T_f1  (the physical rank-zero product of the warp), exactly, both orientations."""
    key=(op,f0,f1,tuple(G),qmut)
    if key in WARPCACHE:return WARPCACHE[key]
    assert len(G)==h and f2rank(G)==h,'non-invertible G'
    U,E=frames[f0],frames[f1]
    if op>0:assert sorted(lin(G,x) for x in span(U))==sorted(span(E)),'G does not carry the from frame onto the to frame'
    else:assert sorted(lin(G,x) for x in span(E))==sorted(span(U)),'G^-1 does not carry the from frame onto the to frame'
    z=warp_product(G,U,E,op,h,qmut)
    fwd=check_mono(z)
    bre,bim,bexp=z                                   # inverse-transpose of a (scaled) unitary monomial is its entrywise conjugate
    bwd=check_mono((bre,-bim,bexp))
    WARPCACHE[key]=(fwd,bwd);return WARPCACHE[key]
# ---------------------------------------------------------------------------------------------------------------------------
def add_row(row,src,q):
    for j,x in src.items():
        z=row.get(j,Q(0))+q*x
        if z:row[j]=z
        else:row.pop(j,None)
def warp_row(row,op):
    out={}
    for (var,word),x in row.items():
        word=word[1:] if word and word[0]==-op else (op,)+word
        out[var,word]=x
    return out

def local(events,back,table=None,qmut=None):
    table=c['warps'] if table is None else table
    G_of={w['op']:w['G_columns'] for w in table}
    rows={('L',r):{(r,()):Q(1)} for r in range(n)}
    norm={('L',r):Q(1) for r in range(n)};prefix=Q(1);cur=c['start'].copy();private={}
    hist=Counter();phases=[];entry=[];exit=[];centers=[];chain={};wrappers=[]
    wset=set(wrapped);pre_seen=set();post_seen=set();zlive=set();warp_hashes=[];nwarp=0
    allowed=['zero_frame_precondition','entry_adapters','A','centers','B']+(['cleanup_tail'] if c.get('tail') else [])+['final','exit_adapters','full_frame_cleanup','done']
    for event in events:
        tag=event[0]
        if tag=='phase':
            phases.append(event[1]);assert phases==allowed[:len(phases)]
            if event[1]=='A':assert entry==[(r,f) for r,f in enumerate(c['start']) if r in plain] and sorted(r for k_,r,f_ in wrappers if k_=='pre')==wrapped
            if event[1]=='centers':assert all(cur[r]==levels.get(r-v,0) for r in range(v,2*v))
            if event[1]=='full_frame_cleanup':assert cur==c['final'] and exit==[(r,f) for r,f in enumerate(c['final']) if r not in hpe]
            assert not private
        elif tag=='residual_adapter':
            _,kind,r,f,*end=event;assert r in wrapped and f==c['start'][r] and kind in ('pre','post')
            assert end==([c['final'][r]] if r in hpe else [])
            if end and kind=='post':assert cur[r]==end[0]
            assert (kind=='pre' and phases[-1]=='entry_adapters') or (kind=='post' and phases[-1]=='full_frame_cleanup')
            assert (kind,r) not in {(k,x) for k,x,_ in wrappers};wrappers.append((kind,r,f))
            (pre_seen if kind=='pre' else post_seen).add(r)
        elif tag=='adapter':
            assert event[3]==(c['start'] if event[1]=='old_to_new' else c['final'])[event[2]]
            (entry if event[1]=='old_to_new' else exit).append((event[2],event[3]))
        elif tag=='climb':
            _,part,r,a,b,rank=event
            assert not private and phases[-1]==part and cur[r]==a
            assert contains(frames[a],frames[b]) and rank==len(frames[b])-len(frames[a])>0
            hist[rank]+=1;cur[r]=b
        elif tag=='zero_buffer':   # BW: private FULL-frame zero buffers of the cleanup; allocated empty, returned empty
            _,kind,z=event;assert phases[-1]=='full_frame_cleanup' and z in zb
            if kind=='alloc':
                assert z not in zlive and ('Z',z) not in rows;zlive.add(z);rows['Z',z]={};norm['Z',z]=Q(0)
            else:
                assert kind=='free' and z in zlive and not rows['Z',z];zlive.remove(z)
        elif tag=='warp':          # BW: monomial logical reference change, rank zero, exact on all 512 columns
            _,r,op,f0,f1=event;nwarp+=1
            assert op and abs(op) in G_of and phases[-1] in ('zero_frame_precondition','A','B','cleanup_tail','full_frame_cleanup')
            assert not private
            if r[0]=='L':
                assert cur[r[1]]==f0,('warp frame mismatch',r,cur[r[1]],f0)
                assert r[1] not in wset or (r[1] in pre_seen and r[1] not in post_seen),('warp wrapper order',r)
            else:
                assert r[0]=='Z' and r[1] in zlive and f0==f1==1
            assert len(frames[f0])==len(frames[f1]),'a warp is rank zero: equal dimensions'
            warp_hashes.append(warp_columns(op,f0,f1,G_of[abs(op)],qmut))
            rows[tuple(r)]=warp_row(rows[tuple(r)],op)
            if r[0]=='L':cur[r[1]]=f1
        elif tag=='center':
            _,k,a,b,rank=event
            assert phases[-1]=='centers' and private=={('C',k):a}
            cf=c['center_frames'][k];cr=len(frames[cf])
            assert contains(frames[a],frames[b]) if back else contains(frames[b],frames[a])
            assert rank==abs(len(frames[a])-len(frames[b]))>0
            chain.setdefault(k,[]).append((a,b))
            private['C',k]=b;hist[rank]+=1;centers.append(k)
        elif tag=='scalar':
            _,e,f=event;op=e[0];target=tuple(e[1]);source=tuple(e[2]) if op in ('copy','add') else None
            if target[0]=='C' and op=='clear':
                assert private.get(target,f)==f
                private.pop(target,None)
            else:
                for r in (target,source):
                    if r is None:continue
                    if r[0]=='L':assert cur[r[1]]==f and (r[1] not in wset or (r[1] in pre_seen and r[1] not in post_seen)),('common frame / wrapper order',r,cur[r[1]],f)
                    elif r[0]=='Z':   # BW: a zero buffer lives only inside the FULL-frame cleanup, at FULL
                        assert r[1] in zlive and f==1 and phases[-1]=='full_frame_cleanup',('zero buffer misuse',r)
                    else:
                        if r==target and r not in private:private[r]=f
                        assert private[r]==f
            if op=='clear':rows[target]={};norm[target]=Q(0)
            elif op=='copy':rows[target]=dict(rows[source]);norm[target]=norm[source]
            elif op=='scale':
                q=Q(e[2],e[3]);a,b=abs(q.numerator),q.denominator
                assert a&(a-1)==0 and b&(b-1)==0
                rows[target]={j:q*x for j,x in rows[target].items()};norm[target]*=abs(q)
            else:
                q=Q(e[3],e[4]);a,b=abs(q.numerator),q.denominator
                assert source!=target and b&(b-1)==0
                w=0
                for bit in bin(a)[2:]:w=2*w+int(bit)
                assert Q(w,b)*(1 if q>0 else -1)==q
                prefix=max(prefix,Q(a)*norm[source])
                norm[target]=norm.get(target,Q(0))+abs(q)*norm[source]
                row=rows.setdefault(target,{})
                add_row(row,rows[source],q)
            prefix=max(prefix,norm[target])
        else:raise AssertionError(tag)
    assert phases==allowed and set(centers)==set(range(len(c['centers']))) and not private and not zlive
    assert sorted(r for k,r,_ in wrappers if k=='pre')==wrapped and sorted(r for k,r,_ in wrappers if k=='post')==wrapped
    for k,st in chain.items():
        cf=c['center_frames'][k]
        if back:assert st[-1][1]==cf and all(st[i][1]==st[i+1][0] for i in range(len(st)-1))
        else:assert st[0][0]==cf and all(st[i][1]==st[i+1][0] for i in range(len(st)-1))
    assert all(not row for reg,row in rows.items() if reg[0] in 'CZ')
    assert cur==c['final']
    for r in range(n):
        expected={(r,()):Q(1)}
        if back and r<v:expected[(v+r,())]=Q(-1)
        elif not back and v<=r<2*v:expected[(r-v,())]=Q(1)
        assert rows['L',r]==expected,('column mismatch',back,r)
    assert prefix<2**192
    return hist,{'all_exact_columns':n,'prefix_l1_upper':str(prefix),
                 'prefix_bits_upper':prefix.numerator.bit_length()-prefix.denominator.bit_length()+1,
                 'charged_payload_bits':192,'private_work_erased':True,'zero_buffers_returned_to_zero':len(zb),
                 'warp_events':nwarp,'warp_columns_each_exact':1<<h,'warp_product_sha256':hashlib.sha256(json.dumps(warp_hashes).encode()).hexdigest()}

t0=time.monotonic()
profiles={};checks={}
for name in ('forward','backward'):
    profiles[name],checks[name]=local(ir['local_programs'][name],name=='backward')
    assert dict(profiles[name])=={int(r):z for r,z in c['local_profile'].items()}
    print('independent emitted replay PASS',name,flush=True)
controls=[];reasons={}
def ev_index(es,pred,start=0):return next(i for i in range(start,len(es)) if pred(es[i]))
def phase_at(es,name):return es.index(['phase',name])
def first_warp(es,sign=1,start=0):return ev_index(es,lambda e:e[0]=='warp' and (e[2]>0)==(sign>0),start)
def cleanup_warp(es):return first_warp(es,-1,phase_at(es,'full_frame_cleanup'))
mutations=[
    ('wrong_scale',lambda es:next(e for e in es if e[0]=='scalar' and e[1][0]=='scale')[1].__setitem__(2,3)),
    ('missing_center',lambda es:es.pop(next(i for i,e in enumerate(es) if e[0]=='center'))),
    ('wrong_common_frame',lambda es:next(e for e in es if e[0]=='scalar' and e[2]!=0).__setitem__(2,0)),
    ('wrong_child_rank',lambda es:next(e for e in es if e[0]=='climb').__setitem__(5,99)),
]+([
    ('missing_pre_wrapper',lambda es:es.pop(next(i for i,e in enumerate(es) if e[0]=='residual_adapter' and e[1]=='pre'))),
    ('missing_post_wrapper',lambda es:es.pop(next(i for i,e in enumerate(es) if e[0]=='residual_adapter' and e[1]=='post'))),
    ('wrapper_with_wrong_frame',lambda es:next(e for e in es if e[0]=='residual_adapter' and e[2] in entering).__setitem__(3,0)),
    ('wrapper_in_wrong_phase',lambda es:es.insert(es.index(['phase','A']),es.pop(next(i for i,e in enumerate(es) if e[0]=='residual_adapter' and e[1]=='post')))),
    ('wrapper_on_a_data_register',lambda es:next(e for e in es if e[0]=='residual_adapter').__setitem__(2,3)),
    ('wrapper_on_a_target_register',lambda es:next(e for e in es if e[0]=='residual_adapter').__setitem__(2,v+3)),
    ('wrapper_on_a_centre_register',lambda es:next(e for e in es if e[0]=='residual_adapter').__setitem__(2,['C',0])),
] if entering else [])+([
    ('centre_step_not_nested',lambda es:next(e for e in es if e[0]=='center').__setitem__(3,next(f for f in range(len(frames)) if not contains(frames[f],frames[next(e for e in es if e[0]=='center')[2]]) and not contains(frames[next(e for e in es if e[0]=='center')[2]],frames[f])))),
    # no nonzero-level descent exists once every centre is rank 8: the control then drops a descent step to the zero level
    ('centre_descent_step_skipped',lambda es:es.pop(next((i for i,e in enumerate(es) if e[0]=='center' and e[3]!=0),next(i for i,e in enumerate(es) if e[0]=='center')))),
] if levels else [])+([
    ('hpe_pre_wrapper_resolved_to_full_recipe',lambda es:next(e for e in es if e[0]=='residual_adapter' and e[1]=='pre' and len(e)==5).pop()),
    ('hpe_post_wrapper_without_terminal_frame',lambda es:next(e for e in es if e[0]=='residual_adapter' and len(e)==5).pop()),
    ('hpe_post_wrapper_wrong_terminal_frame',lambda es:next(e for e in es if e[0]=='residual_adapter' and len(e)==5).__setitem__(4,1)),
    ('hpe_tail_gate_at_full_frame',lambda es:next(e for e in es[es.index(['phase','cleanup_tail']):] if e[0]=='scalar').__setitem__(2,1)),
    ('hpe_tail_climb_dropped',lambda es:es.pop(next(i for i in range(es.index(['phase','cleanup_tail']),len(es)) if es[i][0]=='climb'))),
    ('hpe_helper_exit_adapter_to_full',lambda es:es.insert(es.index(['phase','full_frame_cleanup']),['adapter','new_to_old',min(hpe),1])),
    ('hpe_tail_gate_moved_into_full_cleanup',lambda es:(lambda x:(x.__setitem__(2,1),es.insert(es.index(['phase','full_frame_cleanup'])+1,x)))(es.pop(next(i for i in range(es.index(['phase','cleanup_tail']),len(es)) if es[i][0]=='scalar')))),
] if hpe else [])+([
    ('cold_hpe_pre_wrapper_replaced_by_identity_entry_adapter',lambda es:(lambda i:es.__setitem__(i,['adapter','old_to_new',cold[0],0]))(next(i for i,e in enumerate(es) if e[0]=='residual_adapter' and e[1]=='pre' and e[2]==cold[0]))),
    ('cold_hpe_pre_wrapper_dropped',lambda es:es.pop(next(i for i,e in enumerate(es) if e[0]=='residual_adapter' and e[1]=='pre' and e[2]==cold[0]))),
    ('cold_hpe_post_wrapper_replaced_by_exit_adapter',lambda es:(lambda i:es.__setitem__(i,['adapter','new_to_old',cold[0],c['final'][cold[0]]]))(next(i for i,e in enumerate(es) if e[0]=='residual_adapter' and e[1]=='post' and e[2]==cold[0]))),
    ('cold_hpe_pre_wrapper_resolved_to_cold_full_convention',lambda es:next(e for e in es if e[0]=='residual_adapter' and e[1]=='pre' and e[2]==cold[0]).pop()),
    ('cold_hpe_wrapper_with_nonzero_entrance',lambda es:next(e for e in es if e[0]=='residual_adapter' and e[1]=='pre' and e[2]==cold[0]).__setitem__(3,1)),
    ('cold_hpe_post_wrapper_wrong_terminal_frame',lambda es:next(e for e in es if e[0]=='residual_adapter' and e[1]=='post' and e[2]==cold[0]).__setitem__(4,1)),
    ('cold_hpe_premix_gate_before_pre_wrapper',lambda es:(lambda ev:es.insert(next(i for i,e in enumerate(es) if e[0]=='residual_adapter' and e[1]=='pre' and e[2]==cold[0]),ev))(es.pop(next(i for i,e in enumerate(es) if e[0]=='scalar' and (('L',cold[0]) in [tuple(e[1][1])]+([tuple(e[1][2])] if e[1][0] in ('add','copy') else []))))) ),
] if cold else [])
# BW: mutations of the warp / zero-buffer events (each must be rejected by the literal replay)
if c.get('warps'):
    def other_frame(es,i):   # a frame of the same dimension that is not the event's own to-frame
        e=es[i];return next(f for f in range(len(frames)) if f not in (e[3],e[4]) and len(frames[f])==len(frames[e[4]]) and f!=0)
    mutations+=[
    ('warp_missing_inverse_at_full_cleanup',lambda es:es.pop(cleanup_warp(es))),
    ('warp_missing_forward',lambda es:es.pop(first_warp(es,1,phase_at(es,'B')))),
    ('warp_frame_mismatch',lambda es:(lambda i:es[i].__setitem__(3,other_frame(es,i)))(first_warp(es,1,phase_at(es,'B')))),
    ('warp_to_frame_not_carried_by_G',lambda es:(lambda i:es[i].__setitem__(4,other_frame(es,i)))(first_warp(es,1,phase_at(es,'B')))),
    ('warp_wrong_sign',lambda es:(lambda i:es[i].__setitem__(2,-es[i][2]))(first_warp(es,1,phase_at(es,'B')))),
    ('warp_wrong_operator',lambda es:(lambda i:es[i].__setitem__(2,es[i][2]%len(c['warps'])+1))(first_warp(es,1,phase_at(es,'B')))),
    ('warp_inverse_moved_before_use',lambda es:es.insert(first_warp(es,1,phase_at(es,'B')),es.pop(cleanup_warp(es)))),
    ('warp_inverse_wrong_frame',lambda es:es[cleanup_warp(es)].__setitem__(3,0)),
    ('warp_rank_changing',lambda es:(lambda i:es[i].__setitem__(4,0))(first_warp(es,1,phase_at(es,'B')))),
    ('warp_phase_B_dropped_gate_after_warp',lambda es:es.pop(ev_index(es,lambda e:e[0]=='scalar' and e[1][0]=='add',first_warp(es,1,phase_at(es,'B'))))),
    ]
if zb:
    mutations+=[
    ('zero_buffer_not_freed',lambda es:es.pop(ev_index(es,lambda e:e[0]=='zero_buffer' and e[1]=='free'))),
    ('zero_buffer_gate_outside_cleanup',lambda es:es.insert(phase_at(es,'full_frame_cleanup')-1,['scalar',['add',['Z',zb[0]],['L',0],1,1],1])),
    ('zero_buffer_garbage_left',lambda es:es.pop(ev_index(es,lambda e:e[0]=='scalar' and e[1][0]=='add' and e[1][1]==['Z',zb[0]] ,phase_at(es,'full_frame_cleanup')))),
    ]
def mutate_gate_to_L(es):
    i=ev_index(es,lambda e:e[0]=='scalar' and ['Z',zb[0]] in [e[1][1]]+([e[1][2]] if e[1][0]=='add' else []),phase_at(es,'full_frame_cleanup'))
    g=es[i][1];es[i][1]=[g[0]]+[(['L',zb[0]] if x==['Z',zb[0]] else x) for x in g[1:3]]+list(g[3:])
if zb:
    mutations.append(('zero_buffer_replaced_by_restored_register_at_full',mutate_gate_to_L))
# BW post-cut correction: signed warp items inside phase B (forward warp, correction adds, inverse warp); present only when a B-phase inverse warp exists
_f0=ir['local_programs']['forward']
def b_inverse(es):return ev_index(es,lambda e:e[0]=='warp' and e[2]<0,phase_at(es,'B'))
if any(e[0]=='warp' and e[2]<0 for e in _f0[phase_at(_f0,'B'):phase_at(_f0,'full_frame_cleanup')]):
    mutations+=[
    ('postcut_inverse_warp_sign_flipped',lambda es:(lambda i:es[i].__setitem__(2,-es[i][2]))(b_inverse(es))),
    ('postcut_inverse_warp_wrong_operator',lambda es:(lambda i:es[i].__setitem__(2,-(abs(es[i][2])%len(c['warps'])+1)))(b_inverse(es))),
    ('postcut_inverse_warp_wrong_register',lambda es:(lambda i:es[i].__setitem__(1,es[first_warp(es,1,phase_at(es,'B'))+1][1] if es[first_warp(es,1,phase_at(es,'B'))+1][1]!=es[i][1] else es[first_warp(es,1,phase_at(es,'B'))+2][1]))(b_inverse(es))),
    ('postcut_inverse_warp_omitted',lambda es:es.pop(b_inverse(es))),
    ('postcut_forward_warp_omitted',lambda es:es.pop(first_warp(es,1,phase_at(es,'B')))),
    ('postcut_correction_add_before_forward_warp',lambda es:(lambda w0:es.insert(w0,es.pop(ev_index(es,lambda e:e[0]=='scalar' and e[1][0]=='add',w0))))(first_warp(es,1,phase_at(es,'B')))),
    ('postcut_correction_add_moved_out_of_phase_B',lambda es:es.insert(phase_at(es,'B'),es.pop(ev_index(es,lambda e:e[0]=='scalar' and e[1][0]=='add',first_warp(es,1,phase_at(es,'B')))))),
    ]
for name,mut in mutations:
    es=copy.deepcopy(ir['local_programs']['forward']);mut(es)   # a mutation that cannot be built is an error, not a rejection
    try:local(es,False)
    except (AssertionError,KeyError) as exc:controls.append(name);reasons[name]=repr(exc.args)[:160]
    else:raise AssertionError('mutation accepted: '+name)
# BW: table / operator tampering of the warps themselves
def tampered(name,table_fn,qmut=None):
    t=copy.deepcopy(c['warps']);table_fn(t)
    try:local(ir['local_programs']['forward'],False,table=t,qmut=qmut)
    except (AssertionError,KeyError) as exc:controls.append(name);reasons[name]=repr(exc.args)[:160]
    else:raise AssertionError('tampered warp operator accepted: '+name)
if c.get('warps'):
    def wrongG(t):
        U=frames[t[0]['from_frame']];E=frames[t[0]['to_frame']]
        G=list(t[0]['G_columns']);outside=next(x for x in range(1,1<<h) if x not in span(U))
        # replace a column so that G is still invertible but a frame vector no longer lands in the to frame
        for i in range(h):
            for j in range(h):
                if i!=j:
                    G2=list(G);G2[i]^=G2[j]
                    if f2rank(G2)==h and sorted(lin(G2,x) for x in span(U))!=sorted(span(E)):t[0]['G_columns']=G2;return
        raise AssertionError('no column tamper found')
    tampered('warp_wrong_G_invertible_not_carrying_frame',wrongG)
    tampered('warp_noninvertible_G',lambda t:t[0]['G_columns'].__setitem__(1,t[0]['G_columns'][0]))
    tampered('warp_zero_column_G',lambda t:t[0]['G_columns'].__setitem__(0,0))
    tampered('warp_operator_dropped_from_table',lambda t:t.pop(0))
    tampered('warp_wrong_quadratic_phase_of_K',lambda t:None,qmut=(0,2))
result={'status':'PASS_INDEPENDENT_LOCAL_SCALAR_FRAME_AND_WRAPPER_REPLAY',   # lineage label kept: the warp replay below is a strict superset
'warp_replay':{'status':'PASS_EXACT_MONOMIAL_WARP_COLUMNS_ALL_512_BOTH_ORIENTATIONS','warps':len(c.get('warps',[])),'event_classes_checked_on_all_512_columns':len(WARPCACHE),'zero_buffers':len(zb)},
'canonical_word_sha256':hashlib.sha256((OUT/'CANONICAL-WORD.json.gz').read_bytes()).hexdigest(),
'local_programs_sha256':hashlib.sha256((OUT/'LOCAL-PROGRAMS.json.gz').read_bytes()).hexdigest(),
'v':v,'helpers':R,'local':checks,'paid_profiles':{name:dict(H) for name,H in profiles.items()},
'entering_helpers':len(entering),**({'cold_hyperplane_ended_helpers':len(cold)} if cold else {}),
'negative_controls_rejected':controls,'negative_control_reasons':reasons,
'scope':'Literal forward and inverse-transpose replay on every arbitrary data/helper column in the free warp operator algebra, physical frame incidence, ordered paid wrappers, every warp product checked exactly on all 512 columns incl. scalar phases, cleared private work and zero buffers, prefix coefficients. Global hosting and outer exponent are separate.'}
(OUT/'INDEPENDENT-LOCAL-REPLAY.json').write_text(json.dumps(result,indent=2)+'\n')
print(result['status'],result['warp_replay']['status'],len(controls),'controls rejected',flush=True)

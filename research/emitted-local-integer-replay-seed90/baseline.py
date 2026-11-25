# Local-only extraction of the attributed PR514 / PR433 independent replay.
# Prepared for icekylinx with OpenAI Codex assistance. Apache-2.0.
# The complete local checker and its negative controls are retained verbatim.
# Global hosting is verified separately for the changed 112-port geometry.
import copy,gzip,hashlib,json,sys
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path
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
hpe={r for r in range(2*v,n) if c['final'][r]!=1}   # HPE: helpers whose terminal frame is a proper subspace U of FULL
assert all(len(frames[c['final'][r]])<h for r in hpe)
# COLD-HPE: cold helpers (start frame 0) ending at U carry the (0, U) wrappers too; without cold ends wrapped == entering
cold=sorted(hpe-set(entering));wrapped=sorted(set(entering)|hpe);plain={r for r in range(n) if r not in set(wrapped)}
def local(events,back):
    rows={('L',r):{r:Q(1)} for r in range(n)}
    norm={('L',r):Q(1) for r in range(n)};prefix=Q(1);cur=c['start'].copy();private={}
    hist=Counter();phases=[];entry=[];exit=[];centers=[];matrix_hash=hashlib.sha256();chain={};wrappers=[]
    wset=set(wrapped);pre_seen=set();post_seen=set()   # WRAPPER ORDER (Lemma A): R^-1 precedes, L^-1 follows, every scalar touching a wrapped helper
    allowed=['zero_frame_precondition','entry_adapters','A','centers','B']+(['cleanup_tail'] if c.get('tail') else [])+['final','exit_adapters','full_frame_cleanup','done']   # HPE
    for event in events:
        tag=event[0]
        if tag=='phase':
            phases.append(event[1]);assert phases==allowed[:len(phases)]
            if event[1]=='A':assert entry==[(r,f) for r,f in enumerate(c['start']) if r in plain] and sorted(r for k_,r,f_ in wrappers if k_=='pre')==wrapped   # GK
            if event[1]=='centers':assert all(cur[r]==levels.get(r-v,0) for r in range(v,2*v))   # GK
            if event[1]=='full_frame_cleanup':assert cur==c['final'] and exit==[(r,f) for r,f in enumerate(c['final']) if r not in hpe]   # HPE: no old-convention exit for U-ended helpers
            assert not private
        elif tag=='residual_adapter':   # GK: paid wrappers of entering helpers: R_E^-1 before the invocation, L_E^-1 after the full-frame cleanup
            _,kind,r,f,*end=event;assert r in wrapped and f==c['start'][r] and kind in ('pre','post')
            # HPE: the post wrapper of a U-ended helper names U (= its terminal frame) and is L_{E,U}^-1; every other wrapper has no 5th field
            # HPE: both wrappers of a U-ended helper name U, so the recipe is the (E,U) one, R_{E,U} and L_{E,U}
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
        elif tag=='center':
            _,k,a,b,rank=event
            assert phases[-1]=='centers' and private=={('C',k):a}
            cf=c['center_frames'][k];cr=len(frames[cf])
            # GK: stepwise descent cf -> served levels -> lowest (forward), reversed ascent (backward); each step is a nested child
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
                # Independent symbolic replay of the cleared coefficient work.
                w=0
                for bit in bin(a)[2:]:w=2*w+int(bit)
                assert Q(w,b)*(1 if q>0 else -1)==q
                prefix=max(prefix,Q(a)*norm[source])
                norm[target]=norm.get(target,Q(0))+abs(q)*norm[source]
                row=rows.setdefault(target,{})
                for j,x in list(rows[source].items()):
                    z=row.get(j,Q(0))+q*x
                    if z:row[j]=z
                    else:row.pop(j,None)
            prefix=max(prefix,norm[target])
        else:raise AssertionError(tag)
    assert phases==allowed and set(centers)==set(range(len(c['centers']))) and not private
    assert sorted(r for k,r,_ in wrappers if k=='pre')==wrapped and sorted(r for k,r,_ in wrappers if k=='post')==wrapped   # GK
    for k,st in chain.items():   # GK: the steps of each centre chain link up and end at the centre frame
        cf=c['center_frames'][k]
        if back:assert st[-1][1]==cf and all(st[i][1]==st[i+1][0] for i in range(len(st)-1))
        else:assert st[0][0]==cf and all(st[i][1]==st[i+1][0] for i in range(len(st)-1))
    assert all(not row for reg,row in rows.items() if reg[0]=='C')
    for r in range(n):
        expected={r:Q(1)}
        if back and r<v:expected[v+r]=Q(-1)
        elif not back and v<=r<2*v:expected[r-v]=Q(1)
        assert rows['L',r]==expected
    # A 192-bit local payload allowance vastly dominates even coefficient work.
    assert prefix<2**192
    return hist,{'all_exact_columns':n,'prefix_l1_upper':str(prefix),
                 'prefix_bits_upper':prefix.numerator.bit_length()-prefix.denominator.bit_length()+1,
                 'charged_payload_bits':192,'private_work_erased':True}

profiles={};checks={}
for name in ('forward','backward'):
    profiles[name],checks[name]=local(ir['local_programs'][name],name=='backward')
    assert dict(profiles[name])=={int(r):z for r,z in c['local_profile'].items()}
    print('independent emitted replay PASS',name,flush=True)
controls=[]
for name,mut in [
    ('wrong_scale',lambda es:next(e for e in es if e[0]=='scalar' and e[1][0]=='scale')[1].__setitem__(2,3)),
    ('missing_center',lambda es:es.pop(next(i for i,e in enumerate(es) if e[0]=='center'))),
    ('wrong_common_frame',lambda es:next(e for e in es if e[0]=='scalar' and e[2]!=0).__setitem__(2,0)),
    ('wrong_child_rank',lambda es:next(e for e in es if e[0]=='climb').__setitem__(5,99)),
]+([
    ('missing_pre_wrapper',lambda es:es.pop(next(i for i,e in enumerate(es) if e[0]=='residual_adapter' and e[1]=='pre'))),
    ('missing_post_wrapper',lambda es:es.pop(next(i for i,e in enumerate(es) if e[0]=='residual_adapter' and e[1]=='post'))),
    ('wrapper_with_wrong_frame',lambda es:next(e for e in es if e[0]=='residual_adapter' and e[2] in entering).__setitem__(3,0)),   # COLD-HPE: an ENTERING helper's wrapper (a cold one's frame is 0 already)
    ('wrapper_in_wrong_phase',lambda es:es.insert(es.index(['phase','A']),es.pop(next(i for i,e in enumerate(es) if e[0]=='residual_adapter' and e[1]=='post')))),
    ('wrapper_on_a_data_register',lambda es:next(e for e in es if e[0]=='residual_adapter').__setitem__(2,3)),
    ('wrapper_on_a_target_register',lambda es:next(e for e in es if e[0]=='residual_adapter').__setitem__(2,v+3)),
    ('wrapper_on_a_centre_register',lambda es:next(e for e in es if e[0]=='residual_adapter').__setitem__(2,['C',0])),
] if entering else [])+([
    ('centre_step_not_nested',lambda es:next(e for e in es if e[0]=='center').__setitem__(3,next(f for f in range(len(frames)) if not contains(frames[f],frames[next(e for e in es if e[0]=='center')[2]]) and not contains(frames[next(e for e in es if e[0]=='center')[2]],frames[f])))),
    ('centre_descent_step_skipped',lambda es:es.pop(next(i for i,e in enumerate(es) if e[0]=='center' and e[3]!=0))),
] if levels else [])+([
    ('hpe_pre_wrapper_resolved_to_full_recipe',lambda es:next(e for e in es if e[0]=='residual_adapter' and e[1]=='pre' and len(e)==5).pop()),
    ('hpe_post_wrapper_without_terminal_frame',lambda es:next(e for e in es if e[0]=='residual_adapter' and len(e)==5).pop()),
    ('hpe_post_wrapper_wrong_terminal_frame',lambda es:next(e for e in es if e[0]=='residual_adapter' and len(e)==5).__setitem__(4,1)),
    ('hpe_tail_gate_at_full_frame',lambda es:next(e for e in es[es.index(['phase','cleanup_tail']):] if e[0]=='scalar').__setitem__(2,1)),
    ('hpe_tail_climb_dropped',lambda es:es.pop(next(i for i in range(es.index(['phase','cleanup_tail']),len(es)) if es[i][0]=='climb'))),
    ('hpe_helper_exit_adapter_to_full',lambda es:es.insert(es.index(['phase','full_frame_cleanup']),['adapter','new_to_old',min(hpe),1])),
    ('hpe_tail_gate_moved_into_full_cleanup',lambda es:(lambda x:(x.__setitem__(2,1),es.insert(es.index(['phase','full_frame_cleanup'])+1,x)))(es.pop(next(i for i in range(es.index(['phase','cleanup_tail']),len(es)) if es[i][0]=='scalar')))),
] if hpe else [])+([   # COLD-HPE controls on the first cold hyperplane-ended helper
    ('cold_hpe_pre_wrapper_replaced_by_identity_entry_adapter',lambda es:(lambda i:es.__setitem__(i,['adapter','old_to_new',cold[0],0]))(next(i for i,e in enumerate(es) if e[0]=='residual_adapter' and e[1]=='pre' and e[2]==cold[0]))),
    ('cold_hpe_pre_wrapper_dropped',lambda es:es.pop(next(i for i,e in enumerate(es) if e[0]=='residual_adapter' and e[1]=='pre' and e[2]==cold[0]))),
    ('cold_hpe_post_wrapper_replaced_by_exit_adapter',lambda es:(lambda i:es.__setitem__(i,['adapter','new_to_old',cold[0],c['final'][cold[0]]]))(next(i for i,e in enumerate(es) if e[0]=='residual_adapter' and e[1]=='post' and e[2]==cold[0]))),
    ('cold_hpe_pre_wrapper_resolved_to_cold_full_convention',lambda es:next(e for e in es if e[0]=='residual_adapter' and e[1]=='pre' and e[2]==cold[0]).pop()),
    ('cold_hpe_wrapper_with_nonzero_entrance',lambda es:next(e for e in es if e[0]=='residual_adapter' and e[1]=='pre' and e[2]==cold[0]).__setitem__(3,1)),
    ('cold_hpe_post_wrapper_wrong_terminal_frame',lambda es:next(e for e in es if e[0]=='residual_adapter' and e[1]=='post' and e[2]==cold[0]).__setitem__(4,1)),
    ('cold_hpe_premix_gate_before_pre_wrapper',lambda es:(lambda ev:es.insert(next(i for i,e in enumerate(es) if e[0]=='residual_adapter' and e[1]=='pre' and e[2]==cold[0]),ev))(es.pop(next(i for i,e in enumerate(es) if e[0]=='scalar' and (('L',cold[0]) in [tuple(e[1][1])]+([tuple(e[1][2])] if e[1][0] in ('add','copy') else []))))) ),
] if cold else []):
    es=copy.deepcopy(ir['local_programs']['forward']);mut(es)
    try:local(es,False)
    except (AssertionError,KeyError):controls.append(name)
    else:raise AssertionError('mutation accepted: '+name)


result={'status':'PASS_INDEPENDENT_LOCAL_SCALAR_FRAME_AND_WRAPPER_REPLAY',
'canonical_word_sha256':hashlib.sha256((OUT/'CANONICAL-WORD.json.gz').read_bytes()).hexdigest(),
'local_programs_sha256':hashlib.sha256((OUT/'LOCAL-PROGRAMS.json.gz').read_bytes()).hexdigest(),
'v':v,'helpers':R,'local':checks,'paid_profiles':{name:dict(H) for name,H in profiles.items()},
'entering_helpers':len(entering),**({'cold_hyperplane_ended_helpers':len(cold)} if cold else {}),'negative_controls_rejected':controls,
'scope':'Literal forward and inverse-transpose replay on every arbitrary data/helper column, physical frame incidence, ordered paid wrappers, cleared private work and prefix coefficients. Global hosting and outer exponent are separate.'}
(OUT/'INDEPENDENT-LOCAL-REPLAY.json').write_text(json.dumps(result,indent=2)+'\n')
print(result['status'],len(controls),'controls rejected',flush=True)

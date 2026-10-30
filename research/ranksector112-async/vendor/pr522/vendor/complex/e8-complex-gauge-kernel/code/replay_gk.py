# GK: modified copy of PR #433's complex_replay.py (icekylinx with Codex assistance; PR #425) by DreamingOfClouds with Claude Opus 5.5
# (Anthropic), via Claude Code.  Every change is marked "GK:".  On a word without start_extra / target_levels the behaviour
# and every written file equal PR #433's (regression anchor in verify.py).
import sys as _sys, os as _os; _sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
# Adapted for heterogeneous centres by icekylinx with Codex assistance.
"""Independent read-back of the serialized local/global instruction stream."""
import copy,gzip,hashlib,importlib.util,json,math
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path

OUT=Path('split-centres');P=OUT/'GLOBAL-TEMPLATE.json.gz'
ir=json.load(gzip.open(P));c=json.load(gzip.open(OUT/'CANONICAL-WORD.json.gz'))
integration=json.loads((OUT/'INTEGRATION.json').read_text())
assert hashlib.sha256(gzip.decompress(P.read_bytes())).hexdigest()==integration['global_template_sha256']
assert c['ports']==json.load(gzip.open('work/higher-stage-e8/verified/gcert1-e8-retimed.json.gz'))['ports']
v,R,h=c['v'],c['R'],c['h'];n=2*v+R;frames=c['frames']
from gk_common import tile   # GK
widths=[h-len(frames[c['start'][2*v+i]]) for i in range(R)]
assign,nb,pads=tile([(rep,i,widths[i]) for rep in range(8) for i in range(R)]);W=7680+9*nb
levels={int(t):f for t,f in c.get('target_levels',{}).items()}
entering=[r for r,f in enumerate(c['start']) if r>=2*v and f!=0];plain={r for r in range(n) if r not in set(entering)}   # GK
def contains(a,b):
    for x in a:
        for y in b:
            if x>>(y.bit_length()-1)&1:x^=y
        if x:return False
    return True
def local(events,back):
    rows={('L',r):{r:Q(1)} for r in range(n)}
    norm={('L',r):Q(1) for r in range(n)};prefix=Q(1);cur=c['start'].copy();private={}
    hist=Counter();phases=[];entry=[];exit=[];centers=[];matrix_hash=hashlib.sha256();chain={};wrappers=[]
    allowed=['zero_frame_precondition','entry_adapters','A','centers','B','final','exit_adapters','full_frame_cleanup','done']
    for event in events:
        tag=event[0]
        if tag=='phase':
            phases.append(event[1]);assert phases==allowed[:len(phases)]
            if event[1]=='A':assert entry==[(r,f) for r,f in enumerate(c['start']) if r in plain] and sorted(r for k_,r,f_ in wrappers if k_=='pre')==entering   # GK
            if event[1]=='centers':assert all(cur[r]==levels.get(r-v,0) for r in range(v,2*v))   # GK
            if event[1]=='full_frame_cleanup':assert cur==c['final'] and exit==list(enumerate(c['final']))
            assert not private
        elif tag=='residual_adapter':   # GK: paid wrappers of entering helpers: R_E^-1 before the invocation, L_E^-1 after the full-frame cleanup
            _,kind,r,f=event;assert r in entering and f==c['start'][r] and kind in ('pre','post')
            assert (kind=='pre' and phases[-1]=='entry_adapters') or (kind=='post' and phases[-1]=='full_frame_cleanup')
            assert (kind,r) not in {(k,x) for k,x,_ in wrappers};wrappers.append((kind,r,f))
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
                    if r[0]=='L':assert cur[r[1]]==f,('common frame',r,cur[r[1]],f)
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
    assert sorted(r for k,r,_ in wrappers if k=='pre')==entering and sorted(r for k,r,_ in wrappers if k=='post')==entering   # GK
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
    ('wrapper_with_wrong_frame',lambda es:next(e for e in es if e[0]=='residual_adapter').__setitem__(3,0)),
    ('wrapper_in_wrong_phase',lambda es:es.insert(es.index(['phase','A']),es.pop(next(i for i,e in enumerate(es) if e[0]=='residual_adapter' and e[1]=='post')))),
    ('wrapper_on_a_data_register',lambda es:next(e for e in es if e[0]=='residual_adapter').__setitem__(2,3)),
    ('wrapper_on_a_target_register',lambda es:next(e for e in es if e[0]=='residual_adapter').__setitem__(2,v+3)),
    ('wrapper_on_a_centre_register',lambda es:next(e for e in es if e[0]=='residual_adapter').__setitem__(2,['C',0])),
] if entering else [])+([
    ('centre_step_not_nested',lambda es:next(e for e in es if e[0]=='center').__setitem__(3,next(f for f in range(len(frames)) if not contains(frames[f],frames[next(e for e in es if e[0]=='center')[2]]) and not contains(frames[next(e for e in es if e[0]=='center')[2]],frames[f])))),
    ('centre_descent_step_skipped',lambda es:es.pop(next(i for i,e in enumerate(es) if e[0]=='center' and e[3]!=0))),
] if levels else []):
    es=copy.deepcopy(ir['local_programs']['forward']);mut(es)
    try:local(es,False)
    except (AssertionError,KeyError):controls.append(name)
    else:raise AssertionError('mutation accepted: '+name)

def residual_cells(route):
    """cells of a bank family occupied by a helper residual (independent of tile): a width-9 slot or [offset, offset + width)"""
    return set(range(route[1]*9,route[1]*9+9)) if len(route)==2 else set(range(route[1],route[1]+route[2]))
def bank_rule(owners,occ,sole=True):
    """GK: the one-helper rule of PR #458 on EVERY register class of one invocation (owners: 240 active data owners, then the 560 helpers).
    data class (family < 7680): only the active wires, each the sole owner of its family; bank class (7680 <= family < W): helpers only; an ENTERING
    helper (width < 9) is the sole owner of its bank family, its route is [2, offset, width, spectators] with the spectators the first
    cells of the bank beyond every residual cell of it (occ[family] = those cells, over all invocations); width-9 helpers share a pure bank in
    disjoint 9-cell slots (no wrapper acts on them); nobody owns a family of the private namespace (family >= W).  sole=False skips only the
    sole-owner assertion (used by a control to show that the footprints themselves are fine)."""
    fam=Counter(f for f,_ in owners);foot={}
    for i,(f,route) in enumerate(owners):
        assert f<W,('owner in the private namespace',f)
        if f<7680:
            assert i<240 and route[0]==1 and fam[f]==1,('data class: only the active wires, each alone on its family',i,f)
        else:
            assert i>=240 and route[0]==2,('bank class: helpers only',i,f);w=widths[i-240]
            if w==9: assert len(route)==2,('width-9 helper in a pure bank',i)
            else:
                if sole: assert fam[f]==1,('entering helper shares its bank family in one invocation',i,f)
                assert len(route)==4 and route[2]==w and len(set(route[3]))==9-w==len(route[3]),('entering helper without a spectator record',i)
                assert route[3]==list(range(len(occ[f]),len(occ[f])+9-w)) and len(occ[f])+9-w<=73,('spectators are not the first cells beyond the residuals',i,f)
            cells=residual_cells(route)|(set(route[3]) if len(route)==4 else set())
            assert len(cells)==9 and not cells&foot.setdefault(f,set()),('footprints overlap on a bank family',i,f);foot[f]|=cells
def global_check(t):
    assert t['live']==W and t['physical']==W+R+len(c['centers'])+2   # GK
    occ={}
    for call in t['calls']:
        for fam,route in call['owners'][240:]:occ.setdefault(fam,set()).update(residual_cells(route))
    assert all(cs==set(range(len(cs))) for cs in occ.values()),'bank residuals are packed from cell 0'
    # Eight data-wire scalar columns, independently recomposed.
    matrix=[[int(i==j) for j in range(8)] for i in range(8)]
    for e in t['recipe']:
        if e['kind']=='local':
            a=2*e['pair'];b=a+1;dst,src,q=(a,b,-1) if e['reverse'] else (b,a,1)
            matrix[dst]=[x+q*y for x,y in zip(matrix[dst],matrix[src])]
        elif e['kind']=='bridge':
            i,j,q=e['dst'],e['src'],e['coefficient']
            matrix[2*i]=[x+q*y for x,y in zip(matrix[2*i],matrix[2*j])]
            matrix[2*j+1]=[x-q*y for x,y in zip(matrix[2*j+1],matrix[2*i+1])]
        else:
            assert e['kind']=='terminal';old=copy.deepcopy(matrix)
            for i in range(4):matrix[2*i]=old[2*i+1];matrix[2*i+1]=[-x for x in old[2*i]]
    assert matrix==[[int(i==j) for j in range(8)] for i in range(8)]
    seen=set();hist=Counter();pairs={e['stage']:e for e in t['recipe'] if e['kind']=='local'}
    for call in t['calls']:
        stage,rep,pair=call['stage'],call['replica'],call['pair']
        assert (stage,rep) not in seen;seen.add((stage,rep))
        assert pair==pairs[stage]['pair']
        assert call['orientation']==('backward' if pairs[stage]['reverse'] else 'forward')
        assert len(call['owners'])==800
        for r,(fam,route) in enumerate(call['owners']):
            if r<240:assert fam==rep*960+(2*pair+r//120)*120+r%120 and route==[1,stage,r%120]
            else:
                bk,off_,w_,pure_,sp_=assign[rep,r-240];assert fam==7680+stage*nb+bk and route==([2,off_//9] if (w_==9 and pure_) else [2,off_,w_,list(sp_)])   # GK
        assert len(set((f,json.dumps(r)) for f,r in call['owners']))==800
        bank_rule(call['owners'],occ)   # GK: the rule on every register class, stated independently of tile()
        for r,z in profiles[call['orientation']].items():hist[r]+=z
    assert seen=={(s,r) for s in range(9) for r in range(8)}
    for child in t['idle_children']:hist[child['rank']]+=child['replicas']
    assert t['bank_padding']=={'families':list(range(7680,W)),'axis':72,'child_rank':1}
    for r_,z_ in pads.items():hist[r_]+=z_*9   # GK
    assert t['cover_final_correction']['families']==[0,W]
    assert t['cover_final_correction']['charged_calls_per_cover']==W
    assert t['execution_schedule'][-1]=={'kind':'translate_every_live_family',**{k:v for k,v in t['cover_final_correction'].items() if k!='kind'}}
    assert 73*W-sum(r*z for r,z in hist.items())==2496
    return hist
H=global_check(ir)
# Derivative repair: select two genuine width-9 owners; a fixed route may already match.
pure_alias=[r for r in range(240,800) if widths[r-240]==9 and len(ir['calls'][0]['owners'][r][1])==2]
assert len(pure_alias)>=2
alias_src,alias_dst=pure_alias[:2]
assert ir['calls'][0]['owners'][alias_src]!=ir['calls'][0]['owners'][alias_dst]
def alias_owner(owners):
    owners[alias_dst]=copy.deepcopy(owners[alias_src])
for name,mut in [('missing_padding',lambda t:t['bank_padding']['families'].pop()),
                 ('aliased_owner',lambda t:alias_owner(t['calls'][0]['owners'])),
                 ('missing_cover_phase',lambda t:t['cover_final_correction'].__setitem__('charged_calls_per_cover',0))]:
    t=copy.deepcopy(ir);mut(t)
    assert t!=ir,('vacuous global mutation',name)
    try:global_check(t)
    except (AssertionError,KeyError):controls.append(name)
    else:raise AssertionError('global mutation accepted: '+name)
# GK: controls of the rule itself, one per register class, run on bank_rule (not on the equality with tile()); only for words with entering
# helpers (the anchor's INDEPENDENT-REPLAY.json must stay byte-identical to PR #433's)
occ_all={}
for call in ir['calls']:
    for fam_,route_ in call['owners'][240:]:occ_all.setdefault(fam_,set()).update(residual_cells(route_))
def rule_control(name,mut,must):
    o=copy.deepcopy(ir['calls'][0]['owners']);mut(o)
    try:bank_rule(o,occ_all)
    except AssertionError as e:
        assert must in str(e),(name,str(e));controls.append(name)
    else:raise AssertionError('rule mutation accepted: '+name)
bank_rule(ir['calls'][0]['owners'],occ_all)
rule_control('same_width_pure_helper_alias',alias_owner,'footprints overlap')
ent=[r for r in range(240,800) if widths[r-240]<9]
if entering:
    a_,b_=ent[0],ent[1]
    def to_one_bank(o):   # bank class: b joins a's bank family at the next free cells, with a spectator of its own
        fa=o[a_][0];free=len(occ_all[fa]);o[b_]=[fa,[2,free,widths[b_-240],[free+widths[b_-240]]]]
    rule_control('two_entering_helpers_on_one_bank_family',to_one_bank,'shares its bank family')
    rule_control('bank_spectator_is_a_residual_cell',lambda o:o[a_][1].__setitem__(3,[o[a_][1][1]]+o[a_][1][3][1:]),'first cells beyond')
    rule_control('bank_spectator_shifted',lambda o:o[a_][1].__setitem__(3,[x+1 for x in o[a_][1][3]]),'first cells beyond')
    rule_control('bank_spectator_record_dropped',lambda o:o[a_].__setitem__(1,o[a_][1][:3]),'without a spectator record')
    rule_control('bank_spectator_count_wrong',lambda o:o[a_][1].__setitem__(3,o[a_][1][3]*2),'without a spectator record')
    rule_control('second_owner_on_an_active_data_family',lambda o:o.__setitem__(241,[o[0][0],[1,0,0]]),'data class')
    rule_control('helper_owner_on_an_active_data_family',lambda o:o.__setitem__(250,[o[3][0],[2,0]]),'data class')
    rule_control('active_wire_on_a_bank_family',lambda o:o.__setitem__(5,[7680,[1,0,5]]),'bank class')
    C_=len(c['centers'])
    rule_control('owner_in_the_private_namespace_centres',lambda o:o.__setitem__(300,[W+3,[2,0]]),'private namespace')
    rule_control('owner_in_the_private_namespace_reserved_tableau',lambda o:o.__setitem__(300,[W+C_+5,[2,0]]),'private namespace')
    rule_control('owner_in_the_private_namespace_coefficient',lambda o:o.__setitem__(300,[W+C_+R+1,[2,0]]),'private namespace')
    t=copy.deepcopy(ir);t['calls'][0]['owners'][0][0]+=960   # copies: an active owner of replica 0's invocation on a family of replica 1
    try:global_check(t)
    except (AssertionError,KeyError):controls.append('active_owner_on_the_family_of_another_replica')
    else:raise AssertionError('global mutation accepted: active_owner_on_the_family_of_another_replica')
assert dict(H)=={int(r):z for r,z in integration['global_profile'].items()}

def load(name):
    sp=importlib.util.spec_from_file_location('replay_hamming_'+name,Path('work/pr361/code/engines')/(name+'.py'))
    m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
M,B=load('moment'),load('base_two_moment');b=Q(integration['complex_b']);grid=Q(1,10**18)
assert M.moment(H,73,W,b,True)[1]<1<M.moment(H,73,W,b+grid,True)[0]
def other(a):
    lo,hi=B.moment(73,W,list(H.items()),a)
    l2,h2=B.moment(73,W,[(1,32*73**2*sum(H.values()))],a)
    return lo+l2/10**16,hi+h2/10**16
assert other(b)[1]<1<other(b+grid)[0]
result={'status':'PASS_INDEPENDENT_NEW_STRUCTURAL_IR_REPLAY',
        'template_sha256':integration['global_template_sha256'],'local':checks,
        'mutation_controls_rejected':controls,'all_eight_global_scalar_columns':True,
        'bank_owners_and_padding_exact':True,'paid_profile':dict(sorted(H.items())),
        'two_rational_moment_engines':True,'complex_b':str(b),
        'next_b_grid_rejected':True,
        'scope':'Independent finite replay; retains the written generic scalar-interface lemma and inherited all-size/analytic assumptions.'}
(OUT/'INDEPENDENT-REPLAY.json').write_text(json.dumps(result,indent=2)+'\n')
print('PASS independent local/global replay and two exact moments',flush=True)

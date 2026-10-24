#!/usr/bin/env python3
"""One actual paid H3 split and owned clean prefix, source20bb only.
Apache-2.0; substantial OpenAI Codex assistance. Credits native #4610,
#4712 arbitrary-owner protocols and the retained exact phase compiler.
"""
from pathlib import Path
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
import ast,gzip,json,os,subprocess,sys,types
HERE=Path(__file__).resolve().parent
PIN='20bb93cd990d2ff683e4d0fc56b87a42cd5d3296'
WORD='research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz'
CE='research/t74-native-fast/vendor/native/new/code/borrow/vendor/clifford/clifford_exact.py'
PRUNE='research/kappa-function-composition/complex/prune_native.py'
IV='research/higher-moment-strictification/verify.py'
VAL='research/kappa-round3-warp-20261022/NATIVE-VALIDATION.json'
def need(x,m):
    if not x:raise ValueError(m)
def read(p):return subprocess.check_output(['git','show',PIN+':'+p],env={**os.environ,'GIT_NO_REPLACE_OBJECTS':'1'})
raw={p:read(p)for p in(WORD,CE,PRUNE,IV,VAL)}
need(sha256(raw[WORD]).hexdigest()=='7679daa4ec6a40f56fc7f0202379a6f454310e94945aba4f48beaaaafb838d05','frozen4610 word')
p=json.loads(gzip.decompress(raw[WORD]));c=p['canonical'];w=p['programs']['backward'];f=c['frames']
old_validation=json.loads(raw[VAL])
need(old_validation['actual_word_canonical_sha256']==sha256(gzip.decompress(raw[WORD])).hexdigest(),
    'retained original632-column endpoint receipt binds exact payload')
need(old_validation['native']['backward']['independent_persistent_columns']==632
    and old_validation['native']['backward']['arbitrary_owned_C0_cleared'],
    'authenticated retained all-owner original endpoint coverage')
old=['climb','warp_retimed',496,911,1,3]
need(w[15372]==old and c['start'][496]==0 and c['final'][496]==1,'one actual H3 primitive and wholeH9 helper')
need(c['ports'][39]==162 and c['final'][151]==181,'actual selected mainY interface')
def writes(e,r):return(e[0]=='scalar'and e[1][1]==['L',r])or(e[0]=='warp'and e[1]==['L',r])
need(max(i for i,e in enumerate(w)if writes(e,496))==13182,'helper clean before terminal child')
need(max(i for i,e in enumerate(w)if writes(e,151)or(e[0]=='climb'and e[2]==151))==14597,'Y already final and never written again')
need(all(r[1]==0 for e in w if e[0]=='scalar'for r in e[1][1:3]if isinstance(r,list)and r[0]=='C'),'new ownedC1 does not alias oldC0')
ce=types.ModuleType('actual_h3_split');sys.modules[ce.__name__]=ce
exec(compile(raw[CE],CE,'exec'),ce.__dict__)
defs=[n for n in ast.parse(raw[PRUNE]).body if isinstance(n,ast.FunctionDef)and n.name=='conjugate'];env={'need':need}
exec(compile(ast.Module(body=defs,type_ignores=[]),PRUNE,'exec'),env)
def bar(op):return env['conjugate'](ce,op)
def grade(op):return ce.rank([x for x,z,p in op.tab[op.n:]])
def same(a,b):return a.tab==b.tab and a.zero_state()==b.zero_state()
FU,FM,FV=[ce.canonical_frame(9,f[j])for j in(911,181,1)]
records={}
for direction,conv in [('forward',lambda x:x),('backward_raw_dual',bar)]:
    original=conv(FU.adjoint().then(FV));first=conv(FU.adjoint().then(FM));second=conv(FM.adjoint().then(FV))
    need([grade(z)for z in(original,first,second)]==[3,2,1],'actual physical child ranks')
    need(same(first.then(second),original),'all-input signed-tableau and absolute-phase replacement')
    lowered={}
    for tag,z in [('old_H3',original),('new_H2',first),('new_H1',second)]:
        recipe,reconstructed=ce.lower_child(z);need(same(z,reconstructed),'literal child decomposition phase')
        lowered[tag]=dict(rank=grade(z),literal_word=z.circuit,signed_tableau=z.tab,recipe=recipe)
    records[direction]=lowered
need(not same(FM.adjoint().then(FV),ce.cgate(9,162))and not same(FM.adjoint().then(FV),ce.cgate(9,162,-1)),
    'do not replace actual tail by bare rootQ in either sign')

# Independent reverse pullbacks bind the prefix to actual arbitrary owners.
def pullback(role,cut):
    state={('L',role):{():Q(1)}}
    def add(t,b,k):
        a=state.setdefault(t,{})
        for u,v in b.items():
            a[u]=a.get(u,Q(0))+k*v
            if not a[u]:del a[u]
        if not a:state.pop(t,None)
    for e in reversed(w[:cut]):
        if e[0]=='scalar':
            g=e[1];t=tuple(g[1]);v=dict(state.get(t,{}))
            if not v:continue
            if g[0]=='add':add(tuple(g[2]),v,Q(g[3],g[4]))
            elif g[0]=='scale':state[t]={u:k*Q(g[2],g[3])for u,k in v.items()}
            elif g[0]=='copy':state.pop(t,None);add(tuple(g[2]),v,Q(1))
            elif g[0]=='clear':state.pop(t,None)
        elif e[0]=='warp':
            t=tuple(e[1]);v=state.get(t,{})
            state[t]={(u[1:]if u and u[0]==-e[2]else(e[2],)+u):k for u,k in v.items()}
            if not state[t]:state.pop(t,None)
    return state
need(pullback(496,15372)=={('L',496):{():Q(1)}},'clean arbitrary helper prefix before old child')
need(pullback(151,15372)=={('L',151):{():Q(1)}},'simultaneous clean arbitrary Y field')
xrow=pullback(39,len(w))
need(xrow.get(('L',151))=={():Q(-1)},'actual backward mainX39 cross coefficient from originalY151')
patch=dict(direction='backward',replace_index=15372,expected_event=old,
    initialize_owned=['scalar',['clear',['C',1]],181],
    replacement=[['climb','one_terminal_h3_split',496,911,181,2],
        ['scalar',['copy',['C',1],['L',496]],181],
        ['climb','one_terminal_h3_split',496,181,1,1]],
    clear_after_new_consumer=['scalar',['clear',['C',1]],181],owned_entry_zero=True)
(HERE/'PATCH.json').write_text(json.dumps(patch,indent=2)+'\n')
P=Counter(e[5]for e in p['programs']['forward']if e[0]=='climb');P.update(e[4]for e in p['programs']['forward']if e[0]=='center')
supplier_new=P.copy();supplier_new[3]-=1;supplier_new[2]+=1;supplier_new[1]+=1
H=Counter(len(f[c['final'][r]])-len(f[c['start'][r]])for r in range(224,632))
paid=Counter({r:2*n for r,n in P.items()});newpaid=paid.copy();newpaid[3]-=1;newpaid[2]+=1;newpaid[1]+=1
targets=Counter({r:2*n for r,n in H.items()});targets[17]=224
coeff={r:targets.get(r,0)-paid.get(r,0)for r in set(targets)|set(paid)if targets.get(r,0)!=paid.get(r,0)}
need(all((v<0 and r<=5)or(v>0 and r>5)for r,v in coeff.items()),
    'old raw relaxation normalized by5^t increases throughout the interval')
iv={'__name__':'one_child_split_intervals','__file__':str(HERE/'pinned_iv.py')};exec(compile(raw[IV],IV,'exec'),iv)
def sub(a,b):return a[0]-b[1],a[1]-b[0]
comparisons={}
for C in(Q('.0030217758'),Q('.0034')):
    t=1-C;two=iv['power'](2,t);delta=sub((two[0]+1,two[1]+1),iv['power'](3,t))
    margin=sub(iv['moment'](dict(targets),t),iv['moment'](dict(newpaid),t))
    need(delta[0]>0 and margin[0]>31,'positive small split cost with complete raw profile still positive')
    comparisons[str(C)]=dict(split_surcharge=list(map(str,delta)),new_margin=list(map(str,margin)))
out=dict(status='PASS_ONE_ACTUAL_H3_SPLIT_CLEAN_PREFIX_NOT_CONSUMER',source_commit=PIN,
    source_sha256={k:sha256(v).hexdigest()for k,v in raw.items()},source_event=15372,
    helper=496,helper_start=0,helper_final=1,mainY_role=151,port=39,q=162,
    before_chart=911,middle_chart=181,after_chart=1,chart_bases={j:f[j]for j in(911,181,1)},
    phases=records,allwidth='literal columnwise identities with exact shared canonical-frame cancellation, not a tensor of sums',
    new_observation='C1=bar(F181) h496; Y151=bar(F181) y151 at simultaneous cut',
    actual_main_cross=dict(source_X_role=39,source_Y_role=151,logical_coefficient=-1,
        physical_coefficient='-bar(F9)',relative_to_Y_exit='-Gamma Y151, Gamma=bar(F9)bar(F181)^-1',
        phase_identity='Exact same canonical endpoint frames as retained raw-dual H1 tail; no bareQ substitution.',
        limitation='One source cross coefficient, not proof of a free arbitrary query or a whole multi-input consumer.'),
    helper_original_return='bar(F9) h496',other_original_owners_unchanged=True,
    all_owner_equations='For every old632-input vector, after the two child calls the old live state equals the oldH3 state exactly; COPY reads only; all later old events are identical. C1 retains observation until consumer, then CLEAR returns0.',
    inherited_owned_C0_unchanged=True,new_owned_C1=dict(initial=0,at_cut='bar(F181)h496',after_clear=0),
    actual_paid_delta={1:1,2:1,3:-1},productive_delta={},paid_profile=dict(newpaid),target_profile=dict(targets),
    original_supplier_paid_profile=dict(P),changed_supplier_paid_profile=dict(supplier_new),
    original_supplier_scalar_allowance=old_validation['native']['backward']['real_scalar_allowance'],
    inherited_formal_prefix_l1=old_validation['native']['backward']['max_formal_prefix_l1'],
    cost_comparisons=comparisons,whole_C_interval=['.0030217758','.0034'],
    cost_scope='Raw price-only relaxation:224H17 main targets remain unrealized. The exact physical achievement changes one old632-input supplier paid child; it is not a complete two-FULL caller.',
    uniform_positive_bound='splitdelta<=3-3^t<=.0306; oldmargin>31 oninterval, hence newmargin>30.9694',
    finite_bill=dict(extra_storage_fields=1,ambient=17,N='2^(17f)',
        initialize_passes=1,COPY_passes=1,CLEAR_passes=1,
        conservative_new_monomial_passes_ignoring_old_removed_normalizers=16,
        conservative_total_extra_full_array_passes=19,
        COPY_and_CLEAR_exact=True,precision='COPY adds no arithmetic rounding. Allocate each new unitary child error<=oldchild_error/3: combined<=2e/3+e^2/9<e for0<e<=1. Concrete source precision/compiler/outer reserves not replayed.'),
    tail_is_not_bare_Q=True,productive_H9_not_subtracted=True,
    raw_duality_scope='Each forward/raw-dual local child split is checked separately. Added owned COPY/CLEAR access words are not asserted to be literal inverse-transposes of one another.',
    proof_coverage='Exact local9-axis signed tableau plus absolute phase, prefix pullbacks and authenticated retained632-input endpoint receipt. No fresh full632-column replay or complete mixed-target consumer.',
    one_resource_only=True,capacity112_claim=False,consumer_constructed=False,compiler_funded=False,
    no_transfer_to_4929=True,new_kappa=False)
(HERE/'RESULT.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items()if k not in('phases','chart_bases')},sort_keys=True))

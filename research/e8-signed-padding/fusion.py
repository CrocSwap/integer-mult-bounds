"""Compose PR395 signed prefixes with PR394 padding, with a fresh global invoice.
Rohan Arun with OpenAI Codex assistance. Apache-2.0; supplier notices retained.
"""
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter
import copy,gzip,hashlib,importlib.util,json,math,sys
ROOT=Path(__file__).resolve().parent
SOURCE=ROOT.parent/'e8-prefix-restoration'
BOOT=ROOT.parent/'e8-prefix-bootstrap'
sys.dont_write_bytecode=True
sys.set_int_max_str_digits(0)
sys.path.insert(0,str(SOURCE/'public/378/source/research/e8-complex-far-retiming/code'))
read=lambda p:json.loads(p.read_text())
readgz=lambda p:json.loads(gzip.decompress(p.read_bytes()))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
W=module('padding_word',ROOT/'vendor394/word.py')
E=module('padding_emit',ROOT/'vendor394/emit.py')
S=module('padding_scalar',ROOT/'scalar_compiler.py')
C=module('padding_clifford',SOURCE/'public/381/source/research/e8-nine-stage-kappa/complex377/work/odd-stages/clifford_exact.py')
def encode(x):
    if isinstance(x,Q):return {'numerator':x.numerator,'denominator':x.denominator}
    if isinstance(x,dict):return {str(k):encode(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)):return [encode(v) for v in x]
    return x

def mixed_recipe(frames,fid):
    n=len(frames[1]);local=C.canonical_frame(n,frames[fid]).adjoint().then(C.canonical_frame(n,frames[1]));old,_=C.lower_child(local)
    # One exterior coordinate plus n local coordinates; all other coordinates
    # are identity spectators. Relabel exterior n to bank coordinate m-1.
    lifted=C.ident(n+1)
    for e in local.circuit:
        if e[0]=='P':part=C.perm(n+1,tuple(e[1])+(1<<n,))
        elif e[0]=='D':part=C.diag(n+1,tuple(e[1])+(0,),tuple(e[2])+(0,))
        elif e[0]=='C':part=C.cgate(n+1,e[1],e[2])
        elif e[0]=='X':part=C.xgate(n+1,e[1])
        elif e[0]=='phase':part=C.Op(n+1,C.identity(n+1),[e])
        else:raise AssertionError(e)
        lifted=lifted.then(part)
    pad=C.cgate(n+1,1<<n);fused=lifted.then(pad);reverse=pad.then(lifted)
    assert fused.tab==reverse.tab and fused.zero_state()==reverse.zero_state()
    recipe,compiled=C.lower_child(fused)
    assert recipe['rank']==old['rank']+1 and compiled.tab==fused.tab and compiled.zero_state()==fused.zero_state()
    return dict(old_frame=fid,new_frame=1,local_rank=old['rank'],paid_rank=recipe['rank'],active_coordinates=n+1,local_padding_coordinate=n,recipe=recipe,exact_global_phase=True,tensor_commutation=True)

def build(baseline,out):
    assert __debug__
    baseline=Path(baseline).resolve();out=Path(out).resolve();assert not out.exists();out.mkdir(parents=True)
    prior=read(baseline/'RESULT.json');assert prior['status']=='PASS_FULL_SIGNED_PREFIX_AND_HETEROGENEOUS_COMPOSITION'
    assert Q(prior['kappa'])==Q(read(ROOT/'SOURCE.json')['baseline_kappa'])
    spec=read(ROOT/'SOURCE.json')
    for n,d in spec['vendor_files'].items():assert sha(ROOT/'vendor394'/n)==d,n
    old=readgz(SOURCE/'data/prefix18.json.gz');base=readgz(baseline/'candidate/candidate.json.gz');gates=base['A']+base['B'];oldgates=old['A']+old['B']
    free=read(ROOT/'vendor394/sinks-e8clean.json')
    for e in free:
        match=[i for i,g in enumerate(gates) if g==oldgates[e['cut_group']]];assert len(match)==1;e['cut_group']=match[0]
    hetero=read(baseline/'candidate/sink-audit.json')['accepted'];H={e['sink_helper']:e['frame'] for e in hetero};F={e['sink_helper'] for e in free};assert not F&set(H)
    word=W.insert(base,hetero+free);without=W.insert(base,hetero)
    # Independently regenerate the inherited bracket and compare every gate.
    legacy=W.insert(old,read(SOURCE/'data/sink-audit.json')['accepted']);pinned=read(SOURCE/'data/prewhite.json')
    for got,key in zip(E.prewhite(legacy,set(H)),['pre_target_dirty_cancellation_gates','pre_helper_inverse_gates','post_full_helper_clean_repair_gates']):
        assert got==[(t,s,Q(a,b)) for t,s,a,b in pinned[key]],key
    orig=E.replay_main(base,{i:{i:Q(1)} for i in range(E.N)});changed=E.replay_main(word,{i:{i:Q(1)} for i in range(E.N)})
    assert orig[:2*E.V]==changed[:2*E.V] and base['A']==word['A'] and base['ret']==word['ret'] and base['scat']==word['scat']
    pw=E.prewhite(word,set(H)|F);physical=read(baseline/'hetero/RESULT.json');oldlocal=readgz(baseline/'hetero/HETEROGENEOUS-TEMPLATE.json.gz')
    programs={};checks={};counts={};lowered={};controls=[];recipes={}
    def reject(name,fn):
        try:fn()
        except (AssertionError,KeyError,ValueError):controls.append(name)
        else:raise AssertionError('mutation accepted: '+name)
    for ori in ['forward','backward']:
        ev=list(E.emit(word,ori,H,F,pw));checks[ori]=E.validate(ev,word,ori,H,F)
        oldedges={(e[3],e[4]) for e in oldlocal['local_programs'][ori] if e[0]=='climb'}
        assert set(map(tuple,checks[ori]['edges']))==oldedges,'new ordinary Clifford edge'
        unfused=E.validate(list(E.emit(without,ori,H,set(),E.prewhite(without,set(H)))) ,without,ori,H,set())
        assert unfused['paid_hist']=={int(k):v for k,v in physical['local_profile'].items()}
        simple=[e for e in ev if e[0]=='scalar'];macros=[];stream=[]
        for e in simple:
            op=e[2]
            if op[0]=='add':op=op[:3]+(op[3].numerator,op[3].denominator);S.check_lowered_coefficient(op[3],op[4])
            macros.append(op);stream.extend((e[1],x) for x in S.lower_scalar(op))
        lowered[ori]=stream;counts[ori]=dict(scalar_macros=len(macros),real_component_primitives=2*len(stream))
        for e in ev:
            if e[0]=='climb_pad72':
                assert e[3]==1 and e[4]+1==e[5]
                if e[2] not in recipes:recipes[e[2]]=mixed_recipe(word['frames'],e[2])
                assert recipes[e[2]]['paid_rank']==e[5]
        ix=next(i for i,e in enumerate(ev) if e[0]=='climb_pad72');bad=copy.deepcopy(ev);bad[ix]=bad[ix][:-1]+(bad[ix][-1]-1,)
        reject(ori+':padding_not_paid',lambda:E.validate(bad,word,ori,H,F))
        bad=copy.deepcopy(ev);e=bad.pop(ix);j=max(i for i,x in enumerate(bad) if x[0]=='scalar' and x[1]=='main' and ('L',e[1]) in x[2][1:3]);bad.insert(j,e)
        reject(ori+':padding_before_last_use',lambda:E.validate(bad,word,ori,H,F))
        bad=copy.deepcopy(ev);j=next(i for i,x in enumerate(bad) if x[0]=='scalar' and x[1]=='cleanup');bad.insert(j,('scalar','cleanup',E.lift(min(F),0,Q(1),ori),'old1'))
        reject(ori+':cleanup_touches_fused_sink',lambda:E.validate(bad,word,ori,H,F))
        bad=copy.deepcopy(ev);j=next(i for i,x in enumerate(bad) if x[0]=='scalar' and x[1]=='old_response');x=bad[j];bad[j]=x[:2]+(x[2][:3]+(-x[2][3],),x[3])
        reject(ori+':wrong_precancellation',lambda:E.validate(bad,word,ori,H,F))
        programs[ori]=ev
    assert checks['forward']['paid_hist']==checks['backward']['paid_hist']
    banks=read(baseline/'HETEROBANKS.json');template=readgz(baseline/'hetero/GLOBAL-HETEROGENEOUS-TEMPLATE.json.gz');phases=read(baseline/'hetero/BANK-ENDPOINT-PHASE.json')
    assert template['banks']==banks['assignments'] and len(template['calls'])==288
    m=physical['m'];padcoord=m-1;routes=[[int(x,2) for x in rows] for rows in banks['route_recipes']]
    transpose=lambda A:[sum(((row>>i)&1)<<j for j,row in enumerate(A)) for i in range(m)]
    assert template['bank_placement_matrices']==routes and template['bank_owner_right_factors']==[transpose(A) for A in routes]
    assignment={(a['replica'],a['helper']):a for a in banks['assignments']};records=[]
    for call in template['calls']:
        for h in sorted(F):
            a=assignment[call['replica'],h];A=routes[a['orthogonal_route_id']]
            assert a['rank']==base['h'] and A[padcoord]==1<<padcoord and all(not(row>>padcoord&1) for i,row in enumerate(A) if i!=padcoord)
            owner=call['owners'][h];assert owner==[8*E.V*banks['replicas']+call['stage']*banks['banks_per_stage']+a['bank'],['helper',a['orthogonal_route_id']]]
            event=next(e for e in programs[call['orientation']] if e[0]=='climb_pad72' and e[1]==h)
            records.append(dict(stage=call['stage'],replica=call['replica'],helper=h,bank=a['bank'],owner=owner,route_id=a['orthogonal_route_id'],padding_coordinate=padcoord,old_frame=event[2],local_rank=event[4],paid_rank=event[5],phase_recipe=event[2]))
    keys={(a['stage'],a['bank']) for a in records};assert len(keys)==len(records)
    original_padding={(a['stage'],a['bank']):a for a in template['bank_padding']};assert keys<=original_padding.keys()
    remaining=[a for a in template['bank_padding'] if (a['stage'],a['bank']) not in keys]
    byframe={a['frame']:a['canonical_to_orthogonal_coordinate_adapter'] for a in phases['endpoints']}
    for ori,ev in programs.items():
        for i,e in enumerate(ev):
            if e[:2]==('adapter','canonical_to_bank_residual'):
                assert H[e[2]]==e[3];ev[i]=('rankzero_endpoint_adapter',e[2],e[3],copy.deepcopy(byframe[e[3]]))
    template['local']=dict(local_programs=programs,endpoint_frames=oldlocal['endpoint_frames'],new_phase_recipes=oldlocal['new_phase_recipes'],fused_child_phase_recipes=recipes,lowered_scalar_programs=lowered)
    template['bank_padding']=remaining;template['fused_padding']=records
    template['fusion_scope']='PR394 operator-level padding commutation under inherited arbitrary-dirty bank property; exact mixed child uses n+1 active coordinates and identity spectators.'
    def global_check(t):
        fused=t['fused_padding'];rk={(x['stage'],x['bank']) for x in fused};rest={(x['stage'],x['bank']) for x in t['bank_padding']}
        assert len(rk)==len(fused)==len(records) and not rk&rest and rk|rest==set(original_padding)
        assert t['bank_owner_right_factors']==[transpose(A) for A in t['bank_placement_matrices']]
        for x in fused:
            a=assignment[x['replica'],x['helper']];assert x['bank']==a['bank'] and x['route_id']==a['orthogonal_route_id'] and x['padding_coordinate']==padcoord
            A=t['bank_placement_matrices'][x['route_id']];assert A[padcoord]==1<<padcoord and x['paid_rank']==recipes[x['phase_recipe']]['paid_rank']
        for ori in programs:
            assert t['local']['local_programs'][ori]==programs[ori]
        assert t['cover_final_correction']['charged_calls']==physical['live']
    global_check(template)
    for name in ['missing_fusion','double_padding','wrong_route','wrong_rank','omit_cover']:
        bad=copy.deepcopy(template)
        if name=='missing_fusion':bad['fused_padding'].pop()
        elif name=='double_padding':bad['bank_padding'].append(original_padding[next(iter(keys))])
        elif name=='wrong_route':bad['fused_padding'][0]['route_id']=-1
        elif name=='wrong_rank':bad['fused_padding'][0]['paid_rank']-=1
        else:bad['cover_final_correction']['charged_calls']-=1
        reject(name,lambda:global_check(bad))
    calls=len(template['calls']);oldpaid={int(k):n for k,n in physical['local_profile'].items()};idle=Counter({int(k):n for k,n in physical['profile'].items()})
    for k,n in oldpaid.items():idle[k]-=calls*n
    idle[1]-=len(original_padding);assert all(n>=0 for n in idle.values())
    profile=Counter({int(k):calls*n for k,n in checks['forward']['paid_hist'].items()});profile.update(idle);profile[1]+=len(remaining)
    mass=sum(k*n for k,n in profile.items());live=physical['live'];stock_count=physical['physical'];assert mass==physical['rank_mass'] and m*live-mass==physical['deficit']
    delta={k:profile[k]-physical['profile'].get(str(k),0) for k in profile if profile[k]!=physical['profile'].get(str(k),0)}
    assert delta=={1:-len(records),2:-len(records),3:len(records)}
    # Recompute every scalar primitive. Retain the original conservative
    # nonlocal compiler reserve and additionally pay 64 groups per fusion.
    compiler=64*(m+1)**3;macros=max(x['scalar_macros'] for x in counts.values());lc=sum(checks['forward']['paid_hist'].values());adapters=16*(macros+lc+E.N+base['h'])+64*m
    local_bound=max(x['real_component_primitives'] for x in counts.values())+adapters*compiler
    orientations=Counter(a['orientation'] for a in template['calls']);scalar_total=sum(orientations[o]*x['real_component_primitives'] for o,x in counts.items());T=banks['replicas'];stages=len({a['stage'] for a in template['calls']});v=base['v'];h=base['h'];R=base['R']
    bridge_adds=2*stages*v*T;terminal_shifts=4*v*T;terminal_moves=2*4*v*T;cover=live
    nonlocal_items=4*v*T*stages+2*v*T*stages+2*stages*T*R+2160*T+stages*banks['banks_per_stage']+bridge_adds+terminal_shifts+terminal_moves+cover+stock_count+2*stages*T
    outside=8*nonlocal_items+64*m+64*len(records);pervertex=scalar_total+bridge_adds+terminal_shifts+terminal_moves+cover+(calls*adapters+outside)*compiler+64*stock_count
    d=(m-1)//2;group=2**(d*d)*math.prod(2**(2*i)-1 for i in range(1,d+1));stock=group*stock_count;s=group*mass;logical=group*pervertex+64;router=compiler*(logical+1)*(stock+1)**2;reserve=1<<100000;B=s+reserve;literal=2*(1<<30000)*stock**2+8*s+4*stock+4+32*m
    assert local_bound<1<<48 and logical<1<<6050 and router<1<<30000 and literal<reserve and 32*m*B*B<1<<210000 and m*m>2*max(profile)**2
    row=2*stock.bit_length()+9909+252;assert row<20161
    invoice=dict(local_primitive_bound=local_bound,pervertex=pervertex,scalar_program_counts=counts,additional_fusion_compiler_groups=64*len(records),physical_stock_bits=stock.bit_length(),router_bits=router.bit_length(),literal_bits=literal.bit_length(),required_C0_bits=(32*m*B*B).bit_length(),physical_row_coefficient=row,halving_degree=2)
    sys.path.insert(0,str(BOOT));from coarse_precision import certify,module as engine;from refine import refine
    root=engine('moment').certify(profile,m,live,True);coarse18=Q(int(Q(root['lower'])*10**18),10**18);coarse=certify(profile,m,live,coarse18)
    witness=refine(Q(coarse['coarse_lower']),Q(read(baseline/'bit/BIT-COMPOSITION-RECEIPT.json')['pricing']['bit_coarse']))
    k=Q(witness['kappa']);assert k>Q(prior['kappa']);u=Q(coarse['coarse_upper']);assert u/(1+u)<k+Q(1,10**18)
    result=dict(status='PASS_SIGNED_FUSION_LOCAL_GLOBAL_TEMPLATE_INVOICE_AND_EXACT_PRICE',kappa=str(k),kappa_float=float(k),baseline_kappa=prior['kappa'],gain=str(k-Q(prior['kappa'])),coarse=str(coarse18),profile=dict(sorted(profile.items())),profile_delta=delta,live=live,physical=stock_count,rank_mass=mass,deficit=m*live-mass,local_checks=checks,controls_rejected=controls,fused_occurrences=len(records),remaining_padding=len(remaining),invoice=invoice,strict_constraints=47,bit_fresh_replay_required=True,scope=template['fusion_scope'])
    for name,data in [('RESULT.json',result),('COARSE.json',coarse),('WITNESS.json',witness),('FUSED-RECIPES.json',recipes),('RELOCATED-SINKS.json',free)]: (out/name).write_text(json.dumps(data,indent=2)+'\n')
    template['inherited_source_hashes']=template.pop('source_hashes')
    template['source_hashes']={str(p):sha(p) for p in [ROOT/'fusion.py',ROOT/'scalar_compiler.py',ROOT/'vendor394/emit.py',ROOT/'vendor394/word.py',ROOT/'vendor394/sinks-e8clean.json',baseline/'RESULT.json',baseline/'HETEROBANKS.json',baseline/'candidate/candidate.json.gz',out/'RESULT.json',out/'RELOCATED-SINKS.json']}
    raw=json.dumps(encode(template),sort_keys=True,separators=(',',':')).encode();(out/'GLOBAL-FUSED-TEMPLATE.json.gz').write_bytes(gzip.compress(raw,mtime=0));assert readgz(out/'GLOBAL-FUSED-TEMPLATE.json.gz')==encode(template)
    (out/'WORD.json.gz').write_bytes(gzip.compress(json.dumps(word,sort_keys=True,separators=(',',':')).encode(),mtime=0))
    print(json.dumps({k:v for k,v in result.items() if k not in ['local_checks','profile']},indent=2),flush=True);return result
if __name__=='__main__':build(sys.argv[1],sys.argv[2])

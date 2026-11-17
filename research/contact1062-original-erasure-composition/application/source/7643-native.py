# SPDX-License-Identifier: Apache-2.0
"""Full authenticated native validation for the changed 485/1455 producer.

Based on retained #7480 verify_native.py, attributed there to Rohan Arun,
dillona, and OpenAI Codex assistance. Source closure is authenticated through
its unmodified source.py. Every engine adaptation is counted and logged.
All inventories, prices, grids, envelopes, and physical checks are freshly
computed for the literal candidate. This does not select a public frontier.
"""
from pathlib import Path
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256
from types import ModuleType
import sys,json,gzip,subprocess,tempfile,io,contextlib,time
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
SOURCE=ROOT/'inputs/pr7480'
CANDIDATE=ROOT/'producer54/reroute'
sys.path.insert(0,str(SOURCE))
from source import read,load,sources,canonical,need
from construct import construct
from derive_grid import derive
from verify_native import normalized,delta,rejects,forward_endpoint

EXPECTED='dcd797e45b6d4b74411a8a73a9b6e8247bb2ea8744924332b0dd43db3e219f02'
BASELINE='5044adee019f073f286789ccb688ffca76d42b60518242bb4daea818d33d337a'
PATCHES=[]
TIMINGS=[]
def module(name,path,edits=()):
    raw=path.read_text();record={'module':name,'source_name':path.name,'source_sha256':sha256(raw.encode()).hexdigest(),'edits':[]}
    for before,after in edits:
        count=raw.count(before);need(count==1,'Unique adaptation '+repr(before))
        raw=raw.replace(before,after)
        record['edits'].append({'before':before,'after':after,'occurrences':count})
    record['adapted_sha256']=sha256(raw.encode()).hexdigest();PATCHES.append(record)
    obj=ModuleType(name);obj.__file__=str(path);sys.modules[name]=obj
    exec(compile(raw,str(path),'exec'),obj.__dict__)
    return obj

def checkpoint(stage,data=None):
    now=time.time();TIMINGS.append({'stage':stage,'elapsed_seconds':now-STARTED})
    (HERE/'CHECKPOINT.json').write_text(json.dumps(normalized({'stage':stage,'word_canonical_sha256':EXPECTED,'data':data,'timings':TIMINGS}),indent=2)+'\n')
    print('PASS',stage,flush=True)

def charts(vendor,word):
    compiler=load('helper757_chart_compiler',vendor/'frozen/clifford_exact.py')
    interpreter=load('helper757_chart_interpreter',vendor/'frozen/native_verify.py')
    before=read(ROOT/'frozen-composition/7481-WORD.json.gz')
    need(sha256(canonical(before)).hexdigest()=='64fca675b91298868e12f09423b47e0c2327cba7095e35c8919c1953b4ed68b8','Exact #7481 physical comparator')
    routes=lambda w:{i:[tuple(e[2:4])for e in w['program']if e[0]=='MOVE'and e[1]==i]for i in range(w['public'])}
    old_routes,new_routes=routes(before),routes(word)
    changed=[i for i in old_routes if old_routes[i]!=new_routes[i]]
    affected={pair for i in changed for pair in old_routes[i]+new_routes[i]}
    contact_ranks={(3,373):2,(3,618):3,(373,618):1,(373,733):2,(373,913):5,(618,733):1,(618,913):4}
    contact_maps={}
    incumbent_chart_path=ROOT/'frozen-composition/7642-WORD.json.gz'
    incumbent_chart_word=read(incumbent_chart_path)
    need(sha256(canonical(incumbent_chart_word)).hexdigest()=='aa83ede3e5833d43606d711068619db0dc28cbcd858dd11e8e89da6d09883916','Exact #7642 phase comparator')
    for role in (134,329):
        old_role_pairs=[tuple(e[2:4]) for e in incumbent_chart_word['program'] if e[0]=='MOVE' and e[1]==role]
        affected |= set(old_role_pairs+new_routes[role])
    need(set(contact_ranks)<=affected,'Every old and new contact chart pair')
    need({(3,618),(716,807),(327,907),(618,913),(729,808),(3,603),(914,245),(245,127),(914,127)}<=affected,'All inherited and main-46 changed-route pairs')
    main46_maps={}
    main46_ranks={(914,245):1,(245,127):1,(914,127):2}
    report=[]
    for a,b in sorted(affected):
        ca,cb=(compiler.canonical_frame(9,tuple(word['frames'][f]))for f in(a,b))
        recipe,_=compiler.lower_child(ca.adjoint().then(cb))
        expected=interpreter.adjoint(interpreter.frame(word['frames'][a],9))+interpreter.frame(word['frames'][b],9)
        actual=interpreter.recipe(recipe)
        interpreter.equal(actual,expected,'Signed Pauli action and absolute phase')
        need(recipe['rank']==len(word['frames'][b])-len(word['frames'][a]),'Exact public ascent rank')
        for x,y in ((actual,expected),(interpreter.adjoint(actual),interpreter.adjoint(expected))):
            for column in range(512):need(interpreter.state(x,column)==interpreter.state(y,column),'Exact forward/adjoint Gaussian column')
        if (a,b) in main46_ranks:
            need(recipe['rank']==main46_ranks[a,b],'Exact main-46 pair rank')
            main46_maps[a,b]=actual
        if (a,b) in contact_ranks:
            need(recipe['rank']==contact_ranks[a,b],'Exact contact rank')
            contact_maps[a,b]=actual
        bad=deepcopy(recipe);bad['left']['phase']=(bad['left']['phase']+1)%4
        need(rejects(lambda:interpreter.equal(interpreter.recipe(bad),expected,'Wrong absolute phase')),'Reject wrong phase')
        report.append({'pair':[a,b],'rank':recipe['rank'],'columns':512,'adjoint_columns':512,'absolute_phase_verified':True})
    via=main46_maps[914,245]+main46_maps[245,127]
    direct=main46_maps[914,127]
    for x,y in ((via,direct),(interpreter.adjoint(via),interpreter.adjoint(direct))):
        interpreter.equal(x,y,'Exact main-46 composed signed action and absolute phase')
        for column in range(512):
            need(interpreter.state(x,column)==interpreter.state(y,column),'Exact main-46 composed Gaussian column')
    contact_compositions={}
    for label,left,right in (
        ('134_retained',contact_maps[3,618]+contact_maps[618,913],contact_maps[3,373]+contact_maps[373,913]),
        ('329_contribution_to_134',contact_maps[373,618]+contact_maps[618,913],contact_maps[373,913]),
        ('329_retained',contact_maps[373,618]+contact_maps[618,733],contact_maps[373,733]),
    ):
        for x,y in ((left,right),(interpreter.adjoint(left),interpreter.adjoint(right))):
            interpreter.equal(x,y,label+' exact signed Pauli action and phase')
            for column in range(512):
                need(interpreter.state(x,column)==interpreter.state(y,column),label+' exact Gaussian column')
        contact_compositions[label]={'columns':512,'adjoint_columns':512,'absolute_phase_verified':True}
    return {'all_affected_pairs':report,'changed_public_fields':changed,'wrong_phase_rejected':True,
            'main46_composed_columns':512,'main46_composed_adjoint_columns':512,
            'contact_compositions':contact_compositions}

def run():
    need(__debug__,'Assertions are proof obligations')
    new=read(CANDIDATE/'WORD.json.gz');need(sha256(canonical(new)).hexdigest()==EXPECTED,'Only final short candidate')
    previous=read(SOURCE/'NATIVE-RESULT.json')
    proposal=read(CANDIDATE/'RESULT.json')
    with sources()as(vendor,archive,rank9,bundle,parent,parent_word):
        old=construct(parent_word)
        need(canonical(old)==gzip.decompress((SOURCE/'WORD.json.gz').read_bytes()),'Regenerate frozen #7480 from authenticated #7334 closure')
        need(sha256(canonical(old)).hexdigest()==BASELINE,'Exact source word')
        emitted=[];skip=set(proposal['removed_old_indices'])
        for i,e in enumerate(old['program']):
            if i==proposal['insert_before_old_index']:emitted.extend(proposal['splice'])
            if i not in skip:emitted.append(e)
        incumbent=read(ROOT/'frozen-composition/7481-WORD.json.gz')
        need(incumbent==dict(old,program=emitted),'Rebuild exact #7481 from its predecessor')
        peer=read(ROOT/'frozen-composition/7604-WORD.json.gz')
        need(sha256((ROOT/'frozen-composition/7604-WORD.json.gz').read_bytes()).hexdigest()=='aae5a85746db1abc5145b993e9a9408076f34c53c4bb8040a99b6a39f2685527','Exact open #7604 comparator')
        program=peer['program']
        required={33517:['ADD',1143,757,'-1',3],38584:['MOVE',757,3,595,False],38585:['ADD',757,902,'-1',595],42714:['ADD',757,1557,'-2/3',595],42716:['MOVE',757,595,603,False],42717:['ADD',1255,757,'-1',603]}
        need(all(program[i]==e for i,e in required.items()),'Exact helper757 contacts')
        touches=[i for i in range(33518,42716)if 757 in(program[i][1:3]if program[i][0]in('ADD','COPY')else program[i][1:2])]
        need(touches==[38584,38585,42714],'No intervening read of helper757')
        emitted=[]
        for i,event in enumerate(program):
            if i==33518:emitted.append(['ADD',757,1255,'-1',3])
            if i==42716:emitted.extend([['MOVE',757,3,603,False],['ADD',757,1255,'1',603]])
            elif i not in(38584,38585,42714):emitted.append(event)
        baseline_path=ROOT/'frozen-composition/7605-WORD.json.gz'
        need(sha256(baseline_path.read_bytes()).hexdigest()=='37358c493d18ebc6be386aebb4c17529b38883674731f7009ef4e96a5313467d','Exact #7605 compressed word')
        baseline=read(baseline_path)
        need(baseline==dict(peer,program=emitted),'Rebuilt exact timed helper757 baseline from #7604')
        need(sha256(canonical(baseline)).hexdigest()=='e20f3f9240ac3f5fa4bbd7ab9b5550d660886901bb209f335409c329ac45d9cd','Exact #7605 canonical word')
        tape=baseline['program']
        plan_path=ROOT/'frozen-composition/7610-EDITS.json'
        need(sha256(plan_path.read_bytes()).hexdigest()=='a49e9962e32d13fd91cd8715d888bb1f4305003e63dd25485aa413905e00b8d9','Exact public #7610 edit list')
        plan=read(plan_path)
        need(len(tape)==76636==plan['base_events']+5 and not plan['append'],'Five-event shift and no appended operations')
        deletes={clock+5:event for clock,event in plan['delete']}
        inserts={clock+5 if clock else 0:events for clock,events in plan['insert_before']}
        need(sorted(deletes)==[45372,45373,45375,47958] and sorted(inserts)==[0,45377,47958],'Exact unique translated #7610 clocks')
        need(all(tape[i]==event for i,event in deletes.items()),'Exact deleted #7605 operations')
        need(tape[45376:45379]==[['MOVE',818,914,245,False],['ADD',818,1456,'1',245],['ADD',818,588,'1',245]],'Carrier and first outward reads')
        need(tape[47959]==['ADD',1019,46,'1',127],'Main 46 return before first chart-127 use')
        baseline_tagged=list(enumerate(tape))
        candidate_tagged=[]
        for i,event in baseline_tagged:
            candidate_tagged.extend((-(16*i+j+1),added) for j,added in enumerate(inserts.get(i,[])))
            if i not in deletes:
                candidate_tagged.append((i,event))
        incumbent_tagged=candidate_tagged
        incumbent_path=ROOT/'frozen-composition/7642-WORD.json.gz'
        incumbent=read(incumbent_path)
        need(incumbent==dict(baseline,program=[event for _,event in incumbent_tagged]),'Exact preserved main-46 transplant')
        need(sha256(canonical(incumbent)).hexdigest()=='aa83ede3e5833d43606d711068619db0dc28cbcd858dd11e8e89da6d09883916','Exact #7642 canonical word')
        contact_path=ROOT/'frozen-composition/7612-CONTACT.json'
        need(sha256(contact_path.read_bytes()).hexdigest()=='512dbbc3c5133b07400b720f55753e976aca48020e91b2d0086345802de1bc14','Exact #7612 port receipt')
        plan=read(contact_path)
        need(plan['incumbent_word_sha256']=='aa83ede3e5833d43606d711068619db0dc28cbcd858dd11e8e89da6d09883916' and plan['peer_head']=='e814828ee5b869c9468282d57ba28c364b07d130','Exact signed contact sources')
        original={int(clock):event for clock,event in plan['old_events'].items()}
        edits={int(clock):event for clock,event in plan['proposed_events'].items()}
        need(original=={41049:['MOVE',134,3,618,False],41050:['MOVE',329,373,618,False],
                         41051:['ADD',134,329,'-1/2',618],41142:['MOVE',329,618,733,False],
                         42086:['MOVE',134,618,913,False]},'Exact five original contact events')
        need(edits=={41049:['MOVE',134,3,373,False],41050:None,
                      41051:['ADD',134,329,'-1/2',373],41142:['MOVE',329,373,733,False],
                      42086:['MOVE',134,373,913,False]},'Exact one-ADD rechart and paid return changes')
        need(all(incumbent_tagged[i][1]==event for i,event in original.items()),'Literal #7642 clock and operand matches')
        roles=lambda event: set(event[1:3] if event[0] in ('ADD','COPY') else event[1:2])
        tape=incumbent['program']
        need([i for i in range(41049,42087) if 134 in roles(tape[i])]==[41049,41051,42086]
             and [i for i in range(41050,41143) if 329 in roles(tape[i])]==[41050,41051,41142],'No intervening observations of either recharted role')
        candidate_tagged=[(tag,edits.get(clock,event)) for clock,(tag,event) in enumerate(incumbent_tagged)
                          if edits.get(clock,event) is not None]
        need(new==dict(incumbent,program=[event for _,event in candidate_tagged]),'Exact literal contact word with unchanged metadata')
        need({k:v for k,v in new.items() if k!='program'}=={k:v for k,v in incumbent.items() if k!='program'},'Unchanged boundary metadata')
        G=load('producer_native_price_engine',bundle/'gate.py');sys.path.insert(0,str(rank9))
        helper_count=sum(previous['native']['helpers'].values())
        base=module('producer_rank9',rank9/'candidate_gate.py',(
            ('== 1080','== '+str(helper_count)),
            ('fresh_arbitrary_helpers=18 * 1080','fresh_arbitrary_helpers=18 * '+str(helper_count)),
            ('grid.word_run(word), grid.caller_run(caller)','grid.word_run(word, frac=25), grid.caller_run(caller)'),
            ("    exec(compile(src, str(env_path), 'exec'), env.__dict__)",'    assert src.count("(life, peak, owned_count) == (54, 43, 51)") == 1\n    src=src.replace("(life, peak, owned_count) == (54, 43, 51)","(life, peak, owned_count) == (74, 50, 68)")\n    exec(compile(src, str(env_path), \'exec\'), env.__dict__)')))
        I=base.independent(vendor)
        oldN,peerN,baselineN,incumbentN,N=map(I.native,(old,peer,baseline,incumbent,new))
        baseline_native_path=ROOT/'frozen-composition/7605-NATIVE.json'
        need(sha256(baseline_native_path.read_bytes()).hexdigest()=='0ada1e2e7de8887e6ebbd16cda3c8b9738d71873857657ff4fa6e180653cf888','Exact #7605 native receipt')
        baseline_receipt=read(baseline_native_path)
        need(normalized(baselineN)==baseline_receipt['native'] and baseline_receipt['word_canonical_sha256']=='e20f3f9240ac3f5fa4bbd7ab9b5550d660886901bb209f335409c329ac45d9cd','Independently reconstructed #7605 native inventory')
        fixed=('public','helpers','rises','owned_peak','lifetimes','bad_inputs')
        need(all(baselineN[k]==peerN[k] for k in fixed),'Fixed complete #7604 ownership and target contract')
        need(delta(baselineN['paid'],peerN['paid'])=={1:-2,2:1},'Exact inherited helper757 native saving')
        incumbent_native_path=ROOT/'frozen-composition/7642-NATIVE.json'
        need(sha256(incumbent_native_path.read_bytes()).hexdigest()=='49372e31656269fcf0d62db2d02739f9163dc5b2406f406cc701a873afb5b220','Exact #7642 native receipt')
        incumbent_receipt=read(incumbent_native_path)
        need(normalized(incumbentN)==incumbent_receipt['native'] and incumbent_receipt['word_canonical_sha256']=='aa83ede3e5833d43606d711068619db0dc28cbcd858dd11e8e89da6d09883916','Freshly reconstructed #7642 native inventory')
        need(all(incumbentN[k]==baselineN[k] and N[k]==incumbentN[k] for k in fixed),'Exact preserved ownership and target contracts')
        need(delta(incumbentN['paid'],baselineN['paid'])=={1:-2,2:1},'Inherited main-46 native saving')
        need(delta(N['paid'],incumbentN['paid'])=={1:-2,2:2,3:-1,4:-1,5:1},'Exact contact native saving')
        need(normalized(oldN)==previous['native'] and not N['bad_inputs'],'Recomputed source inventory and every candidate adjoint input')
        need(all(N[k]==oldN[k]for k in('lifetimes','owned_peak','rises')),'Unchanged complete owned contract')
        need(new['owned_fields']==old['owned_fields']==68,'Unchanged 68 owned labels')
        need(delta(N['helpers'],oldN['helpers'])=={} and delta(N['paid'],oldN['paid'])=={1:-11,2:-2,3:-1,5:1,6:1,7:1},'Exact paid delta and all helper targets')
        need(N['lifetimes']==74 and N['owned_peak']==50 and len(new['program'])==len(old['program'])+173,'Actual instruction and lifetime counts')
        checkpoint('authenticated source, complete frame and adjoint checks',{'native':N})
        derived,_=derive(new)
        need(derived['odd_scale']==1125 and derived['fractional_bits']==25,'Fresh minimal common grid')
        audit=module('producer_forward',archive/'audit_native.py',(('2**24','2**25'),('25 - (abs(value) & -abs(value)).bit_length()','26 - (abs(value) & -abs(value)).bit_length()')))
        baseline_forward,baseline_grid=audit.replay(baseline,baseline_tagged,set())
        forward,grid=audit.replay(new,candidate_tagged,set())
        incumbent_forward,incumbent_grid=audit.replay(incumbent,incumbent_tagged,set())
        need(forward==incumbent_forward==baseline_forward,'Exact #7642 and #7605 endpoints, versions, all CLEAR rows, COPY rows and owned events')
        need(len(forward[0])==1569 and len(forward[2])==74,'All rows and CLEARs checked')
        need(delta(incumbent_grid['opcodes'],baseline_grid['opcodes'])=={'ADD':11,'MOVE':-1},'Inherited main-46 complete opcode counts')
        need(delta(grid['opcodes'],incumbent_grid['opcodes'])=={'MOVE':-1},'Exact contact opcode counts and unchanged scalar counts')
        forward_receipt=forward_endpoint(new,forward[0])
        forward_receipt['copy_guards_checked']=len(forward[3])
        forward_receipt['owned_clear_rows_checked']=len(forward[2])
        need(grid['odd_grid_lcm']==1125 and grid['owned_rise_mass']==56,'Fresh exact grid and owned ascent')
        need(grid['dyadic_height']==derived['fractional_bits'] and grid['maximum_scaled_mass']==derived['scaled_maximum_mass'],'Independent integer and rational grid agreement')
        checkpoint('complete forward grid, COPY guards and all public/owned endpoints',{'grid':grid,'derived_grid':derived})
        caller_path=rank9/'dyadic/CALLER.json';C=read(caller_path)
        need(sha256(caller_path.read_bytes()).hexdigest()==G.CALLER,'Exact 18-stage ingredient caller')
        symbolic=I.caller(C)
        need(not symbolic['bad_outputs'] and normalized(symbolic)==previous['caller'],'Full retained ingredient caller')
        before=I.invoices(old,C,oldN);invoice=I.invoices(new,C,N)
        need(normalized(before)==previous['invoice'],'Recomputed complete source ingredient invoice')
        unadjusted=I.ordinary(old,C,oldN);ordinary=I.ordinary(new,C,N)
        routes=previous['ordinary']['caller_items']['B']['fused_routes'];route_delta=routes-unadjusted['caller_items']['B']['fused_routes']
        surcharge=0
        for e in C['events']:
            if e[0]=='B'and e[1]in('ADD','SCALE'):
                q=Q(e[4]if e[1]=='ADD'else e[3]);a,d=abs(q.numerator),q.denominator
                surcharge+=4*(a.bit_length()+d.bit_length()+1+(a.bit_count()if e[1]=='ADD'else 0))
        surcharge*=len(C['types']['B']['ports'])
        need(surcharge==previous['ordinary']['extra_B_scalar_surcharge'],'Fresh caller scalar surcharge')
        need(unadjusted['conservative_total']+route_delta+surcharge==previous['ordinary']['conservative_total'],'Complete source ordinary bill')
        ordinary['caller_items']['B']['fused_routes']=routes
        for k in('caller_total','raw_upper','conservative_total'):ordinary[k]+=route_delta
        ordinary['extra_B_scalar_surcharge']=surcharge;ordinary['conservative_total']+=surcharge
        ordinary['margin_to_billion']=10**9-ordinary['conservative_total'];need(ordinary['margin_to_billion']>0,'Full ordinary allowance')
        gate,price=G.exact_price(vendor,archive,before,invoice,previous)
        (HERE/'INGREDIENT-PRICE.json').write_text(json.dumps(normalized({'before':before,'after':invoice,'gate':gate,'price':price,'ordinary':ordinary}),indent=2)+'\n')
        manifest=read(vendor/'INDEPENDENT-SOURCES.json');P=load('producer_bit_binding',archive/'verify.py');P.bit_binding(I,manifest)
        precision=base.precision(vendor,new,C,gate,manifest)
        need(precision['word']['odd_scale_lcm']==1125 and precision['word']['dyadic_height']==25,'Fresh ingredient precision')
        checkpoint('complete ingredient invoices, both directed prices, all outer gates and precision',{'gate_claim':gate['claim'],'ordinary':ordinary['conservative_total'],'context_c':precision['context_c']})
        chart_receipt=charts(vendor,new)
        controls={}
        for name,event in(
            ('doubled_early_encoding',['ADD',1455,485,'2/3',3]),
            ('doubled_late_decoding',['ADD',1455,485,'-2/3',724]),
            ('doubled_824_compensation',['ADD',824,54,'-1',721]),
            ('doubled_1438_restoration',['ADD',1438,1439,'1',127])):
            need(new['program'].count(event)==1,'Unique producer correction')
            controls[name]=bool(I.native(new,mutant=new['program'].index(event))['bad_inputs'])
        bad=deepcopy(new);i=bad['program'].index(['MOVE',757,3,603,False]);bad['program'][i][2]=595
        controls['wrong_helper757_source']=rejects(lambda:I.native(bad))
        bad=deepcopy(new);bad['program'].remove(['MOVE',757,3,603,False])
        controls['missing_helper757_paid_move']=rejects(lambda:I.native(bad))
        direct=['MOVE',46,914,127,False]
        need(new['program'].count(direct)==1,'Unique literal main-46 direct MOVE')
        bad=deepcopy(new);bad['program'].remove(direct)
        controls['missing_main46_paid_move']=rejects(lambda:I.native(bad))
        bad=deepcopy(new);bad['program'][bad['program'].index(direct)][2]=245
        controls['wrong_main46_move_source']=rejects(lambda:I.native(bad))
        correction=['ADD',588,818,'1',245]
        i=45384
        need(new['program'][i:i+3]==[correction,['ADD',1456,818,'-1',245],['ADD',818,1456,'1',245]],'Exact coframe correction before first outward read')
        bad=deepcopy(new);del bad['program'][i]
        bad_tagged=candidate_tagged[:i]+candidate_tagged[i+1:]
        def replay_missing_correction():
            bad_forward,_=audit.replay(bad,bad_tagged,set())
            need(bad_forward==baseline_forward,'Removed correction changes the exact old rows')
        controls['missing_main46_coframe_correction']=rejects(replay_missing_correction)
        return_move=['MOVE',329,373,733,False]
        need(new['program'][41141]==return_move and new['program'].count(return_move)==1,'Unique literal role329 return')
        bad=deepcopy(new);bad['program'].remove(return_move)
        controls['missing_contact_paid_return']=rejects(lambda:I.native(bad))
        contact_index=41050
        need(new['program'][contact_index]==['ADD',134,329,'-1/2',373],'Literal recharted signed ADD')
        bad=deepcopy(new);bad['program'][contact_index][-1]=618
        controls['wrong_contact_chart']=rejects(lambda:I.native(bad))
        bad=deepcopy(new);del bad['program'][contact_index]
        bad_contact=candidate_tagged[:contact_index]+candidate_tagged[contact_index+1:]
        def replay_missing_contact():
            bad_forward,_=audit.replay(bad,bad_contact,set())
            need(bad_forward==incumbent_forward,'Omitted contact changes exact output or retirement')
        controls['missing_contact_add']=rejects(replay_missing_contact)
        bad=deepcopy(new);i=bad['program'].index(['MOVE',485,3,724,False]);bad['program'][i][2]=721
        controls['wrong_move_source']=rejects(lambda:I.native(bad))
        bad=deepcopy(new);bad['final'][485]=721
        controls['wrong_output_frame']=rejects(lambda:I.native(bad))
        owned=module('producer_owned_census',vendor/'retained/query-only-precision-envelope/envelopes.py',(('(life, peak, owned_count) == (54, 43, 51)','(life, peak, owned_count) == (74, 50, 68)'),))
        need(owned.validate_word(new)['lifetimes']==74,'Fresh owned census from envelope validator')
        bad=deepcopy(new);bad['program']=[['INIT',1501,724],['CLEAR',1501,724]]+bad['program']
        controls['extra_uncharged_owned_lifetime']=rejects(lambda:owned.validate_word(bad))
        grid_engine=module('producer_grid_controls',vendor/'retained/odd-native-common-grid/independent_bounds.py')
        controls['insufficient_odd_grid']=rejects(lambda:grid_engine.word_run(new,375,25))
        controls['insufficient_fractional_grid']=rejects(lambda:grid_engine.word_run(new,1125,24))
        need(all(controls.values()),'Every corruption control rejected')
        physical_checks=[]
        with tempfile.TemporaryDirectory(prefix='producer-physical-')as tmp:
            path=Path(tmp)/'word.json.gz';path.write_bytes(gzip.compress(canonical(new),mtime=0))
            for command,args in[(vendor/'frozen/verify_host3_odd.py',[path,'1125']),(vendor/'frozen/physical.py',[path,vendor/'frozen/clifford_exact.py','1000000009','11'])]:
                with(HERE/(command.name+'.log')).open('w')as stream:
                    subprocess.run([sys.executable,'-I','-B','-X','pycache_prefix='+str(ROOT/'isolated/pycache'),str(command),*map(str,args)],stdout=stream,stderr=subprocess.STDOUT,check=True)
                physical_checks.append(command.name)
                print((HERE/(command.name+'.log')).read_text(),end='',flush=True)
            engine=module('producer_signed_routes',rank9/'physical_child.py',(('cca66a7ec924bab47ccd1410968d16e071a01dc6110b5c08040bd207f753d066',EXPECTED),))
            capture=io.StringIO()
            with contextlib.redirect_stdout(capture):engine.main(path,vendor/'data/caller.json',caller_path)
            signed_routes=json.loads(capture.getvalue())
            need(signed_routes['status']=='PASS_PHYSICAL_RANK9_ALGEBRA'and signed_routes['paid_calls']==32,'Signed physical fields')
            need(1000*sum(len(row['caller_fields'])*row['ordinary_elementary_units']for row in signed_routes['bindings'])==routes,'Actual signed-route elementary charge')
        checkpoint('all affected Gaussian columns and absolute phase, finite physical replay and signed routes')
        return normalized(dict(status='PASS_CONTACT134_329_COMPLETE_NATIVE',source_head='58a9d052143f5d85295ed2d0163591c47f89a331',source_word_canonical_sha256=BASELINE,word_canonical_sha256=EXPECTED,native=N,forward=forward_receipt,grid=grid,derived_grid=derived,caller=symbolic,invoice=invoice,ordinary=ordinary,gate=gate,price=price,precision=precision,charts=chart_receipt,controls=controls,physical_checks=physical_checks,signed_routes=signed_routes,adapter=PATCHES,timings=TIMINGS,limitations=['Five inherited framework assumptions remain.','Source-aware retained engines are not independent human/formal acceptance.','The complete 17-stage signed application is checked separately.']))

if __name__=='__main__':
    STARTED=time.time();result=run()
    (HERE/'NATIVE-RESULT.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    print(result['status'],result['price']['claim_decimal'],flush=True)

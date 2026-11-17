#!/usr/bin/env python3
"""E4 source-bound native operator and complete route-column qualification.

Ingredient native gate only. No certificate rank or signed-caller admission.
Requires reviewed external one-run controller; do not launch directly.
Based on the executed #7627 run.py and its retained #7480 source closure.
"""
import copy, gzip, hashlib, importlib.util, json, os, signal, sys, time
from pathlib import Path
from types import ModuleType

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
WORK=ROOT/'outputs/kappa-swarm30-20261116/signed-completion-run/case/work'
E4=ROOT/'outputs/kappa-target368-20261116/agents/e4-direct-204'
SRC=WORK/'inputs/pr7480'
PHYSICAL=HERE.parent/'e4-native-physical/physical_leaf.py'
ECONOMICS=HERE.parent/'e4-native-economics/economics_leaf.py'

def need(ok,msg):
    if not ok: raise ValueError(msg)
def sha(raw): return hashlib.sha256(raw).hexdigest()
def canonical(obj): return json.dumps(obj,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()
def read_pinned(path, expected):
    need(path.is_file() and not path.is_symlink(), 'missing or symlinked input '+str(path))
    raw=path.read_bytes(); need(sha(raw)==expected,'input hash mismatch '+str(path)); return raw
def word(path, compressed, canonical_hash):
    value=json.loads(gzip.decompress(read_pinned(path,compressed)))
    need(sha(canonical(value))==canonical_hash,'canonical mismatch '+str(path)); return value
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path); module=importlib.util.module_from_spec(spec)
    sys.modules[name]=module;spec.loader.exec_module(module);return module
def normalized(x):return json.loads(json.dumps(x,default=str))
def reject(fn):
    try: fn()
    except (AssertionError,ValueError,KeyError,IndexError):return True
    raise ValueError('mutation accepted')

def run():
    need(__debug__,'assertions are proof obligations')
    pins={
      SRC/'source.py':'aa434e4c154a6e1e5ac9d13c3627953069da02b4e0f9e977d9a13bfd1e50aa95',
      SRC/'INPUTS.json':'6f3548f0015d2dea38522e47ad707ef305b30baccb79a73c1ec20c2ce84f2bfe',
      SRC/'derive_grid.py':'ceb7a44ef19d72a16db7b43c65c85910d965499d1715436011de32af5d39dbb0',
      PHYSICAL:'d005fb93208b5f58d9741e4384e56f08face18e30c488dab6694c89997f8bf7e',
      ECONOMICS:'6eb51ae2a36f99beb5f5d1d8a835ec8dde3c1d65d39c4f04a757caf0af473430',
      E4/'RUN-01.json':'0fc0ba9b143e956e41c30e89550b104b0c451b074aa4d35d5a384ecf957ff337',
      E4/'PARENT-01.TERMINAL.json':'39cac72f6709dc2f19ba12cb8b5b1aa6cb5d41452d8ee99d9013fca226e509e5',
      E4/'origins.json':'7fe3af176684321d4776d50b8fe2209db37889f128e65c940e9fb2770ba16ed2',
      E4/'candidate-certificates.json':'bda1d8b279c5962e579f261349c432fa511e66a7dc592e8a526353857c629c14',
      WORK/'producer54/validation_native/NATIVE-RESULT.json':'e6aa4d573d7db4b43263449420d8c160f83ba3f25ced5e0c767e8ce6f80d94f4',
    }
    raw={p:read_pinned(p,h) for p,h in pins.items()}
    exact=json.loads(raw[E4/'RUN-01.json']); terminal=json.loads(raw[E4/'PARENT-01.TERMINAL.json'])
    need(exact['status']=='PASS_LITERAL_EXACT_ONLY' and exact['candidate_canonical_sha256']=='1ea66c263faa51da704d7aae944f3371400afaf5df8a56904ab96319f6554e0e','exact gate')
    need(terminal['exit_code']==0 and terminal['wall_killed'] is False and terminal['authentication_errors']==[] and terminal['process_group_empty'] is True and terminal['post_authentication_pass'] is True and terminal['readback_limits_pass'] is True and terminal['candidate_gate_status']==exact['status'] and terminal['candidate_pinned_word']==exact['candidate_canonical_sha256'] and terminal['raw_hashes']['RUN-01.json']==sha(raw[E4/'RUN-01.json']),'exact terminal')
    defs={
      'base':(WORK/'frozen-composition/7481-WORD.json.gz','acee323696b18914bd863d55341f92112b48d3d1dc1443c276efb6c396fcc0a9','64fca675b91298868e12f09423b47e0c2327cba7095e35c8919c1953b4ed68b8'),
      'source7624':(WORK/'frozen-composition/7624-WORD.json.gz','bfe2a4fb54dd82940ba78d8b3efd4f587e3fc9e978ccfd48561199d2c9fb4887','c14f365d254598f6a2daa349b47f815d20c649f0439cc36897b531412e19a3de'),
      'source7626':(WORK/'frozen-composition/7626-WORD.json.gz','501876971143a0588403d653852b2305893d9b385be94f0f5d7134ebd97e03f0','df521d552dc35de6271e67655e4f9c466bc9247d37a5196b85613870209106a2'),
      'source7627':(WORK/'producer54/reroute/WORD.json.gz','3b0947df9d291308279a00e009f9c1f845151b5b40f81960a53a2949cb44c9a9','b80b6e74bff87c8d8160c5e121dac7c68df0827a7061847b896075417a346238'),
      'candidate':(E4/'candidate-word.json.gz','736d475843e2ca53cad8a193ed582926e2659abaec40895a41d55efd4fca532f','1ea66c263faa51da704d7aae944f3371400afaf5df8a56904ab96319f6554e0e')}
    words={k:word(*v) for k,v in defs.items()};old=words['source7627'];new=words['candidate']
    need({k:v for k,v in old.items() if k!='program'}=={k:v for k,v in new.items() if k!='program'},'source/candidate word boundary')
    prior=json.loads(raw[WORK/'producer54/validation_native/NATIVE-RESULT.json'])
    need(prior['status']=='PASS_SWARM30_COMPLETE_NATIVE' and prior['word_canonical_sha256']==defs['source7627'][2],'old native identity')
    rows=prior['charts']['all_affected_pairs']; hist=[]
    for x in rows:
        p=x['pair'];need(type(p) is list and len(p)==2 and all(type(i) is int and i>=0 for i in p) and x['columns']==512 and x['adjoint_columns']==512 and x['absolute_phase_verified'] is True,'old chart inventory')
        hist.append(tuple(p))
    need(hist and len(hist)==len(set(hist)), 'duplicate or empty historical inventory')
    pairmod=load('e4_pairs',HERE/'pairs.py'); manifest=pairmod.inventory(words,hist)
    need(manifest['comparisons']['source7627__candidate']['fields']==[490],'source to candidate route field')
    pairs={tuple(x) for x in manifest['full_validation_pairs']};need(len(pairs)==1090,'derived pair denominator')
    need({(594,725),(594,883),(725,883),(883,1009),(1009,176)} <= pairs-set(hist),'five omitted historical pairs')
    origins=json.loads(raw[E4/'origins.json']);need(len(origins)==len(new['program']) and origins.count(None)==21,'literal origin inventory')
    retained=[i for i in origins if i is not None]
    need(retained==[i for i in range(len(old['program'])) if i!=43041], 'complete ordered source origin mapping')
    changed={41629:['MOVE',490,594,883,False],41631:['ADD',1427,296,'-1',725]}
    for origin,event in zip(origins,new['program']):
        if origin is None:
            need(event[0]=='ADD' and event[-1]==127,'candidate repair operation')
        else:
            need(event==changed.get(origin,old['program'][origin]),'literal source projection')
    need(exact['candidate_gzip_sha256']==defs['candidate'][1] and exact['origins.json_sha256']==sha(raw[E4/'origins.json']) and exact['candidate-certificates.json_sha256']==sha(raw[E4/'candidate-certificates.json']),'candidate artifact binding')
    need(terminal['raw_hashes']['candidate-word.json.gz']==defs['candidate'][1] and terminal['raw_hashes']['origins.json']==exact['origins.json_sha256'] and terminal['raw_hashes']['candidate-certificates.json']==exact['candidate-certificates.json_sha256'],'candidate parent custody')
    sys.path.insert(0,str(SRC))
    source=load('e4_auth_source',SRC/'source.py')
    started=time.monotonic();timings=[]
    def budget(stage,deadline):
        elapsed=time.monotonic()-started
        need(elapsed<deadline,'cumulative stage deadline '+stage)
        timings.append({'stage_start':stage,'elapsed_seconds':elapsed,'cumulative_wall_deadline':deadline})
        signal.setitimer(signal.ITIMER_REAL,deadline-elapsed)
    budget('authenticated_source_native_and_grids',900)
    with source.sources() as (vendor,archive,rank9,bundle,parent,parent_word):
        # The loader authenticates nested archived bytes before returning vendor.
        independent=load('e4_native_independent',vendor/'independent.py')
        before=independent.native(old);after=independent.native(new)
        need(not before['bad_inputs'] and not after['bad_inputs'],'fresh adjoint inputs')
        need(normalized(before)==prior['native'],'source native reproduction')
        derive=load('e4_grid_derive',SRC/'derive_grid.py').derive
        grid_leaf=load('e4_grid_leaf',HERE/'grid_leaf.py')
        grids={'source':grid_leaf.one(old,derive,archive/'audit_native.py','source'),
               'candidate':grid_leaf.one(new,derive,archive/'audit_native.py','candidate')}
        need(grids['source']['grid']==prior['grid'] and grids['source']['derived_grid']==prior['derived_grid'],'fresh source grid reproduction')
        budget('ingredient_economics',1400)
        economics=load('e4_economics_leaf',ECONOMICS).run(vendor,archive,rank9,bundle,old,new,before,after,grids,prior)
        need(economics['status']=='PASS_E4_18_CALL_INGREDIENT_ECONOMICS_ONLY','fresh ingredient economics')
        budget('complete_chart_columns_and_phase',3300)
        compiler=load('e4_chart_compiler',vendor/'frozen/clifford_exact.py')
        interp=load('e4_chart_interpreter',vendor/'frozen/native_verify.py')
        charts=[]
        for a,b in sorted(pairs):
            ca,cb=(compiler.canonical_frame(9,tuple(new['frames'][f])) for f in (a,b))
            recipe,_=compiler.lower_child(ca.adjoint().then(cb))
            expected=interp.adjoint(interp.frame(new['frames'][a],9))+interp.frame(new['frames'][b],9)
            actual=interp.recipe(recipe)
            interp.equal(actual,expected,'Signed Pauli action and absolute phase')
            need(recipe['rank']==len(new['frames'][b])-len(new['frames'][a]),'exact ascent rank')
            for x,y in ((actual,expected),(interp.adjoint(actual),interp.adjoint(expected))):
                for column in range(512):need(interp.state(x,column)==interp.state(y,column),'Gaussian column')
            bad=copy.deepcopy(recipe);bad['left']['phase']=(bad['left']['phase']+1)%4
            need(reject(lambda:interp.equal(interp.recipe(bad),expected,'wrong phase')),'wrong phase control')
            charts.append({'pair':[a,b],'rank':recipe['rank'],'columns':512,'adjoint_columns':512,'absolute_phase_verified':True,'wrong_phase_rejected':True})
        budget('native_and_grid_mutations',3850)
        # E4-specific native controls exercise the actual literal engine.
        edge=['MOVE',490,594,883,False];need(new['program'].count(edge)==1,'unique E4 edge')
        i=new['program'].index(edge); bad=copy.deepcopy(new);bad['program'][i][2]=725
        controls={'wrong_E4_move_source':reject(lambda:independent.native(bad))}
        bad=copy.deepcopy(new);bad['program'].pop(i)
        controls['missing_E4_move']=reject(lambda:independent.native(bad))
        correction=origins.index(None);need(new['program'][correction][0]=='ADD','first E4 repair')
        controls['doubled_E4_first_repair']=bool(independent.native(new,mutant=correction)['bad_inputs'])
        # Retain all historical operator corruptions, testing the actual E4
        # literal word. Non-operator grid and ownership controls follow below.
        for name,event in (
            ('doubled_early_encoding',['ADD',1455,485,'2/3',3]),
            ('doubled_late_decoding',['ADD',1455,485,'-2/3',724]),
            ('doubled_824_compensation',['ADD',824,54,'-1',721]),
            ('doubled_1438_restoration',['ADD',1438,1439,'1',127])):
            need(new['program'].count(event)==1,'unique inherited correction '+name)
            controls[name]=bool(independent.native(new,mutant=new['program'].index(event))['bad_inputs'])
        def corrupt(name,event,action,value=None):
            need(new['program'].count(event)==1,'unique inherited event '+name)
            bad=copy.deepcopy(new);idx=bad['program'].index(event)
            if action=='remove':bad['program'].pop(idx)
            elif action=='source':bad['program'][idx][2]=value
            else:raise ValueError('unknown mutation')
            try:result=independent.native(bad)
            except (AssertionError,ValueError,KeyError,IndexError):return True
            return bool(result['bad_inputs'])
        for name,event,action,value in (
            ('wrong_helper757_source',['MOVE',757,3,603,False],'source',595),
            ('missing_helper757_paid_move',['MOVE',757,3,603,False],'remove',None),
            ('wrong_move_source',['MOVE',485,3,724,False],'source',721),
            ('wrong_902_1091_contact_source',['ADD',1091,902,'1/2',373],'source',1093),
            ('missing_902_paid_move',['MOVE',902,3,373,False],'remove',None),
            ('wrong_courier_1461_source',['MOVE',1461,755,757,False],'source',3),
            ('missing_courier_1461_move',['MOVE',1461,755,757,False],'remove',None),
            ('wrong_226_restop_source',['MOVE',226,260,906,False],'source',3)):
            controls[name]=corrupt(name,event,action,value)
        bad=copy.deepcopy(new);bad['final'][485]=721
        controls['wrong_output_frame']=reject(lambda:independent.native(bad))
        # The generic integer-grid leaf must reject reducing the fresh minimal
        # odd and dyadic scales. No predecessor fixed 1125/25 is assumed.
        grid_engine=load('e4_grid_rejects',vendor/'retained/odd-native-common-grid/independent_bounds.py')
        odd=grids['candidate']['derived_grid']['odd_scale'];frac=grids['candidate']['derived_grid']['fractional_bits']
        need(odd>1 and frac>0,'insufficient grid controls require nontrivial grids')
        factor=next((p for p in range(3,odd+1,2) if odd%p==0),None)
        need(factor is not None,'odd grid factor')
        controls['insufficient_odd_grid']=reject(lambda:grid_engine.word_run(new,odd//factor,frac))
        controls['insufficient_fractional_grid']=reject(lambda:grid_engine.word_run(new,odd,frac-1))
        owned_path=vendor/'retained/query-only-precision-envelope/envelopes.py'
        owned_raw=owned_path.read_text(); old_anchor='(life, peak, owned_count) == (54, 43, 51)'
        new_anchor=f"(life, peak, owned_count) == ({after['lifetimes']}, {after['owned_peak']}, {new['owned_fields']})"
        need(owned_raw.count(old_anchor)==1,'unique envelope ownership adaptation')
        owned_code=owned_raw.replace(old_anchor,new_anchor);owned=ModuleType('e4_owned_census')
        owned.__file__=str(owned_path);sys.modules[owned.__name__]=owned
        exec(compile(owned_code,str(owned_path),'exec'),owned.__dict__)
        need(owned.validate_word(new)['lifetimes']==after['lifetimes'],'independent owned life census')
        bad=copy.deepcopy(new);bad['program']=[['INIT',1501,724],['CLEAR',1501,724]]+bad['program']
        controls['extra_uncharged_owned_lifetime']=reject(lambda:owned.validate_word(bad))
        owned_adaptation={'source_sha256':sha(owned_raw.encode()),'adapted_sha256':sha(owned_code.encode()),'before':old_anchor,'after':new_anchor,'count':1}
        need(all(controls.values()),'E4 native mutation controls')
        budget('finite_physical_and_signed_routes',4100)
        physical=load('e4_physical_leaf',PHYSICAL);physical_results={}
        for label,w in (('source',old),('candidate',new)):
            run_dir=HERE/('PHYSICAL-'+label.upper());run_dir.mkdir(mode=0o700,exist_ok=False)
            physical_results[label]=physical.run(vendor,rank9,w,grids[label]['derived_grid']['odd_scale'],run_dir,
               authorization='INDEPENDENT_GO',caller_sha256=economics['caller_sha256'],
               expected_route_charge=economics['expected_route_charge'][label])
            need(physical_results[label]['status']=='PASS_FINITE_PHYSICAL_ONLY','fresh physical '+label)
    return normalized({'schema':'e4-native-paired/v1','status':'PASS_E4_INGREDIENT_NATIVE_ONLY',
       'source_word':{'canonical_sha256':defs['source7627'][2],'gzip_sha256':defs['source7627'][1]},
       'candidate_word':{'canonical_sha256':defs['candidate'][2],'gzip_sha256':defs['candidate'][1]},
       'native':{'source':before,'candidate':after},'grids':grids,'pair_manifest':manifest,'charts':charts,'controls':controls,'owned_adaptation':owned_adaptation,
       'economics':economics,'physical':physical_results,
       'elapsed_seconds':time.monotonic()-started,'timings':timings,'limitations':['18-call ingredient native and price only; the 17-call signed caller, certificate rank, supplier, independent external resource and custody receipts remain.']})

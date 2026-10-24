#!/usr/bin/env python3
"""Independent literal caller bill and exact funding. No candidate imports.

The complete backward source is authenticated reuse of our #5396 review;
the new caller census is derived here from literal records, not RESULT or
submitted counters. The standalone rational engine is our prior independent
engine, with only endpoint/reserve inputs changed. Apache-2.0.
Ali Romman and all retained source predecessors retain construction credit.
Substantial OpenAI Codex assistance; no human or kernel acceptance claimed.
"""
from pathlib import Path
from hashlib import sha256, sha1
from fractions import Fraction as Q
from collections import Counter
import ast, copy, gzip, json, subprocess, sys, resource, time, argparse
from exact_engine import evaluate, MODEL, need, enc

HERE=Path(__file__).resolve().parent
ROUND=HERE.parents[1]
ROOT=HERE.parents[2]
REPO=ROUND/'repository'
PKG='research/kappa-backward-controller-20261023'
HEAD='174fb211493b43a42210434083e9702b4fb7a2ce'
BASE='1ec1119972c9aefe42525172d07b332fcff81cb4'
PREVIOUS=ROOT/'swarm-execution-sol-high-20261024/repository/research/kappa-joint-relations-20261023'
WORD_SHA='7883ba0faefc96505bb61ca7312d588fa22dfe2164050c817c1718b8fa28693a'
PAYLOAD_SHA='2aee5e997df99726fc763e510d9cb69fbe4f86114dc8d2cd33ad26c6c462a21d'
OUT=HERE
MANIFEST=None

def sha(p): return sha256(p.read_bytes()).hexdigest()
def read(p):
    b=p.read_bytes(); return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
def blob(b): return sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
def hist(c): return {str(k):v for k,v in sorted(c.items()) if v}
def scalar(g):
    if g[0] in ('copy','clear'): return 2
    q=Q(*(g[3:] if g[0]=='add' else g[2:]));n,d=abs(q.numerator),q.denominator
    need(n>0 and d&(d-1)==0,'nonzero dyadic scalar required')
    if g[0]=='scale':
        need(n&(n-1)==0,'dyadic unit SCALE required')
        return 2*(abs(n.bit_length()-d.bit_length())+int(q<0))
    need(g[0]=='add','scalar alphabet')
    return 2*(3+n.bit_length()-1+n.bit_count()+d.bit_length()-1)

def authenticate():
    if MANIFEST is None:
        need(subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip()==HEAD,'wrong source checkout')
        rows=[]
        tree=subprocess.check_output(['git','ls-tree','-rz',HEAD,'--',PKG],cwd=REPO)
        for line in tree.split(b'\0'):
            if not line: continue
            meta,path=line.split(b'\t'); mode,kind,gitblob=meta.decode().split();path=path.decode()
            need(mode=='100644' and kind=='blob','package regular source file required')
            b=(REPO/path).read_bytes();need(blob(b)==gitblob,'candidate source differs from exact Git blob: '+path)
            rows.append({'path':path,'sha256':sha256(b).hexdigest(),'git_blob':gitblob})
    else:
        frozen=read(MANIFEST);need(frozen['head']==HEAD,'frozen source manifest head')
        rows=frozen['package_rows']
        for row in rows:
            b=(REPO/row['path']).read_bytes()
            need(sha256(b).hexdigest()==row['sha256'] and blob(b)==row['git_blob'],'source manifest row differs')
    need(len(rows)==11,'new package census changed')
    source=read(REPO/PKG/'SOURCES.json');need(source['base_commit']==BASE,'canonical base changed')
    inputs=[]
    verify=read(REPO/PKG/'VERIFY.json');expected=set(verify['inputs'])
    for row in source['files']:
        if row['usage']!='input':continue
        p=REPO/row['path'];b=p.read_bytes()
        need(sha256(b).hexdigest()==row['sha256'] and blob(b)==row['git_blob'],'source input changed: '+row['path'])
        inputs.append(dict(row))
    need({r['path'] for r in inputs}==expected and len(inputs)==11,'complete source input inventory')
    reuse=[]
    for name,digest in [('native.py','3c8efab1f830868c054d33391ee2f8bc74f9bae9c134edf5b455790eb674c1c4'),('WITNESS.json','24599011da06325e1012619b2b84a4dd3aceb90ab42d3caaf6414879e7d16591')]:
        p=REPO/PKG/name;old=PREVIOUS/name
        need(sha(p)==digest and p.read_bytes()==old.read_bytes(),'unchanged admitted backward supplier differs')
        reuse.append({'candidate_path':PKG+'/'+name,'prior_path':'research/kappa-joint-relations-20261023/'+name,'sha256':digest})
    oldword=PREVIOUS/'WORD.json.gz';need(sha(oldword)==WORD_SHA,'prior admitted literal word changed')
    need(sha256(gzip.decompress(oldword.read_bytes())).hexdigest()==PAYLOAD_SHA,'prior word payload changed')
    return {'head':HEAD,'canonical_base':BASE,'package_rows':rows,'input_rows':inputs,'unchanged_supplier':reuse,'prior_word':{'path':'research/kappa-joint-relations-20261023/WORD.json.gz','sha256':WORD_SHA,'payload_sha256':PAYLOAD_SHA}}

def source_keys():
    p=REPO/'research/pr4359-p7-padding/dependencies/compiler-refill/endpoint.py'
    node=next(n for n in ast.parse(p.read_bytes()).body if isinstance(n,ast.FunctionDef) and n.name=='ledger');keys={}
    for n in node.body:
        if isinstance(n,ast.Assign) and len(n.targets)==1 and isinstance(n.targets[0],ast.Name) and isinstance(n.value,ast.Dict): keys[n.targets[0].id]=[k.value for k in n.value.keys]
    return {'path':str(p.relative_to(REPO)),'sha256':sha(p),'strict':sorted(set(keys['checks'])|{k+'_above_kappa' for k in keys['margins']}),'functional':sorted(set(keys['functional'])|{'actual_new_BIT_stock_sublinear'})}

def invoice():
    auth=authenticate()
    controller=read(REPO/'research/joint-helper-lattice/CONTROLLER.json')
    changed=copy.deepcopy(controller);events=[];sites=[]
    for i,e in enumerate(controller['physical_events']):
        if e[0]=='LOCAL' and e[3] is False:
            _,stage,pair,_=e;x,y=2*pair,2*pair+1
            sites.append({'source_index':i,'stage':stage,'pair':pair})
            events.extend([['SIGNED_SWAP',y,x],['Q_POWER',x,2],['LOCAL',stage,pair,True],['SIGNED_SWAP',x,y],['Q_POWER',y,-2]])
        else:events.append(copy.deepcopy(e))
    changed['physical_events']=events;changed['wrapper_sites']=sites;del changed['invoice']
    def check_caller(payload): need(changed==payload,'literal caller differs from independent wrapper reconstruction')
    candidate=read(REPO/PKG/'CONTROLLER.json');check_caller(candidate)
    need([s['stage'] for s in sites]==[0,32] and len(sites)==2,'actual boundary replacement stages')
    old=read(PREVIOUS/'WORD.json.gz');base=read(REPO/'research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz');c=base['canonical']
    need(all(c[k]==v for k,v in old['canonical'].items()) and set(c)-set(old['canonical'])=={'local_profile'},'source frame inventory changed')
    owned=set(map(tuple,old['owned']['backward']));need(len(owned)==17,'raw backward owner count')
    def derive_local(program):
        local=Counter();allowance=0;kinds=Counter();ops=Counter()
        for e in program:
            kinds[e[0]]+=1
            if e[0] in ('climb','center'):
                a,b=e[-3:-1];rank=e[-1]
                need(type(rank)is int and rank>0 and abs(len(c['frames'][a])-len(c['frames'][b]))==rank,'paid frame delta mismatch')
                local[rank]+=1
            elif e[0]=='scalar':allowance+=scalar(e[1]);ops[e[1][0]]+=1
        return local,allowance,kinds,ops
    local,allowance,kinds,ops=derive_local(old['programs']['backward'])
    helpers=Counter(len(c['frames'][c['final'][r]])-len(c['frames'][c['start'][r]]) for r in range(224,len(c['start'])) if ('L',r) not in owned)
    P=Counter();T=Counter();counts=Counter();chron=[];main=Counter();idles=Counter()
    stages={e[1] for e in events if e[0]=='LOCAL'}
    for i,e in enumerate(events):
        counts[e[0]]+=1;paid=Counter();productive=Counter()
        if e[0]=='LOCAL':need(e[3] is True,'unfunded forward source used');paid.update(local);productive.update(helpers)
        elif e[0]=='QUERY_SHEAR':paid[1]+=112
        elif e[0]=='IDLE':
            need(len(set(e[2]))==len(e[2]) and all(type(s)is int and s in stages for s in e[2]),'idle stage set mismatch')
            paid[8*len(e[2])]+=224;idles.update(paid)
        else:need(e[0] in ('ADD','SIGNED_SWAP','Q_POWER'),'unknown caller charge')
        P.update(paid);T.update(productive);chron.append({'index':i,'event':e,'paid':hist(paid),'productive':hist(productive)})
    for term in changed['diagonal']:
        need(abs(term[0])==1 and all(x in (0,1) for x in term[1:]),'main rank term')
        main[1+8*sum(term[1:])]+=112
    T.update(main)
    need((counts['LOCAL'],counts['QUERY_SHEAR'],sum(P.values()),sum(T.values()))==(18,15,64116,10784),'complete invoice changed')
    need(sum(r*n for r,n in T.items())-sum(r*n for r,n in P.items())==752,'rank surplus changed')
    need((local,helpers,allowance)==(Counter({1:2193,2:412,3:510,4:127,5:40}),Counter({4:28,7:7,8:47,9:318}),158744),'literal supplier counts differ')
    routes={'source_paid':sum(local.values()),'two_helper_wrappers':2*408,'warps':kinds['warp'],'adapters':kinds['adapter'],'phases':kinds['phase'],'two_per_added_owned':2*(len(owned)-1)}
    route_units=1000*sum(routes.values());need(route_units+allowance<10**7,'source ordinary local cap fails')
    # Both scalar boundary programs and ordinary caller records fit32/port.
    boundary={}
    for side in ['left','right']:
        cost=0;prog=changed['boundaries'][side+'_program']
        for e in prog:
            if e[0]=='SWAP':units=26
            elif e[0]=='SCALE':q=Q(e[2]);units=scalar(['scale',['L',0],q.numerator,q.denominator])
            else:need(e[0]=='ADD','boundary alphabet');q=Q(e[3]);units=scalar(['add',['L',0],['L',1],q.numerator,q.denominator])
            need(units<=32,'boundary tariff exceeded');cost+=112*units
        boundary[side]={'events':len(prog),'explicit_scalar_units':cost}
    newcounts=Counter(e[0] for e in events)-Counter(e[0] for e in controller['physical_events'])
    need(newcounts==Counter({'SIGNED_SWAP':4,'Q_POWER':4}),'new wrapper count mismatch')
    # A signed swap is three ADDs (24units); reserve26, also covering an
    # ordinary swap. Its intermediate row l1 norm is at most2, never omitted.
    x,y=[Q(1),Q(0)],[Q(0),Q(1)]
    x=[a+b for a,b in zip(x,y)];y=[b-a for a,b in zip(x,y)];x=[a+b for a,b in zip(x,y)]
    need((x,y)==([Q(0),Q(1)],[Q(-1),Q(0)]),'signed swap scalar recipe')
    wrapper=112*(newcounts['SIGNED_SWAP']*26+newcounts['Q_POWER']*1000)
    ctlreserve=32*112*(len(events)+sum(v['events'] for v in boundary.values()))
    raw=18*10**7+counts['QUERY_SHEAR']*1792+ctlreserve+wrapper
    need(raw==181586816 and wrapper==459648 and raw<10**9,'complete ordinary raw allowance differs')
    controls={}
    for label,kind in [('omitted_native_wrapper','Q_POWER'),('omitted_idle_job','IDLE'),('omitted_query_shear','QUERY_SHEAR'),('omitted_scalar_sign_swap','SIGNED_SWAP')]:
        bad=copy.deepcopy(changed)
        bad['physical_events'].pop(next(i for i,e in enumerate(events) if e[0]==kind))
        try:check_caller(bad)
        except ValueError as exc:controls[label]=str(exc)
        else:raise ValueError('accepted missing charged record: '+label)
    # Normalizer records are source-derived role/frame pairs, not the
    # author's helper counters. Both sides of every productive helper exist.
    normalizers=[{'role':r,'entry_frame':c['start'][r],'exit_frame':c['final'][r],'rank':len(c['frames'][c['final'][r]])-len(c['frames'][c['start'][r]]),'sides':2} for r in range(224,len(c['start'])) if ('L',r) not in owned]
    def validate_invoice_payload(payload):
        need(payload['histograms']=={'paid':hist(P),'productive':hist(T)},'claimed recursive invoice differs from literal source/caller census')
        need(payload['helper_normalizers']==normalizers,'missing/wrong source helper normalizer role/frame/side')
        need(payload['local_paid']==hist(derive_local(payload['local_program'])[0]),'paid program invoice mismatch')
        need(payload['local_paid']==hist(local),'claimed local profile differs from unchanged complete backward supplier')
        need(payload['wrapper_allowance']>=112*(newcounts['SIGNED_SWAP']*26+newcounts['Q_POWER']*1000),'unfunded actual wrapper ordinary bill')
    payload={'histograms':{'paid':hist(P),'productive':hist(T)},'helper_normalizers':normalizers,'local_program':old['programs']['backward'],'local_paid':hist(local),'wrapper_allowance':wrapper}
    validate_invoice_payload(payload)
    mutations={}
    bad=copy.deepcopy(payload);bad['histograms']['productive']['9']+=16;mutations['unearned16rank9_targets']=bad
    bad=copy.deepcopy(payload);bad['histograms']['productive']['9']-=16;mutations['lost16rank9_targets']=bad
    bad=copy.deepcopy(payload);bad['helper_normalizers'].pop();mutations['missing_helper_normalizer']=bad
    bad=copy.deepcopy(payload);bad['helper_normalizers'][0]['sides']=1;mutations['one_sided_helper_normalizer']=bad
    bad=copy.deepcopy(payload);bad['wrapper_allowance']=0;mutations['unfunded_wrapper_bill']=bad
    bad=copy.deepcopy(payload);next(e for e in bad['local_program'] if e[0] in ('climb','center'))[-1]+=1;mutations['wrong_paid_job_rank']=bad
    for label,bad in mutations.items():
        # Re-serialize each private mutant as valid JSON: rejection is in the
        # same validator used for the valid scientific payload, not its hash.
        bad=json.loads(json.dumps(bad))
        try:validate_invoice_payload(bad)
        except ValueError as exc:controls[label]=str(exc)
        else:raise ValueError('accepted invoice mutation: '+label)
    return {'schema':'independent5398-literal-invoice/1','candidate':{'head':HEAD,'package':PKG},'authentication':auth,'histograms':{'paid':hist(P),'productive':hist(T)},'totals':{'paid':sum(P.values()),'productive':sum(T.values()),'paid_mass':sum(r*n for r,n in P.items()),'productive_mass':sum(r*n for r,n in T.items()),'rank_surplus':752},'local':{'paid':hist(local),'helpers':hist(helpers),'scalar_units':allowance,'kinds':dict(kinds),'scalar_ops':dict(ops),'owned':len(owned)},'controller':{'events':len(events),'counts':dict(counts),'sites':sites,'new_wrapper_counts':dict(newcounts),'main':hist(main),'idle':hist(idles),'raw_owned':18*len(owned)},'ordinary':{'source_route_terms':routes,'source_route_units_upper':route_units,'local_units_upper':route_units+allowance,'local_budget':10**7,'wrapper_allowance':wrapper,'boundary':boundary,'boundary_controller_reserve':ctlreserve,'raw_upper':raw,'raw_budget':10**9,'signed_swap_intermediate_norm_factor':2,'tariff_scope':'Retained primitive allowances, not literal tape-step counts. Common1000/group reserved for source9axis recipes only; compiler matchers need their own finite fold.'},'chronology':chron,'helper_normalizers':normalizers,'controls':controls,'source_keys':source_keys(),'no_candidate_code_imported':True,'external_gates':['full Laurent caller and native wrapper-contact phase','authenticated unchanged all641 source columns/17owned returns','fresh complete306bank precision/compiler/stock/tape including signed-swap intermediate factor2']}

def save(name,data):
    p=OUT/name;need(not p.exists(),'immutable receipt already exists: '+name)
    p.write_text(json.dumps(enc(data),indent=2,sort_keys=True)+'\n');p.chmod(0o444)
    return sha(p)

def main():
    global REPO,PREVIOUS,OUT,MANIFEST
    parser=argparse.ArgumentParser()
    parser.add_argument('--repo',type=Path,default=REPO)
    parser.add_argument('--prior',type=Path,default=PREVIOUS)
    parser.add_argument('--output-dir',type=Path,default=HERE)
    parser.add_argument('--source-manifest',type=Path)
    parser.add_argument('--static-only',action='store_true')
    args=parser.parse_args();REPO=args.repo.resolve();PREVIOUS=args.prior.resolve();OUT=args.output_dir.resolve();MANIFEST=args.source_manifest
    OUT.mkdir(parents=True,exist_ok=True)
    resource.setrlimit(resource.RLIMIT_AS,(500*1024*1024,500*1024*1024))
    start=time.monotonic();inv=invoice()
    if args.static_only:
        save('SOURCE-BINDINGS-v2.json',{'head':HEAD,'package_rows':inv['authentication']['package_rows']})
        digest=save('INVOICE-v2.json',inv)
        print(json.dumps({'status':'PASS_STATIC_LITERAL_INVOICE','sha256':digest,'totals':inv['totals'],'ordinary':inv['ordinary'],'seconds':time.monotonic()-start}));return
    if not (OUT/'INVOICE-v2.json').exists():save('INVOICE-v2.json',inv)
    old=read(OUT/'INVOICE-v2.json');need(inv==old,'fresh literal invoice differs from frozen preflight')
    constants={}
    for n in ast.parse((REPO/PKG/'price.py').read_bytes()).body:
        if isinstance(n,ast.Assign) and len(n.targets)==1 and isinstance(n.targets[0],ast.Name) and isinstance(n.value,ast.Call) and isinstance(n.value.func,ast.Name) and n.value.func.id=='Q' and len(n.value.args)==1 and isinstance(n.value.args[0],ast.Constant):constants[n.targets[0].id]=n.value.args[0].value
    need(constants['KAPPA']=='.00302728823' and constants['TESTED']=='.00302728824','candidate typed endpoints differ')
    bit=read(REPO/'research/query-thinned-controllers/RESULT.json')['ordinary_BIT']
    config={'model':MODEL,'tuple':{'power':1024,'cutoff':20,'floor':21,'tail_offset':'1/5','theta':'63/64','logarithm_power':1000},'kappa':constants['KAPPA'],'tested':constants['TESTED'],'reserve':'1/1000000000000','root_bracket':['.00302728824993','.00302728824994'],'ordinary_BIT':bit}
    result=evaluate(inv['histograms']['productive'],inv['histograms']['paid'],config)
    need(set(result['outer']['strict_checks'])==set(inv['source_keys']['strict']) and set(result['outer']['functional_checks'])==set(inv['source_keys']['functional']),'uncovered current-source outer predicate')
    scientific_controls={}
    for label,change in [('unearned16rank9_targets',16),('lost16rank9_targets',-16)]:
        mutant=copy.deepcopy(inv['histograms']['productive']);mutant['9']+=change
        try:evaluate(mutant,inv['histograms']['paid'],config)
        except ValueError as exc:scientific_controls[label]=str(exc)
        else:raise ValueError('accepted changed complete target profile: '+label)
    for label,patch in [('unsupported_source_tuple',{'tuple':dict(config['tuple'],cutoff=22)}),('former_reserve_1e9',{'reserve':'1/1000000000'}),('insufficient_rounding_reserve_1e13',{'reserve':'1/10000000000000'})]:
        try:evaluate(inv['histograms']['productive'],inv['histograms']['paid'],dict(config,**patch))
        except ValueError as exc:scientific_controls[label]=str(exc)
        else:raise ValueError('accepted unsupported/unfunded numerical mutation: '+label)
    result['changed_profile_controls']=scientific_controls
    # j and H are computed by exact integer bisection in evaluate(), never
    # read from the candidate RESULT or prior funding receipts.
    result.update(schema='independent5398-exact-funding/1',candidate=inv['candidate'],config=config,invoice_sha256=sha(OUT/'INVOICE-v2.json'),invoice_source_bindings=inv['authentication'],ordinary=inv['ordinary'],source_predicates=inv['source_keys'],typed_endpoints=constants,engine_sha256=sha(HERE/'exact_engine.py'),reviewer_sha256=sha(Path(__file__)),gain_over_5387=str(Q(result['kappa'])-Q('.003026674765')),gain_over_5392=str(Q(result['kappa'])-Q('.00302725')),endpoint_funded=False,scientific_scope='Independent exact funding arithmetic and literal bill only. New direct caller/native-contact correctness and fresh expanded306bank precision remain separate prerequisite gates. Existing5392 profile equality does not admit the new caller. No unconditional theorem, selected promotion or proof-kernel acceptance.')
    digest=save('FUNDING-v1.json',result)
    print(json.dumps({'status':result['status'],'sha256':digest,'kappa':result['kappa'],'H':result['H'],'j':result['j'],'seconds':time.monotonic()-start,'endpoint_funded':False}))

if __name__=='__main__':main()

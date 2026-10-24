"""Fresh kernel replay; explicit --resume authenticates actual earlier outputs.
Prepared by Cao Yifan, substantial OpenAI Codex assistance. Apache-2.0.
"""
from concurrent.futures import ThreadPoolExecutor,wait,FIRST_COMPLETED
from datetime import datetime,timezone
from fractions import Fraction as Q
from pathlib import Path
from hashlib import sha256
import argparse,gzip,importlib.util,json,os,re,subprocess,sys,time
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
CURRENT_RECEIPT=None
OLD=ROOT/'research/kappa-lean-verification-20261022';SOURCE=ROOT/'research/kappa-round3-warp-20261022'
PAYLOAD='cfcd36b40326d7a5815e1db5313444379b3fb756b27d5201c561574c085cc0dd'
def need(p,s):
    if not p:raise ValueError(s)
def digest(p):return sha256(Path(p).read_bytes()).hexdigest()
def read(p):
    b=p.read_bytes();return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
def write(p,x):p.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n',encoding='utf-8',newline='\n')
def load(p,n):
    sp=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(sp);sys.modules[n]=m;sp.loader.exec_module(m);return m
def bindings(W):
    raw=gzip.decompress((SOURCE/'ACTUAL-WORD.json.gz').read_bytes());need(sha256(raw).hexdigest()==PAYLOAD,'Actual frozen word hash')
    frozen=read(SOURCE/'ACTUAL-WORD-FREEZE.json');need(frozen['canonical_payload_sha256']==PAYLOAD,'Freeze binding')
    checker=load(SOURCE/'verify_candidate.py','round3_bound_checker');c,words,_,_=checker.inputs()
    need(c==json.loads(raw)['canonical'] and words==json.loads(raw)['programs'],'Native checker input binding')
    native=read(SOURCE/'NATIVE-VALIDATION.json');phase=read(SOURCE/'PHASE-VALIDATION.json.gz');arithmetic=read(SOURCE/'ARITHMETIC.json')
    need(native['status']=='PASS_JOINT_HELPER_MAPS_NATIVE_BOTH_632_INTERPRETERS' and phase['status']=='PASS_JOINT_HELPER_MAPS_ALL_ACTUAL_ABSOLUTE_PHASES','Fresh native/phase gates')
    need(native['actual_word_canonical_sha256']==PAYLOAD and native['verifier_sha256']==digest(SOURCE/'verify_candidate.py'),'Native provenance binding')
    need(phase['actual_word_canonical_sha256']==PAYLOAD and phase['source_manifest_sha256']==digest(SOURCE/'SOURCES.json') and phase['verifier_sha256']==digest(SOURCE/'phase_check.py'),'Absolute phase provenance binding')
    need(phase['both_actual_orientation_pairsets_equal'] and phase['inherited_frame_prefix_exact'] and phase['main_endpoint_adapters_unchanged'],'Phase interface guards')
    need(len(phase['actual_warp_classes'])==180 and len(phase['new_paid_pairs'])==105,'Phase class coverage')
    previous=read(ROOT/'research/warp-interface-20261022/ACTUAL-WORD.json.gz')['canonical']
    priorwords=read(ROOT/'research/warp-interface-20261022/ACTUAL-WORD.json.gz')['programs']
    oldG={g['op']:g['G_columns'] for g in previous['warps']};newG={g['op']:g['G_columns'] for g in c['warps']}
    changedG=sorted(op for op in newG if oldG[op]!=newG[op])
    need(changedG==phase['changed_G_operators'] and {g['operator'] for g in phase['native_operator_columns']}==set(changedG),'Exact changed native column coverage')
    warps=lambda p:{(e[2],e[3],e[4]) for e in p if e[0]=='warp'}
    edges=lambda p:{(e[3],e[4]) for e in p if e[0]=='climb'}
    need(warps(words['forward'])==warps(words['backward'])=={(g['operator'],g['input'],g['output']) for g in phase['actual_warp_classes']},'Exact actual warp phase coverage')
    need(edges(words['forward'])==edges(words['backward']),'Both complete paid pair sets')
    need(edges(words['forward'])-edges(priorwords['forward'])=={(g['input'],g['output']) for g in phase['new_paid_pairs']},'Exact new paid phase coverage')
    changed={r for r in range(224,632) if c['start'][r]!=previous['start'][r]}
    covered=[r for h in phase['changed_helper_boundaries'] for r in h['helpers']]
    need(len(covered)==len(set(covered))==26 and set(covered)==changed,'Every changed arbitrary helper phase covered')
    for h in phase['changed_helper_boundaries']:
        for r in h['helpers']:
            need((h['input'],h['output'],h['rank'])==(c['start'][r],c['final'][r],len(c['frames'][c['final'][r]])-len(c['frames'][c['start'][r]])),'Exact changed helper phase interface')
    price=load(ROOT/'research/kappa-interface-round2-20261022/price_profile.py','round3_bound_price')
    expected=price.run(native,Q('.00302176'))
    need(all(arithmetic[k]==v for k,v in expected.items()),'Exact full arithmetic recomputation')
    need(arithmetic['native_receipt_sha256']==digest(SOURCE/'NATIVE-VALIDATION.json'),'Native arithmetic receipt binding')
    W.HERE=HERE
    numeric=W.numerical_binding(arithmetic,native)
    paths={SOURCE/x for x in ['ACTUAL-WORD.json.gz','ACTUAL-WORD-FREEZE.json','PATCH.json','SOURCES.json','NATIVE-VALIDATION.json','PHASE-VALIDATION.json.gz','ARITHMETIC.json','verify_candidate.py','phase_check.py','regenerate.py']}
    for row in read(SOURCE/'SOURCES.json')['files']:paths.add(ROOT/row['path'])
    for relative,h in arithmetic['source_sha256'].items():need(digest(ROOT/relative)==h,'Arithmetic source pin '+relative);paths.add(ROOT/relative)
    paths|={OLD/x for x in ['verify_lean.py','lean-toolchain','lakefile.toml','lake-manifest.json']}
    return {p.relative_to(ROOT).as_posix():digest(p) for p in sorted(paths)},numeric
def main():
    global CURRENT_RECEIPT
    ap=argparse.ArgumentParser();ap.add_argument('--jobs',type=int,default=2);ap.add_argument('--only',nargs='+');ap.add_argument('--resume',type=Path);ap.add_argument('--check-inputs',action='store_true');ap.add_argument('--lake');ap.add_argument('--receipt',default='LEAN-VERIFICATION.json');args=ap.parse_args()
    need(sys.version_info[:2]==(3,14),'Global Python3.14 required');need(1<=args.jobs<=4,'One to four Lean workers')
    target=HERE/args.receipt;need(target.resolve().parent==HERE,'Receipt stays inside package')
    if not args.check_inputs:
        CURRENT_RECEIPT=target
        write(target,{'status':'CHECKING_INPUTS'})
    need(digest(OLD/'verify_lean.py')=='6c953b31c385179f852eb4b56246e62a4084cb8906843f15fbf2724508539895','Retained proof-audit implementation pin')
    W=load(OLD/'verify_lean.py','round3_retained_replay_support')
    # Retain independently checked source audit, exact profile parser and axiom parser.
    # Constants are changed explicitly in a readable derivative, never in proof logs.
    support=(OLD/'verify_lean.py').read_text(encoding='utf-8')
    start=support.index('def numerical_binding(');end=support.index('\ndef authenticate_inputs()',start)
    fragment=support[start:end].replace('302153, 100000000','302177, 100000000').replace('37769, 12500000','9443, 3125000')
    exec(compile(fragment,str(Path(__file__)),'exec'),W.__dict__)
    if args.check_inputs:
        W.HERE=HERE;bindings(W);W.check_generators()
        for p in HERE.glob('*.lean'):W.audit_source(p)
        print('PASS_INPUT_BINDINGS_ONLY; no new Lean proof was compiled',flush=True)
        return
    W.HERE=OLD
    leanbin=OLD/'.toolchain/lean-4.21.0-windows/bin'
    lake=args.lake or (str(leanbin/'lake.exe') if (leanbin/'lake.exe').is_file() else 'lake')
    if Path(lake).is_file():os.environ['PATH']=str(Path(lake).resolve().parent)+os.pathsep+os.environ['PATH']
    print('CHECK_RUNTIME',flush=True)
    lean,env,runtime=W.environment(lake)
    library=[str((OLD/Path(p)).resolve()) if not Path(p).is_absolute() else p for p in env['LEAN_PATH'].split(os.pathsep) if p and Path(p).resolve()!=OLD]
    env['LEAN_PATH']=os.pathsep.join([str(HERE),*library]);W.HERE=HERE
    print('CHECK_INPUT_BINDINGS',flush=True)
    bound,numeric=bindings(W)
    print('CHECK_GENERATOR_BYTES',flush=True)
    generated=W.check_generators()
    modules=W.order(args.only or ['KappaWarpVerification'])
    sources={m:digest(HERE/(m+'.lean')) for m in modules};expected={m:W.audit_source(HERE/(m+'.lean')) for m in modules}
    data={'status':'RUNNING','started_utc':datetime.now(timezone.utc).isoformat(),'canonical_payload_sha256':PAYLOAD,'runtime':runtime,'lean_version':runtime['lean_version'],'mathlib_revision':runtime['mathlib_revision'],'input_sha256':bound,'numerical_profile_binding':numeric,'transcriptions':generated,'source_sha256':sources,'script_sha256':digest(Path(__file__)),'module_order':modules,'modules':[],'scope':'Finite complete native binary frames/invoices, real moments/tails/capacity, rational finite compiler and outer ledger; excludes amplitudes/phases/free-group endpoint and full multiplication theorem.'}
    reuse={}
    if args.resume:
        prior=read(args.resume);need(prior['runtime']==runtime,'Resume runtime binding');need(prior['canonical_payload_sha256']==PAYLOAD,'Resume input word')
        for row in prior['modules']:
            m=row['module']
            if m not in sources or row.get('exit_code')!=0:continue
            if row['source_sha256']!=sources[m]:continue
            need(row['argv']==['lean','-s','65536','-o',m+'.olean',m+'.lean'],'Resume exact ordinary compiler command')
            need(not any(re.search(r'skipKernelTC|trustCompiler|ofReduceBool|native_decide',s) for s in row['argv']),'Resume command bypass')
            need(row['argv'][row['argv'].index('-o')+1]==m+'.olean','Resume output binding')
            for k,ext in [('source','.lean'),('olean','.olean'),('log','.log')]:need(digest(HERE/(m+ext))==row[k+'_sha256'],'Resume '+k+' integrity')
            need(W.parse_axioms(HERE/(m+'.log'),expected[m])==row['axioms'],'Resume axiom reports')
            reuse[m]=row
        data['resume_receipt']={'path':str(args.resume),'sha256':digest(args.resume)}
    write(target,data);completed={};pending=set(modules);running={}
    def compile_one(m,dep):
        started=time.monotonic();argv=[lean,'-s','65536','-o',m+'.olean',m+'.lean']
        with (HERE/(m+'.log')).open('wb') as stream:r=subprocess.run(argv,cwd=HERE,env=env,stdout=stream,stderr=subprocess.STDOUT,timeout=1800,check=False)
        need(r.returncode==0,'Lean failed '+m+'; see '+m+'.log')
        return {'module':m,'source_sha256':sources[m],'olean_sha256':digest(HERE/(m+'.olean')),'log_sha256':digest(HERE/(m+'.log')),'argv':['lean',*argv[1:]],'exit_code':r.returncode,'seconds':time.monotonic()-started,'mode':'fresh','dependency_olean_sha256':dep,'axioms':W.parse_axioms(HERE/(m+'.log'),expected[m])}
    try:
        with ThreadPoolExecutor(max_workers=args.jobs) as pool:
            while pending or running:
                for m in modules:
                    if m not in pending or len(running)>=args.jobs:continue
                    deps=W.imports(m)
                    if not set(deps)<=completed.keys():continue
                    dep={d:completed[d]['olean_sha256'] for d in W.order(deps)}
                    pending.remove(m)
                    if m in reuse and reuse[m]['dependency_olean_sha256']==dep:
                        completed[m]=dict(reuse[m],mode='validated-reuse');data['modules'].append(completed[m]);write(target,data);print('REUSE',m,flush=True)
                    else:print('COMPILE',m,flush=True);running[pool.submit(compile_one,m,dep)]=m
                if not running:need(not pending,'Dependency scheduler stuck');continue
                done,_=wait(running,return_when=FIRST_COMPLETED)
                for job in done:
                    m=running.pop(job);completed[m]=job.result();data['modules'].append(completed[m]);write(target,data);print('PASS',m,round(completed[m]['seconds'],2),flush=True)
        need(all(digest(HERE/(m+'.lean'))==h for m,h in sources.items()),'Sources changed during compilation')
        need(digest(Path(__file__))==data['script_sha256'],'Replay implementation changed during compilation')
        need(bindings(W)==(bound,numeric),'Inputs changed during compilation')
        data['status']='PASS_PARTIAL_LEAN_REPLAY' if args.only else 'PASS_SCOPED_LEAN_REPLAY';data['completed_utc']=datetime.now(timezone.utc).isoformat();write(target,data);print(data['status'],len(modules),flush=True)
    except Exception as e:data['status']='FAIL_LEAN_REPLAY';data['error']=str(e);write(target,data);raise
if __name__=='__main__':
    try:main()
    except Exception as exc:
        if CURRENT_RECEIPT:
            data=read(CURRENT_RECEIPT);data['status']='FAIL_LEAN_REPLAY' if 'modules' in data else 'FAIL_INPUT_BINDINGS';data['error']=str(exc);write(CURRENT_RECEIPT,data)
        raise

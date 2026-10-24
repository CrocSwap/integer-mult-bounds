"""Fresh tightened numerical/compiler proofs with explicit native evidence reuse.
Cao Yifan; substantial OpenAI Codex assistance. Apache-2.0.
This is a scoped conditional certificate, not a multiplication theorem.
"""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timezone
from fractions import Fraction as Q
from hashlib import sha256
import argparse,contextlib,gzip,importlib.util,io,json,os,re,subprocess,sys,tempfile,time
from pathlib import Path

sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
RUNTIME=ROOT/'research/kappa-lean-verification-20261022'
NATIVE=ROOT/'research/kappa-round3-warp-lean-20261022'
SOURCE=ROOT/'research/kappa-round3-warp-20261022'
PAYLOAD='cfcd36b40326d7a5815e1db5313444379b3fb756b27d5201c561574c085cc0dd'
AUDITOR='6c953b31c385179f852eb4b56246e62a4084cb8906843f15fbf2724508539895'
MODULES=['TightenedNumerical','TightenedArithmetic','TightenedCapacity','TightenedVerification']

def need(ok,message):
    if not ok:raise ValueError(message)
def digest(p):return sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def save(p,data):Path(p).write_text(json.dumps(data,indent=2,sort_keys=True)+'\n',encoding='utf-8',newline='\n')
def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path);mod=importlib.util.module_from_spec(spec)
    sys.modules[name]=mod;spec.loader.exec_module(mod);return mod

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--native-receipt',type=Path,default=NATIVE/'LEAN-VERIFICATION.json')
    ap.add_argument('--lake');ap.add_argument('--jobs',type=int,default=2);args=ap.parse_args()
    need(sys.version_info[:2]==(3,14),'Use global Python3.14')
    need(1<=args.jobs<=3,'One to three fresh Lean workers')
    receipt=HERE/'LEAN-VERIFICATION.json';data=dict(status='CHECKING_INPUTS',mode='fresh-four-modules-with-explicit-native-reuse',modules=[])
    save(receipt,data)
    try:
        need(digest(RUNTIME/'verify_lean.py')==AUDITOR,'Proof auditor source pin')
        W=load(RUNTIME/'verify_lean.py','tightening_pinned_auditor')
        lake=args.lake or str(RUNTIME/'.toolchain/lean-4.21.0-windows/bin/lake.exe')
        lean,env,runtime=W.environment(lake)
        need(runtime['lean_executable_sha256']=='fb7a62288f197279fb84e55bb1972348fd2cce1d550845793975f1cebb0c24ab','Compiler digest')
        old=read(args.native_receipt)
        need(old['runtime']==runtime and old['canonical_payload_sha256']==PAYLOAD,'Native proof runtime/payload')
        need(old['status'] in ['PASS_SCOPED_LEAN_REPLAY','PASS_PARTIAL_LEAN_REPLAY'],'Successful predecessor evidence required')
        bound={}
        for name,pin in old['input_sha256'].items():
            need(digest(ROOT/name)==pin,'Native predecessor input drift: '+name);bound[name]=pin
        need(sha256(gzip.decompress((SOURCE/'ACTUAL-WORD.json.gz').read_bytes())).hexdigest()==PAYLOAD,'Actual native archive')
        W.HERE=NATIVE
        inherited=W.order(['Native','AnalyticGain']);rows={x['module']:x for x in old['modules']}
        reused=[]
        for module in inherited:
            need(module in rows,'Native evidence lacks '+module)
            row=rows[module];need(row['exit_code']==0,'Failed inherited module')
            for kind,suffix in [('source','.lean'),('log','.log'),('olean','.olean')]:
                need(digest(NATIVE/(module+suffix))==row[kind+'_sha256'],'Inherited '+kind+' hash: '+module)
            expected=W.audit_source(NATIVE/(module+'.lean'))
            need(W.parse_axioms(NATIVE/(module+'.log'),expected)==row['axioms'],'Inherited axiom report')
            deps=W.order(W.imports(module))
            need(row['dependency_olean_sha256']=={d:rows[d]['olean_sha256'] for d in deps},'Inherited dependency closure')
            need(row['argv']==['lean','-s','65536','-o',module+'.olean',module+'.lean'],'Inherited compile command')
            reused.append(dict(module=module,source_sha256=row['source_sha256'],log_sha256=row['log_sha256'],
                               olean_sha256=row['olean_sha256'],axioms=row['axioms']))
        arithmetic=read(HERE/'ARITHMETIC.json')
        need(arithmetic['kappa']=='15108879/5000000000' and arithmetic['strictification']['tested']=='302177581/100000000000','Saving contract')
        price=load(HERE/'arithmetic.py','tightening_exact_price')
        expected=price.run(read(SOURCE/'NATIVE-VALIDATION.json'),Q('.0030217758'))
        need(all(arithmetic[k]==v for k,v in expected.items()),'Complete arithmetic recomputation')
        need(arithmetic['native_receipt_sha256']==digest(SOURCE/'NATIVE-VALIDATION.json'),'Actual native arithmetic binding')
        for name,pin in arithmetic['source_sha256'].items():
            need(digest(ROOT/name)==pin,'Arithmetic source drift: '+name);bound[name]=pin
        # Check readable derivation of the arithmetic engine.
        patch=read(HERE/'ARITHMETIC-SOURCE-PATCH.json')
        source=ROOT/patch['source'];need(digest(source)==patch['source_sha256'],'Arithmetic predecessor pin')
        derived=source.read_text(encoding='utf-8')
        for a,b in patch['changes']:
            need(derived.count(a)==1,'Ambiguous arithmetic derivation');derived=derived.replace(a,b)
        need((HERE/'arithmetic.py').read_bytes()==derived.encode('utf-8'),'Readable arithmetic source derivation')
        need(digest(HERE/'arithmetic.py')==patch['derived_sha256'],'Derived arithmetic digest')
        prepared=read(HERE/'PROOF-SOURCES.json')
        for name,pin in prepared['predecessor_sha256'].items():
            need(digest(ROOT/name)==pin,'Proof predecessor drift');bound[name]=pin
        need(digest(HERE/'prepare.py')==prepared['preparation_script_sha256'],'Proof preparation pin')
        sources={m:digest(HERE/(m+'.lean')) for m in MODULES}
        need(all(sources[Path(name).stem]==pin for name,pin in prepared['prepared_sha256'].items()),'Prepared proof source mismatch')
        for generator,output in [('numerical_generate.py','TightenedNumerical.lean'),('generate_arithmetic.py','TightenedArithmetic.lean')]:
            mod=load(HERE/generator,'tightening_check_'+generator[:-3])
            # Keep temporary proof generation inside the writable checkout.
            scratch=HERE/'.lean-build';scratch.mkdir(exist_ok=True)
            with tempfile.TemporaryDirectory(prefix='kappa-proof-check-',dir=scratch) as folder:
                tmp=Path(folder);mod.HERE=tmp
                save(tmp/'ARITHMETIC.json',arithmetic)
                with contextlib.redirect_stdout(io.StringIO()):mod.main()
                need((tmp/output).read_bytes()==(HERE/output).read_bytes(),'Nonreproducible generated '+output)
        # Literal complete profiles must equal the freshly assembled controller.
        code=W.strip_lean((HERE/'TightenedNumerical.lean').read_text(encoding='utf-8'))
        term=re.compile(r'\s*(\d+)\s*\*\s*\((\d+)\s*:\s*ℝ\)\s*\^\s*t\s*')
        for name,profile in [('targetMoment',arithmetic['targets']),('paidMoment',arithmetic['paid'])]:
            defs=re.findall(r'noncomputable\s+def\s+'+name+r'\s*\(t\s*:\s*ℝ\)\s*:\s*ℝ\s*:=\s*\n(.*?)(?=\n\s*\n)',code,re.S)
            need(len(defs)==1,'Numerical profile definition')
            found={}
            for part in defs[0].split('+'):
                match=term.fullmatch(part);need(match is not None,'Numerical literal syntax')
                count,rank=map(int,match.groups());need(rank not in found,'Duplicate numerical rank');found[rank]=count
            need(found=={int(k):v for k,v in profile.items()},'Numerical/native profile mismatch')
        paths=[]
        for entry in env['LEAN_PATH'].split(os.pathsep):
            if entry:
                p=Path(entry);paths.append(str(p if p.is_absolute() else (RUNTIME/p).resolve()))
        env['LEAN_PATH']=os.pathsep.join([str(HERE),str(NATIVE),*paths])
        expected_reports={m:W.audit_source(HERE/(m+'.lean')) for m in MODULES}
        need([len(expected_reports[m]) for m in MODULES]==[3,11,5,12],'Exported proof inventory')
        local={p.name:digest(p) for p in HERE.iterdir() if p.suffix in ['.py','.lean']}
        data.update(status='RUNNING',started_utc=datetime.now(timezone.utc).isoformat(),runtime=runtime,
            kappa=arithmetic['kappa'],tested=arithmetic['strictification']['tested'],canonical_payload_sha256=PAYLOAD,
            source_sha256=sources,input_sha256=bound,local_source_sha256=local,
            arithmetic_sha256=digest(HERE/'ARITHMETIC.json'),script_sha256=digest(__file__),
            native_reuse_receipt_sha256=digest(args.native_receipt),native_reuse_modules=reused,
            allowed_axioms=sorted(W.ALLOW),scope='Fresh real contraction/tails, real compiler capacity, exact source outer formulas and finite threshold, bound to validated reused native certificates. Retains the published conditional native/analytic/tape/precision/recovery hypotheses; not a Lean multiplication theorem.')
        save(receipt,data)
        def compile_one(module):
            print('COMPILE',module,flush=True);began=time.monotonic();log=HERE/(module+'.log')
            argv=[lean,'-s','262144','-o',module+'.olean',module+'.lean']
            with log.open('wb') as stream:
                proc=subprocess.run(argv,cwd=HERE,env=env,stdout=stream,stderr=subprocess.STDOUT,timeout=900)
            need(proc.returncode==0,'Lean failed '+module+'; see '+log.name)
            need(digest(HERE/(module+'.lean'))==sources[module],'Proof source drift')
            row=dict(module=module,source_sha256=sources[module],log_sha256=digest(log),
                olean_sha256=digest(HERE/(module+'.olean')),exit_code=proc.returncode,argv=['lean',*argv[1:]],
                axioms=W.parse_axioms(log,expected_reports[module]),seconds=time.monotonic()-began)
            print('PASS',module,len(row['axioms']),'reports',flush=True);return row
        with ThreadPoolExecutor(max_workers=args.jobs) as pool:
            data['modules'].extend(list(pool.map(compile_one,MODULES[:3])))
        save(receipt,data)
        data['modules'].append(compile_one(MODULES[3]))
        need(all(digest(ROOT/p)==h for p,h in bound.items()),'External input drift')
        need(all(digest(HERE/p)==h for p,h in local.items()),'Local source drift')
        need(digest(HERE/'ARITHMETIC.json')==data['arithmetic_sha256'],'Arithmetic drift')
        data.update(status='PASS_TIGHTENED_SCOPED_LEAN_CERTIFICATES',completed_utc=datetime.now(timezone.utc).isoformat(),
            fresh_axiom_reports=sum(len(x['axioms']) for x in data['modules']))
        save(receipt,data);print(data['status'],'fresh modules',len(data['modules']),'reports',data['fresh_axiom_reports'],flush=True)
    except Exception as exc:
        data.update(status='FAIL_TIGHTENED_VERIFICATION',error=str(exc));save(receipt,data);raise

if __name__=='__main__':main()

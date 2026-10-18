"""Exact differential replay; timings are observations, never correctness gates."""
import argparse,shutil,gzip,hashlib,json,os,platform,re,subprocess,sys,tempfile,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from build import ROOT,compile_c,source
from oracle import run as oracle_run

def need(ok,message):
    if not ok:raise ValueError(message)

def authenticate():
    pins=json.loads((ROOT/'SOURCES.json').read_text())
    for p,h in pins['bundled_files'].items():
        need(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,'source mismatch: '+p)
    raw=gzip.decompress((ROOT/'data/data88.txt.gz').read_bytes())
    need(hashlib.sha256(raw).hexdigest()==pins['upstream_data_sha256'],'decompressed source mismatch')
    return raw

def call(exe,request):
    return subprocess.run([str(exe)],input=request,text=True,capture_output=True,timeout=240,check=True).stdout

def control(exe,request,expected):
    need(call(exe,request)==expected,'positive/negative fixture mismatch')

def kernel_check(work):
    original=compile_c(source(kernel=True),work/'original-kernel')
    fast_text=source(fast=True,kernel=True)
    fast=compile_c(fast_text,work/'fast-kernel')
    count=oracle_run(str(fast))
    requests=gzip.decompress((ROOT/'data/kernel-requests.txt.gz').read_bytes()).decode()
    times={};outputs={}
    for name,exe in [('original',original),('fast',fast)]:
        start=time.perf_counter();outputs[name]=call(exe,requests);times[name]=time.perf_counter()-start
    need(outputs['original']==outputs['fast'],'minimal requirement sets differ')
    lines=outputs['fast'].splitlines()
    need(len(lines)==25001,'missing kernel cases')
    # Each mutation has a concrete rejection witness, not just a changed source hash.
    fixture='2\n1 2\n0 3 1 1\n'
    valid=call(fast,fixture)
    mutants={
        'missing_second_branch':fast_text.replace('if(n4<d){','if(0){',1),
        'premature_terminal':fast_text.replace('if(!x){','if(1){',1),
        'wrong_capacity':fast_text.replace('if(n3<c){','if(n3+1<c){',1),
    }
    for name,text in mutants.items():
        need(text!=fast_text,'mutation did not apply')
        exe=compile_c(text,work/name)
        need(call(exe,fixture)!=valid,'mutant survived '+name)
    overflow=compile_c(fast_text.replace('#define MAXFL 60000','#define MAXFL 1'),work/'overflow')
    proc=subprocess.run([str(overflow)],input=fixture,text=True,capture_output=True)
    need(proc.returncode==2 and 'OPTION OVERFLOW' in proc.stderr,'overflow must fail closed')
    proc=subprocess.run([str(fast)],input='1\n1\n0 1 7 0\n',text=True,capture_output=True)
    need(proc.returncode==2,'unsupported capacity must reject')
    # The same exact result under sanitizers catches writes past the option and basis bounds.
    sanitized=compile_c(fast_text,work/'sanitized',('-fsanitize=undefined,bounds','-fsanitize-undefined-trap-on-error'))
    need(call(sanitized,requests)==outputs['fast'],'sanitized kernel drift')
    for filename in ['vendor/s4z.c','data/kernel-requests.txt.gz']:
        copy=work/('tamper-'+Path(filename).name)
        shutil.copytree(ROOT,copy,ignore=shutil.ignore_patterns('__pycache__'))
        target=copy/filename;target.write_bytes(target.read_bytes()+b'!')
        proc=subprocess.run([sys.executable,'-I','-B',str(copy/'verify.py'),'--kernel-only'],text=True,capture_output=True)
        need(proc.returncode!=0 and 'source mismatch' in proc.stderr,'source corruption survived '+filename)
    return {'cases':len(lines),'option_pairs':sum(int(l.split()[0]) for l in lines),
            'output_sha256':hashlib.sha256(outputs['fast'].encode()).hexdigest(),
            'independent_explicit_subspace_cases':count,'negative_controls':7,'seconds':times,
            'speedup':times['original']/times['fast']}

def full_check(work,raw):
    (work/'data88.txt').write_bytes(raw)
    (work/'gens.txt').write_bytes((ROOT/'vendor/gens.txt').read_bytes())
    (work/'pairs.txt').write_bytes((ROOT/'data/pairs.txt').read_bytes())
    results={};logs={};exports={}
    for name,fast in [('original',False),('fast',True)]:
        exe=compile_c(source(fast=fast,trace=fast),work/name)
        env={k:v for k,v in os.environ.items() if k not in ['FREES','NOSYM','ONLY','JMOD','JREM','NEWLO','PASS1','PAIRS','EXITCRACK','EXPORT_ONLY','EXPORT','PAIRLOG','DBG','TRACE']}
        env.update(ONLY='46',PAIRS=str(work/'pairs.txt'),PAIRLOG='1',EXPORT=str(work/name)+'-instance')
        if fast:env['TRACE']=str(work/'requests.trace')
        start=time.perf_counter()
        p=subprocess.run([str(exe),'data88.txt','4','6','4','5','88','8','1','0'],cwd=work,env=env,text=True,capture_output=True,timeout=300,check=True)
        elapsed=time.perf_counter()-start;logs[name]=p.stdout
        (work/(name+'.log')).write_text(p.stdout+p.stderr)
        need('overflow 0' in p.stdout and 'pairs 12 surviving 11' in p.stdout,'incomplete/overflowed full run')
        records=re.findall(r'TIMING rep 46 j (\d+) options ([\d.]+) closure ([\d.]+) nw (\d+)',p.stderr)
        need(len(records)==11,'missing timing records')
        results[name]={'wall_seconds':elapsed,'option_cpu_seconds':sum(float(r[1]) for r in records),
                       'closure_cpu_seconds':sum(float(r[2]) for r in records),'pairs':records}
        exports[name]={f.name.split('-instance-')[1]:f.read_bytes() for f in work.glob(name+'-instance-*.json')}
    trace=(work/'requests.trace').read_text().splitlines()
    regenerated='112\n'+raw.decode().splitlines()[0]+'\n'+''.join(s[:16]+' '+s[16:]+'\n' for s in sorted(set(trace)))
    need(regenerated.encode()==gzip.decompress((ROOT/'data/kernel-requests.txt.gz').read_bytes()),'corpus regeneration mismatch')
    need(len(trace)==25991,'missing traced option calls')
    need(logs['original']==logs['fast'],'full output/histogram mismatch')
    need(len(exports['original'])==11 and exports['original']==exports['fast'],'complete exported requirements differ')
    # A known positive (6,6,4,0) witness guards against rejecting every branch.
    (work/'positive-pair.txt').write_text('82 103676\n')
    positive=[]
    for name in ['original','fast']:
        env={k:v for k,v in os.environ.items() if k not in ['FREES','NOSYM','ONLY','JMOD','JREM','NEWLO','PASS1','PAIRS','EXITCRACK','EXPORT_ONLY','EXPORT','PAIRLOG','DBG','TRACE']}
        env.update(ONLY='82',PAIRS=str(work/'positive-pair.txt'),EXITCRACK='1')
        proc=subprocess.run([str(work/name),'data88.txt','6','6','4','0','88','5','1','0'],cwd=work,env=env,text=True,capture_output=True,timeout=120,check=True)
        need('CRACK? target 5 span 5 rep 82 V2idx 103676' in proc.stdout,'positive witness lost')
        positive.append(proc.stdout)
    need(positive[0]==positive[1],'positive witness differs')
    digest=hashlib.sha256(logs['fast'].encode()).hexdigest()
    return {'benchmark':results,'full_stdout_sha256':digest,
            'positive_span_five_control':'PASS','exported_requirement_sets':11,'closure_leaves':5509,
            'option_speedup':results['original']['option_cpu_seconds']/results['fast']['option_cpu_seconds'],
            'wall_speedup':results['original']['wall_seconds']/results['fast']['wall_seconds']}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--work',type=Path);ap.add_argument('--kernel-only',action='store_true');ap.add_argument('--full-only',action='store_true');args=ap.parse_args()
    need(not(args.kernel_only and args.full_only),'conflicting modes')
    raw=authenticate();tmp=None
    if args.work:
        need(not args.work.exists(),'work directory must be fresh');args.work.mkdir(parents=True);work=args.work.resolve()
    else:tmp=tempfile.TemporaryDirectory(prefix='two-flat-cover-');work=Path(tmp.name)
    report={'status':'PASS_TWO_FLAT_COVER_BRANCHING','python':sys.version,'platform':platform.platform(),
            'compiler':subprocess.check_output(['cc','--version'],text=True).splitlines()[0]}
    if not args.full_only:report['kernel']=kernel_check(work)
    if not args.kernel_only:report['full']=full_check(work,raw)
    (work/'RESULT.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2));print('PASS_TWO_FLAT_COVER_BRANCHING')
    if tmp:tmp.cleanup()
if __name__=='__main__':main()

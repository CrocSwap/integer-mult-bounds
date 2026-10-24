"""Fresh-process paired raw-moment measurements; no timing acceptance threshold."""
import argparse
from fractions import Fraction as Q
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import platform
import statistics
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
CASES = {'admission_raw_test':'.003020155',
         'published_root_upper':'30201659771/10000000000000',
         'larger_rate_control':'.0031'}
METHODS = ['source_full','source_normalized','adaptive','reject_gate']

def load_probe():
    spec=importlib.util.spec_from_file_location('probe',HERE/'verify.py')
    probe=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(probe)
    return probe

def worker(method,case):
    probe=load_probe()
    raw=(HERE/'INPUT.json').read_bytes()
    probe.need(sha256(raw).hexdigest()==probe.EXPECTED,'input binding')
    data=json.loads(raw)
    targets={int(k):v for k,v in data['targets'].items()}
    paid={int(k):v for k,v in data['paid'].items()}
    source=probe.load_upstream()
    a=Q(CASES[case])
    started=time.perf_counter()
    if method=='source_full':
        bounds=probe.upstream_margin(source,targets,paid,a)
        stage='source'
    elif method=='source_normalized':
        bounds=probe.margin(targets,paid,a,lambda b,r: source.power(r,-b))
        stage='source_factored'
    elif method=='adaptive':
        bounds,stage=probe.adaptive_margin(targets,paid,a,
            lambda t,p,b:probe.upstream_margin(source,t,p,b))
    else:
        bounds,stage=probe.reject_gate_margin(targets,paid,a,
            lambda t,p,b:probe.upstream_margin(source,t,p,b))
    elapsed=time.perf_counter()-started
    return {'method':method,'case':case,'stage':stage,
            'computation_seconds':elapsed,'bounds':probe.display(bounds)}

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--worker',choices=METHODS)
    ap.add_argument('--case',choices=list(CASES))
    ap.add_argument('--pairs',type=int,default=21)
    ap.add_argument('--output',type=Path)
    args=ap.parse_args()
    if args.worker:
        if not args.case: ap.error('--worker requires --case')
        print(json.dumps(worker(args.worker,args.case)))
        return
    if args.output is None or args.output.exists():
        ap.error('provide a fresh --output path')
    if args.pairs<1: ap.error('positive --pairs required')
    rows=[]
    for i in range(args.pairs):
        for ci,case in enumerate(CASES):
            shift=(i+ci)%len(METHODS)
            order=METHODS[shift:]+METHODS[:shift]
            if i%2: order=list(reversed(order))
            group=[]
            for method in order:
                started=time.perf_counter()
                result=subprocess.run([sys.executable,'-I','-B',str(HERE/'benchmark.py'),
                    '--worker',method,'--case',case],capture_output=True,text=True,check=True)
                elapsed=time.perf_counter()-started
                row=json.loads(result.stdout)
                row.update(round=i,process_seconds=elapsed)
                rows.append(row);group.append(row)
            decisions={x['bounds']['decision'] for x in group}
            if len(decisions)!=1 or 'inconclusive' in decisions:
                raise ValueError('timed methods disagree')
            lo=max(Q(x['bounds']['lower']) for x in group)
            hi=min(Q(x['bounds']['upper']) for x in group)
            if lo>hi: raise ValueError('timed enclosures do not intersect')
    summary={}
    for case in CASES:
        by_method={m:[r for r in rows if r['case']==case and r['method']==m] for m in METHODS}
        item={m:{'median_process_seconds':statistics.median(r['process_seconds'] for r in data),
                 'median_computation_seconds':statistics.median(r['computation_seconds'] for r in data)} for m,data in by_method.items()}
        item['paired_comparisons']={}
        for variant in METHODS[2:]:
            candidates={r['round']:r for r in by_method[variant]}
            for baseline in METHODS[:2]:
                ratios=[1-candidates[r['round']]['process_seconds']/r['process_seconds'] for r in by_method[baseline]]
                item['paired_comparisons'][variant+'_vs_'+baseline]={
                    'median_fraction_saved':statistics.median(ratios),
                    'faster_pairs':sum(x>0 for x in ratios),'pairs':len(ratios)}
        summary[case]=item
    report={'python':sys.version,'platform':platform.platform(),
            'pairs':args.pairs,'fresh_processes':len(rows),
            'scope':'One frozen raw moment sign; process time includes Python startup, imports, source hash checks, input parsing and cold logarithm caches. OS file caches are not flushed. No native, compiler, full PR, or multiplication timing.',
            'ordering':'Adjacent four-method blocks per case; cyclic method order and alternating reversal',
            'sources':{p.name:sha256(p.read_bytes()).hexdigest() for p in [HERE/'verify.py',HERE/'benchmark.py',HERE/'INPUT.json',HERE/'upstream_moment.py']},
            'summary':summary,'samples':rows}
    args.output.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'fresh_processes':len(rows),'summary':summary},indent=2))

if __name__=='__main__':
    main()

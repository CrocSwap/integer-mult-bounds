#!/usr/bin/env python3
"""Cold independent admission replay for the final merged PR4610 construction.
Apache-2.0. Construction credit: Cao Yifan/Cinna Davis and retained sources.
Independent audit integration and checkers: substantial OpenAI Codex assistance.
"""
from pathlib import Path
from fractions import Fraction as F
import argparse,hashlib,importlib,json,sys,time,tempfile,atexit
# -B prevents writes, not reads. A fresh namespace prevents stale/injected pyc.
_cache=tempfile.TemporaryDirectory(prefix="4610-bytecode-");atexit.register(_cache.cleanup)
sys.pycache_prefix=_cache.name;sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from checks import source
STAGES=('frame','native','helpers','all_helpers','paid','lineage','lift','invoice','arithmetic','compiler','specialization')

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--repo',type=Path,default=HERE.parents[1]);ap.add_argument('--receipt',type=Path);ap.add_argument('--preflight-only',action='store_true');ap.add_argument('--stages',nargs='+',choices=STAGES);a=ap.parse_args()
    source.need(__debug__,'Optimized execution is rejected: exact checks include guarded assertions; run without -O/-OO')
    started=time.monotonic();identity=source.bootstrap(a.repo,HERE/'SOURCES.json')
    if (not a.preflight_only and (not a.stages or 'paid' in a.stages)) or (HERE/'LOCAL-INPUTS.json').exists():
        identity.update(source.local_bootstrap(HERE))
    claim=json.loads((HERE/'CLAIM.json').read_bytes())
    from checks import claim as claim_checks
    claim_identity=claim_checks.run(claim)
    integrity=source.corruption_control();results={}
    stages=() if a.preflight_only else tuple(a.stages or STAGES)
    for stage in stages:
        module_name={'invoice':'census_controls','paid':'paid','specialization':'specialization'}.get(stage,stage)
        try:module=importlib.import_module('checks.'+module_name)
        except ModuleNotFoundError as e:raise ValueError('DRAFT: required stage not yet packaged: '+stage) from e
        if stage=='native':result=module.run(a.repo)
        elif stage in ('arithmetic','compiler'):
            source.need('invoice' in results,'arithmetic/compiler require fresh invoice in this same run')
            result=module.run(a.repo,results['invoice']) if stage=='compiler' else module.run(results['invoice'])
        else:result=module.run()
        results[stage]=result
    complete=stages==STAGES
    out={'status':'PASS_INDEPENDENT_FINAL4610_CONDITIONAL_ADMISSION' if complete else 'PASS_PREFLIGHT_ONLY' if a.preflight_only else 'PASS_PARTIAL_CHECKS_NOT_ADMISSION',
         'complete':complete,'claim':claim,'identity':identity,'input_integrity_control':integrity,'claim_identity':claim_identity,'results':results,
         'scope':'Independent source-compatible verification of Cao Yifan PR4610 under exactly selected4470 conditional assumptions. No new construction, unconditional/Lean multiplication theorem, selected-record edit, practical speedup or materialized uniform word.',
         'source_stability':source.final_recheck(),'elapsed_seconds':time.monotonic()-started,
         'checks_sha256':{str(p.relative_to(HERE)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(HERE.rglob('*.py'))},
         'source_manifest_sha256':source.digest((HERE/'SOURCES.json').read_bytes())}
    if a.receipt:a.receipt.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:out[k] for k in ('status','complete','elapsed_seconds')}|{'stages':list(results),'kappa':claim['decimal'],'gain':claim['gain_decimal']},sort_keys=True))
if __name__=='__main__':main()

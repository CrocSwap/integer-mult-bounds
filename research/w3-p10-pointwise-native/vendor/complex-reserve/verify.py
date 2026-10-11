#!/usr/bin/env python3
"""Mandatory content integrity and fresh PR348 fully regenerated complex admission.
Prepared with substantial OpenAI Codex assistance; Apache-2.0. No kappa claim.
"""
import sys
if not __debug__: raise SystemExit('Assertions required; refusing -O')
sys.dont_write_bytecode=True
import argparse,hashlib,json,os,subprocess,time
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text())

def integrity():
    actual={}
    for p in ROOT.rglob('*'):
        assert not p.is_symlink(),'symlink in package'
        if p.is_file() and p!=ROOT/'MANIFEST.json': actual[p.relative_to(ROOT).as_posix()]=sha(p)
    assert actual==read(ROOT/'MANIFEST.json')['files'],'Changed, missing or unpinned package source'
    pins=read(ROOT/'SOURCE.json')
    assert sha(ROOT/'vendor/neutral/MANIFEST.json')==pins['neutral_reference_manifest_sha256']
    for rel,digest in pins['generic_checker_provenance']['unchanged_files'].items():
        assert sha(ROOT/rel)==digest
    assert sha(ROOT/pins['candidate_path'])==pins['candidate_sha256']
    assert sha(ROOT/'upstream/pr348/MANIFEST.json')==pins['upstream_package_manifest_sha256']
    return sha(ROOT/'MANIFEST.json')

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output',required=True,type=Path); args=ap.parse_args()
    assert sys.version_info>=(3,11)
    begun=time.monotonic(); initial=integrity(); pins=read(ROOT/'SOURCE.json')
    out=args.output.resolve()
    assert not out.exists() and not out.is_relative_to(ROOT),'Use a fresh external output'
    out.mkdir(parents=True); (out/'logs').mkdir(); stages=[]
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
    for key in ('CX_PINS','CX_SOURCE_PINS','CX_RECORD'): env.pop(key,None)
    def run(stage,argv):
        print(stage,flush=True); start=time.monotonic(); log=out/'logs'/(stage+'.log')
        with log.open('w') as f:
            result=subprocess.run([sys.executable,'-B']+list(map(str,argv)),cwd=out,env=env,stdout=f,stderr=subprocess.STDOUT)
        assert result.returncode==0,stage+' failed with exit '+str(result.returncode)
        stages.append(dict(stage=stage,returncode=result.returncode,seconds=time.monotonic()-start,log_sha256=sha(log)))
    try:
        (out/'upstream-work').mkdir()
        run('complete-public-pr348-regeneration',[ROOT/'upstream/pr348/verify.py','--temp-root',out/'upstream-work'])
        run('complex-primary-input',[ROOT/'primary_input.py','--output',out/'candidate.json'])
        run('complete-p10-operational-transfer',[ROOT/'verify_supplier.py','--input',out/'candidate.json','--expected-sha256',pins['candidate_sha256'],'--output',out/'SUPPLIER-CHECK.json'])
        c=read(out/'SUPPLIER-CHECK.json')
        assert c['status']=='PASS_RESEARCH_P10_COMPLEX_SUPPLIER_FULL_SCALAR_SPLICE_GUARD_TWO_MOMENTS'
        assert c['candidate_sha256']==pins['candidate_sha256'] and c['kappa_claim'] is False
        assert c['parameters']==pins['parameters']
        for key,value in pins['ledger'].items(): assert c['ledger'][key]==value
        assert c['roots']['with_fallback']['b']==pins['complex_coarse']
        assert c['roots']['without_fallback']['b']==pins['complex_coarse_without_fallback']
        assert len(c['mutation_controls'])==20 and all(x['rejected'] for x in c['mutation_controls'])
        assert len(c['gx_check']['controls'])==2 and c['gx_check']['certificate_sha256']==pins['candidate_sha256']
        guard=c['finite_guard']
        assert guard['status']=='PASS_FRESH_EXACT_P10_COMPLEX_GUARD'
        assert (guard['live_per_vertex'],guard['physical_per_vertex'],guard['retained_row_coefficient'])==(10093,16367,20161)
        assert guard['physical_row_overcharge_coefficient']==15125 and guard['induction_gap_multiple_of_B']==115
        assert integrity()==initial,'Package source changed during replay'
        report=dict(status='PASS_PORTABLE_REGENERATED_PR348_P10_COMPLEX_SUPPLIER',manifest_sha256=initial,public_head=pins['public_head'],candidate_sha256=pins['candidate_sha256'],complex_coarse=pins['complex_coarse'],fresh_stages=stages,inputs_unchanged=True,receipt_hashes={name:sha(out/name) for name in ('candidate.json','SUPPLIER-CHECK.json')},seconds=time.monotonic()-begun,kappa_claim=False,producer_regeneration_claim=True,declarative_source=True,scope=pins['scope'])
        (out/'VERIFICATION.json').write_text(json.dumps(report,sort_keys=True,indent=2)+'\n')
        print('PASS fully regenerated PR348 complex supplier; b = '+pins['complex_coarse']+'; no kappa claim',flush=True)
    except BaseException as error:
        (out/'FAILURE.json').write_text(json.dumps(dict(status='FAIL',error=str(error),completed_stages=stages),indent=2)+'\n')
        raise
if __name__=='__main__':main()

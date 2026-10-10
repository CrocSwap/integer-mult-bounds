#!/usr/bin/env python3
"""Fresh portable replay of the PR315 complex supplier's frame retiming.
Prepared with substantial OpenAI Codex assistance; Apache-2.0.
"""
import sys
if not __debug__:raise SystemExit('Assertions required; refusing -O')
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
        if p.is_file() and p!=ROOT/'MANIFEST.json':actual[p.relative_to(ROOT).as_posix()]=sha(p)
    assert actual==read(ROOT/'MANIFEST.json')['files'],'Changed, missing or unpinned source'
    assert sha(ROOT/'vendor/pr315/MANIFEST.json')==read(ROOT/'SOURCE.json')['source_manifest_sha256']
    return sha(ROOT/'MANIFEST.json')

def structural_selection(data):
    return [{k:v for k,v in row.items() if k not in ('log_gain','log_improvement')} for row in data]

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',required=True,type=Path);a=ap.parse_args()
    assert sys.version_info>=(3,11);start=time.monotonic();initial=integrity();pins=read(ROOT/'SOURCE.json')
    out=a.output.resolve();assert not out.exists() and not out.is_relative_to(ROOT),'Use a fresh external output'
    out.mkdir(parents=True);(out/'logs').mkdir();env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1');stages=[]
    def run(name,args):
        print(name,flush=True);begun=time.monotonic()
        with (out/'logs'/(name+'.log')).open('w') as f:subprocess.run([sys.executable,'-B']+list(map(str,args)),check=True,stdout=f,stderr=subprocess.STDOUT,env=env,cwd=out)
        stages.append(dict(stage=name,seconds=time.monotonic()-begun))
    try:
        run('split-and-single-retiming',[ROOT/'frame_retime.py','--output',out/'single','--split-groups','--passes','30'])
        assert sha(out/'single/candidate.json')==pins['single_sha256']
        assert structural_selection(read(out/'single/selection.json'))==structural_selection(read(ROOT/'stages/single-selection.json'))
        assert len(read(out/'single/selection.json'))==29
        run('component-retiming',[ROOT/'plateau_retime.py','--input',out/'single/candidate.json','--output',out/'plateau','--passes','30'])
        assert sha(out/'plateau/candidate.json')==pins['plateau_sha256']
        assert structural_selection(read(out/'plateau/selection.json'))==structural_selection(read(ROOT/'stages/component-selection.json'))
        assert len(read(out/'plateau/selection.json'))==69
        run('neutral-down-retiming',[ROOT/'plateau_retime.py','--input',out/'plateau/candidate.json','--output',out/'neutral-down','--passes','30','--neutral','down'])
        assert sha(out/'neutral-down/candidate.json')==pins['neutral_down_sha256']
        assert structural_selection(read(out/'neutral-down/selection.json'))==structural_selection(read(ROOT/'stages/neutral-down-selection.json'))
        assert len(read(out/'neutral-down/selection.json'))==50
        run('neutral-up-retiming',[ROOT/'plateau_retime.py','--input',out/'neutral-down/candidate.json','--output',out/'candidate','--passes','30','--neutral','up'])
        assert sha(out/'candidate/candidate.json')==pins['candidate_sha256']
        assert structural_selection(read(out/'candidate/selection.json'))==structural_selection(read(ROOT/'stages/neutral-up-selection.json'))
        assert len(read(out/'candidate/selection.json'))==672
        run('complete-supplier-admission',[ROOT/'verify_supplier.py','--input',out/'candidate/candidate.json','--expected-sha256',pins['candidate_sha256']])
        result=read(out/'candidate/SUPPLIER-CHECK.json')
        assert result['status']=='PASS_RESEARCH_COMPLEX_SUPPLIER_FRAME_RETIMING'
        assert result['roots']['with_fallback']['b']==pins['complex_coarse']
        assert result['roots']['without_fallback']['b']==pins['complex_coarse_without_fallback']
        assert result['ledger']['calls']==351655 and result['ledger']['rank_mass']==1571680 and result['ledger']['deficit']==3080
        assert result['unchanged_scalar_program'] and result['unchanged_scatter_ports_endpoints']
        assert result['gx_check']['status']=='PASS_COMPLEX_PROGRAM_GX_CHECK1_SCALAR_AND_GXCORE_MIRROR'
        assert len(result['gx_check']['controls'])==2 and len(result['mutation_controls'])==14
        assert integrity()==initial,'Source mutated during replay'
        report=dict(status='PASS_PORTABLE_COMPLEX_NEUTRAL_FRAME_RETIMING_SUPPLIER',candidate_sha256=pins['candidate_sha256'],
                    manifest_sha256=initial,inputs_unchanged=True,fresh_stages=stages,complex_coarse=pins['complex_coarse'],
                    supplier_receipt_sha256=sha(out/'candidate/SUPPLIER-CHECK.json'),kappa_claim=False,seconds=time.monotonic()-start,
                    scope=result['scope'])
        (out/'VERIFICATION.json').write_text(json.dumps(report,sort_keys=True,indent=2)+'\n')
        print('PASS complex coarse = '+pins['complex_coarse']+'; no kappa claim',flush=True)
    except BaseException as error:
        (out/'FAILURE.json').write_text(json.dumps(dict(status='FAIL',error=str(error),completed=stages),indent=2)+'\n');raise

if __name__=='__main__':main()

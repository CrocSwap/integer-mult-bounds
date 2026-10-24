"""Bind the completed gate and palette receipts; verify by default.
Cao Yifan; substantial OpenAI Codex assistance. Apache-2.0.
This coherence audit does not rerun Lean, the rank census or the optimizer.
"""
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
import realification_census as R

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
FILES=['README.md','PLAN.md','.gitattributes','.gitignore','SOURCES.json','pin_sources.py',
       'PauliHole.lean','PauliHole.log','pauli_hole.py','replay_pauli_lean.py','LEAN-PAULI-HOLE.json',
       'PAULI-HOLE.json.gz','realification_census.py','REALIFICATION-CENSUS.json.gz',
       'mixed_gauge.py','MIXED-GAUGE.json.gz','weighted_gauge.py','WEIGHTED-GAUGE.json.gz',
       'weighted_milp.py','WEIGHTED-MILP.json.gz','palette_gauge.py','PALETTE-GAUGE.json.gz','freeze.py']


def digest(path):return sha256(path.read_bytes()).hexdigest()


def audit():
    pins=R.read(HERE/'SOURCES.json')
    for pin in pins['files']:
        raw=(HERE/pin['copy']).read_bytes()
        R.need(sha256(raw).hexdigest()==pin['sha256'],'Copied source SHA-256')
        blob=subprocess.check_output(['git','rev-parse',pin['git_commit']+':'+pin['path']],cwd=ROOT).decode().strip()
        R.need(blob==pin['git_blob'],'Pinned commit:path resolves to recorded blob')
        R.need(raw==subprocess.check_output(['git','cat-file','blob',blob],cwd=ROOT),'Copied source is the Git blob bytes')
    mapping={'PAULI-HOLE.json.gz':'pauli_hole.py','REALIFICATION-CENSUS.json.gz':'realification_census.py',
             'MIXED-GAUGE.json.gz':'mixed_gauge.py','WEIGHTED-GAUGE.json.gz':'weighted_gauge.py',
             'WEIGHTED-MILP.json.gz':'weighted_milp.py','PALETTE-GAUGE.json.gz':'palette_gauge.py'}
    receipts={}
    for name,script in mapping.items():
        r=R.read(HERE/name);receipts[name]=r
        R.need(r['script_sha256']==digest(HERE/script),'Receipt binds its script: '+name)
        R.need(r['new_kappa'] is False,'No finite negative receipt claims new kappa')
        if 'source_manifest_sha256' in r:R.need(r['source_manifest_sha256']==digest(HERE/'SOURCES.json'),'Receipt pins source manifest')
        for helper,h in r.get('helper_script_sha256',{}).items():R.need(digest(HERE/helper)==h,'Receipt binds helper script')
    R.need(receipts['MIXED-GAUGE.json.gz']['helper_sha256']==digest(HERE/'realification_census.py'),'Mixed graph binds actual compiler helper')
    for name in ['WEIGHTED-GAUGE.json.gz','WEIGHTED-MILP.json.gz']:
        R.need(receipts[name]['graph_sha256']==digest(HERE/'MIXED-GAUGE.json.gz'),'Weighted receipt binds exact graph')
    R.need(receipts['WEIGHTED-MILP.json.gz']['setup_sha256']==digest(HERE/'WEIGHTED-GAUGE.json.gz'),'Weighted MILP binds exact moment setup')
    for r in [receipts['WEIGHTED-MILP.json.gz'],receipts['PALETTE-GAUGE.json.gz']]:
        for block in r['results']:
            for case in block['cases']:
                R.need(case['changed_components']==0 and case['moment_gain_lower']==case['moment_gain_upper']=='0',
                       'Completed weighted candidate has exactly zero gain')
    R.need(all(c.get('passed',c.get('rejected',False)) for c in receipts['PALETTE-GAUGE.json.gz']['controls']),
           'Actual native and ownership controls')
    lean=R.read(HERE/'LEAN-PAULI-HOLE.json')
    R.need(lean['exit_code']==0 and lean['source_sha256']==digest(HERE/lean['source']) and
           lean['log_sha256']==digest(HERE/lean['log']),'Lean source and successful fresh compilation log')
    R.need(len(lean['axioms'])==2 and all(set(row['axioms'])<=set(lean['allowed_axioms']) for row in lean['axioms']),
           'Both Lean axiom reports are standard')
    return dict(status='PASS_COMPLETED_PAULI_AND_FRAME_PALETTE_COHERENCE',source_pins=len(pins['files']),
                lean_reports=2,receipt_count=len(receipts),new_kappa=False,
                files={name:digest(HERE/name) for name in FILES},
                scope='Byte/provenance/receipt coherence only. Fresh run outputs are preserved; floating MIP status is not formal global optimality.')


def main():
    result=audit();target=HERE/'FREEZE.json'
    if '--freeze' in sys.argv:
        R.need(not target.exists(),'Do not overwrite the completed freeze manifest')
        target.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    else:R.need(result==R.read(target),'Completed frozen core bytes remain unchanged')
    print(result['status'],'pins',result['source_pins'],'Lean reports',result['lean_reports'],'receipts',result['receipt_count'])


if __name__=='__main__':main()

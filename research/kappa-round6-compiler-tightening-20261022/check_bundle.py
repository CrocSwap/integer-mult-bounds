"""Check publication bytes and recorded proof/input hashes; does not run Lean.
Cao Yifan; substantial OpenAI Codex assistance. Apache-2.0.
"""
from hashlib import sha256
from pathlib import Path
import argparse
import json

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]

def need(ok,message):
    if not ok:raise ValueError(message)

def digest(path):return sha256(Path(path).read_bytes()).hexdigest()
def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))

def files():
    for p in sorted(HERE.rglob('*')):
        rel=p.relative_to(HERE)
        if not p.is_file() or any(x in {'.lean-build','__pycache__','.scratch'} for x in rel.parts):continue
        if p.suffix in {'.olean','.ilean','.pyc'}:continue
        if rel.as_posix()=='PUBLICATION.json':continue
        yield p

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--write-inventory',action='store_true')
    ap.add_argument('--compare-root',type=Path)
    args=ap.parse_args()
    r=read(HERE/'LEAN-VERIFICATION.json')
    need(r['status']=='PASS_TIGHTENED_SCOPED_LEAN_CERTIFICATES','Completed fresh proof receipt required')
    need(len(r['modules'])==4 and r['fresh_axiom_reports']==31,'Fresh proof inventory')
    need(digest(HERE/'verify_lean.py')==r['script_sha256'],'Replay tool bytes')
    need(digest(HERE/'ARITHMETIC.json')==r['arithmetic_sha256'],'Arithmetic bytes')
    for name,pin in r['local_source_sha256'].items():
        need(digest(HERE/name)==pin,'Local proof input drift: '+name)
    for name,pin in r['input_sha256'].items():
        need(digest(ROOT/name)==pin,'External proof input drift: '+name)
    allow={'propext','Classical.choice','Quot.sound'}
    for row in r['modules']:
        need(row['exit_code']==0,'Failed recorded module')
        for kind,suffix in [('source','.lean'),('log','.log')]:
            need(digest(HERE/(row['module']+suffix))==row[kind+'_sha256'],'Fresh '+kind+' drift')
        need(all(set(a['axioms'])<=allow for a in row['axioms']),'Unexpected axiom in recorded proof')
    native=ROOT/'research/kappa-round3-warp-lean-20261022'
    for row in r['native_reuse_modules']:
        for kind,suffix in [('source','.lean'),('log','.log')]:
            need(digest(native/(row['module']+suffix))==row[kind+'_sha256'],'Reused '+kind+' drift')
    audit=read(HERE/'audit/AUDIT.json')
    need(audit['status']=='PASS_INDEPENDENT_COMPLETE_INVOICE_COMPILER_AND_58_OUTER_FORMULAS','Independent arithmetic audit')
    need(audit['arithmetic_sha256']==r['arithmetic_sha256'],'Audited arithmetic bytes')
    need(audit['replay_sha256']==digest(HERE/'audit/replay.py'),'Independent auditor bytes')
    for name,pin in audit['proof_source_sha256'].items():need(digest(HERE/name)==pin,'Audited proof source drift')
    controls=read(HERE/'audit/CONTROLS.json')
    need(controls['status']=='PASS_ACTUAL_VERIFIER_ISOLATED_CORRUPTION_CONTROLS','Verifier rejection controls')
    need(controls['verifier_sha256']==r['script_sha256'],'Controlled replay tool bytes')
    need(controls['control_runner_sha256']==digest(HERE/'audit/controls.py'),'Control runner bytes')
    need(len(controls['results'])==3 and all(x['rejected'] and x['failed_before_Lean_compilation'] for x in controls['results']),'Three rejected corruptions')
    # Compiled output hashes were checked by the actual replay. Objects are
    # deliberately absent from the publication inventory and are not rechecked here.
    listing={p.relative_to(HERE).as_posix():dict(bytes=p.stat().st_size,sha256=digest(p)) for p in files()}
    if args.write_inventory:
        (HERE/'PUBLICATION.json').write_text(json.dumps(dict(
            status='PINNED_SOURCE_LOG_AND_AUDIT_BUNDLE',files=listing,
            fresh_modules=4,fresh_axiom_reports=31,reused_modules=len(r['native_reuse_modules']),
            scope='Byte inventory and recorded source/log/input verification only; no new Lean compilation or formal multiplication theorem.'
        ),indent=2,sort_keys=True)+'\n',encoding='utf-8',newline='\n')
    else:need(read(HERE/'PUBLICATION.json')['files']==listing,'Publication inventory drift')
    if args.compare_root:
        other=args.compare_root.resolve()/'research'/HERE.name
        for name,row in listing.items():need(digest(other/name)==row['sha256'],'Publication copy differs: '+name)
        need(digest(other/'PUBLICATION.json')==digest(HERE/'PUBLICATION.json'),'Publication manifest differs')
    print('PASS_SOURCE_LOG_INPUT_BUNDLE',len(listing),'files;',len(r['native_reuse_modules']),'explicitly reused modules; no new compilation')

if __name__=='__main__':main()

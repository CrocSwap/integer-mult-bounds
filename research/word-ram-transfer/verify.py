"""Byte-bound finite replay. Dugongue; substantial OpenAI assistance; Apache-2.0."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parent

def require(ok, message):
    if not ok:
        raise ValueError(message)

def main():
    manifest=json.loads((ROOT/'CONTENT-HASHES.json').read_text(encoding='utf-8'))
    actual={x.relative_to(ROOT).as_posix() for x in ROOT.rglob('*') if x.is_file() and '__pycache__' not in x.parts}
    require(actual == set(manifest) | {'CONTENT-HASHES.json'}, 'Package inventory differs from authenticated manifest')
    for name,expected in manifest.items():
        path=ROOT/name
        require(path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest()==expected, 'Source drift: '+name)
    reports={}
    for name in ['compiler/tm_to_ramstd.py','packed_tape.py','cost/streaming_affine.py','cost/quadratic_phase.py','cost/monomial_metadata.py']:
        run=subprocess.run([sys.executable,'-I','-O','-B',str(ROOT/name)],capture_output=True,text=True,encoding='utf-8',timeout=110)
        require(run.returncode==0, name+' failed: '+run.stderr[-2000:])
        reports[name]=json.loads(run.stdout)
    c=reports['compiler/tm_to_ramstd.py']
    require(c['cases']==246 and c['macro_boundaries']==4794 and c['small_word_rejections']==1,'TM replay coverage changed')
    require(len(c['emitted_code_faults_rejected'])==5 and c['lsb_emitter']['wrong_direction_code_rejected'],'TM negative controls missing')
    p=reports['packed_tape.py']
    require(p['operation_traces']==15360 and p['get_instructions']==13 and p['set_instructions']==17 and p['wrong_bank_rejected'] and p['dirty_padding_preserved'],'Packed representation control missing')
    receipt=json.loads((ROOT/'machine/INDEPENDENT-AUDIT.json').read_text(encoding='utf-8'))
    require(receipt['status']=='VERIFIED' and len(receipt['theorems'])==5,'Missing formal audit receipt')
    require(receipt['sha256']==manifest['machine/WordRAMLogWidthTransfer20261022.lean'],'Formal source differs from audit')
    allowed={'propext','Classical.choice','Quot.sound'}
    require(all(set(t['axioms'])<=allowed for t in receipt['theorems']),'Nonstandard axiom receipt')
    dependencies=json.loads((ROOT/'machine/DEPENDENCIES.json').read_text(encoding='utf-8'))
    for row in dependencies['files']:
        require(hashlib.sha256((ROOT/'machine/sources'/row['relative_path']).read_bytes()).hexdigest()==row['sha256'],'Frozen Lean dependency drift')
    print(json.dumps({'status':'PASS','scope':'finite exact replays and authenticated historical Lean audit; no fresh Lean build in this command; no new kappa','reports':reports},indent=2))

if __name__=='__main__':
    main()

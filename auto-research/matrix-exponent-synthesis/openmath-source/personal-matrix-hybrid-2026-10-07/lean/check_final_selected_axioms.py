"""Fresh serial reproduction using installed pinned Lean/Lake and fetched dependencies.
No historical receipts are overwritten. Run from any directory; no package install here.
"""
from pathlib import Path
import hashlib, json, os, re, subprocess
from datetime import datetime, timezone
ROOT = Path(__file__).resolve().parent
MANIFEST = json.loads((ROOT / 'final_source_manifest.json').read_text(encoding='utf8'))
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def require(ok, message):
    if not ok: raise RuntimeError(message)
def run(command):
    env = dict(os.environ, LEAN_NUM_THREADS='1')
    p = subprocess.run(command, cwd=ROOT, env=env, capture_output=True)
    return p.returncode, p.stdout.decode('utf8', errors='replace'), p.stderr.decode('utf8', errors='replace')
def main():
    for row in MANIFEST['sources_in_build_order']:
        p=ROOT/row['file']
        require(p.stat().st_size==row['bytes'] and digest(p)==row['sha256'], 'source mismatch '+row['file'])
    require(digest(ROOT/MANIFEST['audit']['file'])==MANIFEST['audit']['sha256'], 'audit mismatch')
    lock=json.loads((ROOT/'lake-manifest.json').read_text(encoding='utf8'))
    require({p['name']:p['rev'] for p in lock['packages']}=={p['name']:p['rev'] for p in MANIFEST['dependency_pins']}, 'lock pin mismatch')
    code, version, err=run(['lake','env','lean','--version'])
    require(code==0 and 'version 4.33.1,' in version, 'wrong Lean version')
    fresh=ROOT/'reproduction'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    fresh.mkdir(parents=True, exist_ok=False)
    lib=ROOT/'.lake/build/lib/lean';lib.mkdir(parents=True, exist_ok=True)
    rows=[]
    for row in MANIFEST['sources_in_build_order']:
        cmd=['lake','env','lean','-j1','-DautoImplicit=false','-DrelaxedAutoImplicit=false','-o',str(lib/(row['module']+'.olean')),row['file']]
        code,out,err=run(cmd)
        (fresh/(row['module']+'.stdout.txt')).write_text(out,encoding='utf8')
        (fresh/(row['module']+'.stderr.txt')).write_text(err,encoding='utf8')
        require(code==0, 'source compilation failed '+row['module'])
        rows.append({'module':row['module'],'source_sha256':row['sha256'],'exit_code':code})
    code,out,err=run(['lake','env','lean','-j1','-DautoImplicit=false','-DrelaxedAutoImplicit=false','SelectedFinalAxiomAudit.lean'])
    (fresh/'SelectedFinalAxiomAudit.stdout.txt').write_text(out,encoding='utf8')
    (fresh/'SelectedFinalAxiomAudit.stderr.txt').write_text(err,encoding='utf8')
    require(code==0,'selected audit failed')
    parsed={}
    for name,values in re.findall(r"'([^']+)' depends on axioms:\s*\[([^\]]*)\]",out):
        require(name not in parsed,'duplicate selected print '+name)
        parsed[name]=[v.strip() for v in values.split(',') if v.strip()]
    require(set(parsed)==set(MANIFEST['selected_endpoints']), 'selected endpoint set mismatch')
    allowed={'propext','Classical.choice','Quot.sound'}
    require(all(set(values)<=allowed for values in parsed.values()),'native/custom/sorry axiom')
    for row in MANIFEST['sources_in_build_order']:
        require(digest(ROOT/row['file'])==row['sha256'],'source changed during reproduction')
    receipt={'schema':'personal-matrix-fresh-serial-reproduction-v1','status':'PASS','checked_utc':datetime.now(timezone.utc).isoformat(),
        'sources':rows,'selected_axioms':parsed,'standard_endpoint_count':len(parsed),'lean_version':version.strip(),
        'historical_qualification_sha256':MANIFEST['qualification_sha256']}
    (fresh/'actual_reproduction.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'status':'PASS','source_count':len(rows),'standard_endpoint_count':len(parsed),'receipt':str(fresh/'actual_reproduction.json')}))
if __name__=='__main__': main()

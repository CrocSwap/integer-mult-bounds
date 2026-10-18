"""Read-only full finite conditional application; Lean replay is separate."""
from pathlib import Path
import argparse,hashlib,json,os,subprocess,sys,tempfile
P=Path(__file__).resolve().parent
def need(ok,msg):
    if not ok:raise ValueError(msg)
def rd(p):return json.loads(p.read_bytes())
def snapshot():return{p.relative_to(P).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in P.rglob('*')if p.is_file()}
def run(work,cache=None):
    before=snapshot();manifest=rd(P/'MANIFEST.json')
    need(set(before)==set(manifest)|{'MANIFEST.json'}and all(before[k]==v for k,v in manifest.items()),'package manifest differs')
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONUTF8='1',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1');env.pop('PYTHONOPTIMIZE',None)
    args=[sys.executable,'-B',str(P/'verify_release.py'),'--main',str(Path.cwd()),'--work',str(work/'release'),'--jobs','3']
    if cache:args+=['--native-cache',str(cache.resolve())]
    subprocess.run(args,check=True,env=env)
    strict=work/'release/verify/strict'
    admitted_owners=work/'release/verify/parent/layout/packing74/candidate/OWNERS.json.gz'
    need(hashlib.sha256(admitted_owners.read_bytes()).hexdigest()==before['OWNERS.json.gz'],
         'admitted OWNERS differs from immutable package owner archive')
    subprocess.run([sys.executable,'-B',str(P/'hosted_owner_binding.py'),
                    '--hosted',str(strict/'global/hosted/GLOBAL-TEMPLATE.json.gz'),
                    '--owners',str(admitted_owners),'--assembly',str(strict/'ASSEMBLY.json'),
                    '--out',str(work/'HOSTED-OWNERS-BINDING.json')],check=True,env=env)
    subprocess.run([sys.executable,'-B',str(P/'ordinary_bootstrap.py'),'--out',str(work/'ORDINARY-BOOTSTRAP.json')],check=True,env=env)
    release=rd(work/'release/RELEASE-RECEIPT.json');supplier=rd(work/'release/verify/RESULT.json');ordinary=rd(work/'ORDINARY-BOOTSTRAP.json')
    invoice=rd(work/'release/verify/strict/global/audit/PREFIX-AND-INVOICE.json')
    need(release['status']=='PASS_RELEASE'and supplier['status']=='PASS_T74_EXACT_FILL_COMPLETE_FINITE_ADMISSION','incomplete supplier/outer admission')
    owner_link=rd(work/'HOSTED-OWNERS-BINDING.json')
    need(owner_link['status']=='PASS_HOSTED_OWNERS_CROSS_STAGE_BINDING' and owner_link['roles']==supplier['roles'] and len(owner_link['mutations_rejected'])==2,'incomplete hosted owner-map binding')
    need(snapshot()==before,'source changed during full replay')
    result=dict(status='PASS_COMPLETE_NEW_CONDITIONAL_KAPPA_PACKAGE',kappa_decimal=release['kappa_decimal'],source_manifest_sha256=before['MANIFEST.json'],roles=supplier['roles'],physical=invoice['physical'],row=supplier['physical_row_coefficient'],supplier_controls=supplier['controls'],ordinary_bootstrap_levels=ordinary['levels'],source_unchanged=True,hosted_owner_binding=True,hosted_owner_binding_controls=2,scope='Complete finite conditional construction; explicit inherited all-size/compiler/fixed-tape/precision/recovery/analytic and modern outer premises remain. Full multiplication and Python certificates are not formalized in Lean; fresh Lean audit is separate.')
    (work/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2),flush=True)
def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--out',type=Path);ap.add_argument('--native-cache',type=Path);a=ap.parse_args()
    if a.out:
        need(not a.out.resolve().is_relative_to(P),'external output directory required');a.out.mkdir(parents=True,exist_ok=False);run(a.out,a.native_cache)
    else:
        with tempfile.TemporaryDirectory(prefix='t74-pure44-')as t:run(Path(t),a.native_cache)
if __name__=='__main__':main()

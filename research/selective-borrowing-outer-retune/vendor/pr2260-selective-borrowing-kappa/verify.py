#!/usr/bin/env python3
"""Fresh, read-only complete finite conditional supplier replay (stdlib only)."""
import argparse,gzip,hashlib,json,subprocess,sys,tempfile,time
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent

def need(ok,label):
    if not ok:raise ValueError(label)
def read(path):return json.loads(path.read_bytes())
def snapshot():
    return {p.relative_to(HERE).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in HERE.rglob('*') if p.is_file()}
def run(work):
    before=snapshot();manifest=read(HERE/'MANIFEST.json')['sha256']
    need(set(before)==set(manifest)|{'MANIFEST.json'},'package contains missing or undeclared files')
    need(all(before[k]==v for k,v in manifest.items()),'frozen package SHA256 differs')
    def command(script,*args):
        subprocess.run([sys.executable,'-I','-O','-B',str(HERE/script),*map(str,args)],check=True,timeout=500)
    command('local/verify.py','--out',work/'LOCAL.json')
    command('owners/verify.py','--out',work/'owners')
    command('independent/verify.py','--work',work/'independent')
    command('local/invoice.py','--variant',HERE/'local/data','--owners',HERE/'owners/OWNERS.json.gz','--out',work/'INVOICE.json')
    need(read(work/'INVOICE.json')==read(HERE/'local/data/finite-invoice.json'),'fresh finite invoice differs')
    command('arithmetic/verify.py','--out',work/'ARITHMETIC.json')
    local=read(work/'LOCAL.json');owner=read(work/'owners/OWNERS-RECEIPT.json');invoice=read(work/'INVOICE.json');arithmetic=read(work/'ARITHMETIC.json')
    need(local['source_hashes']['forward_trace']==owner['source_trace_sha256'],'local and owner word differ')
    need(owner['owners_sha256']==invoice['owner_table_sha256'],'owner and finite invoice differ')
    need(arithmetic['source_sha256']['owners/OWNERS.json.gz']==owner['owners_sha256'],'arithmetic owner differs')
    need(arithmetic['profile']==owner['profile'],'complete paid profiles differ')
    need(arithmetic['kappa']=='3361/2000000','wrong final kappa')
    need(snapshot()==before,'source package changed during replay')
    result=dict(status='PASS_COMPLETE_FINITE_CONDITIONAL_KAPPA',kappa=arithmetic['kappa'],kappa_decimal=arithmetic['kappa_decimal'],source_manifest_sha256=hashlib.sha256((HERE/'MANIFEST.json').read_bytes()).hexdigest(),all_source_files_unchanged=True,physical_roles=owner['roles'],physical_stock=invoice['physical_families'],native_jobs=sum(r['native_jobs'] for r in local['reports'].values()),strict_outer_rows=len(arithmetic['outer_constraints']),scope='All supplied finite identities, physical factor partition, exact fine-grid invoice and rational asymptotic assembly checked. Inherits original all-size compiler/physical fixed-tape/analytic transfer and retained bit supplier assumptions. Optional Lean lemmas are separate; this replay is not a Lean proof of multiplication.')
    (work/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2),flush=True)

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--out',type=Path,help='Nonexistent external directory for receipts (otherwise temporary).');args=parser.parse_args()
    if args.out:
        need(not args.out.resolve().is_relative_to(HERE),'output must be outside source package')
        args.out.mkdir(parents=True,exist_ok=False);run(args.out)
    else:
        with tempfile.TemporaryDirectory(prefix='selective-borrowing-kappa-') as d:run(Path(d))
if __name__=='__main__':main()

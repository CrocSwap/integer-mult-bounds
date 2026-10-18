#!/usr/bin/env python3
"""Complete conditional kappa application plus source-bound reusable lemma checks."""
import argparse,gzip,hashlib,json,subprocess,sys,tempfile,os
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;BASE=HERE.parent/'selective-borrowing-kappa'
def need(ok,label):
    if not ok:raise ValueError(label)
def read(path):return json.loads(path.read_bytes())
def snapshot(root):return{p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in root.rglob('*')if p.is_file()}
def run(work):
    before=snapshot(HERE);base_before=snapshot(BASE);manifest=read(HERE/'MANIFEST.json')['sha256']
    need(set(before)==set(manifest)|{'MANIFEST.json'}and all(before[k]==v for k,v in manifest.items()),'toolkit package manifest differs')
    base_manifest=read(BASE/'MANIFEST.json')['sha256']
    need(set(base_before)==set(base_manifest)|{'MANIFEST.json'}and all(base_before[k]==v for k,v in base_manifest.items()),'predecessor source package drift')
    expected_base=read(HERE/'SOURCES.json')['retained_sources']['manifest_sha256']
    need(hashlib.sha256((BASE/'MANIFEST.json').read_bytes()).hexdigest()==expected_base,'wrong predecessor package')
    def command(script,*args,assertions=False):
        flags=['-B']if assertions else['-I','-O','-B'];env=dict(os.environ);env.pop('PYTHONOPTIMIZE',None)
        subprocess.run([sys.executable,*flags,str(script),*map(str,args)],check=True,timeout=500,env=env)
    # Recompose the immutable predecessor checks without requiring a platform-dependent
    # generated gzip hash from its historical independent receipt.
    command(BASE/'local/verify.py','--out',work/'LOCAL.json')
    command(BASE/'owners/verify.py','--out',work/'predecessor-owners')
    command(BASE/'arithmetic/verify.py','--out',work/'PREDECESSOR-ARITHMETIC.json')
    command(HERE/'build_toolkit.py','--check')
    audit=read(HERE/'LEAN-AUDIT.json');index=read(HERE/'LEMMA-INDEX.json')
    need(hashlib.sha256((HERE/'Toolkit.lean').read_bytes()).hexdigest()==audit['source_sha256'],'standalone audit source differs')
    names={n for part in index['parts']for n in part['theorems']+part['definitions']}
    need({x['name']for x in audit['exports']}==names and len(names)==106,'incomplete declaration audit')
    need(sum(x['kind']=='theorem'for x in audit['exports'])==87,'wrong theorem inventory')
    need(all(set(x['axioms'])<={'propext','Classical.choice','Quot.sound'}for x in audit['exports']),'unapproved source axiom')
    # Verify the whole declared old->new literal row delta, including offsets.
    old=json.loads(gzip.decompress((BASE/'owners/OWNERS.json.gz').read_bytes()));new=json.loads(gzip.decompress((HERE/'OWNERS.json.gz').read_bytes()));delta=json.loads(gzip.decompress((HERE/'OWNER-DELTA.json.gz').read_bytes()));seen=set()
    need(delta['old_sha256']==base_before['owners/OWNERS.json.gz']and delta['new_sha256']==before['OWNERS.json.gz'],'delta source binding')
    for move in delta['changes']:
        i=move['row'];need(i not in seen and old[i]==move['before'],'changed row mismatch or duplicated delta');seen.add(i)
        need(all(move['before'][k]==move['after'][k]for k in ('time','stage','replica','helper','width')),'role inventory changed in owner delta');old[i]=move['after']
    need(old==new and len(seen)==93,'complete literal owner delta differs')
    command(HERE/'owners_replay.py','--out',work/'owners')
    owner=read(work/'owners/RESULT.json');need(owner==read(HERE/'OWNERS-EXPECTED.json'),'actual owner/chart receipt differs')
    command(HERE/'physical_replay.py','--out',work/'physical')
    physical=read(work/'physical/MATHEMATICAL-RESULT.json');need(physical==read(HERE/'PHYSICAL-EXPECTED.json'),'actual physical factor receipt differs')
    command(BASE/'local/invoice.py','--variant',BASE/'local/data','--owners',HERE/'OWNERS.json.gz','--out',work/'INVOICE.json')
    invoice=read(work/'INVOICE.json');need(invoice==read(HERE/'INVOICE-EXPECTED.json'),'fresh finite invoice differs')
    command(HERE/'profile_transfer.py','--out',work/'TRANSFER.json');need(read(work/'TRANSFER.json')==read(HERE/'TRANSFER-EXPECTED.json'),'exact old/new cost transfer differs')
    command(HERE/'price.py','--out',work/'PRICE.json');price=read(work/'PRICE.json');need(price==read(HERE/'PRICE-EXPECTED.json'),'new exact price differs')
    command(HERE/'check_portability.py','--physical',work/'physical','--out',work/'PORTABILITY.json')
    need(price['kappa']=='84037/50000000'and owner['profile']==price['profile']==physical['complete_profile'],'profile/kappa mismatch')
    command(HERE/'outer/verify.py','--out',work/'OUTER.json',assertions=True)
    modern=read(work/'OUTER.json')
    need(modern['kappa']=='168357/100000000'and modern['supplier_C']==price['certified_complex_saving'],'modern advertised kappa/supplier rate mismatch')
    command(HERE/'ordinary_bootstrap.py','--out',work/'ORDINARY-BOOTSTRAP.json')
    need(read(work/'ORDINARY-BOOTSTRAP.json')==read(HERE/'ORDINARY-BOOTSTRAP-EXPECTED.json'),'finite ordinary bootstrap differs')
    need(modern['owners_sha256']==owner['owners_sha256']and modern['profile']==owner['profile'],'modern outer uses a different physical supplier')
    need(owner['owners_sha256']==invoice['owner_table_sha256']==physical['source_sha256']['owners'],'different actual owner sources')
    need(snapshot(HERE)==before and snapshot(BASE)==base_before,'source files changed during replay')
    result=dict(status='PASS_LEMMA_TOOLKIT_AND_COMPLETE_CONDITIONAL_KAPPA',kappa=modern['kappa'],kappa_decimal=modern['kappa_decimal'],previous_supplier_kappa='0.0016805',legacy_outer_kappa=price['kappa_decimal'],latest_reviewed_outer_pr=2269,latest_reviewed_outer_claim_approximately='0.0016962471390584742',current_numerical_record_claimed=False,finite_ordinary_bootstrap_levels=31,source_manifest_sha256=hashlib.sha256((HERE/'MANIFEST.json').read_bytes()).hexdigest(),named_theorem_apis=87,theorems_in_new_modules=76,definitions_audited=19,lemma_validation='Source-bound fresh independent kernel/axiom audit already completed; this Python replay checks immutable bindings. Run audit_lean.py for a new kernel replay.',physical_roles=owner['roles'],actual_73column_charts=owner['actual_73column_charts'],native_jobs_replayed=5992,legacy_strict_outer_rows=len(price['outer_constraints']),modern_strict_outer_rows=modern['strict_rows'],modern_rejecting_controls=modern['rejecting_controls'],retained_outer_evidence_replays=modern['supplier_independent_replays'],all_source_files_unchanged=True,scope='Universal reusable sufficient Lean lemmas plus complete finite conditional kappa application. Full compiler/tape/bit/recovery/analytic interfaces remain inherited, with additional modern capped-fusion/gauge-free/radix-union/fine-prime premises explicitly required; no full Lean multiplication theorem.')
    (work/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2),flush=True)
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',type=Path);a=p.parse_args()
    if a.out:
        need(not a.out.resolve().is_relative_to(HERE.parent),'use an external output directory');a.out.mkdir(parents=True,exist_ok=False);run(a.out)
    else:
        with tempfile.TemporaryDirectory(prefix='kappa-lemma-toolkit-')as t:run(Path(t))
if __name__=='__main__':main()

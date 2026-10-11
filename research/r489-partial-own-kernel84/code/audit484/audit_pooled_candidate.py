"""Portable independent admission of the complete pooled PR484 derivative.
Prepared by OpenAI Codex. Inputs are fresh supplier replay outputs and new
serialized candidate, with separate stdlib controller audit supplied by another
checker. No source or supplier result is modified.
"""
from pathlib import Path
import argparse,json,subprocess,sys,hashlib,gzip
p=argparse.ArgumentParser()
for x in ['parent','hosted','bit-result','phases','controller-audit','out']:p.add_argument('--'+x,type=Path,required=True)
a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False);C=Path(__file__).resolve().parent;steps=[];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
commands=[('owners',[C/'audit_pooled_owners.py',a.out,a.parent,a.hosted,a.phases]),('scalar-invoice',[C/'audit_scalar_invoice.py',a.out,a.parent,a.hosted]),('global-prefix',[C/'audit_pooled_prefix.py',a.out,a.parent,a.hosted,a.controller_audit]),('two-moments-outer',[C/'assemble_candidate.py',a.out,a.parent,a.hosted,a.bit_result])]
for label,args in commands:
 with(a.out/(label+'.log')).open('w')as log:r=subprocess.run([sys.executable,'-B',*map(str,args)],stdout=log,stderr=subprocess.STDOUT)
 steps.append(dict(stage=label,observed_exit=r.returncode));(a.out/'OBSERVED-EXITS.json').write_text(json.dumps(steps,indent=2)+'\n');r.check_returncode()
read=lambda p:json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
raw=gzip.decompress((a.hosted/'GLOBAL-TEMPLATE.json.gz').read_bytes());t=json.loads(raw);h=read(a.hosted/'HOSTED.json');c=read(a.controller_audit);o=read(a.out/'OWNERS-AND-PROFILE.json');g=read(a.out/'GLOBAL-PREFIX.json');x=read(a.out/'EXACT-ASSEMBLY.json')
hash_=hashlib.sha256(raw).hexdigest();assert hash_==h['template_sha256']==c['complex_template_sha256']==g['template_sha256']==x['complex_template_sha256'];assert c['complex_profile']==h['global_profile']==o['paid_profile'];assert c['complex_live']==t['live']==o['live']
assert len(c['mutations_rejected'])>=18 and c['one_owner_per_complete_invocation'];assert all(sha(a.parent/n)==v for n,v in h['source_artifacts'].items())
report=dict(status='PASS_COMPLETE_POOLED_COMPLEX_FINITE_ADMISSION',complex_template_sha256=hash_,complex_profile=o['paid_profile'],complex_live=o['live'],physical=o['physical'],rank_mass=o['rank_mass'],deficit=o['deficit'],complex_hosted_residuals=o['hosted_residuals'],one_owner_per_complete_invocation=True,actual_73column_sigmas=o['actual_73column_sigmas'],cross_replica_helper_roles=o['cross_replica_helper_roles'],global_prefix_bits=g['global_prefix_bits'],retained_payload_bits=g['retained_payload_bits'],source_artifacts=h['source_artifacts'],controller_audit_sha256=sha(a.controller_audit),controller_mutations_rejected=c['mutations_rejected'],bit_result_sha256=sha(a.bit_result),complex_lower=x['complex_lower'],kappa=x['kappa'],kappa_decimal=x['kappa_decimal'],observed_stages=steps,files={str(p.name):sha(p)for p in a.out.glob('*.json')},scope='Exact finite program, complete-invocation normalization, whole physical owners, both scalar orientations, full paid profile, cross-replica-safe global prefix and strict arithmetic assembly. Retains inherited all-size compiler/precision/tape/common-grid and analytic-transfer contracts. PR484 source remains unchanged; independent audit by OpenAI Codex.')
(a.out/'ADMISSION.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status'],'kappa',report['kappa_decimal'],flush=True)

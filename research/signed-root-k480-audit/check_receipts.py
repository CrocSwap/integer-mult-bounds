"""Check frozen package and fresh replay receipt bindings (standard library).
This checks evidence integrity; it does not replace mathematical replay.
Prepared with substantial OpenAI Codex assistance. Apache-2.0.
"""
import gzip,hashlib,json
from fractions import Fraction
from pathlib import Path

P=Path(__file__).resolve().parent
package=P.parent/'signed-root-k480';fresh=P/'fresh'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_bytes())
def need(condition,message):
 if not condition:raise ValueError(message)

audit_manifest=read(P/'MANIFEST.json')
audit_actual={f.relative_to(P).as_posix():sha(f) for f in P.rglob('*') if f.is_file() and f != P/'MANIFEST.json' and '__pycache__' not in f.parts}
need(audit_actual==audit_manifest,'audit evidence manifest differs')
manifest=read(package/'MANIFEST.json')
actual={f.relative_to(package).as_posix():sha(f) for f in package.rglob('*') if f.is_file() and f.name!='MANIFEST.json' and '__pycache__' not in f.parts}
need(actual==manifest,'package manifest differs')
receipt=read(fresh/'RECEIPT.json');result=read(fresh/'RESULT.json');spec=read(package/'data/SPEC.json')
need(receipt['manifest_sha256']==sha(package/'MANIFEST.json'),'replay used another package manifest')
need(receipt['spec_sha256']==sha(package/'data/SPEC.json'),'replay used another spec')
need(result['reused']==dict(baseline=False,locals=[]),'replay reused a baseline or local')
need(Fraction(result['kappa_decimal'])==Fraction(spec['expected']['kappa_decimal']),'kappa mismatch')
need(result['global_profile']==spec['expected']['global_profile'],'global profile mismatch')
need(result['provider_counts']==spec['expected']['provider_counts'],'dispatch mismatch')
need(len(receipt['steps'])==64 and len({s['name'] for s in receipt['steps']})==64,'stage inventory')
for stage in receipt['steps']:
 need(stage['exit_code']==0,'failed stage '+stage['name'])
 need(sha(fresh/(stage['name']+'.log'))==stage['log_sha256'],'stage log differs '+stage['name'])
for name,value in receipt['artifacts'].items():need(sha(fresh/name)==value,'artifact differs '+name)
need(receipt['source_manifest_sha256']=={k:v['manifest_sha256'] for k,v in spec['build']['sources'].items()},'source pins differ')
controls=read(P/'SCHEDULE-CONTROLS.json')
need(controls['status']=='PASS_SIGNED_SCHEDULE_REPRODUCTION_AND_MUTATIONS' and len(controls['controls'])==16,'signed schedule controls')
suite=read(P/'REPOSITORY-CHECKS.json')
need(suite['exit_code']==0 and suite['gen4_bank_verify_included'] is True,'repository checks incomplete')
need(hashlib.sha256(gzip.decompress((P/'make-verify.log.gz').read_bytes())).hexdigest()==suite['log_sha256'],'repository check log differs')
print('PASS frozen package, 64 successful stage logs,',len(receipt['artifacts']),'replay artifacts, source pins, schedule controls and repository check log')

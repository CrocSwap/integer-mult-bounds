from pathlib import Path
import json,gzip,hashlib,copy,ast
from collections import Counter,defaultdict
P=Path('pr378-donor-screen');BASE=Path('pr378-complex-screen/compressed/work/complex-nine-native');sha=lambda b:hashlib.sha256(b).hexdigest()
raw=gzip.decompress((P/'signed25-bound-template.json.gz').read_bytes());t=json.loads(raw);assert sha(raw)==json.load(open(P/'signed25-integration.json'))['template_sha256']
phasebytes=(BASE/'DATA-PHASES.json').read_bytes();phase=json.loads(phasebytes);rraw=gzip.decompress((P/'prefix-gauge-routes.json.gz').read_bytes());routes=json.loads(rraw);c=json.load(gzip.open(P/'signed25-donor-candidate.json.gz'));ext=dict(c['ext']);h=c['h'];m=t['m'];v=c['v'];n=2*v+c['R'];basis=json.load(open(P/'best-bank-geometry.json'))['orthonormal_complement'];I=[[int(i==j) for j in range(8)] for i in range(8)]
# Extract unchanged independent audit functions; never run the old producer.
src=ast.parse((P/'audit_complete_schedule.py').read_text());funcs=[x for x in src.body if isinstance(x,ast.FunctionDef)];exec(compile(ast.Module(body=funcs,type_ignores=[]),'source_bound_independent_audit','exec'))
schedule(t);owners(routes,t);controls=[]
for name,fn in [('idle_omission',lambda a:a['execution_schedule'].pop(next(i for i,e in enumerate(a['execution_schedule']) if e['kind']=='idle_cover_sweep'))),('phase_omission',lambda a:a['execution_schedule'][0].pop('entry_exit_phase_adapters')),('wrong_owner',lambda a:a['calls'][0]['owners'][240].__setitem__(0,0)),('padding_omission',lambda a:a['bank_padding'].pop())]:
 bad=copy.deepcopy(t);fn(bad)
 try:schedule(bad);owners(routes,bad)
 except (KeyError,AssertionError):controls.append(name)
 else:raise AssertionError('accepted '+name)
s=(P/'check_ambient_phase.py').read_text().replace('prefix-gauge-bound-template.json.gz','signed25-bound-template.json.gz').replace("read_text()", "read_text()")
s=s.replace("json.load(open(P/'bound-schedule-audit.json'))['template_sha256']", "json.load(open(P/'signed25-integration.json'))['template_sha256']").replace('prefix-donor-candidate.json.gz','signed25-donor-candidate.json.gz').replace('ambient-phase-audit.json','signed25-ambient-phase-audit.json')
exec(compile(s,'fresh_signed25_ambient','exec'),{})
out=dict(status='PASS_FRESH_SIGNED25_SCHEDULE_OWNER_AND_AMBIENT_AUDIT',template_sha256=sha(raw),structural_controls=controls,route_count=len(routes),scope='Fresh full schedule, owner inverse and Z4 residual checks on new signed25 emission; inherited recursive-child and compiler semantics remain conditional.')
(P/'signed25-global-audit.json').write_text(json.dumps(out,indent=2));print(json.dumps(out))

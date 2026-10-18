from pathlib import Path
import json,hashlib,subprocess,shutil
P=Path('/tmp/pr-efficient1800');R=Path('/tmp/integer-mult-efficient1100-20261015');D=P/'combined-1926';pkg='research/unittest-receipt-comparison';H=D/pkg;A=R/'research/community-efficient1800-audit';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
pk=json.loads((P/'packets/1926.json').read_text());c=json.loads((P/'check-1926-migrated.json').read_text());assert c['status']=='passed' and not c['changed_files_after'] and len(c['commands'])==3
live=json.loads((P/'live-1926-review.json').read_text());assert live['headRefOid']==pk['head'] and live['state']=='OPEN' and not live['isDraft']
originals={Path(x['path']).name:x for x in pk['files']};retained=[]
for name,row in originals.items():
 f=H/('historical' if name in ['README.md','SOURCES.json','VERIFY.json'] else '')/name
 raw=subprocess.check_output(['git','cat-file','blob',row['source']['oid']],cwd=R);assert f.read_bytes()==raw;retained.append(dict(original_path=row['path'],retained_path=f.relative_to(D).as_posix(),sha256=sha(f),original_oid=row['source']['oid']))
for f in H.rglob('*'):
 if f.is_file():assert c['input_sha256'][f.relative_to(D).as_posix()]==sha(f)
finding=dict(status='passed',number=1926,head=pk['head'],original_files=retained,scope='Arham Tahir byte-preserving stderr comparator and opt-in historical benchmark adapter; no full repository benchmark, performance claim, production-runner replacement or mathematical bound.',review=['Raw versus summary tags plus encoded prefix length preserve injectivity of every retained diagnostic byte; only recognized final elapsed value is omitted.','All20 original byte/real-capture/end-to-end controls and complete deterministic receipt pass normally and with optimized parent.','Exact historical runner remains declared executable input, now mapped from PR2859 archive; no input demotion or invented historical digest.','Private replay authenticates all10 original package files and three predecessor inputs before copying; requires exact completion marker and unchanged complete snapshot.','New controls reject all13 original/runtime byte mutations, absent input, nonzero child, silent zero exit, terminal-marker bypass and post-execution mutation.','Registered metadata passes current validator and Git-source provenance checks.'],limits=['Full-suite adapter remains restricted to exact historical checkout; this does not establish compatibility with the live runner.','Syntactic output comparison does not prove the producer ran honest tests; source-bound test execution and completion guards are separate.'],credit='Arham Tahir / Arham-Tahir64 with OpenAI Codex assistance; Aaron Wang/navinor predecessor retained; context migration Douglas Colkitt/Codex using Dennis/antunishdPursuit PR2859 snapshot.')
(P/'finding-1926-migration-complete.json').write_text(json.dumps(finding,indent=2)+'\n')
if (P/'check-1926.json').exists():
 for ext in ['json','log']:
  f=P/f'check-1926.{ext}'
  if f.exists():f.rename(P/f'check-1926-before-migration.{ext}')
c['scope']='Completed PR1926 migration; full current registered replay including immutable original20-test receipts and four new context guard tests. '+c['scope'];(P/'check-1926.json').write_text(json.dumps(c,indent=2)+'\n');shutil.copy2(P/'check-1926-migrated.log',P/'check-1926.log')
plan=json.loads((P/'resolution-plan.json').read_text());assert not any(x['number']==1926 for x in plan)
for f in H.rglob('*'):
 if not f.is_file():continue
 rel=f.relative_to(D).as_posix();name=f.name;row=next((x for x in pk['files'] if x['path']==rel),None)
 original=subprocess.check_output(['git','cat-file','blob',row['source']['oid']],cwd=R) if row else b''
 if original==f.read_bytes():continue
 out=P/'resolutions/1926'/rel;out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(f,out)
 if row:
  old=P/'prior-revisions/1926-original'/rel;old.parent.mkdir(parents=True,exist_ok=True);old.write_bytes(original)
 plan.append(dict(number=1926,path=rel,original_sha256=hashlib.sha256(original).hexdigest(),resolved_sha256=sha(f),resolved_mode='100644',reason='Preserve original comparator/tests/RESULT and archived metadata; route registered checks through exact original runner context from PR2859 with byte, completion and immutability controls. Current runner untouched.'))
(P/'resolution-plan.json').write_text(json.dumps(plan,indent=2)+'\n')
holds=json.loads((P/'extra-holds.json').read_text());holds.pop('1926',None);(P/'extra-holds.json').write_text(json.dumps(holds,indent=2)+'\n')
f=P/'scopes.txt';lines=[l for l in f.read_text().splitlines() if not l.startswith('1926|')];lines.append('1926|Arham Tahir\'s byte-preserving unittest stderr comparator retains all diagnostics except the recognized final elapsed value. Both exact legacy collisions, complete original20-test receipts and real-capture/fault controls pass normal/optimized. Registered replay now uses exact archived runner in an authenticated private context; all original10files retained, four added context guards pass. No full-suite benchmark, current-runner compatibility, speedup or kappa claim. Aaron Wang/navinor predecessor credit retained.');f.write_text('\n'.join(lines)+'\n')
for name in ['prepare_1926_migration.py','write_1926_migration.py','run_1926_migrated.py','register_1926.py']:shutil.copy2(P/name,A/name)
print('Registered complete PR1926 with',sum(x['number']==1926 for x in plan),'explicit migration resolutions')

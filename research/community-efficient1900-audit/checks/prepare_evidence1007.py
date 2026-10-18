from pathlib import Path
import json,subprocess,shutil,base64,hashlib
P=Path('/tmp/pr-efficient1900');R=Path('/tmp/integer-mult-efficient1100-20261015');D=P/'combined-1007';D.mkdir(exist_ok=True)
def git(*a):return subprocess.check_output(['git',*a],cwd=R)
ledger=json.loads((R/'docs/research/pr-ledger.json').read_text())
paths=set(ledger['source_sha256'])|{'research/pr-reconciliation-20261012/starting-snapshot.json','scripts/reconcile_pr_queue.py','docs/research/pr-ledger.json','docs/research/pr-ledger.md'}
paths.update(p.relative_to(R).as_posix() for p in (R/'docs/research').glob('*.md'))
for rel in sorted(paths):
 f=D/rel;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes((R/rel).read_bytes() if (R/rel).exists() else git('show','HEAD:'+rel))
meta=json.loads((P/'packets/1007.json').read_text());head=meta['head']
for item in meta['files']:
 rel=item['path']
 if rel.startswith('research/') or rel.startswith('tests/'):
  f=D/rel;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(git('show',head+':'+rel))
patch=git('diff',meta['merge_base'],head,'--','scripts/reconcile_pr_queue.py')
subprocess.run(['git','apply','-'],input=patch,cwd=D,check=True)
cert=json.loads((D/'research/pr116-evidence-reconciliation/CERTIFICATE.json').read_text())
for oid,obj in cert['objects'].items():
 raw=git('cat-file',obj['type'],oid);assert raw==base64.b64decode(obj['base64']),oid
(P/'provenance-1007-objects.json').write_text(json.dumps({'head':head,'objects':len(cert['objects']),'status':'all_embedded_raw_objects_match_local_git_database','commits':cert['commits'],'baseline':git('rev-parse','HEAD').decode().strip()},indent=2)+'\n')
(P/'before-1007-ledger.json').write_bytes((R/'docs/research/pr-ledger.json').read_bytes())
print('Prepared',len(paths),'current inputs; authenticated',len(cert['objects']),'Git objects')

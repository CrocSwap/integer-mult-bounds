from pathlib import Path
import json,subprocess,tarfile,hashlib,shutil
P=Path('/tmp/pr-efficient1800');R=Path('/tmp/integer-mult-efficient1100-20261015');D=P/'combined-1076';assert not D.exists();D.mkdir()
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip()
def blob(rel,rev=head):return subprocess.check_output(['git','show',rev+':'+rel],cwd=R)
manifest=json.loads(blob('research/quadratic-affine-packed/SOURCES.json'))
paths=set(manifest['files'])|{'tests/test_quadratic_affine.py'}
paths.update(subprocess.check_output(['git','ls-tree','-r','--name-only',head,'research/quadratic-affine-packed'],cwd=R,text=True).splitlines())
for rel in paths:
 f=D/rel;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(blob(rel))
for f in json.loads((P/'packets/1076.json').read_text())['files']:
 rel=f['path'];dst=D/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(P/'sources/1076'/rel,dst)
subprocess.run(['git','init','-q',str(D)],check=True);obj=(R/subprocess.check_output(['git','rev-parse','--git-path','objects'],cwd=R,text=True).strip()).resolve();(D/'.git/objects/info/alternates').write_text(str(obj)+'\n');(D/'.git/HEAD').write_text(head+'\n')
sha=lambda b:hashlib.sha256(b).hexdigest()
config=dict(base_commit=manifest['base_commit'],manifest_sha256=sha(blob('research/quadratic-affine-packed/SOURCES.json')),accepted_live={},package_files={},scope='Authenticate unchanged PR752 manifest/code; restore exact historical dependencies in a temporary tree. Does not re-pin the predecessor or test new production code through a historical oracle.')
for rel,pin in manifest['files'].items():
 data=(D/rel).read_bytes()
 if sha(data)!=pin:
  old=blob(rel,manifest['base_commit']);assert sha(old)==pin
  config['accepted_live'][rel]=[sha(data)]
for rel in sorted(paths-set(manifest['files'])):config['package_files'][rel]=sha((D/rel).read_bytes())
(D/'research/quadratic-affine-performance/HISTORICAL-PACKED.json').write_text(json.dumps(config,indent=2)+'\n')
# Complete baseline identity, rather than merely trust an attribution comment.
base='2921874911956718fcaaaf9396fe8267b3cfa9f0';old=blob('scripts/experiments/quadratic_affine.py',base).decode();new=(D/'scripts/experiments/quadratic_affine.py').read_text()
assert old[:old.index('def rank_witness(')]==new[:new.index('def _character_masks(')]
assert blob('certificates/quadratic-affine-vectors.json',base)==(D/'research/quadratic-affine-performance/evidence/base-certificate.json').read_bytes()
for rel in ['scripts/audit_quadratic_affine.py','scripts/experiments/quadratic_affine_witnesses.json','docs/research/quadratic-affine-vectors.md']:
 assert blob(rel)==(P/'sources/1076'/rel).read_bytes(),rel
# README after-run details and additional command; preserve author measurements.
f=D/'research/quadratic-affine-performance/README.md';f.write_text(f.read_text()+'''\n## Maintainer integration and historical replay\n\nAll 14,662 rows and the complete certificate were independently replayed on\nPython 3.12. The author's recorded timing remains a historical measurement.\nThe maintainer supplement exercises a real omitted gather stage, beyond the\noriginal synthetic row-corruption control.\n\nCurtis Dransfield's earlier PR752 package retains its original code and pins.\nIts direct command already rejected several changed helpers on current main;\nthe production replacement also changes its pinned quadratic helper and\ncertificate. Run the exact original package through:\n\n```sh\npython3 -B research/quadratic-affine-performance/historical_packed.py\n```\n\nThis authenticates the old manifest, package code, and allowed live successor\nhashes, retrieves matching historical Git blobs, and executes the unchanged\nfull predecessor verification in a temporary tree. It checks the terminal\nsuccess marker and input immutability. Full repository Git history is required.\nIt is explicitly a historical replay; the new production engine is checked\nseparately by this package's complete benchmark. No frozen pins are weakened.\n''')
print('Prepared',len(paths),'inputs;',len(config['accepted_live']),'historicalreplacements')

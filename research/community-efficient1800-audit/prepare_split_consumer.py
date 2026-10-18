from pathlib import Path
import json,hashlib,subprocess,shutil
P=Path('/tmp/pr-efficient1800');R=Path('/tmp/integer-mult-efficient1100-20261015');D=P/'shared-frame-consumers';E=P/'split-frame-consumer'
assert not E.exists();E.mkdir()
def blob(path):return subprocess.check_output(['git','show','HEAD:'+path],cwd=R)
def put(path):
 p=E/path
 if not p.exists():p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(blob(path))
for name in ['scripts','tests']:shutil.copytree(D/name,E/name)
for pkg in ['research/split-skip','research/skip-strips','research/skip-clones']:
 for path in subprocess.check_output(['git','ls-tree','-r','--name-only','HEAD','--',pkg],cwd=R,text=True).splitlines():put(path)
for pkg in ['research/split-skip','research/skip-strips','research/skip-clones']:
 for path in json.loads((E/pkg/'SOURCE.json').read_bytes())['files']:put(path)
for path in ['research/exclusion-embedding-masks/baseline.py','research/shared-point-digest/baseline.py','research/joint-frames-cleared-product/baseline.py']:
 t=E/path;t.parent.mkdir(parents=True,exist_ok=True)
 if (D/path).exists():shutil.copy2(D/path,t)
 else:t.write_bytes(blob(path))
f=E/'scripts/replay_historical_check.py';s=f.read_text();needle="\n\n\ndef require(condition, message):";assert s.count(needle)==1
s=s.replace(needle,"""
# Candidate PR1922 joint product successor: retain exact historical executable
# bytes rather than rewriting the frozen split-skip manifest.
CONFIG['split-skip']['additional_inputs'].append({
    'manifest': 'research/split-skip/SOURCE.json', 'field': 'files',
    'path': 'scripts/audit_joint_frames.py', 'input_from_root': True,
    'input': 'research/joint-frames-cleared-product/baseline.py',
    'sha256': '3df8061392ce0ba42bbde8c02f2a30c8141145e70e9a48c18da73d3aafb14423',
    'accepted_live_sha256': [
        'c20c3ab068e7e0ad0090dd4298594766feab220f1e2c6cb333ae1ac32e17207e',
    ],
})
"""+needle);f.write_text(s)
# Minimal tracked fixture is required by the actual historical-copy entrypoint.
subprocess.run(['git','init','-q'],cwd=E,check=True);subprocess.run(['git','add','.'],cwd=E,check=True)
# This is a prepared candidate, not a successful replay receipt.
(P/'provenance-split-consumer.json').write_text(json.dumps(dict(status='prepared_not_verified',baseline=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),fixture=str(E),helper_sha256=hashlib.sha256((E/'scripts/audit_joint_frames.py').read_bytes()).hexdigest(),scope='Only explicit fourth historical dependency added; original split-skip and skip-strips sources and pins unchanged.'),indent=2)+'\n')
print('Prepared',E)

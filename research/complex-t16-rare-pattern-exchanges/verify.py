"""Replay frozen owner exchanges through the unchanged PR1087 strict verifier. Python 3.12+."""
import argparse,hashlib,json,tarfile,subprocess,sys,shutil,os
from pathlib import Path
assert __debug__, 'Assertions required'
P=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ap=argparse.ArgumentParser();ap.add_argument('--main',type=Path,required=True);ap.add_argument('--local',type=Path,required=True);ap.add_argument('--work',type=Path,required=True);a=ap.parse_args()
manifest=json.loads((P/'MANIFEST.json').read_text())
actual={str(f.relative_to(P)):sha(f) for f in P.rglob('*') if f.is_file() and f!=P/'MANIFEST.json' and '__pycache__' not in f.parts}
assert actual==manifest, 'Submission file inventory or hash changed'
work=a.work.resolve();assert not work.exists(), 'Use a fresh output directory';work.mkdir(parents=True)
source=work/'source';source.mkdir()
with tarfile.open(P/'upstream1087.tar.gz') as t:
 for m in t.getmembers():assert m.isfile() and (source/m.name).resolve().is_relative_to(source), 'Unsafe archive member'
 t.extractall(source,filter='data')
pins=json.loads((source/'MANIFEST.json').read_text());assert sha(source/'MANIFEST.json')==json.loads((P/'SOURCE.json').read_text())['manifest_sha256']
assert {str(f.relative_to(source)):sha(f) for f in source.rglob('*') if f.is_file() and f!=source/'MANIFEST.json'}==pins, 'Upstream archive mismatch'
for name in ('OWNERS.json.gz','PLAN.json','SPEC.json'):shutil.copyfile(P/'data'/name,source/'data'/name)
env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1')
subprocess.run([sys.executable,'-B',str(source/'verify_t16.py'),'--main',str(a.main.resolve()),'--local',str(a.local.resolve()),'--work',str(work/'strict')],env=env,check=True)
r=json.loads((work/'strict/REPLAY.json').read_text());expected=json.loads((P/'CANDIDATE.json').read_text())
assert r['status']=='PASS_GAUGE44_T16_STRICT_GLOBAL_REPLAY'
assert r['kappa_decimal']==expected['kappa']
assert r['complex_profile']==json.loads((P/'PROFILE.json').read_text())
print('PASS_T16_RARE_PATTERN_EXCHANGES',r['kappa_decimal'])

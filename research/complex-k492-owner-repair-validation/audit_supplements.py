from pathlib import Path
import tempfile,shutil,json,subprocess,gzip,hashlib
import argparse
ap=argparse.ArgumentParser();ap.add_argument('--work',type=Path,required=True);args=ap.parse_args()
O=Path(__file__).resolve().parent;P=O.parent/'complex-k492-owner-repair';native=args.work.resolve();records=[]
def dump(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
with tempfile.TemporaryDirectory(prefix='k492-supplement-controls-') as td:
 T=Path(td)/'package';T.mkdir()
 for d in ('data','comparison','extras'):shutil.copytree(P/d,T/d)
 def reset():
  for p in (P/'data').glob('*'):
   if p.is_file():shutil.copy2(p,T/'data'/p.name)
 def run(tool,case,reason=None):
  args=[__import__('sys').executable,'-I','-O','-B',str(T/'extras'/tool)]
  if tool=='check_owner_map.py':args+=['--work',str(native),'--out',str(Path(td)/'check.json')]
  r=subprocess.run(args,capture_output=True,text=True)
  if reason is None:
   if r.returncode:raise ValueError(r.stderr)
  elif not r.returncode or reason not in r.stderr:raise ValueError((case,r.returncode,r.stderr))
  records.append(dict(case=case,exit_code=r.returncode,expected=reason or 'PASS'))
 run('check_declarations.py','declarations-positive');run('check_owner_map.py','map-positive')
 for case in ('global','provider','shadow','dispatch'):
  reset();s=json.loads((T/'data/SPEC.json').read_bytes())
  if case=='global':s['expected']['global_profile']['1']+=1;reason='global outputs'
  elif case=='provider':s['providers']['jp8']['artifacts.canonical_sha256']='0'*64;reason='provider outputs'
  elif case=='shadow':s['build']['shadows'].pop(next(iter(s['build']['shadows'])));reason='complete typed build'
  else:s['dispatch'][0]=s['dispatch'][1];reason='same complete dispatch'
  dump(T/'data/SPEC.json',s);run('check_declarations.py',case,reason)
 for case in ('width','family','call','footprint'):
  reset();s=json.loads((T/'data/SPEC.json').read_bytes());roles=json.loads(gzip.decompress((T/'data/OWNERS.json.gz').read_bytes()))
  if case=='width':roles[0]['width']+=1;reason='actual width'
  elif case=='family':roles[0]['family']+=1;reason='physical family'
  elif case=='call':roles[0]['stage']+=1;reason='ordered complete call'
  else:roles[0]['offset']=1000000;reason='window and footprint'
  p=T/'data/OWNERS.json.gz';p.write_bytes(gzip.compress(json.dumps(roles).encode(),mtime=0));s['data']['owners_sha256']=hashlib.sha256(p.read_bytes()).hexdigest();dump(T/'data/SPEC.json',s);run('check_owner_map.py',case,reason)
dump(O/'SUPPLEMENT-CONTROLS.json',dict(status='PASS',interpreter_flags=['-I','-O','-B'],positive_controls=2,rejections=8,records=records));print('PASS 2 positive controls and 8 explicit rejections under -I -O')

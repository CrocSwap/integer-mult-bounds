from pathlib import Path
import json,gzip,copy,tempfile,importlib.util,time,argparse
P=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('audit',P/'local/hpe_audit_and_transport.py');A=importlib.util.module_from_spec(s);s.loader.exec_module(A)
ap=argparse.ArgumentParser();ap.add_argument('--word',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
w=json.loads(gzip.decompress(a.word.read_bytes()));recipe=json.loads((P/'data/FRAME-RECIPE.json').read_text());routing=P/'vendor/main/research/complex-k492-owner-repair/vendor/multicold/vendor/pr558/vendor/pr552/complex-local/inputs/phase-baseline/CANONICAL-WORD.json.gz'
def trial(z):
 with tempfile.TemporaryDirectory()as td:
  d=Path(td);f=d/'word.json.gz';f.write_bytes(gzip.compress(json.dumps(z).encode(),mtime=0))
  try:A.run(f,routing,d/'native');return None
  except AssertionError as e:return str(e)
start=time.monotonic();assert trial(w)is None;records=[]
for section,i,old,new in recipe['gate_frames']:
 z=copy.deepcopy(w);z[section][i][-1]=[];error=trial(z);assert error and 'nonmonotone' in error,(i,error);records.append(dict(name='frame-'+str(i)+'-emptied',rejected=error))
z=copy.deepcopy(w);i=recipe['gate_frames'][0][1];z['B'][i][3]*=2;error=trial(z);assert error and 'arbitrary-dirt endpoint'in error,error;records.append(dict(name='changed-read-coefficient',rejected=error))
z=copy.deepcopy(w);z['report']['local_profile']['1']+=1;error=trial(z);assert error and 'paid local profile differs'in error,error;records.append(dict(name='paid-profile-tampering',rejected=error))
a.out.write_text(json.dumps(dict(status='PASS_FOCUSED_EIGHT_FRAME_NATIVE_CONTROLS',positive=1,rejected=records,seconds=time.monotonic()-start),indent=2)+'\n');print('PASS',len(records),'mutations',flush=True)

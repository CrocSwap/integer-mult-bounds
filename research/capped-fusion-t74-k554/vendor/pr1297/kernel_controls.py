"""Perturb each new donor, cancellation and restoration; reject with the retained full rational auditor."""
import argparse,copy,gzip,json,subprocess,sys,tempfile,hashlib
from pathlib import Path
P=Path(__file__).resolve().parent
ap=argparse.ArgumentParser();ap.add_argument('--word',type=Path,required=True);ap.add_argument('--main',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();w0=json.loads(gzip.decompress(a.word.read_bytes()));aud=a.main/'research/gauge44-slots/independent/audit_local.py'
def locate(seq,gate):
 ids=[i for i,g in enumerate(seq) if g[:5]==gate[:5]];assert len(ids)==1,(gate,ids);return ids[0]
def check(w,d):
 p=d/'word.json.gz';p.write_bytes(gzip.compress(json.dumps(w,separators=(',',':')).encode(),mtime=0));r=subprocess.run([sys.executable,'-B',str(aud),'--word',str(p),'--main',str(a.main),'--output',str(d/'audit.json')],capture_output=True,text=True);return r.returncode,r.stdout+r.stderr
mutants={}
for c in json.loads((P/'COMPOSITION.json').read_text())['chosen']:
 q=c['pivot'];ed=c['ed'];gates=[g for i,g in ed['insert']];assert len(gates)==3
 for name,gate in zip(['donor','undo','partner'],gates):
  i=locate(w0['B'],gate);w=copy.deepcopy(w0);del w['B'][i];mutants[f'drop_{name}@{q}']=w
 w=copy.deepcopy(w0);i=locate(w['B'],gates[0]);w['B'][i][3]*=-1;mutants[f'flip_donor_sign@{q}']=w
 ci=locate(w0['cleanup'],ed['tail'][0][1]);assert sum(i==ci for i,U in w0['early_cleanup'])==1
 w=copy.deepcopy(w0);del w['cleanup'][ci];w['early_cleanup']=[[i-int(i>ci),U] for i,U in w['early_cleanup'] if i!=ci];mutants[f'drop_restore@{q}']=w
 w=copy.deepcopy(w0);w['cleanup'][ci][3]*=-1;mutants[f'flip_restore_sign@{q}']=w
with tempfile.TemporaryDirectory(dir=a.out.parent,prefix='kernel-controls-') as tmp:
 d=Path(tmp);rc,msg=check(w0,d);assert rc==0,('honest',msg[-2000:]);rejected=[]
 for name,w in mutants.items():
  rc,msg=check(w,d);assert rc!=0 and ('endpoint' in msg or 'entrance response' in msg),(name,rc,msg[-2000:]);rejected.append(dict(name=name,reason=msg.strip().splitlines()[-1]));print('REJECTED',name,flush=True)
a.out.write_text(json.dumps(dict(status='PASS_NEW_COLD_KERNEL_MUTATION_CONTROLS',word_sha256=hashlib.sha256(a.word.read_bytes()).hexdigest(),honest='PASS',rejected=rejected),indent=2)+'\n')

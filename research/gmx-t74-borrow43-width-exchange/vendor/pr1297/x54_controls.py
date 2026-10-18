"""Four direct X54 failure controls on each final refitted word, using the unchanged local auditor."""
import argparse,copy,gzip,hashlib,json,subprocess,sys,tempfile
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('--word',type=Path,required=True);ap.add_argument('--recipe',type=Path,required=True);ap.add_argument('--main',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();w0=json.loads(gzip.decompress(a.word.read_bytes()));rc=json.loads(a.recipe.read_text());audit=a.main/'research/gauge44-slots/independent/audit_local.py'
def locate(section,gate):
 ids=[i for i,g in enumerate(section) if g[:-1]==gate[:-1]];assert len(ids)==1,(gate,ids);return ids[0]
def check(w,d):
 p=d/'WORD.json.gz';p.write_bytes(gzip.compress(json.dumps(w,separators=(',',':')).encode(),mtime=0));r=subprocess.run([sys.executable,'-B',str(audit),'--word',str(p),'--main',str(a.main),'--output',str(d/'AUDIT.json')],capture_output=True,text=True);return r.returncode,(r.stdout+r.stderr)
with tempfile.TemporaryDirectory(dir=a.out.parent,prefix='x54-controls-') as tmp:
 d=Path(tmp);code,msg=check(w0,d);assert code==0,('honest',msg[-1000:]);mutants={}
 w=copy.deepcopy(w0)
 for gate in rc['cleanup_prepend']:
  ci=locate(w['cleanup'],gate);assert all(i!=ci for i,U in w['early_cleanup']);del w['cleanup'][ci];w['early_cleanup']=[[i-int(i>ci),U] for i,U in w['early_cleanup']]
 mutants['drop_full_restore']=(w,'all-column endpoint failure')
 w=copy.deepcopy(w0)
 for pos,gate in rc['tail_insert']:
  ci=locate(w['cleanup'],gate);assert sum(i==ci for i,U in w['early_cleanup'])==1;w['early_cleanup']=[[i,U] for i,U in w['early_cleanup'] if i!=ci];w['cleanup'][ci][-1]=[1<<i for i in range(8,-1,-1)]
 mutants['move_early_restore_to_full']=(w,'all-column endpoint failure')
 w=copy.deepcopy(w0);donations=[(i,g) for i,g in rc['B_insert'] if not 112<=g[1]<224];first=min(i for i,g in donations)
 prereads=[g for i,g in rc['B_insert'] if i<first and 112<=g[1]<224];assert prereads
 for gate in prereads:del w['B'][locate(w['B'],gate)]
 mutants['drop_entrance_preread']=(w,'nonzero entrance response')
 w=copy.deepcopy(w0)
 for pos,gate in donations:
  di=locate(w['B'],gate);g=w['B'].pop(di);ri=next(i for i,e in enumerate(w['B']) if i>=di and e[0]=='add' and 112<=e[1]<224 and e[2]==g[1]);w['B'].insert(ri+1,g)
 mutants['move_donation_after_read']=(w,'nonzero entrance response');rejected=[]
 for name,(word,expected) in mutants.items():
  code,msg=check(word,d);assert code!=0 and expected in msg,(name,code,msg[-1200:]);rejected.append(dict(name=name,reason=msg.strip().splitlines()[-1]));print('REJECTED',name,flush=True)
a.out.write_text(json.dumps(dict(status='PASS_FINAL_WORD_X54_CONTROLS',honest='PASS',word_sha256=hashlib.sha256(a.word.read_bytes()).hexdigest(),rejected=rejected),indent=2)+'\n')

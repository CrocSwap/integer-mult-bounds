"""Independent changed-stock local replay, fresh target mixing and retiming for candidate201."""
from pathlib import Path
import os,sys,json,gzip,subprocess,hashlib
r=Path.cwd();out=r/'r714-precursor-check';assert not out.exists();out.mkdir();os.environ['E8COORD']='ham'
sys.path[:0]=[str(r/'source454-review/e8-r740-replica32/code'),str(r/'source463-review/code/rekid'),str(r/'source454-review/e8-r740-replica32/parent436/code/reuse')]
import e8core as E,retime as RT
src=r/'r715-hierarchy-rewrite-screen/candidate-201/WORD.json.gz';w=E.load_word(str(src));steps=[]
def check(word,name):
 a=E.replay(word,span_mode='z');assert not a['viol'],a['viol'][:5]
 result=dict(status='PASS_EXACT_CHANGED_STOCK_LOCAL',columns=a['n'],helpers=word['R'],profile=dict(a['H']),word_sha256=hashlib.sha256(json.dumps(word,sort_keys=True,separators=(',',':')).encode()).hexdigest());(out/(name+'.json')).write_text(json.dumps(result,indent=2)+'\n');steps.append(name);print(name,result,flush=True)
try:
 check(w,'RAW-LOCAL')
 with (out/'mixing.log').open('w') as f:subprocess.run([sys.executable,'-B',str(r/'source463-review/code/rekid/mix_target_nochain.py'),str(src),str(out/'MIXED.json')],stdout=f,stderr=subprocess.STDOUT,check=True)
 w=json.loads((out/'MIXED.json').read_text());check(w,'MIXED-LOCAL');w,moves=RT.retime(w,sweeps=6,M=78);check(w,'RETIMED-LOCAL')
 (out/'PRECURSOR.json.gz').write_bytes(gzip.compress(json.dumps(w,sort_keys=True,separators=(',',':')).encode(),mtime=0));(out/'RECEIPT.json').write_text(json.dumps(dict(status='PASS_R714_RAW_MIXED_RETIMED_LOCAL_ONLY',steps=steps,moves=moves,scope='954 arbitrary dirty F2 columns, rational frames and integer operand support. Native, physical hosting and final supplier remain pending.'),indent=2)+'\n')
except BaseException as e:
 (out/'FAILURE.json').write_text(json.dumps(dict(error=repr(e),steps=steps),indent=2)+'\n');raise

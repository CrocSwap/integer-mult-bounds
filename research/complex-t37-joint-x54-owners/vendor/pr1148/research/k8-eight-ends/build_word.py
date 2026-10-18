"""Apply a frozen frame/end recipe without changing scalar gates. Apache-2.0."""
import argparse,gzip,json,hashlib
from pathlib import Path
P=Path(__file__).resolve().parent

def build(source, output):
 recipe=json.loads((P/'RECIPE.json').read_text());raw=gzip.decompress(source.read_bytes())
 assert hashlib.sha256(raw).hexdigest()==recipe['input_content_sha256'],'baseline word pin'
 w=json.loads(raw)
 for sec in ['A','B','early_cleanup']:
  for i,old,new in recipe[sec]:
   assert w[sec][i][-1]==old,('original annotation',sec,i)
   w[sec][i][-1]=new
 for q,old,new in recipe['ends']:
  assert w['helper_final'][str(q)]==old
  w['helper_final'][str(q)]=new
 for key,value in recipe['report'].items():w['report'][key]=value
 raw=json.dumps(w,sort_keys=True,separators=(',',':')).encode()
 assert hashlib.sha256(raw).hexdigest()==recipe['output_content_sha256'],'new word pin'
 output.parent.mkdir(parents=True,exist_ok=True);output.write_bytes(gzip.compress(raw,mtime=0))
 return w
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--base',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();build(a.base,a.out);print('PASS_PINNED_EIGHT_END_CONSTRUCTION')

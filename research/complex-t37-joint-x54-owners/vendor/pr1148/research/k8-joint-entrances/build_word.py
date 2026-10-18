"""Apply the frozen local-interface recipe; no optimization."""
import argparse,gzip,hashlib,json
from pathlib import Path
P=Path(__file__).resolve().parent
def main():
 assert __debug__
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();assert not a.out.exists()
 raw=gzip.decompress((P.parent/'k8-eight-ends/FULL-WORD.json.gz').read_bytes());r=json.loads((P/'RECIPE.json').read_text());assert hashlib.sha256(raw).hexdigest()==r['input_content_sha256'];w=json.loads(raw)
 for h,old,new in r['start_extra']:assert w['start_extra'][h]==old;w['start_extra'][h]=new
 for sec in ['A','B']:
  for i,old,new in r[sec]:assert w[sec][i][-1]==old;w[sec][i][-1]=new
 for i,old,new in r['early_cleanup']:assert w['early_cleanup'][i][1]==old;w['early_cleanup'][i][1]=new
 w['report']=r['report'];raw=json.dumps(w,sort_keys=True,separators=(',',':')).encode();assert hashlib.sha256(raw).hexdigest()==r['output_content_sha256'];a.out.write_bytes(gzip.compress(raw,mtime=0));print('PASS_JOINT_ENTRANCES_FROZEN_RECIPE')
if __name__=='__main__':main()

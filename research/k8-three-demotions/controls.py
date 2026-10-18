"""Semantic rejection controls for the changed local interfaces."""
import argparse,contextlib,copy,gzip,importlib.util,io,json,tempfile
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parents[1]
def main():
 assert __debug__
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();assert not a.out.exists()
 spec=importlib.util.spec_from_file_location('audit',ROOT/'research/gauge44-slots/independent/audit_local.py');A=importlib.util.module_from_spec(spec);spec.loader.exec_module(A)
 word=json.loads(gzip.decompress((P/'FULL-WORD.json.gz').read_bytes()));recipe=json.loads((P/'RECIPE.json').read_text());rejected=[]
 with tempfile.TemporaryDirectory(prefix='k8-demotion-controls-') as d:
  d=Path(d)
  def check(label,w):
   f=d/'mutant.json.gz';f.write_bytes(gzip.compress(json.dumps(w).encode(),mtime=0))
   try:
    with contextlib.redirect_stdout(io.StringIO()):A.run(f,d/'audit.json',ROOT)
   except RuntimeError as e:rejected.append(dict(control=label,reason=str(e)));return
   raise AssertionError('control admitted: '+label)
  for h,old,new in recipe['start_extra']:
   w=copy.deepcopy(word);w['start_extra'][h]=old;check('restore-promoted-start-'+h,w)
   w=copy.deepcopy(word);gate=next(e for e in w['A']+w['B'] if int(h) in A.registers(e));gate[-1]=gate[-1][:-1];check('first-frame-too-small-'+h,w)
  w=copy.deepcopy(word);w['report']['local_profile']['1']+=1;check('false-paid-profile',w)
  w=copy.deepcopy(word);w['B'][next(i for i,e in enumerate(w['B']) if e[0]=='add' and 112<=e[1]<224)][3]+=1;check('wrong-target-coefficient',w)
  w=copy.deepcopy(word);w['report']['width_inventory']['4']+=1;check('false-helper-inventory',w)
 assert len(rejected)==27
 a.out.write_text(json.dumps(dict(status='PASS_THREE_DEMOTION_SEMANTIC_CONTROLS',rejected=rejected),indent=2)+'\n');print('PASS',len(rejected),'demotion controls')
if __name__=='__main__':main()

"""Apply eight pinned B-frame changes, preserving every scalar gate and all endpoints."""
from pathlib import Path
import argparse,copy,gzip,hashlib,importlib.util,json
P=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('promotion',P/'construction/promo/build_promotion.py');B=importlib.util.module_from_spec(s);s.loader.exec_module(B)
def construct(raw,recipe):
 assert hashlib.sha256(raw).hexdigest()==recipe['input_content_sha256'],'input word pin'
 w=json.loads(raw);assert len(recipe['gate_frames'])==8 and all(c[0]=='B' for c in recipe['gate_frames']),'eight B frames'
 out=B.apply(w,dict(entrances={},gate_frames=recipe['gate_frames']))
 for section in ('A','cut','B','precondition','cleanup'):
  assert [e[:-1]for e in w[section]]==[e[:-1]for e in out[section]],'scalar program unchanged'
 assert out['start_extra']==w['start_extra'] and out['helper_final']==w['helper_final'],'endpoint frames unchanged'
 assert out['report']['local_profile']==recipe['expected']['local_profile'] and out['report']['width_inventory']==recipe['expected']['width_inventory'],'profile and width pins'
 data=json.dumps(out,sort_keys=True,separators=(',',':')).encode();assert hashlib.sha256(data).hexdigest()==recipe['expected']['output_content_sha256'],'output word pin'
 return data
ap=argparse.ArgumentParser();ap.add_argument('--input',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();raw=gzip.decompress(a.input.read_bytes());recipe=json.loads((P/'data/FRAME-RECIPE.json').read_text());data=construct(raw,recipe);rejected=[]
for name,change,reason in [('input-pin',lambda r:r.__setitem__('input_content_sha256','0'*64),'input word pin'),('old-frame',lambda r:r['gate_frames'][0].__setitem__(2,[]),'gate frame mismatch'),('output-pin',lambda r:r['expected'].__setitem__('output_content_sha256','0'*64),'output word pin')]:
 r=copy.deepcopy(recipe);change(r)
 try:construct(raw,r)
 except AssertionError as e:
  assert reason in str(e),(name,str(e));rejected.append(dict(name=name,reason=reason))
 else:raise AssertionError('accepted '+name)
a.out.mkdir();(a.out/'FULL-WORD.json.gz').write_bytes(gzip.compress(data,mtime=0));(a.out/'BUILD.json').write_text(json.dumps(dict(status='PASS_EIGHT_FRAME_EXACT_CONSTRUCTION',input_sha256=hashlib.sha256(raw).hexdigest(),output_sha256=hashlib.sha256(data).hexdigest(),scalar_program_unchanged=True,frames=8,rejected_controls=rejected),indent=2)+'\n');print('PASS eight B frames and three pin controls')

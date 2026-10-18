import os
import json,gzip,copy,importlib.util,math
from pathlib import Path
from collections import Counter
P=Path(__file__).resolve().parent;ROOT=P.parents[2]
def mod(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
promo=mod('p',ROOT/'research/gauge44-slots/construction/promo/build_promotion.py');a=mod('a',ROOT/'research/gauge44-slots/independent/audit_local.py');M=mod('M',P/'frame_model.py')
w=json.loads(gzip.decompress(Path(os.environ['K8_BASE_WORD']).read_bytes()));nw=json.loads(gzip.decompress((P/'end-combo-12-13-14-15.json.gz').read_bytes()));target=promo.chain_profile(nw)
# Revert annotations whose original frame has an exactly unchanged paid profile.
# A full independent cone/algebra audit validates the resulting literal word.
for iteration in range(3):
 changes=0
 for sec in ['A','B','early_cleanup']:
  for i,(old,new) in enumerate(zip(w[sec],nw[sec])):
   if old[-1]==new[-1]:continue
   saved=new[-1];new[-1]=old[-1]
   try:valid=promo.chain_profile(nw)==target
   except AssertionError:valid=False
   if valid:changes+=1
   else:new[-1]=saved
 print('reverted',changes,flush=True)
 if not changes:break
out=P/'ENDS-8.json.gz';out.write_bytes(gzip.compress(json.dumps(nw,sort_keys=True,separators=(',',':')).encode(),mtime=0))
recipe={sec:[[i,old[-1],new[-1]] for i,(old,new) in enumerate(zip(w[sec],nw[sec])) if old!=new] for sec in ['A','B','early_cleanup']};recipe['ends']=[[int(q),w['helper_final'][q],f] for q,f in nw['helper_final'].items() if f!=w['helper_final'][q]];(P/'ENDS-8-RECIPE.json').write_text(json.dumps(recipe,indent=2)+'\n');print('changes',{k:len(v) for k,v in recipe.items()});a.run(out,P/'ENDS-8-AUDIT.json',ROOT)

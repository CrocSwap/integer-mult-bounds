#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Source-pinned late-helper assignment, positive controls and word mutations.

The source-partner generator and exact algebra are PR2530/zxv's. PR2462
(Jeremy Kothe) supplies the native words; PR2436 (Tekalign) supplies lifted
compensation; PR2322 (Vlado Vojdanovski) supplies the frame/profile utilities.
New assignment and this wrapper: Mason Hale with OpenAI Codex assistance.
This is local exact evidence; complete native/global/outer admission is separate.
"""
import argparse,contextlib,copy,gzip,hashlib,importlib.util,io,json,sys,types
from pathlib import Path
HERE=Path(__file__).resolve().parent
ORIGINAL=[(656,49,33),(657,83,74),(658,98,85),(660,101,55),(632,68,4),(648,80,88),(649,88,80),(633,31,12)]
CURRENT=[(656,49,33),(657,83,74),(658,98,85),(660,101,55),(632,68,4),(596,80,88),(600,88,80),(633,31,12)]
LATE=[(680,49,33),(681,83,74),(682,98,85),(684,101,55),(688,68,4),(689,80,88),(690,88,80),(692,31,12)]
PROFILE={1:2363,2:632,3:318,4:120,5:26,7:4,8:4}
WIDTHS={4:33,5:9,7:62,8:78,9:240}
TARGETS={'23':[30],'34':[30],'50':[30],'108':[30],'14':[45],'41':[45],'43':[45],'52':[45],'78':[45],'99':[45],'104':[45],'106':[45]}
def need(ok,msg):
 if not ok:raise RuntimeError(msg)
def sha(b):return hashlib.sha256(b).hexdigest()
def sem(v):return sha(json.dumps(json.loads(json.dumps(v)),sort_keys=True,separators=(',',':')).encode())
def read(p):return json.loads(gzip.decompress(p.read_bytes())) if p.suffix=='.gz' else json.loads(p.read_bytes())
def write(p,v):
 raw=(json.dumps(v,sort_keys=True,separators=(',',':'))+'\n').encode();p.write_bytes(gzip.compress(raw,mtime=0) if p.suffix=='.gz' else raw)
def validate(root,pins):
 for rel,want in pins.items():need(sha((root/rel).read_bytes())==want,'source hash: '+str(root/rel))
def load_engine(pins):
 validate(HERE,pins['vendor'])
 file=HERE/'vendor/source_partner_generate.py';src=file.read_text()
 edits=[("HERE=Path(__file__).resolve().parent","HERE=Path(__file__).resolve().parent.parent"),
        ("def make(source, output, tag='base'):","def make(source, output, tag='base', assignments=None):"),
        (" assignments=[(656,49,33)"," if assignments is None:assignments=[(656,49,33)"),
        ("gzip.compress(json.dumps(nw,separators=(',',':')).encode())","gzip.compress(json.dumps(nw,separators=(',',':')).encode(),mtime=0)")]
 for before,after in edits:need(src.count(before)==1,'engine adaptation boundary');src=src.replace(before,after)
 m=types.ModuleType('pinned_source_partner_engine');m.__file__=str(file);exec(compile(src,str(file),'exec'),m.__dict__);return m

def controls(engine,source,word,folder):
 folder.mkdir();WP=engine.mod('negative_word_patch',source/'new/borrow/word_patch.py');AU=engine.mod('negative_audit',source/'new/borrow/audit_local.py');restored=WP.restored_of(word)
 firstnew=next(i for i,g in enumerate(word['A'][:word['prelude_events']]) if g[0]=='add' and g[2]==49 and g[-1]==[45])
 restoration=next(i for i,g in enumerate(word['B']) if g[:5]==['add',49,33,-1,1])
 original_warps=50
 need(len(word['warps'])==58,'control new warp count');need(word['warps'][original_warps][1]==49,'control first new lender')
 rs=[]
 for name in ['removed_prelude','missing_restoration','wrong_restoration_sign','wrong_alias','wrong_warp']:
  w=copy.deepcopy(word)
  if name=='removed_prelude':w['A'].pop(firstnew);w['prelude_events']-=1
  elif name=='missing_restoration':
   w['B'].pop(restoration)
   for x in w['warps']:
    if x[0]>restoration:x[0]-=1
  elif name=='wrong_restoration_sign':w['B'][restoration][3]=1
  elif name=='wrong_alias':
   i=w['warps'][original_warps][0];need(w['B'][i][1]==49,'control first alias use');w['B'][i][1]=83
  elif name=='wrong_warp':w['warps'][original_warps][2][0]^=w['warps'][original_warps][2][1]
  tmp=copy.deepcopy(w);tmp['A']=tmp['A'][w['prelude_events']:];w['cleanup']=WP.derive_cleanup(tmp,restored)
  # Recompute the bill where the changed frames are meaningful. This prevents
  # a stale claimed bill or stale inverse cleanup from being the rejection.
  stage='fresh_profile';log=io.StringIO()
  try:
   with contextlib.redirect_stdout(log):
    pp,iv=engine.paid_lifted(w);w['report']['local_profile']=pp;w['report']['width_inventory']=iv
    file=folder/(name+'.json.gz');write(file,w);stage='exact_word_audit';AU.run(file,folder/(name+'-unexpected-pass.json'))
  except (AssertionError,RuntimeError,ValueError) as exc:
   rs.append({'name':name,'rejected':True,'stage':stage,'error_type':type(exc).__name__,'reason':str(exc),'cleanup_rederived':True,'word_semantic_sha256':sem(w)})
  else:raise RuntimeError('negative control accepted: '+name)
  (folder/(name+'.log')).write_text(log.getvalue())
 write(folder/'RESULT.json',rs);return rs

def main():
 need(__debug__,'pinned upstream auditors require assertions; run without -O')
 ap=argparse.ArgumentParser();ap.add_argument('--source2462',type=Path,required=True);ap.add_argument('--source2588',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
 need(not a.out.exists(),'out must not exist');pins=read(HERE/'SOURCE-PINS.json');validate(a.source2462,pins['source2462']);validate(a.source2588,pins['source2588']);engine=load_engine(pins);a.out.mkdir(parents=True)
 result={'status':'PASS_LATE_ASSIGNMENT_LOCAL_WORDS_AND_CONTROLS','sources':pins['sources'],'assignments':LATE,'providers':{}}
 for tag in ['base','extra']:
  provider={}
  for label,assignment in [('pr2530',ORIGINAL),('pr2588',CURRENT),('candidate',LATE)]:
   dest=a.out/label;log=io.StringIO()
   with contextlib.redirect_stdout(log):w=engine.make(a.source2462,dest,tag,assignment)
   (dest/(tag+'-generation.log')).write_text(log.getvalue())
   if label=='pr2530':need(sem(w)==pins['pr2530_positive_semantics'][tag],'complete PR2530 positive word')
   if label=='pr2588':need(sem(w)==sem(read(a.source2588/f'new/borrow/words/BORROW-WORD-43{tag}.json.gz')),'complete PR2588 positive word')
   if label=='candidate':
    need(w['report']['local_profile']==PROFILE,'candidate paid profile');need(w['report']['width_inventory']==WIDTHS,'candidate width inventory');need(w['target_levels']==TARGETS,'candidate target map')
    provider['controls']=controls(engine,a.source2462,w,a.out/(tag+'-controls'))
   provider[label]={'semantic_sha256':sem(w),'local_profile':w['report']['local_profile'],'width_inventory':w['report']['width_inventory'],'target_levels':w['target_levels'],'word_content_sha256':sha(gzip.decompress((dest/f'eight-alias-{tag}.json.gz').read_bytes()))}
  result['providers'][tag]=provider;print('PASS',tag,'two exact predecessor words, candidate646-column audit, five rejecting controls',flush=True)
 write(a.out/'RESULT.json',result);print(result['status'])
if __name__=='__main__':main()

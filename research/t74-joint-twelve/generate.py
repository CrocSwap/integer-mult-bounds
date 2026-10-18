#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Tekalign (@tekuuu), with substantial OpenAI Codex assistance.
"""Rebuild the changed twelve-alias word and PR2679 pre-life/refit composition.
Pristine source is authenticated; only a fresh output directory is written.
"""
from pathlib import Path
import argparse,copy,gzip,hashlib,json,sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import joint_engine as J
ASSIGNMENTS=[(696,33,49),(697,55,101),(698,74,83),(700,85,98),(680,49,33),(681,83,74),(682,98,85),(684,101,55),(688,68,4),(689,80,88),(690,88,80),(692,31,12)]
def need(ok,msg):
 if not ok:raise ValueError(msg)
def rd(p):
 b=p.read_bytes();return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
def wr(p,w):p.write_bytes(gzip.compress((json.dumps(w,sort_keys=True,separators=(',',':'))+'\n').encode(),mtime=0))
def main():
 need(__debug__,'assertions must be enabled')
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--source',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
 source=a.source.resolve();out=a.out.resolve();pins=rd(HERE/'GENERATOR-PINS.json')
 sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
 need(sha(source/'MANIFEST.json')==pins['pr2679_manifest'],'PR2679 source manifest')
 need(all(sha(source/k)==v for k,v in rd(source/'MANIFEST.json').items()),'complete source files')
 need(all(sha(HERE/k)==v for k,v in pins['vendor'].items()),'vendor sources')
 need(not out.exists() and not out.is_relative_to(source),'fresh separate output required');out.mkdir(parents=True)
 S=source/'new/borrow';sys.path[:0]=[str(S),str(S/'prelife/search')]
 import build_word,word_patch as W,prelife2 as P,repair2,alias_build as AB,audit_local as AU
 for canon,tag,h in [('gauge44','base','eeb6a236'),('extra','extra','cd417b90')]:
  f=out/f'canonical-{tag}.json.gz';build_word.main(str(S/f'inputs/{canon}.canonical.json.gz'),str(S/'inputs/blocks.json'),str(S/f'inputs/witness_43_{tag}.json'),str(f),h);w=rd(f)
  patch=rd(S/f'inputs/refit_43{tag}.json')
  for sec,i,frame in patch['frames']:w[sec][i][-1]=frame
  w['report']['local_profile']=patch['local_profile'];w['cleanup']=W.derive_cleanup(w,W.restored_of(w))
  w=W.apply_kernel(w,rd(S/f'inputs/kernel_43{tag}.json'))
  for name in ['handoff','entrance']:w=W.apply_handoff(w,rd(S/f'inputs/{name}_43{tag}.json'))
  need(W.apply_lowfour(w,rd(S/f'inputs/lowfour_43{tag}.json'))==rd(HERE/f'inputs/POSITIVE2462-{tag}.json.gz'),'complete PR2462 positive reconstruction')
  w['prelude_events']=0;w=J.make(source,out/'joint',tag,seed=w,assignments=ASSIGNMENTS)
  patch=rd(S/f'inputs/prelife_43{tag}.json')
  for pair in patch['pairs']:
   host,borrower=pair['h'],pair['L'];E=next(x[4] for x in patch['fields']['warps'][58:] if x[1]==host)
   P.TRACE,_=repair2.run(copy.deepcopy(w),None);w=P.build(w,borrower,host,E)
  indices=[i for i,g in enumerate(w['B']) if g[:5]==['add',515,563,1,1]];need(len(indices)==1,'unique refit gate')
  w['B'][indices[0]][-1]=rd(S/f'inputs/refit563_43{tag}.json')['frames'][0][-1]
  w,_=AB.alias(w,653,563);lp,wi=AB.profile(w);w['report'].update(local_profile=lp,width_inventory=wi)
  f=out/f'WORD-{tag}.json.gz';wr(f,w);AU.run(f,out/f'audit-{tag}.json')
  need(rd(f)==rd(HERE/f'inputs/WORD-{tag}.json.gz'),'complete regenerated word equality')
 print('PASS_REGENERATED_JOINT_TWELVE_BOTH_WORDS')
if __name__=='__main__':main()

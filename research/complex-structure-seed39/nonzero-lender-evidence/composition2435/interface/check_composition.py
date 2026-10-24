#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Tekalign (@tekuuu), with substantial OpenAI Codex assistance.
# Entrance-raise source: Jeremy Kothe (@jeremykothe2), PR2435; source credit retained.
"""Exact finite composition screen: FOUR428 plus PR2435's 24 entrance raises.

Transfers only the exact 24 start and93gate-frame deltas, with matched old
frames and scalar operations. Does not import PR2435's handoff construction.
No native physical phase/compiler or global/outer admission is claimed.
"""
from collections import Counter
import copy,difflib,gzip,hashlib,importlib.util,json
from fractions import Fraction as Q
from pathlib import Path
import tempfile
HERE=Path(__file__).resolve().parent
COMP=HERE.parent
CASE=COMP.parent
OLD=CASE.parent/'anticipatory-stage-evidence'
RAISED=[474,475,476,477,486,487,488,489,522,523,524,525,526,527,528,529,534,535,536,537,538,539,540,541]
PROTECTED={33,55,74,85,49,101,83,98,135,146,162,220}

def read(p):return json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def span(v):
 s={0}
 for x in v:s|={y^x for y in s.copy()}
 return frozenset(s)
def signature(e):
 if e[0] in ('add','scale'):return json.dumps(e[:-3]+[str(Q(*e[-3:-1]))],separators=(',',':'))
 return json.dumps(e,separators=(',',':'))
def support(e):return e[1:3] if e[0]=='add' else e[1:2]
def writeword(p,w):p.write_bytes(gzip.compress(json.dumps(w,sort_keys=True,separators=(',',':')).encode(),mtime=0))

def main():
 assert __debug__
 pins=read(COMP/'SOURCE-PINS.json');assert pins['head']=='324d7d3590dc21003940a44cb0cbdc32b3620f25'
 for name,h in pins['files'].items():assert sha(COMP/'vendor'/name)==h,name
 spec=importlib.util.spec_from_file_location('four_transport',CASE/'transport_lifted.py');T=importlib.util.module_from_spec(spec);spec.loader.exec_module(T)
 report={}
 for tag in ('base','extra'):
  source=COMP/f'vendor/new/borrow/inputs/entrance_43{tag}.json'
  before=COMP/f'vendor/new/borrow/inputs/handoff_43{tag}.json'
  e,h=read(source)['fields'],read(before)['fields']
  original=CASE/f'words/FOUR-{tag}.json.gz';w=read(original);candidate=copy.deepcopy(w)
  parent=read(OLD/f'parent/new/borrow/words/BORROW-WORD-43{tag}.json.gz')
  starts=[int(r) for r in e['start_extra'] if span(e['start_extra'][r])!=span(h['start_extra'][r])]
  assert sorted(starts)==RAISED
  assert not set(starts)&set(w['removed']) and not set(starts)&{x[1] for x in w['warps']}
  helper_map={r:i+224 for i,r in enumerate(r for r in range(224,704) if r not in w['removed'])}
  start_records=[]
  for r in starts:
   old,new=h['start_extra'][str(r)],e['start_extra'][str(r)]
   assert span(old)==span(w['start_extra'][str(r)]) and len(old)==1 and len(new)==2 and span(old)<span(new)
   assert str(r) not in w['helper_final'],'expected FULL-ended copy helper'
   candidate['start_extra'][str(r)]=new
   start_records.append(dict(original=r,native=helper_map[r],old=old,new=new,old_width=8,new_width=7,terminal='FULL'))
  frame_records=[]
  for part,previous in [('A',parent['A']),('B',h['B'])]:
   after=e[part];assert len(previous)==len(after)
   assert all(signature(x)==signature(y) for x,y in zip(previous,after))
   delta=[i for i,(a,b) in enumerate(zip(previous,after)) if span(a[-1])!=span(b[-1])]
   matcher=difflib.SequenceMatcher(None,[signature(x) for x in previous],[signature(x) for x in w[part]],autojunk=False)
   mapping={i:j for b in matcher.get_matching_blocks() for i,j in zip(range(b.a,b.a+b.size),range(b.b,b.b+b.size))}
   assert len(delta)==(45 if part=='A' else 48)
   for i in delta:
    assert i in mapping; j=mapping[i]
    assert signature(previous[i])==signature(w[part][j])
    assert span(previous[i][-1])==span(w[part][j][-1]),(part,i,j)
    # Exact whole-A alignment / unique local B context removes heuristic ambiguity.
    if part=='A':
     assert j==i+28 and [signature(x) for x in previous]==[signature(x) for x in w[part][28:]]
    else:
     aa=[signature(x) for x in previous];bb=[signature(x) for x in w[part]]
     context=aa[i-2:i+3];assert context==bb[j-2:j+3]
     assert sum(aa[k:k+5]==context for k in range(len(aa)-4))==sum(bb[k:k+5]==context for k in range(len(bb)-4))==1,(part,i)
    assert not set(support(after[i]))&PROTECTED,(part,i)
    candidate[part][j][-1]=after[i][-1]
    frame_records.append(dict(part=part,source_index=i,four_index=j,operation=after[i][:-1],old=previous[i][-1],new=after[i][-1]))
  # Every mathematical field outside the declared deltas is exactly unchanged.
  for key in set(w)-{'A','B','start_extra','report'}:assert candidate[key]==w[key],key
  for part in ['A','B']:
   assert [signature(x) for x in candidate[part]]==[signature(x) for x in w[part]]
  oldprofile=Counter({int(k):v for k,v in w['report']['local_profile'].items()});profile=oldprofile.copy()
  for rank,n in [(1,24),(2,120),(3,-96)]:profile[rank]+=n
  assert all(n>0 for n in profile.values())
  candidate['report']['local_profile']=dict(sorted(profile.items()))
  widths=Counter({int(k):v for k,v in w['report']['width_inventory'].items()});widths[8]-=24;widths[7]+=24
  candidate['report']['width_inventory']=dict(sorted(widths.items()))
  path=HERE/f'COMPOSED-{tag}.json.gz';writeword(path,candidate)
  with tempfile.TemporaryDirectory(prefix='composition2435-transport-') as td:
   out=Path(td)/'valid';T.run(path,out);audit=read(out/'SCALAR-FRAME-AUDIT.json');canonical=read(out/'CANONICAL-WORD.json.gz')
   assert audit['helpers']==428 and audit['live_columns_each_orientation']==652 and audit['zero_buffers']==76 and audit['warps']==52
   assert audit['local_rank_mass']==5304 and audit['local_profile']=={str(k):v for k,v in profile.items()}
   assert {int(k):v for k,v in widths.items()}==dict(Counter(audit['widths']))
   for r in starts:assert canonical['helper_origin'][helper_map[r]-224]==r and len(canonical['frames'][canonical['start'][helper_map[r]]])==2
   # Omitting the first necessary A-frame raise must fail the retained transport.
   bad=copy.deepcopy(candidate);first=next(x for x in frame_records if x['part']=='A');bad['A'][first['four_index']][-1]=first['old'];badpath=Path(td)/'missing-frame.json.gz';writeword(badpath,bad)
   try:T.run(badpath,Path(td)/'invalid')
   except AssertionError as exc:control=str(exc)
   else:raise AssertionError('accepted omitted frame adaptation')
  report[tag]=dict(original_four_sha256=sha(original),entrance_source_sha256=sha(source),handoff_source_sha256=sha(before),composed_word_sha256=sha(path),starts=start_records,frame_edits=frame_records,frame_edit_counts={'A':45,'B':48},profile_delta={'1':24,'2':120,'3':-96},local_profile=dict(sorted(profile.items())),width_inventory=dict(sorted(widths.items())),transport=audit,omitted_frame_control=control,unchanged='All scalar operations/coefficients and their order; original A prelude, target COPY levels/segments, warps, cut, source restoration, cleanup, helpers removed and private zero inventory. Existing24 entry/exit wrappers require fresh dimension-two recipes; no new wrapper pair is introduced.')
 receipt=dict(status='PASS_EXACT_FRAME_DELTA_COMPOSITION_AND_BOTH_ORIENTATION_FREE_ALGEBRA_NO_NATIVE_GLOBAL_ADMISSION',base='7ee02b7c96d85f22b38d28bd7ed49bb8c1aeb261',pr2435_head=pins['head'],source_sha256=sha(COMP/'SOURCE-PINS.json'),checker_sha256=sha(Path(__file__)),providers=report,attribution='Jeremy Kothe (@jeremykothe2), PR2435 entrance raises; Tekalign (@tekuuu), FOUR428 composition, substantial OpenAI Codex assistance, Apache-2.0.',obligations=['Fresh physical Clifford recipes and all-column native phase/wrapper admission for24 dimension-two entrances.','Update literal global owner widths and pay all changed residual wrappers and idle children.','Repeat complete physical invoice, global checks and outer transfer before any new kappa claim.'])
 (HERE/'COMPOSITION-CHECK.json').write_text(json.dumps(receipt,indent=2)+'\n');print(receipt['status'])
if __name__=='__main__':main()

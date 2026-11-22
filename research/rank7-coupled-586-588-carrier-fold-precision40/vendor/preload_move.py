# SPDX-License-Identifier: Apache-2.0
"""Declared preload-move stage: two more staged quartets on the PR2857 shared-kernel words.

Preload re-synthesis (quartets (456,457,466,467) and (458,459,464,465)) by Jeremy Kothe
(jeremykothe2), with AI assistance; the staged-kernel gate shapes, frame/inverse-cleanup
conventions and the dirt-entry supplier are credited in CREDITS.md (PR2857 Lyy-iiis, PR2863
Dugongue, PR2833 Jeremy Kothe, PR2853 philippeVV).

apply(word, patch) takes the decoded PR2857 shared-kernel word and a DECLARED patch input
that lists every changed gate. Every listed old gate must be present at its index, no
other gate may change, the changed sections are limited to
{A, B, compensation, start_extra, report, cleanup}, the frame/paid profile and width
inventory are re-derived exactly from the changed word and must equal the declaration, and
the inverse-reverse cleanup is re-derived. The inherited exact auditor (forward and dual
free-operator replay over every input column) is the separate semantic check.
No file, import, process or output is touched by apply().
"""
import copy, hashlib, json
from collections import Counter

SOURCE_CANONICAL = {
 'base': 'c0af0ef7ee6282e91f046d027983b35eaed7ebcb46489134d47e07724cf664bc',
 'extra': '61b20fbe78fdcbca0cde0597befcc254017ee206dad0724c576672aca690c66f',
}
ALLOWED_SECTIONS = {'A', 'B', 'compensation', 'start_extra', 'report', 'cleanup'}

def require(ok, reason):
 if not ok:raise ValueError(str(reason))

def canon(w):return hashlib.sha256(json.dumps(w,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def basis(vs):
 piv={}
 for a in vs:
  while a:
   bit=a.bit_length()-1
   if bit in piv:a^=piv[bit]
   else:piv[bit]=a;break
 for k in sorted(piv):
  for j in piv:
   if j>k and piv[j]>>k&1:piv[j]^=piv[k]
 return tuple(piv[k] for k in sorted(piv,reverse=True))

def contained(a,b):return basis(a+b)==b

def restored_of(w):
 n=2*w['report']['v']+w['report']['R']
 return {g[1]-n for g in w['cleanup'] if g[1]>=n}|{g[2]-n for g in w['cleanup'] if g[0]=='add' and g[2]>=n}

def derive_cleanup(w,restored):
 v=w['report']['v'];n=2*v+w['report']['R'];full=list(basis([1<<i for i in range(w['report']['h'])]))
 byp={}
 for op,rec in enumerate(w['warps'],1):byp.setdefault(rec[0],[]).append((op,rec))
 fw=list(w['A'])
 for p in range(len(w['B'])+1):
  for op,rec in byp.get(p,[]):fw.append(['warp',rec[1],op])
  if p<len(w['B']):fw.append(w['B'][p])
 fw+=w['restore'];buf=lambda r:r+n if r in restored else r;out=[]
 for g in reversed([g for g in fw if g[0]=='warp' or not(v<=g[1]<2*v)]):
  if g[0]=='warp':out.append(['warp',buf(g[1]),-g[2],full])
  elif g[0]=='add':out.append(['add',buf(g[1]),buf(g[2]),-g[3],g[4],full])
  else:out.append(['scale',buf(g[1]),g[3],g[2],full])
 return out

def frame_report(x):
 """Exact paid profile and width inventory of a word, by the inherited frame rules."""
 full=basis([1<<i for i in range(9)]);end=[full]*112+[basis([z for z in range(1,512) if(z&p).bit_count()%2==0]) for p in x['ports']]+[full]*480
 for r,U in x['helper_final'].items():end[int(r)]=basis(U)
 start=[(p,) for p in x['ports']]+[()]*(112+480)
 for r,U in x['start_extra'].items():start[int(r)]=basis(U)
 cur=start.copy();paid=Counter()
 def climb(r,U):
  U=basis(U);require(contained(cur[r],U),('nonmonotone frame',r,cur[r],U))
  d=len(U)-len(cur[r])
  if d:paid[d]+=1
  cur[r]=U
 def step(g):
  if g[0]=='warp':require(cur[g[1]]==basis(g[3]),'A warp frame');cur[g[1]]=basis(g[4])
  else:
   for r in(g[1:3] if g[0]=='add' else g[1:2]):climb(r,g[-1])
 for g in x['A']:step(g)
 for r,U in zip(x['centers'],x['center_frames']):
  require(cur[r]==basis(U),'centre frame')
  for T in sorted({basis(x['target_levels'].get(str(g[1]-112),[])) for g in x['cut'] if g[2]==r},key=lambda t:-len(t)):
   if basis(U)!=T:paid[len(U)-len(T)]+=1
   U=T
 bw={}
 for rec in x['warps']:bw.setdefault(rec[0],[]).append(rec)
 for p in range(len(x['B'])+1):
  for rec in bw.get(p,[]):require(cur[rec[1]]==basis(rec[3]),'B warp frame');cur[rec[1]]=basis(rec[4])
  if p<len(x['B']):step(x['B'][p])
 for g in x['restore']:step(g)
 live=set(range(704))-set(x['removed'])
 for r in live:climb(r,end[r])
 inv=Counter(len(end[r])-len(start[r]) for r in live if r>=224)
 return {str(k):v for k,v in sorted(paid.items())},{str(k):v for k,v in sorted(inv.items())}

def apply(word, patch):
 """Return (changed word, ledger). Authenticates the decoded source first."""
 require(patch.get('stage')=='preload-move','stage tag')
 digest=canon(word);require(digest==patch['source_canonical_sha256'],'source canonical hash differs from the declared source')
 require(patch['variant'] in SOURCE_CANONICAL and SOURCE_CANONICAL[patch['variant']]==digest,'unauthorized decoded source SHA256')
 x=copy.deepcopy(word)
 # A: replacements and insertions, both addressed by index in the SOURCE A (before any edit).
 ops=patch['A_edits'];seen=set();byp={};repl={}
 for e in ops:
  if e['op']=='replace':
   i=e['index'];require(i not in seen and i not in repl,('duplicate A replace',i));require(word['A'][i]==e['old'],('A old gate mismatch',i,word['A'][i]));repl[i]=e['new']
  else:
   require(e['op']=='insert' and 0<=e['before']<=len(word['A']),'A edit op');byp.setdefault(e['before'],[]).append(e['gate'])
 A=[]
 for p in range(len(word['A'])+1):
  A.extend(copy.deepcopy(g) for g in byp.get(p,[]))
  if p<len(word['A']):A.append(copy.deepcopy(repl.get(p,word['A'][p])))
 x['A']=A
 for name in ('B','compensation'):
  idx=set()
  for e in patch[name+'_edits']:
   i=e['index'];require(i not in idx,(name,'duplicate index',i));idx.add(i);require(word[name][i]==e['old'],(name,'old gate mismatch',i,word[name][i]));x[name][i]=copy.deepcopy(e['new'])
 for r,U in patch['start_extra_added'].items():
  require(r not in x['start_extra'],('start_extra already declared',r));x['start_extra'][r]=list(U)
 require(x['prelude_events']==word['prelude_events']+0 and len(x['A'])==len(word['A'])+len(patch['A_edits'])-len(repl),'A length bookkeeping')
 profile,inventory=frame_report(x)
 require(profile==patch['declared_local_profile'] and inventory==patch['declared_width_inventory'],('derived paid profile/width inventory differ from the declaration',profile,inventory))
 x['report']['local_profile']=profile;x['report']['width_inventory']=inventory
 t=copy.deepcopy(x);t['A']=t['A'][t['prelude_events']:];x['cleanup']=derive_cleanup(t,restored_of(x))
 changed={k for k in word if word[k]!=x[k]}
 require(changed<=ALLOWED_SECTIONS,('sections outside the declared stage',changed-ALLOWED_SECTIONS))
 require(x['warps']==word['warps'] and x['helper_final']==word['helper_final'] and x['removed']==word['removed'] and x['prelude_events']==word['prelude_events'],'phase and buffer ABI unchanged')
 require(canon(x)==patch['candidate_canonical_sha256'],'candidate canonical hash differs from the declaration')
 ledger=dict(variant=patch['variant'],source_canonical_sha256=digest,candidate_canonical_sha256=canon(x),local_profile=profile,width_inventory=inventory,
  changed_sections=sorted(changed),A_replaced=sorted(repl),A_inserted=sum(map(len,byp.values())),B_edits=len(patch['B_edits']),compensation_edits=len(patch['compensation_edits']),start_extra_added=sorted(patch['start_extra_added']))
 return x,ledger

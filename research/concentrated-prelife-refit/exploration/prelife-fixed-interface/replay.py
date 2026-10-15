#!/usr/bin/env python3
"""Standalone fixed-interface pre-life obstruction checker; standard library only.

Reverse-bound method: PR2679 pre-life/propagated-pin work (Philippe Van Velzen).
This transparent replay: Marius-Paul Dumitrean with OpenAI Codex assistance.
Reads two immutable PR2733 words; never writes supplier files.
"""
if not __debug__:
 raise RuntimeError('Run without -O; assertions are part of verification.')
from pathlib import Path
from functools import lru_cache
import argparse,collections,copy,gzip,hashlib,json,time

def basis(vs):
 p={}
 for x in vs:
  while x:
   k=x.bit_length()-1
   if k in p:x^=p[k]
   else:p[k]=x;break
 for k in sorted(p):
  for j in p:
   if j>k and(p[j]>>k)&1:p[j]^=p[k]
 return tuple(p[k]for k in sorted(p,reverse=True))
FULL=basis([1<<i for i in range(9)])
def contained(U,V):return basis(list(U)+list(V))==V
@lru_cache(None)
def ann(U):return basis([v for v in range(512)if all((v&u).bit_count()%2==0 for u in U)])
@lru_cache(None)
def meet(U,V):return ann(basis(list(ann(U))+list(ann(V))))
def regs(g):return g[1:3]if g[0]=='add'else g[1:2]
def upper(w):
 end=[FULL]*112+[basis(v for v in range(512)if(v&p).bit_count()%2==0)for p in w['ports']]+[FULL]*480
 for r,U in w['helper_final'].items():end[int(r)]=basis(U)
 up=list(end);hi={};warp_checks=0
 def gate(g,label):
  assert g[0]in['add','scale'];H=FULL
  for r in regs(g):H=meet(H,up[r])
  assert contained(basis(g[-1]),H),('baseline positive gate violates bound',label)
  for r in regs(g):up[r]=H
  return H
 for j in range(len(w['restore'])-1,-1,-1):gate(w['restore'][j],('restore',j))
 by=collections.defaultdict(list)
 for op,rec in enumerate(w['warps'],1):by[rec[0]].append((op,rec))
 for i in range(len(w['B']),-1,-1):
  if i<len(w['B']):hi[i]=gate(w['B'][i],('B',i))
  for op,(pos,r,G,U,E)in reversed(by[i]):
   assert contained(basis(E),up[r]),('baseline warp output violates bound',op,r)
   up[r]=basis(U);warp_checks+=1
 return hi,warp_checks

def domain(w):
 live=sorted(set(range(224,704))-set(w['removed']));buffers=set()
 for g in w['cleanup']:
  for r in regs(g):
   if r>=704:buffers.add(r-704)
 pos=collections.defaultdict(list)
 for i,g in enumerate(w['B']):
  for r in regs(g):pos[r].append(i)
 warped={r[1]for r in w['warps']}
 hosts=[h for h in live if str(h)in w['helper_final']and h in buffers and h not in warped and not any(h in regs(g)for g in w['restore'])]
 borrowers=[L for L in live if str(L)not in w['helper_final']and str(L)not in w['start_extra']and L not in buffers and pos[L]and not any(L in regs(g)for sec in ['precondition','A','cut','restore']for g in w[sec]if g[0]!='warp')]
 pairs=[]
 for h in hosts:
  for L in borrowers:
   if h==L or max(pos[h],default=-1)>=pos[L][0]or any(rec[1]==L and rec[0]<pos[L][0]for rec in w['warps']):continue
   assert not any(g[0]=='warp'and g[1]==L for g in w['A'])
   d=len(basis(w['helper_final'][str(h)]));s=len(basis(w['start_extra'].get(str(h),[])));pairs.append((h,L,d,s,pos[L][0]))
 return hosts,borrowers,pairs

PINS={'base': 'ff85b16fa4bdebab6af9ea2d77fcfa81dcb8f4bc3511cf6ea4c34f5ad7684f30', 'extra': 'e89f28aa8577d2c7c26ed9b5b878e4ad25a8decb9a1b70b837970db7627dd94b'}
def check(path,tag):
 raw=path.read_bytes();assert hashlib.sha256(raw).hexdigest()==PINS[tag],('immutable source word hash',tag);w=json.loads(gzip.decompress(raw));assert w['report']['h']==9 and w['report']['v']==112 and w['report']['R']==480
 H,n=upper(w);hosts,borrowers,pairs=domain(w);rows=[]
 for h,L,d,s,i in pairs:
  assert d==4 and s==0
  rows.append({'h':h,'L':L,'first_B':i,'host_end_dimension':d,'borrower_first_upper':list(H[i]),'upper_dimension':len(H[i]),'infeasible':d>len(H[i])})
 assert len(rows)==32 and set(borrowers)=={530,542}and all(r['infeasible']for r in rows)
 # Positive algebra controls and a concrete corrupted-boundary rejection.
 assert len(FULL)==9 and meet(FULL,FULL)==FULL and meet(FULL,())==()
 bad=copy.deepcopy(w);bad['helper_final']['530']=[]
 try:upper(bad)
 except AssertionError:pass
 else:raise AssertionError('Invalid zero final frame was accepted')
 return {'source_word_sha256':hashlib.sha256(raw).hexdigest(),'eligible_host_labels':hosts,'borrowers':borrowers,'pairs':rows,'fixed_warp_positive_checks':n,'positive_existing_frames':'PASS','zero_final_frame_control':'REJECTED'}

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--base-word',type=Path,required=True);p.add_argument('--extra-word',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();assert not a.out.exists();start=time.process_time();r={t:check(f,t)for t,f in [('base',a.base_word),('extra',a.extra_word)]};result={'status':'PASS_FIXED_INTERFACE_SINGLE_PRELIFE_OBSTRUCTION','source2733_head':'2761b52b17590b8cf94f2e410004a8252d5592dc','providers':r,'scope':'Single extra cold-host pre-life replacement, unchanged scalar incidence and all existing warp pins. Any rank-four image and any gate-frame reassignment are covered. Changed warp interfaces and other grammars are excluded. Group projection is not claimed by this script.','cpu_seconds':time.process_time()-start,'checker_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()};a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(result,indent=2)+'\n');print(result['status'])
if __name__=='__main__':main()

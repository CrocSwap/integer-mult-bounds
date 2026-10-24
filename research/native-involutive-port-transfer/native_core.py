"""Exact source-bound coded-supplier replay core. Apache-2.0; Codex assistance.
Frozen source: Cao Yifan #4610 and retained Cinna Davis/Dugongue lineage.
"""
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter
from hashlib import sha256
import gzip,json,copy,importlib.util,sys
HERE=Path(__file__).resolve().parent
SOURCE_SHA='cfcd36b40326d7a5815e1db5313444379b3fb756b27d5201c561574c085cc0dd'
def need(c,m):
 if not c:raise ValueError(m)
def identity(i):return {(i,()):Q(1)}
def add(dst,src,a):
 for k,v in tuple(src.items()):
  z=dst.get(k,Q(0))+a*v
  if z:dst[k]=z
  else:dst.pop(k,None)
def warp(row,op,back):
 s=(1 if op>0 else -1)*(abs(op)+(1000000 if back else 0));out={}
 for (v,w),a in row.items():
  ww=w[1:]if w and w[0]==-s else(s,)+w;out[v,ww]=out.get((v,ww),Q(0))+a
 return {k:a for k,a in out.items()if a}
def expected(i,back):
 r=identity(i)
 if back and i<112:add(r,identity(i+112),-1)
 if not back and 112<=i<224:add(r,identity(i-112),1)
 return r

def replay(c,program,back=False,check_frames=True):
 rows={i:identity(i)for i in range(632)};rows[632]={};cur=c['start'][:]+[None];paid=Counter();maxnorm=Q(1)
 for e in program:
  if e[0]=='scalar':
   g,f=e[1:];r=g[1][1]+(632 if g[1][0]=='C'else 0)
   if g[0]=='clear':need(r==632,'Borrowed erasure');rows[r]={};cur[r]=f
   else:
    if check_frames:need(cur[r]==f,'Scalar target frame')
    if g[0]in('add','copy'):
     v=g[2][1]+(632 if g[2][0]=='C'else 0)
     if check_frames:need(cur[v]==f,'Scalar source frame')
     if g[0]=='copy':need(r==632,'Borrowed overwrite');rows[r]=rows[v].copy()
     else:need(r!=v,'Self add');add(rows[r],rows[v],Q(g[3],g[4]))
    elif g[0]=='scale':rows[r]={k:Q(g[2],g[3])*v for k,v in rows[r].items()}
    else:raise ValueError('Scalar opcode')
    maxnorm=max(maxnorm,sum(map(abs,rows[r].values()),Q(0)))
  elif e[0]=='warp':
   _,r,op,x,y=e;r=r[1]+(632 if r[0]=='C'else 0)
   if check_frames:need(cur[r]==x,'Warp source frame')
   rows[r]=warp(rows[r],op,back);cur[r]=y
  elif e[0]=='climb':
   _,_,r,x,y,k=e
   if check_frames:need(cur[r]==x,'Climb source frame')
   need(k==len(c['frames'][y])-len(c['frames'][x])and k>0,'Ascending paid rank');cur[r]=y;paid[k]+=1
  elif e[0]=='center':
   _,r,x,y,k=e;r+=632
   if check_frames:need(cur[r]==x,'Center source frame')
   need(k==abs(len(c['frames'][y])-len(c['frames'][x])),'Center paid rank');cur[r]=y;paid[k]+=1
  else:need(e[0]in('phase','adapter','residual_adapter'),'Unknown opcode')
 need(cur[:632]==c['final'],'Final frames');need(not rows[632],'Owned field cleared')
 return rows,paid,maxnorm

def clear_centers(program):return [['scalar',['clear',['C',e[1]]],e[3]]if e[0]=='center'else copy.deepcopy(e)for e in program]
def error_kernel(a):
 rows,paid,_=replay(a['canonical'],clear_centers(a['programs']['forward']));E=[]
 for i in range(632):
  err=rows[i].copy();add(err,expected(i,False),-1)
  for (j,w),v in sorted(err.items()):
   need(112<=i<224 and(j<112 or j>=224),'Strict triangular error block');need(not w,'Constant owner kernel')
   need(a['canonical']['final'][j]==1,'Repair source final full frame');need(j<112 or a['canonical']['start'][j]==0,'Pre-repair source initial ground')
   E.append((i,j,v))
 need(len(E)==12532,'Frozen error term count')
 return E


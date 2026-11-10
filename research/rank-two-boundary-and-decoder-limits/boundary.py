"""Exact same-word boundary-plane enlargement with ADD-component propagation.
No all-frames rank2 impossibility is claimed: neighbors remain frozen.
"""
from pathlib import Path
from fractions import Fraction as Q
from collections import defaultdict
import gzip
import json
P=Path(__file__).resolve().parent
def nullspace(rows,n=8):
 a=[[Q(x) for x in row] for row in rows if any(row)];pivot=[];k=0
 for j in range(n):
  p=next((i for i in range(k,len(a)) if a[i][j]),None)
  if p is None:continue
  a[k],a[p]=a[p],a[k];v=a[k][j];a[k]=[x/v for x in a[k]]
  for i in range(len(a)):
   if i!=k and a[i][j]:v=a[i][j];a[i]=[x-v*y for x,y in zip(a[i],a[k])]
  pivot.append(j);k+=1
  if k==len(a):break
 out=[]
 for free in range(n):
  if free in pivot:continue
  v=[Q(i==free) for i in range(n)]
  for i,j in enumerate(pivot):v[j]=-a[i][free]
  out.append(v)
 return out

def boundary_rows():
 w=json.loads(gzip.decompress((P/'evidence/native-word.json.gz').read_bytes()))
 frames=json.loads(gzip.decompress((P/'evidence/frames.json.gz').read_bytes()))['frames']
 parent=[];frame=[]
 def new(f):parent.append(len(parent));frame.append(f);return len(parent)-1
 def root(x):
  while parent[x]!=x:parent[x]=parent[parent[x]];x=parent[x]
  return x
 def union(a,b):
  a,b=root(a),root(b)
  if a!=b:assert frame[a]==frame[b];parent[b]=a
 current=[new(f) for f in w['initial']]+[new(None) for _ in w['owned']];initial=current.copy();edges=[]
 for e in w['program']:
  if e[0]=='CLEAR':current[e[1]]=new(e[2])
  elif e[0]=='ADD':assert frame[root(current[e[1]])]==frame[root(current[e[2]])]==e[3];union(current[e[1]],current[e[2]])
  else:
   _,d,a,b,q=e;assert frame[root(current[d])]==a;v=new(b);edges.append((current[d],v,q));current[d]=v
 neighbors=defaultdict(set)
 for a,b,q in edges:
  a,b=root(a),root(b);neighbors[a].add(frame[b]);neighbors[b].add(frame[a])
 rows=[]
 for i in range(111):
  x=root(initial[i]);y=root(current[111+i]);fx,fy=frame[x],frame[y];assert frames[str(fx)]['dim']==1 and frames[str(fy)]['dim']==7
  q=frames[str(fx)]['B'][0];cx=[q];cy=[q]
  for f in neighbors[x]:
   if frames[str(f)]['dim']>1:cx+=frames[str(f)]['A']
  for f in neighbors[y]:
   if frames[str(f)]['dim']<7:cy+=frames[str(f)]['B']
  nx,ny,both=nullspace(cx),nullspace(cy),nullspace(cx+cy)
  rows.append({'port':i,'initial_control_ADD_component':x,'final_destination_ADD_component':y,'initial_frame':fx,'final_frame':fy,'initial_plane_extension_dimension':len(nx),'final_complement_shrink_dimension':len(ny),'paired_legal_second_direction_dimension':len(both),'basis':[[str(x) for x in v] for v in both],'initial_larger_neighbor_frames':sorted(f for f in neighbors[x] if frames[str(f)]['dim']>1),'final_smaller_neighbor_frames':sorted(f for f in neighbors[y] if frames[str(f)]['dim']<7)})
 return rows

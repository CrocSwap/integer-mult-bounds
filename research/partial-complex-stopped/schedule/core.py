"""Reconstruct the actual PR113 cyclic matched rational-center role word."""
import array,struct,collections
from pathlib import Path

def load(prefix, match_path):
 P=Path(prefix)
 with open(str(P)+'.bin','rb') as f:
  h,v,n,q=struct.unpack('<4I',f.read(16))
  args=array.array('I');args.fromfile(f,2*n)
  core=array.array('Q');core.fromfile(f,n)
  cover=array.array('Q');cover.fromfile(f,n)
  roots=array.array('I');roots.fromfile(f,q)
  kind=array.array('I');kind.fromfile(f,q)
  active=array.array('B');active.fromfile(f,n)
 with open(str(P)+'.labels','rb') as f:
  ranks=array.array('I');ranks.fromfile(f,n)
  types=array.array('B');types.fromfile(f,n)
 with open(match_path,'rb') as f:
  size=struct.unpack('<I',f.read(4))[0];match=array.array('I');match.fromfile(f,size)
 return dict(h=h,v=v,n=n,q=q,args=args,core=core,cover=cover,roots=roots,kind=kind,active=active,ranks=ranks,types=types,match=match)

def compile_word(z):
 h,v,n,q=z['h'],z['v'],z['n'],z['q'];args=z['args'];roots=z['roots'];active=z['active'];match=z['match'];ranks=z['ranks']
 uses=[[] for _ in range(n)]
 for node in range(1,n):
  if active[node] and args[2*node]:
   uses[args[2*node]].append(('g',node,0))
   uses[args[2*node+1]].append(('g',node,1))
 for j,node in enumerate(roots):uses[node].append(('r',j,0))
 useidx={};flat=[]
 for node in range(n):
  for use in uses[node]:useidx[use]=len(flat);flat.append(use)
 assert len(flat)==len(match)
 def ukey(use):
  if use[0]=='r':target=roots[use[1]];ordinal=n+use[1]
  else:target=use[1];ordinal=target
  return (ranks[target],ordinal)
 sorted_uses=[sorted(us,key=ukey) for us in uses]
 donor_to_target={}
 for i,donor in enumerate(match):
  if donor:
   assert donor not in donor_to_target
   donor_to_target[donor]=i
 assert len(donor_to_target)==37802
 role=[None]*len(flat);gates=[];born=[];R=0;src={};rootrole=[None]*q
 for node in sorted((x for x in range(1,n) if active[x]),key=lambda x:(ranks[x],x)):
  left,right=args[2*node:2*node+2]
  if left:
   in0=role[useidx[('g',node,0)]];in1=role[useidx[('g',node,1)]]
   assert in0 is not None and in1 is not None,(node,in0,in1)
   target=donor_to_target.get(node)
   if target is not None:
    value_node=roots[flat[target][1]] if flat[target][0]=='r' else args[2*flat[target][1]+flat[target][2]]
    if value_node==left:pivot,retired=in1,in0;ins=(in1,in0);swapped=True
    else:
     assert value_node==right,(node,value_node,left,right)
     pivot,retired=in0,in1;ins=(in0,in1);swapped=False
    assert role[target] is None
    role[target]=retired
   else:pivot=in0;ins=(in0,in1);swapped=False
  else:
   pivot=R;R+=1;born.append((node,pivot));src[node]=pivot;ins=(pivot,)
  outs=[pivot]
  assert sorted_uses[node] and not match[useidx[sorted_uses[node][0]]]
  assert role[useidx[sorted_uses[node][0]]] is None
  role[useidx[sorted_uses[node][0]]]=pivot
  for use in sorted_uses[node][1:]:
   i=useidx[use]
   if match[i]:continue
   assert role[i] is None
   slot=R;R+=1;born.append((node,slot));role[i]=slot;outs.append(slot)
  gates.append((node,ins,tuple(outs)))
 for j in range(q):rootrole[j]=role[useidx[('r',j,0)]]
 assert R==38506,R
 assert all(r is not None for r in role)
 return dict(R=R,gates=gates,src=src,rootrole=rootrole,born=born,uses=uses,role=role,flat=flat)

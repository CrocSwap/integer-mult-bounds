import sys,json,time
from pathlib import Path
from output import OUTPUT
import graph as S
sys.path.insert(0,str(S.ROOT/'research/general-gaussian-contact-search'))
import model as M,discover as D
def graph(payload,mode):
 nodes=[0,0]+S.NF;edges=[]
 for a,b,r,_ in S.paid:
  edges.append(('paid',a+2,b+2,r,tuple(S.frames[S.NF[a]])))
 for a,b,g,B in S.warp:
  edges.append(('warp',a+2,b+2,B,tuple(S.image(S.Gs[g],x) for x in B)))
 return nodes,edges,{n+2:0 for n in S.fixed|set(S.starts[:224])|set(S.ends[:224])},[]
M.graph=graph
original_load=M.load
def patched_load(path):
 payload=original_load(path)
 for direction,word in payload['programs'].items():
  for i,e in enumerate(word):
   if e[0]=='center':word[i]=['climb','center-discovery-accounting',632+e[1],e[2],e[3],e[4]]
 return payload
M.load=patched_load
if __name__=='__main__':
 cases=[('kernel',[1<<i]) for i in range(9)]
 cases += [('kernel',[1<<i,1<<j]) for i in range(9) for j in range(i+1,9)]
 cases += [('pauli',[1<<i,0]) for i in range(9)]
 cases += [('pauli',[0,1<<i]) for i in range(9)]
 cases += [('pauli',[1<<i,1<<j]) for i in range(9) for j in range(9)]
 results=[];best=0;start=time.monotonic()
 for i,(mode,forms) in enumerate(cases):
  r=D.solve(S.path.parent/'SOURCE-WORD.json.gz',forms,10,'none',mode)
  results.append(r);energy=r.get('actual_local_energy',0)
  if energy<best-1e-9:
   best=energy;(OUTPUT/'relaxed-general-best.json').write_text(json.dumps(r,indent=2)+'\n');print('BEST',i,mode,forms,energy,flush=True)
  if i%10==0:print('progress',i,len(cases),'seconds',time.monotonic()-start,'best',best,flush=True)
 (OUTPUT/'relaxed-general-screen.json').write_text(json.dumps(results,indent=2)+'\n');print('DONE',len(cases),time.monotonic()-start,'best',best,flush=True)

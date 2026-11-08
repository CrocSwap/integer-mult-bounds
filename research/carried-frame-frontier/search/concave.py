import cut as Q,joint as J,inspect,json,time
from pathlib import Path
from output import OUTPUT
ns=J.ns.copy();src=J.src
src=src.replace('power=[0.]+[i**t for i in range(1,11)]','power=[min(i,CAP) for i in range(11)]')
exec(src,ns);solve=ns['solve']
if __name__=='__main__':
 best=0;start=time.monotonic();records=[]
 for cap in range(1,10):
  ns['CAP']=cap
  low=0;count=0
  for l in range(1,512):
   r=solve(l,1);records.append({'cap':cap,'l':l,'energy':r['energy']})
   if r['energy']<low:
    low=r['energy'];(OUTPUT/'concave-best.json').write_text(json.dumps(dict(r,cap=cap),indent=2)+'\n')
   if r['energy']<0:count+=1
  print('CAP',cap,'negative_cases',count,'best',low,'seconds',time.monotonic()-start,flush=True)
 (OUTPUT/'concave-screen.json').write_text(json.dumps(records,indent=2)+'\n')

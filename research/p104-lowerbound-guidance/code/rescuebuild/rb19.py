"""rb19: build-up search. Start from the COORDINATE version (masks + mains of a logged design, all idle pieces singletons);
if it builds (fixed generic walks), greedily merge two idle pieces of one role (largest value gain first) while it still builds.
Reports the best BUILT (frame-level, numeric) design value per start.  usage: rb19.py k log1 [log2 ...]"""
import sys,ast,itertools;sys.path.insert(0,'.')
from rb13 import *
def coordof(d):
    return [(F(M),[F({t}) for t in M if t not in mn]) for M,P,mn in d]
def merges(R):
    out=[]
    for r,(M,P) in enumerate(R):
        for i,j in itertools.combinations(range(len(P)),2):
            R2=list(R);R2[r]=(M,[p for t,p in enumerate(P) if t not in (i,j)]+[P[i]|P[j]]);out.append(R2)
    return out
def climb(k,R,nw=3,tr=6):
    b,v=builds(k,R,nw=nw,tr=tr)
    if not b:return None,float(chat(k,R)),v
    cur=R
    while True:
        cands=sorted(merges(cur),key=lambda X:-float(chat(k,X)));moved=False
        for X in cands:
            if float(chat(k,X))<=float(chat(k,cur)):break
            if builds(k,X,nw=nw,tr=tr)[0]:cur=X;moved=True;break
        if not moved:return cur,float(chat(k,cur)),0
def main():
  k=int(sys.argv[1]);seen=set()
  for fn in sys.argv[2:]:
      for l in open(fn):
          if not l.startswith('#') and not l.startswith('(('):continue
          d=ast.literal_eval(l.split(' ',3)[3].strip() if l.startswith('#') else l.strip())
          key=tuple(sorted((tuple(sorted(M)),tuple(sorted(mn))) for M,P,mn in d))
          if key in seen:continue
          seen.add(key);R=coordof(d)
          best,val,res=climb(k,R)
          print('start',l.split()[1] if l.startswith('#') else 'sup','coord-chat %.3f'%float(chat(k,R)),
                ('BUILT-CLIMB %.3f'%val+' '+str([(sorted(M),[sorted(p) for p in P]) for M,P in best])) if best else 'coord stalls %.1e'%res,flush=True)

if __name__=='__main__':main()

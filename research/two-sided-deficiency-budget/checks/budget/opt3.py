import os; exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'opt2.py')).read().split('for b in range(1,9):')[0])
import itertools
for t in range(1,7):
  out=[]
  for b in range(1,9):
    K=t+b; best=None
    for k in range(1,K+1):
      for sig in itertools.combinations_with_replacement(range(6),k):
        if feasible(sig,b):
          s=sum(sig)
          if best is None or s<best: best=s
    out.append(max(0,6*b-best))
  print('t=%d deficit 6b-minSigma for b=1..8:'%t,out)

import sys,subprocess,ast
from symlp import lp
from collections import Counter
import os
def lists(d,target):
    src=open('enum.py').read().replace("for x in out[:15]: print(x)","for x in out: print(repr(x))")
    out=subprocess.run([sys.executable,'-c',src,str(d),str(target)],capture_output=True,text=True).stdout.splitlines()
    return [ast.literal_eval(l) for l in out if l.startswith('(')]
for d,codim,need in [(6,2,109),(7,1,111),(8,0,112)]:
    for wt,ws in lists(d,8*d+1):
        if wt!=8*d: continue
        val,bd=lp(dict(Counter(ws)),codim=codim,NL=112)
        print(d,ws,'LPval %.3f'%val,'exact bound',float(bd),'need',need,'KILLED' if bd<need else 'SURVIVES',flush=True)

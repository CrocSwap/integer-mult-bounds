# helper to name item sets relative to a target
import json, sys
sys.path.insert(0,'/home/claude/work/agentA')
from decomp import comps, name, lab, idx
if __name__=='__main__':
    t=int(sys.argv[1]); xs=list(map(int,sys.argv[2:]))
    print(lab[t], name(t,xs))

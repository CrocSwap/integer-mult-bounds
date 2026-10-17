from cov import *
import lib
from lib import lines,simple,canon,ip,n
idx={l:i for i,l in enumerate(lines)}
perms=[]
for a in simple:
    p=[]
    for l in lines:
        c=ip(l,a)
        v=tuple(x-c*y for x,y in zip(l,a))
        p.append(idx[canon(v)]+1)
    perms.append(p)
I=(0,1,2,3,4,5)
E6=[t+1 for t in parabolic(I)]
open('grp.g','w').write("G:=Group(%s);\nPrint(Size(G),\"\\n\");\nE6:=%s;\nS:=Stabilizer(G,E6,OnSets);\nPrint(Size(S),\"\\n\");\nPrint(List(GeneratorsOfGroup(S),g->ListPerm(g,120)),\"\\n\");\nQUIT;\n"%(
 ",".join("PermList(%s)"%p for p in perms), E6))

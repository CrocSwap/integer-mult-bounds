import sys
from common import *
hpe_word=rd(sys.argv[1]); recipe=rd(sys.argv[2])
w=BCE.apply(copy.deepcopy(hpe_word),recipe)
v,R=w['report']['v'],w['report']['R'];n=2*v+R
start,endB=frames_endB(w)
P,Pinv,comp=main_maps(w)
U30=span([256,128,64,32,18,10,6,1]);U24=span([256,128,64,32,24,4,2,1])
first={}
for part in ('A','B'):
    for e in w[part]:
        for r in regs(e):
            first.setdefault(r,span(e[-1]))
for U,ks in ((U30,[508,532,509,533]),(U24,[484,556,485,557])):
  for k in ks:
    print('k',k,'start',start[k],'endB',endB[k],{g:str(x) for g,x in Pinv[k].items()})
    for g,x in Pinv[k].items():
        if not inside(endB[g],U):
            print('   viol',g,'start',start[g],'first',first.get(g),'endB',endB[g],'row',{gg:str(xx) for gg,xx in Pinv[g].items()},'inQU?',[inside(endB[gg],U) for gg in Pinv[g]])

import sys
from feas import *
for h in map(int,sys.argv[1:]):
    print('== h',h,'start',len(start[h]),'end',len(end[h]),'inComp',h in compH)
    for idx,(tag,e) in enumerate(prog):
        if e[0]=='scale':
            if e[1]==h:print(' ',tag,'scale',e[2:4])
        elif h in e[1:3]:
            print(' ',tag,('h+= %s*r%d'%(e[3:5],e[2]) if e[1]==h else 'r%d+= %s*h'%(e[1],e[3:5])),'frame dim',len(B(e[-1])) if tag[0] not in 'PCL' else '-')

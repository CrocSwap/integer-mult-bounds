import sys; sys.argv=['x']
import k9b, numpy as np
S=k9b.S
# negative control: E6 = roots orthogonal to an A2
L=S.L; a=L[0]; b=[w for w in L if int(a@w)//4==-1 or int(a@(-w))//4==-1][0]
E6=['r%d'%t for t in range(120) if (L[t]@a)==0 and (L[t]@b)==0]
print('E6 lines',len(E6),'K9 graphic:',k9b.graphic(tuple(E6),9),flush=True)
sets=k9b.parse('../SERVE/all600.txt'); nk=0
for i,t in enumerate(sets):
    if k9b.graphic(t,9): nk+=1; print('GRAPHIC',i,len(t),flush=True)
print('DONE sets',len(sets),'graphic',nk,flush=True)

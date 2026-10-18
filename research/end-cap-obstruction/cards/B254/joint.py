import pickle
from sim import *
import closure as C
S=pickle.load(open('S161.pkl','rb'));ok=pickle.load(open('ok161.pkl','rb'))
for name,hs in (('all65',ok),('Brelay53',[h for h in ok if len(end[h])>0 and (h in S) and len(prog)>0 and h not in (408,412,424,428,546,547,548,549,558,560,568,570)]),):
    P=prog;rem=[]
    for h in hs:
        P2,_=C.remove(P,h)
        if P2 is None:print('bail',h);continue
        P=P2;rem.append(h)
    print(name,len(rem),simulate(P,removed=set(rem))[:2])

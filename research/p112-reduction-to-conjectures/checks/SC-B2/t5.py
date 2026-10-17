from cov3 import *
T=[t for t in range(n) if t not in set(parabolic((0,1,2,3,4,5)))]
tg=Tgt(T)
for w,Ls in ((7,[36,30,28,26,24]),(6,[20,19,18,17]),(5,[12,11,10]),(4,[8,7,6])):
    print(w,[(L,len(tg.level(w,L))) for L in Ls],flush=True)

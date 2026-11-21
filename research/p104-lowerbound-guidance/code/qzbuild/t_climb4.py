from qzclimb import *
import pickle
A=set(range(4))
masks=[A,A,{1,2,3},{1,2,3},{2,3},{2,3}]
pieces=[frozenset(p) for p in [{1}]*2+[{2}]*4+[{3}]*4]
order=(0,1,2,3); pos={t:i+1 for i,t in enumerate(order)}
place={i:pos[min(S)] for i,S in enumerate(pieces)}
best=climb(6,4,masks,pieces,order,place,log=sys.stdout)
pickle.dump(best,open('climb4.pkl','wb'))
print('BEST',best[0])

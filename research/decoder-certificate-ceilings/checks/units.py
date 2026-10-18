from geom import *
fr=[0]
for t in range(n):
    if all(G[t,s]==0 for s in fr): fr.append(t)
s=[t for t in range(n) if abs(G[0,t])==1][0]
units={'E8':(list(range(n)),8),'P112':([t for t in range(n) if t not in fr],8),
 'E7':([t for t in range(n) if G[t,0]==0],7),'E6':([t for t in range(n) if G[t,0]==0 and G[t,s]==0],6)}

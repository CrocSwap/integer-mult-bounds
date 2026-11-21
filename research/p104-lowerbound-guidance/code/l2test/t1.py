from base import *
import sys
print('2G=AhAh^T 104:',(2*G==Ah@Ah.T).all())
for n in (96,104):
    S=sections(n); rows=[]
    for u,X in S.items():
        w,c=omega(X); r=rankQ(Ah[X]) if X else 0
        rows.append((u,len(X),w,r))
    from collections import Counter
    cnt=Counter((a[1],a[2],a[3]) for a in rows)
    print('n',n); 
    for k,v in sorted(cnt.items()): print('  |X|,omega,rankE8',k,'x',v)
    print('  min omega',min(a[2] for a in rows),'min rankE8',min(a[3] for a in rows),'sections with omega<rankE8:',sum(1 for a in rows if a[2]<a[3]))
    import pickle; pickle.dump(rows,open('t1_%d.pkl'%n,'wb'))

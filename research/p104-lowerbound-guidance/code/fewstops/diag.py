from meet import *
st,members,pinev=meetings(W)
mid={}
for m,L in members.items():
    for x in L: mid[x]=m
init=[SM_[x] for x in W['initial']]; fin=[SM_[x] for x in W['final']]
chain=Counter(); 
for r in range(n):
    if kind(r)=='H' and dm(fin[r])-dm(init[r])==9:
        chain[tuple([dm(init[r])]+[dm(c) for c,_,_ in st[r]]+[dm(fin[r])])]+=1
print('climb-9 helper dim chains (init, stays..., final)',chain.most_common(12))
mc=Counter()
for r in range(n):
    if kind(r) in('X','Y','X2','Y2'):
        mc[(kind(r),tuple([dm(init[r])]+[dm(c) for c,_,_ in st[r]]+[dm(fin[r])]))]+=1
print('main chains',mc.most_common(16))

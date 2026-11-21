from meet import *
from decimal import Decimal as Dc, getcontext
getcontext().prec=50
st,members,pinev=meetings(W)
mid={}
for m,L in members.items():
    for x in L: mid[x]=m
pinned=set(pinev)
init=[SM_[x] for x in W['initial']]; fin=[SM_[x] for x in W['final']]
# per public: stays in pinned meetings
Porig=Counter(); Ppin=Counter(); stat=Counter()
for r in range(n):
    k=kind(r); kk='M' if k!='H' else 'H'
    ch=[init[r]]+[c for c,_,_ in st[r]]+[fin[r]]
    for a,b in zip(ch,ch[1:]):
        if a!=b: Porig[(kk,dm(b)-dm(a))]+=1
    chp=[init[r]]+[st[r][j][0] for j in range(len(st[r])) if mid[(r,j)] in pinned]+[fin[r]]
    for a,b in zip(chp,chp[1:]):
        if a!=b: Ppin[(kk,dm(b)-dm(a))]+=1
    for j in range(len(st[r])):
        first=j==0 and st[r][j][0]==init[r]; last=j==len(st[r])-1 and st[r][j][0]==fin[r]
        if first or last: continue
        stat[(kk,'pinned' if mid[(r,j)] in pinned else 'free')]+=1
print('intermediate stays',sorted(stat.items()))
print('moves orig',sum(Porig.values()),'pinned-only chains',sum(Ppin.values()))
# kappa if public moves = pinned-only chains (hypothetical upper bound for free-stop removal)
nat=pk.native_from_word(W); P0=Counter(nat['P'])
for (kk,r),v in Porig.items(): P0[r]-=v
for (kk,r),v in Ppin.items(): P0[r]+=v
ci=pk.caller_invoice(C); inv=pk.invoice(ci,dict(nat,P=P0)); print('kappa if all FREE stops removed (hyp.)',str(pk.kappa(inv['T'],inv['P'],20)['lo'])[:16])
# only helpers / only mains
for only in ('H','M'):
    P1=Counter(nat['P'])
    for (kk,r),v in Porig.items():
        if kk==only: P1[r]-=v
    for (kk,r),v in Ppin.items():
        if kk==only: P1[r]+=v
    inv=pk.invoice(ci,dict(nat,P=P1)); print(only,'free stops removed: kappa',str(pk.kappa(inv['T'],inv['P'],20)['lo'])[:16])

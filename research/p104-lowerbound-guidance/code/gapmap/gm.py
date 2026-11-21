# GAPMAP: exact decomposition of t7669's invoice vs the rung floors. threads=1, stdlib only.
import sys, json
sys.path.insert(0,'<word-rung-package>/tools')
import pricekit as pk
from collections import Counter, defaultdict
from decimal import Decimal as Dc, localcontext, getcontext
getcontext().prec=60
D='<word-rung-package>/data/'
W=pk.load(D+'t7669.json.gz'); C=pk.load(D+'7113_CALLER.json')
n=W['public']; P=W['program']; dim=[len(f) for f in W['frames']]
live=set(W['live']); H=W['hosted']
cls={}
for r in live: cls[r]='X'; cls[r+112]='Y'
for r in H['X2']: cls[r]='X2'
for r in H['Y2']: cls[r]='Y2'
# owned lifetimes
cur={}; life=[]  # (reg, init_i, clear_i, moves)
open_={}
for i,e in enumerate(P):
    if e[0]=='INIT': open_[e[1]]=[e[1],i,None,[]]
    elif e[0]=='CLEAR': l=open_.pop(e[1]); l[2]=i; life.append(l)
    elif e[0]=='MOVE' and e[1]>=n: open_[e[1]][3].append((dim[e[2]],dim[e[3]],i))
assert not open_
mainmoves=Counter(); mainper={}; helpmoves=Counter(); credit=Counter()
byclass=defaultdict(Counter)
for r in range(n):
    credit_r = dim[W['final'][r]]-dim[W['initial'][r]]
    if r not in cls: credit[credit_r]+=1
for i,e in enumerate(P):
    if e[0]=='MOVE' and e[1]<n:
        d=dim[e[3]]-dim[e[2]]; c=cls.get(e[1])
        if c: mainmoves[d]+=1; byclass[c][d]+=1
        else: helpmoves[d]+=1
Dh=Counter(); Rh=Counter(); mixed=0; Dl=[]; Rl=[]
for reg,i0,i1,mv in life:
    if not mv: continue
    ds=[b-a for a,b,_ in mv]
    if all(x<0 for x in ds): Dh.update(abs(x) for x in ds); Dl.append((reg,i0,i1,mv))
    elif all(x>0 for x in ds): Rh.update(ds); Rl.append((reg,i0,i1,mv))
    else:
        mixed+=1; print('MIXED lifetime',reg,ds)
print('D mass',sum(k*v for k,v in Dh.items()),'R mass',sum(k*v for k,v in Rh.items()),'mixed',mixed, 'lifetimes D',len(Dl),'R',len(Rl))
print('D hist',sorted(Dh.items()),'R hist',sorted(Rh.items()))
print('main moves',sorted(mainmoves.items()),'help',sorted(helpmoves.items()),'credit',sorted(credit.items()))
json.dump(dict(mainmoves=mainmoves, helpmoves=helpmoves, credit=credit, Dh=Dh, Rh=Rh, byclass={k:dict(v) for k,v in byclass.items()}),open('code/gapmap/hists.json','w'))

# functions of t (s=1-t)
def pw(r,t): return (Dc(r).ln()*(1-Dc(t))).exp() if r>0 else Dc(0)
def val(h,t): return sum(Dc(int(v))*pw(r,t) for r,v in h.items())
ci=pk.caller_invoice(C); L=ci['nJ']; print('calls',L)
def caller_net(t): return val(ci['T'],t)-val(ci['P'],t)
def mainsc(t): return val(mainmoves,t)
def helpnet(t): return val(helpmoves,t)-val(credit,t)
def Dc_(t): return val(Dh,t)
def Rc_(t): return val(Rh,t)
def native(t): return mainsc(t)+helpnet(t)+Dc_(t)+Rc_(t)
def F(t, adj=lambda t:Dc(0)): return caller_net(t)-L*native(t)+L*adj(t)
def root(f,lo=Dc('1e-6'),hi=Dc('0.05')):
    assert f(lo)>0 and f(hi)<0
    for _ in range(200):
        m=(lo+hi)/2
        if f(m)>0: lo=m
        else: hi=m
    return (lo+hi)/2
k0=root(F); print('kappa base',k0)
# floors
g8=lambda t: pw(8,t); psi=lambda t: pw(9,t)-pw(8,t); hh=lambda t: 1+pw(7,t)-pw(8,t)
fl={'mains':lambda t:400*g8(t), 'D':lambda t:56*psi(t), 'R':lambda t:56*psi(t), 'help':lambda t:104*hh(t)}
act={'mains':mainsc,'D':Dc_,'R':Rc_,'help':helpnet}
def exc(c,t): return act[c](t)-fl[c](t)
res={}
tk=k0
print('at kappa_f: s=',1-tk)
for c in act: print(c,'actual',float(act[c](tk)),'floor',float(fl[c](tk)),'excess',float(exc(c,tk)), 'excess/16? ')
tot=sum(exc(c,tk) for c in act); print('total excess',float(tot),'  = native - FL', float(native(tk)-(fl['mains'](tk)+fl['D'](tk)+fl['R'](tk)+fl['help'](tk))))
for c in act:
    res[c]=root(lambda t:F(t,lambda u:exc(c,u))); print('kappa with',c,'at floor:',res[c],' gain',float(res[c]-k0))
allk=root(lambda t:F(t,lambda u:sum(exc(c,u) for c in act))); print('all floors',allk)
for pair in [('D','R'),('mains','help'),('mains','D','R')]:
    print(pair, root(lambda t:F(t,lambda u:sum(exc(c,u) for c in pair))))
# caller budget
sf=1-tk
chat=lambda t: caller_net(t)/L-400*g8(t)
print('chat(.99)=',float(chat(Dc('0.01'))),' chat at kf',float(chat(tk)), ' 112psi+104h at kf', float(112*psi(tk)+104*hh(tk)), 'at .01', float(112*psi(Dc('0.01'))+104*hh(Dc('0.01'))))
print('chat(0)=',float(chat(Dc(0))))
# first-order D0 contributions: -F'(0): use finite derivative
def d0(h): return sum(Dc(int(v))*Dc(r).ln()*Dc(r) for r,v in h.items() if r>1)
print('D0 comps (r ln r sums per call): mains',float(d0(mainmoves)),'helper moves',float(d0(helpmoves)),'credit',float(d0(credit)),'D',float(d0(Dh)),'R',float(d0(Rh)))
print('floor D0: mains',float(400*8*Dc(8).ln()),'D,R each', float(56*Dc(9).ln()*9-56*Dc(8).ln()*8)) 

print('---- extra counterfactuals')
# helper split by climb group
h9m=Counter(); h9c=0
for r in range(n):
    if r in cls: continue
    cl=dim[W['final'][r]]-dim[W['initial'][r]]
    if cl==9:
        h9c+=1
        for e in []: pass
mvr=defaultdict(list)
for e in P:
    if e[0]=='MOVE' and e[1]<n: mvr[e[1]].append(dim[e[3]]-dim[e[2]])
h9m=Counter(); 
for r in range(n):
    if r in cls: continue
    if dim[W['final'][r]]-dim[W['initial'][r]]==9: h9m.update(mvr[r])
ex9=lambda t: val(h9m,t)-h9c*pw(9,t)
print('helper climb-9 group',h9c,'excess@kf',float(ex9(tk)))
print('kappa with climb-9 helpers single-jump', root(lambda t:F(t,ex9)))
# D,R at one-jump ideal 8*7^s
ide=lambda t: 8*pw(7,t)
print('kappa D,R both at 8*7^s', root(lambda t:F(t,lambda u:(Dc_(u)-ide(u))+(Rc_(u)-ide(u)))))
print('kappa D at 8*7^s', root(lambda t:F(t,lambda u:(Dc_(u)-ide(u)))))
print('Dc,Rc at kf',float(Dc_(tk)),float(ide(tk)))
# mains halved excess, helpers halved excess
print('kappa mains+helper excess halved', root(lambda t:F(t,lambda u:(exc('mains',u)+exc('help',u))/2)))
# S and D
print('S native per call (rank mass) at t=0 floor', 400*8+112, ' actual', float(native(Dc(0))))
print('caller net(0)',float(caller_net(Dc(0))), 'native*17(0)',float(17*native(Dc(0))), 'S=',float(caller_net(Dc(0))-17*native(Dc(0))))

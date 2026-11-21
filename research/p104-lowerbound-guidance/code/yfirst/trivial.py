# SANITY: a helper-free word: owned single-rank transfers at main endpoints. Checks my reading of the model.
import sys, json, gzip, copy; sys.path.insert(0,'../fewstops')
from load import *
from fractions import Fraction as Q
live=W['live']; Hh=W['hosted']; Dp=set(Hh['Dports'])
prog=[]; own=n  # owned ids start at n
Nown=0
def newown():
    global Nown; Nown+=1; return n+Nown-1
zero=[k for k,f in enumerate(F) if len(f)==0][0]
full=[k for k,f in enumerate(F) if len(f)==9][0]
for i,x in enumerate(live):
    y=x+112; cx=W['initial'][x]
    if i in Dp:
        a=newown(); prog+= [['INIT',a,cx],['ADD',a,x,'1',cx],['MOVE',a,cx,zero,True],['ADD',y,a,'1',zero],['CLEAR',a,zero]]
    else:
        a=newown(); b=newown()
        prog+= [['INIT',a,cx],['ADD',a,x,'1',cx],['MOVE',a,cx,zero,True],['INIT',b,zero],['ADD',b,y,'1',zero],
                ['SCALE',y,'1/2',zero],['ADD',y,a,'1/2',zero],['MOVE',b,zero,cx,True],['ADD',x,b,'-1',cx],['CLEAR',a,zero],['CLEAR',b,cx]]
for x2,y2 in zip(Hh['X2'],Hh['Y2']):
    cx=W['initial'][x2]; b=newown()
    prog+= [['INIT',b,zero],['ADD',b,y2,'1',zero],['MOVE',b,zero,cx,True],['ADD',x2,b,'-1',cx],['CLEAR',b,cx]]
# mains single jumps; helpers: single jump init->final as in t7669 (net zero)
for r in range(n):
    a,b=W['initial'][r],W['final'][r]
    if a!=b: prog.append(['MOVE',r,a,b,False])
W2=dict(W); W2['program']=prog; W2['owned_fields']=Nown
r=pk.replay(W2); print('replay ok',r['ok'],r['problems'][:3])
R=r['rows']; base=pk.replay(W)['rows']
print('rows equal t7669 on all publics', all(R[x]==base[x] for x in range(n)))
nat=pk.native_from_word(W2); ci=pk.caller_invoice(C); inv=pk.invoice(ci,nat)
print('P',dict(nat['P']),'T',dict(nat['T']))
k=pk.kappa(inv['T'],inv['P'],20); print('kappa',k['lo'],k['status'])
print('slots',pk.check_slots(C,nat))
print('S',pk.S_of(inv['T'],inv['P']))
for t in ['0.001','0.0037','0.01','0.05','0.2','0.5','0.9']:
    print(t, pk.F_at(inv['T'],inv['P'],t))
nat0=pk.native_from_word(W); inv0=pk.invoice(ci,nat0); print('t7669 S',pk.S_of(inv0['T'],inv0['P']), [ (t,pk.F_at(inv0['T'],inv0['P'],t)) for t in ['0.001','0.0037','0.01']])

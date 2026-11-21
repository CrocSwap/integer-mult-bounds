from ls import *
from collections import Counter
import sys
setup(W); st=stays_of(W)
init=[SM_[x] for x in W['initial']]; fin=[SM_[x] for x in W['final']]
pos={}
for r in range(n):
    for k,(c,evs,_) in enumerate(st[r]):
        for i in evs: pos[(i,r)]=k
def ch(r): return tuple([dm(init[r])]+[dm(c) for c,_,_ in st[r]]+[dm(fin[r])])
def show(r):
    print('REG',r,kind(r),'chain',ch(r))
    for k,(c,evs,_) in enumerate(st[r]):
        items=[]
        for i in evs:
            e=P[i]
            if e[0]=='SCALE': items.append('scale%s'%e[2]); continue
            d,s_=e[1],e[2]
            if d==r: o=s_; t='in<'
            else: o=d; t='out>'
            if o>=n: items.append('%s O%d'%(t,o))
            else: items.append('%s %s%d[st%d/%d]%s'%(t,kind(o),o,pos[(i,o)],len(st[o]),e[3]))
        print('  stay',k,'dim',dm(c),'t=%d..%d'%(evs[0],evs[-1]),' | '.join(items[:14]),'...(%d)'%len(items) if len(items)>14 else '')
want=sys.argv[1] if len(sys.argv)>1 else '0,0,1,2,3,4,9,9'
want=tuple(int(x) for x in want.split(','))
c=0
for r in range(n):
    if kind(r)=='H' and ch(r)==want:
        show(r); c+=1
        if c>=2: break

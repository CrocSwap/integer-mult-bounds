"""Exact per-role invoices for one legal A2 rewrite (development)."""
from bisect import bisect_left, bisect_right
from collections import defaultdict

class Trace:
    def __init__(self, records, start, final, owned, distances):
        self.records,self.start,self.final,self.owned,self.distances=records,start,final,owned,distances
        n=len(start); rows=[1<<i for i in range(n)]
        self.positions=[[] for _ in range(n)]
        self.history=[([-1],[rows[i]]) for i in range(n)]
        self.requests=[[] for _ in range(n)]
        self.values=[]
        for k,e in enumerate(records):
            op,d=e[:2]
            self.positions[d].append(k)
            if op=='ADD':
                s,f=e[2:];self.positions[s].append(k)
                self.values.append((rows[d],rows[s]))
                if rows[s]:
                    self.requests[d].append((k,0,f,bool(rows[d])))
                    self.requests[s].append((k,0,f,True))
                rows[d]^=rows[s]
            else:
                if op not in ('INIT','ERASE') or d not in owned or (op=='INIT' and rows[d]):
                    raise ValueError('invalid owned reset')
                self.values.append((rows[d],0));rows[d]=0
                self.requests[d].append((k,0,e[2],None))
            self.history[d][0].append(k);self.history[d][1].append(rows[d])
        self.endpoint=rows
        for d,f in enumerate(final):
            if d in owned:
                if rows[d]:raise ValueError('owned final nonzero')
            else:self.requests[d].append((len(records),0,f,bool(rows[d])))
        self.keys=[[r[0] for r in req] for req in self.requests]
        self.base=[0]*9
        for d,req in enumerate(self.requests):self._price(self.start[d],req,self.base,1)

    def row(self,r,k):
        ids,vals=self.history[r]
        return vals[bisect_left(ids,k)-1]

    def _price(self,frame,requests,bill,sign):
        for _,_,target,nonzero in requests:
            if nonzero and frame!=target:
                if frame is None:raise ValueError('paid uninitialized role')
                bill[self.distances[frame][target]]+=sign
            frame=target

    def _replace(self,r,left,right,changed,bill,merge=False):
        req=self.requests[r];keys=self.keys[r]
        lo=bisect_left(keys,left);hi=bisect_right(keys,right)
        frame=req[lo-1][2] if lo else self.start[r]
        old=req[lo:hi]
        if merge:changed=sorted(old+changed)
        if hi<len(req):
            old=old+[req[hi]];changed=changed+[req[hi]]
        self._price(frame,old,bill,-1)
        self._price(frame,changed,bill,1)

    def delta(self,candidate):
        left,right,a,b,corrections=candidate
        ra,rb=self.positions[a],self.positions[b]
        relevant=sorted(set(ra[bisect_right(ra,left):bisect_left(ra,right)])|set(rb[bisect_right(rb,left):bisect_left(rb,right)]))
        changed={a:[],b:[]};extras=defaultdict(list)
        for k in relevant:
            op,d,s,f=self.records[k]
            if op!='ADD':raise ValueError('barrier in legal interval')
            oldd,olds=self.values[k]
            bval=self.row(b,k)
            source=olds^bval if s==a else olds
            destination=oldd^bval if d==a else oldd
            if source:
                if d in changed:changed[d].append((k,0,f,bool(destination)))
                if s in changed:changed[s].append((k,0,f,True))
            if k in corrections:
                _,cd,cs,cf=corrections[k]
                if d==b:
                    corrsource=olds
                    corrdest=self.row(a,k)^bval
                elif s==a:
                    corrsource=bval
                    corrdest=oldd^source
                    if not olds and bval:
                        extras[d].append((k,0,f,bool(oldd)))
                else:raise ValueError('unexpected A2 contact')
                if corrsource:
                    if cd in changed:changed[cd].append((k,1,cf,bool(corrdest)))
                    if cs in changed:changed[cs].append((k,1,cf,True))
        bill=[0]*9
        for r in (a,b):self._replace(r,left,right,changed[r],bill)
        for r,extra in extras.items():self._replace(r,left,right,extra,bill,True)
        return bill

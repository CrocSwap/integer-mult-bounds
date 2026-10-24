"""Paid signed exponential tables: bounded-word executable model, Apache-2.0.
Dugongue with substantial OpenAI Codex assistance.
Decimal is used only by check() as an independent reference.
"""
from decimal import Decimal,localcontext
from math import factorial
import json


def need(ok,why):
    if not ok:raise ValueError(why)


class ExpTable:
    def __init__(self,n,c=2,C=2):
        need(n>=1 and 1<=c<=8 and 1<=C<=8,'fixed template domain')
        self.ell=(n+2).bit_length();self.p=c*self.ell;self.C=C
        self.hbits=self.ell//4
        self.J=C*self.ell*(1<<self.hbits)
        self.degree=8*(c+4*C+64)+1
        self.P=self.p+4*C*self.ell+(self.J+1).bit_length()+self.degree.bit_length()+32
        self.S=1<<self.P;self.width=2*self.P+32
        self.limit=1<<self.width;self.operations=0;self.maximum_bits=0
        h=self.S>>self.hbits
        self.q=max(0,self.poly(h)-self.degree-2)
        self.rows=[self.S]
        for _ in range(self.J):
            self.rows.append(self.val(self.val(self.rows[-1]*self.q)//self.S))
        self.setup_operations=self.operations

    def val(self,x):
        need(abs(x)<self.limit,'word overflow')
        self.operations+=1;self.maximum_bits=max(self.maximum_bits,abs(x).bit_length());return x

    def poly(self,x):
        term=self.S;out=self.S
        for k in range(1,self.degree+1):
            term=self.val(self.val(term*x)//self.val(self.S*k))
            out=self.val(out-term if k&1 else out+term)
        return out

    def query(self,argument,fraction_bits):
        need(0<=fraction_bits<=self.P,'argument precision')
        x=self.val(abs(argument)<<(self.P-fraction_bits))
        need(x<=self.C*self.ell*self.S,'argument range')
        index=x>>(self.P-self.hbits)
        residual=self.val(x-(index<<(self.P-self.hbits)))
        value=self.val(self.val(self.rows[index]*self.poly(residual))//self.S)
        if argument>0:
            need(value>0,'reciprocal positivity')
            value=self.val(self.val(self.S*self.S)//value)
        shift=self.P-self.p
        return self.val((value+(1<<(shift-1)))>>shift)


def check():
    cases=queries=0;peak=0
    for n in (1,15,255,4095):
        for c,C in ((1,1),(2,2),(4,1)):
            tab=ExpTable(n,c,C)
            need((1<<tab.P)<=factorial(tab.degree+1)*(1<<(tab.hbits*(tab.degree+1))),
                 'independent symbolic Taylor tail control')
            bound=tab.C*tab.ell
            for num in (-16*bound,-13,0,7,16*bound):
                got=tab.query(num,4)
                with localcontext() as ctx:
                    ctx.prec=100
                    exact=(Decimal(num)/16).exp()
                    need(abs(Decimal(got)/(Decimal(2)**tab.p)-exact)<Decimal(2)**(-tab.p),'signed exponential error')
                queries+=1
            peak=max(peak,tab.maximum_bits);cases+=1
    try:ExpTable(15).query(10000,0)
    except ValueError:pass
    else:raise ValueError('out-of-range argument accepted')
    return dict(status='PASS',prepared_tables=cases,signed_queries=queries,
                maximum_bits=peak,out_of_range_control=True,
                scope='bounded-word signed exp tables; Decimal reference is check-only')


if __name__=='__main__':print(json.dumps(check(),indent=2))

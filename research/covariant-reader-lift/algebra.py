"""Exact full-field replay over Q[z]/(z^4-1), before native specialization."""
from fractions import Fraction as F

from source import need

ZERO=(F(0),)*4
ONE=(F(1),F(0),F(0),F(0))


def constant(x):return (F(x),F(0),F(0),F(0))


def shift(p,k):
    out=[F(0)]*4
    for i,x in enumerate(p):out[(i+k)%4]=x
    return tuple(out)


def add(row,other,c=F(1)):
    out=row.copy()
    for j,p in other.items():
        value=tuple(a+c*b for a,b in zip(out.get(j,ZERO),p))
        if value!=ZERO:out[j]=value
        else:out.pop(j,None)
    return out


def identity(n=704):return [{i:ONE} for i in range(n)]


def replay(word,initial=None,metrics=False):
    rows=identity() if initial is None else [row.copy() for row in initial]
    peak_l1=F(1);denominator=1;numerator=1;support=1
    for event in word:
        at=event[1];need(0<=at<704,"literal destination")
        if event[0]=="add":rows[at]=add(rows[at],rows[event[2]],F(event[3]))
        elif event[0]=="scale":rows[at]={j:tuple(F(event[2])*x for x in p) for j,p in rows[at].items()}
        else:
            need(event[0]=="z" and event[2] in (-1,1),"formal monomial power")
            rows[at]={j:shift(p,event[2]) for j,p in rows[at].items()}
        if metrics:
            values=[x for p in rows[at].values() for x in p]
            peak_l1=max(peak_l1,sum(map(abs,values)))
            denominator=max(denominator,max((x.denominator for x in values),default=1))
            numerator=max(numerator,max((abs(x.numerator) for x in values),default=0))
            support=max(support,len(rows[at]))
    if not metrics:return rows
    return rows,{"row_l1":str(peak_l1),"denominator":denominator,
                 "formal_numerator":numerator,"input_support":support}


def left(reader,operator):
    out=[]
    for row in reader:
        value={}
        for j,c in row.items():value=add(value,operator[j],c)
        out.append(value)
    return out


def reader_rows(reader):return [{j:constant(v) for j,v in row.items()} for row in reader]


def expected_reader(reader,order):
    rows=reader_rows(reader)
    return [{j:shift(p,1) for j,p in rows[i].items()} for i in order]


def encoded(rows):
    return [{str(j):[str(v) for v in p] for j,p in sorted(row.items())} for row in rows]

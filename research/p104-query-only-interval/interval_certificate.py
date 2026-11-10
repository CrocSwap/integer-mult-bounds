"""Independent exact interval matrices with unrestricted formal D monomials.

No predecessor arithmetic is imported. D powers are tuples of formal labels
with multiplicities retained. Prepared for @CubeJerry with substantial OpenAI
assistance. Apache-2.0.
"""
from fractions import Fraction
import hashlib
import json
from copy import deepcopy
from source_binding import need
from replacement import START, STOP, three_queries, to_basis, from_basis


def plus(a,b):
    out=dict(a)
    for key,(u,v) in b.items():
        x,y=out.get(key,(Fraction(0),Fraction(0)))
        value=(x+u,y+v)
        if value == (0,0):
            out.pop(key,None)
        else:
            out[key]=value
    return out


def factor(row,real=1,imag=0,power=0,labels=(),period=4):
    out={}
    real,imag=Fraction(real),Fraction(imag)
    for (source,q,ds),(a,b) in row.items():
        value=(a*real-b*imag,a*imag+b*real)
        key=(source,(q+power)%period,tuple(sorted(ds+tuple(labels))))
        if value != (0,0):
            out[key]=value
    return out


def matrix(word,n,period=4,projector_mutant=False):
    rows=[{(r,0,()):(Fraction(1),Fraction(0))} for r in range(n)]
    peak=n
    for event in word:
        need(event[0] == 'A', 'interval contains no HOST or B event')
        op,r=event[1:3]
        if op == 'ADD':
            rows[r]=plus(rows[r],factor(rows[event[3]],real=Fraction(event[4]),period=period))
        elif op == 'SCALE':
            rows[r]=factor(rows[r],real=Fraction(event[3]),period=period)
        elif op == 'SWAP':
            rows[r],rows[event[3]]=rows[event[3]],rows[r]
        elif op == 'QUERY':
            rows[r]=plus(rows[r],factor(rows[event[3]],power=event[4],period=period))
        elif op == 'QSELF':
            rows[r]=factor(rows[r],power=event[3],period=period)
        elif op == 'IDLE_ONE':
            rows[r]=factor(rows[r],labels=tuple(event[3]),period=period)
        elif op == 'LAMBDA':
            half=Fraction(1,2)
            s=0 if projector_mutant else event[3]
            rows[r]=plus(factor(rows[r],real=half,imag=s*half,period=period),
                         factor(rows[r],real=half,imag=-s*half,power=2,period=period))
        else:
            raise ValueError('unsupported local interval operation')
        peak=max(peak,sum(map(len,rows)))
        need(peak < 200000,'bounded local symbolic certificate')
    return rows,peak


def digest(rows):
    serial=[[[source,q,list(ds),str(a),str(b)] for (source,q,ds),(a,b) in sorted(row.items())]
            for row in rows]
    return hashlib.sha256(json.dumps(serial,separators=(',',':')).encode()).hexdigest()


def verify(caller,new):
    original=caller['events'][START:STOP]
    replacement=new['events'][START:START+223]
    need(new['events'][:START] == caller['events'][:START]
         and new['events'][START+223:] == caller['events'][STOP:],
         'all actual events outside interval unchanged')
    old,op=matrix(original,38)
    fresh,np=matrix(replacement,38)
    need(old == fresh, 'exact full separated interval on all independent input columns')
    core,cp=matrix(three_queries(0,1,2,3),4)
    target,_=matrix([['A','QSELF',0,-1],['A','QSELF',1,-1],['A','QUERY',2,3,-1]],4)
    need(core == target,'complete four-field gadget, including arbitrary workspace outputs')
    unit,_=matrix(to_basis()+from_basis(),38)
    identity,_=matrix([],38)
    need(unit == identity,'global even basis invertibility, including q=+/-i sectors')
    return dict(interval=[START,STOP],old_events=len(original),new_events=len(replacement),
        arbitrary_interval_inputs=38,formal_D_variables_retained='all; interval uses D9 only',
        D_exponents='unrestricted tuples, multiplicities preserved',
        q_relation='q^4=1',old_peak_terms=op,new_peak_terms=np,
        endpoint_terms=sum(map(len,old)),endpoint_sha256=digest(old),
        four_field_gadget_peak_terms=cp,four_field_gadget_endpoint_sha256=digest(core),
        basis_round_trip='identity over the full quotient, without division or sector restriction')


def controls(caller,new):
    original=caller['events'][START:STOP]
    replacement=new['events'][START:START+223]
    want,_=matrix(original,38)
    checks=[]
    def rejects(label,mutant,**kw):
        got,_=matrix(mutant,38,**kw)
        need(got != want,'negative-control discriminator failed: '+label)
        checks.append(label)
    z=deepcopy(replacement)
    at=next(i for i,e in enumerate(z) if e[1] == 'QUERY')
    z[at][-1]=1
    rejects('wrong_QUERY_orientation',z)
    z=deepcopy(replacement);z.pop(at)
    rejects('only_two_QUERY_calls',z)
    z=deepcopy(replacement)
    at=next(i for i,e in enumerate(z) if e == ['A','ADD',0,2,'-1'])
    z.pop(at)
    rejects('omitted_source_conjugation_correction',z)
    z=deepcopy(replacement)
    at=next(i for i,e in enumerate(z) if e[1] == 'QUERY')
    prior=max(i for i in range(at) if z[i][1] == 'LAMBDA')
    z.pop(prior)
    rejects('incomplete_t_scaling_or_source_restoration',z)
    z=deepcopy(replacement)
    di=next(i for i,e in enumerate(z) if e[1] == 'IDLE_ONE')
    z.insert(di,z[di][:])
    rejects('repeated_D9_is_not_idempotent',z)
    z=deepcopy(replacement);z.append(['A','ADD',37,0,'1'])
    rejects('cross_input_contamination',z)
    rejects('lambda_projection_zero_divisor_mutant',replacement,projector_mutant=True)
    wide_old,_=matrix(original,38,period=8)
    wide_new,_=matrix(replacement,38,period=8)
    need(wide_old != wide_new,'q^4 hypothesis discriminator')
    checks.append('missing_q_fourth_power_relation')
    return dict(rejected=checks,count=len(checks),method='exact formal coefficients; no sampled field values')

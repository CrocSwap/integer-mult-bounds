"""Standalone exact all-input compensated-retiming replay. Python 3 stdlib."""
from fractions import Fraction as Q
import json

def need(ok,message):
    if not ok: raise ValueError(message)

def evaluate(program, fields=6, width=2):
    size=fields*width
    rows=[[[Q(int(f*width+j==k)) for k in range(size)] for j in range(width)] for f in range(fields)]
    for g in program:
        tag=g[0]
        if tag=='add':
            _,d,s,a=g
            for j in range(width): rows[d][j]=[x+a*y for x,y in zip(rows[d][j],rows[s][j])]
        elif tag=='scale':
            _,d,a=g; rows[d]=[[a*x for x in r] for r in rows[d]]
        elif tag=='rotate':
            d=g[1]; rows[d]=[[-x for x in rows[d][1]],rows[d][0]]
        else: raise ValueError('Unknown operation')
    return rows

def retime(program,x=0,y=1,wrong_sign=False):
    first=program[0]
    need(first[:3]==('add',x,y),'Wrong initial update')
    a=first[3]; out=[]
    for g in program[1:]:
        if g[0]=='add':
            _,d,s,b=g
            need(s!=x,'An observable read of the delayed field is forbidden')
            need(d!=s,'Distinct ADD arguments required')
            out.append(g)
            if d==y: out.append(('add',x,s,(a*b if wrong_sign else -a*b)))
        else:
            need(g[1] not in (x,y),'Only additive changes to delayed/source fields allowed')
            out.append(g)
    out.append(('add',x,y,a))
    return out

def main():
    cases=0
    for a in [Q(-2),Q(-1),Q(1,2),Q(1),Q(2)]:
        for b in [Q(-1),Q(1,2),Q(1),Q(2)]:
            for c in [Q(-2),Q(-1,2),Q(1),Q(3)]:
                p=[('add',0,1,a),('rotate',2),('add',1,2,b),
                   ('add',0,4,c),('add',5,1,Q(2)),('scale',3,Q(-1,2)),
                   ('add',1,3,c),('rotate',4),('add',0,1,Q(1,4))]
                need(evaluate(p)==evaluate(retime(p)),'All-input identity failed')
                need(evaluate(p)!=evaluate(retime(p,wrong_sign=True)),'Wrong sign escaped detection')
                cases+=1
    bad=[('add',0,1,Q(1)),('add',2,0,Q(1)),('add',1,3,Q(1))]
    try: retime(bad)
    except ValueError: pass
    else: raise ValueError('Observable-read mutant was admitted')
    # The read restriction has mathematical content, not merely a parser rule.
    unsafe=[('add',2,0,Q(1)),('add',1,3,Q(1)),('add',0,3,Q(-1)),('add',0,1,Q(1))]
    need(evaluate(bad)!=evaluate(unsafe),'Unsafe-read counterexample vanished')
    print(json.dumps({'status':'PASS','all_input_cases':cases,'independent_columns_per_case':12,
        'unrelated_noncommuting_operators':True,'wrong_sign_controls':cases,
        'observable_read_rejected':True,'unsafe_read_counterexample':True},sort_keys=True))

if __name__=='__main__': main()

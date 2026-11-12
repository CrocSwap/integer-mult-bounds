"""Exact termwise instruction census; no observed timing fits."""
from pathlib import Path
import json
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import linear as m


def gamma_cost(n):
    return 47*n-30*n.bit_count()+33*n.bit_length()-42


def price(side,shape):
    f,r,p,s,w=shape
    v=2*w*r*p*s*(1 << (9*f))
    e=sum(2*n.bit_length()-1 for n in shape)
    volume=47*v+28*p+40*p*r+40*p*r*s-24*p*r*s*w+168*f+83
    cost=75+sum(gamma_cost(n) for n in shape)+5*e+3+volume+20*v+11+1
    for target,control in m.cnot_word(m.MATRICES[side]):
        high,low=min(target,control),max(target,control)
        a=p*(1 << ((high+1)*f-1));mid=1 << ((low-high)*f-1);b=2*w*r*s*(1 << ((8-low)*f))
        cost+=124*a+124*mid+47*b-36*p-24*r*s*w+28*r*s+10*r+180*f+44
        for j in range(f):
            cost+=58*v+78*a*mid+48*a+16
            if j+1<f:
                cost+=47*b+15*a+33
                b*=2;a//=2
        cost+=3*f+7*(a+mid+b)+15
    cost+=23*v+7*sum(shape)+120
    return cost,65536*(f*v+e+1)


def main():
    records=[]
    base=json.loads((HERE/'RESULT.json').read_text())
    for x in base['cases']:
        if x['kind'] in ('complete m9 f1','opaque sixth Gamma code'):records.append((x['side'],x['shape'],x['steps']))
    big=json.loads((HERE/'BIG-RESULT.json').read_text())
    for side in m.MATRICES:
        for label in ('f1','f2'):
            x=big['records'][side+'_'+label];records.append((side,x['shape'],x['steps']))
    for side,shape,actual in records:
        exact,bound=price(side,shape)
        if actual!=exact:raise ValueError('literal census '+str((side,shape,actual,exact)))
        if exact>bound:raise ValueError('complete envelope')
    abstract=0
    for f in (1,2,3,4,8,31,128):
        for shape in ((f,1,1,1,1),(f,2,3,5,7),(f,1,1 << 257,1,1),(f,1 << 129,1,1,1 << 63)):
            for side in m.MATRICES:
                exact,bound=price(side,shape)
                if exact>bound:raise ValueError('adversarial parameter price')
                abstract+=1
    print(json.dumps({'status':'PASS_EXACT_SELECTED_LINEAR_COST','physical_receipts_matched':len(records),'abstract_shapes_checked':abstract,
        'scope':'Exact helper-derived formula matches full physical traces; large shapes check arithmetic inequalities only, not payload execution.'},indent=2,sort_keys=True))


if __name__=='__main__':main()

"""Move opaque payload bits on complete GL2 low/high packet fibers."""
from fractions import Fraction as F
from itertools import product
import json
from qadic_streams import (Meter,Tape,need,low_update,add_high,scale_high,
                           completed_swap_oracle,permute_finite_classes)


def low_types(q):
    return [x for x in product(range(q),repeat=4) if (x[0]*x[3]-x[1]*x[2])%q]


def right_step(values,step,modulus):
    kind,dest,src,c=step;out=list(values)
    a=c.numerator*pow(c.denominator,-1,modulus)%modulus
    for row in range(2):
        i,j=2*row+dest,2*row+src
        if kind=="swap":out[i],out[j]=out[j],out[i]
        elif kind=="scale":out[i]=a*out[i]%modulus
        else:out[i]=(out[i]+a*out[j])%modulus
    return tuple(out)


def packet_step(source,q,width,types,step,outer,suffix,wrong_carry=False):
    """All rows use the old low GL type; then move the entire high packet."""
    kind,dest,src,c=step;high=q**(width-1);classes=len(types)
    index={x:i for i,x in enumerate(types)}
    newtypes=[right_step(x,step,q) for x in types]
    for row in range(2):
        i,j=2*row+dest,2*row+src
        if kind=="scale":
            lowrows=newtypes if wrong_carry else types
            carries=[low_update(0,x[i],c,q,True)[1] for x in lowrows]
            source=scale_high(source,high,c,lambda a:carries[(a//high**i)%classes],
                              outer*classes*high**i,high**(3-i)*suffix)
        else:
            left,right=sorted((i,j))
            before=outer*classes*high**left
            middle=high**(right-left-1);tail=high**(3-right)*suffix
            if kind=="swap":source=completed_swap_oracle(source,high,before,middle,tail)
            else:
                lowrows=newtypes if wrong_carry else types
                carries=[low_update(x[j],x[i],c,q)[1] for x in lowrows]
                source=add_high(source,high,c,lambda a:carries[(a//high**left)%classes],
                                before,middle,tail,j>i)
    return permute_finite_classes(source,outer,classes,high**4*suffix,
                                  [index[x] for x in newtypes])


def dense_expected(raw,q,width,types,word,outer,suffix):
    """Full modular column arithmetic, independent of the carry decomposition."""
    high=q**(width-1);mod=q**width;index={x:i for i,x in enumerate(types)}
    expected=[None]*len(raw)
    for pre,low_index in product(range(outer),range(len(types))):
        for coordinates in product(range(high),repeat=4):
            values=tuple(a+q*b for a,b in zip(types[low_index],coordinates))
            for step in word:values=right_step(values,step,mod)
            old=pre*len(types)+low_index;new=pre*len(types)+index[tuple(x%q for x in values)]
            for x,y in zip(coordinates,values):old=old*high+x;new=new*high+y//q
            expected[new*suffix:(new+1)*suffix]=raw[old*suffix:(old+1)*suffix]
    need(None not in expected,"dense oracle bijection")
    return expected


def check_packets():
    word=[("add",1,0,F(1,2)),("scale",0,0,F(-2)),("swap",0,1,F(1)),
          ("add",0,1,F(-1,2)),("add",1,0,F(1,4))]
    cases=[]
    for q,width in ((3,1),(3,2),(5,1)):
        types=low_types(q);outer,suffix=2,7
        size=outer*len(types)*q**(4*(width-1))*suffix
        raw=[((i//suffix)*17+3)>> (i%suffix)&1 for i in range(size)]
        meter=Meter();stream=Tape(meter,raw)
        for step in word:stream=packet_step(stream,q,width,types,step,outer,suffix)
        expected=dense_expected(raw,q,width,types,word,outer,suffix)
        need(stream.bits==expected,"complete GL low/high packet mismatch")
        need(expected!=raw,"nontrivial low-type packet route")
        need(len(meter.ordinary)==(6 if width>1 else 0),"ordinary calls independent of low-class count")
        cases.append({"q":q,"width":width,"low_GL_classes":len(types),"bits":size,
                      "ordinary_calls":len(meter.ordinary),"finite_low_permutations":5})
        if width>1:
            wrong=Tape(Meter(),raw)
            for step in word:wrong=packet_step(wrong,q,width,types,step,outer,suffix,True)
            need(wrong.bits!=expected,"updated-low carry mutant must fail")
    return {"status":"PASS_COMPLETE_GL2_PAYLOAD_PACKETS","cases":cases,
            "updated_low_carry_control":"REJECT"}


if __name__=="__main__":print(json.dumps(check_packets(),indent=2))

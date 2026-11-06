#!/usr/bin/env python3
"""Independent whole-Laurent-word audit for the five-projector bridge lemma."""
import itertools
import json

N=5
I=sum(1<<(i*N+i) for i in range(N))
DIAG=I
J=(1<<(N*N))-1
E=[1<<(i*N+i) for i in range(5)]
EDGE12=1<<1
EDGE34=1<<(2*N+3)


def require(ok,msg):
    if not ok:raise AssertionError(msg)

def mul(a,b):
    out=0
    for i in range(N):
        row=(a>>(i*N))&31; value=0
        for j in range(N):
            if row>>j&1:value^=(b>>(j*N))&31
        out|=value<<(i*N)
    return out

def rank(vectors):
    pivots={}
    for x in vectors:
        while x:
            k=x.bit_length()-1
            if k in pivots:x^=pivots[k]
            else:pivots[k]=x;break
    return len(pivots)

def word(order,negative_second_bridge=True):
    matrices=E[:4]+[J,J]
    exponents=[(0,1,0),(0,1,0),(0,0,1),(0,0,1),(1,0,0),(-1 if negative_second_bridge else 1,0,0)]
    out={(0,0,0):I}
    for call in order:
        p=matrices[call]; exponent=exponents[call]; new={}
        for key,matrix in out.items():
            new[key]=new.get(key,0)^mul(I^p,matrix)
            shifted=tuple(x+y for x,y in zip(key,exponent))
            new[shifted]=new.get(shifted,0)^mul(p,matrix)
        out={key:value for key,value in new.items() if value}
    return out


def run():
    off=lambda x:x&~DIAG
    quotient=[off(J),EDGE12,EDGE34]
    row_stars=[off(mul(E[i],J)) for i in range(4)]
    column_stars=[off(mul(J,E[i])) for i in range(4)]
    symmetric_stars=[a^b for a,b in zip(row_stars,column_stars)]
    require(rank(quotient)==3,'quotient generators independent')
    require(rank(quotient+symmetric_stars)==7,'four Ki independent in quotient')
    require(rank(quotient+row_stars+column_stars)==11,'eight ordered stars independent in quotient')
    require(rank(quotient+symmetric_stars+[off(mul(E[4],J)^mul(J,E[4]))])==7,'control: fifth star is dependent')
    expected={(0,1,0):E[0]^E[1],(0,0,1):E[2]^E[3],(0,0,0):E[4]}
    passed=0;rejected=0;off_edge_rejected=0
    allowed=DIAG|EDGE12|EDGE34
    for order in itertools.permutations(range(6)):
        actual=word(order)
        adjacent=abs(order.index(4)-order.index(5))==1
        require((actual==expected)==adjacent,'whole word agrees exactly with consecutive-bridge criterion')
        if adjacent:passed+=1
        else:
            rejected+=1
            require(any(matrix&~allowed for matrix in actual.values()),'nonconsecutive word has a forbidden endpoint entry')
            off_edge_rejected+=1
    require(passed==240 and rejected==480,'permutation counts')
    changed=word((4,5,0,1,2,3),negative_second_bridge=False)
    require(changed!=expected and any(matrix&~allowed for matrix in changed.values()),'control: consecutive but noncancelling bridge must fail full endpoint')
    print(json.dumps({'status':'PASS_INDEPENDENT_WHOLE_LAURENT_WORD_AUDIT','model':'F2[Z^3], exact integer exponent tuples, five scalar coordinates','relation_basis':['e0-e1','e2-e3','e4+e5'],'calls':6,'all_five_types_present':True,'permutations':720,'consecutive_bridge_words_passing':passed,'nonconsecutive_words_rejected':rejected,'forbidden_off_edge_endpoints':off_edge_rejected,'symmetric_star_quotient_rank':4,'ordered_star_quotient_rank':8,'controls':2,'scope':'Finite whole-word corroboration of the new written unbounded bridge-cancellation lemma; not a bounded-search proof of the universal statement.'},indent=2))

if __name__=='__main__':run()

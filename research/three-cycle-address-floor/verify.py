#!/usr/bin/env python3
"""Exact address exclusion and formal controls; uniform reduction is PROOF.md.
JoyboyBrian, substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
import hashlib
import itertools
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent

def need(ok,message):
    if not ok: raise ValueError(message)

def identity(n): return tuple(1<<i for i in range(n))
def add(matrix,gate):
    i,j=gate;n=len(matrix)
    need(0<=i<n and 0<=j<n and i!=j,'illegal coordinate CNOT')
    rows=list(matrix);rows[i]^=rows[j];return tuple(rows)
def product(a,b):
    need(len(a)==len(b),'matrix dimensions')
    out=[]
    for row in a:
        value=0
        for j in range(len(a)):
            if row>>j&1:value^=b[j]
        out.append(value)
    return tuple(out)
def inverse(matrix):
    n=len(matrix);rows=[x|(1<<(n+i)) for i,x in enumerate(matrix)]
    for j in range(n):
        candidates=[k for k in range(j,n) if rows[k]>>j&1]
        need(candidates,'singular matrix')
        k=candidates[0];rows[j],rows[k]=rows[k],rows[j]
        for k in range(n):
            if k!=j and rows[k]>>j&1:rows[k]^=rows[j]
    return tuple(x>>n for x in rows)
def apply_word(n,word):
    result=identity(n)
    for g in word:result=add(result,g)
    return result

def ball(n,radius):
    gates=[(i,j) for i in range(n) for j in range(n) if i!=j]
    words={identity(n):()};front={identity(n)};layers=[1]
    for _ in range(radius):
        following=set()
        for matrix in sorted(front):
            for gate in gates:
                target=add(matrix,gate)
                if target not in words:
                    words[target]=words[matrix]+(gate,);following.add(target)
        layers.append(len(following));front=following
    need(all(apply_word(n,w)==m for m,w in words.items()),'stored address words')
    return words,layers

def encode(value):return json.dumps(value,sort_keys=True,separators=(',',':'))
def digest(value):return hashlib.sha256(encode(value).encode()).hexdigest()

def matrix_xor(a,b):return tuple(x^y for x,y in zip(a,b))
def formal_product(a,b):
    out={}
    for g,x in a.items():
        for h,y in b.items():
            label=product(g,h);coefficient=product(x,y)
            out[label]=matrix_xor(out.get(label,(0,)*len(x)),coefficient)
    return {g:m for g,m in out.items() if any(m)}
def scalar(n,matrix):return {identity(n):matrix}
def paid(n,r,gate,u,v):
    need(0<u<1<<r and 0<v<1<<r and (u&v).bit_count()%2==1,'rank-one idempotent')
    N=tuple(v if u>>i&1 else 0 for i in range(r))
    label=add(identity(n),gate)
    result={identity(n):matrix_xor(identity(r),N),label:N}
    return {g:m for g,m in result.items() if any(m)}

def formal_controls():
    word=((0,1),(1,0),(0,1),(1,2),(2,1),(1,2))
    fixtures=[]
    for n,r in ((3,1),(4,3),(8,5)):
        cycle=apply_word(n,word)
        need(cycle==tuple([2,4,1]+[1<<i for i in range(3,n)]),'cycle orientation')
        E=tuple(1 if i==0 else 0 for i in range(r))
        expected={identity(n):matrix_xor(identity(r),E),cycle:E}
        expected={g:m for g,m in expected.items() if any(m)}
        current=scalar(n,identity(r))
        for gate in word:current=formal_product(paid(n,r,gate,1,1),current)
        need(current==expected,'six-call full formal endpoint')
        # Scalar conjugation produces dense projectors; scalar frames then undo it.
        B=identity(r)
        for i in range(1,r):B=add(B,(i,0))
        if r>1:B=add(B,(0,r-1))
        Bi=inverse(B);u=sum(((B[i]&1)!=0)<<i for i in range(r));v=Bi[0]
        dense=scalar(n,B)
        for gate in word:dense=formal_product(paid(n,r,gate,u,v),dense)
        dense=formal_product(scalar(n,Bi),dense)
        need(dense==expected,'free scalar frames and dirty restoration')
        inv_word=tuple(reversed(word));inv_target=apply_word(n,inv_word)
        need(product(cycle,inv_target)==identity(n) and cycle!=inv_target,'inverse cycle distinction')
        fixtures.append({'n':n,'R':r,'coefficient_terms':len(current),'dense_projector':[u,v],
                         'endpoint_sha256':digest(sorted(current.items()))})
    # Arbitrary mixing cannot create group support outside label subwords.
    n=r=3;labels=((0,1),(1,2),(2,0),(1,0));current=scalar(n,identity(r));subwords={identity(n)}
    couplings=((3,1),(6,2),(5,4),(7,1))
    for i,(label,(u,v)) in enumerate(zip(labels,couplings)):
        current=formal_product(paid(n,r,label,u,v),current)
        group=add(identity(n),label)
        subwords|={product(group,h) for h in subwords}
        frame=add(identity(r),(i%r,(i+1)%r))
        current=formal_product(scalar(n,frame),current)
        need(set(current)<=subwords,'formal subword support')
    # An actual nonzero formal element can vanish in the natural representation.
    gl2=[(a,b) for a in range(1,4) for b in range(1,4) if a!=b]
    total=(0,0)
    for g in gl2:total=matrix_xor(total,g)
    need(total==(0,0) and len(gl2)==6,'natural representation alias control')
    omitted=sum(apply_word(4,word[:i]+word[i+1:])!=(2,4,1,8) for i in range(6))
    need(omitted==6,'omitted upper-bound call')
    wrong=word[:-1]+((0,2),)
    need(apply_word(4,wrong)!=(2,4,1,8),'wrong final label')
    need(apply_word(4,word+((3,0),))!=(2,4,1,8),'unreturned address spectator')
    for gate in ((0,0),(4,0),(-1,0)):
        try:add(identity(4),gate)
        except ValueError:pass
        else:raise ValueError('illegal label accepted')
    return {'fixtures':fixtures,'support_word_calls':len(labels),'support_terms':len(current),
            'subword_elements':len(subwords),'omission_controls':omitted,
            'other_semantic_controls':6,'natural_alias_terms':len(gl2)}

def calculate():
    B,layers=ball(4,3);B2={m for m,w in B.items() if len(w)<=2};target=(2,4,1,8)
    need(layers==[1,12,96,542],'complete exact address layers')
    hits=[m for m in B if product(inverse(m),target) in B2]
    need(not hits,'three-cycle reached within five address calls')
    # Positive bridge control: a five-call endpoint must be detected.
    short=apply_word(4,((0,1),(1,0),(0,1),(1,2),(2,1)))
    short_hits=sum(product(inverse(m),short) in B2 for m in B)
    need(short_hits>0,'short target positive join')
    six_hits=sum(product(inverse(m),target) in B for m in B)
    need(six_hits>0,'six-call target reachability')
    return {'status':'PASS_THREE_CYCLE_ADDRESS_FLOOR','address_dimension_checked':4,
            'generators':12,'layers':layers,'ball_two':len(B2),'ball_three':len(B),
            'ball_three_sha256':digest(sorted(B)),'joins_through_five':len(B),
            'target_hits_through_five':len(hits),'six_call_joins':six_hits,
            'short_target_positive_joins':short_hits,'minimum':6,
            'uniform_scope':'one coordinate three-cycle; all finite n>=3 and R>=1 by PROOF.md',
            'controls':formal_controls()}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--emit',action='store_true');args=parser.parse_args()
    actual=calculate()
    if args.emit:print(json.dumps(actual,indent=2,sort_keys=True));return
    need(encode(actual)==encode(json.loads((HERE/'RESULT.json').read_text())),'receipt mismatch')
    print('PASS_THREE_CYCLE_ADDRESS_FLOOR minimum=6 GL4_ball3=651 five_call_hits=0')
if __name__=='__main__':main()

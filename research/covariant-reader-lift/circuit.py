"""Literal rank-zero source action: signed X permutation and a dirty helper chart.

The helper chart follows Richardson's dyadic-section construction, with a new
zero-frame section and an explicitly checked 28-operation basis factorization.
"""
from collections import Counter
from fractions import Fraction as F

from source import PIVOTS, Q, need


def plus(a,b,sign=1):
    need(a!=b and sign in (-1,1),"signed unit source ADD")
    return [("add",a,b,sign)]


def scale(a,value):
    need(value in (F(2),F(1,2),F(-1)),"dyadic scalar alphabet")
    return [("scale",a,str(value))]


def swap(a,b):
    return plus(a,b)+plus(b,a,-1)+plus(a,b)+scale(b,F(-1))


def invert(word):
    out=[]
    for event in reversed(word):
        if event[0]=="add":out.append(("add",event[1],event[2],-event[3]))
        elif event[0]=="scale":out.append(("scale",event[1],str(1/F(event[2]))))
        else:
            need(event[0]=="z","closed literal alphabet")
            out.append(("z",event[1],-event[2]))
    return out


def permute(fields,wanted):
    labels=list(fields);word=[]
    need(set(fields)==set(wanted),"complete literal field permutation")
    for i,source in enumerate(wanted):
        j=labels.index(source)
        if j!=i:
            word+=swap(fields[i],fields[j]);labels[i],labels[j]=labels[j],labels[i]
    need(labels==list(wanted),"literal permutation endpoint")
    return word


def helper_basis():
    a,b,c,d,e,f,g,h=PIVOTS
    word=plus(b,c,-1)+scale(a,F(2))+plus(a,b,-1)
    word+=scale(d,F(2))+plus(d,b)+scale(c,F(2))+plus(c,b)+scale(c,F(-1))
    word+=plus(c,a)+plus(c,d)+swap(a,d)+swap(b,d)
    word+=plus(f,e)+scale(e,F(2))+plus(e,f,-1)
    word+=plus(h,g)+scale(g,F(2))+plus(g,h,-1)
    word+=plus(a,f)+plus(a,h)+plus(b,e)+plus(b,g)
    need(len(word)==28,"literal helper basis length")
    return word


def construct(data):
    basis=helper_basis();load=[]
    for i,target in enumerate(PIVOTS):
        for j,value in sorted(data["reader"][i].items()):
            if j<224 or j in PIVOTS:continue
            need(value.denominator==1,"integer nonpivot helper load")
            need(data["word"]["start"][j]==0,"actual common-frame helper source")
            for _ in range(abs(value.numerator)):load+=plus(target,j,1 if value>0 else -1)
    need(len(load)==450,"complete dirty helper source loads")
    chart=basis+load
    cycle=permute(PIVOTS,[PIVOTS[i] for i in Q])
    helper=chart+cycle+[("z",i,1) for i in PIVOTS]+invert(chart)
    wanted=[None]*112
    for j,(i,sign) in enumerate(data["permutation"]):wanted[i]=j
    data_word=permute(tuple(range(112)),wanted)
    for j,(i,sign) in enumerate(data["permutation"]):
        if sign<0:data_word+=scale(i,F(-1))
    data_word += [("z",i,1) for i in range(112)]
    word=data_word+helper
    return dict(basis=basis,load=load,chart=chart,cycle=cycle,helper=helper,
                data=data_word,word=word,inverse=invert(word))


def invoice(word):
    kinds=Counter(event[0] for event in word)
    scales=Counter(event[2] for event in word if event[0]=="scale")
    scalar=kinds["add"]+kinds["scale"]
    # A signed unit complex ADD has retained real-component tariff8; each
    # doubling, halving or negation has tariff2. Address maps are separate.
    return {"events":len(word),"unit_ADD":kinds["add"],"scales":dict(sorted(scales.items())),
            "scalar_operations":scalar,"payload_monomials":kinds["z"],
            "real_scalar_primitives":8*kinds["add"]+2*kinds["scale"],
            "positive_rank_children":0,"CLEAR":0,"algebraic_scratch_fields":0}

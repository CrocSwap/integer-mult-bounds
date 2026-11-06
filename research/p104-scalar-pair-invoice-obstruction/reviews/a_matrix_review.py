#!/usr/bin/env python3
"""Independent finite-field corroboration of worker A's separated-pair proof.

No worker A implementation is imported. @CubeJerry/OpenAI; Apache-2.0.
"""
from itertools import product
from collections import Counter
import json

FIELD=3
def mm(a,b):return [[sum(x*y for x,y in zip(row,col))%FIELD for col in zip(*b)] for row in a]
def add(a,b):return [[(x+y)%FIELD for x,y in zip(ar,br)] for ar,br in zip(a,b)]
def neg(a):return [[(-x)%FIELD for x in row] for row in a]
def scale(a,t):return [[t*x%FIELD for x in row] for row in a]
def eye(n):return [[int(i==j) for j in range(n)] for i in range(n)]
def rank(a):
    a=[row[:] for row in a];out=0
    for j in range(len(a[0])):
        k=next((k for k in range(out,len(a)) if a[k][j]%FIELD),None)
        if k is None:continue
        a[out],a[k]=a[k],a[out];factor=pow(a[out][j],-1,FIELD)
        a[out]=[(factor*x)%FIELD for x in a[out]]
        for k in range(len(a)):
            if k==out:continue
            factor=a[k][j];a[k]=[(x-factor*y)%FIELD for x,y in zip(a[k],a[out])]
        out+=1
    return out
def require(ok,message):
    if not ok:raise ValueError(message)

def main():
    ident=eye(8);queries=[];prefix=[];b=ident
    for i in range(9):
        u=[[int(j==i)] for j in range(8)] if i<8 else [[(-(-1)**j)%FIELD] for j in range(8)]
        v=[[(int(i>j)-int(i<j))%FIELD for j in range(8)]]
        r=mm(u,v);queries.append((u,v,r));b=mm(add(ident,scale(r,-2)),b);prefix.append(b)
    require(b==scale(ident,-1),'canonical complete query endpoint')
    # Close the second pair directly using its actual query factors/prefix.
    u5,v5,_=queries[5];u6,v6,_=queries[6]
    image=[[u5[j][0],u6[j][0],mm(prefix[5],u5)[j][0]] for j in range(8)]
    rows=v5+v6+mm(v5,prefix[5])
    require(rank(image)==rank(rows)==3,'actual second pair hulls')
    vectors=list(product(range(FIELD),repeat=5));counts=Counter();cases=0
    for z in vectors:
        if sum(z)%FIELD!=1:continue
        for a in vectors:
            if sum(x*y for x,y in zip(a,z))%FIELD:continue
            p=[[0]*8 for _ in range(8)]
            for i in range(3):
                p[i][i]=1
                for j in range(5):p[i][j+3]=((-1)**i*a[j])%FIELD
            for i in range(5):
                for j in range(5):p[i+3][j+3]=z[i]
            require(mm(p,p)==p and rank(p)==4,'first pair idempotent rank')
            for i in (1,2):
                r=queries[i][2]
                require(mm(p,r)==mm(r,p)==r,'first pair two-sided compatibility')
                require(mm(p,prefix[i])==mm(prefix[i],p),'first pair actual prefix')
            contributions=[]
            for projection in (p,add(ident,neg(p))):
                a_closed=mm(projection,image);c_closed=mm(rows,projection)
                contributions.append(rank(a_closed)+rank(c_closed)-rank(mm(c_closed,a_closed)))
            bound=sum(contributions)
            require(bound>=5,'separated pair rank floor')
            counts[tuple(contributions)]+=1;cases+=1
    rank5_cases=0
    for z3 in range(FIELD):
        for s in range(FIELD):
            delta=(s+1)%FIELD
            if not delta:continue
            z4=(1-z3)%FIELD;z=[z3,z4,0,0,0];a=[z4,-z3,s,s,s]
            p=[[0]*8 for _ in range(8)]
            for i in range(3):
                p[i][i]=1
                for j in range(5):p[i][j+3]=((-1)**i*a[j])%FIELD
            for i in range(5):
                for j in range(5):p[i+3][j+3]=z[i]
            w=[[x%FIELD] for x in [s,-s,s]+z];c=[[x%FIELD for x in [1,1,1]+[a[j]+1 for j in range(5)]]]
            t=scale(mm(w,c),pow(delta,-1,FIELD));q=add(add(ident,neg(p)),t)
            require(mm(q,q)==q and rank(q)==5 and mm(p,q)==mm(q,p),'new rank-five formula')
            for i in (5,6):
                r=queries[i][2]
                require(mm(q,r)==mm(r,q)==r,'new second pair support')
                require(mm(q,prefix[i])==mm(prefix[i],q),'new second pair prefixes')
            endpoints=[]
            for stage,site in ((p,0),(q,8)):
                exclusive=add(stage,neg(t));u,v,r=queries[site]
                column=mm(exclusive,u);row=mm(v,exclusive);pairing=mm(row,column)[0][0]
                require(pairing!=0,'endpoint exclusive pairing')
                endpoint=add(t,scale(mm(column,row),pow(pairing,-1,FIELD)))
                require(mm(endpoint,endpoint)==endpoint and rank(endpoint)==2,'new endpoint rank')
                require(mm(endpoint,r)==mm(r,endpoint)==r,'new endpoint support')
                endpoints.append(endpoint)
            stages=[endpoints[0],p,q,endpoints[1]]
            for left in stages:
                for right in stages:require(mm(left,right)==mm(right,left),'four stage commutation')
            inventory={}
            for mask in range(16):
                joint=ident
                for j,stage in enumerate(stages):joint=mm(joint,stage if mask>>j&1 else add(ident,neg(stage)))
                size=rank(joint)
                if size:inventory[mask]=size
            require(inventory=={2:2,3:1,4:3,12:1,15:1},'new rank-five incidence')
            rank5_cases+=1
    result={'field':FIELD,'all_parameters':cases,'rank_five_complete_parameter_cases':rank5_cases,'split_bound_histogram':{str(key):value for key,value in sorted(counts.items())},'scope':'All F3 parameters only; universal field conclusion rests on the reviewed written proof.'}
    print(json.dumps(result,sort_keys=True))

if __name__=='__main__':main()

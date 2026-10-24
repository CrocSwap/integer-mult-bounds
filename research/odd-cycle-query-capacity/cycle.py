"""Compressed exact query factorization for every unequal odd-cycle mask.

JoyboyBrian; substantial OpenAI Codex assistance. Apache-2.0.
Credit Tekalign PR3362 and classical matching/vertex-cover methods.
"""

def need(ok,message):
    if not ok: raise ValueError(message)

def dimensions(values):
    need(type(values) in (list,tuple) and len(values)>=5 and len(values)%2==1,
         'odd cycle length at least five')
    need(all(type(x) is int and x>=0 for x in values),'nonnegative integer widths')
    return tuple(values)

def independent(values):
    d=dimensions(values)
    def path(start,stop):
        weights=[0,0];taken=[]
        for i in range(start,stop):
            take=weights[-2]+d[i]
            taken.append(take>weights[-1])
            weights.append(max(weights[-1],take))
        witness=[];j=stop-start-1
        while j>=0:
            if taken[j]:witness.append(start+j);j-=2
            else:j-=1
        return weights[-1],tuple(reversed(witness))
    omitted=path(1,len(d));weight,vertices=path(2,len(d)-1)
    included=(weight+d[0],(0,)+vertices)
    return max(omitted,included)

def minimum(values):
    d=dimensions(values)
    return max(independent(d)[0],(sum(d)+1)//2)

def construct(values):
    """Use logarithmically many greedy path matchings; never expand widths."""
    d=dimensions(values);n=len(d)
    def path(t):
        capacity=list(d);capacity[0]-=t;capacity[-1]-=t
        edge=[0]*n;edge[-1]=t
        for i in range(n-1):
            edge[i]=min(capacity[i],capacity[i+1])
            capacity[i]-=edge[i];capacity[i+1]-=edge[i]
        return sum(edge),edge,capacity
    low,high=0,min(d[0],d[-1]);evaluations=0
    while low<high:
        middle=(low+high)//2
        evaluations+=2
        if path(middle)[0]<path(middle+1)[0]:low=middle+1
        else:high=middle
    sharing,edge,private=path(low);evaluations+=1
    alpha,witness=independent(d)
    result=dict(dimensions=list(d),edge=edge,private=private,
                rank=sum(d)-sharing,alpha=alpha,independent=list(witness),
                path_evaluations=evaluations)
    validate(result)
    return result

def validate(recipe):
    d=dimensions(recipe['dimensions']);n=len(d)
    edge,private=recipe['edge'],recipe['private']
    need(type(edge) is list and type(private) is list and len(edge)==len(private)==n,
         'one edge and private count per cycle vertex')
    need(all(type(x) is int and x>=0 for x in edge+private),'integer channel counts')
    need(all(edge[i-1]+edge[i]+private[i]==d[i]for i in range(n)),
         'complete disjoint coordinate coverage')
    need(type(recipe['rank']) is int and recipe['rank']==sum(edge)+sum(private)==minimum(d),
         'sharp complete query capacity')
    witness=recipe['independent']
    need(type(witness) is list and all(type(i) is int and 0<=i<n for i in witness),
         'independent witness vertices')
    present=[False]*n
    for i in witness:
        need(not present[i],'distinct independent witness vertices')
        present[i]=True
    need(all(not present[(i+1)%n]for i in witness),'independent witness mask')
    need(type(recipe['alpha']) is int and sum(d[i]for i in witness)==recipe['alpha']==independent(d)[0],
         'sharp independent weight')
    return True

#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Compare the noncommutative two-row tariff with unrestricted shortest words."""
from itertools import product
import heapq
import json


def need(ok,message):
    if not ok:raise ValueError(message)


VALUES=list(product(range(2),repeat=3));INDEX={x:i for i,x in enumerate(VALUES)}
ONE=INDEX[(1,0,1)]
ADD=[[INDEX[tuple(a^b for a,b in zip(x,y))] for y in VALUES] for x in VALUES]
MUL=[[INDEX[(a*d,(a*e)^(b*f),c*f)] for d,e,f in VALUES] for a,b,c in VALUES]
PRINCIPAL=[frozenset(MUL[a][g] for a in range(8)) for g in range(8)]


def tariff(lam,prices):
    mu=prices[:2];c=prices[2:]
    ideal=frozenset(ADD[a][b] for a in PRINCIPAL[lam[0]] for b in PRINCIPAL[lam[1]])
    terms=[sum(mu[i] for i in range(2) if lam[i])]
    for i in range(2):
        j=1-i;terms.append(2*mu[i]+2*c[j])
        if ideal in PRINCIPAL:
            terms.append(mu[i] if not lam[j] else mu[i]+2*c[j] if lam[j] in PRINCIPAL[lam[i]] else mu[i]+2*c[j]+2*c[i])
    return min(terms)


def step(state,kind,i,coefficient):
    s=list(state)
    if kind=='P':
        s[3*i+2]=ADD[s[3*i+2]][coefficient]
    else:
        j=1-i
        for k in range(3):s[3*i+k]=ADD[s[3*i+k]][MUL[coefficient][s[3*j+k]]]
    return tuple(s)


def search(prices):
    start=(ONE,0,0,0,ONE,0)
    goals={(ONE,0,a,0,ONE,b):(a,b) for a,b in product(range(8),repeat=2)}
    dist={start:0};heap=[(0,start)];answers={};settled=0
    gates=[(kind,i,c,prices[i if kind=='P' else i+2])
           for kind in ('P','E') for i in range(2) for c in range(1,8)]
    while heap and len(answers)<64:
        cost,x=heapq.heappop(heap)
        if dist[x]!=cost:continue
        settled+=1
        if x in goals:answers[goals[x]]=cost
        for kind,i,c,price in gates:
            y=step(x,kind,i,c);new=cost+price
            old=dist.get(y)
            if old is None or new<old:
                dist[y]=new;heapq.heappush(heap,(new,y))
        need(len(dist)<=8**6,'finite formal-state capacity')
    need(len(answers)==64,'every demand reached')
    return answers,settled,len(dist)


def run():
    contexts=[(1,1,1,1),(1,9,1,1),(9,1,1,1),(4,5,2,3),(100,1000,1,1)]
    totals=states=comparisons=0
    for prices in contexts:
        actual,settled,seen=search(prices)
        for lam,value in actual.items():
            need(value==tariff(lam,prices),'unrestricted shortest word versus formula')
            comparisons+=1
        totals+=settled;states+=seen
    e11=INDEX[(1,0,0)];e12=INDEX[(0,1,0)]
    need(tariff((e11,e12),(100,1000,1,1))==202,'nonprincipal left-ideal tariff')
    need(e12 in {MUL[e11][a] for a in range(8)} and e12 not in PRINCIPAL[e11],'coefficient side matters')
    need(MUL[e11][e12]!=MUL[e12][e11],'noncommutative carrier')
    return dict(status='PASS_NONCOMMUTATIVE_TWO_ROW_TARIFF',price_contexts=len(contexts),
                demand_comparisons=comparisons,settled_states=totals,discovered_states=states,
                wrong_side_price_foil=202,no_new_kappa=True)


if __name__=='__main__':
    print(json.dumps(run(),sort_keys=True))

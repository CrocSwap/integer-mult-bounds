#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Check source-insertion counts over finite noncommutative rings."""
from collections import deque
from itertools import product
import json


def need(ok, message):
    if not ok:
        raise ValueError(message)


def ring(kind, p):
    width = 3 if kind == 'tri' else 4
    values = list(product(range(p), repeat=width)); index = {v:i for i,v in enumerate(values)}
    def multiply(x,y):
        if kind == 'full':
            a,b,c,d=x; e,f,g,h=y
            return (a*e+b*g,a*f+b*h,c*e+d*g,c*f+d*h)
        a,b,c=x[:3]; d,e,f=y[:3]
        z=(a*d,a*e+b*f,c*f)
        return z if kind == 'tri' else z+(x[3]*y[3],)
    add=[[index[tuple((a+b)%p for a,b in zip(x,y))] for y in values] for x in values]
    mul=[[index[tuple(a%p for a in multiply(x,y))] for y in values] for x in values]
    neg=[index[tuple(-a%p for a in x)] for x in values]
    one=index[(1,0,1) if kind=='tri' else (1,0,0,1) if kind=='full' else (1,0,1,1)]
    return dict(values=values,index=index,add=add,mul=mul,neg=neg,one=one,n=len(values))


def run_word(r,k,word):
    a=[[r['one'] if i==j else 0 for j in range(k)]+[0] for i in range(k)]
    for event in word:
        if event[0]=='P':
            _,i,c=event;a[i][-1]=r['add'][a[i][-1]][c]
        else:
            _,i,j,c=event;a[i]=[r['add'][x][r['mul'][c][y]] for x,y in zip(a[i],a[j])]
    return a


def run():
    contexts=[('tri',2,1),('tri',2,2),('tri',2,3),('tri',3,2),('full',2,2),('prod',2,2)]
    total=single=double=zero=orbits=0
    for kind,p,k in contexts:
        r=ring(kind,p); n=r['n'];add=r['add'];mul=r['mul'];neg=r['neg']
        principal=[frozenset(mul[a][g] for a in range(n)) for g in range(n)]
        def generated(lam):
            s={0}
            for x in lam:
                s={add[a][b] for a in s for b in principal[x]}
            return frozenset(s)
        reachable=set()
        for beta in range(1,n):
            start=(beta,)+(0,)*(k-1)
            if start in reachable:continue
            orbits+=1;reachable.add(start);queue=deque([start])
            while queue:
                x=queue.popleft()
                for i in range(k):
                    for j in range(k):
                        if i==j:continue
                        for c in range(1,n):
                            y=list(x);y[i]=add[y[i]][mul[c][y[j]]];y=tuple(y)
                            if y not in reachable:reachable.add(y);queue.append(y)
        for lam in product(range(n),repeat=k):
            ideal=generated(lam);is_principal=ideal in principal
            need((lam in reachable)==(any(lam) and is_principal),'orbit versus principal LEFT ideal')
            if not any(lam):
                word=[];zero+=1
            elif is_principal:
                chosen=None
                for aa in product(range(n),repeat=k-1):
                    beta=lam[0]
                    for a,x in zip(aa,lam[1:]):beta=add[beta][neg[mul[a][x]]]
                    if principal[beta]==ideal:chosen=(aa,beta);break
                need(chosen is not None,'finite-ring shortening')
                aa,beta=chosen
                rr=[next(c for c in range(n) if mul[c][beta]==x) for x in lam[1:]]
                cword=[('E',j,0,c) for j,c in enumerate(rr,1)]+[('E',0,j,c) for j,c in enumerate(aa,1)]
                inverse=[('E',i,j,neg[c]) for _,i,j,c in reversed(cword)]
                word=inverse+[('P',0,beta)]+cword;single+=1
            else:
                before=[('E',j,0,neg[x]) for j,x in enumerate(lam[1:],1)]
                after=[('E',i,j,neg[c]) for _,i,j,c in reversed(before)]
                word=before+[('P',0,r['one'])]+after+[('P',0,add[lam[0]][neg[r['one']]])];double+=1
            actual=run_word(r,k,word)
            expected=[[r['one'] if i==j else 0 for j in range(k)]+[lam[i]] for i in range(k)]
            need(actual==expected,'all original dirt and source columns')
            need(sum(e[0]=='P' and e[-1]!=0 for e in word)==(0 if not any(lam) else 1 if is_principal else 2),'exact nonzero insertion count')
            total+=1
    r=ring('tri',2);e11=r['index'][(1,0,0)];e12=r['index'][(0,1,0)]
    left=frozenset(r['add'][r['mul'][a][e11]][r['mul'][b][e12]] for a in range(r['n']) for b in range(r['n']))
    need(all(left!=frozenset(r['mul'][a][g] for a in range(r['n'])) for g in range(r['n'])),'left ideal nonprincipal')
    need(left==frozenset(r['mul'][e11][a] for a in range(r['n'])),'right ideal gives a false shortcut')
    need(r['mul'][e11][e12]!=r['mul'][e12][e11],'actual noncommutativity')
    return dict(status='PASS_FINITE_RING_INSERTIONS',contexts=len(contexts),demands=total,
                zero=zero,single=single,double=double,source_orbits=orbits,
                wrong_side_control=True,no_new_kappa=True)


if __name__=='__main__':
    print(json.dumps(run(),sort_keys=True))

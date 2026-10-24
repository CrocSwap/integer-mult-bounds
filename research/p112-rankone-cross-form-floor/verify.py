#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact finite premises/controls for PROOF.md, not a universal decoder search."""
import hashlib
import itertools
import json
from fractions import Fraction
from math import gcd
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

def need(ok, message):
    if not ok:
        raise ValueError(message)

def basis(rows):
    pivots = {}
    for x in rows:
        while x:
            k = x.bit_length() - 1
            if k in pivots:
                x ^= pivots[k]
            else:
                pivots[k] = x
                break
    return tuple(pivots.values())

def rank(rows):
    pivots = {}
    for source in rows:
        row = list(source)
        for k, old in sorted(pivots.items()):
            if row[k]:
                a, b = old[k], row[k]
                row = [a*x-b*y for x,y in zip(row,old)]
                g = 0
                for x in row:
                    g = gcd(g,x)
                if g:
                    row = [x//g for x in row]
        k = next((k for k,x in enumerate(row) if x),None)
        if k is not None:
            pivots[k] = row
    return len(pivots)

def bit(x,y):
    return (x & y).bit_count() % 2

def dot(x,y):
    return sum(a*b for a,b in zip(x,y))

def coordinate(i,n=8):
    return tuple(int(i==j) for j in range(n))

def support(x,labels,coeff):
    return basis(label for row,label in zip(x,labels) if dot(row,coeff))

def price(B,C,readers,sources):
    rows=[]
    for call,rs in enumerate(readers):
        for r in rs:
            row=[]
            for other,ss in enumerate(sources):
                for s in ss:
                    row.append(bit(r,s) if call==other else
                               bit(r,(B if call==0 else C)[0])*bit(s,(B if call==0 else C)[1]))
            rows.append(sum(v<<j for j,v in enumerate(row)))
    return len(basis(rows))

def endpoint(terms):
    return [[sum(a[i]*c[j] for a,c in terms) for j in range(16)] for i in range(16)]

def exact(terms):
    need(endpoint(terms)==[[int(i==j) for j in range(16)] for i in range(16)],'exact I16 endpoint')

def costs(data,B,C,terms):
    return [price(B,C,[support(data['X'],data['duals'],a[:8]),support(data['X'],data['duals'],a[8:])],
                  [support(data['X'],data['labels'],c[:8]),support(data['X'],data['labels'],c[8:])]) for a,c in terms]

def run():
    for item in json.loads((HERE/'SOURCES.json').read_text())['files']:
        if item['usage']=='input':
            need(hashlib.sha256((ROOT/item['path']).read_bytes()).hexdigest()==item['sha256'],'source pin '+item['path'])
    data=json.loads((ROOT/'research/p112-single-lift/reference-geometry.json').read_text())
    X=data['X']; need(len(X)==112 and all(len(x)==8 for x in X),'112x8 source')
    need([[sum(x[i]*x[j] for x in X) for j in range(8)] for i in range(8)]==[[56*int(i==j) for j in range(8)] for i in range(8)],'left inverse')
    for i in range(112):
        for j in range(112):
            need(dot(X[i],X[j])%2==0 and bit(data['duals'][i],data['labels'][j])==(1+dot(X[i],X[j])//2)%2,'actual label pairing')
    exceptional=[]; spaces=[]
    for labels in (data['duals'],data['labels']):
        exceptions={}; hist={}
        for h in range(1,512):
            rows=[x for x,l in zip(X,labels) if bit(h,l)]
            r=rank(rows); hist[r]=hist.get(r,0)+1
            if r<8:
                zeros=[i for i in range(8) if all(x[i]==0 for x in rows)]
                need(r==7 and len(zeros)==1,'coordinate kernel')
                need(zeros[0] not in exceptions,'distinct exception')
                exceptions[zeros[0]]=h
        need(hist=={8:503,7:8},'full support census')
        exceptional.append([exceptions[i] for i in range(8)])
        spaces.append([support(X,labels,coordinate(i)) for i in range(8)])
    rs,ss=exceptional; U,V=spaces; full=tuple(1<<i for i in range(9))
    need(all(bit(r,s)==1 for r in rs for s in ss),'all exceptional pairings one')
    need(all(len(basis(sum(bit(x,y)<<j for j,y in enumerate(v)) for x in u))==8 for u in U for v in V),'64 diagonal pairings')
    # All independent exceptional indices, including unequal ones: transfer zero.
    for r,t,a,b in itertools.product(rs,ss,rs,ss):
        need(bit(t,r) ^ (bit(r,b)&bit(t,a)) == 0,'mixed transfer')
    old=json.loads((ROOT/'research/p112-cross-form-rank-tradeoff/RESULT.json').read_text())['form_fixtures']['undecided_control']
    need(old['ranks']==[1,1] and old['support_minima']==[0,0], 'actual predecessor unresolved fixture')
    old_rows=[33,0,0,0,0,0,0,33,0]
    need(old['beta01_rows']==old['beta10_rows']==old_rows, 'original fixture rows')
    need(rs[0]==129 and ss[0]==33, 'original fixture mixed orientation')
    need(price((129,33),(129,33),[U[1],U[2]],[V[3],V[4]])==16, 'original fixture double rank16')
    B,C=(7,33),(9,289)
    need(B[0] not in rs and C[0] not in rs and B[1]==ss[0] and C[1]==ss[1],'genuine both-right residual fixture')
    # Source full must rule out price15; mixed-reader/full-source must rule out8.
    for a,b,c in itertools.product(range(8),repeat=3):
        need(price(B,C,[U[a],U[b]],[V[c],full])>=16,'double full source1')
        need(price(B,C,[U[a],U[b]],[full,V[c]])>=16,'double full source0')
        need(price(B,C,[U[a],U[b]],[(),full])>=9,'mixed reader full source')
    z=(0,)*8
    e=lambda i:coordinate(i)
    sub=lambda a,b:tuple(x-y for x,y in zip(a,b))
    add=lambda a,b:tuple(x+y for x,y in zip(a,b))
    neg=lambda a:tuple(-x for x in a)
    D0,D1,E0,E1=e(4),e(2),e(1),e(0)
    A0,A1=sub(D0,E0),sub(D1,E1); L0,L1=add(D0,E0),add(D1,E1)
    terms=[(A0+A1,D0+D1),(E0+neg(A1),L0+z),(neg(A0)+E1,z+L1),(A0+z,z+E1),(z+A1,E0+z)]
    terms += [(coordinate(k,16),coordinate(k,16)) for k in range(8) if k not in (1,4)]
    terms += [(coordinate(k+8,16),coordinate(k+8,16)) for k in range(8) if k not in (0,2)]
    exact(terms); bill=costs(data,B,C,terms)
    need(bill==[15,9,9,0,0]+[8]*12 and sum(bill)==129,'actual directed decoder bill')
    transposed=[(c,a) for a,c in terms]; exact(transposed)
    dual_data = dict(data, duals=data['labels'], labels=data['duals'])
    need(costs(dual_data,(C[1],C[0]),(B[1],B[0]),transposed)==bill,'both-left transpose control')
    scaled=[(tuple(3*x for x in a),tuple(Fraction(x,3) for x in c)) for a,c in terms]
    exact(scaled); need(costs(data,B,C,scaled)==bill,'nonunit scaling invariance')
    standard=[(coordinate(k,16),coordinate(k,16)) for k in range(16)]
    exact(standard); need(costs(data,B,C,standard)==[8]*16,'128 attainer')
    # Removing the mixed-term surcharge gives the forbidden relaxed bill127.
    need(sum([15,8,8,0,0]+[8]*12)==127,'relaxed count discriminator')
    broken=terms[:-1]
    need(endpoint(broken)!=endpoint(terms),'missing endpoint term detected')
    need(costs(data,B,C,[(e(0)+z,z+e(0))])==[0] and costs(data,B,C,[(e(0)+z,z+e(2))])==[1],'free-column discriminator')
    # Finite arithmetic control; universal implication is the written argument.
    exceptions=[]
    for n in range(16):
        delta=16-n
        for d in range(delta,n+1):
            for p in range(33):
                if p>=2*(delta-1) and 8*n+7*d+p<128:
                    exceptions.append([n,d,p])
    need(exceptions==[[15,1,0]],'only relaxed equality case')
    return {'status':'PASS','scope':'finite source premises and discriminators; universal result is PROOF.md',
            'reader_exceptions':rs,'source_exceptions':ss,'directed_forms':{'beta01':[33,33,33,0,0,0,0,0,0],'beta10':[289,0,0,289,0,0,0,0,0]},
            'predecessor_fixture':'rank1/minima0 but mixed exceptional orientation; double floor16',
            'exact_decoder_prices':bill,'exact_decoder_cost':129,'separate_attainer_cost':128,'count_exception':exceptions,
            'controls':['full-source double rank','full-source mixed-reader rank','unequal exceptional indices','transpose','nonunit rational scaling','missing endpoint term','wrong free column','relaxed127 bill']}

if __name__=='__main__':
    result=run()
    expected=HERE/'RESULT.json'
    recorded = json.loads(expected.read_text())
    need(json.dumps(result, sort_keys=True)==json.dumps(recorded, sort_keys=True),
         'recorded result differs in value or JSON type')
    print(json.dumps(result,indent=2,sort_keys=True))

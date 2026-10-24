#!/usr/bin/env python3
"""Small source-bound corroboration; the universal classification is in PROOF.md."""
import hashlib
import json
import sys
from fractions import Fraction as F
from itertools import product
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE))
import metric as m


def sha(raw):return hashlib.sha256(raw).hexdigest()
def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':'))
def equal(x,y):m.need(canonical(x)==canonical(y),'complete typed receipt mismatch')


def sources():
    manifest=json.loads((HERE/'SOURCES.json').read_text())
    data={}
    for row in manifest['files']:
        if row['usage']!='input':continue
        path=ROOT/row['path']
        raw=path.read_bytes()
        m.need(not path.is_symlink(),'source symlink')
        m.need(sha(raw)==row['sha256'],'source SHA256 '+row['path'])
        m.need(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==row['git_blob'],'source Git blob')
        data[row['path']]=raw
    return data


def reject(fn):
    try:fn()
    except ValueError:return
    raise ValueError('negative control accepted')


def dual(p,q,h):
    scale=m.pow2(h)
    return (tuple((r[0],r[1]*scale,r[2]) for r in p),
            tuple((r[0],r[1]/scale,r[2]) for r in q))


def positive_cases():
    primitive=[r for r in product(range(-2,3),repeat=3) if any(x%2 for x in r)]
    fixtures=[primitive,[(1,1,2),(1,-1,0)],[(1,1,0),(1,-1,0)],
              [(F(1,3),F(-1,5),F(2,7)),(F(1,3),F(1,5),0)],[(0,1,0)]]
    rows=[]
    for k in (-6,-2,0,2,6):
        for u in (F(1),F(5),F(9),F(1,5)):
            d=m.pow2(k)*u
            for index,p0 in enumerate(fixtures):
                # Preserve a known original unit-metric instance under dual scaling.
                p=tuple((F(r[0]),F(r[1])/m.pow2(k//2),F(r[2])) for r in p0)
                p,q=m.factors(p,d)
                order,labels=m.full_witness(p,d)
                m.need(len(order)==len(p) and m.accepts(p,q,order,labels),'positive full box')
                a,b,g=m.anchors(p,q)
                for h in (-3,0,4):
                    pp,qq=dual(p,q,h)
                    m.need(m.anchors(pp,qq)==(a,b,g) and m.matrix(pp,qq)==m.matrix(p,q),'dual original-anchor invariance')
                rows.append({'d':str(d),'fixture':index,'n':len(p),'order':list(order),
                             'labels':[list(x) for x in labels],'anchors':[list(a),list(b),g]})
    return rows


def negative_cases():
    rows=[]
    for k in (-5,-4,-1,0,1,2,5):
        for u in (F(1),F(3),F(5),F(7),F(1,3),F(3,5)):
            d=m.pow2(k)*u
            if m.classify(d):continue
            p,order,labels=m.obstruction(d)
            p,q=m.factors(p,d);a,b,g=m.anchors(p,q);mat=m.matrix(p,q)
            m.need(all(mat[i][i]>0 for i in range(len(p))),'positive diagonal')
            m.need(all(mat[i][j]==0 for i in range(3) for j in range(3) if i!=j),'orthogonal core')
            mask=b[0]|b[1]|b[2]
            m.need(mask.bit_count()==2 and all(a[i]&b[i] for i in range(len(p))),'rank obstruction with ties')
            m.need(len(order)==len(p)-1 and m.accepts(p,q,order,labels),'exact lower witness')
            rows.append({'d':str(d),'n':len(p),'box':len(order),'A':list(a),'B':list(b),'gamma':g,
                         'diagonal':[str(mat[i][i]) for i in range(len(p))]})
    return rows


def corroborate(data):
    # Execute only the pinned definition-level oracle, never its main or fixed-example suite.
    name='research/weighted-gram-box/verify.py'
    oracle={'__name__':'retained_weighted_oracle','__file__':str(ROOT/name)}
    exec(compile(data[name],str(ROOT/name),'exec'),oracle)
    rows=[]
    for d in (F(2),F(3)):
        p,_,_=m.obstruction(d);p,q=m.factors(p,d)
        a,b,g=oracle['anchors'](p,q)
        m.need((a,b,g)==m.anchors(p,q),'independent canonical anchors')
        tested,valid=oracle['enumerate_boxes'](oracle['matrix'](p,q),a,b)
        m.need(valid[-1]==0 and valid[-2]>0,'definition-level exact box')
        rows.append({'d':str(d),'tested':tested,'valid':valid})
    return rows


def controls():
    reject(lambda:m.classify(0));reject(lambda:m.classify(-1))
    reject(lambda:m.full_witness([(1,0,0),(2,0,0)],1))
    reject(lambda:m.full_witness([(1,0,1),(1,1,-1)],2))
    m.need(m.classify(F(5)) and m.classify(F(5,16)),'nonsquare positive metric')
    m.need(not m.classify(F(2)) and not m.classify(F(1,3)),'both complementary classes')
    p,q=m.factors([(1,1,2),(1,-1,0)],1)
    m.need(m.anchors(p,q)[:2]==((7,3),(3,3)),'unequal original anchors')
    # Collapsing the color partition puts a real zero inside F with same label.
    m.need(not m.accepts(p,q,(0,1),((7,1),(3,1))),'single-color mutant rejected')
    # Omitting the anchor-setting fourth row changes the original canonical box.
    p,_,_=m.obstruction(3);p,q=m.factors(p[:3],3)
    m.need(m.anchors(p,q)[:2] != ((3,3,3),(3,3,3)),'omitted anchor row is detected')
    reject(lambda:equal({'nested':[1]},{'nested':[1.0]}))
    reject(lambda:equal({'nested':[1]},{'nested':[True]}))
    return ['nonpositive metric','empty tie','outside positive class','nonsquare positive',
            'both negative classes','unequal anchors','collapsed coloring','omitted anchor row','float receipt','bool receipt']


def run(data):
    return {'status':'PASS_DIAGONAL_METRIC_FULL_BOX','criterion':'v2(d) even and odd unit 1 modulo4',
            'positive':positive_cases(),'negative':negative_cases(),'oracle':corroborate(data),'controls':controls(),
            'proof_sha256':sha((HERE/'PROOF.md').read_bytes()),'metric_sha256':sha((HERE/'metric.py').read_bytes()),
            'limits':'Universal theorem is written proof; finite cases do not establish it. No physical supplier or new kappa.'}


def main():
    data=sources()
    expected=None if '--emit' in sys.argv else json.loads((HERE/'RESULT.json').read_text())
    result=run(data)
    if expected is not None:equal(result,expected)
    if '--emit' in sys.argv:print(json.dumps(result,indent=2))
    else:print('PASS_DIAGONAL_METRIC_FULL_BOX',len(result['positive']),len(result['negative']),len(result['controls']))


if __name__=='__main__':main()

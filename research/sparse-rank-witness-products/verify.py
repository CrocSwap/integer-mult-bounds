#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Complete-certificate differential and rejection checks, not a rank shortcut.

Joseph Anglada with substantial OpenAI Codex assistance. Reference tool and
fixture credits remain with Ali Romman and Nick Petalas respectively.
"""
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256
from itertools import product
from pathlib import Path
import json
import random
import sys
import types
from unittest.mock import patch

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from fixtures import dense_fixture


def need(ok,message):
    if not ok:raise ValueError(message)


def load(name,path):
    module=types.ModuleType(name);module.__file__=str(path)
    exec(compile(path.read_bytes(),str(path),'exec',dont_inherit=True,optimize=0),module.__dict__)
    return module


def engines():
    rows=json.loads((HERE/'SOURCES.json').read_bytes())['files']
    for name,path in [('scripts/certify_rational_rank.py',HERE/'baseline.py'),
                      ('research/integer-rank-product-checks/fixtures.py',HERE/'fixtures.py'),
                      ('scripts/compare_recursive_invoices.py',ROOT/'scripts/compare_recursive_invoices.py')]:
        expected=next(r['sha256'] for r in rows if r['path']==name)
        need(sha256(path.read_bytes()).hexdigest()==expected,'source drift: '+name)
    helper='compare_recursive_invoices';previous=sys.modules.get(helper)
    sys.modules[helper]=load(helper,ROOT/'scripts/compare_recursive_invoices.py')
    try:
        return load('reference',HERE/'baseline.py'),load('candidate',ROOT/'scripts/certify_rational_rank.py')
    finally:
        if previous is None:sys.modules.pop(helper,None)
        else:sys.modules[helper]=previous


def problem(a):return {'schema':'rational-rank-problem/v1','matrix':a}


def rejects(action):
    try:action()
    except (ValueError,TypeError,KeyError,ZeroDivisionError):return True
    return False


def main():
    before,after=engines();count=0;digest=sha256();rng=random.Random(20261107)
    cases=[problem([[int(i==j) for j in range(64)] for i in range(64)]),
           dense_fixture(),problem([[0]*9 for _ in range(7)]),
           problem([[0,0,0,0],[0,0,2,1],[0,3,0,2],[0,6,4,6]])]
    for values in product((0,1),repeat=9):
        cases.append(problem([list(values[i:i+3]) for i in (0,3,6)]))
    for _ in range(80):
        m,n=rng.randrange(1,9),rng.randrange(1,9)
        cases.append(problem([[str(Q(rng.randrange(-8,9),rng.randrange(1,12))) for _ in range(n)] for _ in range(m)]))
    for value in cases:
        a,b=before.certify(value),after.certify(value)
        need(a==b,'complete certificate changed')
        need(before.verify(value,b) and after.verify(value,a),'cross-check failed')
        digest.update(json.dumps(b,sort_keys=True,separators=(',',':')).encode());count+=1
    products=0
    for _ in range(70):
        m,k,n=(rng.randrange(0,8) for _ in range(3))
        a=[[Q(rng.choice((0,0,0,-2,1,3)),rng.randrange(1,10)) for _ in range(k)] for _ in range(m)]
        b=[[Q(rng.choice((0,0,0,-1,1,2)),rng.randrange(1,10)) for _ in range(n)] for _ in range(k)]
        expected=[[sum((a[i][t]*b[t][j] for t in range(k)),Q(0)) for j in range(n)] for i in range(m)]
        need(after._product(a,b,m,k,n)==expected,'rational product changed')
        need(after._product_equal(a,b,expected,m,k,n),'exact product rejected')
        if m and n:
            bad=deepcopy(expected);bad[-1][-1]+=Q(1,1009)
            need(not after._product_equal(a,b,bad,m,k,n),'false product accepted')
        products+=1
    # Actual denominator growth past the retained threshold, and forced fallback.
    a=[[Q(1,2**5500),Q(1,3**3500),Q(1,5**2400)]];b=[[Q(1)],[Q(-1)],[Q(2)]]
    need(after._scaled_rows(a) is None,'large-denominator control missed threshold')
    expected=[[sum((a[0][i]*b[i][0] for i in range(3)),Q(0))]]
    need(after._product(a,b,1,3,1)==expected,'large-denominator fallback changed')
    need(after._product_equal(a,b,expected,1,3,1),'fallback predicate changed')
    with patch.object(after,'MAX_PRODUCT_SCALE_BITS',0):
        need(after.certify(cases[3])==before.certify(cases[3]),'forced fallback certificate changed')
    value=problem([[1,0,1],[0,1,1],[1,1,2]]);good=before.certify(value);controls=0
    for field in ('minor_inverse','coefficients','right_kernel','left_kernel'):
        bad=deepcopy(good);bad[field][0][0]=str(Q(bad[field][0][0])+1)
        need(rejects(lambda:after.verify(value,bad)),'corrupt '+field+' accepted');controls+=1
    for matrix in ([],[[]],[[True]],[[0.1]],[['1/1000000001']],[[0]*65]):
        need(rejects(lambda:after.certify(problem(matrix))),'invalid matrix accepted');controls+=1
    original=after._product
    def wrong(*args):
        result=original(*args)
        if result and result[0]:result[0][0]+=1
        return result
    with patch.object(after,'_product',wrong):
        need(rejects(lambda:after.certify(value)),'producer stopped checking its own certificate')
    print(json.dumps({'status':'PASS_SPARSE_RANK_WITNESS_PRODUCTS','complete_equal_certificates':count,
                      'product_shapes':products,'rejection_controls':controls,
                      'certificate_digest':digest.hexdigest(),'new_kappa':None},sort_keys=True))


if __name__=='__main__':main()

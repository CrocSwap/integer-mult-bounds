"""Exact 8x8 finite profile-menu comparison; no unrestricted optimum claim."""
import argparse,hashlib,itertools,json,contextlib,io,tempfile
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter
from math import comb
from bindings import refine,arithmetic
HERE=Path(__file__).resolve().parent
CHOICES=[''.join(x) for x in itertools.product('cr',repeat=3)]

def profile(a,b):
    axes=[json.loads((HERE/f'menu/{c}-{h}.json').read_text()) for h,c in ((23,a),(25,b))]
    N=comb(23,3)*comb(25,3);W=2*N+sum(N//x['profile']['v']*x['profile']['R'] for x in axes)
    rows=Counter({1:19*N,21:2*N,17:2*N,481:2*N})
    for x in axes:
        p=x['profile'];h=p['h'];rep=N//p['v'];bank=rep*p['R']
        assert p['crt_disagreements']==0 and p['blocks'][0]==p['blocks'][h]==0
        assert sum(t*n for t,n in enumerate(p['blocks']))==h*p['R']+h*(h-1)
        rows.update({t:n*rep for t,n in enumerate(p['blocks']) if t and n})
        rows.update({h:bank,575-2*h:bank});rows.update({1:2*N,h-2:2*N})
    assert sum(t*n for t,n in rows.items())==575*W-1846900
    return W,rows

def build():
    d=10**18;results=[]
    bridge=json.loads((HERE/'comparisons/pr71.json').read_text())['finite_bridge']
    for a,b in itertools.product(CHOICES,repeat=2):
        W,rows=profile(a,b);lo,hi=1,refine.floor_scaled(Q(717,10**7),d)
        while lo+1<hi:
            mid=(lo+hi)//2;r=refine.exact_moment(575,W,rows,Q(mid,d))
            if r['upper']<1:lo=mid
            elif r['lower']>1:hi=mid
            else:raise ArithmeticError('Inconclusive exact menu enclosure')
        saving=Q(lo,d);lower=refine.exact_moment(575,W,rows,Q(hi,d))['lower'];upper=refine.exact_moment(575,W,rows,saving)['upper']
        assert upper<1<lower
        bridge['bit']['W']=W;assembled=refine.assemble(bridge,saving,Q(1,10**12),d)
        results.append(dict(h23=a,h25=b,W=W,bit_saving=saving,next_bit_saving=Q(hi,d),accepted_upper=upper,rejected_lower=lower,kappa=assembled['kappa']))
        print('SCREEN',a,b,str(assembled['kappa']),flush=True)
    results.sort(key=lambda x:(x['kappa'],x['bit_saving']),reverse=True)
    best=results[0]
    for row in results:
        W,children=profile(row['h23'],row['h25'])
        row['lower_at_selected_saving']=refine.exact_moment(575,W,children,best['bit_saving'])['lower']
        if row is not best:assert row['lower_at_selected_saving']>1,'Menu winner not strictly separated'
    paths=sorted((HERE/'menu').glob('*.json'))
    return arithmetic.js(dict(scope='Exact maximum among 64 frozen whole-profile choices at 1e18 grid; every nonselected profile strictly rejected at selected saving; no broader optimum claimed',
        choices=CHOICES,selected={'23':best['h23'],'25':best['h25']},grid_denominator=d,
        profile_source_hashes={str(p.relative_to(HERE)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},results=results))

def check():
    ledger=json.loads((HERE/'menu-ledger.json').read_text());rows=ledger['results'];d=ledger['grid_denominator']
    assert d==10**18 and ledger['choices']==CHOICES
    assert len(rows)==64 and {(x['h23'],x['h25']) for x in rows}==set(itertools.product(CHOICES,repeat=2))
    for name,digest in ledger['profile_source_hashes'].items():
        assert hashlib.sha256((HERE/name).read_bytes()).hexdigest()==digest
    chosen=next(x for x in rows if (x['h23'],x['h25'])==(ledger['selected']['23'],ledger['selected']['25']))
    bridge=json.loads((HERE/'comparisons/pr71.json').read_text())['finite_bridge']
    for row in rows:
        W,children=profile(row['h23'],row['h25']);assert W==row['W']
        a=Q(row['bit_saving']);n=Q(row['next_bit_saving']);assert n==a+Q(1,d)
        upper=refine.exact_moment(575,W,children,a)['upper'];lower=refine.exact_moment(575,W,children,n)['lower']
        assert upper==Q(row['accepted_upper']) and lower==Q(row['rejected_lower']) and upper<1<lower
        bridge['bit']['W']=W;assembled=refine.assemble(bridge,a,Q(1,10**12),d)
        assert assembled['kappa']==Q(row['kappa']) and Q(row['kappa'])<=Q(chosen['kappa'])
        strict=refine.exact_moment(575,W,children,Q(chosen['bit_saving']))['lower']
        assert strict==Q(row['lower_at_selected_saving'])
        if row is not chosen:assert strict>1
    return ledger

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--record',action='store_true');a=p.parse_args();result=build() if a.record else check()
    path=HERE/'menu-ledger.json'
    if a.record:path.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    else:assert result==json.loads(path.read_text()),'Menu ledger changed'
    print('PASS 64 exact combinations; selected '+str(result['selected']),flush=True)

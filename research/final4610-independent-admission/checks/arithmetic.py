"""Independent complete directed moment/outer checks; no expected-PASS inheritance.
R1 engines by OpenAI Codex; construction and formula sources retain their credit.
Apache-2.0.
"""
from fractions import Fraction as F
from copy import deepcopy
from . import moments as M, outer,source

def run(invoice):
    d=source.js('research/kappa-round6-compiler-tightening-20261022/ARITHMETIC.json')
    ctrl=source.js('research/joint-helper-lattice/CONTROLLER.json')
    T,P=M.reconstruct(ctrl,M.dictint(invoice['local_paid']),M.dictint(invoice['local_helpers']))
    assert T==M.dictint(invoice['targets']) and P==M.dictint(invoice['paid'])
    assert T==M.dictint(d['targets']) and P==M.dictint(d['paid'])
    ks=['.00302015','.0030217758','.00302177581','.00302177587077','.00302177587078']
    margins={k:M.decimal(M.margin(T,P,k)) for k in ks}
    assert M.margin(T,P,ks[-2])[0]>0>M.margin(T,P,ks[-1])[1]
    assert M.derivative_interval(T,P,F(0),F('.004'))[1]<0
    strict=M.strictification(T,P,'.00302177581',{})
    assert strict['same_model_moment_and_tail_screen']
    old=source.js('research/joint-helper-lattice/RESULT.json');assert d['ordinary_BIT']==old['ordinary_BIT'],'unchanged source-bound ordinary BIT interface'
    oT,oP=M.reconstruct(ctrl,M.dictint(old['local_paid']),M.dictint(old['local_helpers']))
    assert oT==T and oP==M.dictint(old['paid']) and oP!=P
    assert M.margin(T,oP,'.0030201659770')[0]>0>M.margin(T,oP,'.0030201659771')[1]
    assert M.margin(T,oP,'.0030217758')[1]<0
    bill_delta={str(r):P.get(r,0)-oP.get(r,0) for r in set(P)|set(oP) if P.get(r,0)!=oP.get(r,0)}
    assert bill_delta
    controls={}
    bad=P.copy();bad[1]+=1
    assert M.margin(T,bad,'.0030217758')[1]<0;controls['one_unfunded_H1_rejected']=True
    bad=P.copy();bad[8]-=18*8
    assert M.margin(T,bad,'.0030217758')[0]>M.margin(T,P,'.0030217758')[1]
    controls['owned_centers_affect_complete_margin']=True
    q=outer.evaluate(outer.parameters('.0030217758','.00302177581'))
    assert q['all_positive']
    for group in ['margins','strict_checks','functional_checks']:
        assert q[group]=={n:F(v) for n,v in d['outer'][group].items()}
    for name,patch in [('old_BIT',{'bit_saving':F('.0027')}),('closed_uniform',{'complex_uniform_saving':q['parameters']['b']}),('unfunded_endpoint',{'kappa':F('.00302177581')}),('closed_epsilon',{'epsilon':F(1)})]:
        z=outer.evaluate(q['parameters']|patch);assert not z['all_positive'];controls[name]=[n for n,v in z['strict_checks'].items() if v<=0]
    # Exact identities, separately from source target enclosures.
    for r in [1,2,3,4,8,20,145]:
        for k,want in [(F(0),r),(F(1),1)]:
            lo,hi=M.power(r,k);assert lo<=want*M.S<=hi
    for r,want in [(4,2),(9,3),(16,4),(64,8)]:
        lo,hi=M.power(r,F(1,2));assert lo<=want*M.S<=hi
    return {'status':'PASS_INDEPENDENT_COMPLETE_DIRECTED_MOMENTS_AND_OUTER','margins':margins,'strictification':strict,'paid_delta_over_selected4470':bill_delta,'selected4470_unfunded_at_candidate':True,'outer':outer.encode(q),'semantic_controls':controls,'source_receipt_used_as_expected_pass':False}

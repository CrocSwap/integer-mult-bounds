#!/usr/bin/env python3
"""Adversarial checks and exact upstream adaptation audit for the selected witness."""
import argparse,json,sys
from pathlib import Path
from fractions import Fraction as Q
from copy import deepcopy
if sys.flags.optimize:raise ValueError('Assertions must remain enabled')
sys.dont_write_bytecode=True
import certificate as c
import balanced_stopped as balanced
import interval_moment as intervals
HERE=Path(__file__).resolve().parent

def adaptation():
    s=(HERE/'balanced_stopped.py').read_text();s=s[s.index('"""Exact, import-safe balanced'):]
    replacements=[
    ('def validate_bridge(finite_bridge, ordinary_leaf):','def validate_bridge(finite_bridge):'),
    ("    for name in ('bit_coarse', 'complex', 'ordinary_leaf'):\n        data = ordinary_leaf if name == 'ordinary_leaf' else finite_bridge[name]", "    for name in ('bit', 'complex'):\n        data = finite_bridge[name]"),
    ("    leaf_degree = result['ordinary_leaf']['halving_degree']*result['ordinary_leaf']['wire_bits']\n    require(integer(finite_bridge['ordinary_leaf_row_degree']) == leaf_degree,\n            'ordinary leaf stock missing or stale')\n    coefficient = sum(result[name]['halving_degree']*result[name]['wire_bits']\n                      for name in ('bit_coarse', 'complex', 'ordinary_leaf'))", "    coefficient = sum(result[name]['halving_degree']*result[name]['wire_bits']\n                      for name in ('bit', 'complex'))"),
    ('def assembly(finite_bridge, ordinary_leaf, a_bit, kappa,','def assembly(finite_bridge, a_bit, kappa,'),
    ('    f = validate_bridge(finite_bridge, ordinary_leaf)','    f = validate_bridge(finite_bridge)'),
    ('def cutoffs(finite_bridge, ordinary_leaf, result):','def cutoffs(finite_bridge, result):'),
    ("    largest = max(f[name]['m'] for name in ('bit_coarse','complex','ordinary_leaf'))", "    largest = max(f['bit']['m'],f['complex']['m'])")]
    for old,new in replacements:c.check(old in s,'Adapter normalization hook missing');s=s.replace(old,new)
    c.check(s==(HERE/'references/pr104/balanced_assembly.py').read_text(),'Unreviewed adapter difference')
    return True

def validate(raw,reference=None):
    c.no_floats(raw);j=c.exact(raw);f=j['finite_bridge'];old=j['ordinary_leaf_bridge'];p=j['profile'];k=Q(j['kappa']);a=Q(j['assembly_bit']);b=Q(j['complex_saving']);beta=Q(j['beta']);eta=Q(j['eta'])
    c.check(j['source_sha256']==c.source_hashes(),'Arithmetic source pins changed')
    c.profile(p);c.profile(j['bit_profile']);balanced.validate_bridge(f,old);adaptation()
    controls=[]
    def rejects(name,fn):
        try:fn()
        except (ValueError,balanced.InvalidAssembly,KeyError):controls.append(dict(name=name,rejected=True))
        else:raise ValueError('Adverse control accepted: '+name)
    mutations=[('missing old stock',lambda x:x.pop('ordinary_leaf_row_degree')),('zero old stock',lambda x:x.update(ordinary_leaf_row_degree=0)),('two-stock coefficient',lambda x:x['rows'].update(coefficient=x['rows']['coefficient']-252,degree_gap=x['rows']['degree_gap']+Q(51*252,25))),('stale coarse child',lambda x:x['bit_coarse'].update(maxchild=527)),('stale scalar charge',lambda x:x['complex'].update(scalar_group_upper=x['complex']['scalar_group_upper']-1)),('zero scalar charge',lambda x:x['complex'].update(scalar_group_upper=0)),('stale C0',lambda x:x['semantic'].update(C0=x['semantic']['C0']-1)),('insufficient row stock',lambda x:x['rows'].update(degree=1,degree_gap=Q(1)-Q(51,25)*x['rows']['coefficient'],suffix_slope=4))]
    for name,mut in mutations:
        x=deepcopy(f);mut(x);rejects(name,lambda:balanced.validate_bridge(x,old))
    rejects('zero stopped leaf gap',lambda:balanced.assembly(f,old,(1-beta)*b,k,beta=beta,h=eta,a_complex=b))
    rejects('next kappa',lambda:balanced.assembly(f,old,a,k+Q(1,10**18),beta=beta,h=eta,a_complex=b))
    rejects('old prefix at selected parameters',lambda:balanced.assembly(f,old,a,k,beta=beta,h=eta,a_complex=b,original_prefix=True))
    x=deepcopy(p);x['child_multiplicities']['1']-=1;rejects('unpaid singleton deletion',lambda:intervals.prepare(x))
    for name,x in [('top float',0.125),('nested float',{'profile':{'seconds':0.125}}),('list float',{'items':[{'x':0.125}]})]:rejects(name,lambda:c.no_floats(x))
    x=deepcopy(p);x['W']=str(x['W']);rejects('noninteger width',lambda:c.profile(x))
    x=deepcopy(p);x['h']+=1;rejects('inconsistent two-factor dimensions',lambda:c.profile(x))
    x=deepcopy(p);x['child_multiplicities']['1']=1.5;rejects('floating child count',lambda:c.profile(x))
    x=deepcopy(p);x['discovery']={'seconds':0.125};c.check(c.profile(x)==p,'Discovery metadata leaked into canonical profile')
    terms=[]
    for x in (f['bit_coarse'],f['complex'],old):
        m,r,d=x['m'],x['maxchild'],x['halving_degree'];c.check(m**d>2*r**d and (d==1 or m**(d-1)<=2*r**(d-1)),'Nonminimal halving degree');c.check(x['wire_bits']==x['W'].bit_length(),'Wire bitlength');terms.append(d*x['wire_bits'])
    c.check(terms==[9909,5400,252] and sum(terms)==f['rows']['coefficient']==15561,'All three row factors')
    q=a*(1-2*eta);eps=(1-eta)/(1+q);g=eps*q;cc=q+eta/4
    c.check(1-eps-g==eta and 1-eps*(1+cc)==eta-eps*eta/4>0,'Balanced identities')
    c.check(k<g<k+Q(1,10**18),'Selected adjacent kappa');bn=Q(j['next_complex_rejected']);cap=min(Q(j['actual_bit_saving']),bn)/(1+min(Q(j['actual_bit_saving']),bn));c.check(cap==Q(j['fixed_profile_family_ceiling'])<k+Q(1,10**18),'Whole fixed-family exclusion')
    # Like-for-like layout comparison, keeping the stopping/backoff values fixed.
    sb,se,sz=Q(1,10**6),Q(1,10**8),Q(1,10**14);sa=min(Q(j['actual_bit_saving']),(1-sb)*b-sz);sq=sa*(1-2*se);newk=c.below((1-se)*sq/(1+sq),10**18)
    balanced.assembly(f,old,sa,newk,beta=sb,h=se,a_complex=b)
    oldc=sq*(1+se);oldk=c.below((1-se)*sq/(1+oldc+sq),10**18);original=c.module(HERE/'references/pr104/structured_bulk_assembly.py','pinned_prefix');original.assembly(sa,b,f,oldk,eta=se,beta=sb)
    comparison=dict(beta=sb,eta=se,backoff=sz,original_prefix_kappa=oldk,balanced_kappa=newk,paid_layout_gain=newk-oldk,additional_backoff_gain=k-newk)
    agreement=None
    if reference is not None:
        c.no_floats(reference);keys=('profile','complex_saving','next_complex_rejected','first_moment','independent_moment','actual_bit_saving','assembly_bit','beta','eta','backoff','kappa','assembly','cutoffs','fixed_profile_family_ceiling')
        for key in keys:c.check(raw[key]==reference[key],'Independent prepackage witness differs at '+key)
        agreement=dict(all_fields_match=True,fields=list(keys))
    result=dict(status='PASS selected exact adverse controls and entire source-adaptation audit',source_sha256=c.source_hashes(),whole_adapter_normalizes_to_pinned_source=True,retained_constraints=47,retained_margins=7,three_stock_terms=terms,controls=controls,same_backoff_layout_comparison=comparison,prepackage_agreement=agreement,kappa=k,scope='Arithmetic and interface-source audit only; full physical and formal-tool receipts are separately bound.')
    result=c.js(result);c.no_floats(result);return result

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--certificate',type=Path,required=True);ap.add_argument('--reference-certificate',type=Path);ap.add_argument('--receipt',type=Path);args=ap.parse_args()
    j=c.read(args.certificate);reference=c.read(args.reference_certificate)if args.reference_certificate else None;result=validate(j,reference);result['certificate_sha256']=c.sha(args.certificate)
    if args.reference_certificate:result['prepackage_reference_sha256']=c.sha(args.reference_certificate)
    c.no_floats(result)
    if args.receipt:args.receipt.write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n')
    print('PASS '+str(len(result['controls']))+' adverse controls; full adapter normalization; three stocks; exact comparison')
    print(json.dumps(result['same_backoff_layout_comparison'],indent=2))
if __name__=='__main__':main()

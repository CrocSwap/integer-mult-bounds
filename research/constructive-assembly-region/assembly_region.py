#!/usr/bin/env python3
"""Original exact-arithmetic diagnostic; never imports or executes upstream programs.

This is an arithmetic-domain result only. Positive bridge gaps are explicit
assumptions; no finite supplier or all-size multiplication interface is proved.
Equations are attributed to the pinned CrocSwap source identified below and in PROOF.md.
Prepared with OpenAI assistance. Apache-2.0.
"""
import argparse
import ast
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]
SOURCE_PATH = Path('research/coordinated-frames-and-entrance-banks/arithmetic/balanced_shared.py')
CERTIFICATE_PATH = REPO_ROOT / 'research/coordinated-frames-and-entrance-banks/certificate.json'
CAP_NAME = 'b_below_one_over32'
BRIDGE_NAMES = {'literal_scalar_guard', 'row_product_gap'}
PINNED_BLOB = 'e94c7dcaa98b72941f35416009c33801ab4ebbb0'
PINNED_COMMIT = '3b6b66891c0ac888521cf591fe306c6286601d4f'
PINNED_SOURCE_SHA256 = 'c3204e1758057f5ef10724014f38b91b8a01f6d8a3562b054263fc74795bfd90'
PINNED_CERTIFICATE_SHA256 = '59b20818af6f850f40d18fd8206b136da504d9cbc57dbbefcba232c62f3384e6'


def rational(value):
    if type(value) is int or type(value) is F:
        return F(value)
    if type(value) is str and re.fullmatch(r'-?[0-9]+(?:/[1-9][0-9]*)?', value):
        return F(value)
    raise ValueError('Expected an exact integer or rational fraction; floats/bools rejected')


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def source_contract(path=REPO_ROOT / SOURCE_PATH):
    # Reuse the checkout's source as inert data; do not import the assembly.
    data = Path(path).read_bytes()
    blob = hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
    require(blob == PINNED_BLOB, 'Pinned source bytes changed')
    require(hashlib.sha256(data).hexdigest() == PINNED_SOURCE_SHA256,
            'Pinned source bytes changed')
    # Parse source as inert syntax, never compile, exec, import or call it.
    tree = ast.parse(data.decode('utf-8'))
    assignments = [n for n in ast.walk(tree) if isinstance(n, ast.Assign)]
    names = {}
    for item in assignments:
        if len(item.targets) == 1 and isinstance(item.targets[0], ast.Name):
            name = item.targets[0].id
            if name in ('slacks', 'margins'):
                require(isinstance(item.value, ast.Call), 'Unexpected source structure')
                names[name] = {kw.arg for kw in item.value.keywords}
    labels = names['slacks'] | {name+'_above_kappa' for name in names['margins']}
    require(len(labels) == 47, 'Expected 47 source constraints')
    return dict(commit=PINNED_COMMIT, path=SOURCE_PATH.as_posix(), git_blob=blob,
                sha256=hashlib.sha256(data).hexdigest(), labels=sorted(labels))


def direct_slacks(a, b, beta, h, kappa, scalar_gap=1, row_gap=1):
    """Independent transcription of the displayed equations, using exact fractions.

    Return violations rather than suppressing the production cap. The caller
    explicitly chooses a diagnostic evaluation mode in verdict().
    """
    a,b,beta,h,kappa,scalar_gap,row_gap = map(rational,
        (a,b,beta,h,kappa,scalar_gap,row_gap))
    q = a*(1-2*h)
    require(1+q != 0, 'Undefined epsilon')
    eps = (1-h)/(1+q)
    G = eps*q
    tau, sigma = 1-a, 1-b
    lp, c = 1-q, q+h/4
    lam = (tau+lp)/2
    r, delta = (G+1-eps)/2, h/8
    internal = tau+(1-beta)*max(sigma-tau, F(0))
    leaf = sigma+beta*(1-sigma)
    margins = {'g1':1-eps, 'g2':a, 'g3':G, 'g4':a,
               'g5':min(1-eps-delta,r-delta), 'g6':1-eps-delta,'g7':eps}
    slacks = {
        'a_positive':a, 'a_below_b':b-a, CAP_NAME:F(1,32)-b,
        'beta_positive':beta, 'beta_below_one':1-beta,
        'phase_leaf_above_bit':(1-beta)*b-a,
        'q_positive':q, 'q_below_internal':1-internal-q,
        'q_below_leaf':1-leaf-q, 'c_positive':c,'c_below_one':1-c,
        'q_below_reservations':c-q, 'lambda_above_tau':lam-tau,
        'lambda_above_sigma':lam-sigma, 'lambda_above_internal':lam-internal,
        'lambda_prime_above_lambda':lp-lam, 'compact_leaf':lp-leaf,
        'compact_reservations':lp-(1-c),'lambda_prime_below_one':q,
        'epsilon_positive':eps,'epsilon_below_one':1-eps,'guard_width':1-eps,
        'K_geometry':1-eps*(1+c),'K_dominates_log':eps*c,
        'record_suffix':1-eps, 'phase_local':1-eps-delta,
        'phase_boundary':r-delta, 'gamma_sublinear':1-eps-r,
        'cell_above_band':eps-(1-r)/2,'prime_interval_packing':1-eps,
        'alpha_positive':r,'alpha_below_one':1-r,
        'alpha_below_one_fourth':F(1,4)-r,'delta_positive':delta,
        'delta_below_one_eighth':F(1,8)-delta,'short_record_fallback':eps-a,
        'small_field_exposure':1-eps-G,
        'artificial_boundary':8-eps+r-delta-G,
        'literal_scalar_guard':scalar_gap,'row_product_gap':row_gap}
    slacks.update({name+'_above_kappa':value-kappa for name,value in margins.items()})
    preconditions = {'positive_backoff':h>0, 'backoff_below_half':h<F(1,2),
                     'positive_kappa':kappa>0}
    return dict(slacks=slacks, margins=margins, preconditions=preconditions,
                parameters=dict(a=a,b=b,beta=beta,h=h,kappa=kappa,q=q,
                                epsilon=eps,G=G,r=r,delta=delta,c=c))


def factored_slacks(a,b,beta,h,kappa,scalar_gap=1,row_gap=1):
    """Second evaluation, from the proof's factorizations for a < b."""
    a,b,beta,h,kappa,scalar_gap,row_gap = map(rational,
        (a,b,beta,h,kappa,scalar_gap,row_gap))
    require(a<b, 'Factorization assumes a < b')
    require(h>=0, 'Minimum-margin factorization assumes h >= 0')
    q=a*(1-2*h); eps=(1-h)/(1+q); G=eps*q; L=(1-beta)*b-a
    r=G+h/2; c=q+h/4
    result={
        'a_positive':a,'a_below_b':b-a,CAP_NAME:F(1,32)-b,
        'beta_positive':beta,'beta_below_one':1-beta,'phase_leaf_above_bit':L,
        'q_positive':q,'q_below_internal':2*a*h,'q_below_leaf':L+2*a*h,
        'c_positive':c,'c_below_one':1-c,'q_below_reservations':h/4,
        'lambda_above_tau':a*h,'lambda_above_sigma':b-a+a*h,
        'lambda_above_internal':a*h,'lambda_prime_above_lambda':a*h,
        'compact_leaf':L+2*a*h,'compact_reservations':h/4,
        'lambda_prime_below_one':q,'epsilon_positive':eps,
        'epsilon_below_one':G+h,'guard_width':G+h,
        'K_geometry':h*(1-eps/4),'K_dominates_log':eps*c,
        'record_suffix':G+h,'phase_local':G+7*h/8,'phase_boundary':G+3*h/8,
        'gamma_sublinear':h/2,'cell_above_band':eps-(1-r)/2,
        'prime_interval_packing':G+h,'alpha_positive':r,'alpha_below_one':1-r,
        'alpha_below_one_fourth':F(1,4)-r,'delta_positive':h/8,
        'delta_below_one_eighth':(1-h)/8,'short_record_fallback':eps-a,
        'small_field_exposure':h,'artificial_boundary':8-eps+3*h/8,
        'literal_scalar_guard':scalar_gap,'row_product_gap':row_gap}
    margins={'g1':G+h,'g2':a,'g3':G,'g4':a,'g5':G+3*h/8,'g6':G+7*h/8,'g7':eps}
    result.update({name+'_above_kappa':value-kappa for name,value in margins.items()})
    return result


def verdict(result, *, include_production_cap=True):
    excluded=set() if include_production_cap else {CAP_NAME}
    failed=[name for name,value in result['slacks'].items() if name not in excluded and value<=0]
    failed += [name for name,value in result['preconditions'].items() if not value]
    return {'accepted':not failed,'failed':failed,
            'excluded_constraints':sorted(excluded),
            'assumed_bridge_constraints':sorted(BRIDGE_NAMES)}


def construct(a,b,kappa):
    a,b,kappa=map(rational,(a,b,kappa))
    require(0<a<F(1,3), 'Sufficient-region theorem requires 0 < a < 1/3')
    require(a<b, 'Sufficient-region theorem requires a < b')
    G0=a/(1+a); d=G0-kappa
    require(0<kappa<G0,'Target kappa must be strictly between zero and a/(1+a)')
    beta=(b-a)/(2*b)
    h=min(F(1,8),(1-3*a)/(4*(1+a)),d/(6*a))
    return dict(a=a,b=b,beta=beta,h=h,kappa=kappa)


def construct_for_kappa(kappa, *, production=False):
    kappa=rational(kappa)
    cap=F(1,32) if production else F(1,3)
    require(0<kappa<cap/(1+cap), 'Target outside the open arithmetic range')
    required_a=kappa/(1-kappa)
    a=(required_a+cap)/2
    return construct(a,(a+cap)/2,kappa)


def proof_bounds(parameters):
    a,b,beta,h,kappa = (parameters[k] for k in ('a','b','beta','h','kappa'))
    result=direct_slacks(**parameters); p=result['parameters']
    G0=a/(1+a); d=G0-kappa; loss=G0-p['G']
    formula=a*h*((3+a)-2*h*(1+a))/((1+a)*(1+a-2*a*h))
    bounds={
        'exact_loss_identity':loss==formula,
        'loss_below_3ah':loss<3*a*h,
        'loss_below_half_target_gap':loss<d/2,
        'gaussian_bound':p['r']<=G0+(F(1,4)-G0)/2<F(1,4),
        'epsilon_lower_bound':p['epsilon']>F(21,32),
        'leaf_gap_identity':(1-beta)*b-a==(b-a)/2,
        'minimum_margin_identity':min(result['margins'].values())==p['G'],
        'target_strictly_attained':p['G']>kappa,
        'all_factorizations_agree':result['slacks']==factored_slacks(**parameters)}
    require(all(bounds.values()), 'A constructive bound failed')
    return bounds


def published_regression(certificate_path):
    # parse_int=str prevents irrelevant enormous literal bridge integers from
    # triggering Python's conversion guard. No global security setting changed.
    data=Path(certificate_path).read_bytes()
    require(hashlib.sha256(data).hexdigest()==PINNED_CERTIFICATE_SHA256,
            'Pinned published certificate bytes changed')
    cert=json.loads(data,parse_int=str)
    assembly=cert['arithmetic']['assembly']; p=assembly['parameters']
    args=dict(a=p['a_bit'],b=p['a_complex'],beta=p['beta'],h=p['h'],kappa=p['kappa'])
    actual=direct_slacks(**args)
    expected=assembly['constraints']
    names=set(actual['slacks'])-BRIDGE_NAMES
    require(all(actual['slacks'][name]==rational(expected[name]) for name in names),
            'Published non-bridge slacks disagree')
    require(all(actual['margins'][name]==rational(value) for name,value in assembly['margins'].items()),
            'Published seven margins disagree')
    return {'certificate_sha256':PINNED_CERTIFICATE_SHA256,
            'matched_non_bridge_constraints':len(names),'matched_margins':7,
            'bridge_gaps':'Not re-proved or compared by this diagnostic'}


def serial(value):
    if type(value) is F: return str(value)
    if isinstance(value,dict): return {k:serial(v) for k,v in value.items()}
    if isinstance(value,(list,tuple)): return [serial(v) for v in value]
    return value


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--certificate',type=Path,default=CERTIFICATE_PATH)
    parser.add_argument('--output',type=Path,required=True,
                        help='Path for the exact diagnostic report (generated, not tracked)')
    args=parser.parse_args()
    pin=source_contract()
    targets=[F(1,100),F(3,100),F(1,10),F(23,100),F(249,1000),
             F(1,4)-F(1,10**12),F(1,4)-F(1,10**50)]
    rows=[]
    for kappa in targets:
        parameters=construct_for_kappa(kappa); result=direct_slacks(**parameters)
        require(set(pin['labels'])==set(result['slacks']),'Constraint labels disagree with pinned source')
        rows.append(dict(parameters=parameters,bounds=proof_bounds(parameters),
                         production=verdict(result),diagnostic=verdict(result,include_production_cap=False),
                         minimum_margin=min(result['margins'].values()),
                         smallest_diagnostic_slack=min(v for k,v in result['slacks'].items() if k!=CAP_NAME)))
    production_parameters=construct_for_kappa(F(1,33)-F(1,10**30),production=True)
    production_result=direct_slacks(**production_parameters)
    output={'status':'PASS: scoped exact arithmetic only','source':pin,
            'claim':'Constructive sufficient region 0<a<1/3; relaxed displayed arithmetic has supremum kappa=1/4',
            'excluded_from_claim':['finite suppliers','valid bridge','moment enclosure extension',
              'uniform recursion','prime supply','precision/recovery','fixed-tape multiplication theorem'],
            'assumptions':{'literal_scalar_guard':'positive, represented by 1','row_product_gap':'positive, represented by 1'},
            'retained_entry_requirements':['0 < h < 1/2','kappa > 0'],
            'unverified_entry_requirements':['validate_shared_bridge(finite_bridge, complex_row)',
                "a <= finite_bridge['bit_uniform']['ordinary_saving']"],
            'diagnostic_rows':rows,
            'retained_cap_control':{'parameters':production_parameters,'verdict':verdict(production_result),
                                   'bounds':proof_bounds(production_parameters)},
            'next_step':'Independent mathematical review; no change to production guards or published kappa'}
    if args.certificate: output['published_regression']=published_regression(args.certificate)
    args.output.write_text(json.dumps(serial(output),indent=2)+'\n')
    print(json.dumps({'status':output['status'],'output':str(args.output),
                      'diagnostic_rows':len(rows),'retained_cap_control_pass':verdict(production_result)['accepted'],
                      'published_regression':output.get('published_regression')},indent=2))


if __name__=='__main__':
    main()

#!/usr/bin/env python3
"""Compose PR24's bit interface with PR23's semantic/bulk assembly.

Dominik Scholz, with substantial OpenAI Codex assistance. Apache-2.0.
The assembly below is adapted from Zhihao Chen's PR23; the bit construction
is icekylinx's PR24. PR23 attributes its analytic transfers to RaD/hipotures.
"""
from copy import deepcopy
from difflib import unified_diff
from fractions import Fraction as Q
from hashlib import sha256
import importlib.util
import json
from pathlib import Path

import endpoint_gauge_network as endpoint
from certify import require
from prepare_layers import serializable

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    'semantic_bulk', ROOT / 'research/semantic-bulk/verify.py')
bulk = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bulk)
BIT_SAVING = endpoint.AB
KAPPA = Q(119720853, 10**13)
HEADROOM = Q(1, 10**12)
PINS = {
    'research/semantic-bulk/certificate.json':
        '6322f9c97a5e72fd6e29477cb60a874d180af29f402751731b5121a088fb48c2',
    'certificates/endpoint-gauge-network.json':
        '0ccbc892174915e3a7559cc116eaf42b288dae4d933b1332520e0710ffff5f96',
}


def canonical(value):
    return json.loads(json.dumps(serializable(value)))


def validate_dependencies():
    for name, digest in PINS.items():
        require(sha256((ROOT / name).read_bytes()).hexdigest() == digest,
                'Pinned dependency certificate changed: '+name)
    prior = bulk.run()
    require(canonical(prior) == json.loads(
        (ROOT / 'research/semantic-bulk/certificate.json').read_text()),
        'PR23 certificate does not reproduce')
    finite = endpoint.certificate()
    require(canonical(finite) == json.loads(
        (ROOT / 'certificates/endpoint-gauge-network.json').read_text()),
        'PR24 certificate does not reproduce')
    for name, digest in finite['source_sha256'].items():
        require(sha256((ROOT / name).read_bytes()).hexdigest() == digest,
                'Endpoint source hash: '+name)
    return prior, finite


def finite_bridge(prior, bit):
    # The complex circuit and its literal semantic charge are unchanged.
    result = deepcopy(prior['finite_bridge'])
    m, W = bit['counts']['m'], bit['counts']['W']
    maximum = max(int(t) for t in bit['counts']['child_multiplicities'])
    depth = bulk.halving(m, maximum)
    result['bit'] = dict(m=m, W=W, maxchild=maximum,
                         halving_degree=depth, wire_bits=W.bit_length())
    complex_counts = result['complex']
    coefficient = (W.bit_length()*depth + complex_counts['wire_bits']*
                   complex_counts['halving_degree'])
    degree = 1000*bulk.ceil(Q(coefficient*51, 25000))
    require(degree > Q(coefficient*51, 25), 'Product stock degree')
    result['rows'] = dict(coefficient=coefficient, degree=degree,
                         suffix_slope=4*degree,
                         degree_gap=degree-Q(coefficient*51, 25),
                         contract=prior['finite_bridge']['rows']['contract'])
    return result


def assembly(f,kappa=KAPPA,a=BIT_SAVING,h=HEADROOM,old_guard=False,old_exposures=False):
    b=Q(18,10**6);beta=Q(1,4)
    tau,sigma=1-a,1-b;q=a*(1-2*h);lp=1-q;lam=(tau+lp)/2
    c=q*(1+h);eps=(1-h)/(1+c+q);G=eps*q
    r=(G+1-eps)/2;delta=h/8
    C1=Q(19991,10000) if old_guard else Q(1)
    margins=dict(g1=1-eps*(1+c),g2=a,g3=G,g4=a,
        g5=min(1-eps-delta,r-delta),g6=1-eps-delta,g7=eps)
    if old_exposures:margins.update(g2=eps*c*a,g4=a*(1-eps))
    internal=tau+(1-beta)*max(sigma-tau,Q(0));leaf=sigma+beta*(1-sigma)
    slacks=dict(a_positive=a,a_below_b=b-a,b_below_one_over32=Q(1,32)-b,
        beta_positive=beta,beta_below_one=1-beta,phase_leaf_above_bit=(1-beta)*b-a,
        q_positive=q,q_below_internal=1-internal-q,q_below_leaf=1-leaf-q,
        c_positive=c,c_below_one=1-c,q_below_reservations=c-q,
        lambda_above_tau=lam-tau,lambda_above_sigma=lam-sigma,
        lambda_above_internal=lam-internal,lambda_prime_above_lambda=lp-lam,
        compact_leaf=lp-leaf,compact_reservations=lp-(1-c),lambda_prime_below_one=q,
        epsilon_positive=eps,epsilon_below_one=1-eps,guard_width=1-eps*C1,
        K_geometry=1-eps*(1+c),K_dominates_log=eps*c,
        record_suffix=1-eps,phase_local=1-eps-delta,phase_boundary=r-delta,
        gamma_sublinear=1-eps-r,cell_above_band=eps-(1-r)/2,
        prime_interval_packing=1-eps,alpha_positive=r,alpha_below_one=1-r,
        alpha_below_one_fourth=Q(1,4)-r,delta_positive=delta,
        delta_below_one_eighth=Q(1,8)-delta,short_record_fallback=eps-a,
        small_field_exposure=1-eps-G,artificial_boundary=8-eps+r-delta-G,
        literal_scalar_guard=Q(f['semantic']['strict_literal_gap']),
        row_product_gap=f['rows']['degree_gap'])
    slacks.update({name+'_above_kappa':val-kappa for name,val in margins.items()})
    assert all(x>0 for x in slacks.values()),{k:str(v) for k,v in slacks.items() if v<=0}
    assert min(margins.values())==G and margins['g1']-G==h
    assert kappa>Q(1,2**17)
    p=dict(a_bit=a,a_complex=b,tau=tau,sigma=sigma,beta=beta,q=q,c=c,
        epsilon=eps,lambda_=lam,lambda_prime=lp,alpha_squared_power=r,
        delta=delta,C0=f['semantic']['C0'],C1=C1,kappa=kappa)
    return dict(parameters=p,constraints=slacks,margins=margins,minimum_margin=G,
        absorption_gap=G-kappa,gap_above_2_minus17=kappa-Q(1,2**17),
        recurrence=dict(internal=internal,leaf=leaf,reservations=1-c))


def certificate():
    prior, finite = validate_dependencies()
    original = assembly(prior['finite_bridge'], kappa=bulk.KAPPA,
                        a=Q(11, 10**6), h=Q(1, 10**8))
    require(original == prior['assembly'], 'Generalized assembly differs from PR23')
    bit = finite['bit']
    require(bit['saving'] == BIT_SAVING and bit['strict_gap'] > 0,
            'Endpoint bit characteristic')
    f = finite_bridge(prior, bit)
    a = assembly(f)
    require(len(a['constraints']) == 47 and len(a['margins']) == 7,
            'Assembly constraint count')
    require(a['absorption_gap'] > Q(3, 10**14), 'Headline absorption gap')
    require(KAPPA > bulk.KAPPA, 'No improvement over PR23')
    negatives = []
    for name, kwargs in (
        ('old_quadratic_guard', dict(old_guard=True)),
        ('old_separate_exposure', dict(old_exposures=True)),
        ('unsupported_2_minus16', dict(kappa=Q(1, 2**16))),
    ):
        try:
            assembly(f, **kwargs)
        except AssertionError:
            negatives.append(name)
        else:
            raise AssertionError('Negative control accepted: '+name)
    sources = [Path(__file__), ROOT / 'notes/endpoint-semantic-composition.tex',
               ROOT / 'docs/research/endpoint-semantic-composition.md']
    return dict(
        status='CONDITIONAL ENDPOINT/SEMANTIC COMPOSITION; NOT FORMAL VERIFICATION',
        baseline_PR23='661ebabc1076c9f525d7ce4967c876b203fa9827',
        bit_PR24='ed90fd940279c336ebc45968631bdebfb087b505',
        dependency_certificate_sha256=PINS,
        bit=bit, finite_bridge=f, assembly=a,
        eventual_bounds=bulk.cutoffs(f, a), negative_controls=negatives,
        improvement_ratio=KAPPA/bulk.KAPPA,
        source_sha256={str(p.relative_to(ROOT)): sha256(p.read_bytes()).hexdigest()
                       for p in sources},
        scope='PR24 bit interface, PR21 complex interface, PR23 semantic guard and '
              'attributed RaD analytic/tape transfers. PR24 complex network is not used.')


def proof_patch():
    name = 'notes/semantic-bulk-17-note.tex'
    original = (ROOT / name).read_text()
    marker = r'\begin{thebibliography}{9}'
    require(original.count(marker) == 1, 'Pinned proof insertion point')
    updated = original.replace(marker,
        '\\input{notes/endpoint-semantic-composition.tex}\n\n'+marker)
    return ''.join(unified_diff(original.splitlines(keepends=True),
                                updated.splitlines(keepends=True),
                                fromfile='a/'+name, tofile='b/'+name))


def main():
    result = certificate()
    (ROOT / 'certificates/endpoint-semantic-composition.json').write_text(
        json.dumps(canonical(result), indent=2, sort_keys=True)+'\n')
    (ROOT / 'patches/endpoint-semantic-composition.patch').write_text(proof_patch())
    print('PASS conditional kappa='+str(KAPPA)+'; 47 strict constraints; 7 margins')
    print('Product row degree:', result['finite_bridge']['rows']['degree'])
    print('Absorption gap > 3e-14; three negative controls rejected')


if __name__ == '__main__':
    main()

"""Exact common-grid Gaussian interpreter for the pinned integer 2208 circuit.

Combines the author's matrix circuit with canonical parity certificates.
This is an arithmetic reference, not a physical network/tensor-rank claim.
"""
from hashlib import sha256
import json
from pathlib import Path
from pi_exact import Gaussian

CIRCUIT_SHA256 = 'f265866665cb707a463b39c067875af9e7d6bedac82a8377c10d217e7ccc922f'

def load_circuit(path):
    raw = Path(path).read_bytes()
    if sha256(raw).hexdigest() != CIRCUIT_SHA256:
        raise ValueError('Pinned matrix circuit hash mismatch')
    data = json.loads(raw)
    if data['gate_count'] != 2208 or data['common_output_denominator'] != 8:
        raise ValueError('Unexpected circuit interface')
    return data

def gaussian_product3(x, y):
    """Gauss's established three-real-product identity, exact over integers."""
    a,b = x; c,d = y
    ac,bd = a*c,b*d
    return ac-bd,(a+b)*(c+d)-ac-bd

def multiply16(A, B, circuit):
    """Flat 256-entry canonical Gaussian inputs; common product tag is 2E."""
    if len(A) != 256 or len(B) != 256 or any(type(z) is not Gaussian for z in A+B):
        raise ValueError('Two flat 16 by 16 canonical Gaussian matrices required')
    values = A+B
    common_tag = max(z.exponent for z in values)
    aligned = [z.aligned(common_tag) for z in values]
    forms = {}
    additions = 0
    coefficient_scales = 0
    def linear(entries):
        nonlocal additions, coefficient_scales
        key = tuple(map(tuple, entries))
        if key not in forms:
            re=im=0
            for index,coefficient in entries:
                a,b = aligned[index]
                re += coefficient*a; im += coefficient*b
            forms[key]=(re,im)
            additions += 2*max(len(entries)-1,0)
            coefficient_scales += 2*sum(abs(c)!=1 for _,c in entries)
        return forms[key]
    products = [gaussian_product3(linear(g['left']),linear(g['right']))
                for g in circuit['gates']]
    outputs=[]
    for out in circuit['output_numerators']:
        re=im=0
        for gate,coefficient in out['terms']:
            a,b=products[gate]
            re += coefficient*a; im += coefficient*b
        additions += 2*max(len(out['terms'])-1,0)
        coefficient_scales += 2*sum(abs(c)!=1 for _,c in out['terms'])
        if re%8 or im%8:
            raise ValueError('Output numerator violated exact /8 component contract')
        outputs.append(Gaussian(re//8,im//8,2*common_tag))
    return outputs,dict(common_input_pi_tag=common_tag,
        raw_product_pi_tag=2*common_tag,extra_bits_beyond_common_product_grid=0,
        mixed_gaussian_products=len(products),real_variable_product_slots=3*len(products),
        exact_integer_quotients=512,distinct_cached_input_forms=len(forms),
        input_output_component_additions=additions,
        input_output_fixed_coefficient_scales=coefficient_scales,
        product_component_additions=5*len(products),
        scope='Exact reference arithmetic; alignment/normalization and tape costs separate')

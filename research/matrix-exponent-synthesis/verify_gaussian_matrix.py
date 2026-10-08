"""Independent Fraction controls for actual Gaussian matrix/parity integration."""
from fractions import Fraction as Q
from pathlib import Path
import argparse
import json
import random
import sys
from gaussian_matrix import load_circuit, multiply16
from pi_exact import Gaussian

def need(condition, message):
    if not condition: raise ValueError(message)

def value(z):
    # Independent repeated complex division by 1+i, no oracle conversion.
    a,b=Q(z.re),Q(z.im)
    for _ in range(z.exponent): a,b=(a+b)/2,(b-a)/2
    return a,b

def product(x,y):
    a,b=x;c,d=y
    return a*c-b*d,a*d+b*c

def main():
    need(not sys.flags.optimize,'Run checked verification without -O')
    ap=argparse.ArgumentParser();ap.add_argument('--circuit',type=Path,required=True)
    args=ap.parse_args();circuit=load_circuit(args.circuit)
    rng=random.Random(1682208);trials=[]
    for trial in range(4):
        maximum=0 if trial==0 else 8
        A=[Gaussian(rng.randrange(-7,8),rng.randrange(-7,8),rng.randrange(maximum+1)) for _ in range(256)]
        B=[Gaussian(rng.randrange(-7,8),rng.randrange(-7,8),rng.randrange(maximum+1)) for _ in range(256)]
        result,counts=multiply16(A,B,circuit)
        aa=list(map(value,A));bb=list(map(value,B))
        for i in range(16):
            for j in range(16):
                re=im=Q(0)
                for k in range(16):
                    a,b=product(aa[16*i+k],bb[16*k+j]);re+=a;im+=b
                need(value(result[16*i+j])==(re,im),'Independent Gaussian matrix product failed')
        if trial==0:
            need(all(z.exponent==0 for z in result),'Gaussian-integer result lost its integral grid')
        trials.append(dict(trial=trial,verified_outputs=256,counts=counts))
    try: multiply16(A[:-1],B,circuit)
    except ValueError: pass
    else: raise ValueError('Wrong shape must be rejected')
    print(json.dumps(dict(status='passed',trials=trials,
        output_values=1024,independent_target_dot_product_terms=16384,
        variable_real_products_per_trial=6624,comparison_four_real_product_slots=8832,
        known_three_real_product_identity_credited=True,
        new_matrix_exponent_claimed=False,new_integer_kappa_claimed=False),indent=2))

if __name__=='__main__':main()

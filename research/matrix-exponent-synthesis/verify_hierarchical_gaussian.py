"""Independent tests of flattened-vs-shared Gaussian evaluation and exact cost."""
from pathlib import Path
import argparse,json,random,sys
from gaussian_matrix import load_circuit,multiply16
from hierarchical_gaussian_matrix import load_outer,multiply16_hierarchical
from verify_gaussian_matrix import value,product,need
from pi_exact import Gaussian
from fractions import Fraction as Q

def main():
    need(not sys.flags.optimize,'Run checked verification without -O')
    ap=argparse.ArgumentParser();ap.add_argument('--circuit',type=Path,required=True)
    ap.add_argument('--outer',type=Path,required=True);args=ap.parse_args()
    circuit=load_circuit(args.circuit);outer=load_outer(args.outer)
    rng=random.Random(486416);receipts=[]
    for trial in range(5):
        e=0 if trial==0 else 9
        A=[Gaussian(rng.randrange(-5,6),rng.randrange(-5,6),rng.randrange(e+1)) for _ in range(256)]
        B=[Gaussian(rng.randrange(-5,6),rng.randrange(-5,6),rng.randrange(e+1)) for _ in range(256)]
        actual,counts=multiply16_hierarchical(A,B,outer)
        flat,flat_counts=multiply16(A,B,circuit)
        need(actual==flat,'Shared DAG differs from pinned flattened circuit')
        aa=list(map(value,A));bb=list(map(value,B))
        for i in range(16):
            for j in range(16):
                re=im=Q(0)
                for k in range(16):
                    a,b=product(aa[16*i+k],bb[16*k+j]);re+=a;im+=b
                need(value(actual[16*i+j])==(re,im),'Independent classical Gaussian target failed')
        need(counts['mixed_gaussian_products']==2208,'Scheduled count changed')
        flat_adds=flat_counts['input_output_component_additions']+flat_counts['product_component_additions']
        receipts.append(dict(trial=trial,outputs=256,counts=counts,
            flat_component_additions=flat_adds,addition_saving=flat_adds-counts['component_additions']))
    print(json.dumps(dict(status='passed',canonical_literal_output_comparisons=1280,
        independent_target_dot_product_terms=20480,trials=receipts,
        arithmetic_reference_only=True,new_kappa_claimed=False),indent=2))

if __name__=='__main__': main()

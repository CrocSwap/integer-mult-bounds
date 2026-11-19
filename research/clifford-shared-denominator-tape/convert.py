"""Run one signed dyadic numerator through the physical gate program."""
import argparse
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from tape import Q,X,Layout,initial,program,read,run,wire


def convert(numerator,divisor,e,p,nearest=True):
    bits=max(1,abs(numerator).bit_length(),max(0,e-p)+1)
    grid=Layout(bits,divisor.bit_length(),e,p)
    state=initial(grid,divisor,abs(numerator))
    cost=run(program(grid,nearest),state)
    q=read(state,0,grid.m,X)
    residue=read(state,grid.m,grid.k+grid.s,X)
    increment=state[wire(grid.m,Q)]
    sign=-1 if numerator<0 else 1
    return dict(grid_integer=sign*q,precision=p,exact_residue=residue,
                residue_modulus=divisor<<grid.s,negative_input=numerator<0,
                increment=increment,sites=grid.sites,not_gates=cost[1],
                cnot_gates=cost[2],toffoli_gates=cost[3],head_moves=cost["moves"])


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("numerator",type=int)
    parser.add_argument("odd_divisor",type=int)
    parser.add_argument("input_fraction_bits",type=int)
    parser.add_argument("output_fraction_bits",type=int)
    parser.add_argument("--truncate",action="store_true")
    args=parser.parse_args()
    import json
    print(json.dumps(convert(args.numerator,args.odd_divisor,args.input_fraction_bits,
                             args.output_fraction_bits,not args.truncate),indent=2))

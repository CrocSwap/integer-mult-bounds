"""Verify the terminal divisor interfaces and a literal width-13 canonical class coefficient."""
from fractions import Fraction
from pathlib import Path
from math import lcm
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from denominators import data,five,require,split,transformed
from tape import Layout,initial,program,run
from check_tape import expected
from convert import convert

D13=22742436009630709072767882717680300149753125


def main():
    kernels=transformed()
    expected_divisors={"canonical":(D13,0),"schedule51":(470624175,11352),"schedule52":(1,7499)}
    for name,k in kernels.items():
        h=lcm(*(v.denominator for f in k for v in f))
        require(split(h)==expected_divisors[name],name)
        print(name,"odd divisor and binary scale",split(h))
    for name in ("schedule51","schedule52"):
        d,e=expected_divisors[name]
        short=convert(-3,d,e,0)
        require(short["grid_integer"]==0 and short["exact_residue"]==3 and short["negative_input"],
                "long padded binary tail and signed zero readout")
        print(name,"three-unit numerator at its actual binary scale: sites",short["sites"])
    corners=data("CORNERS.json")["corners"]
    for width,bits,delay in ((15,381,0),(16,727,0),(18,997,1),(20,2073,1),(22,1829,1)):
        d=five(width,corners)
        require(d.bit_length()==bits and split((d-1)//2)[1]==delay,"five-qubit divisor")
        print("five-qubit",width,"carry bits",bits,"rounding suffix bits",delay)
    # Physical readout of the identity coefficient of the actual inverse kernel.
    val=kernels["canonical"][0][0]
    n=abs(val*D13)
    require(n.denominator==1,"literal integer numerator")
    n=n.numerator
    layout=Layout(n.bit_length(),D13.bit_length(),0,32)
    state=initial(layout,D13,n)
    counts=run(program(layout),state)
    require(state==expected(layout,D13,n,True),"source-bound physical coefficient")
    q=round(val*2**32)
    print("identity kernel",val,"rounded grid integer",q,"sites",layout.sites,
          "NOT/CNOT/Toffoli",tuple(counts[i] for i in (1,2,3)),"head moves",counts["moves"])


if __name__=="__main__":
    main()

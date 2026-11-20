"""Compare the complete binary multiplier with two independent product oracles."""

from math import prod
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from catalogue_codec import emit, open_catalogue
from product import catalogue, choose, multiply
from verify_radius import ensure, error_profile, private_bounds


def schoolbook(left,right,b,size):
    def digits(bits):
        return [int(bits[max(0,j-b):j],2) for j in range(len(bits),0,-b)]
    result = [0]*size
    for i,x in enumerate(digits(left)):
        for j,y in enumerate(digits(right)):
            result[i+j] += x*y
    return result


def check(left,right):
    out,info = multiply(left,right)
    ensure(info["path"]=="gaussian","product used the elementary branch")
    ensure(len(out)==2*max(len(left),len(right)),"output width changed")
    ensure(int(out,2)==int(left,2)*int(right,2),"incorrect binary product")
    raw = schoolbook(left,right,info["digit_bits"],prod(info["sources"]))
    ensure(info["coefficients"]==raw,"incorrect coefficient before carry")
    ensure(2*info["radius_numerator"]<info["radius_denominator"],"unseparated integer")
    ensure(info["max_residual_squared_numerator"]<=info["radius_numerator"]**2,
           "computed complex residual exceeds the all-input bound")
    tr = info["trace"]
    ensure(tr["rings"]==3*prod(info["targets"][1:]) and tr["stages"]>0
           and tr["grouped_requests"]>0 and tr["scalar_products"]>0
           and tr["erased"]>0 and tr["live"]==0,"incomplete physical path")
    return int(out,2),info


def small():
    a,b = 741503,466013
    value,r = check(format(a,"b"),format(b,"b"))
    ensure(value==345550037539 and r["coefficients"]==[11811,10996,4152,868,77]+[0]*30,
           "regression fixture")
    for x,y in (("0","1"),("00000","0000"),("00000001","1"*144),
                ("1"*144,"1"*144),("01"*64,"1001"*35)):
        check(x,y)
    finite,branch=multiply("1".zfill(1801),"11")
    ensure(branch["path"]=="elementary" and finite==format(3,"03602b"),
           "the finite elementary branch or its output width is wrong")
    g = choose(20)
    pages = catalogue(g)
    profile = error_profile(g.precision,g.digit_bits,g.sources,
                            [f.output_shift for _,a,c in pages for f in (a,c)],prod(g.targets[1:]))
    for _,a,c in pages:
        for f in (a,c):
            private_bounds(g.precision,f.condition_guard)
    for q in (2,16,128):
        for guard in (2,3,7,10):
            private_bounds(q,guard)
    encoded = emit(pages)
    old = HERE.parent/"physical-tensor-crt-sandwich-recovery"/"inputs"/"p48-5x7.bin"
    for broken in (old.read_bytes(),encoded[:-1],encoded+b"x"):
        try:
            open_catalogue(broken,g)
        except ValueError:
            continue
        raise ArithmeticError("malformed or diagnostic pointer admitted")
    # The independent operator oracle has a different alpha and its own admission rules.
    sys.path.insert(0,str(HERE.parent/"certified-gaussian-recovery"))
    from gaussian import GaussianLine
    from pipeline import multiply as dense
    lines = [GaussianLine(s,t,6,precision=128,bits=320) for s,t in zip(g.sources,g.targets)]
    dv,dr = dense(741503,466013,lines,8,input_bits=20)
    ensure(value==dv and dr["coefficients"]==r["coefficients"],"dense Gaussian oracle mismatch")
    print("PASS Gaussian products=6 dense_lines="+str(dr["gaussian_line_executions"]),
          "regression="+str(value),"coefficients="+str(r["coefficients"][:5]),
          "coarse_radius="+str(profile[-1]),"fine_radius="+str(float(profile[-2])))
    print("generated_bits",r["catalogue_bits"],"resets",r["trace"]["resets"],
          "payload_travel",r["trace"]["travel"],"live_at_exit",r["trace"]["live"])


if __name__=="__main__":
    small()

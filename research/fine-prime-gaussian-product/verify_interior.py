"""Run a complete encoded product on a Gaussian axis with a strict interior."""

from fractions import Fraction
from math import prod
from pathlib import Path
import sys
from types import SimpleNamespace

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from gaussian_pages import CoefficientAdmissionError
from product import choose
from recovery_radius import page_limit, rounding_numerator
from verify_product import check, ensure


if __name__ == "__main__":
    g=choose(145)
    ensure(choose(144).sources==(5,7) and g.sources==choose(1800).sources==(31,29),
           "finite parameter boundary")
    ensure(2*((1800+3)//4)-1==prod(g.sources),"no-wrap upper endpoint")
    for s,t in zip(g.sources,g.targets):
        selected={(2*t*j+s)//(2*s) for j in range(s)}
        interior=[k for k in range(t) if g.window<=k%g.block<g.block-g.window
                  and all(i in selected for i in range(k-k%g.block,k-k%g.block+g.block))]
        ensure(len(interior)==(2 if s==31 else 0),"nonempty pure-block interior")
    locally_admissible=SimpleNamespace(defect=page_limit(g)*Fraction(3,4),output_shift=3)
    try:
        rounding_numerator(g,[((),locally_admissible,locally_admissible)]*2)
    except CoefficientAdmissionError:
        pass
    else:
        raise ArithmeticError("insufficient global radius accepted")
    a,b=741503,466013
    value,r=check(format(a,"0145b"),format(b,"0145b"))
    ensure(value==345550037539 and r["coefficients"][:9]==[195,166,215,164,280,164,137,46,77],
           "base-16 independent control")
    radius=Fraction(r["radius_numerator"],r["radius_denominator"])
    ensure(radius<Fraction(247,10**6) and r["scale_exponent"]==12,"regular rounding bound")
    squared=Fraction(r["max_residual_squared_numerator"],r["radius_denominator"]**2)
    ensure(squared<Fraction(226,10**11)**2,"observed regular coefficient residual")
    print("PASS encoded interior product",value,"coefficients",len(r["coefficients"]),
          "source",r["sources"],"interior",2,"radius <",0.000247)
    print("catalogue bits",r["catalogue_bits"],"payload travel",r["trace"]["travel"],
          "word products",r["trace"]["scalar_products"],"live",r["trace"]["live"])

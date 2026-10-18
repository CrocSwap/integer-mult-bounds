"""The actual selected directed recipe through physical signed record scans."""
from pathlib import Path
from time import monotonic
import json
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
from check_monomial import one_case
from gaussian_test_support import selected_recipe
from words import need


def run():
    started = monotonic()
    _engine,result = one_case(selected_recipe(),f=1,K=1,G=1,rho=0,bits=3,coefficients=3,rows=2,dirty_bits=1)
    need(result["affine_gates"] == 22 and result["records_per_row"] == 1024, "actual selected recipe and dirty slice")
    print("physical selected monomial seconds",round(monotonic()-started,2),flush=True)
    return dict(recipe="0:1000.right",result=result,
                scope="Complete selected nine-coordinate one-column recipe; two outer rows, one dirty spectator bit and three Gaussian fields")


if __name__ == "__main__":
    print(json.dumps(run(),sort_keys=True,indent=2))
    print("PASS_PHYSICAL_SELECTED_MONOMIAL")

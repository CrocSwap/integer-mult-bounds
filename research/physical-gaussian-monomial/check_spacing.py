"""Physical two-column monomial with nonzero residue and unselected wide bits."""
from pathlib import Path
from time import monotonic
import json
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
from check_monomial import one_case
from gaussian_test_support import GENERIC


def run():
    started = monotonic()
    _engine,result = one_case(GENERIC,f=2,K=2,G=1,rho=1,bits=3,coefficients=3,rows=1)
    print("physical spaced monomial seconds",round(monotonic()-started,2),flush=True)
    return dict(result=result,scope="Complete2048-record two-column dirty rectangle at K2/rho1; all unselected wide bits remain spectators")


if __name__ == "__main__":
    print(json.dumps(run(),sort_keys=True,indent=2))
    print("PASS_PHYSICAL_SPACED_MONOMIAL")

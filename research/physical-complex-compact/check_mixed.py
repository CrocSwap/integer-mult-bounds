"""A complete physical raw word and repair with nonempty good and bad sets."""
from pathlib import Path
from time import monotonic
import json
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
from check_payload import one_case
from words import need


def run():
    started = monotonic()
    _engine,result = one_case(constant=True,omit_source=True,n=1,K=5,G=1,rho=0,
                             outer=1,record_bits=1)
    need(result["good_records"] == 2048 and result["bad_records"] == 6144,
         "complete mixed-guard physical domain")
    print("complete mixed-guard compact seconds",round(monotonic()-started,2),flush=True)
    return dict(result=result,scope="Full 8192-record constant-toggle rectangle; actual raw movement, encoded repair and final high bit; all input columns")


if __name__ == "__main__":
    print(json.dumps(run(),indent=2,sort_keys=True))
    print("PASS_COMPLETE_MIXED_GUARD_COMPACT")

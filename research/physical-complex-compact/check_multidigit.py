"""Full two-digit dirty Compact words in both source orders."""
from pathlib import Path
from time import monotonic
import json
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
from check_payload import one_case


def run():
    started = monotonic()
    _engine,early = one_case(n=2,K=1,G=1,rho=0,q=3,outer=1,record_bits=1)
    _engine,late = one_case(n=2,K=1,G=1,rho=0,late=True,outer=1,record_bits=1)
    print("complete two-digit compact seconds",round(monotonic()-started,2),flush=True)
    return dict(cases=[early,late],scope="Two complete 4096-record rectangles; nG=2 binary calls, including q3 padding; B1 uses its elementary branch")


if __name__ == "__main__":
    print(json.dumps(run(),indent=2,sort_keys=True))
    print("PASS_COMPLETE_TWO_DIGIT_COMPACT")

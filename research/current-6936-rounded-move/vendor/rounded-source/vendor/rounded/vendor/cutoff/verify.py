"""Bounded source, literal metadata and saved physical evidence gates.

Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from argparse import ArgumentParser
import json
from cutoff_sources import HERE,need


def main():
    parser=ArgumentParser();parser.add_argument("--suite",choices=("metadata","evidence"),required=True)
    parser.add_argument("--emit",action="store_true");args=parser.parse_args()
    if args.suite=="metadata":
        from check_transport import check
        from source_audit import check as audit
        result=dict(metadata=check(),source_audit=audit(),no_new_kappa=True)
        need(result["source_audit"]==json.loads((HERE/"SOURCE-AUDIT.json").read_text()),
             "exact standalone cutoff-consumer inventory")
        name="RESULT.json"
    else:
        from check_receipts import check
        result=check();name="EVIDENCE-RESULT.json"
    file=HERE/name
    if args.emit:file.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    else:need(json.dumps(result,sort_keys=True)==json.dumps(json.loads(file.read_text()),sort_keys=True),
              "exact expected cutoff-transport receipt")
    print("PASS_CURRENT_LEAF_CUTOFF_"+args.suite.upper(),json.dumps(dict(
        no_new_kappa=True,complete_MOVE_claim=False,registered_numeric_success_reexecution=False),sort_keys=True))


if __name__=="__main__":main()

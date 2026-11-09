"""Bounded independent arithmetic/interface and complete small-leaf replays.

Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from argparse import ArgumentParser
import json
from rounded_sources import HERE,need

def main():
    parser=ArgumentParser();parser.add_argument('--suite',choices=('interfaces','numeric'),required=True)
    parser.add_argument('--emit',action='store_true');args=parser.parse_args()
    from source_audit import check as audit
    if args.suite=='interfaces':
        from check_interfaces import check
        result=dict(source=audit(),interfaces=check(),no_new_kappa=True)
        file=HERE/'INTERFACE-RESULT.json'
    else:
        from check_rounded import numeric
        result=dict(source=audit(),numeric=numeric(),no_new_kappa=True)
        file=HERE/'NUMERIC-RESULT.json'
    if args.emit:file.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    else:need(json.dumps(result,sort_keys=True)==json.dumps(json.loads(file.read_text()),sort_keys=True),
              'exact expected rounded-leaf replay result')
    print('PASS_CURRENT_ROUNDED_POSITIVE_LEAF_'+args.suite.upper(),json.dumps(dict(
        no_new_kappa=True,full_MOVE=False,selected_producer_witness=False,ports=521),sort_keys=True))

if __name__=='__main__':main()

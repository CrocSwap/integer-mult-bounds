"""Bounded source/metadata/algebra and explicitly structural-only replays.

Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from argparse import ArgumentParser
import json
from rounded_move_sources import HERE,need

def main():
    parser=ArgumentParser();parser.add_argument('--suite',choices=('composition','structural'),required=True)
    parser.add_argument('--emit',action='store_true');args=parser.parse_args()
    from source_audit import check as audit
    if args.suite=='composition':
        from check_composition import check
    else:
        from check_structural import check
    result=dict(source=audit(),result=check(),new_numerical_whole_MOVE=False,no_new_kappa=True)
    file=HERE/(args.suite.upper()+'-EXPECTED.json')
    if args.emit:file.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    else:need(json.dumps(result,sort_keys=True)==json.dumps(json.loads(file.read_text()),sort_keys=True),
              'exact expected bounded once-rounded-MOVE replay')
    print('PASS_CURRENT_ROUNDED_SOURCE_MOVE_'+args.suite.upper(),json.dumps(dict(
        new_numerical_whole_MOVE=False,no_new_kappa=True,ports=4368),sort_keys=True))

if __name__=='__main__':main()

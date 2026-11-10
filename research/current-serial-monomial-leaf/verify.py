"""Bounded replays with source and exact-result authentication.

Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from argparse import ArgumentParser
from pathlib import Path
import json
import sys
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from serial_sources import authenticate, need


def stable(value):
    if isinstance(value,dict):
        return {k:stable(v) for k,v in value.items() if k!='elapsed_seconds'}
    if isinstance(value,(list,tuple)):
        return [stable(v) for v in value]
    return value


def main():
    parser=ArgumentParser()
    parser.add_argument('--suite',required=True,choices=('metadata','domain-history','descriptor','algebra','forward','inverse','phase-domain','history'))
    args=parser.parse_args(); sources=authenticate()
    suites={'metadata':('descriptor','algebra'),'domain-history':('phase-domain','history')}.get(args.suite,(args.suite,))
    expected=json.loads((ROOT/'RESULT.json').read_text());results={}
    for suite in suites:
        if suite=='descriptor':
            import check_descriptor
            result=check_descriptor.run()
        elif suite=='algebra':
            import check_algebra
            result=check_algebra.run()
        else:
            import check_numeric
            result=check_numeric.run(suite)
        need(stable(result)==expected[suite],'exact committed suite receipt')
        results[suite]=stable(result)
    print(json.dumps(dict(status='PASS_CURRENT_SERIAL_MONOMIAL_'+args.suite.upper(),
                         authenticated_source_files=sources,result=results),sort_keys=True))


if __name__=='__main__':main()

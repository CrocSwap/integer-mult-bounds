#!/usr/bin/env python3
"""Recompute the fixed PR186 conditional precision certificate, read-only."""
import argparse,json
from source_binding import HERE,check_sources,require
def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--write',action='store_true',help='Authoring only: write regenerated certificate');args=parser.parse_args()
    check_sources()
    import arithmetic as A
    result=A.regenerate();raw=(json.dumps(result,indent=2,sort_keys=True)+'\n').encode();path=HERE/'certificate.json'
    if args.write:path.write_bytes(raw)
    else:require(path.read_bytes()==raw,'stored certificate differs from exact recomputation')
    print('PASS pinned186 conditional kappa='+result['kappa']+'; both full moments,47 strict constraints,7 margins,first atom and next grids; complex limiter; separate finite scalar/bank checks and inherited all-size contracts remain explicit')
if __name__=='__main__':main()

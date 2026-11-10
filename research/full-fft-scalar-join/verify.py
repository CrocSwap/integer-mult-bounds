#!/usr/bin/env python3
"""Bounded exact source/owner/recovery evidence; receipt emission is explicit."""
import argparse
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from join_checks import run
from join_sources import need


def scientific(actual):
    result=dict(actual)
    for key in ('full','fast','erased'):
        result[key]=dict(actual[key])
        result[key].pop('actual_elapsed_seconds')
    return result


def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(',',':'))


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--emit',action='store_true',help='explicit author-only receipt creation')
    parser.add_argument('--progress',action='store_true')
    args=parser.parse_args()
    actual=run(args.progress)
    result=scientific(actual)
    path=HERE/'RESULT.json'
    if args.emit:
        path.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    else:
        need(canonical(result)==canonical(json.loads(path.read_text())),
             'complete typed source/physical scalar-join receipt')
    print(json.dumps(actual,indent=2,sort_keys=True))


if __name__=='__main__':
    main()

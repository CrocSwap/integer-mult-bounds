#!/usr/bin/env python3
"""Finite source binding only; run kernel.py explicitly for Lean verification."""
import argparse
import json
from pathlib import Path
from finite import replay, need


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-result', action='store_true')
    args = parser.parse_args()
    result = replay()
    path = Path(__file__).resolve().parent / 'FINITE.json'
    if args.write_result:
        path.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    else:
        need(json.loads(path.read_text(encoding='utf-8')) == result, 'finite receipt drift')
    print(result['status'] + ': kernel_checked=false, ' + str(len(result['negative_controls'])) + ' controls')


if __name__ == '__main__':
    main()

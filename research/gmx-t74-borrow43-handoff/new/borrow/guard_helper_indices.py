# Credit: PR2508 (ywz65), research/audit-helper-endpoint-indices/guard.py, vendored verbatim (Apache-2.0).
"""Validate the helper-only index domain before any Python indexing occurs."""
import argparse
import gzip
import json
from pathlib import Path
import re


def violations(word):
    v, count = word['report']['v'], word['report']['R']
    if type(v) is not int or type(count) is not int or v < 1 or count < 0:
        return [{'key': None, 'reason': 'invalid register extent'}]
    ends = word.get('helper_final', {})
    if type(ends) is not dict:
        return [{'key': None, 'reason': 'helper_final must be an object'}]
    bad = []
    for key in ends:
        if type(key) is not str or re.fullmatch(r'0|[1-9][0-9]*', key) is None:
            bad.append({'key': key, 'reason': 'canonical nonnegative decimal helper index required'})
        elif not 2*v <= int(key) < 2*v+count:
            bad.append({'key': key, 'reason': 'endpoint index is outside the helper interval'})
    return bad


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('word', type=Path)
    args = ap.parse_args()
    raw = args.word.read_bytes()
    word = json.loads(gzip.decompress(raw) if args.word.suffix == '.gz' else raw)
    bad = violations(word)
    print(json.dumps({'status': 'FAIL_HELPER_ENDPOINT_INDICES' if bad else
                     'PASS_HELPER_ENDPOINT_INDICES', 'violations': bad}, sort_keys=True))
    return bool(bad)


if __name__ == '__main__':
    raise SystemExit(main())

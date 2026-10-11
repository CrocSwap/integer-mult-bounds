#!/usr/bin/env python3
"""Bind the exact upstream PR348 certificate; full producer replay is mandatory in verify.py."""
import sys
if not __debug__: raise SystemExit('Assertions required')
sys.dont_write_bytecode = True
import argparse, gzip, hashlib, json
from pathlib import Path
ROOT = Path(__file__).resolve().parent
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--output',type=Path,required=True); a=ap.parse_args()
    assert not a.output.exists()
    pins=json.loads((ROOT/'SOURCE.json').read_text())
    raw=(ROOT/pins['candidate_path']).read_bytes()
    compressed=(ROOT/pins['candidate_gzip_path']).read_bytes()
    assert hashlib.sha256(compressed).hexdigest()==pins['candidate_gzip_sha256']
    assert hashlib.sha256(raw).hexdigest()==pins['candidate_sha256']
    assert gzip.decompress(compressed)==raw
    c=json.loads(raw)
    assert c['format']=='gcert/1' and (c['h'],c['v'],c['R'])==(20,960,6253)
    a.output.write_bytes(raw)
    print('PASS exact PR348 source program bytes; full regeneration is a separate mandatory stage')
if __name__=='__main__': main()

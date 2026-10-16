#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""End-to-end gzip-container tolerance and complete-payload rejection controls."""
import sys
sys.dont_write_bytecode = True
import argparse
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source', required=True, type=Path)
    ap.add_argument('--owner-engine', required=True, type=Path)
    ap.add_argument('--work', required=True, type=Path)
    args = ap.parse_args()
    work = args.work.resolve()
    if work.exists():
        raise ValueError('fresh control work directory required')
    work.mkdir(parents=True)
    script = Path(__file__).resolve().parents[1] / 'replay_allocation.py'
    spec = importlib.util.spec_from_file_location('controlled_replay', script)
    replay = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(replay)
    original_encode = replay.encode
    pins = replay.read(script.parent / 'PINS.json')
    original_argv = list(sys.argv)
    results = []
    try:
        for negative in (False, True):
            name = 'wrong-payload' if negative else 'repacked-container'
            out = work / name

            def controlled_encode(obj, compressed=False):
                raw = original_encode(obj, compressed)
                if not compressed:
                    return raw
                payload = gzip.decompress(raw)
                if negative:
                    changed = json.loads(payload)
                    changed['rows'][0][5] += 1
                    payload = original_encode(changed)
                return gzip.compress(payload, compresslevel=1, mtime=123456789)

            replay.encode = controlled_encode
            sys.argv = [str(script), '--source', str(args.source), '--owner-engine',
                        str(args.owner_engine), '--work', str(out)]
            try:
                replay.main()
            except ValueError as error:
                if not negative or 'realization differs from stored witness payload' not in str(error):
                    raise
                if out.exists():
                    raise AssertionError('wrong payload wrote an output directory')
                results.append({'control': name, 'status': 'PASS_REJECTED_BEFORE_OUTPUT', 'reason': str(error)})
            else:
                if negative:
                    raise AssertionError('wrong payload accepted')
                raw = (out / 'FILL.json.gz').read_bytes()
                container_sha = hashlib.sha256(raw).hexdigest()
                payload_sha = hashlib.sha256(gzip.decompress(raw)).hexdigest()
                if container_sha == pins['expected_output_sha256']['FILL.json.gz']:
                    raise AssertionError('positive control did not change the gzip container')
                if payload_sha != pins['expected_output_payload_sha256']['FILL.json.gz']:
                    raise AssertionError('positive control changed the payload')
                results.append({'control': name, 'status': 'PASS_ACCEPTED_IDENTICAL_FULL_PAYLOAD',
                                'container_sha256': container_sha, 'payload_sha256': payload_sha})
    finally:
        replay.encode = original_encode
        sys.argv = original_argv
    (work / 'COMPRESSION-CONTROLS.json').write_text(json.dumps(results, indent=2) + '\n')
    print(json.dumps(results, indent=2))


if __name__ == '__main__':
    main()

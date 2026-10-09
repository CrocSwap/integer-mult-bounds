#!/usr/bin/env python3
"""Rebuild PR217's changed bit word through PR217's own constructor.

Calls `candidate(bit_root)` from the butterfly package (the stage that produces the
changed graph, word and frames), writes the three emitted payloads into --out, and
checks them against the package's own `expected-bit.json` hashes.  Nothing in the
butterfly package or the PR202 checkout is modified, and no network is used.

    python3 rebuild_word.py --package <checkout>/research/butterfly-coordinated-bit-211 \
                            --bit-root <pr202 checkout> --out <fresh dir>
"""
import argparse
import hashlib
import importlib.util
import json
import sys
import time
from pathlib import Path


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--package', type=Path, required=True, help='the butterfly package directory')
    ap.add_argument('--bit-root', type=Path, required=True, help="a checkout of #202's head 8d8d67b")
    ap.add_argument('--out', type=Path, required=True, help='fresh directory for the emitted payloads')
    args = ap.parse_args()
    sys.set_int_max_str_digits(0)
    start = time.monotonic()
    pkg = args.package.resolve()
    if str(pkg) not in sys.path:
        sys.path.insert(0, str(pkg))
    cand = load('bfly_candidate', pkg / 'candidate.py')
    word, emitted, meta = cand.candidate(args.bit_root.resolve())
    print('[%.1fs] candidate built' % (time.monotonic() - start), flush=True)
    expected = json.loads((pkg / 'expected-bit.json').read_text())['emitted_sha256']
    got = {k: hashlib.sha256(v).hexdigest() for k, v in emitted.items()}
    ok = True
    for k in sorted(got):
        same = got[k] == expected.get(k)
        ok &= same
        print('  %-18s %s  %s' % (k, got[k][:16], 'matches expected-bit.json' if same else 'DIFFERS'))
    if not ok:
        raise SystemExit('emitted payloads differ from the package\'s own expected-bit.json')
    print('word: ops %d roles %d v %d h %d pairs %d gauges %d changed frames %d'
          % (len(word.ops), word.R, word.v, word.h, len(word.w.get('pairs', [])),
             len(word.w.get('gauges', [])), len(word.changed_frames)))
    args.out.mkdir(parents=True, exist_ok=True)
    for name, payload in emitted.items():
        (args.out / name).write_bytes(payload)
    (args.out / 'word-meta.json').write_text(json.dumps(
        {'emitted_sha256': got, 'changed_operation_frames': len(word.changed_frames),
         'source_head': meta.get('source_head') if isinstance(meta, dict) else None},
        indent=1, sort_keys=True) + '\n')
    print('wrote', args.out)


if __name__ == '__main__':
    main()

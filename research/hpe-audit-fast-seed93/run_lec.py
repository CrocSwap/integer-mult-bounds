#!/usr/bin/env python3
"""Run the unchanged leaver layer-end controls with the fast or cross-checked audit.

Invokes research/gauge44-leaver8/construction/leaver/layer_end_controls_leaver.py
exactly as reproduce_leaver_chain.py does (same portable wrapper, routing word
and environment), except that PR635_CODE names this package's shim directory.
Prepared by Wronskode (@Wronskode) with substantial AI assistance from Claude
(Anthropic) via Claude Code. Apache-2.0.
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys
import tarfile
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
LEAVER = ROOT / 'research/gauge44-leaver8/construction/leaver'
CONTROLS = LEAVER / 'layer_end_controls_leaver.py'
MULTICOLD = ROOT / 'research/complex-k492-owner-repair/vendor/multicold'
ROUTING = MULTICOLD / 'vendor/pr558/vendor/pr552/complex-local/inputs/phase-baseline/CANONICAL-WORD.json.gz'
ARCHIVE = ROOT / 'research/community-frontier1042-audit/selected-replay.tar.gz'
PR635_CODE = ROOT / 'research/complex-sw4-frame8/vendor/pr635/research/complex-571-cold14-st2/code'
PINS = {
    CONTROLS: '4ba676f1ea326b739a64c3477f64eeb295f8151514f78fa7e62b71e4373a6206',
    MULTICOLD / 'code/run_portable.py': '322d29d43dbee8130cde15d4bf05396698b5e3dfe3735813899db91cc0ba7955',
    ROUTING: 'e070ae2c78b4a1b644b418774af62b40d8d16e6ba89602f0474afb557d507c37',
    PR635_CODE / 'hpe_audit_and_transport.py': '0dacf4cedb020d561e0188052319f1a6e6abaf6c79f9e94d8c9c91492e5c1747',
    HERE / 'baseline.py': 'c9a05ff291016b870b4fc925b317abd9c3a604c73ffc8920dfdbbeb475e20aa3',
    LEAVER / 'LEC-REASON-PINS-k8.json': 'b07279e41ec9d8f89e8509081e1e7f2c8e8b062fd951b22608a03ac461982914',
    LEAVER / 'LEC-REASON-PINS-STACK-k8.json': 'd87ed7b5869bed4a3d266f0ce5fc784cbe88340a625d22ab9f580fa00872df19',
}


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument('--word', type=Path)
    src.add_argument('--archived', choices=['p6n', 'promo', 'jx', 'hyb', 'frames'],
                     help='use this word from the committed selected replay and compare with its archived receipt')
    ap.add_argument('--pins', required=True, choices=['LEC-REASON-PINS', 'LEC-REASON-PINS-STACK'])
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--mode', choices=['reference', 'fast', 'crosscheck'], default='fast')
    a = ap.parse_args()
    for path, digest in PINS.items():
        if sha(path) != digest:
            sys.exit('pinned input changed: %s' % path.relative_to(ROOT))
    out = a.out.resolve()
    if out.exists():
        sys.exit('output directory must not exist')
    out.parent.mkdir(parents=True, exist_ok=True)
    pins = LEAVER / ('%s-k8.json' % a.pins)
    archived = None
    if a.archived:
        with tarfile.open(ARCHIVE) as tar:
            data = tar.extractfile('chain/%s/FULL-WORD.json.gz' % a.archived).read()
            archived = json.loads(tar.extractfile('chain/lec-%s/COLD-END-CONTROLS.json' % a.archived).read())
        a.word = Path(tempfile.mkdtemp()) / 'FULL-WORD.json.gz'
        a.word.write_bytes(data)
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONUTF8='1', PYTHONINTMAXSTRDIGITS='0',
               MULTICOLD_SOURCE=str(MULTICOLD), GAIN_PR564_SOURCE=str(MULTICOLD), LEC_REASON_PINS=str(pins),
               PR635_CODE=str(PR635_CODE if a.mode == 'reference' else HERE / 'shim'),
               HPE_AUDIT_MODE='fast' if a.mode == 'reference' else a.mode,
               HPE_AUDIT_REFERENCE=str(HERE / 'baseline.py'),  # pairwise-era bytes for shim crosscheck
               HPE_AUDIT_CROSSCHECK_LOG=str(out.parent / (out.name + '.crosscheck.jsonl')))
    for k in ('PYTHONOPTIMIZE', 'XPARAM', 'EXTRAH', 'PAIRING_RANKS', 'DIAG', 'HYBBUDGET', 'SW4_PIN'):
        env.pop(k, None)
    cmd = [sys.executable, '-B', str(MULTICOLD / 'code/run_portable.py'), str(CONTROLS),
           str(a.word.resolve()), str(ROUTING), str(out)]
    t = time.monotonic()
    rc = subprocess.call(cmd, env=env, stdout=sys.stdout, stderr=subprocess.STDOUT)
    print('MODE %s exit %d seconds %.1f' % (a.mode, rc, time.monotonic() - t), flush=True)
    if rc == 0 and archived is not None:
        got = json.loads((out / 'COLD-END-CONTROLS.json').read_text())
        got.pop('word'), archived.pop('word')
        if got != archived:
            sys.exit('receipt differs from the archived maintainer receipt')
        print('PASS receipt equals the archived lec-%s receipt (apart from the word path)' % a.archived)
    sys.exit(rc)


if __name__ == '__main__':
    main()

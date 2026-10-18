#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Registered check (standard library only): complete package inventory (MANIFEST.json) and pins (PINS.json); verify.py
and census.py rerun in a temporary directory, their regenerated receipts byte-equal to certificates/; lane K's stored
receipts (evidence/laneK/: the r12-harness NEGATIVE certificates, the cross-check of lane K's current bound.py and
lbforced.py) bound to this package's recomputation. Structure follows our PR2942/PR2979 run_registered.py (Mason Hale's
PR2917 lineage). Marius-Paul Dumitrean, with substantial AI assistance (Claude Code).
"""
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

P = Path(__file__).resolve().parent
LANEK = {'bound.py': '6b1479b436c4f01bb32f771aa06af3d2260adee5dd5a5e2bf568b0192cee69d8',
         'lbforced.py': 'bd81e3f4460f61ef81e15e76ab25be5f8a9d7b71bb7dcbbf7a87873ca5398341'}


def require(ok, message):
    if not ok:
        raise SystemExit('FAIL: ' + message)


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def tree():
    require(not any(f.is_symlink() for f in P.rglob('*')), 'no symlinks')
    return {f.relative_to(P).as_posix(): sha(f) for f in P.rglob('*')
            if f.is_file() and f.name != 'MANIFEST.json' and '__pycache__' not in f.parts}


def read(rel):
    return json.loads((P / rel).read_bytes())


def main():
    manifest = read('MANIFEST.json')
    require(tree() == manifest, 'complete package inventory (MANIFEST.json)')
    pins = read('PINS.json')
    require(all(sha(P / rel) == h for rel, h in pins.items()), 'PINS.json')
    with tempfile.TemporaryDirectory(prefix='rank7-skip-restore-') as tmp:
        out = Path(tmp)
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
        for key in ('PYTHONOPTIMIZE', 'PYTHONPATH', 'PYTHONSTARTUP'):
            env.pop(key, None)
        for script in ('verify.py', 'census.py'):
            log = out / (script + '.log')
            with log.open('w') as stream:
                r = subprocess.run([sys.executable, '-B', '-W', 'error', str(P / script), '--work', str(out / 'regen')],
                                   env=env, stdin=subprocess.DEVNULL, stdout=stream, stderr=subprocess.STDOUT, cwd=str(out))
            text = log.read_text()
            if r.returncode:
                print(text[-6000:])
                raise SystemExit(r.returncode)
            print('PASS', script, text.strip().splitlines()[-1][:200], flush=True)
        regen = sorted(f.name for f in (out / 'regen').iterdir())
        stored = sorted(f.name for f in (P / 'certificates').iterdir())
        require(regen == stored, 'regenerated receipt set equals certificates/ (%s vs %s)' % (regen, stored))
        for name in regen:
            require((out / 'regen' / name).read_bytes() == (P / 'certificates' / name).read_bytes(), 'receipt ' + name)
    res = read('certificates/RESULT.json')
    require(res['status'] == 'PASS_RANK7_SKIP_RESTORE_OPTIMUM' and res['no_new_kappa'] and res['providers'] == 2, 'RESULT status')
    for prov in ('base', 'extra'):
        cert = read('certificates/BOUND-3042-%s.json' % prov)
        neg = read('evidence/laneK/NEGATIVE-3042-%s.json' % prov)
        require(cert['bound'] == cert['certified_cost'] == neg['certified_cost'] == neg['LB_plus_forced'], 'lane K certified cost ' + prov)
        require(cert['LB_forced'] == neg['LB_forced'] and cert['LB_profile'] == neg['LB_profile'], 'lane K LB_forced ' + prov)
        require(cert['forced_caps'] == neg['forced_caps'] == len(neg['caps']), 'lane K cap count ' + prov)
        require(all(cert['caps'][r]['cap'] == v['cap'] and cert['caps'][r]['receivers'] == v['receivers'] for r, v in neg['caps'].items()),
                'lane K caps (frames and receivers) ' + prov)
        require(cert['literal_visits'] == neg['visits'] and cert['literal_visit_units'] == neg['sum_forced_extras'], 'lane K visits ' + prov)
        require((cert['blocked'], cert['extras_blocked']) == (neg['blocked'], neg['blocked_units']), 'lane K blocked ' + prov)
        require(cert['extras_open'] == neg['open_units'] and cert['payer_groups'] == neg['open_but_forced'], 'lane K open-but-forced ' + prov)
    cross = read('evidence/laneK/CROSSCHECK.json')
    require(cross['status'] == 'PASS_LANEK_CROSSCHECK' and cross['laneK_files'] == LANEK, 'cross-check names the current lane K files')
    require(all(sha(P / 'evidence/laneK' / f) == h for f, h in LANEK.items()), 'pinned lane K files')
    require(len(cross['rows']) == 8 and all(r['agree'] for r in cross['rows']), 'lane K current bound agrees on 4 words x 2 restores')
    require(tree() == manifest, 'inventory unchanged by the replay')
    print('PASS_RANK7_SKIP_RESTORE_OPTIMUM_REGISTERED cost=%d LB_forced=%d forced=%d caps=%d (both providers; calibration gap %d; '
          'no new kappa)' % (res['certified_cost'], res['LB_forced'], res['forced_extras'], res['forced_caps'], res['calibration_gap_2979']))


if __name__ == '__main__':
    main()

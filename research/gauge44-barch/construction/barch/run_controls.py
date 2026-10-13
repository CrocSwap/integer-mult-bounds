#!/usr/bin/env python3
"""run_controls.py BASE_WORD RECIPE AUDIT_LOCAL_PY OUTDIR : C0 identity, the recipe word (must PASS) and the four negative
controls (each must FAIL audit_local with its pinned message prefix). Standard library only; writes OUTDIR/controls.json."""
import sys, json, subprocess, os, gzip, hashlib
base, recipe, audit, out = sys.argv[1:5]
here = os.path.dirname(os.path.abspath(__file__)); os.makedirs(out, exist_ok=True)
# pinned rejection sites (observed on RECIPE-V1 and RECIPE-B0; the failing rows are recorded in controls.json): the holder 485 is not restored; the low-end restore 497-=451 moved to the
# FULL cleanup runs after 451's own tail and leaves 497 wrong; without the pre-read (or with the donation after the read)
# the entering helper's start value reaches a target.
EXPECT = {None: 'PASS', 'drop_restore': 'all-column endpoint failure (False, ',
          'restore_full': 'all-column endpoint failure (False, ',
          'drop_preread': 'nonzero entrance response', 'donation_after': 'nonzero entrance response'}
res = {}
ident = os.path.join(out, 'C0.json')
json.dump(dict(json.load(open(recipe)), B_delete=[], B_insert=[], B_frames={}, tail_insert=[], cleanup_prepend=[],
               local_profile=json.loads(gzip.decompress(open(base, 'rb').read()))['report']['local_profile'],
               expect_sha256=hashlib.sha256(gzip.decompress(open(base, 'rb').read())).hexdigest()), open(ident, 'w'))
r = subprocess.run([sys.executable, '-B', os.path.join(here, 'build_tri.py'), base, ident, os.path.join(out, 'C0.json.gz')], capture_output=True, text=True)
res['C0_identity'] = dict(ok=r.returncode == 0, out=r.stdout.strip() or r.stderr.strip()[-200:])
ctls = list(EXPECT) + [c + '@' + str(s['X']) for s in json.load(open(recipe)).get('variants', []) for c in EXPECT if c]
for ctl in ctls:
    name = ctl or 'recipe'; wp = os.path.join(out, name + '.json.gz')
    cmd = [sys.executable, '-B', os.path.join(here, 'build_tri.py'), base, recipe, wp] + (['--control', ctl] if ctl else [])
    b = subprocess.run(cmd, capture_output=True, text=True)
    if b.returncode: res[name] = dict(ok=False, build=b.stderr[-300:]); continue
    a = subprocess.run([sys.executable, '-B', audit, '--word', wp, '--output', os.path.join(out, name + '.audit.json')], capture_output=True, text=True)
    txt = a.stdout + a.stderr
    if ctl is None: ok = a.returncode == 0 and 'PASS_INDEPENDENT' in txt
    else: ok = a.returncode != 0 and EXPECT[ctl.split('@')[0]] in txt
    res[name] = dict(ok=ok, build=json.loads(b.stdout), audit_tail=txt.strip().splitlines()[-1][:200])
json.dump(res, open(os.path.join(out, 'controls.json'), 'w'), indent=1)
print(json.dumps({k: x['ok'] for k, x in res.items()}))
sys.exit(0 if all(x['ok'] for x in res.values()) else 1)

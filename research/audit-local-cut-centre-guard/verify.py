#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Registered check: the unchanged local auditor accepts a word whose cut gates read a non-centre helper; guard.py
rejects it, and accepts the genuine words.

Checks:
  1. input pins: SHA-256 and Git blob ids of the three words equal inputs/PINS.json, and those of the two declared
     repository inputs (the auditor, and the parent CANONICAL-WORD that its --main interface check reads) equal SOURCES.json;
  2. the gap: research/gauge44-frames-x/independent/audit_local.py --main (unchanged, pinned in SOURCES.json) PASSES
     both the genuine base word and the probe word PROBE-CUT-502 (four non-centre cut gates, helper 502 entering);
     the receipts' status, compensation size, entering count and local profile equal evidence/AUDIT-*.json;
  3. the guard: PASS on the base and extra words, FAIL on the probe with exactly its four cut gates;
  4. controls: the guard rejects a base word with one cut source replaced by a non-centre helper, and one with a cut
     target replaced by a non-target row.
The native provider chain's rejection of the probe (hpe_emit_local.py: 'emitted column mismatch', register 153) is
recorded evidence (evidence/NATIVE-PROBE.txt), not rerun here."""
import copy, gzip, hashlib, json, subprocess, sys, tempfile
from pathlib import Path
if not __debug__:
    raise SystemExit('verify.py: do not run with -O (the registered replay runs unoptimised)')
PKG = Path(__file__).resolve().parent
ROOT = PKG.parents[1]
sys.path.insert(0, str(PKG))
import guard  # noqa: E402
AUDITOR = ROOT / 'research/gauge44-frames-x/independent/audit_local.py'
PARENT = ROOT / 'research/community-k492-audit/pr622/replay/baseline558/complex-global/base/split-centres/CANONICAL-WORD.json.gz'  # read by --main
rd = lambda p: json.loads(Path(p).read_text(encoding='utf-8'))
def blob(b): return hashlib.sha1(b'blob %d\0' % len(b) + b).hexdigest()
def require(ok, msg):
    if not ok: raise SystemExit('FAIL: ' + msg)

pins = rd(PKG / 'inputs/PINS.json')['files']
for name, pin in pins.items():
    b = (PKG / 'inputs' / name).read_bytes()
    require(hashlib.sha256(b).hexdigest() == pin['sha256'] and blob(b) == pin['git_blob'], 'input pin ' + name)
src = {r['path']: r for r in rd(PKG / 'SOURCES.json')['files'] if r['usage'] == 'input'}
for path in (AUDITOR, PARENT):
    pin = src[path.relative_to(ROOT).as_posix()]
    require(path.is_file(), 'declared input missing: ' + pin['path'])
    b = path.read_bytes()
    require(hashlib.sha256(b).hexdigest() == pin['sha256'] and blob(b) == pin['git_blob'], 'declared input changed: ' + pin['path'])

def audit(name, out):
    rc = subprocess.run([sys.executable, '-B', str(AUDITOR), '--word', str(PKG / 'inputs' / name), '--output', str(out),
                         '--main', str(ROOT)], cwd=ROOT, capture_output=True, text=True).returncode
    require(rc == 0, 'auditor exit %d on %s' % (rc, name))
    r = rd(out); keep = ('status', 'compensation_gates', 'local_profile')
    return {k: r.get(k) for k in keep} | {'entering': len(json.loads(gzip.decompress((PKG / 'inputs' / name).read_bytes())).get('start_extra', {}))}

with tempfile.TemporaryDirectory() as d:
    for name, ev in (('BASE-WORD.json.gz', 'AUDIT-BASE.json'), ('PROBE-CUT-502.json.gz', 'AUDIT-PROBE.json')):
        got = audit(name, Path(d) / ev)
        require(got['status'] == 'PASS_INDEPENDENT_EXACT_FORWARD_AND_DUAL_ENDPOINT_FRAMES_ENTRANCES_CONES', 'auditor did not pass ' + name)
        require(got == rd(PKG / 'evidence' / ev), 'auditor receipt differs from evidence/' + ev)
        print('auditor PASS', name, got['compensation_gates'], 'compensation gates,', got['entering'], 'entering', flush=True)

words = {n: json.loads(gzip.decompress((PKG / 'inputs' / n).read_bytes())) for n in pins}
require(guard.violations(words['BASE-WORD.json.gz']) == [] and guard.violations(words['EXTRA-WORD.json.gz']) == [], 'guard rejects a genuine word')
bad = guard.violations(words['PROBE-CUT-502.json.gz'])
require([b['gate'] for b in bad] == rd(PKG / 'evidence/GUARD-PROBE.json')['violations_gates'], 'guard probe violations differ')
print('guard PASS base, PASS extra, FAIL probe with', len(bad), 'non-centre cut gates', flush=True)

base = words['BASE-WORD.json.gz']; v = base['report']['v']
c1 = copy.deepcopy(base); c1['cut'][0] = list(c1['cut'][0]); c1['cut'][0][2] = 502
c2 = copy.deepcopy(base); c2['cut'][0] = list(c2['cut'][0]); c2['cut'][0][1] = 2 * v + 5
require(len(guard.violations(c1)) == 1 and len(guard.violations(c2)) == 1, 'guard controls')
print('controls: non-centre source and non-target row both rejected', flush=True)
print('PASS_AUDIT_LOCAL_CUT_CENTRE_GUARD auditor-accepts-probe guard-rejects-probe', flush=True)

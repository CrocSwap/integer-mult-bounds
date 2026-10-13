# R480 at nine stages: the R480 bit word (PR #503) priced in the nine-stage whole-residual hosted pipeline. Verifier.
# Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code. Apache-2.0.
"""usage: python verify.py /absolute/new/output [--light]

Runs the parent PR #503 verifier (research/e8-r480-dead-totals/verify.py, with --light in light mode), which rebuilds
the R480 word and passes it through PR #493's full checker chain, then prices that same word at nine stages: nine-stage
formal columns, the vendored PR #463 nine-stage template, parent audit, hosting emitter and hosted audit (32 replicas,
PR #386 nine-stage geometry, PR #442 whole-residual hosting), the nine-stage bit invoice and both moment engines, and
PR #493's outer assembly per cited complex supplier (47 strict inequalities and controls).
Needs what the parent needs (Python 3.11+, numpy, sympy, scipy; a C++17 compiler CXX; Boost headers BOOST_INCLUDE)."""
import gzip, hashlib, json, os, subprocess, sys, time
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve().parent
R503 = HERE.parent / 'e8-r480-dead-totals'; PARENT = HERE.parent / 'e8-bit-carrier-skeleton'
args = [a for a in sys.argv[1:] if not a.startswith('--')]; LIGHT = '--light' in sys.argv
assert len(args) == 1, __doc__
WD = Path(args[0]).resolve(); WD.mkdir(parents=True, exist_ok=True)
assert not str(WD).startswith(str(HERE.parent)), 'output dir must be outside research/'
PY = sys.executable; CXX = os.environ.get('CXX', 'c++'); BI = os.environ.get('BOOST_INCLUDE', '/usr/include')
ENV = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONINTMAXSTRDIGITS='0')
VK = HERE / 'vendor/e8-r715-eleven-stage-whole/code'
CK = PARENT / 'code/bit/checkers'
WORD = R503 / 'data/bitE8mut-r480.json.gz'; SEL = HERE / 'data/selection9-r480.json'
EXP = json.loads((HERE / 'EXPECTED.json').read_text())
T0 = time.time()


def run(cmd, cwd=None, ok=True, quiet=True):
    p = subprocess.run([str(x) for x in cmd], cwd=cwd, env=ENV, capture_output=True, text=True)
    if ok and p.returncode != 0:
        sys.stderr.write(p.stdout[-3000:] + p.stderr[-3000:]); raise SystemExit('FAILED: %s' % ' '.join(map(str, cmd)))
    if not quiet:
        for line in p.stdout.rstrip().splitlines(): print('   ' + line)
    return p


def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def blob(p):
    b = Path(p).read_bytes(); return hashlib.sha1(b'blob %d\0' % len(b) + b).hexdigest()


def step(s): print('== %s  [%.0fs]' % (s, time.time() - T0), flush=True)


# ------------------------------------------------------------------------------------------------------------------
step('0. manifest (MANIFEST.json), vendored provenance (SOURCE.json git blob ids), pinned parent manifests')
man = json.loads((HERE / 'MANIFEST.json').read_text())
for rel, h in man['files'].items(): assert sha(HERE / rel) == h, ('MISMATCH', rel)
listed = set(man['files']) | {'MANIFEST.json'}
present = {str(p.relative_to(HERE)) for p in HERE.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
assert present == listed, ('unlisted or missing files', sorted(present ^ listed))
assert sha(R503 / 'MANIFEST.json') == man['parent_r480_manifest_sha256'], 'PR #503 MANIFEST.json changed'
assert sha(PARENT / 'MANIFEST.sha256') == man['parent_r489_manifest_sha256'], 'PR #493 MANIFEST.sha256 changed'
src = json.loads((HERE / 'SOURCE.json').read_text())
vend = {str(p.relative_to(HERE)) for p in (HERE / 'vendor').rglob('*.py')}
assert vend == set(src['files']), 'vendored set differs from SOURCE.json'
for rel, e in src['files'].items():
    assert blob(HERE / rel) == e['git_blob'] and sha(HERE / rel) == e['sha256'], rel
hub = PARENT / 'code/hub'
for rel, other in (('vendor/e8-r740-replica32/code/bank_routes.py', hub / 'e8-r740-replica32/code/bank_routes.py'),
                   ('vendor/e8-r740-replica32/code/tile_m.py', hub / 'e8-r740-replica32/code/tile_m.py'),
                   ('vendor/e8-r740-replica32/code/e8core.py', hub / 'e8-r740-replica32/code/e8core.py'),
                   ('vendor/idle-axis-hosting/hosting_core.py', hub / 'idle-axis-hosting/hosting_core.py'),
                   *(('vendor/e8-r740-replica32/code/engines/%s.py' % n, hub / ('e8-r740-replica32/code/engines/%s.py' % n))
                     for n in ('moment', 'base_two_moment', 'outer'))):
    assert (HERE / rel).read_bytes() == other.read_bytes(), rel
print('   %d package files match MANIFEST.json; %d vendored files match PR #%d (head %s) by git blob id; 7 of them are also'
      ' byte-identical to PR #493\'s vendored copies' % (len(man['files']), len(vend), src['pull_request'], src['head'][:7]))

# ------------------------------------------------------------------------------------------------------------------
step('P. parent: PR #503 verify.py%s (R480 rebuilt and checked by PR #493\'s full chain at eleven stages)' % (' --light' if LIGHT else ''))
PD = WD / 'parent'
run([PY, '-B', R503 / 'verify.py', PD] + (['--light'] if LIGHT else []), quiet=True)
r11 = json.loads((PD / 'RESULT.json').read_text())
assert r11['bit_lower'] == EXP['parent_r480']['bit_lower']
print('   PASS (R480 eleven-stage bit c = %s, as PR #503)' % r11['bit_lower_decimal'])

# ------------------------------------------------------------------------------------------------------------------
step('1. nine-stage formal columns (PR #381 columns_k with KPAIRS = 4) on the parent\'s R480 records')
BIN = WD / 'bin'; BIN.mkdir(exist_ok=True)
run([CXX, '-O2', '-std=c++17', '-DHDIM=8', '-DNCOPY=9', '-DVPORTS=120', '-DRHELP=480', '-DKPAIRS=4',
     '-I%s' % (PARENT / 'portable-include'), '-I%s' % CK, '-I%s' % BI, '-o', BIN / 'columns_k4', CK / 'columns_k.cpp'])
run([BIN / 'columns_k4', PD / 'cout/COHORT249-RECORDS.bin', WD / 'columns_k4.json'])
k4 = json.loads((WD / 'columns_k4.json').read_text())
assert k4['status'] == 'PASS_NEW_COHORT249_ALL_BRIDGED_STAGE_FORMAL_COLUMNS_AND_PREFIX_BILL'
assert k4['formal_columns_checked'] == 8 * 120 + 480 and len(k4['stages']) == 9 and k4['bridge_additions'] == 18 * 120
assert len(k4['negative_controls']) == 18 and all(x['rejected'] for x in k4['negative_controls'])
print('   PASS: %d physical columns over F2 through 9 invocations, %d bridge additions, 18/18 omitted-bridge controls'
      ' rejected; prefix payload %d bits < 104' % (k4['formal_columns_checked'], k4['bridge_additions'], k4['payload_prefix_bits']))

# ------------------------------------------------------------------------------------------------------------------
step('2. nine-stage template (vendored global_k.py) and parent audit (audit_parent_k.py, one listed adaptation)')
V9 = WD / 'v9'; (V9 / 'nine').mkdir(parents=True, exist_ok=True)
geo = PD / 'nine/GEOMETRY.json'      # PR #386 nine-stage geometry, built by PR #493's code/nine/geometry.py in the parent run
g9 = json.loads(geo.read_text()); assert g9['status'] == 'PASS_COMPRESSED_NINE_BIT_GEOMETRY_AND_BANK_BLOCKS' and g9['m'] == 64 and g9['stages'] == 9
(V9 / 'nine/GEOMETRY.json').write_bytes(geo.read_bytes())
if not (V9 / 'records').exists(): (V9 / 'records').symlink_to(PD / 'records')
ISO = PARENT / 'data/eleven/residual-isometries.json'
run([PY, '-B', VK / 'global_k.py', '--word', WORD, '--local-check', PD, '--out', V9 / 'nine', '--isometries', ISO])
g = json.loads((V9 / 'nine/GLOBAL.json').read_text())
assert g['R'] == 480 and g['replicas'] == 32 and g['m'] == 64 and g['local_invocations'] == 9 * 32
print('   template PASS: %s; %d local invocations, %d unbanked scalar columns restored, %d omitted bridge shears rejected,'
      ' prefix %d bits' % (g['status'], g['local_invocations'], g['independent_unbanked_scalar_columns'],
                           len(g['omitted_bridge_shears_rejected']), g['global_prefix_bits']))
run([PY, '-B', HERE / 'code/adapt.py', VK, WD / 'adapted'], quiet=False)
run([PY, '-B', WD / 'adapted/audit_parent_k.py', '--local-check', PD, '--out', V9 / 'nine', '--word', WORD])
ap = json.loads((V9 / 'nine/AUDIT.json').read_text())
assert ap['status'] == 'PASS_INDEPENDENT_COMPRESSED_BIT_TEMPLATE_AUDIT' and 'omit a residual route factor' not in ap['mutations_rejected']
print('   parent audit PASS: %d template mutations rejected (the route-factor control is vacuous here: no isometry has a'
      ' route factor)' % len(ap['mutations_rejected']))

# ------------------------------------------------------------------------------------------------------------------
step('3. whole-residual hosting (PR #442 programme via the vendored emitter), hosted audit')
run([PY, '-B', VK / 'emit_k.py', V9 / 'nine', PD, V9 / 'hosted', '--selection', WD / 'selection9.json', '--key', 'bit', '--discover'])
assert json.loads((WD / 'selection9.json').read_text()) == json.loads(SEL.read_text()), 'rediscovered selection differs'
run([PY, '-B', VK / 'audit_hosted_k.py', V9, V9 / 'hosted', V9 / 'hosted/AUDIT.json'])
au = json.loads((V9 / 'hosted/AUDIT.json').read_text())
assert au['status'] == 'PASS_INDEPENDENT_REPLICATED_HOSTING_AUDIT' and au['hosted_residuals'] == 9 * 32 * 480 and au['bank_assignments'] == 0
print('   the hosting programme rediscovers data/selection9-r480.json exactly; hosted audit PASS: %d of %d helper'
      ' residuals hosted whole on idle data coordinates, %d banks, %d renamed instructions, %d mutations rejected'
      % (au['hosted_residuals'], 9 * 32 * 480, au['bank_assignments'], au['emitted_events'], len(au['mutations_rejected'])))

# ------------------------------------------------------------------------------------------------------------------
step('4. nine-stage bit invoice, both moment engines, outer assembly per cited complex supplier')
run([PY, '-B', HERE / 'code/assemble9.py', V9, V9 / 'hosted', V9 / 'hosted/AUDIT.json', PARENT, WD / 'RESULT.json',
     'pr484,pr471,pr458'], quiet=False)
r = json.loads((WD / 'RESULT.json').read_text())

# ------------------------------------------------------------------------------------------------------------------
step('5. findings on the R489 family: (a) LP floor and tight levels, (b) kernel pivots')
FD = HERE / 'code/findings'; ef = EXP['findings']
# (a) min-flow LP on the frame lattice of one 4-frame with the junk-dimension node bounds (cross cell >= 3, matching >= 4)
out = run([PY, '-B', FD / 'flowlp2.py']).stdout
assert 'no junk lemma (donors + 2 wires per cell only): 8.0 per 4-frame' in out
assert 'junk lemma node inflow cross>=3, matching>=4: 16.0 per 4-frame -> 480.0 +9 totals = 489.0' in out
# ... and R480's own frame visits: every node bound attained, levels 2 (180 cells) and 6 (180 D6 frames) tight
lv = {}
for name, w in (('r480', WORD), ('r489', PARENT / 'data/bit/bitE8mut-r489.json.gz')):
    run([PY, '-B', FD / 'levels.py', w, WD / ('levels-%s.json' % name)])
    lv[name] = json.loads((WD / ('levels-%s.json' % name)).read_text())
    assert lv[name]['levels'] == ef['levels'] and lv[name]['cells'] == ef['cells'] and lv[name]['d6'] == ef['d6'], name
a = lv['r480']
assert a['R'] == 480 and a['levels']['2']['helper_visits'] == a['levels']['6']['helper_visits'] == 480
assert a['cells'] == {'2,2,0': 60, '3,0,0': 120}      # matching cells: 2 helpers + 2 sources = 4; cross cells: 3 helpers
print('   (a) LP: 16 helpers per 4-frame -> 480 (8 without the junk-dimension bounds). R480 attains it: every cross cell'
      ' holds 3 helpers, every matching cell 2 helpers + 2 sources; all 480 helpers visit exactly one cell (level 2) and'
      ' exactly one D6 frame (level 6), so both antichains are tight; levels 1/4/7 carry %d/%d/%d. R489 has the same'
      ' visits plus its 9 fresh totals.' % (a['levels']['1']['helper_visits'], a['levels']['4']['helper_visits'], a['levels']['7']['helper_visits']))
# (b) kernel pivots: every root-line entrance class has independent delivery vectors
for name, w in (('r480', WORD), ('r489', PARENT / 'data/bit/bitE8mut-r489.json.gz')):
    out = run([PY, '-B', FD / 'piv0.py', w, WD / ('piv0-%s.json' % name)]).stdout
    assert 'class nullity Counter({0: 120})' in out and 'sum nullity all 0 coord 0' in out, name
    assert name == 'r480' or 'class sizes Counter({6: 120})' in out
print('   (b) kernel pivots: on R480 and R489 all 120 root-line entrance classes (on R489 6 helpers each: 2 carriers of'
      ' the line, 4 cell registers through it; on R480 the 9 total hosts are excluded, as the kernel requires) have'
      ' nullity 0, so the maximum pivot count is 0 for coordinate and root-line entrances of any rank')

# ------------------------------------------------------------------------------------------------------------------
step('6. summary against EXPECTED.json')
e = EXP['nine']
assert r['bit_lower'] == e['bit_lower'] and r['bit_profile'] == e['profile']
for k_ in e['bit']: assert r['bit'][k_] == e['bit'][k_], k_
for name, x in e['kappa'].items():
    assert r['kappa'][name]['kappa'] == x['kappa'] and r['kappa'][name]['binding_component'] == x['binding_component'], name
assert k4['payload_prefix_bits'] == e['nine_stage_payload_bits']
c, c493, c503 = F(r['bit_lower']), F(EXP['parent_r489']['bit_lower']), F(EXP['parent_r480']['bit_lower'])
print('PASS bit c (R = 480, nine stages, 32 replicas, every helper residual hosted whole, 10^-24 grid) = %s = %s'
      % (r['bit_lower'], r['bit_lower_decimal']))
print('     %+.4f%% over PR #493 (R489, eleven stages, %s); %+.4f%% over PR #503 (R480, eleven stages, %s)'
      % (100 * float(c / c493 - 1), EXP['parent_r489']['bit_lower_decimal'], 100 * float(c / c503 - 1), EXP['parent_r480']['bit_lower_decimal']))
for name in ('pr484', 'pr471', 'pr458'):
    k_ = r['kappa'][name]
    print('     with %s complex b = %s: kappa = %s = %s (%s-bound)' % (name, k_['complex_lower'], k_['kappa'], k_['kappa_decimal'], k_['binding_component']))
print('PASS %s  [%.0fs]' % ('LIGHT' if LIGHT else 'FULL', time.time() - T0))

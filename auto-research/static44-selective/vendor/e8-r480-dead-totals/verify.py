# R480: PR #493's bit word with its nine decoder totals hosted on dead registers. Verifier.
# Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code. Apache-2.0.
"""usage: python verify.py /absolute/new/output [--light]

FULL runs PR #493's verify.sh unchanged (the parent: its word, checkers, pipeline, controls and compositions), then
everything below. --light skips the parent run; the parent's manifest is still checked and its R489 price is still
reproduced through its own unmodified files (step 6).
Needs Python 3.11+ with numpy and sympy (scipy for the hosting rediscovery), a C++17 compiler (CXX) and Boost headers
(BOOST_INCLUDE), as the parent does."""
import gzip, hashlib, json, os, re, subprocess, sys, time
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve().parent
PARENT = HERE.parent / 'e8-bit-carrier-skeleton'
args = [a for a in sys.argv[1:] if not a.startswith('--')]
LIGHT = '--light' in sys.argv
assert len(args) == 1, __doc__
WD = Path(args[0]).resolve(); WD.mkdir(parents=True, exist_ok=True)
assert not str(WD).startswith(str(HERE.parent)), 'output dir must be outside research/'
PY = sys.executable; CXX = os.environ.get('CXX', 'c++'); BI = os.environ.get('BOOST_INCLUDE', '/usr/include')
ENV = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
C, B = PARENT / 'code', PARENT / 'code/bit'; CK = B / 'checkers'; HUB = C / 'hub'
WORD = HERE / 'data/bitE8mut-r480.json.gz'; HOST = HERE / 'data/hosting-r480.json'
EXP = json.loads((HERE / 'EXPECTED.json').read_text())
INC = ['-I%s' % (PARENT / 'portable-include'), '-I%s' % CK, '-I%s' % BI]
T0 = time.time()


def run(cmd, cwd=None, ok=True, quiet=True, env=None):
    p = subprocess.run([str(x) for x in cmd], cwd=cwd, env=env or ENV, capture_output=True, text=True)
    if ok and p.returncode != 0:
        sys.stderr.write(p.stdout[-3000:] + p.stderr[-3000:]); raise SystemExit('FAILED: %s' % ' '.join(map(str, cmd)))
    if not quiet:
        for line in p.stdout.rstrip().splitlines(): print('   ' + line)
    return p


def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def content_sha(w): return hashlib.sha256(json.dumps(w, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def load(p): return json.loads(gzip.decompress(Path(p).read_bytes()))


def step(s): print('== %s  [%.0fs]' % (s, time.time() - T0), flush=True)


# ------------------------------------------------------------------------------------------------------------------
step('0. manifests: this package (MANIFEST.json) and the parent package (its MANIFEST.sha256, as its step 0)')
man = json.loads((HERE / 'MANIFEST.json').read_text())
for rel, h in man['files'].items():
    assert sha(HERE / rel) == h, ('MISMATCH', rel)
listed = set(man['files']) | {'MANIFEST.json'}
present = {str(p.relative_to(HERE)) for p in HERE.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
assert present == listed, ('unlisted or missing files', sorted(present ^ listed))
assert sha(PARENT / 'MANIFEST.sha256') == man['parent_manifest_sha256'], 'parent MANIFEST.sha256 changed'
bad = 0
for line in (PARENT / 'MANIFEST.sha256').read_text().splitlines():
    h, p = line.split('  ', 1)
    if sha(PARENT / p) != h: print('PARENT MISMATCH', p); bad += 1
assert not bad
print('   %d package files and %d parent files match their manifests' % (len(man['files']),
      len((PARENT / 'MANIFEST.sha256').read_text().splitlines())))

if not LIGHT:
    step('P. parent: PR #493 verify.sh, unchanged')
    run(['bash', PARENT / 'verify.sh', WD / 'parent'], env=dict(ENV, PYTHON=PY), quiet=False)

# ------------------------------------------------------------------------------------------------------------------
step('1. the R480 word, rebuilt from the parent plan; the parent generator itself, for control')
AD = WD / 'adapted'
run([PY, '-I', '-B', HERE / 'code/adapt.py', PARENT, WORD, AD], quiet=False)
plan = dict(ENV, PLAN=str(PARENT / 'data/skeleton/plan-skB.json'))
(WD / 'gen').mkdir(exist_ok=True); (WD / 'gen0').mkdir(exist_ok=True)
run([PY, '-I', '-B', AD / 'gen_r480.py', WD / 'gen/word.json.gz', '0', 'fresh0'], cwd=WD / 'gen', env=plan)
assert (WD / 'gen/word.json.gz').read_bytes() == WORD.read_bytes(), 'rebuilt word differs from the shipped word'
w = load(WORD); w489 = load(PARENT / 'data/bit/bitE8mut-r489.json.gz')
assert content_sha(w) == EXP['word']['content_sha256'] and w['R'] == 480 and len(w['ret']) == 9
# what changed: nine fewer helpers, no fresh total registers; same frames, sources, cells, quads, Q-nodes, phase B
assert w['frames'] == w489['frames'] and w['lines'] == w489['lines'] and w['scatter'] == w489['scatter']
assert len(w['A']) == len(w489['A']) and len(w['C']) == len(w489['C']) and w['B'] == w489['B']
assert all(729 > q >= 240 for q in w489['ret']) and w489['ret'] == list(range(720, 729))   # parent: 9 fresh registers
assert all(240 <= q < 720 for q in w['ret'])                                              # R480: 9 dead registers
print('   rebuilt word is byte-identical to data/bitE8mut-r480.json.gz (content sha256 %s...); R = 480; the nine'
      ' totals live on dead registers %s' % (content_sha(w)[:16], w['ret']))
# control: the parent's own generator with no fresh totals hosts each total on the FIRST eligible register
run([PY, '-I', '-B', C / 'skeleton/gen.py', WD / 'gen0/word.json.gz', '0', 'fresh0'], cwd=WD / 'gen0', env=plan)
w0 = load(WD / 'gen0/word.json.gz'); assert w0['R'] == 480 and w0['ret'] != w['ret']

# ------------------------------------------------------------------------------------------------------------------
step("2. PR #370's checker: the stock file refuses source destinations; the parent's relaxed copy passes; interface")
p = run([PY, '-I', '-B', B / 'independent/checkword.py', WORD, C / 'pricing'], ok=False)
assert p.returncode != 0 and 'x register written' in p.stderr, 'stock checker did not refuse'
print('   stock checker refuses, as for the parent: x register written')
run([PY, '-I', '-B', B / 'independent/relax.py', WD / 'rchk'])
run([PY, '-I', '-B', WD / 'rchk/checkword_mut.py', WORD, C / 'pricing'], quiet=False)
run([PY, '-I', '-B', B / 'independent/interface.py', WORD, '--json', WD / 'interface.json'], quiet=False)
run([PY, '-I', '-B', B / 'independent/mutate_mut.py', WORD, WD / 'rchk/checkword_mut.py', C / 'pricing',
     B / 'independent/interface.py'], quiet=False)
iface = json.loads((WD / 'interface.json').read_text())

# ------------------------------------------------------------------------------------------------------------------
step('3. official cohort checkers: legality (NCOPY = 9), five-stage columns, eleven-stage columns (KPAIRS = 5)')
BIN = WD / 'bin'; BIN.mkdir(exist_ok=True)
cc = [CXX, '-O2', '-std=c++17', '-DHDIM=8']
run(cc + ['-DNCOPY=9'] + INC + ['-o', BIN / 'legality', CK / 'legality_h.cpp'])
run(cc + INC + ['-o', BIN / 'legality_ncopy_h', CK / 'legality_h.cpp'])
for name, extra in (('columns_h', []), ('columns_k5', ['-DKPAIRS=5']), ('columns_k2', ['-DKPAIRS=2'])):
    src = CK / ('columns_h.cpp' if name == 'columns_h' else 'columns_k.cpp')
    run(cc + ['-DNCOPY=9', '-DVPORTS=120', '-DRHELP=480'] + extra + INC + ['-o', BIN / name, src])
# payload probe = columns_h.cpp minus its payload assertion; used ONLY to report the refused control's bill
probe = (CK / 'columns_h.cpp').read_text()
anchor = 'need(payload<(cpp_int(1)<<104),"payloadfiniteprefix2^104");'; assert probe.count(anchor) == 1
(BIN / 'columns_probe.cpp').write_text(probe.replace(anchor, ''))
run(cc + ['-DNCOPY=9', '-DVPORTS=120', '-DRHELP=480'] + INC + ['-o', BIN / 'columns_probe', BIN / 'columns_probe.cpp'])


def cohort(word, d):
    run([PY, '-I', '-B', B / 'export_records.py', word, d / 'records'])
    run([PY, '-I', '-B', B / 'regression/stage_cohort.py', d / 'records', d / 'records', d / 'cin', d / 'cout'])


cohort(WORD, WD)
co = WD / 'cout'
run([BIN / 'legality', WD / 'cin', co, co / 'legality.json'])
run([BIN / 'columns_h', co / 'COHORT249-RECORDS.bin', co / 'columns.json'])
run([BIN / 'columns_k5', co / 'COHORT249-RECORDS.bin', co / 'columns_k5.json'])
run([BIN / 'columns_k2', co / 'COHORT249-RECORDS.bin', co / 'columns_k2.json'])
lg = json.loads((co / 'legality.json').read_text()); cl = json.loads((co / 'columns.json').read_text())
k5 = json.loads((co / 'columns_k5.json').read_text()); k2 = json.loads((co / 'columns_k2.json').read_text())
assert lg['status'] == 'PASS_INDEPENDENT_COHORT_LEGALITY_SOURCE_OWNERS_AND_LIFECYCLE' and lg['copies'] == lg['erasures'] == 9
assert cl['status'] == 'PASS_NEW_COHORT249_ALL_FIVE_STAGE_FORMAL_COLUMNS_AND_PREFIX_BILL' and cl['formal_columns_checked'] == 4 * 120 + 480
assert k5['status'] == 'PASS_NEW_COHORT249_ALL_BRIDGED_STAGE_FORMAL_COLUMNS_AND_PREFIX_BILL' and k5['formal_columns_checked'] == 10 * 120 + 480
assert len(k5['stages']) == 11 and k5['bridge_additions'] == 24 * 120 and all(x['rejected'] for x in k5['negative_controls'])
assert len(k5['negative_controls']) == 24 and dict(map(tuple, k5['local_raw_H'])) == dict(map(tuple, cl['local_raw_H']))
assert {k: v for k, v in cl.items() if k != 'seconds'} == {k: v for k, v in k2.items() if k != 'seconds'}
print('   legality PASS: %d records, %d common-frame ADDs, rank mass %d, 9 COPY/ERASE at the full frame'
      % (lg['records'], lg['common_frame_ADDs'], lg['rank_mass']))
print('   five-stage formal columns PASS: %d columns over F2; prefix payload %d bits < 104 (eleven-stage: %d bits)'
      % (cl['formal_columns_checked'], cl['payload_prefix_bits'], k5['payload_prefix_bits']))
print('   eleven-stage formal columns PASS: %d columns, %d bridge additions, 24/24 omitted-bridge controls rejected;'
      ' columns_k at KPAIRS = 2 reproduces the five-stage receipt' % (k5['formal_columns_checked'], k5['bridge_additions']))
run([PY, '-I', '-B', B / 'mutate_records.py', WD / 'records', WD / 'cin', co, BIN / 'legality', BIN / 'columns_k5',
     BIN / 'legality_ncopy_h'], quiet=False)
run([PY, '-I', '-B', B / 'mutate_records_mut.py', WORD, WD / 'records', WD / 'cin', co, BIN / 'legality',
     BIN / 'columns_h', BIN / 'columns_k5'], quiet=False)
# control: the parent's first-register hosting of the same nine totals is refused by the official five-stage checker
g0 = WD / 'gen0'; cohort(g0 / 'word.json.gz', g0)
p = run([BIN / 'columns_h', g0 / 'cout/COHORT249-RECORDS.bin', g0 / 'cout/columns.json'], ok=False)
assert p.returncode != 0 and 'payloadfiniteprefix2^104' in (p.stdout + p.stderr), 'first-register control not refused'
run([BIN / 'columns_probe', g0 / 'cout/COHORT249-RECORDS.bin', g0 / 'cout/probe.json'])
pb0 = json.loads((g0 / 'cout/probe.json').read_text())['payload_prefix_bits']
run([BIN / 'columns_probe', co / 'COHORT249-RECORDS.bin', co / 'probe.json'])
assert json.loads((co / 'probe.json').read_text())['payload_prefix_bits'] == cl['payload_prefix_bits']
print('   control: the parent generator (first eligible register hosts each total) is REFUSED by columns_h:'
      ' payload %d bits >= 104; last-register hosting: %d bits' % (pb0, cl['payload_prefix_bits']))

# ------------------------------------------------------------------------------------------------------------------
step('4. exact nondegeneracy (E8 Gram) and prime witnesses on every frame')
run([PY, '-I', '-B', CK / 'gram_frames.py', WD / 'records', '--gram', 'e8ham', '--h', '8', '--positive'], quiet=False)

# ------------------------------------------------------------------------------------------------------------------
step("5. eleven-stage whole-residual hosting (PR #445 geometry, PR #472 emitter and audit), exact price, assembly")
(WD / 'nine').mkdir(exist_ok=True); (WD / 'bit').mkdir(exist_ok=True)
run([PY, '-I', '-B', C / 'nine/geometry.py', '--source', PARENT, '--out', WD / 'nine'])
run([PY, '-I', '-B', HUB / 'r740-hosted-eleven/code/geometry.py', '--source', PARENT, '--out', WD / 'bit'])
run([PY, '-I', '-B', PARENT / 'discovery/host_select.py', WORD, WD / 'hosting-rediscovered.json'])
assert json.loads((WD / 'hosting-rediscovered.json').read_text()) == json.loads(HOST.read_text()), 'hosting differs'
print("   PR #442 hosting programme (parent's discovery/host_select.py) rediscovers data/hosting-r480.json exactly")
run([PY, '-E', '-s', '-B', C / 'eleven/emit.py', '--word', WORD, '--local-check', WD, '--out', WD / 'bit',
     '--isometries', PARENT / 'data/eleven/residual-isometries.json', '--hosting', HOST])
run([PY, '-E', '-s', '-B', AD / 'eleven/audit.py', WD, WD / 'nine', WD / 'bit'])
g = json.loads((WD / 'bit/GLOBAL.json').read_text()); a = json.loads((WD / 'bit/AUDIT.json').read_text())
assert a['status'] == 'PASS_INDEPENDENT_ELEVEN_STAGE_HOSTING_AUDIT' and g['R'] == 480 and g['hosted_residuals'] == 88 * 480
print('   template: 88 calls, %d whole helper residuals hosted on idle data families, %d unbanked scalar columns'
      ' restored; independent audit PASS: %d renamed instructions, %d template mutations rejected'
      % (g['hosted_residuals'], g['independent_unbanked_scalar_columns'], a['emitted_events'], len(a['mutations_rejected'])))
run([PY, '-I', '-B', C / 'eleven/assemble.py', WD / 'bit', '480', PARENT, WD / 'RESULT.json', 'pr484,pr471,pr458'], quiet=False)
r = json.loads((WD / 'RESULT.json').read_text())

# ------------------------------------------------------------------------------------------------------------------
step("6. control: the parent's R489 word through the parent's unmodified emitter, audit and assembly")
if LIGHT:
    c4 = WD / 'r489'; (c4 / 'bit').mkdir(parents=True, exist_ok=True); W489 = PARENT / 'data/bit/bitE8mut-r489.json.gz'
    cohort(W489, c4)
    run(cc + ['-DNCOPY=9', '-DVPORTS=120', '-DRHELP=489'] + INC + ['-o', BIN / 'columns_h489', CK / 'columns_h.cpp'])
    run([BIN / 'legality', c4 / 'cin', c4 / 'cout', c4 / 'cout/legality.json'])
    run([BIN / 'columns_h489', c4 / 'cout/COHORT249-RECORDS.bin', c4 / 'cout/columns.json'])
    (c4 / 'bit/GEOMETRY.json').write_bytes((WD / 'bit/GEOMETRY.json').read_bytes())
    run([PY, '-E', '-s', '-B', C / 'eleven/emit.py', '--word', W489, '--local-check', c4, '--out', c4 / 'bit',
         '--isometries', PARENT / 'data/eleven/residual-isometries.json', '--hosting', PARENT / 'data/eleven/hosting.json'])
    run([PY, '-E', '-s', '-B', C / 'eleven/audit.py', c4, WD / 'nine', c4 / 'bit'])
    run([PY, '-I', '-B', C / 'eleven/assemble.py', c4 / 'bit', '489', PARENT, c4 / 'RESULT.json', 'pr484'])
    r489 = json.loads((c4 / 'RESULT.json').read_text())
else:
    r489 = json.loads((WD / 'parent/RESULT.json').read_text())
pe = json.loads((PARENT / 'EXPECTED.json').read_text())['eleven']
assert r489['bit_lower'] == pe['bit_lower'] and r489['bit_profile'] == pe['profile']
print('   parent R489 bit c reproduced exactly: %s = %s' % (pe['bit_lower'], pe['bit_lower_decimal']))

# ------------------------------------------------------------------------------------------------------------------
step('7. summary against EXPECTED.json')
e = EXP
assert {str(k): v for k, v in cl['local_raw_H']} == e['word']['local_histogram']
assert cl['payload_prefix_bits'] == e['word']['five_stage_payload_bits'] and k5['payload_prefix_bits'] == e['word']['eleven_stage_payload_bits']
assert pb0 == e['control_first_register']['five_stage_payload_bits']
assert iface['source_destination_gates_A'] == e['word']['source_destination_gates_A']
assert r['bit_lower'] == e['eleven']['bit_lower'] and r['bit_profile'] == e['eleven']['profile']
assert r['emitted_program_sha256'] == e['eleven']['emitted_program_sha256']
for k in ('prefix_bits', 'charged_prefix_bits', 'three_level_coefficient_bits', 'charged_three_level_coefficient_bits', 'row_coefficient', 'hosted_residuals'):
    assert r['bit'][k] == e['eleven']['bit'][k], k
for name, x in e['eleven']['kappa'].items():
    assert r['kappa'][name]['kappa'] == x['kappa'] and r['kappa'][name]['binding_component'] == x['binding_component'], name
c, c0 = F(r['bit_lower']), F(pe['bit_lower'])
print('PASS bit c (R = 480; PR #472 eleven-stage whole-residual pipeline, 10^-24 grid) = %s = %s' % (r['bit_lower'], r['bit_lower_decimal']))
print('     %+.4f%% over PR #493 (R = 489, c = %s); profile %s' % (100 * float(c / c0 - 1), pe['bit_lower_decimal'], r['bit_profile']))
for name in ('pr484', 'pr471', 'pr458'):
    k = r['kappa'][name]
    print('     with %s complex b = %s: kappa = %s = %s (%s-bound)' % (name, k['complex_lower'], k['kappa'], k['kappa_decimal'], k['binding_component']))
print('PASS %s  [%.0fs]' % ('LIGHT' if LIGHT else 'FULL', time.time() - T0))

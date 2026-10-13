# Punctured star bit unit (v = 111 ports, nine rank-7 totals): the word through PR #493's hosted-audit chain. Verifier.
# Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code. Apache-2.0.
"""usage: python verify.py /absolute/new/output [--light] [--no-control] [--no-mutants]

FULL runs PR #493's verify.sh unchanged (the parent: its word, checkers, pipeline, controls and compositions), then
everything below.  --light skips the parent run.  The parent's manifest is always checked.
Steps: 0 manifests; 1 the word rebuilt from the parent's plan; 2 the independent checker (v <= 120) and its mutants;
3 the official cohort checkers at (v, R); 4 exact Gram; 5 the eleven-stage whole-residual hosted pipeline (geometry,
hosting, emit, audit, assembly) with every constant derived from the word; 6 the pricing harness (pricex.py) must give
the same c to all 24 digits; 7 REGRESSION: the R480 word of PR #503 through the stock chain and through the adapted
chain, outputs compared byte for byte; 8 mutation controls; 9 composition with the cited complex suppliers (#535) and
the control that reproduces #535's published kappa; 10 summary against EXPECTED.json.
Needs Python 3.11+ with numpy, sympy, scipy, a C++17 compiler (CXX) and Boost headers (BOOST_INCLUDE), as the parent does."""
import filecmp
import gzip
import hashlib
import json
import os
import subprocess
import sys
import time
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve().parent
PARENT = HERE.parent / 'e8-bit-carrier-skeleton'
args = [a for a in sys.argv[1:] if not a.startswith('--')]
LIGHT, NOCTL, NOMUT = '--light' in sys.argv, '--no-control' in sys.argv, '--no-mutants' in sys.argv
UNTIL = next((int(a.split('=')[1]) for a in sys.argv if a.startswith('--until=')), 99)   # development aid: stop after step N
assert len(args) == 1, __doc__
WD = Path(args[0]).resolve(); WD.mkdir(parents=True, exist_ok=True)
assert not str(WD).startswith(str(HERE.parent)), 'output dir must be outside research/'
PY = sys.executable; CXX = os.environ.get('CXX', 'c++'); BI = os.environ.get('BOOST_INCLUDE', '/usr/include')
ENV = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
C, B = PARENT / 'code', PARENT / 'code/bit'; CK = B / 'checkers'; HUB = C / 'hub'
WORD = HERE / 'data/bitE8mut-v111-r489.json.gz'; HOST = HERE / 'data/hosting-v111-r489.json'
CTL = HERE / 'data/control-r480'; CWORD, CHOST = CTL / 'bitE8mut-r480.json.gz', CTL / 'hosting-r480.json'
EXP = json.loads((HERE / 'EXPECTED.json').read_text())
INC = ['-I%s' % (PARENT / 'portable-include'), '-I%s' % CK, '-I%s' % BI]
sys.dont_write_bytecode = True
sys.path.insert(0, str(HERE / 'code'))
import punct_cfg as PC  # noqa: E402
T0 = time.time()


def run(cmd, cwd=None, ok=True, quiet=True, env=None, out=None):
    p = subprocess.run([str(x) for x in cmd], cwd=cwd, env=env or ENV, capture_output=True, text=True)
    if out is not None:
        Path(out).write_text(p.stdout)
    if ok and p.returncode != 0:
        sys.stderr.write(p.stdout[-3000:] + p.stderr[-3000:]); raise SystemExit('FAILED: %s' % ' '.join(map(str, cmd)))
    if not quiet:
        for line in p.stdout.rstrip().splitlines(): print('   ' + line)
    return p


def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def content_sha(w): return hashlib.sha256(json.dumps(w, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def rj(p): return json.loads(Path(p).read_text())


def step(s):
    n = s.split('.')[0]
    if n.isdigit() and int(n) > UNTIL: raise SystemExit('stopped before step %s (--until)' % n)
    print('== %s  [%.0fs]' % (s, time.time() - T0), flush=True)


def stacking(bitdir, v):
    """hosting disclosure: in how many of the 88 calls does one physical family host more than one helper of that call?"""
    from collections import Counter
    t = json.loads(gzip.decompress((Path(bitdir) / 'GLOBAL-TEMPLATE.json.gz').read_bytes()))
    m = [max(Counter(o[0] for o in c['owners'][2 * v:]).values()) for c in t['calls']]
    return dict(calls=len(m), calls_with_stacked_helpers=sum(1 for x in m if x > 1), max_helpers_on_one_family=max(m))


def norm(p, drop=('seconds',)):
    d = rj(p)
    for k in drop: d.pop(k, None)
    return d


# ------------------------------------------------------------------------------------------------------------------
step('0. manifests: this package (MANIFEST.json) and the parent package (its MANIFEST.sha256, as its step 0)')
man = rj(HERE / 'MANIFEST.json')
for rel, h in man['files'].items(): assert sha(HERE / rel) == h, ('MISMATCH', rel)
listed = set(man['files']) | {'MANIFEST.json'}
present = {str(p.relative_to(HERE)) for p in HERE.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
assert present == listed, ('unlisted or missing files', sorted(present ^ listed))
assert sha(PARENT / 'MANIFEST.sha256') == man['parent_manifest_sha256'], 'parent MANIFEST.sha256 changed'
bad = 0
for line in (PARENT / 'MANIFEST.sha256').read_text().splitlines():
    h, p = line.split('  ', 1)
    if sha(PARENT / p) != h: print('PARENT MISMATCH', p); bad += 1
assert not bad
print('   %d package files and %d parent files match their manifests' % (len(man['files']), len((PARENT / 'MANIFEST.sha256').read_text().splitlines())))

if not LIGHT:
    step('P. parent: PR #493 verify.sh, unchanged')
    run(['bash', PARENT / 'verify.sh', WD / 'parent'], env=dict(ENV, PYTHON=PY), quiet=False)

# ------------------------------------------------------------------------------------------------------------------
step('1. the word, rebuilt from the parent plan (code/word/gen_punct.py); the one configuration')
(WD / 'gen').mkdir(exist_ok=True)
P = EXP['word']['punctured']
run([PY, '-I', '-B', HERE / 'code/word/gen_punct.py', WD / 'gen/word.json.gz', 'P=' + ','.join(map(str, P))], cwd=WD / 'gen')
assert (WD / 'gen/word.json.gz').read_bytes() == WORD.read_bytes(), 'rebuilt word differs from the shipped word'
w = PC.load(WORD); cfg = PC.config(w, PARENT)
assert content_sha(w) == EXP['word']['content_sha256'] and w['punctured'] == P
V, R, CST = cfg['v'], cfg['R'], cfg['cst']
assert (V, R, CST) == (EXP['word']['v'], EXP['word']['R'], EXP['word']['cst']) and cfg['copy_ranks'] == EXP['word']['copy_ranks']
print('   rebuilt word is byte-identical to data/bitE8mut-v111-r489.json.gz (content sha256 %s...)' % content_sha(w)[:16])
print('   config: v = %d live ports (120 - %d punctured: %s), R = %d helpers, totals map: registers %s copy ranks %s => cst = %d'
      % (V, len(P), P, R, w['ret'], cfg['copy_ranks'], CST))
AD = WD / 'adapted'
run([PY, '-I', '-B', HERE / 'code/adapt.py', PARENT, WORD, AD], quiet=False)

# ------------------------------------------------------------------------------------------------------------------
SKIP2 = '--skip2' in sys.argv   # development aid only (step 2 is the slow pure-Python checker)
iface = None
if not SKIP2:
    step("2. PR #370's checker for v <= 120 ports: the stock-form file refuses source destinations; the relaxed copy passes; interface")
    p = run([PY, '-I', '-B', AD / 'chk/checkword.py', WORD, C / 'pricing'], ok=False)
    assert p.returncode != 0 and 'x register written' in p.stderr, 'stock-form checker did not refuse'
    print('   stock-form checker refuses, as for the parent: x register written')
    p = run([PY, '-I', '-B', B / 'independent/checkword.py', WORD, C / 'pricing'], ok=False)
    assert p.returncode != 0 and 'AssertionError' in p.stderr and 'x register written' not in p.stderr
    print("   the parent's own checker refuses the 111-line word at its v == 120 assertion (the one edit made in chk/checkword.py)")
    run([PY, '-I', '-B', AD / 'chk/relax.py', AD / 'rchk'])
    run([PY, '-I', '-B', AD / 'rchk/checkword_mut.py', WORD, C / 'pricing'], quiet=False)
    run([PY, '-I', '-B', B / 'independent/interface.py', WORD, '--json', WD / 'interface.json'], quiet=False)
    run([PY, '-I', '-B', B / 'independent/mutate_mut.py', WORD, AD / 'rchk/checkword_mut.py', C / 'pricing',
         B / 'independent/interface.py'], quiet=False)
    iface = rj(WD / 'interface.json')
else:
    run([PY, '-I', '-B', AD / 'chk/relax.py', AD / 'rchk'])

# ------------------------------------------------------------------------------------------------------------------
step('3. official cohort checkers at (v, R): legality (NCOPY = 9), five-stage columns, eleven-stage columns (KPAIRS = 5)')
BIN = WD / 'bin'; BIN.mkdir(exist_ok=True)
cc = [CXX, '-O2', '-std=c++17', '-DHDIM=8']


def build_checkers(v, r):
    """compile the official checkers for (v, r); the compiles run concurrently"""
    # payload probe = columns_h.cpp minus its payload assertion; used ONLY to report a refused control's bill
    probe = (CK / 'columns_h.cpp').read_text()
    anchor = 'need(payload<(cpp_int(1)<<104),"payloadfiniteprefix2^104");'; assert probe.count(anchor) == 1
    (BIN / 'columns_probe.cpp').write_text(probe.replace(anchor, ''))
    flags = ['-DNCOPY=9', '-DVPORTS=%d' % v, '-DRHELP=%d' % r]
    jobs = [cc + ['-DNCOPY=9'] + INC + ['-o', BIN / 'legality', CK / 'legality_h.cpp'],
            cc + INC + ['-o', BIN / 'legality_ncopy_h', CK / 'legality_h.cpp'],
            cc + flags + INC + ['-o', BIN / ('columns_probe_v%d_r%d' % (v, r)), BIN / 'columns_probe.cpp']]
    for name, extra, src in (('columns_h', [], 'columns_h.cpp'), ('columns_k5', ['-DKPAIRS=5'], 'columns_k.cpp'),
                             ('columns_k2', ['-DKPAIRS=2'], 'columns_k.cpp')):
        jobs.append(cc + flags + extra + INC + ['-o', BIN / ('%s_v%d_r%d' % (name, v, r)), CK / src])
    procs = [(j, subprocess.Popen([str(x) for x in j], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=ENV)) for j in jobs]
    for j, p in procs:
        o, e = p.communicate()
        if p.returncode != 0:
            sys.stderr.write(o[-3000:] + e[-3000:]); raise SystemExit('FAILED: %s' % ' '.join(map(str, j)))


def cohort(word, d):
    run([PY, '-I', '-B', B / 'export_records.py', word, d / 'records'])
    run([PY, '-I', '-B', B / 'regression/stage_cohort.py', d / 'records', d / 'records', d / 'cin', d / 'cout'])


def columns(v, r, d, kinds=('columns_h', 'columns_k5', 'columns_k2')):
    co = d / 'cout'
    run([BIN / 'legality', d / 'cin', co, co / 'legality.json'])
    for k in kinds:
        out = {'columns_h': 'columns.json', 'columns_k5': 'columns_k5.json', 'columns_k2': 'columns_k2.json'}[k]
        run([BIN / ('%s_v%d_r%d' % (k, v, r)), co / 'COHORT249-RECORDS.bin', co / out])


build_checkers(V, R)
cohort(WORD, WD); columns(V, R, WD)
co = WD / 'cout'
lg, cl, k5, k2 = rj(co / 'legality.json'), rj(co / 'columns.json'), rj(co / 'columns_k5.json'), rj(co / 'columns_k2.json')
assert lg['status'] == 'PASS_INDEPENDENT_COHORT_LEGALITY_SOURCE_OWNERS_AND_LIFECYCLE' and lg['copies'] == lg['erasures'] == 9
assert cl['status'] == 'PASS_NEW_COHORT249_ALL_FIVE_STAGE_FORMAL_COLUMNS_AND_PREFIX_BILL' and cl['formal_columns_checked'] == 4 * V + R
assert k5['status'] == 'PASS_NEW_COHORT249_ALL_BRIDGED_STAGE_FORMAL_COLUMNS_AND_PREFIX_BILL' and k5['formal_columns_checked'] == 10 * V + R
assert len(k5['stages']) == 11 and k5['bridge_additions'] == 24 * V and all(x['rejected'] for x in k5['negative_controls'])
assert len(k5['negative_controls']) == 24 and dict(map(tuple, k5['local_raw_H'])) == dict(map(tuple, cl['local_raw_H']))
assert {k: v for k, v in cl.items() if k != 'seconds'} == {k: v for k, v in k2.items() if k != 'seconds'}
assert cl['payload_prefix_bits'] < 104 and k5['payload_prefix_bits'] < 104
print('   legality PASS: %d records, %d common-frame ADDs, rank mass %d, 9 COPY/ERASE (ranks %s)'
      % (lg['records'], lg['common_frame_ADDs'], lg['rank_mass'], cfg['copy_ranks']))
print('   five-stage formal columns PASS: %d columns over F2; prefix payload %d bits < 104 (eleven-stage: %d bits)'
      % (cl['formal_columns_checked'], cl['payload_prefix_bits'], k5['payload_prefix_bits']))
print('   eleven-stage formal columns PASS: %d columns, %d bridge additions, 24/24 omitted-bridge controls rejected;'
      ' columns_k at KPAIRS = 2 reproduces the five-stage receipt' % (k5['formal_columns_checked'], k5['bridge_additions']))
BK = lambda k, v=V, r=R: BIN / ('%s_v%d_r%d' % (k, v, r))
run([PY, '-I', '-B', AD / 'mutate_records.py', WD / 'records', WD / 'cin', co, BIN / 'legality', BK('columns_k5'),
     BIN / 'legality_ncopy_h'], quiet=False)
run([PY, '-I', '-B', B / 'mutate_records_mut.py', WORD, WD / 'records', WD / 'cin', co, BIN / 'legality',
     BK('columns_h'), BK('columns_k5')], quiet=False)

# ------------------------------------------------------------------------------------------------------------------
step('4. exact nondegeneracy (E8 Gram) and prime witnesses on every frame')
run([PY, '-I', '-B', CK / 'gram_frames.py', WD / 'records', '--gram', 'e8ham', '--h', '8', '--positive'], quiet=False)

# ------------------------------------------------------------------------------------------------------------------
step('5. eleven-stage whole-residual hosting (PR #445 geometry, PR #472 emitter and audit), exact price, assembly')
NINE_G, ELEVEN_G = 'nine_geometry.py', 'eleven_geometry.py'


def hosted(word, d, hosting_out, suppliers, ad=AD, geom_word=True, outname='bit'):
    """geometry (live labels), hosting nomination, emit, audit, assembly of ONE word with the adapted scripts."""
    (d / 'nine').mkdir(exist_ok=True); (d / outname).mkdir(exist_ok=True)
    gw = ['--word', word] if geom_word else []
    run([PY, '-I', '-B', ad / NINE_G, '--source', PARENT, '--out', d / 'nine'] + gw)
    run([PY, '-I', '-B', ad / ELEVEN_G, '--source', PARENT, '--out', d / outname] + gw)
    run([PY, '-I', '-B', ad / 'host_select.py', word, hosting_out])
    return d / outname


def emit_audit_assemble(word, d, bitdir, hosting, ad, suppl, nine=None):
    run([PY, '-E', '-s', '-B', ad / 'emit.py', '--word', word, '--local-check', d, '--out', bitdir,
         '--isometries', PARENT / 'data/eleven/residual-isometries.json', '--hosting', hosting])
    run([PY, '-E', '-s', '-B', ad / 'audit.py', d, nine or d / 'nine', bitdir])
    Rr = rj(bitdir / 'GLOBAL.json')['R']
    run([PY, '-I', '-B', ad / 'assemble.py', bitdir, str(Rr), PARENT, d / 'RESULT.json', suppl[0]] + suppl[1:])


bit = hosted(WORD, WD, WD / 'hosting-rediscovered.json', None)
assert rj(WD / 'hosting-rediscovered.json') == rj(HOST), 'hosting differs from the frozen selection'
print("   PR #442 hosting programme (host_select.py, v from the word) rediscovers data/hosting-v111-r489.json exactly")
emit_audit_assemble(WORD, WD, bit, HOST, AD, ['pr535', str(HERE / 'data/complex-b.json')])
g, a, r = rj(bit / 'GLOBAL.json'), rj(bit / 'AUDIT.json'), rj(WD / 'RESULT.json')
assert a['status'] == 'PASS_INDEPENDENT_ELEVEN_STAGE_HOSTING_AUDIT' and g['R'] == R and g['v'] == V
assert g['hosted_residuals'] == 88 * R and g['live'] == 2 * 5 * V * 8 and g['deficit'] == 8 * (10 * V - 11 * CST)
print('   template: 88 calls, %d whole helper residuals hosted on idle data families, %d unbanked scalar columns restored;'
      ' independent audit PASS: %d renamed instructions, %d template mutations rejected, local audit %s'
      % (g['hosted_residuals'], g['independent_unbanked_scalar_columns'], a['emitted_events'], len(a['mutations_rejected']),
         a['local_audit']['status']))
print('   bit c (eleven stages, 10^-24 grid) = %s = %s; live %d, rank-mass deficit %d' % (r['bit_lower'], r['bit_lower_decimal'], g['live'], g['deficit']))

# ------------------------------------------------------------------------------------------------------------------
step("6. pricing harness (code/price/pricex.py: local histogram replay + the same hosting programme + moment.certify) must agree to all digits")
p = run([PY, '-B', HERE / 'code/price/pricex.py', WORD, '11'])
line = [x for x in p.stdout.splitlines() if x.startswith('{')][0]; px = json.loads(line)
assert px['feasible'] and F(px['c']) == F(r['bit_lower_decimal']) and px['profile'] == r['bit_profile']
assert px['c'].startswith(r['bit_lower_decimal'][:26])
print('   pricex c = %s == hosted-audit c = %s (24 digits; same profile)' % (px['c'], r['bit_lower_decimal']))
# robustness: the hosting rule used (PR #442's pooled whole-residual programme, as in #472 / #493 / #503 / #510) lets several helpers of one
# invocation share a family at disjoint cells.  Under the STRICTER rule 'one helper per family copy per stage' (PR #458's rule is per invocation,
# so this is a lower bound for any #458-compliant hosting) the c is lower; kappa is complex-bound and unchanged (step 9)
stk = stacking(bit, V)
print('   hosting rule: #442/#472/#493 pooled whole-residual programme; %d of %d calls host several helpers of that call on one family '
      '(at most %d on one family) -- inherited, as in PR #503 (see README, Scope)' % (stk['calls_with_stacked_helpers'], stk['calls'], stk['max_helpers_on_one_family']))
p458 = json.loads(run([PY, '-B', HERE / 'code/price/price458.py', WORD, '11']).stdout.strip().splitlines()[-1])
assert p458['feasible458'] and F(p458['c_stock']) == F(r['bit_lower_decimal'])
print('   stricter hosting (one helper per family copy per stage): c >= %s (%+.4f%% vs the shipped c); kappa unchanged (complex-bound)'
      % (p458['c458'], 100 * float(F(p458['c458']) / F(r['bit_lower_decimal']) - 1)))
# the harness's other stages: infeasible by the exact hosting wall at s = 9 and 7, feasible at s = 13
px_all = {s: json.loads([x for x in run([PY, '-B', HERE / 'code/price/pricex.py', WORD, str(s)]).stdout.splitlines() if x.startswith('{')][0]) for s in (9, 13)}
print('   other stages (information): s = 9 feasible: %s (%s); s = 13 c = %s' % (px_all[9]['feasible'], px_all[9].get('why', ''), px_all[13].get('c')))

# ------------------------------------------------------------------------------------------------------------------
if not NOCTL:
    step("7. REGRESSION: PR #503's R480 word (v = 120, nine rank-8 totals) through the stock chain and the adapted chain")
    CD = WD / 'ctl'; CD.mkdir(exist_ok=True)
    cw = PC.load(CWORD); ccfg = PC.config(cw, PARENT)
    assert content_sha(cw) == EXP['control']['word_content_sha256'] and (ccfg['v'], ccfg['R'], ccfg['cst']) == (120, 480, 72)
    build_checkers(120, 480)
    cohort(CWORD, CD); columns(120, 480, CD, kinds=('columns_h', 'columns_k5'))
    assert rj(CD / 'cout/columns.json')['payload_prefix_bits'] == EXP['control']['five_stage_payload_bits']
    # (a) the checkers: the adapted copies print exactly what the parent's print on the R480 word
    run([PY, '-I', '-B', B / 'independent/relax.py', CD / 'rchk0'])
    s0 = run([PY, '-I', '-B', CD / 'rchk0/checkword_mut.py', CWORD, C / 'pricing']).stdout
    ADC = CD / 'adapted-for-control'   # local_audit.py bakes in the word it audits, so the control has its own adapted copy
    run([PY, '-I', '-B', HERE / 'code/adapt.py', PARENT, CWORD, ADC])
    run([PY, '-I', '-B', ADC / 'chk/relax.py', ADC / 'rchk'])
    s1 = run([PY, '-I', '-B', ADC / 'rchk/checkword_mut.py', CWORD, C / 'pricing']).stdout
    assert s0 == s1, 'relaxed checker output differs on the R480 word'
    m0 = run([PY, '-I', '-B', B / 'mutate_records.py', CD / 'records', CD / 'cin', CD / 'cout', BIN / 'legality',
              BK('columns_k5', 120, 480), BIN / 'legality_ncopy_h']).stdout
    m1 = run([PY, '-I', '-B', ADC / 'mutate_records.py', CD / 'records', CD / 'cin', CD / 'cout', BIN / 'legality',
              BK('columns_k5', 120, 480), BIN / 'legality_ncopy_h']).stdout
    assert m0 == m1 and 'PASS all 6' in m0, 'record-mutant output differs on the R480 word'
    print('   (a) relaxed checker and the 6 record mutants: output identical to the parent files on the R480 word')
    # (b) the hosted chain.  STOCK = parent emit.py / assemble.py unchanged + PR #503's audit.py / local_audit.py (its adapt.py)
    assert sha(HERE / 'code/adapt503.py') == '04ec15262595e502796efc1f100f1efd4f28585add48377af1bda702a12c0e40', "adapt503.py is not PR #503's adapt.py"
    AD503 = CD / 'ad503'
    run([PY, '-I', '-B', HERE / 'code/adapt503.py', PARENT, CWORD, AD503], quiet=False)
    sd, cd_ = CD / 'stock', CD / 'adapted'
    for x in (sd, cd_): (x / 'nine').mkdir(parents=True, exist_ok=True); (x / 'bit').mkdir(exist_ok=True)
    run([PY, '-I', '-B', C / 'nine/geometry.py', '--source', PARENT, '--out', sd / 'nine'])
    run([PY, '-I', '-B', HUB / 'r740-hosted-eleven/code/geometry.py', '--source', PARENT, '--out', sd / 'bit'])
    run([PY, '-I', '-B', PARENT / 'discovery/host_select.py', CWORD, sd / 'hosting.json'])
    run([PY, '-I', '-B', ADC / NINE_G, '--source', PARENT, '--out', cd_ / 'nine'])
    run([PY, '-I', '-B', ADC / ELEVEN_G, '--source', PARENT, '--out', cd_ / 'bit'])
    run([PY, '-I', '-B', ADC / 'host_select.py', CWORD, cd_ / 'hosting.json'])
    assert norm(sd / 'nine/GEOMETRY.json') == norm(cd_ / 'nine/GEOMETRY.json') and norm(sd / 'bit/GEOMETRY.json') == norm(cd_ / 'bit/GEOMETRY.json')
    # HiGHS can return different exact optima. Check both nominations against
    # the frozen bill; the unchanged physical pipelines below still use CHOST.
    for nomination in (sd, cd_):
        run([PY, '-I', '-B', HERE / 'code/compare_hosting.py',
             nomination / 'hosting.json', CHOST, nomination / 'hosting-feasibility.json'], quiet=False)
    # both pipelines read the SAME geometry files (GEOMETRY.json stores its own run time, which is hashed into the template)
    for sub in ('nine', 'bit'): (cd_ / sub / 'GEOMETRY.json').write_bytes((sd / sub / 'GEOMETRY.json').read_bytes())
    print('   (b) geometries equal modulo run time; both hosting nominations exactly feasible with the frozen bill')
    suppl = ['pr484,pr471,pr458']
    for tag, base_, ad_, emit_ in (('stock', sd, AD503, C / 'eleven/emit.py'), ('adapted', cd_, ADC, ADC / 'emit.py')):
        run([PY, '-E', '-s', '-B', emit_, '--word', CWORD, '--local-check', CD, '--out', base_ / 'bit', '--isometries',
             PARENT / 'data/eleven/residual-isometries.json', '--hosting', CHOST])
        run([PY, '-E', '-s', '-B', (ad_ / 'eleven/audit.py') if tag == 'stock' else (ADC / 'audit.py'), CD, base_ / 'nine', base_ / 'bit'])
        run([PY, '-I', '-B', (C / 'eleven/assemble.py') if tag == 'stock' else (ADC / 'assemble.py'), base_ / 'bit', '480', PARENT,
             base_ / 'RESULT.json', 'pr484,pr471,pr458'])
    same = {}
    gs_, ga_ = sd / 'bit/GLOBAL.json', cd_ / 'bit/GLOBAL.json'
    same['GLOBAL.json (all fields but run time)'] = norm(gs_) == norm(ga_)
    same['GLOBAL-TEMPLATE.json.gz'] = filecmp.cmp(sd / 'bit/GLOBAL-TEMPLATE.json.gz', cd_ / 'bit/GLOBAL-TEMPLATE.json.gz', shallow=False)
    same['AUDIT.json'] = filecmp.cmp(sd / 'bit/AUDIT.json', cd_ / 'bit/AUDIT.json', shallow=False)
    same['RESULT.json'] = filecmp.cmp(sd / 'RESULT.json', cd_ / 'RESULT.json', shallow=False)
    assert all(same.values()), same
    rc = rj(cd_ / 'RESULT.json'); ec = EXP['control']
    assert rc['bit_lower'] == ec['bit_lower'] and rc['bit_profile'] == ec['profile']
    assert rj(cd_ / 'bit/GLOBAL.json')['emitted_program_sha256'] == ec['emitted_program_sha256']
    for name, x in ec['kappa'].items(): assert rc['kappa'][name]['kappa'] == x
    pc_ = json.loads([x for x in run([PY, '-B', HERE / 'code/price/pricex.py', CWORD, '11']).stdout.splitlines() if x.startswith('{')][0])
    assert F(pc_['c']) == F(rc['bit_lower_decimal'])
    stk_c = stacking(cd_ / 'bit', 120)
    assert stk_c == ec['stacking'], (stk_c, ec['stacking'])
    print('   (c) emit/audit/assemble: GLOBAL.json, GLOBAL-TEMPLATE.json.gz, AUDIT.json and RESULT.json of the adapted chain are'
          ' BYTE-IDENTICAL to the stock chain on the R480 word (%s)' % ', '.join(same))
    print('       R480 c = %s = %s, emitted-program sha256 %s... == PR #503 EXPECTED; kappa with #484/#471/#458 unchanged; pricex agrees'
          % (rc['bit_lower'], rc['bit_lower_decimal'], ec['emitted_program_sha256'][:16]))
    print('       hosting disclosure for the control: %d of %d calls stack several helpers on one family (max %d) -- the same inherited rule'
          % (stk_c['calls_with_stacked_helpers'], stk_c['calls'], stk_c['max_helpers_on_one_family']))

# ------------------------------------------------------------------------------------------------------------------
if not NOMUT:
    step('8. mutation controls on the star word (code/mutants.py): every one must be rejected')
    run([PY, '-I', '-B', HERE / 'code/mutants.py', WORD, WD, AD, PARENT, HOST, WD / 'mutants.json'], quiet=False)
    mut = rj(WD / 'mutants.json'); assert mut['all_rejected'] and len(mut['controls']) >= 4

# ------------------------------------------------------------------------------------------------------------------
step('9. composition with the cited complex supplier (#535): kappa; control = #535 reproduced from #510 bit c and the same b')
run([PY, '-I', '-B', HERE / 'code/compose_control.py', PARENT, WD / 'RESULT.json', HERE / 'data/complex/pr535/EXPECTED.json',
     WD / 'compose.json'], quiet=False)
comp = rj(WD / 'compose.json')

# ------------------------------------------------------------------------------------------------------------------
step('10. summary against EXPECTED.json')
e = EXP
assert {str(k): v for k, v in cl['local_raw_H']} == e['word']['local_histogram']
assert cl['payload_prefix_bits'] == e['word']['five_stage_payload_bits'] and k5['payload_prefix_bits'] == e['word']['eleven_stage_payload_bits']
assert iface['source_destination_gates_A'] == e['word']['source_destination_gates_A']
assert r['bit_lower'] == e['eleven']['bit_lower'] and r['bit_lower_decimal'] == e['eleven']['bit_lower_decimal'] and r['bit_profile'] == e['eleven']['profile']
assert g['emitted_program_sha256'] == e['eleven']['emitted_program_sha256']
assert stk == e['hosting']['stacking'] and p458['c458'] == e['hosting']['c_strict_per_stage'] and F(p458['c458']) < F(r['bit_lower'])
for k in ('prefix_bits', 'charged_prefix_bits', 'three_level_coefficient_bits', 'charged_three_level_coefficient_bits', 'row_coefficient', 'hosted_residuals', 'live', 'physical', 'rank_mass'):
    assert r['bit'][k] == e['eleven']['bit'][k], k
assert r['kappa']['pr535']['kappa'] == e['kappa']['pr535']['kappa'] and r['kappa']['pr535']['binding_component'] == e['kappa']['pr535']['binding_component']
assert comp['control_reproduces_pr535_kappa'] and comp['kappa_star_vs_pr535'] == e['kappa']['pr535']['kappa']
c = F(r['bit_lower'])
print('PASS bit c (v = %d, R = %d, cst = %d; PR #472 eleven-stage whole-residual pipeline, 10^-24 grid) = %s = %s' % (V, R, CST, r['bit_lower'], r['bit_lower_decimal']))
print('     %+.4f%% over PR #503 (R = 480, v = 120, c = %s) and %+.4f%% over the live bit c of PR #510 (%s)'
      % (100 * float(c / F(e['control']['bit_lower']) - 1), e['control']['bit_lower_decimal'],
         100 * float(c / F(e['live_bit']['bit_lower']) - 1), e['live_bit']['bit_lower_decimal']))
k = r['kappa']['pr535']
print("     with PR #535's complex b = %s: kappa = %s = %s (%s-bound; #535 published %s from the live bit c)"
      % (k['complex_lower'], k['kappa'], k['kappa_decimal'], k['binding_component'], comp['pr535_published_kappa']))
print('PASS %s  [%.0fs]' % ('LIGHT' if LIGHT else 'FULL', time.time() - T0))

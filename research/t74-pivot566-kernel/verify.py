"""verify.py: bounded replay of the pivot-566 helper-donor kernel on PR1319's T74 exact-fill construction.

Standard library plus the unchanged repository sources it pins (no third-party packages):
  1. pins: the live repository inputs (SOURCES.json), every file of PR1319's package against its MANIFEST.json, and
     every file of this package (PINS.json);
  2. rebuild.py: PR1297's two pinned words + inputs/EDITS.json reproduce the shipped words' scalar programs, the
     complete B + early-cleanup map is unchanged over all registers (exact Fractions), the interfaces and the remaining
     cleanup are byte-identical, and every new read of 566 sees its initial value;
  2b. kernel_check.py (RESTORATION.md): the restoration lemma at every pivot read, the nine-term ledger (zero at the end
     of the tail, no port at the end of B), the derived compensation, the frame recount and four mutated kernels,
     reproducing evidence/KERNEL-CHECK.json exactly;
  3. the unchanged independent audit_local.py (research/gauge44-frames-x/independent) passes on both shipped words and
     its recounted paid profiles equal the rebound PLAN provider profiles;
  4. bookkeeping: PLAN.profile = dispatch counts x provider profiles + unchanged idle remainder = SPEC expected profile,
     rank mass leaves the fixed deficit, owners/dispatch/template/construction pins equal PR1319's;
  5. kappa: certified complex endpoints recomputed with the retained moment engines (both engines accept at b and
     reject at b+1e-24), then the retained 47-constraint outer witness on the 1e-18 grid (PR1319 code/assemble.py
     logic with PAYLOAD = charged prefix bits) gives exactly SPEC.expected.kappa and conservative kappa, strictly above
     PR1319's kappa;
  6. evidence binding: the recorded strict T74 replay, refined (PR1549 200-digit) assembly and native receipts agree
     with SPEC / SPEC-R200 (the full chain itself is replay_full.py, not run here); the recorded fresh replay_full.py run
     (evidence/FULL-REPLAY.json, evidence/INTERFACES.json) has every stage, PR1319's own admission of the ancestor at its
     claimed kappa, the container and payload controls, identical call interfaces and equal hosting quantities;
  7. failure controls: flipped coefficient, dropped restore, read moved into the pivot's busy window, corrupted word byte
     and forged profile are all rejected.
usage: python3 -B verify.py"""
import copy, gzip, hashlib, importlib.util, json, subprocess, sys, tempfile
from decimal import Decimal
from fractions import Fraction as Q
from pathlib import Path
if not __debug__:
    raise SystemExit('verify.py: run without -O / PYTHONOPTIMIZE (its assert statements are the checks)')
PKG = Path(__file__).resolve().parent; ROOT = PKG.parents[1]; sys.path.insert(0, str(PKG))
import rebuild as RB, kernel_check as KC
P1319 = ROOT / 'research/global-mixed-t74-exact-fill'
MC = ROOT / 'research/complex-k492-owner-repair/vendor/multicold/engines'
AUDIT = ROOT / 'research/gauge44-frames-x/independent/audit_local.py'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rd(p): p = Path(p); return json.loads(gzip.decompress(p.read_bytes()) if p.suffix == '.gz' else p.read_bytes())
def load(n, p): s = importlib.util.spec_from_file_location(n, p); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
checks = {}
# 1. pins: repository inputs (SOURCES.json, written by scripts/new_research_package.py), every file of PR1319's package
#    against its own MANIFEST.json, and every file of this package (PINS.json)
src = rd(PKG / 'SOURCES.json'); repo = {f['path']: f['sha256'] for f in src['files']}
for f in src['files']:
    if f['usage'] == 'input': assert sha(ROOT / f['path']) == f['sha256'], ('repository input changed', f['path'])
man = rd(P1319 / 'MANIFEST.json')
assert {x.relative_to(P1319).as_posix() for x in P1319.rglob('*') if x.is_file() and '__pycache__' not in x.parts and x != P1319 / 'MANIFEST.json'} == set(man), 'PR1319 package file set differs from its MANIFEST'
for rel, h in man.items(): assert sha(P1319 / rel) == h, ('PR1319 package file changed', rel)
pins = rd(PKG / 'PINS.json')
for rel, h in pins['package'].items(): assert sha(PKG / rel) == h, ('package file changed', rel)
listed = set(pins['package']) | {'PINS.json'}
actual = {p.relative_to(PKG).as_posix() for p in PKG.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
assert actual == listed, ('unpinned or missing package files', sorted(actual ^ listed))
checks['pins'] = dict(repository_inputs=sum(1 for f in src['files'] if f['usage'] == 'input'), pr1319_manifest=len(man), package=len(pins['package']))
# 2. exact rebuild
E = rd(PKG / 'inputs/EDITS.json'); q = E['pivot']; reb = []
for name, (bp, npth) in RB.WORDS.items():
    r = RB.check(name, RB.load(bp), RB.load(npth), E['edit'], q); assert r['pass'], r; reb.append(r)
checks['rebuild'] = {r['word']: dict(rows=r['b_tail_map_rows'], differing=r['b_tail_map_rows_differing']) for r in reb}
# 2b. restoration argument over the whole program (RESTORATION.md): lemma, nine-term ledger, compensation, frames, controls
kc = {}
for name, (bp, npth) in KC.WORDS.items():
    base = KC.load(bp); r = KC.analyse(base, KC.load(npth), E['edit'], q); r['controls'] = KC.controls(base, E['edit'], q)
    r['pass'] = r['pass'] and all(c['rejected'] for c in r['controls'].values()); assert r['pass'], (name, {k: v for k, v in r.items() if k != 'ledger'}); kc[name] = r
assert json.dumps(kc, indent=1, sort_keys=True) + '\n' == (PKG / 'evidence/KERNEL-CHECK.json').read_text(encoding='utf-8'), 'kernel check differs from evidence/KERNEL-CHECK.json'
checks['restoration'] = {n: dict(D_end_of_B=r['D_end_of_B'], D_end_of_tail_zero=r['D_end_of_tail_zero'], compensation_gates=r['compensation_gates'],
                                 paid_profile_delta=r['paid_profile_delta'], controls_rejected=sum(c['rejected'] for c in r['controls'].values())) for n, r in kc.items()}
# 3. unchanged local audit on the shipped words
plan, spec, prof = rd(PKG / 'data/PLAN.json'), rd(PKG / 'data/SPEC.json'), rd(PKG / 'data/PROFILE.json')
words = {'gauge44': PKG / 'inputs/gauge44-word-566.json.gz', 'extra': PKG / 'inputs/extra-word-566.json.gz'}
aud = {}
for pid, w in words.items():
    with tempfile.TemporaryDirectory() as d:
        r = subprocess.run([sys.executable, '-B', str(AUDIT), '--word', str(w), '--output', d + '/AUDIT.json'], capture_output=True, text=True)
        assert r.returncode == 0, (pid, (r.stdout + r.stderr)[-2000:]); a = json.load(open(d + '/AUDIT.json'))
    assert a['status'] == 'PASS_INDEPENDENT_EXACT_FORWARD_AND_DUAL_ENDPOINT_FRAMES_ENTRANCES_CONES', a['status']
    assert a['local_profile'] == plan['provider_registry'][pid]['actual_paid_profile'] == spec['providers'][pid]['expected_profile'], pid
    aud[pid] = a['local_profile']
checks['audit_local'] = aud
# 4. bookkeeping against PR1319's unchanged owner map
for n in ('OWNERS.json.gz', 'DISPATCH.json', 'CONSTRUCTION.json', 'GLOBAL-TEMPLATE.json.gz'): assert sha(P1319 / n) == repo['research/global-mixed-t74-exact-fill/' + n]
old = rd(P1319 / 'PLAN.json'); counts = {}
for c in plan['provider_calls']: counts[c['provider']] = counts.get(c['provider'], 0) + 1
assert counts == {'gauge44': 249, 'extra': 417} and [c['provider'] for c in plan['provider_calls']] == [c['provider'] for c in old['provider_calls']]
assert {k: v for k, v in plan.items() if k not in ('provider_registry', 'provider_calls', 'profile', 'runtime_source_plan_sha256')} == {k: v for k, v in old.items() if k not in ('provider_registry', 'provider_calls', 'profile', 'runtime_source_plan_sha256')}
for pid in counts:
    a, b = plan['provider_registry'][pid], old['provider_registry'][pid]
    assert {k: a[k] for k in ('ports', 'centers', 'widths', 'directory')} == {k: b[k] for k in ('ports', 'centers', 'widths', 'directory')}, pid
H = {}
for pid, n in counts.items():
    for r, v in plan['provider_registry'][pid]['actual_paid_profile'].items(): H[int(r)] = H.get(int(r), 0) + n * v
for r, v in spec['expected']['idle_remainder_profile'].items(): H[int(r)] = H.get(int(r), 0) + v
assert {str(k): v for k, v in sorted(H.items())} == plan['profile'] == spec['expected']['global_profile'] == prof, 'global profile'
T, m = 74, 73; live, deficit = 896 * T, 320 * T
assert m * live - sum(r * n for r, n in H.items()) == deficit and spec['expected']['rank_mass'] == sum(r * n for r, n in H.items())
oldH = {int(r): n for r, n in old['profile'].items()}
checks['profile_delta_per_call'] = {r: (H.get(r, 0) - oldH.get(r, 0)) // 666 for r in sorted(set(H) | set(oldH)) if H.get(r, 0) != oldH.get(r, 0)}
# 5. kappa with the retained engines and outer witness
M, B, A = load('mc_moment', MC / 'moment.py'), load('mc_base_two', MC / 'base_two_moment.py'), load('mc_outer', MC / 'outer.py')
c = Q(rd(P1319 / 'inputs/PR589-EXPECTED.json')['nine']['bit_lower']); PAYLOAD = spec['geometry']['charged_prefix_bits']
def check_moment(h, lower, bad):
    for z, accept in ((lower, True), (lower + Q(1, 10 ** 24), False)):
        l, u = M.moment(h, m, live, z, bad); ll, uu = B.moment(m, live, list(h.items()), z)
        if bad:
            fl, fu = B.moment(m, live, [(1, 32 * m * m * sum(h.values()))], z); ll += fl / 10 ** 16; uu += fu / 10 ** 16
        assert (u < 1 and uu < 1) if accept else (l > 1 and ll > 1)
def ceil(x): return -((-x.numerator) // x.denominator)
def outer_witness(bb):
    eta = beta = Q(1, 10 ** 24); s = min(c, (1 - beta) * bb) - Q(1, 10 ** 27); assert 0 < s < c and s < (1 - beta) * bb
    chain = [Q(384599, 10 ** 10)]
    for _ in range(7):
        old_a = chain[-1]; a = (1 - s) * s + s * old_a; gap = min(s - a, 1 - a - s, 1 - a - s * (1 - old_a), 1 - s); assert old_a < a < s < 1 - a and gap > 0
        cut = max(ceil(Q(36) / gap ** 2), ceil(Q(2 * (4 + PAYLOAD)) / gap))
        assert cut * gap ** 2 >= 36 and cut * gap >= 2 * (4 + PAYLOAD); chain.append(a)
    qq = chain[-1] * (1 - 2 * eta); margin = (1 - eta) * qq / (1 + qq); ticks = margin * 10 ** 18; k = Q((ticks.numerator - 1) // ticks.denominator, 10 ** 18)
    bridge = {'semantic': {'C0': {'base': 2, 'exponent': 210000}, 'strict_literal_gap': 1}, 'rows': {'degree_gap': Q(10 ** 6) - Q(51 * 20161, 25)}}
    outer = A.assembly(chain[-1], bb, bridge, k, eta=eta, beta=beta); assert len(outer['strict_constraints']) == 47 and all(v > 0 for v in outer['strict_constraints'].values())
    for kk, ee, be in ((k + Q(1, 10 ** 18), eta, beta), (k, Q(0), beta), (k, eta, Q(0)), (k, eta, Q(1))):
        try: A.assembly(chain[-1], bb, bridge, kk, eta=ee, beta=be)
        except AssertionError: pass
        else: raise AssertionError('outer rejection control accepted')
    return k
b = Q(M.certify(H, m, live, False)['lower']); bc = Q(M.certify(H, m, live, True)['lower'])
assert b == Q(spec['expected']['complex_lower']) and bc == Q(spec['expected']['conservative_complex_lower'])
check_moment(H, b, False); check_moment(H, bc, True)
k, kc = outer_witness(b), outer_witness(bc)
assert k == Q(spec['expected']['kappa']) and str(Decimal(k.numerator) / Decimal(k.denominator)) == spec['expected']['kappa_decimal']
k1319 = Q(rd(P1319 / 'SPEC.json')['expected']['kappa']); assert k > k1319
checks['kappa'] = dict(kappa=str(k), complex_lower=str(b), conservative_kappa=str(kc), gain_over_pr1319=str(k - k1319))
# 6. evidence binding
ev = rd(PKG / 'evidence/STRICT-T74.json'); assert ev['status'] == 'PASS_STRICT_MIXED_T74_EXACT_FILL' and ev['kappa'] == spec['expected']['kappa']
assert ev['controls_rejected'] == dict(admission=114, bit=12, geometry=6, independent_owner=8, outer=4) and ev['global_profile'] == plan['profile']
nat = rd(PKG / 'evidence/NATIVE.json')
for pid in ('gauge44', 'extra'):
    assert nat[pid]['steps'] == ['native', 'ledgers', 'local-replay', 'wrappers', 'phases'] and all(x == 0 for x in nat[pid]['exit_codes'])
    assert nat[pid]['full_word_sha256'] == sha(words[pid]) or nat[pid]['full_word_content_sha256'] == hashlib.sha256(gzip.decompress(words[pid].read_bytes())).hexdigest()
r200 = rd(PKG / 'evidence/REFINED-R200.json'); s200 = rd(PKG / 'data/SPEC-R200.json')
assert r200['status'] == 'PASS_STRICT_MIXED_T74_EXACT_FILL' and r200['kappa'] == s200['expected']['kappa'] and s200['outer_refinement'] == dict(grid_digits=200, margin_digits=250, endpoint_digits=200, bootstrap_steps=90)
assert Decimal(r200['kappa_decimal']) > Decimal(rd(PKG / 'RESULT.json')['predecessors']['pr1549']['kappa_decimal'])
checks['refined_kappa_decimal_prefix'] = r200['kappa_decimal'][:40]
# 6b. the separate replay (replay_full.py, one fresh work directory): ancestor admission and kernel side by side
STAGES = ['parent', 'ancestor-reconstruct-owners', 'ancestor-lift-parent', 'ancestor-container-control', 'ancestor-strict-t74', 'ancestor-geometry',
          'native-gauge44', 'native-extra', 'rebind', 'strict-t74', 'geometry', 'kernel-check', 'interfaces', 'fine-engine-oracle', 'strict-r200']
fr = rd(PKG / 'evidence/FULL-REPLAY.json')
assert fr['status'] == 'PASS_T74_PIVOT566_KERNEL_COMPLETE_FINITE_ADMISSION' and fr['kappa'] == spec['expected']['kappa'] and fr['refined_kappa'] == s200['expected']['kappa']
assert [x['name'] for x in fr['stages']] == STAGES and all(x['exit_code'] == 0 for x in fr['stages']), 'replay stages'
assert not any(fr['native_reuse']['ancestor'].values()) and not any(fr['native_reuse']['kernel'].values()), 'the recorded replay must be fresh'
anc = fr['ancestor']
assert anc['kappa'] == rd(P1319 / 'CLAIM.json')['kappa'] and anc['strict_status'] == 'PASS_STRICT_MIXED_T74_EXACT_FILL' and anc['geometry_controls_rejected'] == 6
assert anc['container_control']['plan_paths_changed'] == ['assignment_sha256', 'replica_lift.owners_file_sha256'] and anc['payload_control_rejected']
itf = rd(PKG / 'evidence/INTERFACES.json')
assert itf['call_interfaces_identical'] and all(v['identical'] for v in itf['interface'].values())
assert itf['kappa'] == dict(ancestor=anc['kappa'], kernel=spec['expected']['kappa']) and all(v['equal'] for v in itf['hosting_summary'].values())
allowed = ('profile.', 'provider_calls[*].local_program_sha256 ', 'provider_registry.gauge44.', 'provider_registry.extra.')
assert all(x.startswith(allowed) for x in itf['plan']) and all(x.split('.')[2] in ('actual_paid_profile', 'artifact_semantic_sha256', 'artifact_sha256', 'orientation_program_sha256') for x in itf['plan'] if x.startswith('provider_registry.'))
for pid in ('gauge44', 'extra'): assert itf['native'][pid]['RESIDUAL-ADAPTERS.json'] == itf['native'][pid]['WRAPPER-CHECKS.json'] == 'identical bytes'
assert itf['hosting']['global/hosted']['ACTUAL-SIGMAS.json.gz'] == itf['hosting']['global/hosted']['IDLE-REMAINDER-FRAMES.json.gz'] == 'identical bytes'
checks['separate_replay'] = dict(stages=len(STAGES), ancestor_kappa=anc['kappa'], call_interfaces_identical=True,
                                 hosting_equal=sorted(itf['hosting_summary']), plan_paths_differing=len(itf['plan']))
# 7. failure controls
def rejects(fn):
    try: fn()
    except AssertionError: return True
    return False
def bad_edit(mut, prop):
    ed = copy.deepcopy(E['edit']); mut(ed)
    def f():
        for name, (bp, npth) in RB.WORDS.items():
            base = RB.load(bp); r = RB.analyse(base, *RB.compile_edits(base, ed), q); assert r[prop], (name, prop)
    return f
def flip(ed): ed['insert'][3][1][3] = -ed['insert'][3][1][3]                       # donor 672 opened with +2q instead of -2q
def drop_restore(ed): ed['tail'] = []                                              # helper window on 98 never closed
def busy(ed): ed['insert'][6][0] = 900                                             # 98 -= q moved after 566's B write
def corrupt():
    raw = bytearray(gzip.decompress(words['gauge44'].read_bytes())); i = raw.index(b'"B"') + 40; raw[i] = (raw[i] + 1) % 256
    assert hashlib.sha256(gzip.compress(bytes(raw), mtime=0)).hexdigest() == pins['package']['inputs/gauge44-word-566.json.gz']
def forged():                                                                       # mass-neutral forgery (H1 +2, H2 -1): kappa must move
    h = dict(H); h[1] += 2; h[2] -= 1; assert m * live - sum(r * n for r, n in h.items()) == deficit
    assert outer_witness(Q(M.certify(h, m, live, False)['lower'])) == k
controls = dict(flipped_coefficient=rejects(bad_edit(flip, 'exact')), dropped_restore=rejects(bad_edit(drop_restore, 'exact')), read_in_busy_window=rejects(bad_edit(busy, 'inserted_reads_where_pivot_is_initial')), corrupted_word=rejects(corrupt), forged_profile=rejects(forged))
assert all(controls.values()), controls; checks['failure_controls'] = controls
print(json.dumps(checks, indent=1, sort_keys=True))
print('PASS_T74_PIVOT566_KERNEL_BOUNDED', checks['kappa']['kappa'], flush=True)

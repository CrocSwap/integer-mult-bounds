"""layer_end_controls_leaver.py LAYERED-WORD.json.gz ROUTING OUTDIR [ENTERING] (env PR635_CODE, optional env LEC_REASON_PINS
= JSON file {mutant key: expected reason key or literal message substring}).  LeaverSAT variant of the signed
layers_p6n/layer_end_controls.py (fc58c569...): IDENTICAL mutations and checks; the only change is that the expected
rejection reason of a named mutant can be re-pinned per word (on the leaver words, with fewer cold ends, the premix-drop
and into-full mutants are caught by the arbitrary-dirt endpoint replay before the pinned site is reached).  Every
mutation is still REQUIRED to be rejected at its (re-)pinned reason; the unmutated word MUST pass.
Original docstring: layer_end_controls.py LAYERED-WORD.json.gz ROUTING OUTDIR (env PR635_CODE): adapted PR635 cold_end_controls.py (LayerReviewer): raw-word negative controls for the cold low-frame ends and the
refactored cleanup accepted by hpe_audit_and_transport.py.  Every mutation MUST be rejected (AssertionError); the
unmutated word MUST pass.  Apache-2.0.  DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code."""
import copy, gzip, json, shutil, sys, tempfile
from pathlib import Path
import os
sys.path.insert(0, os.environ['PR635_CODE'])   # PR635's unchanged hpe_audit_and_transport.py
import hpe_audit_and_transport as atc

src, routing, outdir = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
word = json.load(gzip.open(src))
v, R = word['report']['v'], word['report']['R']; n = 2*v + R
regs = lambda e: [e[1]] + ([e[2]] if e[0] == 'add' else [])
meta = word['refactored_cleanup']
cold = [int(h) for h in meta['cold_low_frame_ended_helpers']]
npre = meta['premix_gates']; nlow = meta['lower_frame_gates']
early = word['early_cleanup']; eidx = {i for i, _ in early}
rest = [i for i in range(len(word['cleanup'])) if i not in eidx]


def trial(w):
    """None if the transport audit accepts w, else the AssertionError message."""
    tmp = Path(tempfile.mkdtemp())
    p = tmp/'w.json.gz'; p.write_bytes(gzip.compress(json.dumps(w).encode(), mtime=0))
    try:
        atc.run(p, routing, tmp/'out')
        return None
    except AssertionError as e:
        return repr(e.args[0]) if e.args else 'AssertionError'
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# Pinned rejection reasons: each mutant must fail at this assertion of hpe_audit_and_transport.py (message substring).
ENDPOINT, COLDPRE, CONE = "'arbitrary-dirt endpoint'", 'touches a cold hyperplane-ended helper', 'hpe cone pre-check (row / column)'
WHY = dict(premix_to_precondition=COLDPRE, premix_dropped=COLDPRE, e_premix_dropped=ENDPOINT, lower_dropped=ENDPOINT,
           remainder_dropped=ENDPOINT, coefficient=ENDPOINT, into_full='cleanup on non-FULL end', dyadic=ENDPOINT, frame_below="'nonmonotone'",
           nonmonotone="'nonmonotone'", other_frame=CONE, cone=CONE, extra_end=COLDPRE, marker='cleanup is not the literal reversed inverse',
           target='refactored cleanup touches a target', profile_pin='paid local profile differs from the reported local_profile',
           entering_precondition='zero-frame precondition/compensation touches an entering helper')
_REASONS = dict(ENDPOINT=ENDPOINT, COLDPRE=COLDPRE, CONE=CONE)
if os.environ.get('LEC_REASON_PINS'):
    for _k, _v in json.loads(Path(os.environ['LEC_REASON_PINS']).read_text()).items():
        assert _k in WHY, ('unknown mutant key', _k); WHY[_k] = _REASONS.get(_v, _v)
assert trial(word) is None, 'unmutated cold-end word must pass'
results = []


def reject(name, mut, why):
    """the mutation must be rejected, and for the pinned reason (a substring of the audit's assertion message)."""
    w = copy.deepcopy(word); mut(w)
    msg = trial(w)
    assert msg is not None, 'cold-end mutation accepted: ' + name
    assert why in msg, 'cold-end mutation %r rejected for the wrong reason: %s' % (name, msg[:300])
    results.append(name); print('rejected', name, '|', why, flush=True)


h0 = cold[0]
i0, U0 = next((i, f) for i, f in early if h0 in regs(word['cleanup'][i]))
r0 = rest[len(rest)//2]


def premix_to_precondition(w):   # premix before the wrappers; compensation then reads the cold ends
    w['precondition'] = w['precondition'] + w['A'][:npre]; w['A'] = w['A'][npre:]


def lower_gate_into_full(w):     # a lower-frame gate on a cold-ended helper executed in the FULL remainder instead
    w['early_cleanup'] = [x for x in w['early_cleanup'] if x[0] != i0]


def drop_cleanup_gate(w, i):   # remove the gate AND its early_cleanup entry: a structurally valid word missing one gate
    w['cleanup'].pop(i)
    w['early_cleanup'] = [[j - (j > i), f] for j, f in w['early_cleanup'] if j != i]


def other_frame(w):              # a different frame of the same dimension as the cold end (another cold helper's)
    f = next(w['helper_final'][str(h)] for h in cold if w['helper_final'][str(h)] != w['helper_final'][str(h0)])
    w['helper_final'][str(h0)] = f


def extra_cold_end(w):           # declare a premixed partner of h0 cold-ended at h0's frame: fails the row/column cone
    p = next(r for e in w['A'][:npre] for r in regs(e) if r != h0 and h0 in regs(e))
    w['helper_final'][str(p)] = w['helper_final'][str(h0)]


reject('premix placed in the zero-frame precondition (before the cold wrappers)', premix_to_precondition, WHY['premix_to_precondition'])
reject('one premix gate dropped (the compensation then reads a cold-ended helper)', lambda w: w['A'].pop(npre - 1), WHY['premix_dropped'])
reject('one lower-frame cleanup gate dropped (gate and its early_cleanup entry)', lambda w: drop_cleanup_gate(w, i0), WHY['lower_dropped'])
reject('one FULL-remainder gate dropped', lambda w: drop_cleanup_gate(w, r0), WHY['remainder_dropped'])
reject('lower-frame gate coefficient changed', lambda w: w['cleanup'][i0].__setitem__(3, w['cleanup'][i0][3] * 2), WHY['coefficient'])
reject('lower-frame gate moved into the FULL remainder (touches a cold-ended helper at FULL)', lower_gate_into_full, WHY['into_full'])
reject('lower-frame gate frame below its registers\' frames', lambda w: next(x for x in w['early_cleanup'] if x[0] == i0).__setitem__(1, U0[:-1]), WHY['frame_below'])
reject('cold end at another dim-4 frame', other_frame, WHY['other_frame'])
# PROFILE-PIN control: without its helper_final entry the cold-ended helper is a valid FULL-ended helper; the word is
# rejected because its reported paid profile (which counts the low end) no longer matches the frame chains.
reject('profile pin: cold end dropped (valid FULL end, but the reported profile counts the low end)', lambda w: w['helper_final'].pop(str(h0)), WHY['profile_pin'])
reject('extra cold end on a premixed partner (the compensation reads it before its wrapper)', extra_cold_end, WHY['extra_end'])
reject('refactored-cleanup marker removed (literal-inverse rule applies)', lambda w: w.pop('refactored_cleanup'), WHY['marker'])
reject('remainder gate retargeted to a target register', lambda w: w['cleanup'][r0].__setitem__(1, v + 3), WHY['target'])
reject('non-dyadic remainder coefficient', lambda w: w['cleanup'][r0].__setitem__(4 if w['cleanup'][r0][0] == 'add' else 3, 3 * w['cleanup'][r0][4 if w['cleanup'][r0][0] == 'add' else 3]), WHY['dyadic'])
reject('profile not updated (paid climbs misreported)', lambda w: w['report']['local_profile'].__setitem__('5', w['report']['local_profile']['5'] - 1), WHY['profile_pin'])
ent = [int(h) for h in sys.argv[4].split(',')] if len(sys.argv) > 4 else [int(h) for h in meta.get('entering_low_frame_ended_helpers', [])]
for e0 in ent:   # ENTERING LOW-FRAME ENDS (ColdSupply extension; every entering end; absent for words without them)
    j0 = next((i for i, e in enumerate(word['A'][:npre]) if e0 in regs(e)), None)
    print('entering end', e0, 'premix gate', j0, flush=True)
    k0, Ue = next((i, f) for i, f in early if e0 in regs(word['cleanup'][i]))
    def to_pre(w, j0=j0): w['precondition'].append(w['A'][j0]); w['A'].pop(j0)
    def other_hp(w, e0=e0, Ue=Ue): w['helper_final'][str(e0)] = next(f for h, f in w['helper_final'].items() if len(f) == len(Ue) and sorted(f) != sorted(Ue))
    if j0 is not None: reject('entering end %d: premix gate dropped' % e0, lambda w, j0=j0: w['A'].pop(j0), WHY['e_premix_dropped'])
    if j0 is not None: reject('entering end %d: premix gate at frame [] instead of its entrance E' % e0, lambda w, j0=j0: w['A'][j0].__setitem__(-1, []), WHY['nonmonotone'])
    if j0 is not None: reject('entering end %d: premix gate moved into the zero-frame precondition' % e0, to_pre, WHY['entering_precondition'])
    reject('entering end %d: lower-frame gate dropped (gate and its early_cleanup entry)' % e0, lambda w, k0=k0: drop_cleanup_gate(w, k0), WHY['lower_dropped'])
    reject('entering end %d: profile pin: end dropped (valid FULL end, but the reported profile counts the low end)' % e0, lambda w, e0=e0: w['helper_final'].pop(str(e0)), WHY['profile_pin'])
    reject('entering end %d: end at another hyperplane' % e0, other_hp, WHY['cone'])
# Pinned rejection reasons of the COLD-BEYOND mutants (substrings of hpe_audit_and_transport.py assertion messages).
MYWHY = dict(tw_precondition=COLDPRE, tw_dropped=COLDPRE, tw_coefficient=COLDPRE, tw_other_block=COLDPRE,
             tw_entering='zero-frame compensation reads an entering helper',
             ab_dropped=ENDPOINT, ab_coefficient=ENDPOINT, ab_early=ENDPOINT, ab_live=ENDPOINT, ab_centre=ENDPOINT,
             ab_lower="'nonmonotone'", ab_higher="'nonmonotone'",
             sh_dropped=ENDPOINT, sh_coefficient=ENDPOINT, rel_dropped=ENDPOINT, rel_coefficient=ENDPOINT, rel_live=ENDPOINT,
             h8_other=CONE, h8_lower=ENDPOINT)
# COLD-BEYOND primitives (present only when the word carries them): frame-[] target writes in the premix (explicit
# post-wrapper compensation of an ended helper's dirt) and forward absorptions into dead registers.
nw = meta.get('premix_target_writes', 0)
if nw:
    wi = [i for i in range(npre) if v <= word['A'][i][1] < 2*v]
    assert len(wi) == nw

    def writes_to_precondition(w):   # the target writes run before the cold wrappers (inside the zero-frame precondition)
        g = [w['A'][i] for i in wi]; w['precondition'] = w['precondition'] + g
        w['A'] = [e for i, e in enumerate(w['A']) if i not in set(wi)]
    reject('premix target writes placed in the zero-frame precondition (before the cold wrappers)', writes_to_precondition, MYWHY['tw_precondition'])
    reject('one premix target write dropped (compensation must read an ended helper)', lambda w: w['A'].pop(wi[0]), MYWHY['tw_dropped'])
    reject('premix target write coefficient changed', lambda w: w['A'][wi[0]].__setitem__(3, w['A'][wi[0]][3] * 2), MYWHY['tw_coefficient'])
    # (reading another register that carries the SAME weight of the ended helper's dirt is a valid variant, so the mutant reads
    #  the same factory slot of the next block, which carries none of it)
    entering_regs = sorted(int(r) for r in word.get('start_extra', {}))
    reject('premix target write reads an entering helper', lambda w: w['A'][wi[0]].__setitem__(2, entering_regs[0]), MYWHY['tw_entering'])
    reject('premix target write reads a cold helper of another block', lambda w: w['A'][wi[0]].__setitem__(2, 2*v + (w['A'][wi[0]][2] - 2*v + 16) % 224), MYWHY['tw_other_block'])
ab = meta.get('forward_absorption_A_indices', [])
if any(len(word['helper_final'][str(h)]) == 8 for h in cold):
    # with dim-8 cold ends, the centre-retargeted absorption first leaks an ended helper's dirt into the cut's targets
    MYWHY['ab_centre'] = COLDPRE
if ab:
    # the ColdBeyond U_b absorption (q += -1/2 g); ColdThird's extra absorptions have their own controls below
    a0 = next(a for a in ab if word['A'][a][3] * 2 == -word['A'][a][4]); g0 = word['A'][a0]

    def absorption_moved_early(w):   # absorbed before the absorbed register's last kernel write
        e = w['A'].pop(a0); j = max(i for i in range(npre, a0) if g0[2] == w['A'][i][1] and w['A'][i][-1] == g0[-1])
        w['A'].insert(j, e)

    def absorption_into_live(w):     # q += a g moved right after g's previous frame-mate gate, while q is still live
        e = w['A'].pop(a0); j = max(i for i in range(npre, a0) if g0[1] in regs(w['A'][i]))
        w['A'].insert(j, e)
    reject('forward absorption dropped', lambda w: w['A'].pop(a0), MYWHY['ab_dropped'])
    reject('forward absorption into a centre (a live register read by the cut)', lambda w: w['A'][a0].__setitem__(1, next(c for c in word['centers'] if c not in g0[1:3] and c not in cold)), MYWHY['ab_centre'])
    reject('forward absorption coefficient changed', lambda w: w['A'][a0].__setitem__(3, w['A'][a0][3] * 2), MYWHY['ab_coefficient'])
    reject('forward absorption placed before the absorbed register\'s last kernel write', absorption_moved_early, MYWHY['ab_early'])
    reject('forward absorption placed while the absorbing register is still live', absorption_into_live, MYWHY['ab_live'])
    reject('forward absorption at a lower frame than its registers', lambda w: w['A'][a0].__setitem__(-1, w['A'][a0][-1][:-1]), MYWHY['ab_lower'])
    reject('forward absorption at a higher frame (FULL) than its registers', lambda w: w['A'][a0].__setitem__(-1, [256, 128, 64, 32, 16, 8, 4, 2, 1]), MYWHY['ab_higher'])
# COLD-THIRD primitives (present only when the word carries them): several absorptions after one input gate, dirt-release
# absorptions (a dead port takes a live helper's value so that a hyperplane unit's column has no dirt on it), and cold ends at
# a dim-8 frame with lifted partners.
hyper = [h for h in cold if len(word['helper_final'][str(h)]) == 8]
if hyper and ab:
    sh = next(a for a, b in zip(ab, ab[1:]) if b == a + 1)              # two absorptions sharing one input anchor
    rel = next(a for a in ab if a - 1 not in ab and a + 1 not in ab and word['A'][a][2] in hyper and word['A'][a][3] * 2 != -word['A'][a][4])
    hh = hyper[0]; ih = next(i for i, f in early if hh in regs(word['cleanup'][i]))
    reject('second absorption sharing an input anchor dropped', lambda w: w['A'].pop(sh + 1), MYWHY['sh_dropped'])
    reject('shared-anchor absorption coefficient changed', lambda w: w['A'][sh + 1].__setitem__(3, w['A'][sh + 1][3] * 2), MYWHY['sh_coefficient'])
    reject('dirt-release absorption dropped', lambda w: w['A'].pop(rel), MYWHY['rel_dropped'])
    reject('dirt-release absorption coefficient changed', lambda w: w['A'][rel].__setitem__(3, w['A'][rel][3] * 2), MYWHY['rel_coefficient'])
    jr = max(i for i in range(npre, rel) if word['A'][i][0] == 'add' and word['A'][i][2] == word['A'][rel][1])

    def release_while_read(w):   # the release runs before a kernel gate that still READS the port (port live)
        e = w['A'].pop(rel); w['A'].insert(jr, e)
    reject('dirt-release absorption moved before a kernel gate that still reads the port', release_while_read, MYWHY['rel_live'])
if hyper:
    # dim-8 cold-end controls for EVERY dim-8 cold end of the word (read from the word's helper_final and the recipe meta's
    # cold_low_frame_ended_helpers), not one representative per terminal frame
    for hh in hyper:
        ih = next(i for i, f in early if hh in regs(word['cleanup'][i]))
        Uh = word['helper_final'][str(hh)]
        reject('dim-8 cold end %d (frame %s) at another dim-8 frame' % (hh, Uh), lambda w, hh=hh: w['helper_final'].__setitem__(str(hh), next(f for h, f in w['helper_final'].items() if len(f) == 8 and sorted(f) != sorted(w['helper_final'][str(hh)]))), MYWHY['h8_other'])
        reject('dim-8 cold end %d (frame %s): one lower-frame gate dropped (gate and its early_cleanup entry)' % (hh, Uh), lambda w, ih=ih: drop_cleanup_gate(w, ih), MYWHY['h8_lower'])
        reject('dim-8 cold end %d (frame %s): profile pin (end dropped)' % (hh, Uh), lambda w, hh=hh: w['helper_final'].pop(str(hh)), WHY['profile_pin'])
# FACTORED ACCUMULATOR (CarrierBypass; present only when the word carries one): a lower-frame tail gate a += x*g on two
# non-ended registers whose accumulator a is afterwards read by a dim-8 cold end's tail gate (h += y*a at its U).
ended_all = {int(h) for h in word['helper_final']}
tailg = [(i, word['cleanup'][i]) for i, _ in early]
accs = []   # EVERY factored accumulator gate (one per accumulator register a), each controlled on its own
for k, (i, e) in enumerate(tailg):
    if e[0] == 'add' and e[1] not in ended_all and e[2] not in ended_all and len(next(f for j, f in early if j == i)) < 8:
        if e[1] not in [word['cleanup'][j][1] for j in accs] and any(t[0] == 'add' and t[2] == e[1] and t[1] in hyper for _, t in tailg[k + 1:]):
            accs.append(i)
for acc in accs:
    a = word['cleanup'][acc][1]
    reject('factored accumulator %d (gate %d) zeroed' % (a, acc), lambda w, acc=acc: w['cleanup'][acc].__setitem__(3, 0), ENDPOINT)
    reject('factored accumulator %d (gate %d) coefficient doubled' % (a, acc), lambda w, acc=acc: w['cleanup'][acc].__setitem__(3, w['cleanup'][acc][3] * 2), ENDPOINT)
outdir.mkdir(parents=True, exist_ok=True)
(outdir/'COLD-END-CONTROLS.json').write_text(json.dumps(dict(status='PASS_COLD_END_RAW_WORD_CONTROLS', word=str(src), rejected=results), indent=1) + '\n')
print('PASS', len(results), 'cold-end raw-word mutations rejected')

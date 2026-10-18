"""cold_end_controls.py COLD-END-WORD.json.gz ROUTING OUTDIR : raw-word negative controls for the cold low-frame ends and the
refactored cleanup accepted by hpe_audit_and_transport.py.  Every mutation MUST be rejected (AssertionError); the
unmutated word MUST pass.  Apache-2.0.  DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code."""
import copy, gzip, json, shutil, sys, tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
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
           remainder_dropped=ENDPOINT, coefficient=ENDPOINT, into_full=ENDPOINT, dyadic=ENDPOINT, frame_below="'nonmonotone'",
           nonmonotone="'nonmonotone'", other_frame=CONE, cone=CONE, extra_end=COLDPRE, marker='cleanup is not the literal reversed inverse',
           target='refactored cleanup touches a target', profile_pin='paid local profile differs from the reported local_profile',
           entering_precondition='zero-frame precondition/compensation touches an entering helper')
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
ent = [int(h) for h in meta.get('entering_low_frame_ended_helpers', [])]
for e0 in ent:   # ENTERING LOW-FRAME ENDS (ColdSupply extension; every entering end; absent for words without them)
    j0 = next(i for i, e in enumerate(word['A'][:npre]) if e0 in regs(e))
    k0, Ue = next((i, f) for i, f in early if e0 in regs(word['cleanup'][i]))
    def to_pre(w, j0=j0): w['precondition'].append(w['A'][j0]); w['A'].pop(j0)
    def other_hp(w, e0=e0, Ue=Ue): w['helper_final'][str(e0)] = next(f for h, f in w['helper_final'].items() if len(f) == len(Ue) and sorted(f) != sorted(Ue))
    reject('entering end %d: premix gate dropped' % e0, lambda w, j0=j0: w['A'].pop(j0), WHY['e_premix_dropped'])
    reject('entering end %d: premix gate at frame [] instead of its entrance E' % e0, lambda w, j0=j0: w['A'][j0].__setitem__(-1, []), WHY['nonmonotone'])
    reject('entering end %d: premix gate moved into the zero-frame precondition' % e0, to_pre, WHY['entering_precondition'])
    reject('entering end %d: lower-frame gate dropped (gate and its early_cleanup entry)' % e0, lambda w, k0=k0: drop_cleanup_gate(w, k0), WHY['lower_dropped'])
    reject('entering end %d: profile pin: end dropped (valid FULL end, but the reported profile counts the low end)' % e0, lambda w, e0=e0: w['helper_final'].pop(str(e0)), WHY['profile_pin'])
    reject('entering end %d: end at another hyperplane' % e0, other_hp, WHY['cone'])
outdir.mkdir(parents=True, exist_ok=True)
(outdir/'COLD-END-CONTROLS.json').write_text(json.dumps(dict(status='PASS_COLD_END_RAW_WORD_CONTROLS', word=str(src), rejected=results), indent=1) + '\n')
print('PASS', len(results), 'cold-end raw-word mutations rejected')

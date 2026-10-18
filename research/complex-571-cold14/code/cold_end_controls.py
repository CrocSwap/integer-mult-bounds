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
    tmp = Path(tempfile.mkdtemp())
    p = tmp/'w.json.gz'; p.write_bytes(gzip.compress(json.dumps(w).encode(), mtime=0))
    try:
        atc.run(p, routing, tmp/'out')
        return True
    except AssertionError:
        return False
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


assert trial(word), 'unmutated cold-end word must pass'
results = []


def reject(name, mut):
    w = copy.deepcopy(word); mut(w)
    assert not trial(w), 'cold-end mutation accepted: ' + name
    results.append(name); print('rejected', name, flush=True)


h0 = cold[0]
i0, U0 = next((i, f) for i, f in early if h0 in regs(word['cleanup'][i]))
r0 = rest[len(rest)//2]


def premix_to_precondition(w):   # premix before the wrappers; compensation then reads the cold ends
    w['precondition'] = w['precondition'] + w['A'][:npre]; w['A'] = w['A'][npre:]


def lower_gate_into_full(w):     # a lower-frame gate on a cold-ended helper executed in the FULL remainder instead
    w['early_cleanup'] = [x for x in w['early_cleanup'] if x[0] != i0]


def drop_cleanup_gate(w, i):
    w['cleanup'].pop(i)
    w['early_cleanup'] = [[j - (j > i), f] for j, f in w['early_cleanup']]


def other_frame(w):              # a different frame of the same dimension as the cold end (another cold helper's)
    f = next(w['helper_final'][str(h)] for h in cold if w['helper_final'][str(h)] != w['helper_final'][str(h0)])
    w['helper_final'][str(h0)] = f


def extra_cold_end(w):           # declare a premixed partner of h0 cold-ended at h0's frame: fails the row/column cone
    p = next(r for e in w['A'][:npre] for r in regs(e) if r != h0 and h0 in regs(e))
    w['helper_final'][str(p)] = w['helper_final'][str(h0)]


reject('premix placed in the zero-frame precondition (before the cold wrappers)', premix_to_precondition)
reject('one premix gate dropped', lambda w: w['A'].pop(npre - 1))
reject('one lower-frame cleanup gate dropped', lambda w: drop_cleanup_gate(w, i0))
reject('one FULL-remainder gate dropped', lambda w: drop_cleanup_gate(w, r0))
reject('lower-frame gate coefficient changed', lambda w: w['cleanup'][i0].__setitem__(3, w['cleanup'][i0][3] * 2))
reject('lower-frame gate moved into the FULL remainder (touches a cold-ended helper at FULL)', lower_gate_into_full)
reject('lower-frame gate frame below its registers\' frames', lambda w: next(x for x in w['early_cleanup'] if x[0] == i0).__setitem__(1, U0[:-1]))
reject('cold end at another dim-4 frame', other_frame)
reject('cold end dropped (helper climbs to FULL but nothing cleans it there)', lambda w: w['helper_final'].pop(str(h0)))
reject('extra cold end on a premixed partner (row/column cone)', extra_cold_end)
reject('refactored-cleanup marker removed (literal-inverse rule applies)', lambda w: w.pop('refactored_cleanup'))
reject('remainder gate retargeted to a target register', lambda w: w['cleanup'][r0].__setitem__(1, v + 3))
reject('non-dyadic remainder coefficient', lambda w: w['cleanup'][r0].__setitem__(4 if w['cleanup'][r0][0] == 'add' else 3, 3 * w['cleanup'][r0][4 if w['cleanup'][r0][0] == 'add' else 3]))
reject('profile not updated (paid climbs misreported)', lambda w: w['report']['local_profile'].__setitem__('5', w['report']['local_profile']['5'] - 1))
outdir.mkdir(parents=True, exist_ok=True)
(outdir/'COLD-END-CONTROLS.json').write_text(json.dumps(dict(status='PASS_COLD_END_RAW_WORD_CONTROLS', word=str(src), rejected=results), indent=1) + '\n')
print('PASS', len(results), 'cold-end raw-word mutations rejected')

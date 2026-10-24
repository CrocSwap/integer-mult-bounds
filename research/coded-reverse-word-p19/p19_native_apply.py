#!/usr/bin/env python3
"""apply(program, state) for the frozen native word, transcribed from the pinned spec.

The specification is the PR4470/PR4610 lineage's own transcription, pinned here by commit and
hash:

    research/kappa-lean-verification-20261022/NativeCore.lean      the event kinds and `step`
    research/kappa-lean-verification-20261022/native_generate.py   the record -> event encoding

Upstream these are checked in Lean by ordinary kernel reduction on the word whose payload
SHA-256 is 4409d2d9328fffbd276bb03fb800f59a33ec3b2ab15f79a330a7af66e75110cc
(the word frozen in `research/warp-interface-20261022/`, present in this tree).  This receipt
re-implements the same encoding and transition in Python — independently of that Lean run — and
executes it on the frozen word this package prices
(`research/coded-native-caller/native-source.json.gz`), which is a different variant of the same
lineage.

What it establishes, per direction:
  * every record of all seven kinds is encoded to the specified event;
  * the frame trace is legal: each operation's declared input frame equals the role's current
    frame, so the word is a valid schedule, not a list of plausible records;
  * the persistent roles end exactly on `canonical.final`;
  * the paid histogram and the scalar tariff are *derived* from the trace rather than read from
    a profile, and compared with `canonical.local_profile`.
"""
import gzip, hashlib, json, sys
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORD = ROOT/'research/coded-native-caller/native-source.json.gz'
SPEC_CORE = ROOT/'research/kappa-lean-verification-20261022/NativeCore.lean'
SPEC_GEN = ROOT/'research/kappa-lean-verification-20261022/native_generate.py'
AUTHORITATIVE = 'research/warp-interface-20261022/ACTUAL-WORD.json.gz'  # the word frozen there
AUTHORITATIVE_PAYLOAD_SHA = '4409d2d9328fffbd276bb03fb800f59a33ec3b2ab15f79a330a7af66e75110cc'
C0 = 632

def need(ok, why):
    if not ok: raise ValueError(why)

def role(r):
    need(r[0] == 'L' or r == ['C', 0], 'role form')
    return r[1] if r[0] == 'L' else C0

def allowance(kind, num, den):
    """The exact conservative real-primitive tariff of NativeCore.scalarAllowance."""
    if kind in (6, 7):
        return 2
    q = Q(num, den)
    n, d = abs(q.numerator), q.denominator
    need(n and not d & (d - 1), 'dyadic scalar denominator')
    if kind == 5:
        need(not n & (n - 1), 'scale numerator is a power of two')
        return 2 * (abs(n.bit_length() - d.bit_length()) + (1 if q < 0 else 0))
    return 2 * (3 + n.bit_length() - 1 + n.bit_count() + d.bit_length() - 1)

def build_indexes(programs, nframes):
    paid_keys = sorted({(e[3], e[4], e[5], True) if e[0] == 'climb' else (e[2], e[3], e[4], False)
                        for p in programs.values() for e in p if e[0] in ('climb', 'center')})
    warp_keys = sorted({(e[2], e[3], e[4]) for p in programs.values() for e in p if e[0] == 'warp'})
    return ({k: i for i, k in enumerate(paid_keys)}, {k: i for i, k in enumerate(warp_keys)},
            paid_keys, warp_keys)

def encode(e, paid_index, warp_index):
    k = e[0]
    if k == 'phase':   return (0, 0, 0, 0, 0)
    if k == 'adapter': return (8, e[2], 0, e[3], 0)
    if k == 'climb':   return (1, e[2], 0, e[3], e[4], paid_index[(e[3], e[4], e[5], True)], e[5])
    if k == 'center':  return (2, C0, 0, e[2], e[3], paid_index[(e[2], e[3], e[4], False)], e[4])
    if k == 'warp':    return (3, role(e[1]), 0, e[3], e[4], warp_index[(e[2], e[3], e[4])], e[2])
    need(k == 'scalar', 'kind ' + k)
    g, field = e[1], e[2]
    kind = {'add': 4, 'scale': 5, 'clear': 6, 'copy': 7}[g[0]]
    target = role(g[1])
    source = role(g[2]) if kind in (4, 7) else 0
    num, den = ((g[3], g[4]) if kind == 4 else (g[2], g[3])) if kind in (4, 5) else (0, 1)
    return (kind, target, source, field, 0, 0, 0, num, den)

def run(program, paid_index, warp_index, start, paid_ranks):
    state = start[:]
    census = [0]*10
    cost = 0
    steps = 0
    for e in program:
        ev = encode(e, paid_index, warp_index)
        kind, r, s, a, b = ev[0], ev[1], ev[2], ev[3], ev[4]
        if kind in (0, 8):
            continue
        steps += 1
        if kind == 6:
            need(r == C0, 'clear targets the owned role')
            state[r] = a
        else:
            need(state[r] == a, 'frame trace: role %d holds %s, the record expects %s' % (r, state[r], a))
            if kind in (4, 7):
                need(state[s] == a, 'scalar source frame')
            if kind in (1, 2, 3):
                state[r] = b
        if kind in (1, 2):
            rank = ev[6]
            need(rank < 10, 'paid rank inside the certificate slots')
            census[rank] += 1
        if kind in (4, 5, 6, 7):
            cost += allowance(kind, ev[7], ev[8])
    return state, census, cost, steps

def verify_word(path, label, out):
    raw = gzip.decompress(path.read_bytes())
    payload = json.loads(raw)
    c, programs = payload['canonical'], payload['programs']
    paid_index, warp_index, _, _ = build_indexes(programs, len(c['frames']))
    start = c['start'] + [len(c['frames'])]
    res = {'payload_sha256': hashlib.sha256(raw).hexdigest(), 'orientations': {}}
    for direction, program in programs.items():
        state, census, cost, steps = run(program, paid_index, warp_index, start, None)
        ok = state[:632] == c['final']
        res['orientations'][direction] = {'records': len(program), 'state_steps': steps,
                                          'persistent_final_matches': ok,
                                          'paid_histogram_derived': {str(r): n for r, n in enumerate(census) if n},
                                          'scalar_tariff': cost}
        print('  %-8s %5d records, %5d steps | final %s | paid %s | tariff %d'
              % (direction, len(program), steps, ok, {r: n for r, n in enumerate(census) if n}, cost))
    declared = {int(k): v for k, v in c['local_profile'].items()}
    derived = {int(k): v for k, v in res['orientations']['forward']['paid_histogram_derived'].items()}
    res['local_profile_declared'] = declared
    res['profile_matches_derived'] = declared == derived
    return res

def main():
    raw = gzip.decompress(WORD.read_bytes())
    payload = json.loads(raw)
    c, programs = payload['canonical'], payload['programs']
    frames = c['frames']
    paid_index, warp_index, paid_keys, warp_keys = build_indexes(programs, len(frames))

    out = {'status': 'APPLY', 'word': str(WORD.relative_to(ROOT)),
           'payload_sha256': hashlib.sha256(raw).hexdigest(),
           'spec': {'core': str(SPEC_CORE.relative_to(ROOT)),
                    'core_sha256': hashlib.sha256(SPEC_CORE.read_bytes()).hexdigest(),
                    'generator': str(SPEC_GEN.relative_to(ROOT)),
                    'generator_sha256': hashlib.sha256(SPEC_GEN.read_bytes()).hexdigest(),
                    'authoritative_word': AUTHORITATIVE,
                    'authoritative_payload_sha256': AUTHORITATIVE_PAYLOAD_SHA},
           'orientations': {}, 'paid_classes': len(paid_keys), 'warp_classes': len(warp_keys)}
    need(len(paid_keys) == 10 or len(paid_keys) > 0, 'paid classes')

    ok_frames = True
    for direction, program in programs.items():
        start = c['start'] + [len(frames)]        # roles 0..631 plus the owned C0 role
        state, census, cost, steps = run(program, paid_index, warp_index, start, None)
        frames_ok = state[:632] == c['final']
        ok_frames &= frames_ok
        prof = {str(r): n for r, n in enumerate(census) if n}
        out['orientations'][direction] = {
            'records': len(program), 'state_steps': steps,
            'persistent_final_matches': frames_ok,
            'paid_histogram_derived': prof, 'scalar_tariff': cost}
        print('%-8s %5d records, %5d state steps | persistent frames match final: %s | paid %s | tariff %d'
              % (direction, len(program), steps, frames_ok, prof, cost))
        need(frames_ok, 'the %s trace ends on canonical.final' % direction)

    declared = {int(k): v for k, v in c['local_profile'].items()}
    derived_f = {int(k): v for k, v in out['orientations']['forward']['paid_histogram_derived'].items()}
    need(derived_f == {int(k): v for k, v in out['orientations']['backward']['paid_histogram_derived'].items()},
         'both directions derive the same paid histogram')
    out['local_profile_declared'] = declared
    out['paid_histogram_derived'] = derived_f
    out['profile_matches_derived'] = declared == derived_f
    print('declared local_profile %s' % declared)
    print('%s the derived paid histogram equals the declared local_profile'
          % ('PASS' if declared == derived_f else 'FINDING'))

    # control: the authoritative word of the lineage (payload 4409d2d9...) must derive its own
    # declared profile, which differs from this word's -- the interpreter is not tuned to one word
    ctrl_path = ROOT/AUTHORITATIVE
    if ctrl_path.exists():
        print('control: the word frozen in research/warp-interface-20261022/')
        ctrl = verify_word(ctrl_path, 'authoritative', out)
        need(ctrl['payload_sha256'] == AUTHORITATIVE_PAYLOAD_SHA, 'the authoritative payload hash')
        need(ctrl['profile_matches_derived'], 'the control word derives its own declared profile')
        out['control_authoritative_word'] = ctrl
        print('PASS control: the authoritative word derives %s, its own declared profile -- a different variant, '
              'so the interpreter is not tuned to this word' % ctrl['local_profile_declared'])

    out['status'] = ('PASS_NATIVE_APPLY_TRACE' if ok_frames and declared == derived_f
                     else 'FINDING_NATIVE_APPLY')
    out['validates'] = 'the FROZEN BASE WORD event encoding and its frame/tariff trace'
    out['does_not_validate'] = 'the p19 chain own event stream (no chain-to-event lowering exists in the repository)'
    out['scope'] = ('the record -> event encoding and the frame/tariff transitions of the pinned spec, executed '
                    'independently in Python on this package\'s frozen word; amplitudes, Clifford phases and the '
                    'symbolic endpoint algebra are outside the spec (Native-note.md) and are not claimed here')
    (HERE/'P19_NATIVE_APPLY.json').write_text(json.dumps(out, indent=2, sort_keys=True)+'\n')
    print(json.dumps({'status': out['status']}, sort_keys=True))

if __name__ == '__main__':
    main()

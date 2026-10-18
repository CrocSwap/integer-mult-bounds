#!/usr/bin/env python3
"""Exact finite replay of a one-slot multi-column R439 scatter schedule.

Not an optimum proof.  thakrarsagar with substantial AI assistance from Claude
(Anthropic, Claude Opus 5.5).  Apache-2.0.

The decomposition, export, dirty-boundary and invoice checks are adapted from
Ross Richardson's PR2407 verifier (head 4944211c, Apache-2.0), which in turn
adapts Sricharan Vagvala's PR2356 suffix/interleaving method.  Sagar Thakrar's
PR2115 supplies the deferred split; Charles Bethin's PR2279 the split-ideal
model.  The PR2407 code was generalised from one tapped column to an ordered
list of COPY intervals sharing one private slot.
"""
import argparse
from collections import Counter
import copy
import gzip
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import types

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORD = 'research/r439-bsection-stars-seed01/candidate.json.gz'
EXPORT = 'research/e8-bit-carrier-skeleton/code/bit/export_records.py'
OWNER = 'research/e8-bit-p111-tuned/code/xcheck_p.py'
PROFILE = {1: 1323, 2: 1342, 3: 79, 4: 44, 5: 102, 6: 11, 7: 19}
# PR2407 WITNESS.json (column 0, COPY over the whole deferred undo), restated
# in this package's segment format as a calibration point.
# Record-stream SHA256s published in PR2407 RESULT.json (head 4944211c): the
# rebuilt calibration streams must be byte-identical to them.
PR2407_STREAM_SHA256 = {
    'original': '80bb888427eb8bf158dd4279aa56340d20cf573c296f15632b22afabedf0967d',
    'split94_exported': '94629842826785649565b42bc4f7ab3bee39f617895b09a40aaf9bae028e9d39',
    'split94_segments': '94629842826785649565b42bc4f7ab3bee39f617895b09a40aaf9bae028e9d39',
    'pr2407_88_segments': '856873eac7d6d9d737e83a28c321b6e760ee183d9648bd98e80761b8d4dc9aba'}
PR2407_COL0_TAPS = [[0, 13], [0, 26], [0, 34], [0, 58], [0, 79], [0, 90], [0, 95],
                    [104, 6], [126, 24], [182, 3]]


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def inputs():
    pins = json.loads((HERE/'SOURCES.json').read_text())
    result = {}
    for pin in pins['files']:
        if pin['usage'] != 'input':
            continue
        raw = (ROOT/pin['path']).read_bytes()
        require(sha(raw) == pin['sha256'], 'source SHA256: '+pin['path'])
        require(hashlib.sha1(b'blob %d\0' % len(raw)+raw).hexdigest() == pin['git_blob'], 'source Git blob')
        result[pin['path']] = raw
    require(set(result) == {WORD, EXPORT, OWNER}, 'complete source inventory')
    return result


def split_word(w):
    """PR2115/PR2407 deferred split with kept undo gates {31,51,52}."""
    v = w['v']
    require((v, w['R'], len(w['ret'])) == (111, 439, 9), 'fixed source dimensions')
    target = lambda r: v <= r < 2*v
    yy = lambda g: target(g[1]) and all(target(s) for s in g[2])
    reads = [i for i, g in enumerate(w['D']) if target(g[1]) and all(s >= 2*v for s in g[2])]
    lo, hi = min(reads), max(reads)
    prep = [g for g in w['D'][:lo] if yy(g)]
    positions = [i for i, g in enumerate(w['D']) if i > hi and yy(g)]
    undo = [w['D'][i] for i in positions]
    require(len(prep) == len(undo) == 306 and prep == undo[::-1], 'literal inverse target basis')
    require(not any(yy(g) for g in w['D'][lo:hi+1]), 'target basis and helper reads separated')
    require(all(f == 0 and len(ss) == 1 and d != ss[0] for f, d, ss in prep+undo), 'zero-frame elementary undo')
    moved = set(positions)
    require(all(not target(g[1]) and not any(target(s) for s in g[2])
                for i, g in enumerate(w['D']) if i >= positions[0] and i not in moved), 'D tail isolates targets')
    require(all(not target(g[1]) and not any(target(s) for s in g[2]) for g in w['A']), 'A isolates targets')
    require(all(not target(q) for q in w['ret']), 'retained sources isolated from target undo')
    keep = [31, 51, 52]
    kept = [undo[i] for i in keep]
    rest = [g for i, g in enumerate(undo) if i not in keep]

    def operator(gates):
        rows = [1 << i for i in range(v)]
        for _, d, (s,) in gates:
            rows[d-v] ^= rows[s-v]
        return rows
    require(operator(undo) == operator(kept+rest), 'split changes complete target operator')
    require(all(len(row) == len(set(row)) and all(type(j) is int and 0 <= j < 9 for j in row)
                for row in w['scatter']), 'scatter support')
    S = [sum(1 << j for j in row) for row in w['scatter']]
    P = S.copy()
    for _, d, (s,) in prep+kept:
        P[d-v] ^= P[s-v]
    d = copy.deepcopy(w)
    d['D'] = [g for i, g in enumerate(w['D']) if i not in moved]+kept
    d['B'] = rest+w['B']
    d['scatter'] = [[j for j in range(9) if row >> j & 1] for row in P]
    return d, rest, S, P, len(undo)


def suffix_responses(v, rest):
    """suffix[c][i] = response at the end of the undo to a tap into target i at cut c."""
    cols = [1 << i for i in range(v)]
    suffix = {len(rest): cols.copy()}
    for cut in reversed(range(len(rest))):
        _, d, (s,) = rest[cut]
        cols[s-v] ^= cols[d-v]
        suffix[cut] = cols.copy()
    return suffix


def check_schedule(w, rest, S, segments):
    """Algebraic one-slot schedule check; returns per-column tap counts."""
    v = w['v']
    L = len(rest)
    suffix = suffix_responses(v, rest)
    require(sorted(sg['column'] for sg in segments) == list(range(9)), 'each retained column exactly once')
    prev = 0
    for sg in segments:
        a, b = sg['copy_cut'], sg['erase_cut']
        require(type(a) is int and type(b) is int and 0 <= a <= b <= L, 'interval domain')
        require(prev <= a, 'one live COPY slot: chronological intervals overlap')
        prev = b
        taps = sg['taps']
        require(len(taps) == len({tuple(t) for t in taps}), 'distinct tap locations')
        require(all(len(t) == 2 and all(type(z) is int for z in t) and 0 <= t[1] < v for t in taps), 'tap domain')
        require(all(a <= t[0] <= b for t in taps), 'tap outside its COPY interval')
        j = sg['column']
        wanted = sum(1 << i for i, row in enumerate(S) if row >> j & 1)
        actual = 0
        for cut, i in taps:
            actual ^= suffix[cut][i]
        require(actual == wanted, 'tap response differs from required column')
    return {str(sg['column']): len(sg['taps']) for sg in segments}


def export(w, data, path):
    path.mkdir()
    (path/'word.json').write_text(json.dumps(w))
    (path/'export.py').write_bytes(data[EXPORT])
    subprocess.run([sys.executable, '-I', '-B', str(path/'export.py'), str(path/'word.json'), str(path/'out')],
                   check=True, capture_output=True, timeout=120)
    rec = list(struct.iter_unpack('<6i', (path/'out/249-records.bin').read_bytes()))
    frames = json.loads((path/'out/frames.json').read_text())['frames']
    return rec, frames


def interleave(base, w, rest, segments):
    """Literal record stream: one private slot n, ordered COPY intervals."""
    v = w['v']; n = 2*v+w['R']; L = len(rest)
    start = next(i for i, r in enumerate(base) if r[0] == 2)
    stop = max(i for i, r in enumerate(base) if r[0] == 3)+1
    undo_records = [(1, d, ss[0], 1, 0, 4) for _, d, ss in rest]
    require(base[stop:stop+L] == undo_records, 'deferred undo records at scatter exit')
    require(not any(r[0] == 0 for r in base[start:stop]), 'no MOVE inside the scatter window')
    copies = {r[1]: r for r in base if r[0] == 2}
    erases = {r[1]: r for r in base if r[0] == 3}
    out = []
    cut = 0
    for sg in segments:
        while cut < sg['copy_cut']:
            out.append(undo_records[cut]); cut += 1
        q = w['ret'][sg['column']]
        out.append(copies[q])
        for c in range(sg['copy_cut'], sg['erase_cut']+1):
            out.extend((1, v+i, n, 1, 0, 3) for cc, i in sg['taps'] if cc == c)
            if c < sg['erase_cut']:
                out.append(undo_records[c]); cut = c+1
        out.append(erases[q])
    while cut < L:
        out.append(undo_records[cut]); cut += 1
    return base[:start]+out+base[stop+L:]


def strip(records):
    return [r for r in records if r[0] not in (2, 3) and not (r[0] == 1 and r[5] == 3)]


def boundary(records, w, reverse=False):
    v = w['v']; n = 2*v+w['R']
    rows = [1 << i for i in range(n)]+[0]
    live = None
    for op, a, b, c, frame, phase in (reversed(records) if reverse else records):
        if reverse and op in (2, 3):
            op = 5-op
        if op == 0:
            continue
        if op == 1:
            require(c == 1 and 0 <= a < n and 0 <= b <= n and a != b, 'ADD domain')
            rows[a] ^= rows[b]
        elif op == 2:
            require(live is None and b == n and rows[b] == 0, 'COPY occupied slot')
            rows[b] = rows[a]; live = (a, b)
        elif op == 3:
            require(live == (a, b) and rows[a] == rows[b], 'ERASE snapshot changed')
            rows[b] = 0; live = None
        else:
            raise ValueError('unknown opcode')
    expected = [(1 << i) ^ (1 << (i-v)) if v <= i < 2*v else 1 << i for i in range(n)]
    require(live is None and rows[-1] == 0, 'unrestored private slot')
    require(rows[:-1] == expected, 'all-input dirty boundary')


def invoice(records, w, frames):
    n = 2*w['v']+w['R']; cur = w['start'].copy()+[0]
    dim = {int(k): f['dim'] for k, f in frames.items()}
    labels = [set(f) for f in w['frames']]
    profile = Counter(); live = None; live_count = 0; peak_live = 0  # peak is measured, not asserted
    for op, a, b, c, f, phase in records:
        if op == 0:
            require(a < n and cur[a] == b and labels[b] < labels[c] and f == dim[c]-dim[b], 'MOVE frame path')
            cur[a] = c; profile[f] += 1
        elif op == 1:
            require(cur[a] == cur[b] == f and c == 1, 'ADD frame access')
        elif op == 2:
            require(live is None and b == n and cur[a] == c and f == 0 and phase == dim[c], 'COPY frame/lifetime')
            cur[b] = f; live = (a, b); profile[phase] += 1
            live_count += 1; peak_live = max(peak_live, live_count)
        elif op == 3:
            require(live == (a, b) and cur[a] == c and cur[b] == f == 0 and phase == 0, 'ERASE frame/lifetime')
            live = None; live_count -= 1
        else:
            raise ValueError('invoice opcode')
    require(live is None and cur[:n] == w['final'], 'final frame state')
    require(dict(profile) == PROFILE, 'paid profile changed')
    bounds = []
    for reverse in (False, True):
        mass = [1]*n+[0]; peak = 1
        for op, a, b, c, _, _ in (reversed(records) if reverse else records):
            if reverse and op in (2, 3):
                op = 5-op
            if op == 1:
                mass[a] += abs(c)*mass[b]; peak = max(peak, mass[a])
            elif op == 2:
                mass[b] = mass[a]
            elif op == 3:
                mass[b] = 0
        bounds.append(peak)
    F, B = bounds; local = 64*F**3*B**2; nine = (1 << 18)*F**5*B**4
    require(local < 1 << 104 and nine < 1 << 192, 'inherited precision guard')
    count = Counter(r[0] for r in records)
    require(count[2] == count[3] == 9, 'nine COPY/ERASE pairs')
    return {'ADDs': count[1], 'scatter_ADDs': sum(r[0] == 1 and r[5] == 3 for r in records),
            'phase4_ADDs': sum(r[0] == 1 and r[5] == 4 for r in records),
            'MOVEs': count[0], 'COPYs': count[2], 'ERASEs': count[3],
            'COPY_rank_sum': sum(r[5] for r in records if r[0] == 2),
            'peak_live_copy_slots': peak_live, 'paid_profile': {str(k): v for k, v in sorted(profile.items())},
            'paid_rank_mass': sum(k*v for k, v in profile.items()), 'F': F, 'B': B,
            'local_bits': local.bit_length(), 'nine_stage_bits': nine.bit_length(),
            'record_sha256': sha(b''.join(struct.pack('<6i', *r) for r in records))}


def rejects(label, fn, fragment):
    try:
        fn()
    except ValueError as exc:
        require(fragment in str(exc), label+' wrong rejection: '+str(exc))
        return label
    raise ValueError('control accepted: '+label)


def split_segments(P, order=range(9)):
    return [{'column': j, 'copy_cut': 0, 'erase_cut': 0,
             'taps': [[0, i] for i, row in enumerate(P) if row >> j & 1]} for j in order]


def run(output=None):
    data = inputs(); w = json.loads(gzip.decompress(data[WORD]))
    witness = json.loads((HERE/'WITNESS.json').read_text())
    require(witness.get('order') == 'ideal303' and witness.get('keep_undo_indices') == [31, 51, 52], 'fixed split')
    require(witness.get('optimality_claim') is False, 'no optimality claim')
    segments = witness['segments']
    split, rest, S, P, nundo = split_word(w)
    owner = types.ModuleType('pinned_owner'); exec(compile(data[OWNER], OWNER, 'exec'), owner.__dict__)
    h, c, _ = owner.Word(w).interface(); flags = sorted(k for k, v in {**h, **c}.items() if not v)
    require(flags == ['H2_D_frame0_targets_from_helpers', 'K_equals_D'], 'original interface flags')
    # Calibrations: PR2115 split (all columns at cut 0) and PR2407 column-0 stream.
    split_sched = split_segments(P)
    pr2407 = split_segments(P, range(1, 9))+[{'column': 0, 'copy_cut': 0, 'erase_cut': len(rest),
                                               'taps': copy.deepcopy(PR2407_COL0_TAPS)}]
    per_column = check_schedule(w, rest, S, segments)
    # Second, independently discovered 84 schedule: the DP output that the
    # packaged search/search.py produced for both recorded seeds (SEARCH.json).
    # Accepting it here makes the 84 result regenerable from packaged code.
    runs = json.loads((HERE/'SEARCH.json').read_text())['runs']
    alt = runs[0]['dp_schedule_segments']
    require(all(r['dp_schedule_segments'] == alt for r in runs), 'search runs disagree on DP schedule')
    require(alt != segments, 'search DP schedule is a distinct presentation')
    check_schedule(w, rest, S, alt)
    check_schedule(w, rest, S, split_sched); check_schedule(w, rest, S, pr2407)
    nontrivial = sum(sg['copy_cut'] < sg['erase_cut'] for sg in segments)
    with tempfile.TemporaryDirectory(prefix='r439-one-slot-multicol-') as tmp:
        tmp = Path(tmp)
        original, frames = export(w, data, tmp/'original')
        fixed, _ = export(split, data, tmp/'split')
        streams = [('original', original), ('split94_exported', fixed),
                   ('split94_segments', interleave(fixed, w, rest, split_sched)),
                   ('pr2407_88_segments', interleave(fixed, w, rest, pr2407)),
                   ('candidate', interleave(fixed, w, rest, segments)),
                   ('search_dp_alternative', interleave(fixed, w, rest, alt))]
        reports = {}
        for name, records in streams:
            boundary(records, w); boundary(records, w, True)
            reports[name] = invoice(records, w, frames)
            require([r for r in records if r[0] == 0] == [r for r in original if r[0] == 0], 'ordered MOVEs unchanged')
        for name, digest in PR2407_STREAM_SHA256.items():
            require(reports[name]['record_sha256'] == digest, name+': not byte-identical to PR2407 receipt')
        cand = dict(streams)['candidate']
        require(reports['split94_exported']['scatter_ADDs'] == reports['split94_segments']['scatter_ADDs'] == 94,
                'known split calibration')
        require(sorted(dict(streams)['split94_exported']) == sorted(dict(streams)['split94_segments']),
                'segment builder reproduces exported split records (as a multiset)')
        require(reports['pr2407_88_segments']['scatter_ADDs'] == 88 and reports['pr2407_88_segments']['ADDs'] == 11061,
                'PR2407 calibration')
        require(reports['candidate']['scatter_ADDs'] == witness['expected_scatter_adds'], 'claimed scatter ADDs')
        require(reports['candidate']['ADDs'] == witness['expected_total_adds'], 'claimed complete ADDs')
        require(len(rest) == 303, 'deferred undo length')
        require(reports['search_dp_alternative']['scatter_ADDs'] == witness['expected_scatter_adds']
                and reports['search_dp_alternative']['ADDs'] == witness['expected_total_adds'], 'search DP alternative')
        for name in ('split94_segments', 'pr2407_88_segments', 'candidate', 'search_dp_alternative'):
            # Deleting scatter taps and COPY/ERASE records from the exported split
            # and from the rebuilt stream must give the identical ordered stream:
            # every one of the 303 deferred undo gates and every other record is
            # kept, in order; only the nine COPY/ERASE pairs and taps moved.
            require(strip(dict(streams)[name]) == strip(fixed), name+': non-scatter record stream changed')
            require(sorted(r for r in dict(streams)[name] if r[0] in (2, 3)) == sorted(r for r in fixed if r[0] in (2, 3)),
                    name+': COPY/ERASE multiset changed')

        controls = []

        def seg_mut(fn):
            bad = copy.deepcopy(segments); fn(bad); return bad
        # algebra-level controls
        long_ = [k for k, sg in enumerate(segments) if sg['copy_cut'] < sg['erase_cut']]
        require(len(long_) >= 2, 'at least two interleaved columns')
        k0, k1 = long_[0], long_[1]
        bad = seg_mut(lambda s: s[k1].__setitem__('copy_cut', s[k0]['erase_cut']-1))
        controls.append(rejects('overlapping COPY intervals', lambda: check_schedule(w, rest, S, bad), 'intervals overlap'))

        kl = long_[-1]

        def wrongcut(s):
            # latest tap of the last interleaved column moved to its COPY cut
            sg = s[kl]; t = max(sg['taps']); require([sg['copy_cut'], t[1]] not in sg['taps'], 'fresh cut')
            t[0] = sg['copy_cut']
        controls.append(rejects('wrong cut', lambda: check_schedule(w, rest, S, seg_mut(wrongcut)), 'tap response'))
        controls.append(rejects('dropped tap', lambda: check_schedule(w, rest, S, seg_mut(lambda s: s[k1]['taps'].pop())),
                                'tap response'))

        def swap(s):
            s[k0]['column'], s[k1]['column'] = s[k1]['column'], s[k0]['column']
        controls.append(rejects('swapped columns', lambda: check_schedule(w, rest, S, seg_mut(swap)), 'tap response'))

        def outside(s):
            sg = s[k0]; t = max(sg['taps']); t[0] = sg['erase_cut']+1
        controls.append(rejects('tap outside interval', lambda: check_schedule(w, rest, S, seg_mut(outside)), 'outside'))
        # stream-level controls, bypassing the algebraic check
        controls.append(rejects('swapped columns (literal replay)',
                                lambda: boundary(interleave(fixed, w, rest, seg_mut(swap)), w), 'dirty boundary'))
        controls.append(rejects('dropped tap (literal replay)',
                                lambda: boundary(interleave(fixed, w, rest, seg_mut(lambda s: s[k1]['taps'].pop())), w),
                                'dirty boundary'))
        controls.append(rejects('wrong cut (literal replay)',
                                lambda: boundary(interleave(fixed, w, rest, seg_mut(wrongcut)), w), 'dirty boundary'))
        copies = [i for i, r in enumerate(cand) if r[0] == 2]
        erases = [i for i, r in enumerate(cand) if r[0] == 3]
        # overlapping literal lifetimes: issue the second interleaved COPY before the first one's ERASE
        q1 = w['ret'][segments[k1]['column']]
        ci = next(i for i in copies if cand[i][1] == q1)
        e0 = next(i for i in erases if cand[i][1] == w['ret'][segments[k0]['column']])
        require(e0 < ci, 'chronological literal lifetimes')
        badrec = cand[:e0]+[cand[ci]]+[r for i, r in enumerate(cand[e0:], e0) if i != ci]
        controls.append(rejects('overlapping literal COPY lifetimes', lambda: boundary(badrec, w), 'occupied slot'))
        undoidx = next(i for i in range(ci, len(cand)) if cand[i][0] == 1 and cand[i][5] == 4)
        badrec = cand[:undoidx]+cand[undoidx+1:]
        controls.append(rejects('missing paid undo gate', lambda: boundary(badrec, w), 'dirty boundary'))
        e1 = next(i for i in erases if i > ci)
        badrec = cand[:ci+1]+[cand[e1]]+cand[ci+1:e1]+cand[e1+1:]
        controls.append(rejects('premature ERASE', lambda: boundary(badrec, w), 'dirty boundary'))
        badrec = cand.copy(); r = list(badrec[ci+1]); require(r[0] == 1 and r[5] == 3, 'tap after COPY'); r[4] = 1
        badrec[ci+1] = tuple(r)
        controls.append(rejects('wrong tap frame', lambda: invoice(badrec, w, frames), 'frame access'))
        badrec = cand.copy(); r = list(badrec[ci]); r[5] -= 1; badrec[ci] = tuple(r)
        controls.append(rejects('underpriced COPY', lambda: invoice(badrec, w, frames), 'COPY frame'))
        # accepted equivalent presentation: reversed tap lists inside each segment
        eq = seg_mut(lambda s: [sg.__setitem__('taps', list(reversed(sg['taps']))) for sg in s])
        check_schedule(w, rest, S, eq)
        eqr = interleave(fixed, w, rest, eq); boundary(eqr, w); boundary(eqr, w, True)
        require(invoice(eqr, w, frames)['ADDs'] == witness['expected_total_adds'], 'equivalent presentation')
        report = {'status': 'PASS_R439_ONE_SLOT_MULTICOLUMN', 'dirty_columns': 661, 'orientations': 2,
                  'undo_gates': nundo, 'deferred_gates': len(rest), 'kept_gates': 3,
                  'per_column_taps': per_column, 'interleaved_columns': nontrivial,
                  'schedules': reports, 'controls': controls, 'equivalent_tap_order_passes': True,
                  'source_interface_false': flags, 'new_kappa_claim': False, 'optimality_claim': False}
        if output is not None:
            output.mkdir(parents=True, exist_ok=False)
            (output/'records.bin').write_bytes(b''.join(struct.pack('<6i', *r) for r in cand))
            (output/'frames.json').write_text(json.dumps(frames, sort_keys=True)+'\n')
            (output/'RESULT.json').write_text(json.dumps(report, indent=2)+'\n')
        return report


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--write', action='store_true'); ap.add_argument('--output', type=Path)
    args = ap.parse_args(); report = run(args.output)
    if args.write:
        (HERE/'RESULT.json').write_text(json.dumps(report, indent=2)+'\n')
    else:
        require(report == json.loads((HERE/'RESULT.json').read_text()), 'fixed result receipt mismatch')
    c = report['schedules']['candidate']
    print('PASS_R439_ONE_SLOT_MULTICOLUMN scatter=94->88->%d ADDs=11067->11061->%d interleaved_columns=%d '
          'dirty_columns=661 controls=%d no_new_kappa no_optimality_claim'
          % (c['scatter_ADDs'], c['ADDs'], report['interleaved_columns'], len(report['controls'])))


if __name__ == '__main__':
    main()

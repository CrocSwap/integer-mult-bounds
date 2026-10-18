#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Prepared by Sagar Thakrar with substantial Anthropic Claude assistance.
"""Exact finite verification of the phase-B / helper-star composition.

Rebuilds both words deterministically and compares them with the committed payloads. Then:
* every spliced block has the original block's F2 map, checked on all 2^n inputs, on its own
  registers and frame (integer-transfer equality is recorded, not required);
* each word differs from PR589 only in B, C and D. C equals the literal cleanup of A + B. Every
  register's ordered frame path equals PR589's;
* all 661 formal columns are replayed through the literal COPY/ERASE stream in both directions
  (set-valued F2), and the D-section dirty boundary equals PR589's;
* the pinned owner checker (xcheck_p.py) gives the same H1-H5/conclusion pattern as the
  incorporated helper-star word, with paid profile and rank mass unchanged;
* the pinned exporter bills ADD/COPY/ERASE records and record-level positive bounds;
* both inherited precision guards (local 104-bit, nine-stage 192-bit) hold on the literal-stream
  bounds;
* eight negative controls are rejected.
Checks raise ValueError (no assert), so -O does not weaken them; the owner checker is re-run
in a child process without -O.
"""
import argparse, copy, gzip, hashlib, importlib.util, itertools, json, runpy, struct, subprocess, sys, tempfile
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
Bd = runpy.run_path(str(HERE / 'build.py'))
need, load, digest, canonical = Bd['need'], Bd['load'], Bd['digest'], Bd['canonical']
BLOCKS, cleanup, splice = Bd['BLOCKS'], Bd['cleanup'], Bd['splice']
WORD = 'research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz'
CHECKER = 'research/e8-bit-p111-tuned/code/xcheck_p.py'
EXPORTER = 'research/e8-bit-carrier-skeleton/code/bit/export_records.py'
PROFILE = {1: 1323, 2: 1342, 3: 79, 4: 44, 5: 102, 6: 11, 7: 19}


# ------------------------------------------------------------------ blocks

def block_check(original, frame, gates):
    a, b = BLOCKS[frame]
    old = original['B'][a:b]
    need(all(f == frame and len(ss) == 1 for f, _, ss in old), 'original block shape %d' % frame)
    regs = sorted({d for _, d, _ in old} | {ss[0] for _, _, ss in old})
    idx = {r: i for i, r in enumerate(regs)}
    need(all(f == frame and d in idx and len(ss) == 1 and ss[0] in idx and ss[0] != d for f, d, ss in gates),
         'replacement block shape %d' % frame)
    need(len(gates) < len(old), 'replacement not shorter %d' % frame)
    o = [(idx[d], idx[ss[0]]) for _, d, ss in old]
    m = [(idx[d], idx[ss[0]]) for _, d, ss in gates]
    n = len(regs)
    for val in range(1 << n):
        x = [(val >> i) & 1 for i in range(n)]
        y = list(x)
        for d, s in o:
            x[d] ^= x[s]
        for d, s in m:
            y[d] ^= y[s]
        need(x == y, 'F2 block map %d' % frame)

    def transfer(ops):
        cols = []
        for c in range(n):
            v = [int(i == c) for i in range(n)]
            for d, s in ops:
                v[d] += v[s]
            cols.append(v)
        return cols
    return dict(frame=frame, registers=n, original_gates=len(old), new_gates=len(gates),
                boolean_inputs=1 << n, integer_transfer_equal=transfer(o) == transfer(m),
                reverse_transfer_total=[sum(map(sum, transfer(o[::-1]))), sum(map(sum, transfer(m[::-1])))])


# ------------------------------------------------------------------ words

def stream(w):
    out = [('add', d, s) for sec in ('D', 'A') for _, d, ss in w[sec] for s in ss]
    tmp = 2 * w['v'] + w['R']
    for j, centre in enumerate(w['ret']):
        out.append(('copy', tmp, centre))
        out += [('add', w['v'] + i, tmp) for i, ss in enumerate(w['scatter']) if j in ss]
        out.append(('erase', tmp, centre))
    out += [('add', d, s) for sec in ('B', 'C') for _, d, ss in w[sec] for s in ss]
    return out


def flip(kind):
    return {'copy': 'erase', 'erase': 'copy'}.get(kind, kind)


def literal_rows(w, reverse=False):
    n = 2 * w['v'] + w['R']
    rows = [{i} for i in range(n)] + [set()]
    ins = stream(w)
    for kind, d, s in (reversed(ins) if reverse else ins):
        kind = flip(kind) if reverse else kind
        if kind == 'add':
            rows[d] ^= rows[s]
        elif kind == 'copy':
            need(not rows[d], 'copy into a live temporary')
            rows[d] = set(rows[s])
        else:
            need(rows[d] == rows[s], 'erase of a changed copy')
            rows[d] = set()
    need(not rows[-1], 'temporary not erased')
    return rows[:-1]


def literal_bounds(w):
    peaks = []
    for reverse in (False, True):
        val = [1] * (2 * w['v'] + w['R'] + 1)
        peak = 1
        ins = stream(w)
        for kind, d, s in (reversed(ins) if reverse else ins):
            kind = flip(kind) if reverse else kind
            val[d] = val[d] + val[s] if kind == 'add' else (val[s] if kind == 'copy' else 0)
            peak = max(peak, val[d])
        peaks.append(peak)
    F, B = peaks
    return dict(native_ADDs=sum(k == 'add' for k, _, _ in stream(w)), D_adds=sum(len(g[2]) for g in w['D']),
                F=F, B=B, local_bits=(64 * F**3 * B**2).bit_length(), nine_stage_bits=((1 << 18) * F**5 * B**4).bit_length())


def guard(bill):
    need(bill['local_bits'] <= 104, 'local precision guard')
    need(bill['nine_stage_bits'] <= 192, 'nine-stage precision guard')


def d_rows(w):
    rows = [{i} for i in range(2 * w['v'] + w['R'])]
    for f, d, ss in w['D']:
        need(f == 0 and w['v'] <= d, 'D shape')
        for s in ss:
            rows[d] ^= rows[s]
    return rows


def frame_paths(w):
    fs = [frozenset(f) for f in w['frames']]
    ps = [[f] for f in w['start']]
    for sec in 'DABC':
        for f, d, ss in w[sec]:
            for r in (d, *ss):
                if ps[r][-1] != f:
                    need(fs[ps[r][-1]] < fs[f], 'illegal frame move')
                    ps[r].append(f)
    for r, f in enumerate(w['final']):
        if ps[r][-1] != f:
            need(fs[ps[r][-1]] < fs[f], 'illegal final move')
            ps[r].append(f)
    return ps


def exporter(w, out):
    out.mkdir(parents=True)
    (out / 'word.json.gz').write_bytes(gzip.compress(canonical(w), mtime=0))
    subprocess.run([sys.executable, '-I', '-B', str(ROOT / EXPORTER), str(out / 'word.json.gz'), str(out / 'rec')],
                   check=True, capture_output=True, text=True)
    raw = (out / 'rec/249-records.bin').read_bytes()
    need(len(raw) % 24 == 0, 'record alignment')
    rec = list(struct.iter_unpack('<6i', raw))
    bounds = []
    for reverse in (False, True):
        norm, peak, open_ = [1] * (2 * w['v'] + w['R'] + 1), 1, False
        for op, a, b, c, _, _ in (reversed(rec) if reverse else rec):
            if op == 0:
                continue
            if reverse and op in (2, 3):
                op = 5 - op
            if op == 1:
                norm[a] += abs(c) * norm[b]
                peak = max(peak, norm[a])
            elif op == 2:
                need(not open_, 'nested copy')
                norm[b], open_ = norm[a], True
            elif op == 3:
                need(open_, 'erase without copy')
                norm[b], open_ = 0, False
            else:
                raise ValueError('record opcode')
        need(not open_, 'unclosed copy')
        bounds.append(peak)
    payload = 64 * bounds[0]**3 * bounds[1]**2
    need(payload < 1 << 104, 'exporter payload cap')
    return dict(adds=sum(x[0] == 1 for x in rec), copies=sum(x[0] == 2 for x in rec),
                erasures=sum(x[0] == 3 for x in rec), forward=bounds[0], reverse=bounds[1],
                payload_bits=payload.bit_length(), record_sha256=hashlib.sha256(raw).hexdigest())


def owner(w):
    spec = importlib.util.spec_from_file_location('r439_owner', ROOT / CHECKER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    dim, labels, flow, hyp, con, _ = mod.check(w)
    prof = Counter(dim.fdim[b] - dim.fdim[a] for p in frame_paths(w) for a, b in itertools.pairwise(p))
    prof.update(t['rank'] for t in flow['totals'])
    return dict(hypotheses=hyp, conclusions=con, profile={k: prof[k] for k in sorted(prof)},
                copy_ranks=[t['rank'] for t in flow['totals']])


def word_checks(name, w, original, reference_owner, work):
    for k in original:
        if k not in ('B', 'C', 'D'):
            need(w[k] == original[k], '%s field %s changed' % (name, k))
    need(w['C'] == cleanup(w), name + ' literal cleanup')
    need(frame_paths(w) == frame_paths(original), name + ' register frame paths')
    want = [{i, i - w['v']} if w['v'] <= i < 2 * w['v'] else {i} for i in range(2 * w['v'] + w['R'])]
    for reverse in (False, True):
        need(literal_rows(w, reverse) == want, '%s complete boundary (%s)' % (name, 'reverse' if reverse else 'forward'))
    need(d_rows(w) == d_rows(original), name + ' D dirty boundary')
    own = owner(w)
    need({k: own[k] for k in ('hypotheses', 'conclusions')} == reference_owner, name + ' owner pattern')
    need(own['profile'] == PROFILE and sum(r * c for r, c in own['profile'].items()) == 5129, name + ' paid profile')
    bill = literal_bounds(w)
    guard(bill)
    ex = exporter(w, work / name)
    need(ex['adds'] == bill['native_ADDs'] and ex['copies'] == ex['erasures'] == 9, name + ' exporter bill')
    return dict(literal=bill, exporter=ex, copy_ranks=own['copy_ranks'], columns=len(want), directions=2)


# ------------------------------------------------------------------ controls

def controls(original, hs, words, progs, work):
    out = []

    def reject(label, fn):
        try:
            fn()
        except ValueError as e:
            out.append([label, str(e)[:60]])
            return
        raise ValueError('negative control accepted: ' + label)
    f0 = 506
    g = copy.deepcopy(progs[f0]['gates'])
    regs = sorted({d for _, d, _ in original['B'][BLOCKS[f0][0]:BLOCKS[f0][1]]})
    g[0][2] = [next(r for r in regs if r not in (g[0][1], g[0][2][0]))]
    reject('mutated block source', lambda: block_check(original, f0, g))
    reject('dropped block gate', lambda: block_check(original, 507, progs[507]['gates'][:-1]))
    bad = copy.deepcopy(words['composition'])
    bad['B'][BLOCKS[519][0]][0] = 0
    reject('block gate at frame zero', lambda: frame_paths(bad))
    # The old cleanup inverts the same F2 block maps, so it is exact but not the literal cleanup;
    # its extra ADDs are why the inherited literal-cleanup rule, not the endpoint, rejects it.
    stale = copy.deepcopy(words['composition'])
    stale['C'] = hs['C']
    need(literal_rows(stale) == literal_rows(words['composition']), 'stale-cleanup premise')
    need(literal_bounds(stale)['native_ADDs'] > literal_bounds(words['composition'])['native_ADDs'], 'stale-cleanup cost')
    reject('stale cleanup', lambda: need(stale['C'] == cleanup(stale), 'literal cleanup rule'))
    bad = copy.deepcopy(words['composition'])
    bad['C'].pop()
    reject('omitted cleanup gate', lambda: need(literal_rows(bad) == literal_rows(words['composition']), 'boundary'))
    unspliced = copy.deepcopy(original)
    unspliced['D'] = words['candidate']['D']
    reject('new stars without the spliced blocks', lambda: guard(literal_bounds(unspliced)))
    bad = copy.deepcopy(words['candidate'])
    bad['D'].pop()
    reject('omitted star restoration', lambda: need(d_rows(bad) == d_rows(original), 'D boundary'))
    reject('guard equality is not strict', lambda: guard(dict(local_bits=105, nine_stage_bits=1)))
    return out


# ------------------------------------------------------------------ driver

def run(work, check_expected=True):
    manifest = Bd['pins'](ROOT)
    built = Bd['build'](ROOT)
    for name in ('composition', 'candidate', 'pair_control'):
        need(canonical(load(HERE / (name + '.json.gz'))) == canonical(built[name]), 'committed payload ' + name)
    for name in ('candidate_search', 'pair_control_search'):
        need(load(HERE / (name + '.json')) == built[name], 'committed search receipt ' + name)
    original = load(ROOT / WORD)
    hs = load(ROOT / 'research/r439-helper-stars-seed19/candidate.json.gz')
    progs = Bd['programs'](ROOT)
    blocks = [block_check(original, f, progs[f]['gates']) | dict(source=progs[f]['source']) for f in sorted(BLOCKS, key=lambda f: BLOCKS[f][0])]
    ref = owner(hs)
    reference = {k: ref[k] for k in ('hypotheses', 'conclusions')}
    need([k for k, v in reference['hypotheses'].items() if not v] == ['H2_D_frame0_targets_from_helpers']
         and [k for k, v in reference['conclusions'].items() if not v] == ['K_equals_D'], 'helper-star reference pattern')
    need(built['composition']['D'] == hs['D'], 'composition keeps the helper-star D')
    words = dict(helper_star=hs, composition=built['composition'], candidate=built['candidate'], pair_control=built['pair_control'])
    checks = {name: word_checks(name, w, original, reference, work) for name, w in words.items()}
    need(checks['helper_star']['literal']['native_ADDs'] == 11783, 'helper-star bill')
    stars = runpy.run_path(str(ROOT / 'research/r439-helper-stars-seed19/build.py'))
    _, original_search = stars['search'](load(ROOT / 'research/r439-target-compensation/candidate.json.gz'), 2)
    need(original_search['native_ADDs'] == 11783, 'original search reproduces 11,783')
    cs = built['candidate_search']
    report = dict(
        status='PASS_R439_BSECTION_STARS', base_commit=manifest['base_commit'], assignment_seed=1,
        blocks=blocks, block_gates=[sum(b['original_gates'] for b in blocks), sum(b['new_gates'] for b in blocks)],
        words=checks,
        search=dict(original=dict(edges=original_search['helper_edges'], guard_rejections=len(original_search['guard_rejections']),
                                  D_adds=original_search['D_adds'], ADDs=original_search['native_ADDs']),
                    spliced=dict(edges=cs['helper_edges'], guard_rejections=len(cs['guard_rejections']),
                                 D_adds=cs['D_adds'], ADDs=cs['native_ADDs'], two_leaf_stars=cs['two_leaf_stars']),
                    pair_control_ADDs=built['pair_control_search']['native_ADDs']),
        owner_reference=reference, controls=controls(original, hs, words, progs, work),
        payload_sha256={k: digest(built[k]) for k in ('composition', 'candidate', 'pair_control')},
        new_kappa_claim=False)
    if check_expected:
        need(load(HERE / 'CERTIFICATE.json') == json.loads(json.dumps(report)), 'certificate mismatch')
    return report


if __name__ == '__main__':
    if not __debug__:   # the inherited owner checker uses assertions
        raise SystemExit(subprocess.call([sys.executable, '-I', '-B', __file__, *sys.argv[1:]]))
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--write-certificate', action='store_true')
    a = ap.parse_args()
    with tempfile.TemporaryDirectory(prefix='r439-bstars-') as tmp:
        rep = run(Path(tmp), check_expected=not a.write_certificate)
    if a.write_certificate:
        (HERE / 'CERTIFICATE.json').write_text(json.dumps(rep, indent=1) + '\n')
    w = rep['words']
    print('PASS_R439_BSECTION_STARS blocks=%d gates=%d->%d ADDs=%d->%d->%d guard_rejections=%d->%d columns=%d controls=%d no_new_kappa' % (
        len(rep['blocks']), *rep['block_gates'], w['helper_star']['literal']['native_ADDs'],
        w['composition']['literal']['native_ADDs'], w['candidate']['literal']['native_ADDs'],
        rep['search']['original']['guard_rejections'], rep['search']['spliced']['guard_rejections'],
        w['candidate']['columns'], len(rep['controls'])))

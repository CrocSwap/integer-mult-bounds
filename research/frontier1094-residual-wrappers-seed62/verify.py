#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Supplier-boundary audit: the selected frontier1094 word's 36 residual wrappers are exact (no new kappa).

Usage: python3 -I -B research/frontier1094-residual-wrappers-seed62/verify.py [--write]

Lemma A's exact part needs, for every helper that enters at a nonzero frame E or ends below FULL at U, a stored wrapper
(L, R) with L o (C_[w] (x) I) o R = T_end o T_E^-1, w = dim end - dim E (end = FULL, or U for a hyperplane end). For the
selected gauge44 provider these 36 records live in RESIDUAL-ADAPTERS.json. The selected chain's own audit
(gauge44-slots-t16/code/audit_allcold.py) checks only their structural fields; their exactness rests on the producer's
WRAPPER-CHECKS.json, which the owner audit does not pin. This script:

  B  binds the records: the merged #1781 binding (selected record -> frontier1094 certificate -> capsule -> owner audit
     -> gauge44 word and programs), then RESIDUAL-ADAPTERS.json against the owner audit's own digest; the split-centres
     decoy is rejected by digest and the global8 twin is byte-identical (informational);
  I  inventory: the 36 keys are exactly the word's entering / hyperplane-ending helpers' (start) and (start:final);
     every record's frames, vectors and ranks match the word; every monomial is well formed; in both programs every
     wrapped helper has one pre and one post residual event, with the right key;
  FX calibrates the new closed-form kernel B (closed_form.py) on #702's 14 frame kernels and #1415's three operator
     digests, and checks that records 2:999 and 3:998 are Exact.lean's pair 3 and pair 2;
  E  evaluates all 36 identities L o F_w o R o T_E = T_end exactly on all 512 columns, global phase included, with
     kernel B (closed-form sparse amplitudes) and kernel A (#1781's packed evaluator); both must pass;
  C  semantic controls: each mutation is rejected on every record it applies to.

Expected last line: PASS_FRONTIER1094_RESIDUAL_WRAPPERS_EXACT
"""
import argparse
import copy
import gzip
import hashlib
import io
import json
import sys
import tarfile
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
P1781 = ROOT / 'research/frontier1094-recipes-exact-seed76'
sys.path.insert(0, str(HERE))
import closed_form as B  # noqa: E402

PREFIX = 'candidate/strict/'
MEMBERS = dict(adapters='global/base/providers/gauge44/RESIDUAL-ADAPTERS.json',
               checks='global/base/providers/gauge44/WRAPPER-CHECKS.json',
               decoy='global/base/split-centres/RESIDUAL-ADAPTERS.json',
               twin='global8/base/providers/gauge44/RESIDUAL-ADAPTERS.json',
               audit='global/audit/OWNERS-AND-PROFILE.json',
               invoice='global/audit/PREFIX-AND-INVOICE.json')
ARTIFACT = 'providers/gauge44/RESIDUAL-ADAPTERS.json'


class Reject(Exception):
    """A check failed; the argument is the label of the check."""


def need(ok, label):
    if not ok:
        raise Reject(label)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def load_1781():
    """import the merged #1781 package (binding helpers and kernel A) after checking its pinned digests."""
    pins = {f['path']: f['sha256'] for f in json.loads((HERE / 'SOURCES.json').read_text())['files']}
    for name in ('verify.py', 'clifford.py', 'CASES.json'):
        rel = 'research/frontier1094-recipes-exact-seed76/' + name
        need(sha((ROOT / rel).read_bytes()) == pins[rel], 'B #1781 file pinned: ' + name)
    import importlib.util
    sys.path.insert(0, str(P1781))
    import clifford as A
    spec = importlib.util.spec_from_file_location('verify_1781', P1781 / 'verify.py')   # unique name: no clash with this file
    R = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(R)
    return R, A


def bind(R, archive_bytes=None, member_overrides=None):
    data, binding = R.load()
    arc = R.CASES['archive']
    raw = archive_bytes if archive_bytes is not None else (ROOT / arc['path']).read_bytes()
    need(sha(raw) == arc['sha256'], 'B1 archive digest')
    members = dict(MEMBERS, **(member_overrides or {}))
    with tarfile.open(fileobj=io.BytesIO(raw), mode='r:gz') as tar:
        index = R.safe_members(tar)
        got = {k: tar.extractfile(index[PREFIX + p]).read() for k, p in members.items()}
    audit = R.strict_loads(got['audit'])
    need(audit['source_artifacts'][ARTIFACT] == sha(got['adapters']), 'B residual adapters pinned by the owner audit')
    need(sha(got['decoy']) != audit['source_artifacts'][ARTIFACT], 'B the split-centres decoy differs by digest')
    # the certificate's fresh invoice pins every provider file's bytes, WRAPPER-CHECKS.json included
    asm = R.strict_loads((ROOT / R.CASES['certificate']).read_bytes())
    need(sha(got['invoice']) == asm['input_sha256']['fresh_invoice'], 'B fresh invoice bound by the certificate')
    inv_art = R.strict_loads(got['invoice'])['providers']['gauge44']['artifacts']
    need(inv_art['RESIDUAL-ADAPTERS.json'] == sha(got['adapters']), 'B residual adapters pinned by the fresh invoice')
    need(inv_art['WRAPPER-CHECKS.json'] == sha(got['checks']), 'B wrapper checks pinned by the fresh invoice')
    adapters = R.strict_loads(got['adapters'])
    checks = R.strict_loads(got['checks'])
    binding.update(residual_adapters_sha256=sha(got['adapters']), wrapper_checks_sha256=sha(got['checks']),
                   wrapper_checks_pinned_by='certificate input_sha256.fresh_invoice -> PREFIX-AND-INVOICE providers.gauge44.artifacts '
                                            '(bytes only; no chain code checks its status or content)',
                   wrapper_checks_in_owner_audit=any(k.endswith('WRAPPER-CHECKS.json') for k in audit['source_artifacts']),
                   global8_twin_byte_identical=got['twin'] == got['adapters'])
    return data, adapters, checks, binding


def end_of(key):
    if ':' in key:
        e, u = key.split(':')
        return int(e), int(u)
    return int(key), 1


def inventory(A, word, programs, adapters):
    v, R_ = word['v'], word['R']
    n = 2 * v + R_
    frames = word['frames']
    need(adapters['status'] == 'RESIDUAL_ADAPTER_RECIPES' and set(adapters) == {'recipes', 'status'}, 'I record file shape')
    rec = adapters['recipes']
    base = {'entrance_rank', 'frame', 'left', 'rank', 'right', 'vectors'}
    for k, r in rec.items():
        need(set(r) == (base | {'terminal', 'terminal_rank', 'terminal_vectors'} if ':' in k else base), 'I record keys ' + k)
    starts = {str(word['start'][r]) for r in range(2 * v, n) if word['start'][r] != 0 and word['final'][r] == 1}
    ends = {'%d:%d' % (word['start'][r], word['final'][r]) for r in range(2 * v, n) if word['final'][r] != 1}
    need(set(rec) == starts | ends, 'I the 36 keys are the word\'s entering and hyperplane-ending helpers')
    for k, r in rec.items():
        E, U = end_of(k)
        w = len(frames[U]) - len(frames[E])
        need(r['frame'] == E and r['vectors'] == frames[E] and r['rank'] == w and r['entrance_rank'] == len(frames[E]), 'I record frames ' + k)
        if ':' in k:
            need(r['terminal'] == U and r['terminal_vectors'] == frames[U] and r['terminal_rank'] == len(frames[U]), 'I record end ' + k)
        need(A.well_formed(r['left']) and A.well_formed(r['right']), 'I monomials well formed ' + k)
    classes = Counter()
    for r in range(2 * v, n):
        s, f = word['start'][r], word['final'][r]
        classes['cold_full' if s == 0 and f == 1 else 'enter_full' if f == 1 else 'cold_hpe' if s == 0 else 'enter_hpe'] += 1
    events = {}
    for o in ('forward', 'backward'):
        prog = programs[o]
        touches = {}
        for i, e in enumerate(prog):
            if e[0] in ('climb', 'adapter', 'residual_adapter'):
                touches.setdefault(e[2], []).append(i)
            elif e[0] == 'scalar':
                for a in e[1][1:3]:
                    if isinstance(a, list) and a[0] == 'L':
                        touches.setdefault(a[1], []).append(i)
        res = [e for e in prog if e[0] == 'residual_adapter']
        need(all(e[1] in ('pre', 'post') and len(e) in (4, 5) for e in res), 'I residual events are pre or post: ' + o)
        pre = Counter(e[2] for e in res if e[1] == 'pre')
        post = Counter(e[2] for e in res if e[1] == 'post')
        wrapped = {r for r in range(2 * v, n) if word['start'][r] != 0 or word['final'][r] != 1}
        need(set(pre) == set(post) == wrapped and set(pre.values()) == set(post.values()) == {1}
             and len(res) == 2 * len(wrapped), 'I one pre and one post per wrapped helper: ' + o)
        for e in res:
            r = e[2]
            key = str(e[3]) if len(e) == 4 else '%d:%d' % (e[3], e[4])
            want = str(word['start'][r]) if word['final'][r] == 1 else '%d:%d' % (word['start'][r], word['final'][r])
            need(key == want and key in rec, 'I residual event key: ' + o)
        bad = 0
        for r in wrapped:
            idx = sorted(set(touches.get(r, ())))
            bad += not (prog[idx[0]][:2] == ['residual_adapter', 'pre'] and prog[idx[-1]][:2] == ['residual_adapter', 'post'])
        need(bad == 0, 'I pre first and post last for every wrapped helper: ' + o)
        widths = Counter(rec[str(e[3]) if len(e) == 4 else '%d:%d' % (e[3], e[4])]['rank'] for e in res)
        events[o] = dict(pre=sum(pre.values()), post=sum(post.values()), wrapped_helpers=len(wrapped),
                         widths={str(k): x for k, x in sorted(widths.items())})
    kinds = Counter('full_end' if ':' not in k else 'cold_hpe' if k.startswith('0:') else 'enter_hpe' for k in rec)
    return dict(records=len(rec), kinds=dict(sorted(kinds.items())), helper_classes=dict(sorted(classes.items())), events=events)


def calibrate(R, adapters):
    out = {}
    e702 = json.loads((ROOT / R.CASES['fixtures']['pr702']['path']).read_text())['identities']
    need(sha((ROOT / R.CASES['fixtures']['pr702']['path']).read_bytes()) == R.CASES['fixtures']['pr702']['sha256'], 'FX #702 pinned')
    need(all(B.kernel_digest_702(i['frame']) == i['kernel_sha256'] for i in e702), 'FX kernel B reproduces #702')
    out['pr702'] = 'kernel B reproduces all %d frame-kernel digests' % len(e702)
    f1415 = json.loads((ROOT / R.CASES['fixtures']['pr1415']['path']).read_text())['factorizations']
    need(sha((ROOT / R.CASES['fixtures']['pr1415']['path']).read_bytes()) == R.CASES['fixtures']['pr1415']['sha256'], 'FX #1415 pinned')
    for f in f1415:
        d, dens, nz = B.matrix_digest_1415(f['entrance'], f['terminal'])
        need(d == f['left']['matrix_sha256'] and dens == f['left']['denominator_exponents'] and nz == f['left']['nonzero_entries'],
             'FX kernel B reproduces #1415 pair %d' % f['pair'])
    out['pr1415'] = 'kernel B reproduces the three operator digests of T_U o T_E^-1 (frame operator at ranks 1 and 8, and its conjugate transpose)'
    pairs = R.lean_fixtures()
    rec = adapters['recipes']
    for key, k in (('3:998', 2), ('2:999', 3)):
        p = pairs[k - 1]
        need(rec[key]['vectors'] == p['E'] and rec[key]['terminal_vectors'] == p['U'] and rec[key]['left'] == p['L']
             and rec[key]['right'] == p['R'], 'FX record %s is Exact.lean pair %d' % (key, k))
    out['lean_pairs'] = 'records 3:998 and 2:999 equal Exact.lean pair 2 and pair 3 field by field'
    return out


def cross_check(A, word, adapters):
    """kernel B's monomial and F_w against kernel A's on every column of sample records (the frame operator is
    calibrated on #702 / #1415 separately)."""
    rec = adapters['recipes']
    for k in ('2', '423', '0:124', '0:1000', '3:998'):
        for side in ('left', 'right'):
            m = rec[k][side]
            cols = A.columns(A.run(A.monomial(m), A.radix(0)), A.radix(0))
            for x in range(B.DIM):
                need(B.monomial_apply(m, {x: (1, 0)}) == cols.get(x, {}), 'FX kernel B monomial = kernel A: ' + k)
    for w in (1, 4, 8, 9):
        cols = A.columns(A.run(A.fourier(w), A.radix(w)), A.radix(w))
        for x in (0, 1, 77, 300, 511):
            col, e = B.fourier_apply(w, {x: (1, 0)}, 0)
            need(e == w and col == cols.get(x, {}), 'FX kernel B F_w = kernel A')
    return 'kernel B monomials (10, all columns) and F_w (w = 1, 4, 8, 9) equal kernel A'


def evaluate(A, word, adapters):
    frames = word['frames']
    nA = nB = 0
    Ks = Counter()
    for k, r in sorted(adapters['recipes'].items()):
        E, U = end_of(k)
        w = len(frames[U]) - len(frames[E])
        nB += B.wrapper_identity(frames[E], frames[U], r['left'], r['right'], w) is None
        lhs = A.canonical_frame(frames[E]) + A.monomial(r['right']) + A.fourier(w) + A.monomial(r['left'])
        rhs = A.canonical_frame(frames[U])
        nA += A.same_operator(lhs, rhs)
        Ks[max(A.c_gates(lhs), A.c_gates(rhs))] += 1
    need(nA == nB == len(adapters['recipes']), 'E both kernels accept every record')
    return dict(records=len(adapters['recipes']), kernel_A_exact=nA, kernel_B_exact=nB, columns=B.DIM,
                global_phase_included=True, K_histogram={str(k): x for k, x in sorted(Ks.items())})


def _mut(m, field, fn):
    m = copy.deepcopy(m)
    m[field] = fn(m[field])
    return m


def controls(A, word, adapters, checks):
    frames = word['frames']
    rec = adapters['recipes']

    def ok(E, U, left, right, w):
        return A.same_operator(A.canonical_frame(frames[E]) + A.monomial(right) + A.fourier(w) + A.monomial(left),
                               A.canonical_frame(frames[U]))

    def cz(Q):
        Q = list(Q)
        Q[6] ^= 1 << 7
        Q[7] ^= 1 << 6
        return Q
    muts = {
        'global_phase': lambda L, R_, w: (L, _mut(R_, 'phase', lambda p: (p + 1) % 4), w),
        'input_character': lambda L, R_, w: (L, _mut(R_, 'linear_Z4', lambda a: [(a[0] + 2) % 4] + a[1:]), w),
        'cz_term': lambda L, R_, w: (_mut(L, 'quadratic_rows', cz), R_, w),
        'translation': lambda L, R_, w: (L, _mut(R_, 'offset', lambda b: b ^ 256), w),
        'swapped_wrappers': lambda L, R_, w: (R_, L, w),
        'width_minus_one': lambda L, R_, w: (L, R_, w - 1),
        'width_plus_one': lambda L, R_, w: (L, R_, w + 1),
        'transposed_matrix': lambda L, R_, w: (_mut(L, 'matrix_rows', lambda G: [sum(((G[j] >> i) & 1) << j for j in range(9)) for i in range(9)]), R_, w),
    }
    out = {}
    for name, fn in muts.items():
        rej = tot = 0
        for k, r in rec.items():
            E, U = end_of(k)
            w = len(frames[U]) - len(frames[E])
            L, R_, w2 = fn(r['left'], r['right'], w)
            if L == r['left'] and R_ == r['right'] and w2 == w:
                continue
            tot += 1
            rej += not ok(E, U, L, R_, w2)
        need(rej == tot, 'C control not rejected: ' + name)
        out[name] = 'rejected %d/%d' % (rej, tot)
    # hyperplane-end records evaluated against a FULL end; FULL-ended wrappers reused for a hyperplane end
    hpe = [k for k in rec if ':' in k]
    rej = sum(not ok(end_of(k)[0], 1, rec[k]['left'], rec[k]['right'], 9 - len(frames[end_of(k)[0]])) for k in hpe)
    need(rej == len(hpe), 'C hyperplane-end record against FULL')
    out['hpe_record_against_full_end'] = 'rejected %d/%d' % (rej, len(hpe))
    swap = [k for k in hpe if end_of(k)[0] != 0 and str(end_of(k)[0]) in rec]
    rej = sum(not ok(end_of(k)[0], end_of(k)[1], rec[str(end_of(k)[0])]['left'], rec[str(end_of(k)[0])]['right'],
                     len(frames[end_of(k)[1]]) - len(frames[end_of(k)[0]])) for k in swap)
    need(rej == len(swap), 'C FULL-ended wrapper used for a hyperplane end')
    out['full_wrapper_for_hyperplane_end'] = 'rejected %d/%d' % (rej, len(swap))
    # frame basis: same span, other basis -> rejected; reordered rows -> passes
    rej = passed = 0
    for k in ('0:124', '0:1000'):                       # end frames of dimension 4 and 8
        E, U = end_of(k)
        r = rec[k]
        tgt = U
        alt = list(frames)
        Uv = frames[tgt]
        alt[tgt] = [Uv[0] ^ Uv[1]] + Uv[1:]
        rej += not A.same_operator(A.canonical_frame(alt[E]) + A.monomial(r['right']) + A.fourier(len(frames[U]) - len(frames[E]))
                                   + A.monomial(r['left']), A.canonical_frame(alt[U]))
        alt[tgt] = list(reversed(Uv))
        passed += A.same_operator(A.canonical_frame(alt[E]) + A.monomial(r['right']) + A.fourier(len(frames[U]) - len(frames[E]))
                                  + A.monomial(r['left']), A.canonical_frame(alt[U]))
    need(rej == 2 and passed == 2, 'C frame basis control')
    out['frame_basis'] = 'other basis rejected 2/2; reordered rows pass 2/2'
    # kernel B also rejects: phase and width mutants on four records
    sample = ['2', '423', '0:124', '0:1000']
    rej = 0
    for k in sample:
        E, U = end_of(k)
        r = rec[k]
        w = len(frames[U]) - len(frames[E])
        rej += B.wrapper_identity(frames[E], frames[U], r['left'], _mut(r['right'], 'phase', lambda p: (p + 1) % 4), w) is not None
        rej += B.wrapper_identity(frames[E], frames[U], r['left'], r['right'], w - 1) is not None
    need(rej == 2 * len(sample), 'C kernel B rejects phase and width mutants')
    out['kernel_B_mutants'] = 'rejected %d/%d' % (rej, 2 * len(sample))
    out['producer_wrapper_checks'] = dict(status=checks['status'], frames=checks['frames'],
                                          hyperplane_end_pairs=len(checks['hyperplane_end_pairs']))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    ap.add_argument('--write', action='store_true')
    a = ap.parse_args()
    R, A = load_1781()
    data, adapters, checks, binding = bind(R)
    inv = inventory(A, data['word'], data['programs'], adapters)
    cal = calibrate(R, adapters)
    cal['kernel_B_vs_kernel_A'] = cross_check(A, data['word'], adapters)
    ev = evaluate(A, data['word'], adapters)
    ctrl = controls(A, data['word'], adapters, checks)
    result = dict(status='PASS_FRONTIER1094_RESIDUAL_WRAPPERS_EXACT', binding=binding, inventory=inv, calibration=cal,
                  evaluation=ev, controls=ctrl,
                  scope='Record level: all 36 residual wrappers of the selected gauge44 word satisfy L F_w R T_E = T_end on all '
                        '512 columns with global phase (Lemma A exact part); not the executor bridge, a Lean proof or a new kappa')
    text = json.dumps(result, indent=1, sort_keys=True) + '\n'
    target = HERE / 'RESULT.json'
    if a.write:
        target.write_text(text)
    else:
        need(target.read_text() == text, 'RESULT.json reproduced byte for byte')
    print('records %d (%s) events %s' % (inv['records'], inv['kinds'], {o: (x['pre'], x['post']) for o, x in inv['events'].items()}))
    print('PASS_FRONTIER1094_RESIDUAL_WRAPPERS_EXACT')


if __name__ == '__main__':
    try:
        main()
    except Reject as exc:
        raise SystemExit('FAIL ' + str(exc))

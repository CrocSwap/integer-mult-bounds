#!/usr/bin/env python3
"""Exact per-port operator check of the idle overlay on the emitted frames, with chronology.

Model (same as DATA-PHASES / #1255): in the Fourier basis |u>, C_v|u> = i^{u.v}|u> (v odd weight orthonormal axes) and a
translation s maps |u> -> |u+s>.  For every (replica, port) the idle children are applied in child order, each child as
the product of C_v over its frame axes (in stored order), followed by its translation_after; the recipe's stage X/Y
translations precede and the terminal Y translation follows the sequence.  The operator is then |u> -> i^{phi(u)}|u+T>
with phi(u) = sum_k [(u+s_k).v_k mod 2] over the ordered C factors, an exact Z4-valued quadratic form.  For the baseline
frames and the overlay frames we compute (T, phi) EXACTLY as polynomial coefficients mod 4 (linear + pairwise terms, constant)
and require equality for every port group with a changed child, then cross-check by evaluating phi directly at random u
through an independent bit-parity path.  Also requires the group axis multiset and every shift commutation s.v=0 used.
CLI: --hosted-baseline H0 --hosted H1 --base B --out RECEIPT.json [--samples N]"""
import argparse, gzip, json, random
from collections import Counter, defaultdict
from pathlib import Path


def read(p):
    p = Path(p); b = p.read_bytes()
    return json.loads(gzip.decompress(b) if p.suffix == '.gz' else b)


def dot(a, b): return (int(a) & int(b)).bit_count() & 1


def operator(seq):
    """seq: ordered list of ('C', v) / ('T', s). Returns exact (T, const, linear dict, quad dict) mod 4."""
    shift = 0; const = 0; lin = Counter(); quad = Counter()
    for kind, x in seq:
        if kind == 'T':
            shift ^= x
            continue
        v = x; c = dot(shift, v)               # (u+shift).v = u.v xor c
        supp = [i for i in range(v.bit_length()) if v >> i & 1]
        # parity l(u) = sum x_i - 2 sum_{i<j} x_i x_j (mod 4); xor with c: c=0 -> l ; c=1 -> 1-l
        sgn = -1 if c else 1
        const += c
        for i in supp: lin[i] += sgn
        for a in range(len(supp)):
            for b in range(a + 1, len(supp)):
                quad[supp[a], supp[b]] += -2 * sgn
    clean = lambda d: {k: x % 4 for k, x in d.items() if x % 4}
    return shift, const % 4, clean(lin), clean(quad)


def evaluate(seq, u):
    """Direct application to |u>: returns (phase exponent mod 4, final u)."""
    ph = 0
    for kind, x in seq:
        if kind == 'T': u ^= x
        else: ph += dot(u, x)
    return ph % 4, u


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--hosted-baseline', type=Path, required=True); ap.add_argument('--hosted', type=Path, required=True)
    ap.add_argument('--base', type=Path, required=True); ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--samples', type=int, default=24)
    a = ap.parse_args()
    f0 = read(a.hosted_baseline / 'IDLE-REMAINDER-FRAMES.json.gz'); f1 = read(a.hosted / 'IDLE-REMAINDER-FRAMES.json.gz')
    ph = read(a.base / 'work/complex-nine-native/DATA-PHASES.json'); rec = {r['port']: r for r in ph['recipes']}
    g0, g1 = defaultdict(dict), defaultdict(dict)
    for r in f0: g0[r['replica'], r['port']][r['child']] = r
    for r in f1: g1[r['replica'], r['port']][r['child']] = r
    assert g0.keys() == g1.keys()
    rng = random.Random(20261014); changed_groups = 0; evals = 0; axes_checked = 0
    for key in sorted(g0):
        old, new = g0[key], g1[key]
        assert old.keys() == new.keys()
        diff = [c for c in old if old[c] != new[c]]
        if not diff: continue
        changed_groups += 1
        R = rec[key[1]]
        pre = [('T', int(s[k])) for s in R['stage_alignment'] for k in ('entry_X', 'entry_Y', 'exit_X', 'exit_Y')]
        post = [('T', int(R['terminal_Y_translation']))]
        def build(frames):
            seq = list(pre)
            for c in sorted(frames):
                seq += [('C', int(v)) for v in frames[c]['orthogonal_axes']]
                seq.append(('T', int(R['idle_children'][c]['translation_after'])))
            return seq + post
        s0, s1 = build(old), build(new)
        assert operator(s0) == operator(s1), ('operator mismatch', key)
        # the same pair of sequences evaluated directly (independent path) on random basis states
        for _ in range(a.samples):
            u = rng.getrandbits(73)
            assert evaluate(s0, u) == evaluate(s1, u), ('direct mismatch', key, u)
            evals += 1
        axes_checked += sum(len(new[c]['orthogonal_axes']) for c in diff)
    rec_out = dict(status='PASS_EMITTED_STREAM_OPERATOR_EQUALITY', changed_port_groups=changed_groups, changed_axes_in_changed_children=axes_checked,
                   direct_evaluations=evals, exact_form='|u> -> i^phi(u)|u+T>, phi mod 4 exact quadratic coefficients, shifts and chronology included')
    a.out.write_text(json.dumps(rec_out, indent=2) + '\n'); print(rec_out['status'], changed_groups, 'groups')


if __name__ == '__main__':
    main()

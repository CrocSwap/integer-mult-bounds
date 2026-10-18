#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent recount of per-register paid child ranks of the pinned PR2312 and PR2322 T74 words.

Written by an independent AI reviewer subagent (Claude Code, Anthropic) from a plain-language statement of the
BORROW-WORD frame-climb rules only; it imports and copies nothing from move_prices.py or its vendored PR2387 code
(own GF(2) span / nesting / orthogonal-complement logic).  It re-derives, for both providers: each word's reported
local profile; the exact PR2312 -> PR2322 change set (4 removed (1,1,1,1) helpers, X lenders 1/4/6/12
(5,1,1,1) -> (2,1,1,1,1,1,1), partners 616/617/618/620 (4,1,1,1,1) -> (3,2,1,1,1), nothing else); the 33 remaining
(1,1,1,1) helpers and the 12 unused (5,1,1,1) X registers.  Apache-2.0.

Usage: python3 -I -B independent_recount.py [--repo PATH]   (needs the PR2312 / PR2322 commits; see move_prices.py --fetch)
"""
import argparse
import gzip
import hashlib
import os
import subprocess
import json
import sys
from collections import Counter

H = 9
FULL_MASK = (1 << H) - 1
NX, NY = 112, 112
Y0 = NX
HELP0 = NX + NY


def reduce_basis(vecs):
    """Return a canonical reduced row echelon basis (tuple of ints) for span(vecs)."""
    piv = {}  # leading bit -> vector
    for v in vecs:
        v &= FULL_MASK
        while v:
            lb = v.bit_length() - 1
            if lb in piv:
                v ^= piv[lb]
            else:
                piv[lb] = v
                break
    # full reduction
    keys = sorted(piv, reverse=True)
    for k in keys:
        for k2 in keys:
            if k2 != k and (piv[k2] >> k) & 1:
                piv[k2] ^= piv[k]
    return tuple(sorted(piv.values(), reverse=True))


def span(lst):
    return reduce_basis(lst or [])


def contains(big, small):
    """small subset of big (both reduced bases)."""
    return len(reduce_basis(list(big) + list(small))) == len(big)


def dot(a, b):
    return bin(a & b).count("1") & 1


def orth_complement(basis):
    return reduce_basis([w for w in range(1, FULL_MASK + 1)
                         if all(dot(w, b) == 0 for b in basis)])


FULL = span([1 << i for i in range(H)])


def recount(word):
    removed = set(word["removed"])
    ports = word["ports"]
    R = word["report"]["R"]
    nreg = HELP0 + R
    cur = {}
    for i in range(NX):
        cur[i] = span([ports[i]])
    for i in range(NY):
        cur[Y0 + i] = ()
    for r in range(HELP0, nreg):
        cur[r] = ()
    for k, fr in word.get("start_extra", {}).items():
        cur[int(k)] = span(fr)
    paid = {r: [] for r in range(nreg)}
    issues = []
    touched_removed = Counter()

    def move(r, F, where):
        if r in removed:
            touched_removed[r] += 1
            return
        c = cur[r]
        if not contains(F, c):
            issues.append((where, r, c, F))
            return
        d = len(F) - len(c)
        if d > 0:
            paid[r].append(d)
        cur[r] = F

    def gate_regs(g):
        if g[0] == "add":
            return [g[1], g[2]], g[5]
        if g[0] == "scale":
            return [g[1]], g[4]
        raise ValueError(g)

    # precondition / compensation / initial_corrections: pay nothing, but check
    # that they do not touch removed registers.
    for sec in ("initial_corrections", "precondition", "compensation"):
        for g in word.get(sec, []):
            regs, fr = gate_regs(g)
            for r in regs:
                if r in removed:
                    touched_removed[r] += 1
    for idx, g in enumerate(word["A"]):
        regs, fr = gate_regs(g)
        F = span(fr)
        for r in regs:
            move(r, F, ("A", idx))
    # cut: copy reads, ignored for climbs
    for g in word["cut"]:
        for r in gate_regs(g)[0]:
            if r in removed:
                touched_removed[r] += 1
    warps_at = {}
    for w in word["warps"]:
        warps_at.setdefault(w[0], []).append(w)
    B = word["B"]

    def apply_warps(pos):
        for (p, lender, cols, U, E) in warps_at.get(pos, []):
            if lender in removed:
                touched_removed[lender] += 1
                continue
            if cur[lender] != span(U):
                issues.append((("warp", pos), lender, cur[lender], span(U)))
            cur[lender] = span(E)

    for pos, g in enumerate(B):
        apply_warps(pos)
        regs, fr = gate_regs(g)
        F = span(fr)
        for r in regs:
            move(r, F, ("B", pos))
    apply_warps(len(B))
    bad_warp_pos = [p for p in warps_at if not 0 <= p <= len(B)]
    for idx, g in enumerate(word["restore"]):
        regs, fr = gate_regs(g)
        F = span(fr)
        for r in regs:
            move(r, F, ("restore", idx))
    hf = {int(k): span(v) for k, v in word.get("helper_final", {}).items()}
    for r in range(nreg):
        if r in removed:
            continue
        if r < NX:
            E = FULL
        elif r < HELP0:
            E = orth_complement(span([ports[r - Y0]]))
        else:
            E = hf.get(r, FULL)
        move(r, E, ("final", r))
    live = {r: tuple(sorted(paid[r], reverse=True)) for r in range(nreg) if r not in removed}
    prof = Counter()
    for r, ch in live.items():
        prof.update(ch)
    prof[8] += 8  # centre copies
    return live, prof, issues, touched_removed, bad_warp_pos



WORDS = {  # provider -> {word set: (commit, path, sha256)}
    'base': {'pr2312': ('fb76f799ccf078f51780076ebed3fd26b1db11c0',
                        'research/gmx-t74-borrow43-width-exchange/new/borrow/words/BORROW-WORD-43base.json.gz',
                        '4244149b59b287344b0e91aa50c6fa2a2491ee6c7a76d61cd352684a8182d005'),
             'pr2322': ('002304ef01c4416a127916169ae6d94c1bee052b', 'research/t74-joint-owner-hillclimb/words/base.json.gz',
                        '93c32c9dc8ca18394b7f3afac2cb4fa8582a6cb77399441b5107b396e63ca0f9')},
    'extra': {'pr2312': ('fb76f799ccf078f51780076ebed3fd26b1db11c0',
                         'research/gmx-t74-borrow43-width-exchange/new/borrow/words/BORROW-WORD-43extra.json.gz',
                         '01d510cc4ba912567f6b02ea50b6b0e741ed231a3608de9c36e7eeccbdaf6cda'),
              'pr2322': ('002304ef01c4416a127916169ae6d94c1bee052b', 'research/t74-joint-owner-hillclimb/words/extra.json.gz',
                         'aae6592eaa4cf8638f21d50c44d09d4f8a6bb079ddcf5e377711a10ee2ddb526')},
}
H1111 = [273, 275, 277, 282, 289, 291, 293, 298, 305, 307, 309, 314, 321, 323, 325, 330, 337, 339, 341, 346, 353, 355,
         357, 362, 369, 371, 373, 378, 385, 387, 389, 394, 653]
X5111 = [31, 33, 49, 55, 68, 74, 80, 83, 85, 88, 98, 101]


def load(repo, commit, path, sha):
    data = subprocess.run(['git', '-C', repo, 'show', commit + ':' + path], capture_output=True, check=True).stdout
    assert hashlib.sha256(data).hexdigest() == sha, path
    return json.loads(gzip.decompress(data))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--repo', default=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    repo = ap.parse_args().repo
    for prov, ws in WORDS.items():
        res = {}
        for name, (commit, path, sha) in ws.items():
            word = load(repo, commit, path, sha)
            live, prof, issues, touched, badpos = recount(word)
            rep = {int(k): v for k, v in word["report"]["local_profile"].items()}
            assert dict(prof) == rep, (prov, name, 'profile', dict(prof), rep)
            assert not issues and not any(touched.values()) and not badpos, (prov, name, issues[:3], touched, badpos)
            res[name] = (live, word)
        (la, _wa), (lb, wb) = res['pr2312'], res['pr2322']
        assert sorted(set(la) - set(lb)) == [619, 621, 622, 623] and not set(lb) - set(la)
        assert all(la[r] == (1, 1, 1, 1) for r in (619, 621, 622, 623))
        changed = {r: (la[r], lb[r]) for r in set(la) & set(lb) if la[r] != lb[r]}
        want = {r: ((5, 1, 1, 1), (2, 1, 1, 1, 1, 1, 1)) for r in (1, 4, 6, 12)}
        want.update({r: ((4, 1, 1, 1, 1), (3, 2, 1, 1, 1)) for r in (616, 617, 618, 620)})
        assert changed == want, (prov, changed)
        lenders = {w[1] for w in wb["warps"]}
        assert [r for r in sorted(lb) if r >= HELP0 and lb[r] == (1, 1, 1, 1)] == H1111
        assert [r for r in sorted(lb) if r < NX and lb[r] == (5, 1, 1, 1) and r not in lenders] == X5111
        print('%s: profiles match reports; PR2312 -> PR2322 change set, 33 (1,1,1,1) helpers and 12 free (5,1,1,1) '
              'X registers confirmed' % prov)
    print('PASS_T74_INDEPENDENT_RECOUNT')


if __name__ == "__main__":
    main()

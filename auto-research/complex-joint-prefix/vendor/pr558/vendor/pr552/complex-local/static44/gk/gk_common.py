"""Shared helpers for the complex shared-donor-kernel / entrance-gauge word.  Apache-2.0.
Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code.

A "gk word" is PR #433's FULL-WORD.json.gz with optional extension keys (absent in #433's word, so every default is
#433's behaviour):
  start_extra   {register: entrance frame (list of F2^9 vectors)}  helpers that start at a nonzero frame (width 9 - dim)
  target_levels {target: frame}                                    frame a target reaches through nonzero-frame compensation
Entrance gauges are ordinary gates at the head of A (target += c * helper at the entrance frame); kernel updates are
ordinary gates at the head of A (donor += q * pivot at the entrance frame).
"""
import math
from collections import Counter

V, K, T, L, M = 120, 4, 8, 9, 73
DATA = 2 * K * V * T          # 7680
FULL = tuple(1 << i for i in range(8, -1, -1))


def basis(vs):
    b = {}
    for x in vs:
        for p in sorted(b, reverse=True):
            if x >> p & 1: x ^= b[p]
        if x:
            p = x.bit_length() - 1
            for q in b:
                if b[q] >> p & 1: b[q] ^= x
            b[p] = x
    return tuple(b[p] for p in sorted(b, reverse=True))


def widths_of(word):
    """residual width of every helper: 9 - dim(entrance frame); 9 when the word has no extension"""
    R = word['report']['R'] if 'R' not in word else word['R']
    w = [L] * R
    for r, E in word.get('start_extra', {}).items():
        assert 2 * V <= int(r) < 2 * V + R
        w[int(r) - 2 * V] = L - len(basis(E))
    return w


def split_pad(p):
    """a pad of rank p is paid as nested commuting children of rank <= 51 (so that 73^2 > 2*child^2); rank 1 stays 1"""
    if p == 0: return []
    n = -(-p // 51); return [p // n + (1 if i < p % n else 0) for i in range(n)]


def tile(items):
    """Bank tiling of unhosted residuals.  items: list of (rep, helper, width); a bank has M = 73 cells.
    * width-9 residuals (no wrapper acts on them): first fit in the given order, packed from offset 0, eight per bank, pad rank 1
      (PR #433/#442's tiling and routes [2, slot]);
    * ENTERING residuals (width w < 9, paid wrappers, e = 9 - w spectators): banks of their own in which every entering helper is the ONLY
      owner of its bank family in its invocation (the one-helper rule of PR #458 extended to banks): bank j holds the j-th entering
      helper of each replica, residuals packed from offset 0 in replica order (at most one helper per replica, hence per invocation).
      The spectators of an entering helper are the first e cells of the bank beyond every residual cell of the bank (the pad, which no call
      uses for a residual, is paid as before: rank 73 - sum of widths; the spectators are borrowed inside it and not deducted).
    Returns (assign, banks, pads): assign[(rep, helper)] = (bank, offset, width, pure, spectators) with pure = the bank holds only width-9
    residuals and spectators = () for width 9; pads = Counter of pad ranks (split into children of rank <= 51)."""
    assign = {}; pads = Counter(); fill = []
    for z, (rep, h, w) in enumerate(items):             # width 9: first fit, as PR #433 (all widths 9 reproduces it exactly)
        if w != L: continue
        for b, f in enumerate(fill):
            if f + w <= M: break
        else:
            b = len(fill); fill.append(0)
        assign[(rep, h)] = (b, fill[b], w, True, ()); fill[b] += w
    nwide = len(fill); byrep = {}
    for rep, h, w in items:
        if w < L: byrep.setdefault(rep, []).append((h, w))
    cells = [0] * max((len(v) for v in byrep.values()), default=0); emax = [0] * len(cells); place = {}
    for rep in sorted(byrep):                           # the j-th entering helper of every replica goes to entering bank j
        for j, (h, w) in enumerate(byrep[rep]):
            place[(rep, h)] = (nwide + j, cells[j], w); cells[j] += w; emax[j] = max(emax[j], L - w)
    for j in range(len(cells)): assert cells[j] + emax[j] <= M, ('entering bank without room for its spectators', j)
    for (rep, h), (b, off, w) in place.items():
        assign[(rep, h)] = (b, off, w, False, tuple(range(cells[b - nwide], cells[b - nwide] + L - w)))
    fill += cells
    for f in fill:
        for part in split_pad(M - f): pads[part] += 1
    return assign, len(fill), pads


def route(off, w, pure, sp=()):
    """owner route of a banked helper residual: PR #433's [2, slot] for width 9 (pure width-9 bank); an entering helper (w < 9) is
    [2, offset, width, [spectator cells]] with e = 9 - w spectators"""
    if w == L: assert pure and not sp; return [2, off // L]
    assert not pure and len(sp) == L - w; return [2, off, w, list(sp)]


def unhosted_stock(widths):
    """live stock and padding histogram of the unhosted (parent) template, per stage x nine"""
    R = len(widths)
    _, nb, pads = tile([(rep, h, widths[h]) for rep in range(T) for h in range(R)])
    return DATA + L * nb, Counter({r: z * L for r, z in pads.items()})

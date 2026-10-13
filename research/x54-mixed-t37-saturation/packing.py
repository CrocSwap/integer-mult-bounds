#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact idle-remainder optimality of the #1193/#1218 mixed T37 packing (standard library only).

Inputs: the two final local words (D3, D4), the frozen integer pattern flow and call mix of #1193, and the
T37 parent geometry retained on main (the #1042 replay archive and PR858/PR870's unchanged `actual_windows`).

Statement checked here (all integers / exact rationals, 50-digit decimals only for one sign test):

  Width-class invariant.  Put phi(4) = phi(8) = 0, phi(5) = 3, phi(7) = 1, phi(9) = -1 and, for a multiset p of
  helper widths, Phi(p) = sum phi.  Enumerating every multiset over {4,5,7,8,9}: a bin filled exactly to
  capacity 8, 16 or 32 has Phi >= 0, and one filled exactly to capacity 48 has Phi >= -4.

  Consequence.  With the frozen 125 D3 / 208 D4 mix, the T37 bins (8,16,32,48 capacities) and any assignment
  of the 159,840 whole helpers to bins (time windows, ports and family rules ignored, so this is a relaxation),
  the idle (remainder) profile {1:2, 48:11374} of #1193 is the cheapest one achievable: the only cheaper idle
  histogram of the same mass with ranks <= 48 is {2:1, 48:11374}, and every packing realizing it has
  Phi_total > -20814 = Phi(helpers), a contradiction.

Scope: one mix, one bin geometry, one width alphabet. It does not bound other local words, mixes, templates or
outer recipes; `aggregate.py` screens the demotion-count mixes numerically.
"""
import argparse, gzip, hashlib, importlib.util, itertools, json, sys, tarfile, tempfile
from collections import Counter
from decimal import Decimal, getcontext
from pathlib import Path

PKG = Path(__file__).resolve().parent
ROOT = PKG.parents[1]
WIDTHS = (4, 5, 7, 8, 9)
PHI = {4: 0, 5: 3, 7: 1, 8: 0, 9: -1}
ARCHIVE = ROOT / 'research/community-frontier1042-audit/selected-replay.tar.gz'
ARCHIVE_SHA = '22c3f4dce4b897a1d423d1388801933e288b6a6b1906cb15e1b16a5eb68db754'
TEMPLATE = 'slots/global/global/base/split-centres/GLOBAL-TEMPLATE.json.gz'
WINDOWS_MODULE = ROOT / 'research/complex-t21-owners/vendor/pr870/t16/build_parent.py'
M, LIVE = 73, 33152


def require(ok, why):
    if not ok:
        raise AssertionError(why)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    raw = Path(path).read_bytes()
    return json.loads(gzip.decompress(raw) if str(path).endswith('.gz') else raw)


def dim(vectors):
    """GF(2) dimension of the span of 9-bit integer vectors."""
    basis = []
    for v in vectors:
        for b in basis:
            v = min(v, v ^ b)
        if v:
            basis.append(v)
    return len(basis)


def helper_widths(word):
    """Width of every helper: dim(final frame) - dim(start frame); full final frame has dimension 9.
    Independent of the toolkit and of the native canonical word (same convention as the lineage recount)."""
    v, R = word['report']['v'], word['report']['R']
    out = []
    for q in range(2 * v, 2 * v + R):
        start = dim(word['start_extra'].get(str(q), []))
        end = dim(word['helper_final'][str(q)]) if str(q) in word['helper_final'] else 9
        out.append(end - start)
    return out


def min_phi(total, max_len=12):
    """Exact minimum of Phi over multisets of widths with the given sum (None when the sum is unattainable)."""
    best = None
    for k in range(1, max_len + 1):
        for p in itertools.combinations_with_replacement(WIDTHS, k):
            if sum(p) == total:
                f = sum(PHI[w] for w in p)
                best = f if best is None or f < best else best
    return best


def geometry(flow, order):
    """Capacity of every flow group from the retained T37 parent's idle-child ranks (PR858/870 windows)."""
    require(sha(ARCHIVE) == ARCHIVE_SHA, 'retained #1042 archive changed')
    with tempfile.TemporaryDirectory() as tmp, tarfile.open(ARCHIVE) as t:
        member = t.getmember(TEMPLATE)
        require(member.isfile(), 'template member')
        t.extract(member, tmp, filter='data')
        parent = read(Path(tmp) / TEMPLATE)
    spec = importlib.util.spec_from_file_location('pr870_build_parent', WINDOWS_MODULE)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    windows, _ = mod.actual_windows(parent, order)
    caps = []
    for g in flow:
        cs = {windows[k][0] for k in g['physical_windows']}
        require(len(cs) == 1, 'one capacity per group')
        caps.append(cs.pop())
    return caps, windows


def f(r, a):
    """(r/m)^(1-a) to 50 digits."""
    getcontext().prec = 60
    return (Decimal(r) / M) ** (1 - a)


def load_inputs(inputs=PKG / 'inputs'):
    return dict(d3=read(inputs / 'D3-WORD.json.gz'), d4=read(inputs / 'D4-WORD.json.gz'),
                flow=read(inputs / 'FLOW.json.gz'), mix=read(inputs / 'MIX.json'))


def check(data=None, geometry_cache=None):
    data = data or load_inputs()
    d3, d4, flow, mix = data['d3'], data['d4'], data['flow'], data['mix']
    order = sorted([[s, r] for s in range(9) for r in range(37)], key=lambda k: (37 * k[0] + 8 * k[1], k[0], k[1]))
    require([[s, r] for _, s, r in mix] == order, 'frozen #1131/#1152 wave order')
    calls = Counter(pid for pid, _, _ in mix)
    require(calls == {'demote3': 125, 'demote4': 208}, 'call mix')
    inv = {'demote3': Counter(helper_widths(d3)), 'demote4': Counter(helper_widths(d4))}
    require(inv['demote3'] == {4: 44, 5: 44, 7: 38, 8: 114, 9: 240}, 'D3 width inventory')
    require(inv['demote4'] == {4: 40, 5: 48, 7: 38, 8: 114, 9: 240}, 'D4 width inventory')
    helpers = Counter()
    for pid, n in calls.items():
        for w, c in inv[pid].items():
            helpers[w] += n * c

    if geometry_cache is not None and 'caps' in geometry_cache:
        caps = geometry_cache['caps']
    else:
        caps, _ = geometry(flow, order)
        if geometry_cache is not None:
            geometry_cache['caps'] = caps
    bins, used, idle = Counter(), Counter(), Counter()
    phi_bins = 0
    for cap, g in zip(caps, flow):
        require(sum(p['count'] for p in g['patterns']) == 112 * len(g['physical_windows']), 'every port is one bin')
        for p in g['patterns']:
            s = sum(p['widths'])
            require(s <= cap, 'pattern fits')
            bins[cap] += p['count']
            for w in p['widths']:
                used[w] += p['count']
            if cap - s:
                idle[cap - s] += p['count']
            phi_bins += p['count'] * sum(PHI[w] for w in p['widths'])
    require(used == helpers, 'the flow hosts every whole helper exactly once')
    require(dict(idle) == {1: 2, 48: 11374}, '#1193 idle profile')
    capacity = sum(c * n for c, n in bins.items())
    idle_mass = capacity - sum(w * n for w, n in helpers.items())
    require(idle_mass == sum(r * n for r, n in idle.items()) == 545954, 'idle mass')
    phi_total = sum(PHI[w] * n for w, n in helpers.items())
    require(phi_total == phi_bins == -20814, 'Phi is a sum over helpers')

    # Lemma: exact minima of Phi over full bins and over remainder-two bins.
    full = {c: min_phi(c) for c in bins}
    require(full == {8: 0, 16: 0, 32: 0, 48: -4}, 'full-bin Phi minima')
    rem2 = {c: min_phi(c - 2) for c in bins}
    q = idle_mass // 48
    require(idle_mass == 48 * q + 2 and max(bins) == 48, 'mass decomposition')
    # Cheapest idle histograms. Remainder ranks never exceed 48 (the largest capacity) and the idle mass is
    # 48*q + 2. A histogram with exactly q rank-48 parts has remainder (1, 1) (the incumbent) or (2). One with
    # k = q - j rank-48 parts (j >= 1) puts mass 48*j + 2 into parts <= 47; f is concave with f(0) = 0, so by
    # Karamata the greedy partition (47, ..., 47, rest) majorizes every such partition and is the cheapest.
    # The loop checks that this lower bound already exceeds the incumbent cost for every j.
    a = Decimal('0.001678622735735992236999')   # #1193 native upper root endpoint (cost increases with a)
    f1, f2, f47, f48 = f(1, a), f(2, a), f(47, a), f(48, a)
    worst = None
    for j in range(1, q + 1):
        t, rest = divmod(48 * j + 2, 47)
        gap = t * f47 + (f(rest, a) if rest else 0) - j * f48 - 2 * f1
        worst = gap if worst is None or gap < worst else worst
    require(worst > 0, 'every less concentrated histogram is dearer')
    require(2 * f1 > f2, '{2:1} is cheaper than {1:2}')
    # {2:1, 48:q} forces exactly q empty capacity-48 bins, one remainder-two bin and every other bin full.
    occupied48 = bins[48] - q
    bounds = {}
    for c, mphi in rem2.items():
        if mphi is None:
            bounds[c] = None
            continue
        full48 = occupied48 - (1 if c == 48 else 0)
        bounds[c] = full[48] * full48 + mphi
    require(all(b is None or b > phi_total for b in bounds.values()), 'Phi rules out a remainder-two bin')
    # The incumbent is tight: every occupied capacity-48 bin attains -4 and the two remainder-one bins -3 each.
    require(full[48] * occupied48 + 2 * sum(PHI[w] for w in (4, 9, 9, 9)) == phi_total, 'tightness')
    return dict(
        status='PASS_EXACT_IDLE_REMAINDER_OPTIMUM_FOR_FIXED_MIX_RELAXATION',
        mix=dict(calls), helper_widths=dict(sorted(helpers.items())), bins_by_capacity=dict(sorted(bins.items())),
        idle_profile=dict(sorted(idle.items())), idle_mass=idle_mass, phi={str(w): PHI[w] for w in WIDTHS},
        phi_total=phi_total, phi_min_full_bin=full, phi_min_remainder_two_bin=rem2,
        phi_lower_bound_with_remainder_two_bin={str(c): b for c, b in bounds.items()},
        concentration_test=dict(endpoint=str(a), min_gap_over_j=str(worst)[:32], j_range=[1, q]),
        scope='Fixed 125 D3 / 208 D4 mix, the retained T37 bin capacities, whole helpers, time windows and family '
              'rules relaxed. No statement about other local words, mixes, templates or outer recipes.')


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--out', type=Path)
    a = ap.parse_args()
    r = check()
    if a.out:
        a.out.write_text(json.dumps(r, indent=1, sort_keys=True) + '\n')
    print(r['status'], 'Phi', r['phi_total'], 'idle', r['idle_profile'])

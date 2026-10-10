#!/usr/bin/env python3
"""gcert_emit.py: lower a source-aligned complex flow to Jacob Sussman's certificate format gcert/1.

Inputs (all produced by the integer-mult-bounds tool chain of PR #184 / #194 on an aligned tree):
  --cache     the aligned tree's cache (graph.json, selection.json)
  --flow      flow.json          (complex_frame_flow.py --witness)
  --witness   flow.witness.json  (same run)
  --lift      lift.certificate.json.gz (exact_complex_flow_lift.py: local invertible completions as elementary gates)
Output: a gcert/1 JSON(.gz) as read by wht-power-saving-lean/tools/gx/gx.py (check1) and gxgen.py.

Registers: x_j = j (sources, start at the port line), y_t = v+t (targets, start at frame 0, end at port^perp),
slots 2v.. (one per physical flow coordinate: v source copies + births; kernel reuse continues a slot).
Every node of the flow DAG (phase, frame) becomes, at its frame: the source copies (x -> slot), the reads
(slot -> targets, or a retained total for the scatter), then the lift's elementary gates.  A 'swap' relabels
positions, a 'scale' changes the unit of a slot (wanted = lam * stored, as gxconv.py), an 'add' is one 'out'
gate.  After phase 2: the paired-cube K blocks (1 - J/2) on each parity class of a cube, the direct reads of the
mixed sources into their antipodal targets at the target cap frames, and the inverse K blocks at the full frame.
"""
import argparse, gzip, json, heapq, sys, time
from collections import Counter, defaultdict
from fractions import Fraction as F


def load(p):
    p = str(p)
    if p.endswith('.gz'):
        return json.loads(gzip.decompress(open(p, 'rb').read()))
    return json.load(open(p))


def rref(rows):
    piv = {}
    for x in rows:
        for k in sorted(piv, reverse=True):
            if x >> k & 1:
                x ^= piv[k]
        if x:
            k = x.bit_length() - 1
            for kk in list(piv):
                if piv[kk] >> k & 1:
                    piv[kk] ^= x
            piv[k] = x
    return tuple(piv[k] for k in sorted(piv, reverse=True))


def perp(rows, h):
    """basis of the orthogonal complement (standard dot product mod 2) of span(rows)"""
    B = rref(rows)
    piv = [b.bit_length() - 1 for b in B]
    free = [k for k in range(h) if k not in piv]
    out = []
    for k in free:
        u = 1 << k
        for b in B:
            if b >> k & 1:
                u |= 1 << (b.bit_length() - 1)
        out.append(u)
    return rref(out)


def enc(x):
    x = F(x)
    return [x.numerator, x.denominator]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--cache', required=True)
    ap.add_argument('--flow', required=True)
    ap.add_argument('--witness', required=True)
    ap.add_argument('--lift', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--name', default='flow word')
    a = ap.parse_args()
    t0 = time.time()
    g = load(a.cache + '/graph.json'); word = load(a.cache + '/selection.json')
    prof = load(a.flow); wit = load(a.witness); lift = load(a.lift)
    h, v = g['h'], g['v']
    ports = g['inputs']
    assert ports == wit['original_source_ports']
    nodes, edges, vectors = wit['nodes'], wit['edges'], wit['vectors']
    maps, order = lift['maps'], lift['topological_order']
    assert len(maps) == len(nodes) == len(order)
    roots = g['roots']
    # ---- frames
    frames = [(), tuple(1 << i for i in range(h - 1, -1, -1))]
    fid = {frames[0]: 0, frames[1]: 1}

    def frame(rows):
        key = rref(rows)
        if key not in fid:
            fid[key] = len(frames); frames.append(key)
        return fid[key]
    xstart = [frame((q,)) for q in ports]
    caps = [frame(perp((q,), h)) for q in ports]
    # ---- signed side rows of the deferred roles (as contract_v4.validate)
    ops, coeff = word['ops'], word['opcoeff']
    Rw = max(max(x, y) for x, y, _ in ops) + 1
    selected = {s['role']: s for s in word['selected']}
    side = [dict() for _ in range(Rw)]
    for r, s in zip(roots, word['rootroles']):
        if r['kind'] != 'center':
            side[s] = {t: (1 if c == '1/2' else -1) for t, c in zip(r['targets'], r['coefficients'])}

    def add_scaled(dst, src, c):
        for k, x in src.items():
            y = dst.get(k, 0) + c * x
            if y:
                dst[k] = y
            else:
                dst.pop(k, None)
    for (x, y, _), (ca, cb) in zip(reversed(ops), reversed(coeff)):
        add_scaled(side[y], side[x], cb)
        if ca != 1:
            side[x] = {j: ca * c for j, c in side[x].items()}
    for s, z in selected.items():
        assert set(side[s]) == set(z['targets'])

    def responses(rd):
        if rd['kind'] == 'side':
            r = roots[rd['ref']]
            return {t: F(1, 2) if c == '1/2' else F(-1, 2) for t, c in zip(r['targets'], r['coefficients'])}
        assert rd['kind'] == 'deferred'
        return {t: F(-c, 2) for t, c in side[rd['ref']].items()}
    # ---- edge coordinates: (target node, input position) -> (source node, output position)
    by_frame = {(n['frame'][0], tuple(n['frame'][1])): i for i, n in enumerate(nodes)}
    out_off, in_off = Counter(), Counter()
    coord_in = {}
    for e in edges:
        i = by_frame[(e['source'][0], tuple(e['source'][1]))]; j = by_frame[(e['target'][0], tuple(e['target'][1]))]
        for k in range(len(e['basis'])):
            coord_in[j, in_off[j] + k] = (i, out_off[i] + k)
        out_off[i] += len(e['basis']); in_off[j] += len(e['basis'])
    kernel_birth = {}
    for i, aa, j, bb in wit['kernel_pairs']:
        kernel_birth[j, bb] = (i, aa)
    # ---- emission
    A, B, ret = [], [], []
    nslot = 0
    lam = {}

    def new_slot():
        nonlocal nslot
        s = 2 * v + nslot; nslot += 1; lam[s] = F(1)
        return s
    slot_out, kernel_slot = {}, {}
    center_lam = {}
    stats = Counter()
    phase_of_node = {}
    for i in order:
        node, mp = nodes[i], maps[i]
        ph, U = node['frame']
        f = frame(tuple(U))
        gates = A if ph == 1 else B
        n, t, b, d, r = node['n'], node['t'], node['new_dirty'], node['d'], node['r']
        N = n + b
        assert mp['size'] == N and not mp['source_erase'] and not mp['source_inject'], 'source controls not supported yet'
        pos = [None] * N
        nin = in_off[i]
        g0_node = len(gates)
        for p in range(n):
            if p < nin:
                pos[p] = slot_out[coord_in[i, p]]
            else:                                   # original source copy at its port line
                row = vectors[node['inputs'][p]]
                assert len(row) == 1 and row[0][1] == 1 and ph == 1 and f == xstart[row[0][0]]
                s = new_slot(); pos[p] = s
                gates.append(['out', f, row[0][0], [[s, 1, 1]], []])
        for q in range(b):
            if (i, q) in kernel_birth:
                s = kernel_slot[kernel_birth[i, q]]; lam[s] = F(1)
            else:
                s = new_slot()
            pos[n + q] = s
        # reads (in terms of the input positions, before the completion)
        for rd, rc in zip(node['reads'], mp['read_coefficients']):
            if rd['kind'] == 'center':
                assert ph == 1
                k = roots[rd['ref']]['coordinate']
                val = rd['value']
                if val in node['outputs']:
                    assert len(rc) == 1
                    center_lam[k] = (i, 'out', node['outputs'].index(val), F(rc[0][1], rc[0][2]))
                else:
                    # the total is formed in place in one of its (retiring) input registers
                    assert t == 0 and not mp['inverse_gates'], ('center total neither leaves nor rests', i)
                    p0, n0, d0 = rc[0]; s0 = pos[p0]; c0 = F(n0, d0) * lam[s0]
                    for p, num, den in rc[1:]:
                        s = pos[p]
                        gates.append(['out', f, s, [[s0, *enc(F(num, den) * lam[s] / c0)]], []])
                    center_lam[k] = (i, 'pos', p0, c0)
                continue
            assert ph == 2
            resp = responses(rd)
            for p, num, den in rc:
                s = pos[p]
                c = F(num, den) * lam[s]
                gates.append(['out', f, s, [[v + tt, *enc(c * w)] for tt, w in sorted(resp.items())], []])
        # completion gates: the lift stores the row operations taking Q to I; the registers need Q itself,
        # i.e. the inverse operations in reverse order (exact_complex_flow_lift.inverse_program, 'forward').
        g0 = len(gates)
        for kind, x, y, num, den in reversed(mp['inverse_gates']):
            if kind == 'swap':
                pos[x], pos[y] = pos[y], pos[x]
            elif kind == 'scale':
                assert x == y
                lam[pos[x]] /= F(num, den)
            else:
                assert kind == 'add' and x != y
                sx, sy = pos[x], pos[y]
                c = -F(num, den) * lam[sy] / lam[sx]
                gates.append(['out', f, sy, [[sx, *enc(c)]], []])
        # every coordinate that passes through the node is moved to its frame (the flow charges the edge):
        # registers of inputs and births that no gate of this node names ride as extra registers
        named = set()
        for gg in gates[g0_node:]:
            named.add(gg[2]); named.update(x_ for x_, _, _ in gg[3])
            if gg[0] == 'out':
                named.update(gg[4])
        idle = [s_ for s_ in pos if s_ not in named]
        if idle:
            outs = [gg for gg in gates[g0_node:] if gg[0] == 'out']
            if outs:
                outs[-1][4].extend(idle)
            else:
                stats['idle_nodes'] += 1
                gates.append(['out', f, idle[0], [], idle[1:]])
        for q in range(t):
            slot_out[i, q] = pos[q]
        for aa in range(node['retired'] - (d - r)):
            kernel_slot[i, aa] = pos[t + (d - r) + aa]
        # retained totals: the coordinate must survive the completion in one register
        for k, z in list(center_lam.items()):
            if isinstance(z, tuple) and z[0] == i:
                ii, how, p, c = z
                s = pos[p]
                ret.append([k, s, f]); center_lam[k] = c * lam[s] if how == 'out' else c
    R = nslot
    assert R == prof['new_R'], (R, prof['new_R'])
    ret.sort()
    assert [z[0] for z in ret] == list(range(h)), 'one retained total per coordinate expected'
    # ---- K blocks, direct reads, inverse K blocks
    for cube in range(v // 8):
        ids8 = list(range(8 * cube, 8 * cube + 8))
        for parity in range(2):
            ids = [j for j in ids8 if j.bit_count() % 2 == parity]
            S = frame(tuple(ports[j] for j in ids))
            assert len(frames[S]) == 3
            x1, rest = ids[0], ids[1:]
            B.append(['in', S, x1, [[r_, 1, 1] for r_ in rest]])
            B.append(['out', S, x1, [[r_, -1, 2] for r_ in rest], []])
            B.append(['in', S, x1, [[r_, 1, 1] for r_ in rest]])
    for cube in range(v // 8):
        ids8 = list(range(8 * cube, 8 * cube + 8))
        for j in ids8:
            anti = [t for t in ids8 if (ports[t] ^ ports[j]).bit_count() == 6]
            assert len(anti) == 1
            t = anti[0]
            x1 = [jj for jj in ids8 if jj.bit_count() % 2 == j.bit_count() % 2][0]
            B.append(['out', caps[t], j, [[v + t, -1 if j == x1 else 1, 1]], []])
    for cube in range(v // 8):
        ids8 = list(range(8 * cube, 8 * cube + 8))
        for parity in range(2):
            ids = [j for j in ids8 if j.bit_count() % 2 == parity]
            x1, rest = ids[0], ids[1:]
            B.append(['in', 1, x1, [[r_, -1, 1] for r_ in rest]])
            B.append(['out', 1, x1, [[r_, 1, 2] for r_ in rest], []])
            B.append(['in', 1, x1, [[r_, -1, 1] for r_ in rest]])
    # ---- scatter
    sin, sout = F(1, 3), F(-1, 6)
    if all(center_lam[k] == 1 for k in range(h)):
        scat = dict(inside=[1, 3], outside=[-1, 6])
    else:
        scat = dict(table=[[[k, *enc((sin if ports[t] >> k & 1 else sout) * center_lam[k])] for k in range(h)] for t in range(v)])
    nreg = 2 * v + R
    start = [0] * nreg; final = [1] * nreg
    for j in range(v):
        start[j] = xstart[j]; final[v + j] = caps[j]
    cst = sum(len(frames[f]) for _, _, f in ret)
    # ---- blocks (the climb count of gx.check1)
    dim = [len(f) for f in frames]
    cur = list(start)
    H = {'x': Counter(), 'y': Counter(), 's': Counter(), 'c': Counter()}
    cls = lambda r_: 'x' if r_ < v else 'y' if r_ < 2 * v else 's'

    def climb(r_, f):
        o = cur[r_]
        if o != f:
            assert dim[o] < dim[f], ('step not increasing', r_, o, f)
            H[cls(r_)][dim[f] - dim[o]] += 1; cur[r_] = f
    for ph, gates in (('A', A), ('B', B)):
        if ph == 'B':
            for k, s, f in ret:
                assert cur[s] == f, ('retained slot moved before the cut', k, s)
                H['c'][dim[f]] += 1
        for gg in gates:
            regs = [gg[2]] + ([x for x, _, _ in gg[3]] + list(gg[4]) if gg[0] == 'out' else [x for x, _, _ in gg[3]] if gg[0] == 'in' else [])
            for r_ in regs:
                climb(r_, gg[1])
    for r_ in range(nreg):
        climb(r_, final[r_])
    blocks = {k: {str(r_): n_ for r_, n_ in sorted(w.items())} for k, w in H.items()}
    Nn = sum(r_ * n_ for w in H.values() for r_, n_ in w.items())
    assert Nn == R * h + 2 * v * (h - 1) + cst, (Nn, R * h + 2 * v * (h - 1) + cst)
    c1 = dict(format='gcert/1', derived_from='%s (gcert_emit.py from complex_frame_flow.py witness + exact_complex_flow_lift.py completions)' % a.name,
              p=g['p'], h=h, v=v, R=R, cst=cst, N=Nn, ports=ports, frames=[list(f) for f in frames], start=start, final=final,
              ext=[], ret=ret, scat=scat, A=A, B=B, blocks=blocks)
    data = json.dumps(c1, separators=(',', ':')).encode()
    if a.out.endswith('.gz'):
        open(a.out, 'wb').write(gzip.compress(data))
    else:
        open(a.out, 'wb').write(data)
    print(json.dumps(dict(R=R, N=Nn, cst=cst, idle_nodes=stats['idle_nodes'], gates_A=len(A), gates_B=len(B), frames=len(frames), blocks=blocks,
                          scatter='table' if 'table' in scat else 'star', seconds=round(time.time() - t0, 1))))


if __name__ == '__main__':
    main()

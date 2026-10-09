#!/usr/bin/env python3
"""Exact-frame F2 network quotient of the pinned PR168 bit producer.

Author: GPT-6 Astra.
Source: eumemic's PR168, pinned fd25adb7, including its credited antecedents.
This is a new dirty-safe network construction screen, not a reuse of the
source's gauges or aliased role count.  Every common-frame vertex is completed
to an invertible row map; retired complementary rows finish at the full frame.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
import math
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
DEFAULT_SOURCE = HERE.parent / 'public' / 'pr168_fd25adb7'
PINNED_SOURCE = 'github:eumemic/integer-mult-bounds@fd25adb7fbaa12ee761d02c733c54d1d2a7687ee'


class F2Basis:
    def __init__(self, rows=()):
        self.pivot = {}
        self.rows = []
        for x in rows:
            self.add(x)

    def reduce(self, x):
        while x:
            p = x.bit_length() - 1
            if p not in self.pivot:
                break
            x ^= self.pivot[p]
        return x

    def add(self, x):
        y = self.reduce(x)
        if y:
            self.pivot[y.bit_length() - 1] = y
            self.rows.append(x)
            return True
        return False

    def __len__(self):
        return len(self.rows)


def positive(counter):
    return {str(r): n for r, n in sorted(counter.items()) if r and n}


def exponent(W, m, children):
    def residue(a):
        return sum(c * (r / m) ** (1 - a) for r, c in children.items() if r) - W
    lo, hi = 0.0, 0.1
    assert residue(lo) < 0 < residue(hi)
    for _ in range(70):
        mid = (lo + hi) / 2
        if residue(mid) < 0:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def expressions(rows):
    """Return exact input-index expressions, or fail on an outside row."""
    pivots = {}
    for i, row in enumerate(rows):
        x, coeff = row, 1 << i
        while x:
            p = x.bit_length() - 1
            if p not in pivots:
                pivots[p] = (x, coeff)
                break
            y, c = pivots[p]
            x ^= y
            coeff ^= c
    def express(row):
        x, coeff = row, 0
        while x:
            p = x.bit_length() - 1
            assert p in pivots, 'Requested fresh form outside available span'
            y, c = pivots[p]
            x ^= y
            coeff ^= c
        return coeff
    return express


def aligned_rewrite(chk, edge_requests, root_requests, injections, dim):
    """Replace A(selector0) and G(selectors1,2) by source K-pair sums.

    Unchanged operands merely passing through a replaced frame are bypassed
    along their already nested path.  Dead requests are then pruned backwards.
    The fixed higher-dimensional query modules and all root forms are kept.
    """
    g, w = chk.g, chk.w
    edges = {e: list(rows) for e, rows in edge_requests.items()}
    original_edges = {e: F2Basis(rows).rows for e, rows in edges.items()}
    original_injections = {v: list(rows) for v, rows in injections.items()}
    candidate = defaultdict(list)
    for (u, _), rows in edges.items():
        if dim(u) == 3:
            for row in rows:
                if row.bit_count() == 4:
                    candidate[row].append(u)
    by_cube = defaultdict(dict)
    for i, label in enumerate(g['labels']):
        cube = tuple(c // 2 for c in label)
        bits = tuple(c % 2 for c in label)
        by_cube[cube][bits] = i
    pair_info = {}
    for entry in chk.k['entries']:
        a, b = entry['carrier'], entry['passive']
        pair_info[(1 << a) | (1 << b)] = (entry['mix_frame'], a, b)
    modules = []
    for cube, indices in sorted(by_cube.items()):
        for value in range(2):
            a_mask = sum(1 << i for bits, i in indices.items() if bits[0] == value)
            g_mask = sum(1 << i for bits, i in indices.items() if bits[1] ^ bits[2] == value)
            modules.extend([('A0', cube, a_mask), ('G12', cube, g_mask)])
    controls = defaultdict(set)
    replaced, bypassed = Counter(), 0
    for kind, cube, mask in modules:
        assert candidate[mask]
        vertex = min(candidate[mask])  # phase, then exact frame
        assert not root_requests.get(vertex)
        incoming = [(u, row) for (u, v), rows in edges.items() if v == vertex for row in rows]
        parent_of = {}
        for u, row in incoming:
            assert row not in parent_of
            parent_of[row] = u
        reroute = []
        for (u, v), rows in list(edges.items()):
            if u != vertex:
                continue
            keep = []
            for row in rows:
                if row == mask:
                    keep.append(row)
                else:
                    assert row in parent_of, (kind, cube, 'Nontrivial passthrough')
                    reroute.append((parent_of[row], v, row))
                    bypassed += 1
            if keep:
                edges[u, v] = keep
            else:
                del edges[u, v]
        for edge in [e for e in edges if e[1] == vertex]:
            del edges[edge]
        for u, v, row in reroute:
            assert dim(u) <= dim(v) and u[0] <= v[0]
            edges.setdefault((u, v), []).append(row)
        pairs = [p for p in pair_info if p & mask == p]
        assert len(pairs) == 2 and pairs[0] ^ pairs[1] == mask
        for pair in pairs:
            f, a, b = pair_info[pair]
            source_vertex = (vertex[0], f)
            controls[source_vertex].update([1 << a, 1 << b])
            edges.setdefault((source_vertex, vertex), []).append(pair)
        replaced[kind] += 1

    edges = {e: F2Basis(rows).rows for e, rows in edges.items()}
    incoming = defaultdict(list)
    for (u, v), rows in edges.items():
        incoming[v].extend((u, row) for row in rows)
    vertices = set(incoming) | set(injections) | set(root_requests) | set(controls)
    vertices |= {u for u, _ in edges}
    wanted_out = defaultdict(list)
    live_edges = defaultdict(list)
    live_injections = defaultdict(list)
    for vertex in sorted(vertices, key=lambda x: (x[0], dim(x), x), reverse=True):
        wanted = wanted_out[vertex] + root_requests.get(vertex, [])
        if not wanted:
            continue
        free = sorted(controls.get(vertex, ()))
        inc = incoming[vertex]
        source = injections.get(vertex, [])
        rows = free + [row for _, row in inc] + source
        express = expressions(rows)
        needed = 0
        for row in wanted:
            needed |= express(row)
        needed >>= len(free)
        for i, (parent, row) in enumerate(inc):
            if needed >> i & 1:
                live_edges[parent, vertex].append(row)
                wanted_out[parent].append(row)
        for i, row in enumerate(source):
            if needed >> (len(inc) + i) & 1:
                live_injections[vertex].append(row)
    def high_interface(edge_map):
        return Counter((u, v, row) for (u, v), rows in edge_map.items()
                       if dim(v) > 3 for row in rows)
    before_interface = high_interface(original_edges)
    after_interface = high_interface(live_edges)
    assert before_interface == after_interface, 'High boundary changed'

    def rank3_counts(edge_map):
        inc, out = defaultdict(list), defaultdict(list)
        for (u, v), rows in edge_map.items():
            out[u].extend(rows)
            inc[v].extend(rows)
        counts = {}
        for vertex in set(inc) | set(out):
            if dim(vertex) != 3:
                continue
            C, D = inc[vertex], out[vertex]
            n, d, t, r = len(C), len(F2Basis(C)), len(D), len(F2Basis(D))
            b = max(0, t + d - r - n)
            counts[vertex] = (n, d, t, r, b, n + b - t)
        return counts
    before_rank3 = rank3_counts(original_edges)
    after_rank3 = rank3_counts(live_edges)
    assert before_rank3 == after_rank3, 'Rank3 boundary resource counts changed'
    def low_histogram(edge_map, source_map, control_map):
        inc, out = defaultdict(list), defaultdict(list)
        for (u, v), rows in edge_map.items():
            out[u].extend(rows)
            inc[v].extend(rows)
        result = Counter()
        for vertex in set(inc) | set(out) | set(source_map):
            if dim(vertex) > 3:
                continue
            C = inc[vertex] + source_map.get(vertex, [])
            D = out[vertex]
            E = list(control_map.get(vertex, ()))
            e = len(F2Basis(E))
            n, t = len(C), len(D)
            d, r = len(F2Basis(E + C)) - e, len(F2Basis(E + D)) - e
            b = max(0, t + d - r - n)
            result[dim(vertex)] += b + len(source_map.get(vertex, []))
            result[chk.h - dim(vertex)] += n + b - t
        for (u, v), rows in edge_map.items():
            if dim(v) <= 3:
                result[dim(v) - dim(u)] += len(rows)
        return result
    before_low = low_histogram(original_edges, original_injections, {})
    after_low = low_histogram(live_edges, live_injections, controls)
    low_delta = {str(d): after_low[d] - before_low[d]
                 for d in sorted(set(before_low) | set(after_low))
                 if d and after_low[d] != before_low[d]}
    interface_bytes = json.dumps(sorted((u, v, hex(row), count)
                                       for (u, v, row), count in before_interface.items()),
                                 separators=(',', ':')).encode()
    return live_edges, live_injections, controls, dict(
        modules=dict(replaced), bypassed_passthrough_requests=bypassed,
        paid_source_control_vertices=len(controls),
        old_edges=len(edge_requests), rewritten_edges=len(edges),
        pruned_edges=len(edges) - len(live_edges),
        exact_high_boundary_and_suffix_unchanged=True,
        high_boundary_and_suffix_forms=sum(before_interface.values()),
        high_boundary_and_suffix_sha256=hashlib.sha256(interface_bytes).hexdigest(),
        exact_rank3_resource_counts_unchanged=True,
        rank3_vertices=len(before_rank3),
        exact_low_histogram_delta=low_delta)


def build(source, phased_reads=False, source_aligned=False):
    assert not source_aligned or phased_reads
    sys.path.insert(0, str(source / 'scripts'))
    import paired_cube_bit_physical as P
    chk = P.loaded()
    g, w, h, v = chk.g, chk.w, chk.h, chk.v
    frame_dimensions = {int(f): r['dim'] for f, r in chk.fr['frames'].items()}
    def key(phase, f):
        return (phase, f) if phased_reads else f
    def dim(f):
        return frame_dimensions[f[1] if phased_reads else f]
    full = w['full_frame']
    ops = w['ops']
    opf = w['op_frame']
    rootroles = w['rootroles']
    R0 = 1 + max(max(a, b) for a, b, _ in ops)
    sources = {int(x): r for x, r in w['sources'].items()}
    content = [0] * R0
    current = [None] * R0
    injections = defaultdict(list)
    for leaf, role in sources.items():
        content[role] = 1 << leaf
        current[role] = key(0, w['source_frame'][leaf])
        injections[current[role]].append(1 << leaf)

    # An edge request records the exact fresh form which physically traversed
    # the old edge.  Equal-frame operations are contracted at the vertex.
    edge_requests = defaultdict(list)
    pset = set(w['phase1'])
    order = sorted(pset) + [i for i in range(len(ops)) if i not in pset]
    def move(role, f):
        p = current[role]
        if p is not None and p != f and content[role]:
            assert dim(p) <= dim(f), (p, f)
            if not phased_reads:
                assert dim(p) < dim(f), (p, f)
            else:
                assert p[0] <= f[0], (p, f)
            edge_requests[p, f].append(content[role])
        current[role] = f
    for i in order:
        a, b, _ = ops[i]
        f = key(0 if i in pset else 1, opf[i])
        move(a, f)
        move(b, f)
        assert not content[a] & content[b]
        content[a] ^= content[b]

    root_requests = defaultdict(list)
    center_requests = defaultdict(list)
    for root, role, f in zip(g['roots'], rootroles, w['root_frame']):
        f = key(0 if root['kind'] == 'center' else 1, f)
        move(role, f)
        root_requests[f].append(content[role])
        if root['kind'] == 'center':
            center_requests[f].append(content[role])

    controls, rewrite = {}, None
    if source_aligned:
        edge_requests, injections, controls, rewrite = aligned_rewrite(
            chk, edge_requests, root_requests, injections, dim)
    # Only a basis traverses each exact U -> V edge; V reconstructs all scalar
    # expressions it needs.  Equal frames are literal IDs, not equal dimensions.
    edge_bases = {e: F2Basis(rows).rows for e, rows in edge_requests.items()}
    roots = {f: F2Basis(rows).rows for f, rows in root_requests.items()}
    inc, out = defaultdict(list), defaultdict(list)
    for (u, f), rows in edge_bases.items():
        out[u].extend(rows)
        inc[f].extend(rows)
    frames = set(inc) | set(out) | set(injections) | set(roots)
    local = Counter()
    source_births = sum(map(len, injections.values()))
    role_births = source_births
    stats = []
    for f in sorted(frames, key=lambda x: ((x[0] if phased_reads else 0), dim(x), x)):
        C = inc[f] + injections[f]
        D = out[f] + ([] if phased_reads else roots.get(f, []))
        free = sorted(controls.get(f, ()))
        free_rank = len(F2Basis(free))
        basis = F2Basis(free + C)
        n, d, t, r = len(C), len(basis) - free_rank, len(D), len(F2Basis(free + D)) - free_rank
        assert all(basis.reduce(row) == 0 for row in D), f
        assert all(basis.reduce(row) == 0 for row in roots.get(f, [])), f
        births = max(0, t + d - r - n)
        retired = n + births - t
        assert retired >= d - r
        role_births += births
        local[dim(f)] += births + len(injections[f])
        # The roots are held at U until every center scatter at target zero has
        # completed, then read in the original side chronology, then completed.
        tails = retired + (0 if phased_reads else len(roots.get(f, [])))
        local[h - dim(f)] += tails
        stats.append(dict(frame=f, dim=dim(f), incoming=n, input_rank=d,
                          outgoing=t, output_rank=r, births=births,
                          retired=retired, roots=len(roots.get(f, [])),
                          external_source_control_rank=free_rank))
    for (u, f), rows in edge_bases.items():
        local[dim(f) - dim(u)] += len(rows)

    loss = 0
    for f, rows in center_requests.items():
        rank = len(F2Basis(rows))
        loss += dim(f) * rank
        local[dim(f)] += rank
    assert sum(r * c for r, c in local.items()) == h * role_births + loss

    # Original-source partner mixer stays literal; there are no inherited
    # gauges, so side target chains start from frame zero.
    reference = json.loads((source / 'certificates' /
                            'paired-cube-bit-physical-input.json').read_text())
    source_hist = Counter({int(r): c for r, c in reference['source_data_histogram'].items()})
    target = Counter()
    target_dim = [0] * v
    for root, f in zip(g['roots'], w['root_frame']):
        if root['kind'] == 'side':
            for target_index in root['targets']:
                assert frame_dimensions[f] >= target_dim[target_index]
                target[frame_dimensions[f] - target_dim[target_index]] += 1
                target_dim[target_index] = frame_dimensions[f]
    for d0 in target_dim:
        target[h - 1 - d0] += 1
    assert sum(r * c for r, c in target.items()) == (h - 1) * v
    children = Counter()
    for part in (local, source_hist, target):
        for r, c in part.items():
            if r:
                children[r] += 3 * c
    children[2] += 2 * v
    W, m = 2 * v + role_births, 3 * h
    delta = m * W - sum(r * c for r, c in children.items())
    assert delta == 2 * v - 3 * loss
    reference_children = Counter({int(r): c for r, c in reference['child_histogram'].items()})
    combined = None
    if source_aligned:
        last = {}
        for i in order:
            for s in ops[i][:2]:
                last[s] = i
        donor_dims = Counter(frame_dimensions[opf[last[a]]] for a, _ in w['pairs'])
        assert min(donor_dims) >= 3
        # Fixed high-boundary completion: all high gauges and the existing
        # alias matching remain.  The exact rank2 retirees removed below are
        # unpaired; rank3 complement rows stay at the same boundary frames.
        removed = reference['R'] - role_births
        assert removed == rewrite['modules']['A0'] == 440
        local_delta = Counter({int(d): n for d, n in rewrite['exact_low_histogram_delta'].items()})
        assert dict(local_delta) == {1: -4 * removed, 2: removed, h - 2: -removed}
        new_children = Counter(reference_children)
        for width, count in local_delta.items():
            new_children[width] += 3 * count
        new_W = reference['W_per_vertex'] - removed
        new_R = reference['physical_R'] - removed
        assert all(c > 0 for c in new_children.values())
        assert new_W * m - sum(r * c for r, c in new_children.items()) == delta
        combined = dict(
            contract='Preserve exact high-boundary forms, high query word, all gauges and all reuse pairs; recompute nongauged entrance response for the new X-controlled low word',
            physical_R=new_R, W=new_W, m=m, delta=delta,
            retained_gauges=len(w['gauges']), retained_pairs=len(w['pairs']),
            original_paired_donor_terminal_dimensions=positive(donor_dims),
            paired_donors_deleted=0, removed_rank2_retirees=removed,
            local_histogram_delta={str(d): n for d, n in sorted(local_delta.items())},
            child_histogram=positive(new_children),
            kappa_coarse=exponent(new_W, m, new_children),
            entropy=sum(c * r * math.log(m / r) for r, c in new_children.items()))
    inputs = ['research/paired-cube-bit/out/graph_p12.json',
              'research/paired-cube-bit/out/profile_p12.json',
              'references/paired-cube/bit-physical/word_p12.json.gz',
              'references/paired-cube/bit-physical/frames_p12.json.gz',
              'references/paired-cube/bit-physical/kchron_p12.json',
              'certificates/paired-cube-bit-physical-input.json']
    return dict(author='GPT-6 Astra', source=PINNED_SOURCE, h=h, v=v,
                construction=('Top-level quantities describe the unselected exact-frame comparison without gauges or reuse; '
                              'the selected production construction preserves the pinned gauges and reuse through the fixed-boundary lemma '
                              'and is recorded in combined_fixed_boundary_profile' if combined is not None else
                              'Unselected exact-frame network comparison; minimum invertible dirty lifts and edge bases, without gauges or reuse'),
                comparison_scope=('unselected zero-gauge comparison only; selected production profile is combined_fixed_boundary_profile'
                                  if combined is not None else 'unselected zero-gauge comparison only'),
                selected_profile='combined_fixed_boundary_profile' if combined is not None else None,
                phased_direct_reads=phased_reads,
                source_aligned_rewrite=rewrite,
                aux_source_births=source_births,
                vertices=len(frames), distinct_edges=len(edge_bases),
                edge_requests=sum(map(len, edge_requests.values())),
                edge_rank=sum(map(len, edge_bases.values())),
                held_root_requests=sum(map(len, root_requests.values())),
                held_root_rank=sum(map(len, roots.values())),
                root_queries_stored=not phased_reads,
                incoming_nullity=sum(s['incoming'] - s['input_rank'] for s in stats),
                added_births=sum(s['births'] for s in stats),
                retired_fresh_complements=sum(s['input_rank'] - s['output_rank'] for s in stats),
                retired_zero_fresh_kernel=sum(s['retired'] - s['input_rank'] + s['output_rank'] for s in stats),
                R=role_births, W=W, m=m, loss=loss, delta=delta,
                local_histogram=positive(local), source_histogram=positive(source_hist),
                target_histogram=positive(target), child_histogram=positive(children),
                kappa_coarse=exponent(W, m, children),
                entropy=sum(c * r * math.log(m / r) for r, c in children.items()),
                reference_R=reference['physical_R'],
                reference_kappa_coarse=exponent(reference['W_per_vertex'], m, reference_children),
                combined_fixed_boundary_profile=combined,
                source_sha256={p: hashlib.sha256((source / p).read_bytes()).hexdigest() for p in inputs},
                stats=stats)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=DEFAULT_SOURCE)
    parser.add_argument('--phased-reads', action='store_true', help='Keep center cut; evaluate every read directly from incoming rows at its phase/frame vertex')
    parser.add_argument('--source-aligned', action='store_true', help='Align A0 and G12 with paid source K pair planes; implies --phased-reads')
    parser.add_argument('--compact', action='store_true', help='Omit regenerable per-vertex statistics from the output JSON')
    parser.add_argument('--output', type=Path, default=HERE / 'common_frame_network.json')
    args = parser.parse_args()
    result = build(args.source.resolve(), args.phased_reads or args.source_aligned, args.source_aligned)
    if args.compact:
        result.pop('stats', None)
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: v for k, v in result.items() if k != 'stats'}, indent=2))


if __name__ == '__main__':
    main()

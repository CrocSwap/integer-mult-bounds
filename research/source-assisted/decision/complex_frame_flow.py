#!/usr/bin/env python3
"""Price equal-frame fresh-channel compression of the pinned complex word.

New work for icekylinx, GPT-6 Astra, 2026-10-09.  The input program and its
physical frames/reuse are PR168 fd25adb7 (eumemic, Claude assistance), built
on the retained icekylinx/GPT-6 Astra paired producer; no input is modified.

This first pass computes modular ranks and is a decision screen.  It is
not an invertible-completion certificate or an assembled supplier.
"""
from __future__ import annotations
from collections import Counter, defaultdict
from functools import lru_cache
from pathlib import Path
import argparse
import hashlib
import json
import math
import sys
import time


def read(path):
    return json.loads(path.read_text())


def frame_basis(rows):
    b = {}
    for x in rows:
        for p, y in sorted(b.items(), reverse=True):
            if x >> p & 1:
                x ^= y
        if x:
            p = x.bit_length() - 1
            for k, y in list(b.items()):
                if y >> p & 1:
                    b[k] = y ^ x
            b[p] = x
    return tuple(b[p] for p in sorted(b, reverse=True))


@lru_cache(maxsize=None)
def perpendicular(rows, h):
    rows = frame_basis(rows)
    piv = {r.bit_length() - 1: r for r in rows}
    out = []
    for j in range(h):
        if j in piv:
            continue
        x = 1 << j
        for p, r in piv.items():
            if r >> j & 1:
                x |= 1 << p
        out.append(x)
    return frame_basis(out)


@lru_cache(maxsize=None)
def contained(a, b):
    return len(frame_basis(a + b)) == len(b)


class Vectors:
    def __init__(self):
        self.rows = [()]
        self.ids = {(): 0}

    def intern(self, row):
        row = tuple(sorted((k, v) for k, v in row.items() if v)) if isinstance(row, dict) else row
        if row not in self.ids:
            self.ids[row] = len(self.rows)
            self.rows.append(row)
        return self.ids[row]

    def add(self, a, b, ca=1, cb=1):
        row = {k: ca*v for k, v in self.rows[a]}
        for k, v in self.rows[b]:
            x = row.get(k, 0) + cb*v
            if x:
                row[k] = x
            else:
                row.pop(k, None)
        return self.intern(row)


def build_flow(tree, cache, purify_source_donors=False):
    g, witness, word = (read(cache / name) for name in ('graph.json', 'frames.json', 'selection.json'))
    h, v = g['h'], g['v']
    ops, coef = word['ops'], word['opcoeff']
    pin = tree / 'references/paired-cube/physical'
    pairs_in = read(pin / 'pairs.json')['pairs']
    merge = {b: a for a, b, _ in pairs_in}
    deadline = {b: t for _, b, t in pairs_in}
    alias = lambda s: merge.get(s, s)
    R = max(max(a, b) for a, b, _ in ops) + 1
    selected = {z['role']: z for z in word['selected']}
    assert set(selected) == set(merge), 'This screen requires no live external gauges.'
    phase1 = sorted(word['phase1'])
    pset = set(phase1)
    rest = [i for i in range(len(ops)) if i not in pset]
    frames = [perpendicular(tuple(witness['annihilators'][x]), h) for _, _, x in ops]
    for i, U in read(pin / 'frames.json')['frames']:
        frames[i] = tuple(U)
    inputs = g['inputs']
    source = {int(x): s for x, s in word['sources'].items()}
    roots = g['roots']
    args = g['args']
    spans = [(q,) for q in inputs]
    for a in args[v:]:
        spans.append(frame_basis(spans[a[0]] + spans[a[1]]))
    root_frames = [spans[r['node']] if r['kind'] == 'center' else
                   perpendicular(frame_basis(inputs[t] for t in r['targets']), h) for r in roots]
    vec = Vectors()
    current = [0] * R
    location = [None] * R
    edge_values = defaultdict(set)
    sources = defaultdict(list)
    reads = defaultdict(list)
    nodes = set()
    original_crossings = 0
    source_controls = {}
    erasures = []
    erase_after = defaultdict(list)
    if purify_source_donors:
        parity_frames=[]
        for cube in range(v//8):
            for parity in range(2):
                ids=tuple(8*cube+j for j in range(8) if j.bit_count()%2==parity)
                S=frame_basis(inputs[j] for j in ids)
                assert len(S)==3
                parity_frames.append((S,ids))
        order=phase1+rest
        position={i:k for k,i in enumerate(order)}
        last={}
        for i in order:
            aa,bb,_=ops[i];last[aa]=last[bb]=i
        for aa,bb,_ in pairs_in:
            U=frames[last[aa]]
            if len(U)>3:continue
            V=perpendicular(tuple(selected[bb]['annihilator']),h)
            for S,ids in parity_frames:
                if contained(U,S) and contained(S,V):
                    erase_after[last[aa]].append((aa,bb,S,ids))
                    break

    def move(s, node):
        nonlocal original_crossings
        s = alias(s)
        prev = location[s]
        nodes.add(node)
        if prev != node:
            if prev is not None:
                assert prev[0] <= node[0] and contained(prev[1], node[1]), (s, prev, node)
                original_crossings += 1
                if current[s]:
                    edge_values[prev, node].add(current[s])
            location[s] = node
        return s

    for x, s in source.items():
        s = alias(s)
        assert location[s] is None and not current[s]
        node = (1, (inputs[x - 1],))
        nodes.add(node)
        value = vec.intern(((x - 1, 1),))
        sources[node].append(value)
        current[s], location[s] = value, node

    def gate(i, phase):
        a, b, _ = ops[i]
        node = (phase, frames[i])
        aa, bb = move(a, node), move(b, node)
        assert aa != bb
        current[aa] = vec.add(current[aa], current[bb], *coef[i])
        for donor,recipient,S,ids in erase_after[i]:
            slot=move(donor,(phase,S))
            value=current[slot]
            assert all(j in ids for j,c in vec.rows[value])
            source_controls[phase,S]=ids
            erasures.append(dict(operation=i,donor=donor,recipient=recipient,
                                 phase=phase,frame=list(S),source_ports=list(ids),value=value))
            current[slot]=0

    def read_role(s, U, phase, kind, ref):
        node = (phase, U)
        s = move(s, node)
        reads[node].append((kind, ref, current[s]))

    for i in phase1:
        gate(i, 1)
    for j, (r, s) in enumerate(zip(roots, word['rootroles'])):
        if r['kind'] == 'center':
            read_role(s, root_frames[j], 1, 'center', j)
    late = defaultdict(list)
    for s in reversed([z['role'] for z in word['selected']]):
        U = perpendicular(tuple(selected[s]['annihilator']), h)
        if deadline[s] is None:
            read_role(s, U, 2, 'deferred', s)
        else:
            late[deadline[s]].append(s)
    for i in rest:
        for s in late[i]:
            U = perpendicular(tuple(selected[s]['annihilator']), h)
            read_role(s, U, 2, 'deferred', s)
        gate(i, 2)
    for j, (r, s) in enumerate(zip(roots, word['rootroles'])):
        if r['kind'] == 'side':
            read_role(s, root_frames[j], 2, 'side', j)
    # No value is discarded: complements of outgoing fresh row spaces retire
    # to the common full frame in the new invertible local maps.
    return dict(g=g, vec=vec, nodes=nodes, edges=edge_values, sources=sources,
                reads=reads, original_crossings=original_crossings,
                original_physical_roles=R - len(merge), raw_R=R,
                source_controls=source_controls,erasures=erasures)


class Ranker:
    def __init__(self, vectors, prime):
        self.vec, self.prime = vectors, prime
        self.cache = {}

    def basis(self, ids):
        ids = tuple(sorted(set(ids) - {0}, key=lambda x: (len(self.vec.rows[x]), x)))
        if ids in self.cache:
            return self.cache[ids]
        p, pivots, chosen = self.prime, {}, []
        for ident in ids:
            row = {k: v % p for k, v in self.vec.rows[ident] if v % p}
            while row:
                col = min(row)
                if col not in pivots:
                    inv = pow(row[col], -1, p)
                    pivots[col] = {k: a*inv % p for k, a in row.items()}
                    chosen.append(ident)
                    break
                f = row[col]
                for k, a in pivots[col].items():
                    x = (row.get(k, 0) - f*a) % p
                    if x:
                        row[k] = x
                    else:
                        row.pop(k, None)
        self.cache[ids] = tuple(chosen)
        return tuple(chosen)


def price(flow, baseline, prime=1000003, recycle_kernels=False, fixed_kernel_pairs=None):
    g, h, v = flow['g'], flow['g']['h'], flow['g']['v']
    ranker = Ranker(flow['vec'], prime)
    incoming, outgoing = defaultdict(list), defaultdict(list)
    H = Counter({1: v})
    edge_hist = Counter()
    edge_raw = edge_rank = 0
    examples = []
    compressed_edges = []
    for (U, V), values in sorted(flow['edges'].items()):
        basis = ranker.basis(values)
        incoming[V].extend(basis)
        outgoing[U].extend(basis)
        width = len(V[1]) - len(U[1])
        assert width >= 0
        H[width] += len(basis)
        edge_hist[len(values) - len(basis)] += 1
        edge_raw += len(values)
        edge_rank += len(basis)
        compressed_edges.append((U, V, basis))
        if len(values) > len(basis):
            examples.append(dict(source=[U[0], list(U[1])], target=[V[0], list(V[1])],
                                 requested=len(values), rank=len(basis), width=width,
                                 saving=(len(values)-len(basis))*width,
                                 vectors=sorted(values), basis=list(basis)))
    R = v
    births = Counter()
    retirements = Counter()
    node_records = []
    dependent_in = dependent_out = 0
    for U in sorted(flow['nodes']):
        ins = incoming[U] + flow['sources'].get(U, [])
        outs = outgoing[U]
        n, t = len(ins), len(outs)
        db = ranker.basis(ins)
        rb = ranker.basis(outs)
        d, r = len(db), len(rb)
        required = outs + [q[2] for q in flow['reads'].get(U, [])]
        controls=flow.get('source_controls',{}).get(U,())
        if controls:
            # At the already charged original-X parity frame every fresh
            # form here is directly available.  Erase the incoming fresh
            # parts, apply an invertible dirty-row map, then inject the
            # requested outgoing parts using X controls.  The fresh quotient
            # modulo those external controls is zero.
            assert all(j in controls for ident in ins+required for j,c in flow['vec'].rows[ident])
            d=r=0
        else:
            assert len(ranker.basis(ins + required)) == d, ('Output outside incoming fresh span', U)
        b = max(0, t + d - r - n)
        retired = n + b - t
        assert retired >= d-r
        R += b
        H[len(U[1])] += b
        H[h-len(U[1])] += retired
        births[(U[0], len(U[1]))] += b
        retirements[(U[0], len(U[1]))] += retired
        dependent_in += n-d
        dependent_out += t-r
        node_records.append(dict(frame=[U[0], list(U[1])], n=n, d=d, t=t, r=r,
                                 new_dirty=b, retired=retired,
                                 inputs=ins, outputs=outs,
                                 source_controls=list(controls),
                                 ambient_input_rank=len(db),ambient_output_rank=len(rb),
                                 read_values=[q[2] for q in flow['reads'].get(U, [])],
                                 reads=[dict(kind=kind,ref=ref,value=value) for kind,ref,value in flow['reads'].get(U, [])]))
    kernel_pairs=[]
    if recycle_kernels:
        import numpy as np
        from scipy.sparse import csr_matrix
        from scipy.sparse.csgraph import maximum_bipartite_matching
        donors=[]
        recipients=[]
        for i,q in enumerate(node_records):
            donors.extend((i,j) for j in range(q['retired']-(q['d']-q['r'])))
            recipients.extend((i,j) for j in range(q['new_dirty']))
        recipients.sort(key=lambda ij:(len(node_records[ij[0]]['frame'][1]),
                                       node_records[ij[0]]['frame'][0],ij))
        groups=defaultdict(list)
        for col,(i,j) in enumerate(recipients):groups[i].append(col)
        indices=[];indptr=[0];compatible_cache={}
        for i,j in donors:
            if i not in compatible_cache:
                p0,U=node_records[i]['frame'];U=tuple(U)
                compatible_cache[i]=[col for k,cols in groups.items()
                                     if p0<=node_records[k]['frame'][0]
                                     and i!=k and contained(U,tuple(node_records[k]['frame'][1]))
                                     for col in cols]
            indices.extend(compatible_cache[i]);indptr.append(len(indices))
        if fixed_kernel_pairs is not None:
            kernel_pairs=[list(q) for q in fixed_kernel_pairs]
        elif donors and recipients:
            mat=csr_matrix((np.ones(len(indices),dtype=np.int8),np.asarray(indices,dtype=np.int32),
                            np.asarray(indptr,dtype=np.int32)),shape=(len(donors),len(recipients)))
            matched=maximum_bipartite_matching(mat,perm_type='column')
            for left,right in enumerate(matched):
                if right<0:continue
                i,j=donors[left];k,l=recipients[right]
                kernel_pairs.append([i,j,k,l])
        for i,j,k,l in kernel_pairs:
            u=len(node_records[i]['frame'][1]);vv=len(node_records[k]['frame'][1])
            H[h-u]-=1;H[vv]-=1;H[vv-u]+=1;R-=1
        assert min(H.values())>=0
    ell = baseline['loss']
    for U, reads in flow['reads'].items():
        H[len(U[1])] += sum(q[0] == 'center' for q in reads)
    assert sum(k*c for k, c in H.items()) == h*R+ell
    H = Counter({k:c for k,c in H.items() if k and c})
    source = {int(k): c for k,c in baseline['source_data_histogram'].items()}
    # Target accounting is retained from the layer BEFORE terminal-sink
    # substitutions. The newly compiled auxiliary circuit does not consume Y.
    target = {0:6270, 1:3*v, h-4:v}
    C = Counter({k:3*c for k,c in H.items()})
    C.update({k:3*c for k,c in source.items() if k})
    C.update({k:3*c for k,c in target.items() if k})
    C[2] += 2*v
    m, W = 3*h, 2*v+R
    cap = m*W
    mass = sum(k*c for k,c in C.items())
    delta = cap-mass
    assert delta == 2*v-3*ell
    lo, hi = 0., .01
    for _ in range(70):
        a = (lo+hi)/2
        if math.fsum(c*k*(m/k)**a for k,c in C.items()) < cap:
            lo = a
        else:
            hi = a
    entropy = math.fsum(c*k*math.log(m/k) for k,c in C.items())
    baseC = {int(k):c for k,c in baseline['child_histogram'].items()}
    baseE = math.fsum(c*k*math.log(m/k) for k,c in baseC.items())
    result = dict(h=h,v=v,field_prime=prime,frames=len(flow['nodes']),
        vectors=len(flow['vec'].rows), original_physical_roles=flow['original_physical_roles'],
        original_role_crossings=flow['original_crossings'], edge_distinct_values=edge_raw,
        edge_basis_values=edge_rank, edge_removed_values=edge_raw-edge_rank,
        edge_nullity_histogram=dict(sorted(edge_hist.items())),
        incoming_dependencies=dependent_in,outgoing_dependencies=dependent_out,
        source_control_erasures=len(flow.get('erasures',[])),
        kernel_reuses=len(kernel_pairs),
        new_R=R,new_W=W,loss=ell,deficit=delta,
        local_histogram=dict(sorted(H.items())),child_histogram=dict(sorted(C.items())),
        entropy=entropy,baseline_entropy=baseE,entropy_ratio=entropy/baseE,
        numerical_local_root=lo,
        birth_histogram={f'{p}:{r}':c for (p,r),c in sorted(births.items()) if c},
        retirement_histogram={f'{p}:{r}':c for (p,r),c in sorted(retirements.items()) if c},
        status='Modular equal-frame flow price, retaining dirty kernel lifts and complete full-frame cleanup. Not an exact supplier certificate.')
    witness = dict(nodes=node_records,
                   edges=[dict(source=[U[0],list(U[1])],target=[V[0],list(V[1])],basis=list(bs))
                          for U,V,bs in compressed_edges],
                   vectors=flow['vec'].rows,
                   original_source_ports=g['inputs'],
                   source_erasures=flow.get('erasures',[]),kernel_pairs=kernel_pairs,
                   reductions=sorted(examples,key=lambda q:(-q['saving'],-q['requested'])))
    return result,witness


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--tree',type=Path,required=True)
    ap.add_argument('--cache',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--prime',type=int,default=1000003)
    ap.add_argument('--witness',action='store_true')
    ap.add_argument('--purify-source-donors',action='store_true')
    ap.add_argument('--recycle-kernels',action='store_true')
    ap.add_argument('--kernel-pairs',type=Path,help='JSON with a frozen kernel_pairs list; independently verified by the exact lift checker.')
    a=ap.parse_args()
    start=time.monotonic()
    flow=build_flow(a.tree,a.cache,a.purify_source_donors)
    print(json.dumps(dict(stage='flow',vectors=len(flow['vec'].rows),frames=len(flow['nodes']),
                          edges=len(flow['edges']),seconds=time.monotonic()-start)),flush=True)
    result,witness=price(flow,read(a.tree/'certificates/paired-cube-sinks-input.json'),a.prime,a.recycle_kernels,
                         read(a.kernel_pairs)['kernel_pairs'] if a.kernel_pairs else None)
    result['seconds']=time.monotonic()-start
    result['source_sha256']={str(p.relative_to(a.tree)):hashlib.sha256(p.read_bytes()).hexdigest()
                            for p in (a.tree/'references/paired-cube/physical/frames.json',
                                      a.tree/'references/paired-cube/physical/pairs.json')}
    result['cache_sha256']={name:hashlib.sha256((a.cache/name).read_bytes()).hexdigest()
                           for name in ('graph.json','frames.json','selection.json','record.json')}
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2)+'\n')
    if a.witness:
        a.out.with_suffix('.witness.json').write_text(json.dumps(witness,separators=(',',':'))+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    main()

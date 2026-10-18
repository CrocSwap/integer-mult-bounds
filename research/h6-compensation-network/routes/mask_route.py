#!/usr/bin/env python3
"""Exact actual compensation on two or four source-label fibers.

Observed incidence masks receive distinct targets, hence each target uses one
legal subspace. Helper lanes follow explicit Boolean-subset chains.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys
import numpy as np

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))
import fiber
from artifact import write_receipt


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--groups', type=int, choices=(2, 4), default=2)
    args = parser.parse_args()
    k = args.groups
    out = Path(__file__).resolve().parent
    roots, _, shell, profiles = fiber.e.construct_shell()
    P = shell[(profiles & 4) == 0, :16].astype(np.int64)
    _, packed, _ = fiber.e.binary_labels(roots, P)
    representatives = [0, 3, 12, 13][:k]
    words = [int(packed[i]) for i in representatives]
    fiber.require(len(fiber.basis(words)) == k, 'independent selected label fibers')
    groups = [np.flatnonzero(packed == word).tolist() for word in words]
    fiber.require(all(len(group) == 8 for group in groups), 'eight-source fibers')
    S = [source for group in groups for source in group]
    g_of_s = [g for g, group in enumerate(groups) for source in group]
    raw = P @ P[S].T
    fiber.require(np.all(raw % 4 == 0), 'exact integral pairings')
    t = raw // 4
    B = t & 1
    for g in range(k):
        fiber.require(np.all(B[:, g*8:(g+1)*8] == B[:, g*8:g*8+1]), 'fiber support identity')
    masks = sum(B[:, g*8] << g for g in range(k))
    T = np.flatnonzero(masks)
    C = (4*t[T] - t[T]**3).astype(np.int64)
    for row, target in enumerate(T):
        for source_col, source in enumerate(S):
            if target == source:
                C[row, source_col] += 48
    fiber.require(np.array_equal(C != 0, B[T] != 0), 'complete actual compensation support')
    target_masks = masks[T].astype(int)
    observed = sorted(set(target_masks.tolist()), key=lambda mask: (mask.bit_count(), mask))
    fiber.require(set(observed) == set(range(1, 1<<k)), 'all nonzero masks observed')
    frames_by_mask = {mask: fiber.basis(words[g] for g in range(k) if mask >> g & 1) for mask in observed}
    FULL = fiber.basis(1 << bit for bit in range(17))
    caps = {int(target): fiber.perp(int(packed[target])) for target in T}
    for target, mask in zip(T, target_masks):
        fiber.require(fiber.contained(frames_by_mask[int(mask)], caps[int(target)]), 'legal target mask frame')
    chains = []
    owners = {}
    for g in range(k):
        other = [j for j in range(k) if j != g]
        if k == 2:
            sets = [([], [other[0]])]
        else:
            a,b,c = other
            sets = [([], [a], [a,b], [a,b,c]), ([b], [b,c]), ([c], [a,c])]
        group_chains = [[(1<<g) | sum(1<<j for j in subset) for subset in chain] for chain in sets]
        for chain_index, chain in enumerate(group_chains):
            for mask in chain:
                fiber.require((g,mask) not in owners, 'disjoint chain cover')
                owners[g,mask] = chain_index
        fiber.require(set(mask for chain in group_chains for mask in chain) == {mask for mask in observed if mask>>g&1}, 'complete chain cover')
        chains.append(group_chains)
    width = 1 if k == 2 else 3
    # A middle-level antichain has width1 for B1 and width3 for B3;
    # the displayed covers attain it in this explicit mask-chain model.
    H = []
    lane_by_source_chain = {}
    for source_col,g in enumerate(g_of_s):
        for ci,chain in enumerate(chains[g]):
            lane_by_source_chain[source_col,ci] = len(H)
            H.append((source_col,g,chain))
    ns, nh, nt = len(S),len(H),len(T)
    starts = {f's{i}': fiber.basis([words[g_of_s[i]]]) for i in range(ns)}
    starts.update({f'h{i}': () for i in range(nh)})
    starts.update({f't{int(target)}': () for target in T})
    frames = dict(starts)
    paths = {r: [] for r in starts}
    hrows = np.concatenate((np.zeros((nh,ns),dtype=np.int64),np.eye(nh,dtype=np.int64)),axis=1)
    trows = np.zeros((nt,ns+nh),dtype=np.int64)
    dual = np.zeros((ns+nh,nt+ns+nh),dtype=np.int64)
    dual[:,:ns+nh] = 48*np.eye(ns+nh,dtype=np.int64)
    position = {int(target): row for row,target in enumerate(T)}
    events_count = 0
    digest = hashlib.sha256()
    network = out/f'MASK-{k}-NETWORK.jsonl'
    with network.open('w') as stream:
        def event(item):
            nonlocal events_count
            payload=json.dumps(item,sort_keys=True,separators=(',',':'))+'\n'
            stream.write(payload);digest.update(payload.encode());events_count+=1
            if item['op']=='climb':
                r=item['register'];f=tuple(item['frame'])
                fiber.require(f==fiber.basis(f),'canonical frame')
                fiber.require(fiber.contained(frames[r],f),'no ordinary descent')
                inc=len(f)-len(frames[r])
                if inc:paths[r].append(inc)
                frames[r]=f
                return
            dst,src,n,d=item['dst'],item['src'],item['numerator'],item['denominator']
            fiber.require(frames[dst]==frames[src],'equal-current-frame addition')
            if dst.startswith('t'):
                row,lane=position[int(dst[1:])],int(src[1:])
                fiber.require(d==48 and src.startswith('h'),'scatter format')
                trows[row]+=n*hrows[lane]
                dual[ns+lane,ns+nh+row]-=n
            else:
                lane,source=int(dst[1:]),int(src[1:])
                fiber.require(d==1 and dst.startswith('h') and src.startswith('s'),'gather format')
                hrows[lane,source]+=n
                dual[source]-=n*dual[ns+lane]
        def add(dst,src,n,d=1):event(dict(op='add',dst=dst,src=src,numerator=int(n),denominator=d))
        def climb(r,f):event(dict(op='climb',register=r,frame=list(f)))
        # Precompensate each selected helper's independent arbitrary dirt.
        for row,(target,mask) in enumerate(zip(T,target_masks)):
            for source_col,g in enumerate(g_of_s):
                if mask>>g&1:
                    lane=lane_by_source_chain[source_col,owners[g,int(mask)]]
                    add(f't{int(target)}',f'h{lane}',-C[row,source_col],48)
        # All copies of a source scalar are loaded at its initial line frame;
        # each ordinary dirty helper thereafter stays on one monotone chain.
        for lane,(source_col,g,chain) in enumerate(H):
            climb(f'h{lane}',fiber.basis([words[g]]))
            add(f'h{lane}',f's{source_col}',1)
        for source_col in range(ns):climb(f's{source_col}',FULL)
        for mask in observed:
            frame=frames_by_mask[mask]
            for lane,(_,g,chain) in enumerate(H):
                if mask in chain:climb(f'h{lane}',frame)
            for row in np.flatnonzero(target_masks==mask):
                target=int(T[row]);climb(f't{target}',frame)
                for source_col,g in enumerate(g_of_s):
                    if mask>>g&1:
                        lane=lane_by_source_chain[source_col,owners[g,mask]]
                        add(f't{target}',f'h{lane}',C[row,source_col],48)
                climb(f't{target}',caps[target])
        for lane,(source_col,g,chain) in enumerate(H):
            climb(f'h{lane}',FULL)
            add(f'h{lane}',f's{source_col}',-1)
    fiber.require(np.array_equal(trows[:,:ns],C) and not trows[:,ns:].any(),'actual forward block and zero dirt leakage')
    fiber.require(np.array_equal(hrows[:,:ns],np.zeros((nh,ns),dtype=np.int64)) and np.array_equal(hrows[:,ns:],np.eye(nh,dtype=np.int64)),'restored ordinary helpers')
    fiber.require(np.array_equal(dual[:,:ns+nh],48*np.eye(ns+nh,dtype=np.int64)),'dual arbitrary dirt restored')
    fiber.require(np.array_equal(dual[:ns,ns+nh:],-C.T) and not dual[ns:,ns+nh:].any(),'same-order dual actual block')
    fiber.require(all(frames[f's{i}']==FULL for i in range(ns)) and all(frames[f'h{i}']==FULL for i in range(nh)),'full source/helper endpoint')
    fiber.require(all(frames[f't{int(target)}']==caps[int(target)] for target in T),'target cap endpoint')
    pp=lambda role: [dict(path=list(path),count=count) for path,count in sorted(Counter(tuple(paths[r]) for r in paths if r.startswith(role)).items())]
    network_filename=fiber.compress_network(network)
    result=dict(status='PASS_COMPLETE_ACTUAL_MASK_ROUTE',groups=k,source_groups=groups,source_labels=words,
        source_ports=S,target_ports=T.tolist(),target_mask_counts=dict(Counter(target_masks.tolist())),
        coefficients_denominator=48,coefficient_numerators=C.tolist(),helper_count=nh,
        edge_baseline_helper_count=int(np.count_nonzero(C)),helper_lanes_per_source=width,
        chains=chains,source_paths=pp('s'),target_paths=pp('t'),helper_paths=pp('h'),
        total_local_transition_rank=sum(sum(p) for p in paths.values()),private_descent_rank=0,
        expanded_event_count=events_count,expanded_network_sha256=digest.hexdigest(),
        expanded_network_gzip_filename=network_filename,
        full_forward_and_same_order_dual_checks=True,
        source_sha256=hashlib.sha256(fiber.SOURCE.read_bytes()).hexdigest(),
        generator_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        scope='Complete actual I-K contribution of selected label-fiber columns, including all targets and exceptional pairs. Standalone exact scalar/frame word; no unpriced K composition, full supplier invoice, or kappa claim.',
        composition_caveat='Targets acquire different mask subspaces before their final caps. The unchanged K macro starts targets atzero and cannot simply follow this word; K must be fused with priced private center-copy chains or a different schedule.')
    write_receipt(out/f'MASK-{k}-RESULT.json', result, fields=['target_ports', 'coefficient_numerators'])
    print(json.dumps({key:result[key] for key in ('status','groups','helper_count','edge_baseline_helper_count','expanded_event_count','source_paths','target_paths','helper_paths','total_local_transition_rank')},sort_keys=True))


if __name__=='__main__':main()

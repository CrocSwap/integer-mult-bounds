#!/usr/bin/env python3
"""Certify fresh columns, read chronology, and normalize the complex profile.

New exact checker by GPT-6 Astra, for icekylinx, 2026-10-09.
The frozen query modules and physical baseline are credited to pinned
PR168 fd25adb7 and its retained predecessor notices. No floating-point or
modular arithmetic is used for an endpoint or frame identity.
"""
from __future__ import annotations
from collections import Counter, defaultdict
from pathlib import Path
import argparse
import gzip
import hashlib
import json
import math
import time

from complex_frame_flow import frame_basis, contained, perpendicular

ROOT = Path(__file__).resolve().parent.parent


def portable(p):
    p = Path(p).resolve()
    try:
        return str(p.relative_to(ROOT))
    except ValueError:
        return str(p)


def resolve_receipt_path(s):
    p = Path(s)
    return p if p.exists() else ROOT/p


def read(p):
    return json.loads(p.read_text())


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def add_scaled(dst, row, coefficient):
    for j, value in row.items():
        x = dst.get(j, 0)+coefficient*value
        if x:
            dst[j] = x
        else:
            dst.pop(j, None)


def validate(g, word, witness, actual_frames, pairs):
    h, v = g['h'], g['v']
    ports = g['inputs']
    assert ports == witness['original_source_ports']
    assert len(set(ports)) == v and all(q.bit_count() % 2 for q in ports)
    ops, coeff = word['ops'], word['opcoeff']
    R = max(max(a, b) for a,b,_ in ops)+1
    roots = g['roots']
    rootroles = word['rootroles']
    phase1 = set(word['phase1'])
    order = sorted(phase1)+[i for i in range(len(ops)) if i not in phase1]
    position = {i:k for k,i in enumerate(order)}
    last, first = {}, {}
    for i in order:
        a,b,_ = ops[i]
        first.setdefault(a,i); first.setdefault(b,i)
        last[a] = last[b] = i
    selected = {s['role']:s for s in word['selected']}
    alias = {b:a for a,b,_ in pairs}
    deadlines = {b:t for a,b,t in pairs}
    assert set(alias) == set(selected)
    # Selected deferred roles have no copied-center response. All their
    # compensation is an ordinary signed target row, scaled by 2 below.
    center = [{} for _ in range(R)]
    side = [{} for _ in range(R)]
    for r,s in zip(roots,rootroles):
        if r['kind'] == 'center':
            center[s] = {r['coordinate']:1}
        else:
            side[s] = {t:1 if c=='1/2' else -1
                       for t,c in zip(r['targets'],r['coefficients'])}
    for (a,b,_),(ca,cb) in zip(reversed(ops),reversed(coeff)):
        assert ca in (-1,1) and cb in (-1,1)
        add_scaled(center[b],center[a],cb)
        add_scaled(side[b],side[a],cb)
        if ca != 1:
            center[a] = {j:ca*c for j,c in center[a].items()}
            side[a] = {j:ca*c for j,c in side[a].items()}
    assert all(not center[s] for s in selected)
    for s,z in selected.items():
        assert set(side[s]) == set(z['targets'])
    # Original X is copied to all auxiliary V slots at its norm-one line
    # before any later event. Each original source then uses its already
    # charged rank-two head to reach its parity three-space, where it waits
    # until all new controls have finished and before the old K mixing.
    parity = {}
    for cube in range(v//8):
        for bit in range(2):
            ids = tuple(cube*8+j for j in range(8) if j.bit_count()%2==bit)
            S = frame_basis(ports[j] for j in ids)
            assert len(S) == 3 and S not in parity
            parity[S] = ids
    for node in witness['nodes']:
        if node['source_controls']:
            S = tuple(node['frame'][1])
            assert tuple(node['source_controls']) == parity[S]
    for e in witness['source_erasures']:
        a,b,i = e['donor'],e['recipient'],e['operation']
        S = tuple(e['frame'])
        assert alias[b] == a and i == last[a]
        assert position[i] < position[first[b]] and first[b] not in phase1
        assert e['phase'] == (1 if i in phase1 else 2)
        assert tuple(e['source_ports']) == parity[S]
        assert contained(tuple(actual_frames[i]),S)
        gauge = perpendicular(tuple(selected[b]['annihilator']),h)
        assert contained(S,gauge)
        assert all(j in parity[S] for j,c in witness['vectors'][e['value']])
        if deadlines[b] is None:
            assert i in phase1
        else:
            assert deadlines[b] == first[b]
    vectors = [dict(row) for row in witness['vectors']]
    # Re-evaluate the aliased fresh transcript, including every new source
    # erase, independently of the local completion compiler. This checks
    # that the exported read forms are the actual changed forms.
    fresh = [dict() for _ in range(R)]
    erase_at = defaultdict(list)
    for e in witness['source_erasures']:
        erase_at[e['operation']].append(e)
    for x,s in word['sources'].items():
        s = alias.get(s,s)
        assert not fresh[s]
        fresh[s] = {int(x)-1:1}
    actual_reads = {}
    def gate(i):
        a,b,_ = ops[i]; ca,cb = coeff[i]
        a,b = alias.get(a,a),alias.get(b,b)
        dst = {j:ca*c for j,c in fresh[a].items()}
        add_scaled(dst,fresh[b],cb); fresh[a] = dst
        for e in erase_at[i]:
            slot = e['donor']
            assert fresh[slot] == vectors[e['value']]
            fresh[slot] = {}
    for i in sorted(phase1):
        gate(i)
    for j,(r,s) in enumerate(zip(roots,rootroles)):
        if r['kind']=='center':
            actual_reads['center',j] = dict(fresh[alias.get(s,s)])
    late = defaultdict(list)
    for s in reversed([x['role'] for x in word['selected']]):
        if deadlines[s] is None:
            actual_reads['deferred',s] = dict(fresh[alias[s]])
        else:
            late[deadlines[s]].append(s)
    for i in range(len(ops)):
        if i in phase1:
            continue
        for s in late[i]:
            actual_reads['deferred',s] = dict(fresh[alias[s]])
        gate(i)
    for j,(r,s) in enumerate(zip(roots,rootroles)):
        if r['kind']=='side':
            actual_reads['side',j] = dict(fresh[alias.get(s,s)])
    # All accumulated target/source coefficients below are scaled by six.
    # Center scatter is 2/-1; ordinary side responses are +/-3.
    endpoint = [{} for _ in range(v)]
    target_frames = [[] for _ in range(v)]
    count = Counter()
    seen_reads = set()
    for node in witness['nodes']:
        phase,U = node['frame']; U = tuple(U)
        for rr in node['reads']:
            kind,ref = rr['kind'],rr['ref']
            key = kind,ref
            assert key not in seen_reads; seen_reads.add(key)
            val = vectors[rr['value']]
            assert val == actual_reads[key]
            count[kind] += 1
            if kind=='center':
                assert phase == 1
                r = roots[ref]; assert r['kind']=='center'
                k = r['coordinate']
                for t in range(v):
                    add_scaled(endpoint[t],val,2 if k in g['labels'][t] else -1)
                continue
            assert phase == 2
            if kind=='side':
                r = roots[ref]; assert r['kind']=='side'
                responses = {t:3 if c=='1/2' else -3
                             for t,c in zip(r['targets'],r['coefficients'])}
            else:
                assert kind=='deferred'
                responses = {t:-3*c for t,c in side[ref].items()}
            for t,c in responses.items():
                assert all((q & ports[t]).bit_count()%2 == 0 for q in U)
                target_frames[t].append(U)
                add_scaled(endpoint[t],val,c)
    assert seen_reads == set(actual_reads)
    target = Counter()
    for t,chain in enumerate(target_frames):
        # At a common phase/frame all scalar reads commute. Different
        # frames used by any one target must form an actual nested chain.
        chain.sort(key=lambda U:(len(U),U))
        prev = ()
        for U in chain:
            assert contained(prev,U),('Incomparable target read frames',t,prev,U)
            target[len(U)-len(prev)] += 1; prev = U
        cap = perpendicular((ports[t],),h)
        assert contained(prev,cap)
        target[len(cap)-len(prev)] += 1
    # Exact original-source K block, after all source-controlled erasures.
    for c in range(v//8):
        for i in range(8):
            t = 8*c+i
            for j in range(8):
                s = 8*c+j
                dist = (ports[t]^ports[s]).bit_count()
                if dist in (2,6):
                    add_scaled(endpoint[t],{s:1},3 if dist==6 else -3)
    assert all(row=={t:6} for t,row in enumerate(endpoint)), 'Fresh endpoint is not exactly I.'
    return dict(all_fresh_columns_equal_identity=True, arithmetic='integers, endpoint scaled by 6',
                checked_source_columns=v, checked_target_rows=v,
                source_controls_at_paid_parity_frames=True,
                original_source_V_before_all_controls=True,
                controls_before_original_K=True,
                all_centers_in_phase1=True, all_target_cap_reads_in_phase2=True,
                target_chains_nested=True, read_counts=dict(count),
                target_data_histogram=dict(sorted(target.items())),
                positive_target_data_histogram={k:c for k,c in sorted(target.items()) if k and c})


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--tree',type=Path,required=True)
    ap.add_argument('--cache',type=Path,required=True)
    ap.add_argument('--witness',type=Path,required=True)
    ap.add_argument('--flow-profile',type=Path,required=True)
    ap.add_argument('--lift-profile',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    a = ap.parse_args(); start = time.monotonic()
    g = read(a.cache/'graph.json'); w = read(a.cache/'frames.json'); word = read(a.cache/'selection.json')
    witness = read(a.witness); profile = read(a.flow_profile); lift = read(a.lift_profile)
    frames = [perpendicular(tuple(w['annihilators'][x]),g['h']) for _,_,x in word['ops']]
    framepath = a.tree/'references/paired-cube/physical/frames.json'
    pairpath = a.tree/'references/paired-cube/physical/pairs.json'
    for i,U in read(framepath)['frames']:
        frames[i] = tuple(U)
    contract = validate(g,word,witness,frames,read(pairpath)['pairs'])
    expected = {1:3*g['v'],g['h']-4:g['v']}
    assert contract['positive_target_data_histogram'] == expected
    assert lift['witness_sha256'] == sha(a.witness)
    assert lift['physical_R'] == profile['new_R']
    assert lift['all_actual_coefficients_dyadic'] and lift['denominator_lcm']=='2'
    certpath = resolve_receipt_path(lift['certificate_path'])
    assert sha(certpath) == lift['certificate_sha256']
    certificate = json.loads(gzip.decompress(certpath.read_bytes()))
    assert certificate['input_witness_sha256'] == sha(a.witness)
    assert certificate['input_profile_sha256'] == sha(a.flow_profile)
    proof_paths = [Path(__file__),Path(__file__).with_name('complex_frame_flow.py'),
                   Path(__file__).with_name('source_aligned_local.py'),a.witness,a.flow_profile,
                   a.lift_profile,resolve_receipt_path(lift['certificate_path']),framepath,pairpath]
    proof_paths += [Path(__file__).with_name(name) for name in
                   ('exact_complex_flow_lift.py','reproduce_complex.py',
                    'complex_source_aligned_physical_pairs.json','complex_source_aligned_kernel_pairs.json')]
    assert read(Path(__file__).with_name('complex_source_aligned_physical_pairs.json'))['pairs'] == read(pairpath)['pairs']
    frozen_kernel = read(Path(__file__).with_name('complex_source_aligned_kernel_pairs.json'))
    assert frozen_kernel['kernel_pairs'] == witness['kernel_pairs']
    matching_proof = resolve_receipt_path(frozen_kernel['matching_certificate'])
    assert matching_proof.exists()
    assert sha(matching_proof) == frozen_kernel['matching_certificate_sha256']
    proof_paths.append(matching_proof)
    proof_paths += [a.cache/name for name in ('graph.json','frames.json','selection.json','record.json')]
    proof = {portable(p):sha(p) for p in proof_paths}
    child = {int(k):c for k,c in profile['child_histogram'].items()}
    source_hist = read(a.tree/'certificates/paired-cube-sinks-input.json')['source_data_histogram']
    assert {int(k):c for k,c in source_hist.items()} == {1:g['v'],2:g['v'],g['h']-4:g['v']}
    recounted = Counter({int(k):3*c for k,c in profile['local_histogram'].items()})
    recounted.update({int(k):3*c for k,c in source_hist.items()})
    recounted.update({int(k):3*c for k,c in contract['target_data_histogram'].items() if int(k)})
    recounted[2] += 2*g['v']
    assert dict(recounted) == child
    m,W = 3*g['h'],profile['new_W']
    assert m*W-sum(k*c for k,c in child.items()) == profile['deficit']
    result = dict(signature='GPT-6 Astra',
                  status='Exact local invertible flow, exact all-column fresh identity, paid source controls, target read chains, and integer histogram certified. A literal globally renumbered operation program is not exported; dense initial dirty-response subtraction is defined by the exact certified flow.',
                  h=g['h'],v=g['v'],m=m,W_per_vertex=W,physical_R=profile['new_R'],
                  loss=profile['loss'],deficit_per_vertex=profile['deficit'],
                  rank_per_vertex=sum(k*c for k,c in child.items()),
                  local_histogram=profile['local_histogram'],
                  source_data_histogram=source_hist,
                  target_data_histogram=contract['target_data_histogram'],
                  physical_gauge_histogram={},child_histogram=profile['child_histogram'],
                  numerical_local_root=profile['numerical_local_root'],entropy=profile['entropy'],
                  terminal_sink_substitutions=0,
                  exact_lift_certificate_path=lift['certificate_path'],
                  exact_lift_certificate_sha256=lift['certificate_sha256'],
                  exact_scalar_program_sha256=lift['exact_scalar_program_sha256'],
                  matching_optimality_certificate_path=portable(matching_proof),
                  matching_optimality_certificate_sha256=sha(matching_proof),
                  scalar_coefficients=lift['coefficients'], scalar_denominator_lcm='2',
                  contract_checks=contract,proof_chain_sha256=proof,
                  regeneration='Run source_aligned_local.py, complex_frame_flow.py with source purification/kernel reuse, exact_complex_flow_lift.py, and this checker against pinned PR168 fd25adb7. No frozen large cache is required.',
                  seconds=time.monotonic()-start)
    a.out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('status','physical_R','m','W_per_vertex','deficit_per_vertex','numerical_local_root','contract_checks','seconds')},indent=2))


if __name__=='__main__':
    main()

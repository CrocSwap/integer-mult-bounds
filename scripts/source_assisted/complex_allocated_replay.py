#!/usr/bin/env python3
# Copyright 2026 icekylinx. Apache-2.0.
# Integrated with Codex assistance from GPT-6 Astra's round-thirteen flow.
"""Allocate and replay the NEW complex scalar flow with arbitrary dirty probes.

This is a globally numbered scalar transcript. Frame containment is checked;
Clifford/router operations on non-scalar frame components are not emitted.
Finite-field probes supplement, rather than replace, the exact local-map and
all-fresh-column certificates. The old physical-word replay is never used.
"""
import argparse
from collections import defaultdict
import gzip
import hashlib
import json
from pathlib import Path
import random
import sys


def require(ok, message):
    if not ok:
        raise ValueError(message)


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def contained(U, V):
    piv = {}
    for row in V:
        for k in sorted(piv, reverse=True):
            if row >> k & 1:
                row ^= piv[k]
        if row:
            piv[row.bit_length()-1] = row
    for row in U:
        for k in sorted(piv, reverse=True):
            if row >> k & 1:
                row ^= piv[k]
        if row:
            return False
    return True


def allocate(w, cert, expected_R):
    nodes = w['nodes']
    order = cert['topological_order']
    require(sorted(order) == list(range(len(nodes))), 'Invalid topological order')
    require(cert['kernel_pairs'] == w['kernel_pairs'], 'Kernel-pair binding')
    by_frame = {(n['frame'][0], tuple(n['frame'][1])): i for i, n in enumerate(nodes)}
    incoming, outgoing = defaultdict(list), defaultdict(list)
    for e, edge in enumerate(w['edges']):
        i, j = [by_frame[(f[0], tuple(f[1]))] for f in (edge['source'], edge['target'])]
        require(i != j and nodes[i]['frame'][0] <= nodes[j]['frame'][0] and
                contained(nodes[i]['frame'][1], nodes[j]['frame'][1]), 'Edge frame containment')
        for k, ident in enumerate(edge['basis']):
            outgoing[i].append((e, k, ident)); incoming[j].append((e, k, ident))
    donors, births = {}, {}
    for i, a, j, b in w['kernel_pairs']:
        require((i, a) not in donors and (j, b) not in births, 'Repeated kernel role')
        require(i != j and nodes[i]['frame'][0] <= nodes[j]['frame'][0] and
                contained(nodes[i]['frame'][1], nodes[j]['frame'][1]), 'Kernel frame containment')
        require(0 <= a < nodes[i]['retired']-nodes[i]['d']+nodes[i]['r'] and
                0 <= b < nodes[j]['new_dirty'], 'Kernel role out of bounds')
        donors[i, a] = (j, b); births[j, b] = (i, a)
    pending_edges, pending_births = {}, {}
    retired, copied = set(), set()
    transcript = []
    next_slot = 0
    def fresh_slot():
        nonlocal next_slot
        slot = next_slot; next_slot += 1
        return slot
    for i in order:
        node, local = nodes[i], cert['maps'][i]
        require([q[2] for q in incoming[i]] == node['inputs'][:len(incoming[i])], 'Incoming edge instances')
        require([q[2] for q in outgoing[i]] == node['outputs'], 'Outgoing edge instances')
        slots = []
        for e, k, ident in incoming[i]:
            require((e, k) in pending_edges, 'Edge consumed before production')
            slots.append(pending_edges.pop((e, k)))
        for ident in node['inputs'][len(incoming[i]):]:
            row = w['vectors'][ident]
            require(len(row) == 1 and row[0][1] == 1, 'Original V injection')
            port = row[0][0]
            require(port not in copied and node['frame'] == [1, [w['original_source_ports'][port]]], 'Repeated or misplaced V')
            copied.add(port); slot = fresh_slot(); slots.append(slot)
            transcript.append(['inject', slot, ident, 1])
        for b in range(node['new_dirty']):
            if (i, b) in births:
                require((i, b) in pending_births, 'Reused coordinate consumed before retirement')
                slots.append(pending_births.pop((i, b)))
            else:
                slots.append(fresh_slot())
        require(len(slots) == local['size'] == node['n']+node['new_dirty'] and
                len(set(slots)) == len(slots), 'Local physical basis')
        require(len(local['read_coefficients']) == len(node['reads']), 'Read coefficient count')
        for rr, coefficients in zip(node['reads'], local['read_coefficients']):
            transcript.append(['read', rr['kind'], rr['ref'],
                               [[slots[j], num, den] for j, num, den in coefficients]])
        for j, ident in enumerate(local['source_erase']):
            require(set(dict(w['vectors'][ident])) <= set(node['source_controls']), 'Unpaid source erasure')
            transcript.append(['inject', slots[j], ident, -1])
        for kind, a, b, num, den in reversed(local['inverse_gates']):
            if kind == 'add': num = -num
            elif kind == 'scale': num, den = den, num
            transcript.append([kind, slots[a], slots[b], num, den])
        for j, ident in enumerate(local['source_inject']):
            require(set(dict(w['vectors'][ident])) <= set(node['source_controls']), 'Unpaid source injection')
            transcript.append(['inject', slots[j], ident, 1])
        for j, (e, k, ident) in enumerate(outgoing[i]):
            pending_edges[e, k] = slots[j]
        for j in range(node['t'], len(slots)):
            a = j-node['t']-(node['d']-node['r'])
            if (i, a) in donors:
                pending_births[donors[i, a]] = slots[j]
            else:
                require(slots[j] not in retired, 'Twice-retired physical coordinate')
                retired.add(slots[j])
    require(not pending_edges and not pending_births, 'Unconsumed physical roles')
    require(copied == set(range(len(w['original_source_ports']))), 'Missing original V')
    require(next_slot == expected_R and retired == set(range(next_slot)), 'Physical stock / final partition')
    return transcript, next_slot


def responses(g, word):
    ops = word['ops']; R = 1+max(max(a,b) for a,b,_ in ops)
    side = [{} for _ in range(R)]
    for root, slot in zip(g['roots'], word['rootroles']):
        if root['kind'] == 'side':
            side[slot] = {t: 1 if c == '1/2' else -1 for t,c in zip(root['targets'], root['coefficients'])}
    for (a,b,_),(ca,cb) in zip(reversed(ops),reversed(word['opcoeff'])):
        for t,c in side[a].items():
            side[b][t] = side[b].get(t,0)+cb*c
            if not side[b][t]: del side[b][t]
        if ca != 1: side[a] = {t:ca*c for t,c in side[a].items()}
    result = {}
    for j, root in enumerate(g['roots']):
        if root['kind'] == 'center':
            result['center',j] = [(t,2 if root['coordinate'] in labels else -1) for t,labels in enumerate(g['labels'])]
        else:
            result['side',j] = [(t,3 if c == '1/2' else -3) for t,c in zip(root['targets'],root['coefficients'])]
    for selected in word['selected']:
        s = selected['role']; result['deferred',s] = [(t,-3*c) for t,c in side[s].items()]
    return result


def replay(program, vectors, scatters, dirty, x, p, inverse=False):
    z = list(dirty); y = [0]*len(x)
    fresh = [sum(c*x[j] for j,c in row)%p for row in vectors]
    events = reversed(program) if inverse else program
    for op in events:
        kind = op[0]
        if kind == 'read':
            if inverse: continue
            value = sum(z[j]*num*pow(den,-1,p) for j,num,den in op[3])%p
            for t,c in scatters[op[1],op[2]]: y[t] = (y[t]+c*value)%p
        elif kind == 'inject':
            _,j,ident,sign = op
            z[j] = (z[j]+(-sign if inverse else sign)*fresh[ident])%p
        else:
            _,a,b,num,den = op
            c = num*pow(den,-1,p)%p
            if kind == 'swap': z[a],z[b] = z[b],z[a]
            elif kind == 'scale': z[a] = z[a]*(pow(c,-1,p) if inverse else c)%p
            elif kind == 'add': z[a] = (z[a]+(-c if inverse else c)*z[b])%p
            else: raise ValueError(kind)
    return z,y


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--package',type=Path,required=True)
    ap.add_argument('--cache',type=Path,required=True,help='Regenerated aligned cache containing graph and selection')
    ap.add_argument('--transcript','--emit',dest='transcript',type=Path,
                    help='Optional globally numbered transcript, outside frozen package')
    ap.add_argument('--out',type=Path)
    a = ap.parse_args()
    require(not sys.flags.optimize, 'Run without -O')
    d = a.package/'decision'
    witness_path = d/'aligned_parity_purified_flow.result.witness.json'
    if witness_path.exists():
        witness_bytes = witness_path.read_bytes()
    else:
        witness_bytes = gzip.decompress(witness_path.with_suffix('.json.gz').read_bytes())
    cert_path = d/'aligned_parity_exact_lift.result.certificate.json.gz'
    profile = read(d/'complex_source_aligned_profile.json')
    w = json.loads(witness_bytes); cert = json.loads(gzip.decompress(cert_path.read_bytes()))
    require(sha(cert_path) == profile['exact_lift_certificate_sha256'] and
            hashlib.sha256(witness_bytes).hexdigest() == cert['input_witness_sha256'], 'Certificate file binding')
    program, R = allocate(w,cert,profile['physical_R'])
    g, word = read(a.cache/'graph.json'),read(a.cache/'selection.json')
    require(g['inputs'] == w['original_source_ports'], 'Aligned source ports')
    for name in ('graph.json','selection.json'):
        require(sha(a.cache/name) == profile['proof_chain_sha256']['decision/aligned_parity/cache/'+name], 'Aligned cache binding '+name)
    scatters = responses(g,word)
    checks = []; negative_controls = []
    for p in ((1<<61)-1, 1000000007):
        for seed in (13, 29):
            rng = random.Random(seed)
            dirty = [rng.randrange(1,p) for _ in range(R)]
            x = [rng.randrange(1,p) for _ in g['inputs']]
            final, actual = replay(program,w['vectors'],scatters,dirty,x,p)
            _, response = replay(program,w['vectors'],scatters,dirty,[0]*len(x),p)
            # Original K follows every source control. Target values scaled by 6.
            for t,port in enumerate(g['inputs']):
                for s in range(t//8*8,t//8*8+8):
                    dist = (port^g['inputs'][s]).bit_count()
                    if dist in (2,6): actual[t] = (actual[t]+(3 if dist==6 else -3)*x[s])%p
            require(all((v-response[t])%p == 6*x[t]%p for t,v in enumerate(actual)), 'New dirty-response endpoint')
            restored,_ = replay(program,w['vectors'],scatters,final,x,p,inverse=True)
            require(restored == dirty, 'Arbitrary dirty restoration')
            checks.append(dict(prime=p,seed=seed,endpoint=True,restoration=True))
            if not negative_controls:
                erase = next(j for j,op in enumerate(program) if op[0] == 'inject' and op[3] == -1)
                inject = next(j for j,op in enumerate(program) if op[0] == 'inject' and op[3] == 1)
                mutations = [('omit_source_erase', program[:erase]+program[erase+1:])]
                wrong = list(program); wrong[inject] = list(wrong[inject]); wrong[inject][3] = -1
                mutations.append(('reverse_V_injection',wrong))
                for name,mutated in mutations:
                    broken,_ = replay(mutated,w['vectors'],scatters,dirty,x,p)
                    restored,_ = replay(program,w['vectors'],scatters,broken,x,p,inverse=True)
                    require(restored != dirty, 'Mutation survived restoration: '+name)
                    negative_controls.append(dict(mutation=name,rejected_by='new transcript restoration'))
    encoded = (json.dumps(program,separators=(',',':'))+'\n').encode()
    if a.transcript: a.transcript.write_bytes(encoded)
    result = dict(status='PASS globally allocated new scalar flow probes',physical_R=R,
                  scalar_operations=len(program),transcript_sha256=hashlib.sha256(encoded).hexdigest(),
                  dirty_response='New A(z) evaluated by dirty-only replay of this transcript; subtraction at scalar frame zero',
                  allocation='Edge instances and kernel roles consumed once; final physical partition complete',
                  scope='Scalar quotient only; modular probes, not exhaustive dirty columns or full Clifford/router replay',
                  checks=checks,negative_controls=negative_controls)
    if a.out: a.out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__ == '__main__':
    main()

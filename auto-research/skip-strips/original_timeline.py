# Adapted from RaD / hipotures PR41 check_compiled_witness.py.
# Original envelope bases replace positive-label input. Full dirty basis checks
# now run at both h=23 and h=25; timing floats are excluded from certificates.
#!/usr/bin/env python3
"""Independent explicit role compiler for exported positive-frame witnesses.

No producer allocator, carrier matcher or rank-histogram function is imported.
Signed descriptions are converted to integer rational bases. Logical source
coefficients, every physical role trajectory, terminal incidence and both
dirty orientations are recomputed directly from binary DAG and selected uses.
"""
from __future__ import annotations

import argparse
import array
from collections import Counter
from datetime import datetime, timezone
from functools import lru_cache
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import struct
import sys
import time


def read_array(stream, code, count):
    result = array.array(code)
    result.frombytes(stream.read(count*result.itemsize))
    assert len(result) == count and sys.byteorder == 'little'
    return result


def read_dag(path):
    with Path(path).open('rb') as stream:
        h,v,n,q = struct.unpack('<4I',stream.read(16))
        args = read_array(stream,'I',2*n)
        core = read_array(stream,'Q',n)
        cover = read_array(stream,'Q',n)
        roots = read_array(stream,'I',q)
        kinds = read_array(stream,'I',q)
        active = read_array(stream,'B',n)
        assert not stream.read()
    return h,v,n,q,args,core,cover,roots,kinds,active


def original_labels(h,n,core,cover,active):
    ranks=[0]*n;frames=[None]*n
    for node in range(1,n):
        if not active[node]:continue
        c=core[node].bit_count();outside=cover[node]&~core[node]
        if c==3:
            assert core[node]==cover[node]
            ranks[node]=1;symbols=tuple(int(core[node]>>i&1) for i in range(h))
        else:
            assert c in (1,2)
            ranks[node]=outside.bit_count()
            symbols=tuple(1 if core[node]>>i&1 else i+2 if outside>>i&1 else 0 for i in range(h))
        frames[node]=(ranks[node],core[node],symbols)
    return ranks,frames


@lru_cache(maxsize=None)
def basis(frame):
    rank,forced,symbols = frame
    h = len(symbols)
    fs = [i for i in range(h) if forced >> i & 1]
    if len(fs) == 3:
        assert rank == 1 and all(symbols[i] == int(i in fs) for i in range(h))
        return (tuple(int(i in fs) for i in range(h)),)
    assert len(fs) in (1,2)
    assert all(symbols[i] == 1 for i in fs)
    classes = sorted({abs(s) for s in symbols if abs(s)>1})
    assert len(classes) == rank
    denom = 3-len(fs)
    rows = []
    for label in classes:
        row = [0]*h
        delta = sum(1 if s == label else -1 if s == -label else 0 for s in symbols)
        for i,s in enumerate(symbols):
            if i in fs:
                row[i] = delta
            elif abs(s) == label:
                row[i] = denom*(1 if s>0 else -1)
        assert any(row)
        rows.append(tuple(row))
    return tuple(rows)


def vector_in(vector,frame):
    rank,forced,symbols = frame
    fs = [i for i in range(len(vector)) if forced >> i & 1]
    if len(fs) == 3:
        return all(vector[i] == (vector[fs[0]] if i in fs else 0) for i in range(len(vector)))
    t = vector[fs[0]]
    if sum(vector) != 3*t or any(vector[i] != t for i in fs):
        return False
    values = {}
    for i,s in enumerate(symbols):
        if i in fs:
            continue
        if not s:
            if vector[i]:
                return False
        else:
            assert abs(s)>1
            value = vector[i]*(1 if s>0 else -1)
            if abs(s) in values and values[abs(s)] != value:
                return False
            values[abs(s)] = value
    return True


@lru_cache(maxsize=300000)
def contained(a,b):
    return all(vector_in(vector,b) for vector in basis(a))


def check(document, small_dirty=False):
    row = document['producer'] if 'producer' in document else document
    native = document.get('selected_links') or json.loads(Path(row['witness_path']).read_text())
    h,v,n,q,args,core,cover,roots,kinds,active = read_dag(row['dag_path'])
    ranks,frames = original_labels(h,n,core,cover,active)
    triples = list(combinations(range(h),3))
    assert len(triples) == v
    active_nodes = [node for node in range(1,n) if active[node]]
    additions = sum(bool(args[2*node]) for node in active_nodes)
    expected_roles = additions+q-len(native['links'])
    assert expected_roles == row['R']
    scalar = [0]*n
    for node in active_nodes:
        if not args[2*node]:
            assert node <= v
            scalar[node] = 1 << (node-1)
            vector = tuple(int(i in triples[node-1]) for i in range(h))
            assert basis(frames[node]) == (vector,)
        else:
            a,b = args[2*node:2*node+2]
            assert a<node and b<node and not scalar[a] & scalar[b]
            scalar[node] = scalar[a] | scalar[b]
            assert contained(frames[a],frames[node]) and contained(frames[b],frames[node])
        for vector in basis(frames[node]):
            common = (frames[node][1]&-frames[node][1]).bit_length()-1
            assert sum(vector) == 3*vector[common]
            assert sum(x*x for i,x in enumerate(vector) if i != common)>0
    output_targets = []
    center_nodes = []
    for j,node in enumerate(roots):
        common = (core[node]&-core[node]).bit_length()-1
        if kinds[j]:
            assert core[node].bit_count()==1 and ranks[node]==h-1
            expected = sum(1<<i for i,t in enumerate(triples) if common in t)
            output_targets.append([i for i,t in enumerate(triples) if common in t])
            center_nodes.append(node)
        else:
            absent = ((1<<h)-1)^cover[node]
            assert absent.bit_count()==2
            excluded = [i for i in range(h) if absent>>i&1]
            target = tuple(sorted([common,*excluded]))
            expected = sum(1<<i for i,t in enumerate(triples) if common in t and not set(t)&set(excluded))
            output_targets.append([triples.index(target)])
            for vector in basis(frames[node]):
                assert 3*sum(vector[i] for i in target) == sum(vector)
        assert scalar[node] == expected
    assert len(center_nodes)==h and len(set(center_nodes))==h
    uses = [[] for _ in range(n)]
    for node in active_nodes:
        if args[2*node]:
            for pos in (0,1):
                uses[args[2*node+pos]].append(2*node+pos)
    for j,node in enumerate(roots):
        uses[node].append((1<<31)|j)
    for node in center_nodes:
        assert len(uses[node])==1, 'Retained center has a later middle producer incidence'

    def use_node(e):
        return roots[e&0x7fffffff] if e>>31 else e//2

    def use_value(e):
        return use_node(e) if e>>31 else args[e]

    def order_key(node):
        old = 1 if not args[2*node] else cover[node].bit_count()-core[node].bit_count()
        return ranks[node],old,node

    successor = {}
    receivers = set()
    retained = {}
    for donor,receiver in native['links']:
        assert donor not in retained and receiver not in receivers and args[2*donor]
        value = use_value(receiver)
        positions = [pos for pos in (0,1) if args[2*donor+pos] == value]
        assert len(positions)==1
        previous = 2*donor+positions[0]
        assert previous not in successor
        target = use_node(receiver)
        assert contained(frames[donor],frames[target])
        if not receiver>>31:
            assert order_key(donor)<order_key(target)
        successor[previous] = receiver
        receivers.add(receiver)
        retained[donor] = positions[0]

    order = sorted(active_nodes,key=order_key)
    place = {node:i for i,node in enumerate(order)}
    edge_slots = {}
    sources = {}
    gates = []
    slot_frames = []
    slot_values = []
    histogram = Counter()
    transitions = 0

    def allocate(frame,value):
        slot = len(slot_frames)
        slot_frames.append(frame)
        slot_values.append(value)
        histogram[frame[0]] += 1
        return slot

    def assign_chain(first,slot,value):
        seen = set()
        e = first
        while True:
            assert e not in seen and e not in edge_slots and use_value(e)==value
            seen.add(e)
            edge_slots[e] = slot
            if e not in successor:
                break
            e = successor[e]

    for node in order:
        starts = [e for e in uses[node] if e not in receivers]
        assert starts
        if not args[2*node]:
            first = allocate(frames[node],scalar[node])
            outs = [first]+[allocate(frames[node],scalar[node]) for _ in starts[1:]]
            ins = [first]
            sources[node-1] = first
        else:
            a,b = args[2*node:2*node+2]
            assert place[a]<place[node] and place[b]<place[node]
            ins = [edge_slots[2*node],edge_slots[2*node+1]]
            assert ins[0]!=ins[1]
            for operand,slot in zip((a,b),ins):
                assert slot_values[slot]==scalar[operand]
                assert contained(slot_frames[slot],frames[node])
                histogram[ranks[node]-slot_frames[slot][0]] += 1
                transitions += 1
                slot_frames[slot] = frames[node]
            pivot_pos = 1-retained[node] if node in retained else 0
            pivot = ins[pivot_pos]
            controller = ins[1-pivot_pos]
            slot_values[pivot] ^= slot_values[controller]
            assert slot_values[pivot]==scalar[node]
            outs = [pivot]+[allocate(frames[node],scalar[node]) for _ in starts[1:]]
            if node not in retained:
                histogram[h-ranks[node]] += 1
                slot_frames[controller] = None
            ins = [pivot,controller]
        for e,slot in zip(starts,outs):
            assign_chain(e,slot,node)
        gates.append((node,tuple(ins),tuple(outs)))
    assert len(slot_frames)==expected_roles
    output_slots = []
    scatter = [0]*v
    for j,node in enumerate(roots):
        slot = edge_slots[(1<<31)|j]
        assert slot_values[slot]==scalar[node] and contained(slot_frames[slot],frames[node])
        histogram[ranks[node]-slot_frames[slot][0]] += 1
        transitions += 1
        if kinds[j]:
            histogram[ranks[node]] += 1
            histogram[h-ranks[node]] += 1  # Copied retained center: paid copy and direct cleanup.
        else:
            histogram[h-1-ranks[node]] += 1
            histogram[1] += 1
        slot_frames[slot] = None
        output_slots.append(slot)
        for target in output_targets[j]:
            scatter[target] ^= scalar[node]
    assert scatter == [1<<i for i in range(v)], 'JLV must be the complete scalar identity'
    assert all(frame is None for frame in slot_frames), 'Every physical role must terminate'
    reverse_frames = [None]*expected_roles
    for j,slot in enumerate(output_slots):
        assert reverse_frames[slot] is None, 'Designated output terminals must have separate physical roles'
        reverse_frames[slot] = frames[roots[j]]
    reverse_checks = 0
    for node,ins,outs in reversed(gates):
        for slot in set(ins+outs):
            assert reverse_frames[slot] is None or contained(frames[node],reverse_frames[slot])
            reverse_frames[slot] = frames[node]
            reverse_checks += 1
    for input_id,slot in sources.items():
        assert contained(reverse_frames[slot],frames[input_id+1]) and contained(frames[input_id+1],reverse_frames[slot])
    actual_hist = [histogram[r] for r in range(h+1)]
    expected_hist = list(row['histogram'])
    expected_hist[1] += h
    expected_hist[h] -= h
    assert actual_hist[1:]==expected_hist[1:], (actual_hist,expected_hist)
    assert sum(r*n for r,n in enumerate(actual_hist)) == h*expected_roles+h*(h-1)
    result = dict(status='independent scalar, rational frames, physical compiler and rank timeline PASS',
                  h=h,v=v,additions=additions,designated_outputs=q,retained_links=len(native['links']),
                  roles=expected_roles,center_terminal_count=h,center_rank=h-1,
                  full_output_coefficients=v*v,physical_frame_transitions=transitions,
                  reverse_complement_frame_incidences=reverse_checks,
                  copied_histogram=actual_hist,copied_rank_sum=sum(r*n for r,n in enumerate(actual_hist)),
                  native_zero_rank_bookkeeping=expected_hist[0],
                  zero_rank_scope='Explicit output incidences include no-operation frame checks omitted from native histogram bookkeeping; only positive ranks enter the recurrence',
                  rational_frame_classes=len({frames[node] for node in active_nodes}),
                  selected_links_sha256=sha256(json.dumps(native,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
                  dag_sha256=sha256(Path(row['dag_path']).read_bytes()).hexdigest(),
                  containment_cache=contained.cache_info()._asdict())
    if small_dirty:
        R = expected_roles
        initial = [1<<i for i in range(2*v+R)]
        mixer = []
        for _,ins,outs in gates:
            if len(ins)==2:
                mixer.append((2*v+ins[0],2*v+ins[1]))
            for slot in outs[1:]:
                mixer.append((2*v+slot,2*v+ins[0]))
        J = [(v+out,2*v+slot) for j,slot in enumerate(output_slots) for out in output_targets[j]]
        V = [(2*v+slot,input_id) for input_id,slot in sources.items()]
        word = mixer+J+list(reversed(mixer))+V+mixer+J+list(reversed(mixer))+V
        forward = initial.copy()
        for target,source in word:
            assert target!=source
            forward[target] ^= forward[source]
        assert forward[:v] == initial[:v] and forward[2*v:] == initial[2*v:]
        assert forward[v:2*v] == [initial[v+i]^initial[i] for i in range(v)]
        dual = initial.copy()
        for target,source in reversed(word):
            dual[source] ^= dual[target]
        assert dual[v:2*v] == initial[v:2*v] and dual[2*v:] == initial[2*v:]
        assert dual[:v] == [initial[i]^initial[v+i] for i in range(v)]
        result['complete_dirty_basis'] = dict(auxiliary_basis_vectors=R,total_basis_vectors=2*v+R,
                                             elementary_word_length=len(word),inputs=v,targets=v,
                                             orientations=['forward','reverse-complement'],all_dirty_restore=True)
    return result

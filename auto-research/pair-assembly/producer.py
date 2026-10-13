#!/usr/bin/env python3
"""Full graph/profile replay and an independent dense-support/count audit.

Inherited generators: icekylinx PR18/32/36; profiler: PR32 and Dominik
Scholz PR35. This audit uses direct global bitsets rather than compressed
producer provenance and replays every exported matching use independently.
"""
from collections import Counter
from itertools import combinations
from pathlib import Path
import argparse
import gc
import json
import os
import shlex
import struct
import subprocess
import sys
import tempfile

from verify import ROOT, HERE, require, read, check_sources, exactness
from partial_swap.graph import export
from pair_graph import graph
import original_timeline as timeline


def dense_audit(c):
    h = c.h
    triples = list(combinations(range(h),3))
    require(triples == c.inputs, 'Wrong input enumeration')
    masks = [sum(1<<i for i in t) for t in triples]
    supports = [0]*len(c.args)
    degree = [0]*len(c.args)
    ranks = [0]*len(c.args)
    additions = 0
    for x in sorted(c.active):
        args = c.args[x]
        require(c.core[x] and not c.core[x] & ~c.union[x], 'Invalid envelope')
        if args is None:
            require(1<=x<=len(triples) and c.core[x] == c.union[x] == masks[x-1], 'Source label')
            supports[x] = 1<<(x-1)
            ranks[x] = 1
        else:
            left,right = args
            require(left<x and right<x and left in c.active and right in c.active, 'DAG order')
            require(not supports[left]&supports[right], 'Overlapping exact source supports')
            supports[x] = supports[left]|supports[right]
            require(c.core[x] == c.core[left]&c.core[right], 'Wrong core')
            require(c.union[x] == c.union[left]|c.union[right], 'Wrong cover')
            require(c.core[x].bit_count() in (1,2), 'Invalid common core')
            ranks[x] = c.union[x].bit_count()-c.core[x].bit_count()
            for y in args:
                require(not c.core[x]&~c.core[y] and not c.union[y]&~c.union[x], 'Envelope inclusion')
                degree[y] += 1
            additions += 1
    outputs = list(c.outputs.items())
    totals = 0
    for ((common,target),node) in outputs:
        omitted = set(target)-{common}
        expected = sum(1<<j for j,t in enumerate(triples)
                       if common in t and not omitted.intersection(t))
        require(supports[node] == expected, 'Wrong exact global output')
        require(c.core[node] == 1<<common, 'Output common point')
        require(c.union[node] == ((1<<h)-1)-sum(1<<i for i in omitted), 'Output envelope')
        totals += not omitted
        degree[node] += 1
    require(totals == h, 'Missing or duplicate centers')
    return degree,ranks,outputs,dict(exact_global_additions=additions,
        exact_global_outputs=len(outputs),envelope_inclusions=2*additions,
        retained_centers=totals,source_lines=len(triples))


def recount(c, degree, ranks, outputs, link_path):
    h,n = c.h,len(c.args)
    hist = Counter()
    for x in c.active:
        r = ranks[x]
        require(degree[x]>0, 'Dead node')
        if c.args[x] is None:
            hist[1] += degree[x]
        else:
            hist[r] += degree[x]-1
            hist[h-r] += 1
            for y in c.args[x]:
                hist[r-ranks[y]] += 1
    for ((common,target),node) in outputs:
        r = ranks[node]
        if len(target) == 1:
            hist[r] += 1
            hist[h] += 1
        else:
            hist[h-1-r] += 1
            hist[1] += 1
    raw = link_path.read_bytes()
    nn,nlinks = struct.unpack_from('<2I',raw)
    require(nn == n and len(raw) == 8+8*nlinks, 'Matching record format')
    donors,uses = set(),set()
    orientation_changes = 0
    for i in range(nlinks):
        donor,use = struct.unpack_from('<2I',raw,8+8*i)
        require(donor not in donors and use not in uses, 'Matching collision')
        donors.add(donor)
        uses.add(use)
        require(donor in c.active and c.args[donor] is not None, 'Invalid donor')
        if use>>31:
            j = use&0x7fffffff
            require(j<len(outputs), 'Invalid terminal use')
            target = outputs[j][1]
            value,event = target,n+j
        else:
            target = use//2
            require(target in c.active and c.args[target] is not None, 'Invalid consumer')
            value,event = c.args[target][use%2],target
        require(value in c.args[donor], 'Carrier does not preserve operand')
        require((ranks[donor],donor)<(ranks[target],event), 'Noncausal carrier')
        require(not c.core[target]&~c.core[donor] and not c.union[donor]&~c.union[target],
                'Carrier frames not nested')
        ru,rv,rt = ranks[donor],ranks[value],ranks[target]
        require(rv<=ru<=rt, 'Carrier rank order')
        hist[h-ru] -= 1
        hist[rv] -= 1
        hist[rt-rv] -= 1
        hist[rt-ru] += 1
        orientation_changes += value == c.args[donor][0]
    require(all(n>=0 for n in hist.values()), 'Negative physical multiplicity')
    R = c.additions+len(outputs)-nlinks
    mass = sum(t*n for t,n in hist.items())
    require(mass == h*R+2*h*(h-1), 'Independent old rank accounting')
    return dict(h=h,v=len(c.inputs),c=c.additions,q=len(outputs),baseline_R=c.additions+len(outputs),
                matched=nlinks,R=R,orientation_changes=orientation_changes,
                rank_sum=mass,loss=h*(h-1),histogram=[hist[r] for r in range(h+1)])


RECORD = False


def expect(name, value, message):
    """Compare with the recorded JSON; in --record mode write it first."""
    path = HERE/name
    if RECORD:
        path.write_text(json.dumps(value, indent=2, sort_keys=True)+'\n')
    require(value == read(path), message)


def run(work):
    require(not sys.flags.optimize, 'Assertions must remain enabled')
    check_sources()
    exe = work/'profiles'
    subprocess.run([*shlex.split(os.environ.get('CXX','c++')),'-O3','-std=c++17',
                    '-I',str(ROOT/'scripts/partial_swap'),str(HERE/'profiles.cpp'),'-o',str(exe)],check=True)
    receipt = {}
    for h in (23,25):
        print('Rebuilding scalar graph, original labels and fixed profiles, h='+str(h),flush=True)
        c = graph(h)
        scalar = c.verify()
        expect(f'scalar-{h}.json', scalar, 'Scalar provenance mismatch')
        degree,ranks,outputs,audit = dense_audit(c)
        dag,links = work/f'h{h}.bin',work/f'h{h}.uses'
        export(c,dag)
        original = json.loads(subprocess.check_output([str(exe),str(dag),str(links)],text=True,
                    env=dict(os.environ,LINKS_IN=str(HERE/f'links-{h}.uses'))))
        require(sorted(struct.iter_unpack('<2I',links.read_bytes()[8:])) ==
                sorted(struct.iter_unpack('<2I',(HERE/f'links-{h}.uses').read_bytes()[8:])),
                'Pinned matching changed')
        independent = recount(c,degree,ranks,outputs,links)
        require(original == independent, 'Independent physical recount failed')
        expect(f'original-{h}.json', original, 'Recorded physical recount mismatch')
        actual = read(Path(str(dag)+'.round3_rankone_certified_profiles.json'))
        expect(f'profiles-{h}.json', actual, 'Fixed profile rebuild mismatch')
        exactness(h)
        raw=links.read_bytes()
        nodes,count=struct.unpack_from('<2I',raw)
        selected=[list(struct.unpack_from('<2I',raw,8+8*i)) for i in range(count)]
        row=dict(original,dag_path=str(dag))
        timeline.basis.cache_clear();timeline.contained.cache_clear()
        compiled=timeline.check({'producer':row,'selected_links':{'links':selected}},True)
        expect(f'timeline-{h}.json', compiled, 'Independent full timeline mismatch')
        timeline.basis.cache_clear();timeline.contained.cache_clear()
        print('PASS complete physical timeline and every dirty basis vector, both orientations h='+str(h),flush=True)
        receipt[str(h)] = dict(scalar=scalar,dense_audit=audit,independent_recount=independent,
                          fixed_profile=actual,full_timeline=compiled)
        c.support_in.cache_clear()
        del c
        gc.collect()
        print('PASS complete h='+str(h)+' supports, all matching uses, rank count and CRT profiles',flush=True)
    data_exe = work/'data-corners'
    subprocess.run([*shlex.split(os.environ.get('CXX','c++')),'-O3','-std=c++17',
                    str(HERE/'data_corners.cpp'),'-o',str(data_exe)],check=True)
    print('Checking all 4,073,300 actual fixed-basis data pairs',flush=True)
    actual_data=json.loads(subprocess.check_output([str(data_exe)],text=True))
    require(actual_data==read(HERE/'data-corners.json'),'Full data-corner replay mismatch')
    receipt['data_corners']=dict(pairs=actual_data['pairs'],good=actual_data['good'],
                                fallback=actual_data['fallback'],nonzero_pivots=actual_data['nonzero_pivots'])
    from verify import data_corners
    recovered=data_corners()
    require(recovered['good']==4073300 and recovered['fallback']==0,'Incomplete recovery')
    receipt['exact_recovery']=recovered['exact_recovery']
    print('PASS all data pairs; ten primary-prime failures recovered over Q',flush=True)
    return receipt


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--work-dir',type=Path)
    parser.add_argument('--output',type=Path)
    parser.add_argument('--record',action='store_true',help='write the scalar/original/profile/timeline JSON records')
    args = parser.parse_args()
    RECORD = args.record
    if args.work_dir:
        args.work_dir.mkdir(parents=True,exist_ok=True)
        result = run(args.work_dir)
    else:
        with tempfile.TemporaryDirectory(prefix='pair-assembly-') as directory:
            result = run(Path(directory))
    if args.output:
        args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')

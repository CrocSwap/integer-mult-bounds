"""Screen exact helper-basis pairs after MOVE events.

This is a finite discovery screen, not an optimality certificate.
Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from collections import defaultdict
from fractions import Fraction as Q
import gzip
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from construct import basis
from local import add, span


def pure_combinations(rows, roles, group):
    """Eliminate coordinates outside the group; retain field coefficients."""
    pivots, output = {}, []
    for role in roles:
        outside = {k:v for k,v in rows[role].items() if k not in group}
        inside = {k:v for k,v in rows[role].items() if k in group}
        coefficients = {role:Q(1)}
        while outside:
            pivot = min(outside)
            if pivot not in pivots:
                scale = 1/outside[pivot]
                pivots[pivot] = [{k:v*scale for k,v in row.items()}
                                 for row in (outside, inside, coefficients)]
                break
            scale = -outside[pivot]
            for target, source in zip((outside, inside, coefficients), pivots[pivot]):
                add(target, source, scale)
        if not outside and inside:
            output.append((inside, coefficients))
    return output


def dyadic_program(program):
    for event in program:
        q = Q(event[-2])
        numerator, denominator = abs(q.numerator), q.denominator
        if denominator & (denominator-1):
            return False
        if event[0] == 'SCALE' and numerator & (numerator-1):
            return False
    return True


def candidates(word, group, entry, exit_frame):
    frames = [span(b) for b in word['frames']]
    valid = {f for f,frame in enumerate(frames) if frames[entry] < frame < frames[exit_frame]}
    if not valid:
        return []
    public = word['public']
    snapshots, at = defaultdict(list), defaultdict(set)
    rows = [{r:Q(1)} if r < public else {} for r in range(public+8)]
    for r,f in enumerate(word['initial']):
        at[f].add(r)
    for index,event in enumerate(word['program']):
        op,r = event[:2]
        if op == 'MOVE':
            old,new = event[2:4]
            at[old].remove(r)
            at[new].add(r)
            for frame in (old,new):
                if frame in valid and at[frame] & group:
                    roles = sorted(at[frame])
                    combinations = pure_combinations(rows, roles, group)
                    if combinations:
                        snapshots[index].append((frame,roles,combinations))
        elif op == 'INIT':
            rows[r] = {}
            at[event[2]].add(r)
        elif op == 'CLEAR':
            rows[r] = {}
            at[event[2]].remove(r)
        elif op == 'COPY':
            rows[r] = {k:v*Q(event[-2]) for k,v in rows[event[2]].items()}
        elif op == 'SCALE':
            rows[r] = {k:v*Q(event[-2]) for k,v in rows[r].items()}
        else:
            add(rows[r], rows[event[2]], Q(event[-2]))
    columns = [{r:Q(1)} if r < public else {} for r in range(public+8)]
    hits = []
    for index in range(len(word['program'])-1, -1, -1):
        for frame,roles,prefix_basis in snapshots.get(index, []):
            suffix_basis = pure_combinations(columns, roles, group)
            for c,a in prefix_basis:
                for raw_d,raw_b in suffix_basis:
                    pairing = sum(v*raw_d.get(k,0) for k,v in c.items())
                    if not pairing:
                        continue
                    b = {k:v/pairing for k,v in raw_b.items()}
                    d = {k:v/pairing for k,v in raw_d.items()}
                    if sum(v*b.get(k,0) for k,v in a.items()) != 1:
                        continue
                    available = group & set(roles)
                    pivot = next((r for r in sorted(available) if b.get(r)), min(available))
                    if not dyadic_program(basis(c,d,pivot,entry)+basis(a,b,pivot,frame)):
                        continue
                    ranks = [len(word['frames'][frame])-len(word['frames'][entry]),
                             len(word['frames'][exit_frame])-len(word['frames'][frame])]
                    hits.append({'cut_after':index, 'frame':frame, 'pivot':pivot,
                                 'a':a, 'b':b, 'c':c, 'd':d, 'ranks':ranks})
        event = word['program'][index]
        op,r = event[:2]
        if op == 'INIT':
            columns[r] = {}
        elif op == 'CLEAR':
            columns[r] = {}
        elif op == 'COPY':
            add(columns[event[2]], columns[r], Q(event[-2]))
            columns[r] = {}
        elif op == 'SCALE':
            columns[r] = {k:v*Q(event[-2]) for k,v in columns[r].items()}
        elif op == 'ADD':
            add(columns[event[2]], columns[r], Q(event[-2]))
    return hits


def encode(value):
    if isinstance(value,Q):
        return str(value)
    if isinstance(value,dict):
        return {k:encode(v) for k,v in value.items()}
    if isinstance(value,list):
        return [encode(v) for v in value]
    return value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--word', type=Path, default=HERE/'WORD.json.gz')
    args = parser.parse_args()
    word = json.loads(gzip.decompress(args.word.read_bytes()))
    mains = set(word['live']) | {r+112 for r in word['live']}
    groups = defaultdict(set)
    for r in range(word['public']):
        if r not in mains:
            groups[word['initial'][r],word['final'][r]].add(r)
    hits, tested = [], 0
    for (entry,exit_frame),roles in groups.items():
        if len(word['frames'][exit_frame])-len(word['frames'][entry]) > 1:
            hits.extend(candidates(word, roles, entry, exit_frame))
            tested += 1
    print(json.dumps(encode({'tested_boundary_groups':tested, 'candidates':hits}), sort_keys=True))


if __name__ == '__main__':
    main()

"""Exact main-endpoint path certificate for the twelve early native maps.

No optimizer, native interpreter, floating arithmetic or third-party library.
Prepared for Cinna Davis with substantial OpenAI Codex assistance. Apache-2.0.
Source circuit and attribution: Cao Yifan's round-three word, PR4470 lineage.
"""
from collections import deque
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import argparse
import gzip
import json
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = 'research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz'
SOURCE_SHA256 = '7679daa4ec6a40f56fc7f0202379a6f454310e94945aba4f48beaaaafb838d05'


def need(condition, message):
    if not condition:
        raise ValueError(message)


def span(vectors):
    points = {0}
    for v in vectors:
        points.update(x ^ v for x in tuple(points))
    return points


def rank(vectors):
    pivots = {}
    for v in vectors:
        while v:
            j = v.bit_length() - 1
            if j in pivots:
                v ^= pivots[j]
            else:
                pivots[j] = v
                break
    return len(pivots)


def owners(event):
    if event[0] == 'warp':
        return {event[1][1]}
    if event[0] != 'scalar':
        return set()
    gate = event[1]
    fields = gate[1:3] if gate[0] in ('add', 'copy') else gate[1:2]
    return {field[1] for field in fields if field[0] == 'L'}


def load_source(raw=None):
    raw = (ROOT/SOURCE).read_bytes() if raw is None else raw
    need(sha256(raw).hexdigest() == SOURCE_SHA256, 'Exact frozen native source bytes')
    word = json.loads(gzip.decompress(raw))
    c = word['canonical']
    need((c['h'], c['v'], len(c['start']), len(c['final'])) == (9, 112, 632, 632),
         'Nine axes, 224 main owners and 408 independent helper owners')
    programs = {d:[e for e in p if e[0] != 'climb'] for d,p in word['programs'].items()}
    need(set(programs) == {'forward', 'backward'}, 'Both source orientations')
    return c, programs


def graph(c, program):
    """All scalar contacts vary; every warp breaks frame-containment flow."""
    edges, last = {}, {}
    for i,event in enumerate(program):
        if event[0] == 'warp':
            last[event[1][1]] = i
        elif event[0] == 'scalar':
            for r in owners(event):
                if r in last:
                    edges.setdefault(last[r], set()).add(i)
                last[r] = i
    for r in range(2*c['v']):
        if r in last:
            edges.setdefault(last[r], set()).add('main:' + str(r))
    return edges


def early_occurrences(c, program):
    out = {}
    for op in range(47,59):
        positive = [i for i,e in enumerate(program)
                    if e[0]=='warp' and e[2]==op and len(c['frames'][e[3]])==1]
        need(len(positive)==1, 'One early positive occurrence per source operator')
        a = positive[0]
        b = next(i for i in range(a+1,len(program))
                 if program[i][0]=='warp' and program[i][2]==-op)
        ea, eb = program[a], program[b]
        need(ea[1]==eb[1] and ea[3:5]==[eb[4],eb[3]], 'Original paired inverse frames')
        need(b-a==5 and all(program[i][0]=='scalar' and program[i][1][0]=='add'
                            and len(owners(program[i]))==2 for i in range(a+1,b)),
             'Four original early ADD contacts')
        need(all(program[i][1][2]==ea[1] for i in range(a+1,b)),
             'Original early source is read at every forward contact')
        need(not any(e[0]=='warp' and ea[1][1] in owners(e) for e in program[:a]),
             'Initial source line has no prior warp')
        initial = c['frames'][c['start'][ea[1][1]]]
        need(initial==c['frames'][ea[3]] and len(initial)==1, 'Original initial source line')
        out[str(op)] = {'positive':a, 'negative':b,
                        'positive_line':c['frames'][ea[4]][0], 'negative_line':initial[0]}
    return out


def make_certificate(c, program):
    adjacency = graph(c,program)
    result = {}
    for op,record in early_occurrences(c,program).items():
        result[op] = {}
        for orientation in ('positive','negative'):
            start = record[orientation]
            queue, parent = deque([start]), {start:None}
            caps = []
            while queue:
                a = queue.popleft()
                for b in sorted(adjacency.get(a,()), key=str):
                    if b in parent:
                        continue
                    parent[b] = a
                    if isinstance(b,str):
                        caps.append(int(b.split(':')[1]))
                    else:
                        queue.append(b)
            intersection, witnesses = set(range(512)), []
            for r in sorted(caps, key=lambda r:(len(c['frames'][c['final'][r]]),r)):
                cap = span(c['frames'][c['final'][r]])
                smaller = intersection & cap
                if smaller == intersection:
                    continue
                at, path = 'main:'+str(r), []
                while at is not None:
                    path.append(at)
                    at = parent[at]
                path.reverse()
                witnesses.append({'role':r,'frame':c['final'][r], 'path':path})
                intersection = smaller
                if len(intersection)==2:
                    break
            line = record[orientation+'_line']
            need(intersection=={0,line}, 'Source main endpoints force the recorded line')
            result[op][orientation] = {'start':start,'line':line,'witnesses':witnesses}
    return {'schema_version':1, 'source':SOURCE, 'source_sha256':SOURCE_SHA256,
            'status':'EXACT_MAIN_ENDPOINT_PRELUDE_CAP_CERTIFICATE', 'operators':result}


def check_certificate(c, programs, certificate):
    """Validate paths by direct chronological scans, without graph construction."""
    need(certificate['source']==SOURCE and certificate['source_sha256']==SOURCE_SHA256,
         'Certificate scientific source pin')
    need(set(certificate['operators'])=={str(i) for i in range(47,59)}, 'All twelve operators')
    total_paths = 0
    for direction,program in programs.items():
        for op,record in certificate['operators'].items():
            need(set(record)=={'positive','negative'}, 'Both early native outputs')
            for orientation,claim in record.items():
                start, line = claim['start'], claim['line']
                e = program[start]
                sign = 1 if orientation=='positive' else -1
                need(e[0]=='warp' and e[2]==sign*int(op), 'Actual early native output')
                need(c['frames'][e[4]]==[line], 'Claimed line equals original native output')
                intersection, normals = set(range(512)), []
                seen_roles = set()
                for witness in claim['witnesses']:
                    path, r, frame = witness['path'], witness['role'], witness['frame']
                    need(r not in seen_roles and 0<=r<224, 'Distinct actual main endpoint')
                    seen_roles.add(r)
                    need(frame==c['final'][r], 'Actual fixed main exit frame')
                    need(path[0]==start and path[-1]=='main:'+str(r), 'Correct path endpoints')
                    for a,b in zip(path[:-2],path[1:-1]):
                        need(isinstance(a,int) and isinstance(b,int) and a<b,
                             'Strict chronological path')
                        need(program[b][0]=='scalar', 'Every internal vertex is a scalar contact')
                        shared = owners(program[a]) & owners(program[b])
                        valid = [owner for owner in shared
                                 if not any(owner in owners(x) for x in program[a+1:b])]
                        need(bool(valid), 'Consecutive owner contacts with no intervening warp')
                        actual_a = program[a][4] if program[a][0]=='warp' else program[a][2]
                        need(span(c['frames'][actual_a]) <= span(c['frames'][program[b][2]]),
                             'Original actual frames satisfy the directed containment')
                    last = path[-2]
                    need(isinstance(last,int) and r in owners(program[last]), 'Final path owns main endpoint')
                    need(not any(r in owners(x) for x in program[last+1:]),
                         'No later owner contact or warp before the fixed exit')
                    cap = span(c['frames'][frame])
                    actual_last = program[last][4] if program[last][0]=='warp' else program[last][2]
                    need(span(c['frames'][actual_last]) <= cap,
                         'Original final contact satisfies the actual main exit cap')
                    need(len(cap)==256 and len(c['frames'][frame])==8, 'Actual rank-eight endpoint cap')
                    intersection &= cap
                    dual = [v for v in range(1,512)
                            if all((v & b).bit_count()%2==0 for b in c['frames'][frame])]
                    need(len(dual)==1, 'Unique exact nonzero endpoint normal')
                    normals.append(dual[0])
                    total_paths += 1
                need(intersection=={0,line}, 'Exact point-set intersection is the claimed line')
                need(rank(normals)==8 and all((v&line).bit_count()%2==0 for v in normals),
                     'Independent dual elimination proves the same one-dimensional cap')
    return {'orientations':2,'early_native_outputs':24,'checked_paths':total_paths}


def rejected(call):
    try:
        call()
    except (ValueError,KeyError,IndexError,TypeError):
        return True
    return False


def main(write=False):
    c, programs = load_source()
    generated = make_certificate(c,programs['forward'])
    path = HERE/'CERTIFICATE.json'
    if write:
        path.write_text(json.dumps(generated,indent=2,sort_keys=True)+'\n')
    certificate = json.loads(path.read_text())
    need(certificate==generated, 'Deterministic regenerated source paths')
    checks = check_certificate(c,programs,certificate)
    controls = {}
    bad = deepcopy(certificate)
    bad['operators']['47']['positive']['line'] ^= 1
    controls['false_output_line'] = rejected(lambda:check_certificate(c,programs,bad))
    bad2 = deepcopy(certificate)
    bad2['operators']['47']['positive']['witnesses'][0]['frame'] = 1
    controls['changed_main_exit'] = rejected(lambda:check_certificate(c,programs,bad2))
    bad3 = deepcopy(certificate)
    witness = bad3['operators']['47']['positive']['witnesses'][0]
    witness['path'] = [witness['path'][0], witness['path'][-2], witness['path'][-1]]
    controls['invented_dependency_edge'] = rejected(lambda:check_certificate(c,programs,bad3))
    changed = deepcopy(programs)
    step = certificate['operators']['47']['positive']['witnesses'][0]['path'][1]
    changed['forward'][step] = ['warp',['L',133],999,0,0]
    controls['warp_instead_of_scalar'] = rejected(lambda:check_certificate(c,changed,certificate))
    raw = bytearray((ROOT/SOURCE).read_bytes());raw[-12] ^= 1
    controls['changed_frozen_source'] = rejected(lambda:load_source(bytes(raw)))
    need(all(controls.values()), 'All semantic corruption controls reject')
    print(json.dumps({'status':'PASS_EXACT_PRELUDE_MAIN_ENDPOINT_CAPS_NO_NEW_KAPPA',
                      'checks':checks, 'controls':controls},sort_keys=True))


if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--write',action='store_true')
    args = parser.parse_args()
    main(args.write)

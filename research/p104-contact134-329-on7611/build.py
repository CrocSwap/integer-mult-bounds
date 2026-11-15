#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Occurrence-bound #7611 134/329 common-contact construction.

Nomination by Terra-high agent 18; credit retained to Ali Romman,
DreamingOfClouds, SYLforge, Hao Yan, ToikY, Rohan Arun, Clear1nsight,
and their predecessors.  Source-only construction is not qualification.
"""
import argparse
import collections
import copy
import gzip
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
MANIFEST_SHA = '5d825fa2a208352ad0309202bdc63265dbf1a874fbd264a3460e5bc3d53dd4b4'
BASE_SHA = 'cb8c33817afbf7863074af90e3d287d1ef48c45a761f653143947ce2f58db1b6'
CANONICAL_SHA = '177b74c42ac633aaee21b0bbd5373441ccba8e5bad029d827877cf2d585fd0e3'
CALLS = 17
DELTA = {1:-34, 2:34, 3:-17, 4:-17, 5:17}
LITERALS = {
    41073:['MOVE',134,3,618,False],
    41074:['MOVE',329,373,618,False],
    41075:['ADD',134,329,'-1/2',618],
    41166:['MOVE',329,618,733,False],
    42110:['MOVE',134,618,913,False],
}
REPLACEMENTS = {
    41073:['MOVE',134,3,373,False],
    41075:['ADD',134,329,'-1/2',373],
    41166:['MOVE',329,373,733,False],
    42110:['MOVE',134,373,913,False],
}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def read(path):
    raw = Path(path).read_bytes()
    return json.loads(gzip.decompress(raw) if raw[:2] == b'\x1f\x8b' else raw)


def canonical(word):
    return json.dumps(word, sort_keys=True, separators=(',', ':')).encode()


def authenticate():
    manifest_raw = (HERE/'data/retained-hashes.json').read_bytes()
    require(digest(manifest_raw) == MANIFEST_SHA, 'retained manifest pin')
    manifest = json.loads(manifest_raw)
    root = HERE/'retained'
    require(len(manifest) == 166, 'complete 138+14+14 frozen source inventory')
    actual = {p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()}
    require(actual == set(manifest), 'complete retained source inventory')
    for name, sha in manifest.items():
        p = root/name
        require(not p.is_symlink() and p.resolve().is_relative_to(root.resolve()), 'source path '+name)
        require(digest(p.read_bytes()) == sha, 'source hash '+name)
    require(digest((root/'pr7611/data/word.json.gz').read_bytes()) == BASE_SHA, '7611 word bytes')


def apply_edits(program, edits):
    require(len(program) == edits['base_events'], 'lineage base length')
    deletes = {}
    for i, e in edits['delete']:
        require(i not in deletes and program[i] == e, 'lineage deleted literal')
        deletes[i] = e
    inserts = collections.defaultdict(list)
    for i, events in edits['insert_before']:
        require(0 <= i <= len(program), 'lineage insertion bound')
        inserts[i].extend(events)
    out=[]
    for i,e in enumerate(program):
        out.extend(inserts.get(i, []))
        if i not in deletes: out.append(e)
    out.extend(inserts.get(len(program), []))
    out.extend(edits['append'])
    return out


def source_word():
    authenticate()
    root=HERE/'retained'
    prior=read(root/'pr7605/data/word.json.gz')
    mid=read(root/'pr7608/data/word.json.gz')
    base=read(root/'pr7611/data/word.json.gz')
    require(read(root/'pr7608/data/base-7605-word.json.gz') == prior, '7608 base is 7605')
    require(read(root/'pr7611/data/base-7608-word.json.gz') == mid, '7611 base is 7608')
    for x,y,name in ((prior,mid,'pr7608'),(mid,base,'pr7611')):
        require(x.keys()==y.keys() and all(x[k]==y[k] for k in x if k!='program'), name+' header')
        require(apply_edits(x['program'],read(root/name/'data/edits.json'))==y['program'], name+' exact edit lineage')
    require(digest(canonical(base))==CANONICAL_SHA, '7611 canonical word pin')
    return base


def incident(e, field):
    return field in (e[1:3] if e[0] in ('ADD','COPY') else e[1:2])


def guard_incidents(p):
    # A separate guard permits mutation controls to exercise this exact check.
    require([(i,p[i]) for i in range(41073,42111) if incident(p[i],134)] == [(i,LITERALS[i]) for i in (41073,41075,42110)], '134 incident window')
    require([(i,p[i]) for i in range(41074,41167) if incident(p[i],329)] == [(i,LITERALS[i]) for i in (41074,41075,41166)], '329 incident window')


def build_word():
    word=source_word(); p=word['program']
    require(len(p)==76668, 'base event count')
    require(all(p[i]==e and p.count(e)==1 for i,e in LITERALS.items()), 'unique exact five literals')
    guard_incidents(p)
    result=copy.deepcopy(word)
    result['program']=[REPLACEMENTS.get(i,e) for i,e in enumerate(p) if i != 41074]
    q=result['program']
    require(len(q)==len(p)-1, 'exact one deleted move')
    scalar=lambda e: e[:-1] if e[0] in ('ADD','COPY','SCALE') else None
    require([scalar(e) for e in p if scalar(e) is not None] == [scalar(e) for e in q if scalar(e) is not None], 'scalar opcode operand coefficient stream')
    owner=lambda e:e[0] in ('INIT','CLEAR') or (e[0]=='MOVE' and e[4])
    require([e for e in p if owner(e)] == [e for e in q if owner(e)], 'ordered owner chronology')
    require([e for e in p if e[0]=='MOVE' and e[1] not in (134,329)] == [e for e in q if e[0]=='MOVE' and e[1] not in (134,329)], 'all other protected geometry unchanged')
    return result


def invoice():
    source=read(HERE/'retained/pr7611/data/invoice-new.json')
    result=copy.deepcopy(source)
    require(sum(source['paid'].values())==110281 and sum(source['targets'].values())==22461, '7611 complete invoice counts')
    for rank, change in DELTA.items():
        key=str(rank); require(key in result['paid'], 'rank present')
        result['paid'][key]+=change
        require(result['paid'][key]>=0, 'nonnegative paid')
    mass=lambda h:sum(int(k)*v for k,v in h.items())
    require(sum(result['paid'].values())==110264, 'complete candidate paid count')
    require(mass(result['targets'])-mass(result['paid']) == 1424, 'complete rank surplus')
    return result


def validate_invoice(actual):
    require(actual == invoice(), 'stored complete candidate invoice')


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--write',action='store_true');args=parser.parse_args()
    word=build_word(); bill=invoice()
    if args.write:
        (HERE/'data/word.json.gz').write_bytes(gzip.compress(json.dumps(word,separators=(',', ':')).encode(),mtime=0))
        (HERE/'data/invoice-new.json').write_text(json.dumps(bill,indent=2)+'\n')
    require(read(HERE/'data/word.json.gz')==word, 'stored exact candidate word')
    validate_invoice(read(HERE/'data/invoice-new.json'))
    print(json.dumps({'status':'PASS_LITERAL_BUILD','candidate_sha256':digest(canonical(word)),'events':len(word['program']),'delta_paid':DELTA,'delta_targets':{}}))

if __name__=='__main__': main()

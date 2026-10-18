#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Sharp ten-coordinate threshold for two degenerate triple endpoint pairs."""
import argparse
import ast
from collections import Counter
import hashlib
from itertools import combinations
import json
from math import comb
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
BASE='ba82555c64e1879e4b7decce28186f208fcb8262'
REQUIRED=('research/complex-parity-frames-seed35/README.md',
          'research/complex-parity-frames-seed35/check.py',
          'research/complex-parity-frames-seed35/CERTIFICATE.json',
          'docs/research/parity-side.md')


def need(ok,why):
    if not ok:
        raise ValueError(why)


def canon(x):
    return json.dumps(json.loads(json.dumps(x)),sort_keys=True,separators=(',',':'),allow_nan=False)


def read(p):
    return json.loads(p.read_text(encoding='utf8'))


def sha(p):
    return hashlib.sha256(p.read_bytes().replace(b'\r\n',b'\n')).hexdigest()


def pins(root=ROOT,here=HERE):
    data=read(here/'SOURCES.json')
    need(data['base_commit']==BASE and set(data['files'])==set(REQUIRED),'exact source inventory')
    for name in REQUIRED:
        need(sha(root/name)==data['files'][name],'source hash: '+name)
    need(sha(here/'BASE-SELECTED.json')==data['selected_snapshot_sha256'],'selected snapshot')
    # Bind the predecessor's existing unpermuted positive fixture by parsing,
    # without executing its checker or copying its frame algorithms.
    tree=ast.parse((root/REQUIRED[1]).read_text(encoding='utf8'))
    fixtures={}
    for node in ast.walk(tree):
        if isinstance(node,ast.Assign) and len(node.targets)==1 and isinstance(node.targets[0],ast.Name):
            name=node.targets[0].id
            if name in ('aa','bb','uu') and isinstance(node.value,ast.Call):
                call=node.value.args[0]
                if isinstance(call,ast.Call) and isinstance(call.func,ast.Name) and call.func.id=='map':
                    fixtures[name]=ast.literal_eval(call.args[1])
    need(fixtures=={'aa':(7,25),'bb':(224,800),'uu':(7,25,4,16)},'predecessor witness binding')


def dot(a,b):
    return (a&b).bit_count()%2


def span(vs):
    ans={0}
    for v in vs:
        ans|={x^v for x in tuple(ans)}
    return ans


def scalar(s,t):
    n=(s&t).bit_count()
    return (1,0,-1,0)[n]


def admissible_pair(s,t):
    need(len(set(s+t))==4,'four distinct labels')
    need(all(x.bit_count()==3 for x in s+t),'triple labels')
    need(dot(*s)==dot(*t)==1,'two degenerate pairs')
    need(all(dot(x,y)==0 for x in s for y in t),'cross orthogonality')
    need(scalar(s[0],t[0])*scalar(s[1],t[1])==scalar(s[0],t[1])*scalar(s[1],t[0]),'scalar rank one')
    need(span(s)&span(t)=={0},'common span')


def nondegenerate(space):
    return all(x==0 or any(dot(x,y) for y in space) for x in space)


def onb(space):
    need(nondegenerate(space),'degenerate residual')
    if len(space)==1:
        return []
    for v in sorted(space):
        if not dot(v,v):
            continue
        rest={x for x in space if not dot(x,v)}
        if len(rest)>1 and not any(dot(x,x) for x in rest):
            continue
        result=[v]+onb(rest)
        need(span(result)==space and all(dot(x,y)==int(i==j) for i,x in enumerate(result) for j,y in enumerate(result)),'orthonormal basis')
        return result
    raise ValueError('alternating residual')


def frame(n,s,t,generators):
    u=span(generators)
    need(nondegenerate(u),'degenerate frame')
    v={x for x in range(1<<n) if all(not dot(x,y) for y in generators)}
    need(set(s)<=u and set(t)<=v,'frame containment')
    records=[]
    for side,space,labels in [('source',u,s),('target',v,t)]:
        for label in labels:
            residual={x for x in space if not dot(x,label)}
            records.append(dict(side=side,label=label,dimension=(len(residual)-1).bit_length(),orthonormal_basis=onb(residual)))
    return dict(ambient=n,frame_basis=list(generators),frame_dimension=(len(u)-1).bit_length(),residuals=records)


def census(n):
    s=(7,25)
    triples=[sum(1<<i for i in c) for c in combinations(range(n),3)]
    targets=[t for t in triples if all(not dot(t,x) for x in s)]
    counts=Counter(); accepted=[]
    for t in combinations(targets,2):
        if not dot(*t):
            continue
        counts['cross_orthogonal_degenerate']+=1
        if scalar(s[0],t[0])*scalar(s[1],t[1])!=scalar(s[0],t[1])*scalar(s[1],t[0]):
            counts['scalar_rank_two']+=1
            continue
        counts['scalar_rank_one']+=1
        if span(s)&span(t)!={0}:
            counts['common_radical']+=1
            continue
        counts['admissible_algebraic_rectangles']+=1
        need(all(not (x&31) for x in t),'support classification')
        admissible_pair(s,t)
        accepted.append(list(t))
    expected=15*comb(n-5,5) if n>=10 else 0
    need(len(accepted)==expected,'universal count formula')
    counts['admissible_algebraic_rectangles']+=0
    return dict(ambient=n,triple_labels=len(triples),eligible_targets=len(targets),counts=dict(sorted(counts.items())),
                accepted_target_pairs=accepted,fixed_source_formula=expected,
                all_labeled_source_pairs=15*comb(n,5),all_labeled_rectangles=15*comb(n,5)*expected)


def build():
    rows=[census(n) for n in range(5,13)]
    witness=frame(10,(7,25),(224,800),(7,25,4,16))
    admissible_pair((7,25),(224,800))
    all_witnesses=[]
    for pair in rows[5]['accepted_target_pairs']:
        all_witnesses.append(dict(targets=pair,frame=frame(10,(7,25),tuple(pair),(7,25,4,16))))
    return dict(schema='triple-shared-frame-threshold/1',base_commit=BASE,canonical_sources=[7,25],
                classification='All scalar-shareable, disjoint-span degenerate triple rectangles have disjoint source/target supports.',
                sharp_minimum_ambient=10,census=rows,predecessor_sharp_witness=witness,
                dimension_ten_frames=all_witnesses,scope='One shared scalar node and historical orthonormal-residual interface only; no supplier or kappa.')


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--write-certificate',action='store_true');args=parser.parse_args()
    pins();result=build();path=HERE/'CERTIFICATE.json'
    if args.write_certificate:
        need(not path.exists(),'refusing certificate overwrite')
        path.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n',encoding='utf8')
    need(canon(read(path))==canon(result),'certificate mismatch')
    print('PASS_TRIPLE_SHARED_FRAME_THRESHOLD: sharp h=10; canonical h=5..12; 15 sharp frames; all-dimension classification')


if __name__=='__main__':
    main()

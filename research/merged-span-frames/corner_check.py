#!/usr/bin/env python3
"""Independent dense-integer checks of PR96 ranks on actual selected frames.

This is representative exact algebra evidence, not a complete physical proof.
No floating arithmetic or modular rank inference is used in this audit.
"""
import ast
import argparse
from hashlib import sha256
import gzip
import importlib.util
import json
from math import gcd
from pathlib import Path
import random
import sys

if sys.flags.optimize:raise ValueError('Assertions required')
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
PACKAGE=HERE
AXIS_DIR=None
SOURCE=ROOT/'references/frame-compiler/pr96/scripts/experiments/merged_exterior.py'

def rank(matrix):
    if not matrix or not matrix[0]:return 0
    if len(matrix)>len(matrix[0]):matrix=list(map(list,zip(*matrix)))
    pivots={}
    for source in matrix:
        row=list(source)
        for j,pivot in pivots.items():
            if row[j]:
                a,b=pivot[j],row[j]
                common=gcd(a,b);a//=common;b//=common
                row=[a*x-b*y for x,y in zip(row,pivot)]
                factor=0
                for x in row:factor=gcd(factor,x)
                if factor>1:row=[x//factor for x in row]
        j=next((j for j,x in enumerate(row) if x),None)
        if j is not None:pivots[j]=row
    return len(pivots)

def dense_projector(core,cover,h,complement):
    """Direct fixed-I+J entry formula; no low-rank classes/kernel helpers."""
    c=core.bit_count();outside=cover&~core;n=outside.bit_count();s=3-c
    denominator=6*(h+1) if c==3 else 3*(h+1)*(s*s+(c-1)*n)
    result=[]
    for i in range(h):
        oi=(outside>>i)&1;wi=3+((core>>i)&1);row=[]
        for j in range(h):
            oj=(outside>>j)&1;zj=3*(h+1)*((core>>j)&1)-10
            value=wi*zj if c==3 else (denominator*int(i==j)*oi+s*oi*zj+
                3*(h+1)*s*wi*oj+n*wi*zj-3*(h+1)*(c-1)*oi*oj)
            row.append(denominator*int(i==j)-value if complement else value)
        result.append(row)
    return result,denominator

def subrank(N,S,T):
    h=len(N)
    return rank([[N[i][j] for j in range(h) if T>>j&1] for i in range(h) if S>>i&1])

def check_layout():
    path=ROOT/'research/copied-fixed/reversed/pr34/independent_controls.py'
    manifest=json.loads((path.parent.parent/'geometry-source.json').read_text())
    assert sha256(path.read_bytes()).hexdigest()==manifest['sha256']['pr34/independent_controls.py']
    tree=ast.parse(path.read_text())
    chosen=[node for node in tree.body if isinstance(node,ast.FunctionDef) and node.name in ('completion','corner_labels')]
    assert len(chosen)==2
    namespace={};exec(compile(ast.Module(body=chosen,type_ignores=[]),str(path),'exec'),namespace)
    permutations=namespace['completion'](23,*namespace['corner_labels'](23))
    assert permutations==me.PERMS
    return path

def run():
    controls=check_layout();rng=random.Random(96002325);axes={};hashes={}
    for h,folder in ((23,'coordinate-23'),(25,'coordinate94-25')):
        path=(AXIS_DIR/folder/'word.json.gz') if AXIS_DIR else PACKAGE/f'word-{h}.json.gz'
        word=json.loads(gzip.decompress(path.read_bytes()))
        frames=word['frames'];selected=set()
        for c in (1,2,3):
            ids=[i for i,(core,cover) in enumerate(frames) if core.bit_count()==c]
            if ids:
                key=lambda i:(1 if c==3 else frames[i][1].bit_count()-c,i)
                selected.update((min(ids,key=key),max(ids,key=key)))
        local=me.local_index(h);other=[i%25 if h==23 else me.PERMS[i%25][i//25] for i in range(575)]
        assert sorted(zip(local,other))==[(a,b) for a in range(h) for b in range(575//h)]
        prefix,suffix=me.flags(local);full=(1<<h)-1;records=[]
        for frame in sorted(selected):
            core,cover=frames[frame]
            for complement in (False,True):
                N,d=dense_projector(core,cover,h,complement)
                assert all(sum(N[i][k]*N[k][j] for k in range(h))==d*N[i][j] for i in range(h) for j in range(h))
                r=rank(N);operator=me.operator(core,cover,h,complement)
                expected=1 if core==cover else cover.bit_count()-core.bit_count()
                assert r==(h-expected if complement else expected)
                masks=[(full,full),(core,cover),(cover,core),(0,full),(full,0)]
                masks += [(rng.randrange(1<<h),rng.randrange(1<<h)) for _ in range(20)]
                masks += [(prefix[i+1],suffix[j]) for i,j in ((0,0),(h-1,h),(2*h,2*h+1),(2*h,575-2*h))]
                for S,T in masks:assert subrank(N,S,T)==me.rank(operator,S,T),(h,frame,complement,S,T)
                corners=[(h-1,0),(h+3,h-2),(2*h,2*h+1),(2*h,575-2*h),(575-h-2,575-h-1),(574,575-h)]
                n=575//h;line=[int(i<3) for i in range(n)]
                v=[3+t for t in line];nu=[3*(n+1)*t-10 for t in line];den=6*(n+1)
                assert sum(x*y for x,y in zip(v,nu))==den and all(v) and all(nu)
                for i,j in corners:
                    actual=rank([[d*den*int(k==ell)-N[local[k]][local[ell]]*v[other[k]]*nu[other[ell]]
                        for ell in range(j,575)] for k in range(i+1)])
                    expected=(i-j+1-r+subrank(N,prefix[j],full)+subrank(N,full,suffix[i+1])
                        if j<=i+1 else subrank(N,prefix[i+1],suffix[j]))
                    assert actual==expected,(h,frame,complement,i,j,actual,expected)
                records.append(dict(frame=frame,core=core,cover=cover,complement=complement,
                    exact_projector_rank=r,local_submatrices_checked=len(masks),physical_corners_checked=len(corners)))
        axes[str(h)]=dict(roles=word['R'],representative_actual_frames=len(selected),operators=records)
        hashes[str(path.resolve().relative_to(ROOT)) if path.resolve().is_relative_to(ROOT) else str(path.resolve())]=sha256(path.read_bytes()).hexdigest()
        print('PASS representative exact local and physical corners h',h,flush=True)
    for path in (SOURCE,controls,Path(__file__)):hashes[str(path.resolve().relative_to(ROOT)) if path.resolve().is_relative_to(ROOT) else str(path.resolve())]=sha256(path.read_bytes()).hexdigest()
    receipt=dict(status='PASS representative exact dense-integer corner audit',axes=axes,input_sha256=hashes,
        arithmetic='Fraction-free integer Gaussian elimination with exact gcd reduction; direct entry projector formula; no modular or floating inference.',
        scope='Actual frozen h23/h25 frames, both projector complements, exact physical PR34 layout and rank-one line. Representative corner evidence, not all selected matrices or endpoint topology. Endpoint multiplicative-gauge and full paid-ledger audits are separate.')
    return receipt

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package-dir',type=Path,default=HERE)
    parser.add_argument('--repo-root',type=Path)
    parser.add_argument('--axis-dir',type=Path)
    parser.add_argument('--profiler',type=Path)
    parser.add_argument('--record',action='store_true')
    parser.add_argument('--output',type=Path)
    args=parser.parse_args();PACKAGE=args.package_dir.resolve()
    ROOT=(args.repo_root or PACKAGE.parents[1]).resolve()
    AXIS_DIR=args.axis_dir.resolve() if args.axis_dir else None
    SOURCE=args.profiler.resolve() if args.profiler else ROOT/'references/frame-compiler/pr96/scripts/experiments/merged_exterior.py'
    spec=importlib.util.spec_from_file_location('pr96_formula',SOURCE)
    me=importlib.util.module_from_spec(spec);spec.loader.exec_module(me)
    result=run();output=args.output or PACKAGE/'corner-audit.json'
    if args.record:output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    else:assert result==json.loads(output.read_text()),'Corner audit receipt differs'
    print(result['status'],flush=True)

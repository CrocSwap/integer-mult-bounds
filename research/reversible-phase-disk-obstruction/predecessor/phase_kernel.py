#!/usr/bin/env python3
"""Executable norm-preserving phase interface; ywz65/Codex, Apache-2.0."""
from fractions import Fraction as F
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]


def need(ok,message):
    if not ok:
        raise ValueError(message)


def load():
    records=[(ROOT/r['path'],r) for r in json.loads((HERE/'SOURCES.json').read_text())['files']]
    records += [(HERE/r['local_path'],r) for r in json.loads((HERE/'PREDECESSORS.json').read_text())]
    for path,r in records:
        b=path.read_bytes()
        need(hashlib.sha256(b).hexdigest()==r['sha256'],'source SHA: '+str(path))
        need(hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==r['git_blob'],'source blob')
    spec=importlib.util.spec_from_file_location('pinned_phase_intervals',HERE/'source/intervals.py')
    m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)
    return m


def trunc(n,d):
    return n//d if n>=0 else -((-n)//d)


def phase_product(m,x,box,p):
    """Integer numerators on the p-grid. The box must enclose the unit phase.

    Unit-phase enclosure is a mathematical input contract. Width, grids, input
    disk and the extracted phase disk are checked here before multiplication.
    """
    need(type(p) is int and p>=1,'precision')
    scale=1<<p
    need(len(x)==2 and all(type(a) is int for a in x),'integer payload')
    need(sum(a*a for a in x)<=scale*scale,'input disk')
    q=box[0].bits
    need(q>=p+1 and box[1].bits==q,'common fine grid')
    need(all(z.hi-z.lo<=1<<(q-p-1) for z in box),'phase enclosure width')
    w,_=m.inward_quantize(box,p)
    need(sum(a*a for a in w)<=scale*scale,'phase disk')
    return (trunc(x[0]*w[0]-x[1]*w[1],scale),
            trunc(x[0]*w[1]+x[1]*w[0],scale))


def rect_error(x,y,box,p):
    """All four exact rectangle corners; convex squared norm bounds the box."""
    q=box[0].bits
    for a,b in itertools.product((box[0].lo,box[0].hi),(box[1].lo,box[1].hi)):
        er=(y[0]<<q)-(x[0]*a-x[1]*b)
        ei=(y[1]<<q)-(x[0]*b+x[1]*a)
        need(er*er+ei*ei < 16*(1<<(2*q)),'four-h phase-product error')


def rejection(f):
    try:f()
    except ValueError:return
    raise ValueError('control accepted')


def run():
    m=load()
    need(F(25,2)<16,'uniform squared constant')
    phases=set()
    for a in range(7):
        for b in range(1,5):
            t=F(a,b);x=(1-t*t)/(1+t*t);y=2*t/(1+t*t)
            for _ in range(4):
                phases.add((x,y));x,y=-y,x
    exact_cases=0
    for p in (2,3,4):
        scale=1<<p
        inputs=[(a,b) for a in range(-scale,scale+1) for b in range(-scale,scale+1)
                if a*a+b*b<=scale*scale]
        for a,b in sorted(phases):
            need(a*a+b*b==1,'rational phase')
            box=m.point(a,b,p+8)
            for x in inputs:
                y=phase_product(m,x,box,p)
                need(sum(t*t for t in y)<=sum(t*t for t in x),'norm increase')
                er=F(y[0])-x[0]*a+x[1]*b
                ei=F(y[1])-x[0]*b-x[1]*a
                need(er*er+ei*ei<16,'exact rational four-h error')
                rect_error(x,y,box,p)
                exact_cases+=1
    roots,cases,max_width_ratio=0,0,F(0)
    for p in (2,8,16):
        scale=1<<p
        inputs=[(scale,0),(-scale,0),(0,scale),(0,-scale),(scale//2,scale//2),
                (-scale//2,scale//2),(1,-1),(0,0)]
        for k in range(2,33):
            for j in range(k):
                box=m.root_of_unity(j,k,p+16)
                roots+=1
                max_width_ratio=max(max_width_ratio,*(F(c.hi-c.lo,1<<16) for c in box))
                for x in inputs:
                    y=phase_product(m,x,box,p)
                    need(sum(t*t for t in y)<=sum(t*t for t in x),'root norm increase')
                    rect_error(x,y,box,p);cases+=1
    # Actual rounding alternatives falsify the norm conclusion.
    nearest=tuple((2*n+29)//58 for n in (84,80))
    need(nearest==(3,3) and sum(x*x for x in nearest)>4*4,'nearest phase rounding control')
    need(trunc(84,29)==2 and trunc(80,29)==2,'inward phase fixture')
    floored=(-12//5,16//5)
    need(sum(x*x for x in floored)>4**2,'signed-floor phase control')
    box=m.point(F(4,5),F(3,5),10)
    need(phase_product(m,(-1,0),box,2)==(0,0),'inward product fixture')
    w,_=m.inward_quantize(box,2)
    bad=(-w[0]//4,-w[1]//4)
    need(sum(x*x for x in bad)>1,'signed-floor product norm control')
    wide=(m.Interval(-1024,1024,10),m.Interval(-1024,1024,10))
    rejection(lambda:phase_product(m,(4,0),wide,2))
    rejection(lambda:phase_product(m,(5,0),box,2))
    return dict(status='PASS_INWARD_UNIT_PHASE_CONTRACT',rational_phases=len(phases),
                exhaustive_disk_products=exact_cases,root_enclosures=roots,root_products=cases,
                max_phase_component_width_over_h=str(max_width_ratio),semantic_controls=5,
                uniform_bound='norm(out)<=norm(input), error<=sqrt(25/2)*h<4*h',
                scope='Unit-phase enclosure contract and exact integer kernel; generator analysis and outer complexity remain separate.')


if __name__=='__main__':
    result=run();path=HERE/'RESULT.json'
    if sys.argv[1:]==['--write-receipt']:
        need(not path.exists(),'refuse receipt overwrite')
        path.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    else:
        need(not sys.argv[1:],'unknown arguments')
        need(result==json.loads(path.read_text()),'receipt mismatch')
    print(json.dumps(result,indent=2))

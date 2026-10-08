#!/usr/bin/env python3
"""Rebuild four-point stars in a previously certified direct producer.

This screen checks every replacement boundary with exact masks. It does not
combine its savings with the separate common-frame fusion certificate.
"""
from collections import Counter
from hashlib import sha256
from pathlib import Path
import argparse
import json
import subprocess
import struct
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
from prime_field_circuit import optimize


def check_template(targets,gates):
    available={1<<i for mask in targets for i in range(mask.bit_length()) if mask>>i&1}
    for a,b in gates:
        if a not in available or b not in available or a&b or a|b in available:
            raise ValueError('Invalid disjoint replacement gate')
        available.add(a|b)
    if any(mask not in available for mask in targets):
        raise ValueError('Missing replacement boundary')


def resynthesize(demands,h,template_path=None):
    cache={};old_total=new_total=improved=0;histogram=Counter()
    digest=sha256();selected=[]
    for line in Path(demands).read_text().splitlines():
        core,old,*masks=map(int,line.split())
        # Preserve the original recursive point order; no graph-isomorphism
        # assumption is needed, since the full target tuple is the cache key.
        points=[j for j in range(h) if not core>>j&1]
        key=tuple(sorted(sum(1<<i for i,j in enumerate(points) if mask>>j&1) for mask in masks))
        if key not in cache:
            gates=optimize(list(key))
            check_template(key,gates)
            cache[key]=gates
        gates=cache[key]
        new=min(old,len(gates))
        if new<old:
            expand=lambda mask:sum(1<<j for i,j in enumerate(points) if mask>>i&1)
            selected.append((core,sorted(masks),[(expand(a),expand(b)) for a,b in gates]))
        old_total+=old;new_total+=new;improved+=new<old;histogram[old-new]+=1
        digest.update(json.dumps([core,old,key,gates],separators=(',',':')).encode())
    if template_path is not None:
        with Path(template_path).open('wb') as stream:
            def words(values):stream.write(struct.pack('<'+'I'*len(values),*values))
            words([h,len(selected)])
            for core,targets,gates in selected:
                words([core,len(targets),len(gates),*targets])
                words([x for pair in gates for x in pair])
    return dict(old_star_additions=old_total,new_star_additions=new_total,
                saved_additions=old_total-new_total,improved_stars=improved,
                templates=len(cache),savings_histogram=dict(sorted(histogram.items())),
                exact_template_sha256=digest.hexdigest(),every_replacement_disjoint=True,
                every_boundary_sum_checked=True)


def screen(dag,producer,workdir):
    producer=json.loads(Path(producer).read_text())
    dag=Path(dag)
    with dag.open('rb') as stream:
        digest=sha256()
        for chunk in iter(lambda:stream.read(1<<20),b''):digest.update(chunk)
    if digest.hexdigest()!=producer['dag_sha256']:
        raise ValueError('DAG does not match certified producer')
    for name,value in producer['proof_sha256'].items():
        if sha256((ROOT/name).read_bytes()).hexdigest()!=value:
            raise ValueError('Stale producer source: '+name)
    workdir=Path(workdir);workdir.mkdir(parents=True,exist_ok=True)
    binary=workdir/'star-demands';demands=workdir/'demands.txt'
    subprocess.run(['c++','-O3','-std=c++17',str(Path(__file__).with_name('ternary_star_demands.cpp')),'-o',str(binary)],check=True)
    extracted=json.loads(subprocess.check_output([str(binary),str(dag),str(demands)],text=True))
    if extracted['additions']!=producer['support']['retained_additions']:
        raise ValueError('Producer addition count mismatch')
    replacement=resynthesize(demands,extracted['h'])
    if replacement['old_star_additions']!=extracted['old_star_additions']:
        raise ValueError('Star count mismatch')
    return dict(status='EXACT LOCAL RESYNTHESIS; ASSEMBLY AND COMPOSITION CHECKS SEPARATE',
                predecessor_dag_sha256=producer['dag_sha256'],extracted=extracted,
                replacement=replacement,
                roles=extracted['additions']+extracted['outputs']-replacement['saved_additions'])


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--dag',type=Path,required=True)
    p.add_argument('--producer',type=Path,default=ROOT/'certificates/ternary-target-network.json')
    p.add_argument('--workdir',type=Path,required=True)
    p.add_argument('--output',type=Path)
    args=p.parse_args();result=screen(args.dag,args.producer,args.workdir)
    text=json.dumps(result,sort_keys=True,indent=2)+'\n'
    if args.output:args.output.write_text(text)
    print(text,end='')

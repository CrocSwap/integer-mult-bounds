#!/usr/bin/env python3
"""Exact source-bound nearest-chart census. Apache-2.0; OpenAI assistance."""
import argparse
from hashlib import sha256
import importlib.util
import itertools
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
sys.path.insert(0,str(Path(__file__).resolve().parent))
import algebra as A
import discover as D
import intervals as I


def authenticate():
    for row in json.loads((A.HERE/'SOURCES.json').read_text())['files']:
        if row['usage']=='input':
            p=A.ROOT/row['path']
            A.need(not p.is_symlink() and sha256(p.read_bytes()).hexdigest()==row['sha256'],'exact source '+row['path'])


def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec)
    sys.modules[name]=mod
    spec.loader.exec_module(mod)
    return mod


def geometry():
    total=images=0
    for n in (1,2,3):
        first=A.canonical([1<<(n+i) for i in range(n)])
        spaces,todo={first},[first]
        while todo:
            old=todo.pop()
            direct={A.turn(old,axis,n) for axis in range(1,1<<(2*n))}-{old}
            generated=list(A.neighbors(old,n))
            actual={s for _,s in generated}
            A.need(len(generated)==2*((1<<n)-1)==len(actual),'distinct complete neighbors')
            A.need(actual==direct,'independent exhaustive nonzero-axis enumeration')
            for axis,chart in generated:
                A.need(A.distance(old,chart,n)==1 and A.turn(chart,axis,n)==old,'exact neighbor and inverse')
            for chart in direct-spaces:
                spaces.add(chart)
                todo.append(chart)
            images+=(1<<(2*n))-1
        A.need(len(spaces)=={1:3,2:15,3:135}[n],'full tiny Lagrangian count')
        total+=len(spaces)
    return dict(lagrangians=total,brute_force_axis_images=images)


def literal_geometry():
    ce=load(A.ROOT/'research/t74-native-fast/vendor/native/new/code/borrow/vendor/clifford/clifford_exact.py','chart_clifford')
    # Reuse the credited literal quarter-turn circuit, not its rank model.
    sys.path.insert(0,str(A.ROOT/'research/general-gaussian-contact-search'))
    previous=load(A.ROOT/'research/general-gaussian-contact-search/verify.py','chart_literal_circuit')
    source=A.predecessor()
    pairs=compositions=0
    for n in (1,2):
        spaces={frozenset({0}):[]}
        for value in range(1,1<<n):
            for span,basis in list(spaces.items()):
                if value not in span:
                    spaces.setdefault(frozenset(span|{x^value for x in span}),basis+[value])
        old={s:A.canonical(source.lagrangian(b,n)) for s,b in spaces.items()}
        ops={s:ce.canonical_frame(n,b) for s,b in spaces.items()}
        low=(1<<n)-1
        for x in range(1,1<<(2*n)):
            rx=previous.pauli_rotation(ce,n,x&low,x>>n)
            for y in range(1,1<<(2*n)):
                ry=previous.pauli_rotation(ce,n,y&low,y>>n)
                for a,b in itertools.product(spaces,repeat=2):
                    left=rx.then(ops[a]);right=ry.then(ops[b])
                    physical=left.adjoint().then(right)
                    expected=A.distance(A.turn(old[a],x,n),A.turn(old[b],y,n),n)
                    A.need(ce.rank([u for u,z,p in physical.tab[n:]])==expected,'literal independent-axis rank')
                    pairs+=1
                for a in spaces:
                    twice=ry.then(rx.then(ops[a]))
                    relative=twice.adjoint().then(ops[a])
                    expected=A.distance(A.turn(A.turn(old[a],x,n),y,n),old[a],n)
                    A.need(ce.rank([u for u,z,p in relative.tab[n:]])==expected,'noncommuting sequential composition')
                    compositions+=1
    return dict(independent_axis_pairs=pairs,sequential_compositions=compositions,dimensions=[1,2])


def witness_delta(model,node,axis):
    A.need(node not in model['frozen'],'unfrozen witness')
    charts=model['charts'];trial=A.turn(charts[node],axis,9)
    A.need(A.distance(charts[node],trial,9)==1,'nearest witness')
    delta=[0]*10
    for a,b,op,sign in model['contacts']:
        if node not in (a,b):continue
        olda,oldb=charts[a],charts[b]
        newa=trial if a==node else olda
        newb=trial if b==node else oldb
        if op:
            olda=tuple(A.linear(model['operators'][op],v) for v in olda)
            newa=tuple(A.linear(model['operators'][op],v) for v in newa)
        r0=A.distance(olda,oldb,9);r1=A.distance(newa,newb,9)
        A.need(sign>0 or r1>0,'strict productive helper')
        if r0:delta[r0]-=sign
        if r1:delta[r1]+=sign
    return delta


def census(binary,collapse):
    model=A.build(collapse);data=D.encoded(model)
    output=subprocess.run([str(binary),'certificate','0','0'],input=data,text=True,capture_output=True,check=True,timeout=120).stdout.splitlines()
    header=output[0].split()
    A.need(header[0]=='CENSUS' and len(header)==4,'complete census header')
    valid,invalid,total=map(int,header[1:]);patterns=[]
    for line in output[1:]:
        fields=line.split()
        A.need(fields[0]=='PAT' and len(fields)==14,'exact histogram row')
        row=list(map(int,fields[1:]));count,delta,node,axis=row[0],row[1:11],row[11],row[12]
        A.need(count>0 and delta[0]==0,'histogram multiplicity and zero-rank convention')
        A.need(witness_delta(model,node,axis)==delta,'independent witness invoice')
        patterns.append(dict(count=count,delta=delta,witness=[node,axis]))
    free=len(model['charts'])-len(model['frozen'])
    A.need(sum(p['count'] for p in patterns)==valid and valid+invalid==1022*free,'complete neighbor count')
    A.need(total==len(patterns)==len({tuple(p['delta']) for p in patterns}),'unique complete histogram')
    paid,helper=A.invoice(model,model['charts'])
    return dict(collapse_zero=collapse,groups=len(model['charts']),free_groups=free,
                original_nodes=model['original_nodes'],incidences=len(model['contacts']),
                graph_sha256=sha256(data.encode()).hexdigest(),valid_moves=valid,invalid_moves=invalid,
                patterns=patterns,interval_proof=I.certify(patterns),
                unchanged_rank_polynomial_moves=sum(p['count'] for p in patterns if not any(p['delta'])),
                baseline_paid=dict(sorted(paid.items())),baseline_helpers=dict(sorted(helper.items())))


def reject(call,why):
    try:call()
    except ValueError:return
    raise ValueError('negative control accepted: '+why)


def controls():
    model=A.build();charts=list(model['charts']);node=model['frozen'][0]
    _,charts[node]=next(A.neighbors(charts[node],9))
    reject(lambda:A.invoice(model,charts),'changed frozen chart')
    charts=list(model['charts']);node=next(i for i in range(len(charts)) if i not in model['frozen'])
    charts[node]=tuple([charts[node][0]]*9)
    reject(lambda:A.invoice(model,charts),'rank-deficient chart')
    reject(lambda:I.certify([dict(delta=[0,-1]+[0]*8)]),'unpaid rank-one omission')
    old=A.canonical([4,8]);_,new=next(A.neighbors(old,2))
    A.need(A.distance(old,new,2)==1 and A.distance(new,new,2)==0,'positive descent calibration')
    return dict(rejected_controls=3,positive_rank_descent=True)


def walks():
    rows=json.loads((A.HERE/'DISCOVERY.json').read_text())
    count=0
    for row in rows:
        model=A.build(row['collapse_zero'])
        A.need(sha256(D.encoded(model).encode()).hexdigest()==row['graph_sha256'],'walk graph identity')
        A.need(sha256((A.HERE/'search.cpp').read_bytes()).hexdigest()==row['search_sha256'],'walk exact compiled source')
        charts=D.replay(model,row['moves'])
        paid,helper=A.invoice(model,charts)
        A.need(json.loads(json.dumps(dict(paid)))==row['paid'],'walk final complete paid invoice')
        A.need(json.loads(json.dumps(dict(helper)))==row['helpers'],'walk final complete helper invoice')
        A.need(sha256(json.dumps(charts,separators=(',',':')).encode()).hexdigest()==row['final_chart_sha256'],'walk final chart hash')
        A.need(row['paid']==row['baseline_paid'] and row['helpers']==row['baseline_helpers'],'recorded unchanged exploratory profiles')
        count+=len(row['moves'])
    return dict(runs=len(rows),accepted_moves=count,scope='Exact final rank-invoice replay only; floating discovery and plateau coverage are not certified optimal.')


def run():
    authenticate();small=geometry();literal=literal_geometry();control=controls();walk=walks()
    compiler=shutil.which('g++') or shutil.which('clang++')
    A.need(compiler is not None,'C++17 compiler required for actual full census')
    with tempfile.TemporaryDirectory(prefix='chart-census-') as tmp:
        binary=Path(tmp)/'search'
        subprocess.run([compiler,'-std=c++17','-O3','-Wall','-Wextra','-Werror',str(A.HERE/'search.cpp'),'-o',str(binary)],check=True)
        rows=[census(binary,True),census(binary,False)]
    return dict(status='PASS_EXHAUSTIVE_NEAREST_CLIFFORD_CENSUS_NO_NEW_KAPPA',
                source_base='81e9bd69e4a5b00ba9c713a1620e36d576d5522e',census=rows,
                geometry=small,literal_geometry=literal,controls=control,exploratory_walk_replay=walk,
                scope='Finite source-bound local obstruction for 0<=C<=1/200; joint moves, arbitrary independent assignments, changed words and native maps remain open.')


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');args=ap.parse_args()
    result=json.loads(json.dumps(run(),sort_keys=True));path=A.HERE/'RESULT.json'
    if args.write:path.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    else:A.need(result==json.loads(path.read_text()),'fresh complete census matches receipt')
    print(json.dumps(dict(status=result['status'],geometry=result['geometry'],literal_geometry=result['literal_geometry'],
                         moves=[r['valid_moves'] for r in result['census']],patterns=[len(r['patterns']) for r in result['census']],
                         interval_C=['0','1/200'],controls=result['controls']),sort_keys=True))


if __name__=='__main__':main()

#!/usr/bin/env python3
"""Complete #7000 paid/helper chart catalogue, including inherited maps.

Reuses the pinned producer's Clifford compiler and distinct exact signed-Pauli
and Gaussian phase interpreter; it does not call the old delta-only checker.
Credit the retained compiler and independent-native authors. OpenAI Codex
assistance for Douglas Colkitt; Apache-2.0.
"""
from pathlib import Path
from hashlib import sha256
import copy
import gzip
import importlib.util
import json
import sys
import argparse

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
PACKAGE=ROOT/'research/shared-wire-split-composition'


def need(ok,message):
    if not ok:raise ValueError(message)


def module(relative,name):
    path=PACKAGE/relative
    pins=json.loads((HERE/'SOURCES.json').read_text())['files']
    expected=next(p['sha256'] for p in pins if p['path']==path.relative_to(ROOT).as_posix())
    need(sha256(path.read_bytes()).hexdigest()==expected,'engine source hash')
    spec=importlib.util.spec_from_file_location(name,path)
    value=importlib.util.module_from_spec(spec);sys.modules[name]=value;spec.loader.exec_module(value)
    return value


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--start',type=int,default=0)
    parser.add_argument('--stop',type=int)
    args=parser.parse_args()
    need(not sys.flags.optimize,'retained compiler assertions must be enabled')
    C=module('frozen/clifford_exact.py','complete_catalogue_compiler')
    V=module('frozen/native_verify.py','complete_catalogue_interpreter')
    raw=(PACKAGE/'data/final.json.gz').read_bytes()
    pins=json.loads((HERE/'SOURCES.json').read_text())['files']
    need(sha256(raw).hexdigest()==next(p['sha256'] for p in pins if p['path'].endswith('data/final.json.gz')),'word hash')
    word=json.loads(gzip.decompress(raw))
    main_fields=set(word['live'])|{x+112 for x in word['live']}|set(word['hosted']['X2'])|set(word['hosted']['Y2'])
    paid={(e[2],e[3]) for e in word['program'] if e[0]=='MOVE'}
    helpers={(word['initial'][r],word['final'][r]) for r in range(word['public']) if r not in main_fields}
    charts={};independent={};records=[]
    def chart(index):
        if index not in charts:charts[index]=C.canonical_frame(9,tuple(word['frames'][index]))
        return charts[index]
    def frame(index):
        if index not in independent:independent[index]=V.frame(word['frames'][index],9)
        return independent[index]
    catalogue=sorted(paid|helpers)
    stop=len(catalogue) if args.stop is None else args.stop
    need(0<=args.start<stop<=len(catalogue),'valid catalogue slice')
    for i in range(args.start,stop):
        a,b=catalogue[i]
        recipe,_=C.lower_child(chart(a).adjoint().then(chart(b)))
        need(recipe['rank']==abs(len(word['frames'][a])-len(word['frames'][b]))>0,'positive exact rank')
        V.equal(V.recipe(recipe),V.adjoint(frame(a))+frame(b),'complete paid/helper map '+str((a,b)))
        records.append([a,b,recipe])
        if i%250==0:print('complete catalogue',i,flush=True)
    main_records=[]
    for x,q in (zip(word['live'],word['ports']) if stop==len(catalogue) else []):
        a=word['initial'][x];b=word['final'][x+112]
        left,_=C.lower_child(C.cgate(9,q,1).adjoint().then(chart(a)))
        right,_=C.lower_child(chart(b).adjoint().then(C.cgate(9,q,-1).then(C.fourier(9))))
        need(left['rank']==right['rank']==0,'main boundary adapters are monomial')
        V.equal(V.recipe(left),(('C',q,-1),)+frame(a),'main input absolute phase')
        V.equal(V.recipe(right),V.adjoint(frame(b))+(('C',q,-1),)+V.fourier(9),'main output absolute phase')
        V.equal(frame(word['final'][x]),V.fourier(9),'main full Fourier endpoint')
        main_records.append([q,left,right])
    a,b,recipe=records[0]
    wrong=copy.deepcopy(recipe);wrong['left']['phase']=(wrong['left']['phase']+1)%4
    try:V.equal(V.recipe(wrong),V.adjoint(frame(a))+frame(b),'phase-only fault')
    except ValueError:pass
    else:raise ValueError('global phase control accepted')
    result=dict(status='PASS_CURRENT_NATIVE_CATALOGUE_SLICE',
        word_sha256=sha256(raw).hexdigest(),distinct_paid_maps=len(paid),distinct_helper_maps=len(helpers),
        catalogue_size=len(catalogue),slice_start=args.start,slice_stop=stop,
        catalogue_digest=sha256(json.dumps(catalogue,separators=(',',':')).encode()).hexdigest(),
        checked_maps=len(records),main_boundary_pairs=len(main_records),
        exact_recipe_digest=sha256(json.dumps(records,separators=(',',':'),sort_keys=True).encode()).hexdigest(),
        main_boundary_digest=sha256(json.dumps(main_records,separators=(',',':'),sort_keys=True).encode()).hexdigest(),
        phase_control_rejected=True,scope='Complete signed Pauli action plus exact Gaussian global phase; '
        'for Clifford maps these determine every matrix column. Generic tensor-product and physical '
        'grammar application is written in the review. No random-field substitution.')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()

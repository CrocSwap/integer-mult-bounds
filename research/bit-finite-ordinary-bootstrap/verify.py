#!/usr/bin/env python3
"""Rebind completed finite ordinary backends to PR4760's productive supplier.

Apache-2.0. Prepared for ai-nanachi with substantial OpenAI Codex assistance.
Finite leaf bootstrapping: rohanarun/PR185 and the credited PR199/204 lineage.
Native/compiler/cover sources and their notices remain frozen in the input.
"""
from pathlib import Path
from fractions import Fraction as F
import argparse,hashlib,importlib.util,json,sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
PREVIOUS=HERE.parent/'bit-compact-productive-controller'

def need(value,message):
    if not value:raise ValueError(message)

def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module
    spec.loader.exec_module(module);return module

def encode(value):
    if isinstance(value,F):return str(value)
    if isinstance(value,dict):return {str(k):encode(v)for k,v in value.items()}
    if isinstance(value,(list,tuple)):return [encode(v)for v in value]
    return value

def authenticate():
    manifest=json.loads((HERE/'SOURCES.json').read_bytes());count=0
    for item in manifest['files']:
        if item['usage']!='input':continue
        path=ROOT/item['path'];raw=path.read_bytes()
        need(not path.is_symlink(),'No aliased source')
        need(hashlib.sha256(raw).hexdigest()==item['sha256'],'Changed input '+item['path'])
        need(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==item['git_blob'],'Changed source blob')
        count+=1
    return count

def run():
    inputs=authenticate()
    # One source-identical full native/caller/RAW replay, not another legacy suite.
    source=load(PREVIOUS/'verify.py','bootstrap_previous_complete_verifier')
    previous=source.run()
    need(previous==json.loads((PREVIOUS/'RESULT.json').read_bytes()),'Source-identical complete PR4760 result')
    price=source.price
    inv=price.invoice(price.LOCAL,price.HELPERS)
    need(price.encode(inv)==previous['invoice'],'Exact native invoice, not copied headline')
    common=dict(price.PARAMS)
    common.update(tested=F('.00347545806'),uniform=F('.00347545805'),alpha_gap=F(1,2**39),
                  cover_gap=F(1,2**36)+F(1,10**20),atom=F(1,100),prime_coefficient=2**45)
    covered=common['uniform']-common['cover_gap'];backend=F('.0034597');levels=[]
    for index in range(1,4):
        exact=(1-common['atom'])*covered+common['atom']*backend
        scaled=exact*10**10;admitted=F(scaled.numerator//scaled.denominator,10**10)
        params={**common,'old_backend':backend,'admitted':admitted}
        cert=price.certify(inv,params)
        # The inherited changed-word label and variable historical comparator
        # do not describe a fixed-word finite-backend replacement.
        for key in ('WORD_changed','comparators','relative_gains'):cert.pop(key,None)
        cert.update(raw_moment_word_changed=False,completed_backend_replaced=True)
        need(cert['ordinary_exact']==exact,'Actual body exponent')
        need(backend<admitted<exact<covered<common['atom']<1-exact,'Finite stage strict gaps')
        levels.append({'level':index,'completed_backend_saving':backend,'ordinary_exact':exact,
                       'admitted':admitted,'certificate':cert})
        backend=admitted
    need(backend==F(1737729,500000000),'Declared ordinary supplier')
    old_exact=F(17713901828029,5120000000000000)
    need(backend/old_exact-1>F(1,1000),'Publication preparation margin over previous exact')
    source_receipt=hashlib.sha256(json.dumps(previous,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    return encode({'schema':1,'status':'PASS_CONDITIONAL_ORDINARY_BIT_003475458',
       'source_PR':4760,'source_inputs_authenticated':inputs,'source_full_receipt_sha256':source_receipt,
       'raw_invoice':inv,'raw_moment_word_changed':False,'whole_kappa_changed':False,
       'C1':covered,'params_shared':{k:v for k,v in common.items()if k not in ('admitted','old_backend')},'levels':levels,'admitted':backend,
       'new_H0':levels[0]['certificate']['tail']['compiler_H0'],
       'new_H1':levels[0]['certificate']['tail']['uniform_H1'],
       'previous_exact_ordinary':old_exact,'relative_gain_over_previous_exact':backend/old_exact-1,
       'base_completed_backend':F('.0034597'),'finite_backend_levels':3,
       'scope':'Same raw native WORD; tightened effective rank compiler, new fixed prime/cover constants and three acyclic completed ordinary backends. Retains completed arbitrary-width/spectator/ROW and source implementation premises. Not a materialized uniform program or a new whole multiplication theorem.'})

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--write',action='store_true');args=parser.parse_args()
    result=run();target=HERE/'RESULT.json'
    if args.write:target.write_bytes((json.dumps(result,sort_keys=True,indent=2)+'\n').encode())
    else:need(result==json.loads(target.read_bytes()),'Deterministic finite-backend certificate')
    print(json.dumps({'status':result['status'],'ordinary_BIT':result['admitted'],'finite_levels':3,
                      'raw_WORD_changed':False,'whole_kappa_changed':False}))

"""Reproduce the strict distinction from concurrent PR730's arity-2/3 class.

Runs the byte-exact pinned PR730 optimizer; does not review the rest of that PR.
No dependency on Git objects or network at verification time.
"""

import hashlib
import json
from pathlib import Path
import importlib.util

ROOT=Path(__file__).resolve().parent


def load(name, path):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def check():
    verify=load('local_verify',ROOT/'verify.py')
    planner=load('all_arity_planner',ROOT/'planner.py')
    for pin in json.loads((ROOT/'CONCURRENT-SOURCES.json').read_text())['sources']:
        verify.need(hashlib.sha256((ROOT/pin['path']).read_bytes()).hexdigest()==pin['sha256'],
                    'concurrent source pin: '+pin['path'])
    old=load('pr730',ROOT/'vendor/pr730/optimize.py')
    rows=[]
    for n,cap in ((15,5),(15,6),(27,6),(58,8)):
        charge,tree=old.optimize([1]*n,cap)
        space,recount=old.resources(tree,[1]*n)
        instructions=[(f,s,t,q) for s,t,f,q in old.instructions(tree)]
        verify.need(charge==recount==len(instructions), 'PR730 literal count')
        verify.linear_check(instructions,n,3+space)
        new=planner.optimize([1]*n,cap)
        verify.word_check(planner,new,n)
        verify.need(new['calls']<charge, 'strict higher-arity gain')
        rows.append(dict(factors=n,cap=cap,pr730_calls=charge,all_arity_calls=new['calls']))
    expected=json.loads((ROOT/'EXPECTED.json').read_text())
    weights=expected['rounded']['weighted']['weights']
    charge,tree=old.optimize(weights,5)
    space,recount=old.resources(tree,weights)
    instructions=[(f,s,t,q) for s,t,f,q in old.instructions(tree)]
    verify.need(space<=5 and charge==recount, 'PR730 weighted invoice')
    verify.need(sum(weights[f] for f,_,_,_ in instructions)==charge,'PR730 weighted word')
    verify.linear_check(instructions,15,3+space)
    new=planner.optimize(weights,5)
    verify.need(new['price']==3656 and new['price']<charge, 'strict weighted gain')
    result=dict(status='PASS_HIGHER_ARITY_COMPARISON',
                pr730_commit='d222e348179cc02a54d6d26dbd2838944f62c6e5',
                uniform=rows,weighted=dict(weights=weights,cap=5,pr730_phase_reads=charge,
                                          pr730_calls=len(instructions),
                                          all_arity_phase_reads=new['price'],
                                          all_arity_calls=new['calls']))
    return result


if __name__=='__main__':
    result=check()
    verify=load('comparison_verifier',ROOT/'verify.py')
    verify.compare_certificate(result,json.loads((ROOT/'CONCURRENT.json').read_text()))
    print(json.dumps(result,sort_keys=True,indent=2))
    print('PASS_HIGHER_ARITY_COMPARISON')

#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Compile three new and three inherited paid frame quotients and check exact phase.

Uses the separately authored retained Clifford compiler and independent
Gaussian interpreter. This six-pair test does not replace the exhaustive
composed catalogue, all-width or full caller qualification.
"""
import copy
import importlib.util
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod

def require(ok,label):
    if not ok: raise AssertionError(label)

def rejected(fn):
    try: fn()
    except (ValueError,AssertionError): return True
    return False

def main():
    build=load('contact_build_physical',HERE/'build.py')
    word=build.build_word()
    require(build.read(HERE/'data/word.json.gz')==word,'actual candidate word')
    engines=HERE/'retained/pr7605/retained/role902/independent/engines'
    compiler=load('contact_clifford_compiler',engines/'clifford_exact.py')
    interpreter=load('contact_native_interpreter',engines/'native_verify.py')
    frames=word['frames']
    pairs=((3,373,2),(373,733,2),(373,913,5),(401,922,5),(513,127,6),(740,1071,3))
    report=[]; reversed_rejected=0
    for a,b,rank in pairs:
        ca=compiler.canonical_frame(9,tuple(frames[a])); cb=compiler.canonical_frame(9,tuple(frames[b]))
        rec,_=compiler.lower_child(ca.adjoint().then(cb))
        require(rec['rank']==rank, 'lowered child rank')
        expected=interpreter.adjoint(interpreter.frame(frames[a],9))+interpreter.frame(frames[b],9)
        actual=interpreter.recipe(rec)
        interpreter.equal(actual,expected,'compiled phase-bearing quotient')
        for x,y in ((actual,expected),(interpreter.adjoint(actual),interpreter.adjoint(expected))):
            for col in range(512):
                require(interpreter.state(x,col)==interpreter.state(y,col), 'exact forward/adjoint Gaussian column')
        phase=copy.deepcopy(rec);phase['left']['phase']=(phase['left']['phase']+1)%4
        require(rejected(lambda:interpreter.equal(interpreter.recipe(phase),expected,'wrong phase')), 'phase control')
        wrong_source=618 if a==3 else 3
        wrong=interpreter.adjoint(interpreter.frame(frames[wrong_source],9))+interpreter.frame(frames[b],9)
        require(rejected(lambda:interpreter.equal(wrong,expected,'wrong source')), 'wrong source control')
        require(rejected(lambda:interpreter.equal((),expected,'missing MOVE')), 'missing MOVE control')
        rev=interpreter.frame(frames[b],9)+interpreter.adjoint(interpreter.frame(frames[a],9))
        reverse_reject=rejected(lambda:interpreter.equal(rev,expected,'wrong inverse order'))
        reversed_rejected+=int(reverse_reject)
        report.append({'pair':[a,b],'rank':rank,'forward_columns':512,'adjoint_columns':512,
                       'absolute_phase':True,'wrong_source_rejected':True,'wrong_phase_rejected':True,
                       'missing_move_rejected':True,'inverse_order_rejected':reverse_reject})
    require(reversed_rejected>=1,'inverse-order control must reject at least one nontrivial source')
    print(json.dumps({'status':'PASS_CONTACT_PHYSICAL_SIX_PAIRS','candidate_sha256':build.digest(build.canonical(word)), 'pairs':report,'inverse_order_rejected_count':reversed_rejected},sort_keys=True))

if __name__=='__main__': main()

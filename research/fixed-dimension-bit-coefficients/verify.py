#!/usr/bin/env python3
"""Read-only exact replay; --write-result is explicit receipt generation.

Prepared for CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys
from types import ModuleType

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]


def need(condition,label):
    if not condition: raise ValueError(label)


def load(path):
    name='_coefficient_check_bytes'
    module=ModuleType(name); module.__file__=str(path)
    sys.modules[name]=module
    try: exec(compile(path.read_bytes(),str(path),'exec'),module.__dict__)
    finally: sys.modules.pop(name,None)
    return module


def reject(action,label,fragment=None):
    try: action()
    except ValueError as exc:
        text=str(exc)
        need(fragment is None or fragment in text,label+': wrong rejection '+text)
        return {'control':label,'error':text}
    raise ValueError(label+': accepted')


def run():
    manifest=json.loads((HERE/'SOURCES.json').read_text())
    pins={}
    for row in manifest['files']:
        if row['usage']!='input': continue
        digest=sha256((ROOT/row['path']).read_bytes()).hexdigest()
        need(digest==row['sha256'],'source drift: '+row['path'])
        pins[row['path']]=digest
    checks=load(HERE/'check_consumer.py'); c=checks.C
    cases=[]
    for n,width,kinds,options in [
        (2,1,'',{}),
        (2,2,'GG',{}),
        (2,2,'GP',{'dense':True}),
        (2,3,'PPP',{'dense':True}),
        (3,2,'PP',{}),
        (3,3,'GUPG',{'dense':True}),
        (3,2,'GUPG',{'half_units':True}),
        (3,2,'GUPG',{'repeat':4}),
        (2,2,'PUP',{'warm_history':True}),
        (3,2,'GUP',{'leaf':True,'coefficient':False}),
        (3,2,'GPG',{'dense':True,'inverse':True,'offset':True}),
        (44,2,'G',{'rank':43}),
        (65,2,'',{}),
        (130,1,'',{}),
    ]:
        cases.append(checks.run_case(n,width,kinds,**options))
    controls=[]
    for value in (True,1,-1):
        controls.append(reject(lambda v=value:c.build(v),'dimension '+repr(value),'fixed dimension >=2'))
    for kw,fragment in [
        ({'short_capacity':True},'fixed register inventory'),
        ({'wrong_field_code':True},'original global raw-field code'),
        ({'truncate_field':True},'encoded word extent'),
    ]:
        result=checks.run_case(2,2,'GUPG' if 'wrong_field_code' in kw else 'GP',**kw)
        need(fragment in result['control_error'],'actual bad encoded control')
        controls.append({'control':next(iter(kw)),**result})
    old_changes=c.changes
    def omit_word_limit(n):
        edits=old_changes(n); edits['words']=[]; return edits
    c.changes=omit_word_limit
    try:
        controls.append(reject(lambda:checks.run_case(130,1,''),
                               'retained 128 multiplier guard','finite index multiplier'))
    finally: c.changes=old_changes
    def omit_rank_limit(n):
        edits=old_changes(n)
        edits['controller']=[pair for pair in edits['controller'] if pair[0]!='1 <= rank <= 42']
        return edits
    c.changes=omit_rank_limit
    try:
        controls.append(reject(lambda:checks.run_case(44,2,'G',rank=43),
                               'retained rank-42 guard','actual selected rank'))
    finally: c.changes=old_changes
    def omit_full_field_dimension(n):
        edits=old_changes(n)
        edits['records']=[pair for pair in edits['records'] if not pair[0].startswith('out = [[')]
        return edits
    c.changes=omit_full_field_dimension
    try:
        controls.append(reject(lambda:checks.run_case(65,2,''),
                               'retained 64-squared reader','complete 64-dimensional raw high field'))
    finally: c.changes=old_changes
    old_open=c.Workspace.open
    def fresh_tape(workspace,*args,**kwargs):
        workspace.modules.records.Tape()
        return old_open(workspace,*args,**kwargs)
    c.Workspace.open=fresh_tape
    try:
        controls.append(reject(lambda:checks.run_case(2,2,'G'),
                               'fresh continuation role','fresh continuation tape during callback'))
    finally: c.Workspace.open=old_open
    instance=c.build(130)
    need(instance.edit_count==17,'all seventeen specialization sites')
    need(all(row['source_changes']==17 for row in cases),'case specialization contract')
    return {'schema':1,'claim':'fixed-dimension encoded consumer; no new kappa',
            'base':manifest['base_commit'],'source_inputs':pins,
            'implementation_sha256':{name:sha256((HERE/name).read_bytes()).hexdigest()
                                     for name in ('consumer.py','check_consumer.py')},
            'N130_specialized_sha256':instance.specialized_hashes,
            'cases':cases,'controls':controls,'case_count':len(cases),'control_count':len(controls)}


def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--write-result',action='store_true')
    args=parser.parse_args()
    result=run(); encoded=json.dumps(result,sort_keys=True,separators=(',',':'))
    if args.write_result:
        (HERE/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    else:
        expected=json.loads((HERE/'RESULT.json').read_text())
        need(encoded==json.dumps(expected,sort_keys=True,separators=(',',':')),'typed complete RESULT equality')
    print('PASS_FIXED_DIMENSION_COEFFICIENTS',result['case_count'],result['control_count'],
          sha256(encoded.encode()).hexdigest())


if __name__=='__main__':
    try: main()
    except (ValueError,KeyError,OSError) as exc:
        print('FAIL_FIXED_DIMENSION_COEFFICIENTS',str(exc),file=sys.stderr)
        raise SystemExit(1)

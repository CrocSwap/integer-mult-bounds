#!/usr/bin/env python3
"""Source-bound conditional control certificate and actual caller observer.

JoyboyBrian, substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
import ast
import copy
import hashlib
import json
from pathlib import Path
import sys
import types
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE))
from kernel import need,validate,bounds,complete_bound,access_cost
from observer import Observer,SKIP
import check_bits
SIZE=65536
PRE='research/qq16-protected-return-caller/'


def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False)


def authenticate():
    rows=json.loads((HERE/'SOURCES.json').read_bytes())['files']
    for row in rows:
        if row['usage']!='input':continue
        raw=(ROOT/row['path']).read_bytes()
        need(hashlib.sha256(raw).hexdigest()==row['sha256'],'source integrity: '+row['path'])


def source_sites():
    tree=ast.parse((ROOT/PRE/'adapter.py').read_bytes())
    cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ReturnProtocol')
    methods={n.name:n for n in cls.body if isinstance(n,ast.FunctionDef)}
    def calls(name,attribute):
        return [n for n in ast.walk(methods[name]) if isinstance(n,ast.Call) and
                isinstance(n.func,ast.Attribute) and n.func.attr==attribute]
    need(len(calls('__init__','check_inventory'))==1 and len(calls('__call__','check_inventory'))==2,
         'constructor and both actual return validations')
    need(len(calls('__call__','exchange'))==2,'native plus conditional service exchange')
    exchange_nodes=[n for n in ast.walk(methods['__call__']) if isinstance(n,ast.If) and
                    ast.unparse(n.test)=='caller is i.service']
    need(len(exchange_nodes)==1 and 'self.exchange(service, old, result)' in ast.unparse(exchange_nodes[0]),
         'service-only exchange source condition')
    tree=ast.parse((ROOT/'research/qq16-caller-install/installer.py').read_bytes())
    owner=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='owned_tapes')
    skip=next(n.value for n in ast.walk(owner) if isinstance(n,ast.Assign) and
              any(isinstance(t,ast.Name) and t.id=='skip' for t in n.targets))
    need(ast.literal_eval(skip)==SKIP,'exact source omission alphabet')
    census=json.loads((ROOT/PRE/'RESULT.json').read_bytes())['source_protocol_census']
    need(census['complete_per_Gamma']==511014 and census['service_per_Gamma']==336 and
         census['producer_per_Gamma']==510678 and census['later_producer_per_Gamma']==493097,
         'complete inherited source census includes suffix')


def run_actual():
    observer=Observer(SIZE)
    path=ROOT/PRE/'verify.py';raw=path.read_text()
    anchor="        need(fixture.Tape.__eq__ is object.__eq__, 'retained Tape equality is identity')"
    need(raw.count(anchor)==1,'one read-only observer insertion site')
    changed=raw.replace(anchor,anchor+'\n        OBSERVER.attach(adapter, fixture.Tape)')
    before=ast.parse(raw);after=ast.parse(changed)
    class Remove(ast.NodeTransformer):
        def visit_Expr(self,node):
            if ast.unparse(node)=='OBSERVER.attach(adapter, fixture.Tape)':return None
            return self.generic_visit(node)
    need(ast.dump(before,include_attributes=False)==ast.dump(Remove().visit(after),include_attributes=False),
         'observer preserves complete inherited verifier AST')
    module=types.ModuleType('authenticated_control_caller');module.__file__=str(path)
    module.OBSERVER=observer
    exec(compile(changed,str(path),'exec'),module.__dict__)
    result=module.case('adopt')
    expected=json.loads((ROOT/PRE/'RESULT.json').read_bytes())['cases']['adopt']
    need(canonical(result)==canonical(expected),'unchanged complete actual caller result')
    need(len(observer.checks)==50 and len(observer.exchanges)==36,'complete observed site census')
    # Last call is the inherited verifier's final audit, outside the algorithm.
    active=observer.checks[:-1]
    need(len(active)==1+2*24 and len(observer.exchanges)==24+12,'initialization and every source return')
    # Larger scope/descriptor epochs cannot be bounded by one constructor graph.
    phase_growth=[(owner,key,active[0]['shapes'][owner][key],max(x['shapes'][owner][key] for x in active))
                  for owner in range(3) for key in ('vertices','edges','attributes')]
    need(any(peak>initial for owner,key,initial,peak in phase_growth),
         'constructor-only graph size counterexample')
    return observer,dict(returns=24,service_returns=12,algorithm_validations=49,
                         graph_walks=147,cache_exchanges=36,excluded_final_audit=1,
                         contract_size=SIZE,unchanged_complete_receipt=True,
                         constructor_size_not_uniform=True)


def reject(action,message):
    try:action()
    except ValueError as error:
        need(message in str(error),'exact negative boundary: '+str(error))
    else:raise ValueError('negative control accepted: '+message)


def controls(example):
    tests=0
    for field in ('graphs','saved','external','auxiliary','storage','acquired'):
        bad=copy.deepcopy(example);del bad[field]
        reject(lambda:validate(bad,SIZE),'complete snapshot fields');tests+=1
    reject(lambda:validate(example,1),'bounded source graph contract');tests+=1
    reject(lambda:validate(example,SIZE,width=1),'handle width covers addresses');tests+=1
    bad=copy.deepcopy(example);bad['external'][0]=bad['external'][1]
    reject(lambda:validate(bad,SIZE),'ordered external binding');tests+=1
    bad=copy.deepcopy(example);bad['saved'][0][0]=bad['saved'][0][1]
    reject(lambda:validate(bad,SIZE),'distinct physical inventory');tests+=1
    bad=copy.deepcopy(example);bad['graphs'][0]['rows'][0][2].append(10**8)
    reject(lambda:validate(bad,SIZE),'graph child handle');tests+=1
    reject(lambda:complete_bound(SIZE,1,returns_per_gamma=17581),'complete source census');tests+=1
    return tests


def compute():
    authenticate();source_sites()
    bit_cases=check_bits.verify(access_cost)
    observer,actual=run_actual()
    faults=controls(observer.examples[0])
    bill=complete_bound(SIZE,1)
    u=bounds(SIZE)['bits']
    # Independent integer aggregation; do not call the primary expression again.
    c=510678+336;s=336
    independent=(1+2*c)*u + (c+s)*u + (1+c)*u
    need(independent==bill['control_upper'],'independent complete arithmetic')
    witness_v=independent//(11*c)+1
    need(11*c*witness_v+4*c>independent,'conditional F=0 arithmetic witness only')
    return dict(status='PASS_QQ16_FINITE_HANDLE_CHARGE',actual=actual,
                bit_access_cases=bit_cases,rejection_controls=faults,
                per_kernel_upper=bounds(SIZE),whole_cover_bill=bill,
                assumption='Encoded complete bounded graphs; F remains separate and is not assumed zero.',
                scope='Conditional metadata charge only; no production K, physical embedding, D* versus B* or kappa.'),observer


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--write',action='store_true')
    parser.add_argument('--log',type=Path)
    args=parser.parse_args();result,observer=compute()
    if args.write:(HERE/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    else:need(canonical(result)==canonical(json.loads((HERE/'RESULT.json').read_bytes())), 'typed complete receipt')
    if args.log:
        args.log.write_text(json.dumps(dict(checks=observer.checks,exchanges=observer.exchanges),indent=2)+'\n')
    print(result['status'])

if __name__=='__main__':main()

#!/usr/bin/env python3
"""Finite source correspondence for a standalone formal comparator; Apache-2.0."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def require(ok, message):
    if not ok:
        raise ValueError(message)


def authenticate():
    for item in json.loads((HERE/'SOURCES.json').read_text(encoding='utf-8'))['files']:
        if item['usage'] == 'input':
            require(hashlib.sha256((ROOT/item['path']).read_bytes()).hexdigest() == item['sha256'],
                    'changed source: '+item['path'])
    for item in json.loads((HERE/'VENDOR.json').read_text(encoding='utf-8'))['files']:
        require(hashlib.sha256((HERE/item['snapshot']).read_bytes()).hexdigest() == item['sha256'],
                'changed vendor: '+item['snapshot'])
    formal = json.loads((HERE/'FORMAL.json').read_text(encoding='utf-8'))
    require(hashlib.sha256((HERE/formal['file']).read_bytes()).hexdigest() == formal['sha256'],
            'changed formal source')


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run():
    authenticate()  # Before parsing literals or executing predecessor Python.
    parser = load('radix_literal_parser', ROOT/'research/hpe-lean-semantic-binding/verify.py')
    _, literals = parser.literal_data((ROOT/'research/hyperplane-end-lean/HyperplaneEnd/Exact.lean').read_text(encoding='utf-8'))
    old = load('retained_unitary_radix', ROOT/'research/hpe-unitary-packed-radix/verify.py')
    names = [side+'Lit'+str(i) for i in (1,2,3) for side in ('lhs','rhs')]
    count = {name: sum(g[0]=='cg' for g in literals[name]) for name in names}
    kmax = {name: max(count['lhsLit'+name[-1]],count['rhsLit'+name[-1]]) for name in names}
    known, captures, seen, sums = {}, {}, {}, {}
    original_compile, original_execute = old.compile_gates, old.execute
    digest = hashlib.sha256()
    def compile_bound(gates):
        compiled = original_compile(gates)
        matches = [name for name in names if gates == literals[name]]
        if matches:
            require(len(matches)==1, 'literal circuit names must be distinct')
            name = matches[0]
            known[id(compiled)] = name
            captures[name] = compiled  # Retain identity, preventing object-id reuse.
            seen.setdefault(name,set())
            sums.setdefault(name,[[0,0] for _ in range(old.N)])
        return compiled
    def execute_bound(compiled, values):
        output = original_execute(compiled, values)
        name = known.get(id(compiled))
        if name is not None:
            nonzero = [i for i,z in enumerate(values) if z != (0,0)]
            if len(nonzero)==1 and values[nonzero[0]]==(1,0):
                j = nonzero[0]
                require(j not in seen[name], 'duplicate basis column')
                seen[name].add(j)
                weight = 1 << ((kmax[name]+2)*j)
                require(len(output)==old.N, 'output arity')
                require(sum(a*a+b*b for a,b in output)==4**count[name], 'column energy premise')
                for target,(a,b) in enumerate(output):
                    sums[name][target][0] += a*weight
                    sums[name][target][1] += b*weight
                digest.update(json.dumps([name,j,output],separators=(',',':')).encode())
        return output
    old.compile_gates, old.execute = compile_bound, execute_bound
    try:
        retained = old.run()
    finally:
        old.compile_gates, old.execute = original_compile, original_execute
    expected = json.loads((ROOT/'research/hpe-unitary-packed-radix/RESULT.json').read_text(encoding='utf-8'))
    require(json.dumps(retained,sort_keys=True)==json.dumps(expected,sort_keys=True), 'retained typed receipt')
    require(set(captures)==set(names), 'complete literal census')
    rows = []
    for name in names:
        require(seen[name]==set(range(old.N)), 'complete column coverage')
        values = [(1<<((kmax[name]+2)*j),0) for j in range(old.N)]
        result = original_execute(captures[name],values)
        require(result==[tuple(z) for z in sums[name]], 'packed-row linearity binding')
    for i in (1,2,3):
        left,right='lhsLit'+str(i),'rhsLit'+str(i)
        k=kmax[left];sl=1<<(k-count[left]);sr=1<<(k-count[right])
        require(all((sl*a,sl*b)==(sr*c,sr*d)
                    for (a,b),(c,d) in zip(sums[left],sums[right])), 'normalized packed equality')
        rows.append({'pair':i,'left_C':count[left],'right_C':count[right],
                     'K':k,'B':1<<(k+2),'left_scale':sl,'right_scale':sr,
                     'new_max_input_bits':(k+2)*(old.N-1)+1,
                     'old_max_input_bits':(2*k+2)*(old.N-1)+1})
    return {'pairs':rows,'literal_circuits':len(names),'columns':sum(map(len,seen.values())),
            'packed_real_imag_components':len(names)*old.N*2,
            'ordered_columns_sha256':digest.hexdigest(),
            'retained_semantic_controls':len(retained['controls']),
            'formal_roots':10,'formal_file_sha256':json.loads((HERE/'FORMAL.json').read_text())['sha256'],
            'boundary':'Finite Python correspondence; run check_lean.py separately for a fresh kernel audit. No old Mathlib/Python semantic bridge or selected-checker replacement.'}


def check_receipt(result):
    expected=json.loads((HERE/'RESULT.json').read_text(encoding='utf-8'))
    require(json.dumps(result,sort_keys=True)==json.dumps(expected,sort_keys=True),'typed receipt mismatch')


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');ap.add_argument('--authenticate-only',action='store_true');args=ap.parse_args()
    if args.authenticate_only:
        authenticate();print('PASS_PACKED_RADIX_AUTHENTICATION');return
    result=run()
    encoded=json.dumps(result,indent=2,sort_keys=True)+'\n'
    if args.write:
        (HERE/'RESULT.json').write_text(encoded,encoding='utf-8',newline='\n')
    else:
        check_receipt(result)
    print(json.dumps(result,sort_keys=True));print('PASS_HPE_PACKED_RADIX_CORE_BINDING')


if __name__=='__main__':main()

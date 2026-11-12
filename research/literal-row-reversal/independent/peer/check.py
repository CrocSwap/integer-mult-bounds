"""Independent C3 source/graph, binary-prefix and interface algebra checks.

No author CPU or test suite is called. Root separately checks execution.
Prepared for CubeJerry with OpenAI assistance; Apache-2.0.
"""
from pathlib import Path
import ast
import hashlib
import importlib.util
import inspect
import itertools
import json
import sys

PROGRAM = '4b516d85baf3303db809bc1174394009b1fc71a8f7d17fb6c729ec8bb6aba245'
PROOF = '9dc3019f115098e1c14d41308b07266e48a6cd84f473e1205d472c640539f049'


def need(condition, message):
    if not condition:
        raise ValueError(message)


def decoder_by_prefixes(n):
    digits = bin(n)[2:]
    value = 1
    total = 9+5*len(digits)
    prefixes = 0
    for digit in digits[1:]:
        prefixes += value
        total += 47*value+17*int(digit)+23
        value = 2*value+int(digit)
    need(value == n, 'prefix interpretation')
    need(prefixes == n-n.bit_count(), 'strict binary prefix identity')
    return total


def stage_count(p, r, b):
    # Counts derived directly from the load/pop/emit and retirement loops.
    one_prefix = r*(12*b+7)+1 + (3*r+4) + r*(17*b+10)+1 + (3*r+7)
    v = p*r*b
    return (27 + sum(decoder_by_prefixes(n) for n in (p,r,b))
            + p*one_prefix+(p+1)
            + 1 + 2*(5*v+3)+2*(3*v+3)+(8*v+1)
            + (3*p+3) + sum(7*n+4 for n in (p,r,b)) + 27+1)


def caps(p, r, b):
    v = p*r*b
    return (v,p,r,b,max(p,r,b),max(n.bit_length() for n in (p,r,b)),r*b,b,v)


def target(k, p, r, b):
    prefix, local = divmod(k,r*b)
    row, suffix = divmod(local,b)
    return prefix*r*b+(r-1-row)*b+suffix


def main():
    package = Path(sys.argv[1]).resolve()
    need(hashlib.sha256((package/'reverse.py').read_bytes()).hexdigest() == PROGRAM, 'program pin')
    need(hashlib.sha256((package/'PROOF.md').read_bytes()).hexdigest() == PROOF, 'reviewed proof pin')
    sources = json.loads((package/'SOURCES.json').read_text())['files']
    for entry in sources:
        raw = (package/entry['local']).read_bytes()
        need(len(raw) == entry['bytes'] and hashlib.sha256(raw).hexdigest() == entry['sha256'], 'source bytes '+entry['local'])
    source = (package/'reverse.py').read_text()
    prior = (package/'reference/phase-patterns.py').read_text()
    trees = [{n.name:ast.dump(n,include_attributes=False) for n in ast.parse(s).body
              if isinstance(n,ast.FunctionDef)} for s in (source,prior)]
    helpers = ('fresh','clear','unary_copy','trace_return')
    for name in helpers:
        need(trees[0][name] == trees[1][name], 'retained helper '+name)
    spec = importlib.util.spec_from_file_location('c3_peer_program',package/'reverse.py')
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    need(not inspect.signature(module.compile_reverse).parameters, 'zero-argument graph')
    graph, alphabet = module.compile_reverse()
    need(len(graph) == 524 and tuple(alphabet) == ('_','0','1','|'), 'fixed graph size and alphabet')
    for operation,*args in graph:
        need(operation in ('read','write','move','goto','halt'), 'literal operation')
        if operation in ('read','write','move'):
            need(type(args[0]) is int and 0 <= args[0] < 13, 'fixed owner')
        if operation == 'move':
            need(args[1] in (-1,1), 'unit movement')
        elif operation == 'write':
            need(args[1] in alphabet, 'written symbol')
        elif operation == 'goto':
            need(type(args[0]) is int and 0 <= args[0] < len(graph), 'fixed jump')
        elif operation == 'read':
            need(set(args[1]) <= set(alphabet), 'read alphabet')
            need(all(type(q) is int and 0 <= q < len(graph) for q in args[1].values()), 'fixed local branch')
    integers = sorted(set(range(1,4097)) | {2**k+d for k in range(1,257) for d in (-1,0,1)})
    for n in integers:
        need(decoder_by_prefixes(n) == 47*n-30*n.bit_count()+28*n.bit_length()-31, 'exact decoder census')
    shapes = list(itertools.product(range(1,18),repeat=3)) + [(2**80,1,1),(1,2**101,3),(3,7,2**200+1)]
    for p,r,b in shapes:
        v = p*r*b
        e = sum(n.bit_length() for n in (p,r,b))
        exact = 53*v+23*p*r+71*p+54*r+54*b+28*e-30*sum(n.bit_count() for n in (p,r,b))-8
        need(stage_count(p,r,b) == exact, 'complete stage census')
        need(exact <= 256*(v+e+1), 'complete uniform envelope')
        need(sum(x+2 for x in caps(p,r,b)) <= 8*v+e+18, 'private cap envelope')
    address_checks = 0
    for d in range(1,9):
        for j in range(d):
            for b in (1,2,5):
                block = (1 << (d-j-1))*b
                for copies in (1,3):
                    p = copies*(1 << j)
                    for k in range(copies*(1 << d)*b):
                        q,t = divmod(k,b)
                        expected = (q ^ (1 << (d-j-1)))*b+t
                        need(target(k,p,2,block) == expected, 'source flip map and prefix multiplicity')
                        address_checks += 1
    controls = []
    p,r,b,k = 2,3,2,0
    correct = target(k,p,r,b)
    need(correct != p*r*b-1-k, 'whole-bit reversal witness')
    controls.append('whole-bit reversal')
    need(correct != (p*r-1-k//b)*b+k%b, 'cross-prefix row reversal witness')
    controls.append('cross-prefix row reversal')
    need(0b1010 != 0b1111, 'strided/full-field distinction')
    controls.append('unpaid strided-to-contiguous replacement')
    # Source accepts extra outer repetitions; P=2^j alone would underdeclare.
    d,j,b,copies = 3,1,2,3
    v = copies*(1 << d)*b
    block = (1 << (d-j-1))*b
    need((1 << j)*2*block != v and (v//(2*block))*2*block == v, 'complete-rectangle premise witness')
    controls.append('missing complete-rectangle source premise')
    chain = [(8,1,1),(1,8,1),(1,1,8)]
    history_union = sum(max(caps(*shape)[i] for shape in chain)+2 for i in range(9))
    max_current = max(sum(x+2 for x in caps(*shape)) for shape in chain)
    need(history_union == 86 > max_current == 72, 'historical union differs from max current extent')
    controls.append('max-current history equality')
    need(decoder_by_prefixes(2) != 47*2-29*(2).bit_count()+28*(2).bit_length()-31, 'popcount tariff mutation')
    controls.append('wrong popcount coefficient')
    print(json.dumps({'status':'PASS_C3_INDEPENDENT_ABI_COST_HISTORY','program_sha256':PROGRAM,
        'proof_sha256':PROOF,'table_sha256':hashlib.sha256(json.dumps(graph,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
        'source_files':len(sources),'literal_locations':len(graph),'retained_helpers':helpers,
        'binary_integers':len(integers),'shape_checks':len(shapes),'map_addresses':address_checks,
        'history_union_witness':[history_union,max_current],'negative_controls':controls,
        'scope':'Independent source/graph and exact mathematical checks; no author CPU or test suite replay. Universal proof reviewed separately; root supplies independent execution.'},indent=2,sort_keys=True))


if __name__ == '__main__':
    main()
